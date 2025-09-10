# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
import os
import re
import shutil
import time
import random
from pathlib import Path
# Try both import locations for Markdown header splitter (depends on langchain version)
try:
    from langchain.text_splitter import MarkdownHeaderTextSplitter
except Exception:
    from langchain_text_splitters import MarkdownHeaderTextSplitter  # pip install langchain-text-splitters

# Get API key directly from environment variables (for Docker/App Runner)
API_KEY = os.getenv('API_KEY')
openai.api_key = API_KEY
os.environ["API_KEY"] = API_KEY

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    chunks = split_text_by_markdown_headers(documents)
    save_to_chroma(chunks)

def load_documents():
    """
    Load raw markdown so '#' and '##' remain in page_content.
    """
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.md",
        loader_cls=TextLoader,                    # <-- raw text, no markdown stripping
        loader_kwargs={"encoding": "utf-8"},
        use_multithreading=True,
    )
    documents = loader.load()
    return documents
def split_text_by_markdown_headers(documents: list[Document]) -> list[Document]:
    """
    Split markdown files by # and ## headings first.
    Then sub-split large sections; every resulting chunk starts with: "<h1>: <h2>" (or just "<h1>" if no h2).
    Skip the "Źródło" section and extract its URL as metadata.
    """
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
        ],
        strip_headers=True,  # we'll add our own first line
    )

    def header_prefix(meta: dict) -> str:
        # prefer direct h1/h2; fallback to parent_section if present
        ps = meta.get("parent_section", {}) or {}
        h1 = meta.get("h1") or ps.get("h1") or ""
        h2 = meta.get("h2") or ps.get("h2") or ""
        if h1 and h2:
            return f"{h1}: {h2}"
        return h1 or h2 or "Fragment"

    all_section_docs: list[Document] = []

    for doc in documents:
        header_docs = header_splitter.split_text(doc.page_content)
        
        # Extract source URL from "Źródło" section
        source_url = ""
        for hd in header_docs:
            if hd.metadata.get("h2") == "Źródło":
                # Extract URL from the content
                content = hd.page_content.strip()
                # Look for URL pattern
                url_match = re.search(r'https?://[^\s]+', content)
                if url_match:
                    source_url = url_match.group(0)
                break

        # carry over original file/path metadata and add source URL
        for hd in header_docs:
            # Skip the "Źródło" section entirely
            if hd.metadata.get("h2") == "Źródło":
                continue
                
            meta = dict(hd.metadata or {})
            meta.update({k: v for k, v in doc.metadata.items() if k not in meta})
            
            # Add source URL to metadata if we found one
            if source_url:
                meta["source"] = source_url
            
            hd.metadata = meta

            # prepend "<h1>: <h2>" to this section's content
            prefix = header_prefix(hd.metadata)
            hd.page_content = f"{prefix}\n\n{hd.page_content}".strip()

        all_section_docs.extend([hd for hd in header_docs if hd.metadata.get("h2") != "Źródło"])

    # Optional: sub-split big sections
    section_chunker = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=120,
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""],
    )

    final_chunks: list[Document] = []
    for sec in all_section_docs:
        if len(sec.page_content) <= 1400:
            final_chunks.append(sec)
            continue

        subchunks = section_chunker.split_documents([sec])
        for sc in subchunks:
            # keep header metadata but flatten nested structures
            sc.metadata = {
                **sec.metadata,
                "parent_h1": sec.metadata.get("h1", ""),
                "parent_h2": sec.metadata.get("h2", ""),
            }
            # ensure each subchunk also starts with "<h1>: <h2>"
            prefix = header_prefix(sc.metadata)
            # If the prefix is already there (because we split the section's content),
            # avoid duplicating: check the beginning.
            content = sc.page_content.lstrip()
            if not content.startswith(prefix):
                sc.page_content = f"{prefix}\n\n{content}"
        final_chunks.extend(subchunks)

    print(f"Split {len(documents)} files into {len(all_section_docs)} header sections and {len(final_chunks)} final chunks.")

    if final_chunks:
        example = final_chunks[min(1, len(final_chunks)-1)]
        print("--- Example chunk content ---")
        print(example.page_content[:500])
        print("--- Example chunk metadata ---")
        print(example.metadata)

    return final_chunks

def estimate_tokens(text: str) -> int:
    """
    Rough estimate of tokens (1 token ≈ 4 characters for English text)
    """
    return len(text) // 4

def add_documents_with_retry(db, batch, max_retries=5, base_delay=1):
    """
    Add documents to Chroma with retry logic for network errors.
    """
    for attempt in range(max_retries):
        try:
            db.add_documents(batch)
            return True
        except openai.InternalServerError as e:
            # Handle 502 Bad Gateway and other server errors
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"OpenAI server error (attempt {attempt + 1}): {str(e)[:100]}... Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print(f"Final attempt failed with server error: {str(e)}")
                raise e
        except openai.RateLimitError as e:
            # Handle rate limiting
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit (attempt {attempt + 1}): {str(e)[:100]}... Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print(f"Final attempt failed with rate limit: {str(e)}")
                raise e
        except openai.APIConnectionError as e:
            # Handle connection errors
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Connection error (attempt {attempt + 1}): {str(e)[:100]}... Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print(f"Final attempt failed with connection error: {str(e)}")
                raise e
        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed: {str(e)[:100]}... Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print(f"Final attempt failed: {str(e)}")
                raise e

def save_to_chroma(chunks: list[Document]):
    # Check if database already exists
    db_exists = os.path.exists(CHROMA_PATH)
    
    if db_exists:
        print(f"Chroma database already exists at {CHROMA_PATH}")
        response = input("Do you want to clear and rebuild? (y/n): ").lower().strip()
        if response == 'y':
            shutil.rmtree(CHROMA_PATH)
            db_exists = False
            print("Cleared existing database.")
        else:
            print("Using existing database. Add new documents...")
            # Load existing database
            embeddings = OpenAIEmbeddings(api_key=API_KEY)
            db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=embeddings,
            )
            # Add all chunks to existing database
            batch_size = 50
            total_chunks = len(chunks)
            print(f"Adding {total_chunks} chunks to existing database in batches of {batch_size}...")
            
            for i in range(0, total_chunks, batch_size):
                end_idx = min(i + batch_size, total_chunks)
                batch = chunks[i:end_idx]
                
                print(f"Processing batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size} ({len(batch)} chunks)")
                
                try:
                    add_documents_with_retry(db, batch)
                    print(f"Successfully processed batch {i//batch_size + 1}")
                except Exception as e:
                    print(f"Failed to process batch {i//batch_size + 1}: {str(e)}")
                    continue
            
            try:
                db.persist()
                print(f"Added {total_chunks} chunks to existing database.")
            except Exception as e:
                print(f"Failed to persist database: {str(e)}")
                raise e
            return
    
    # Clear out the database first (fresh build)
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    # Initialize embeddings and Chroma
    embeddings = OpenAIEmbeddings(api_key=API_KEY)
    
    # Process chunks in batches to avoid token limit
    batch_size = 50  # Reduced batch size for better reliability
    total_chunks = len(chunks)
    
    print(f"Processing {total_chunks} chunks in batches of {batch_size}...")
    
    # Initialize Chroma with first batch
    first_batch = chunks[:batch_size]
    print("Initializing Chroma with first batch...")
    
    try:
        db = Chroma.from_documents(
            first_batch,
            embeddings,
            persist_directory=CHROMA_PATH,
        )
        print("Successfully initialized Chroma database")
    except Exception as e:
        print(f"Failed to initialize Chroma: {str(e)}")
        raise e
    
    # Process remaining chunks in batches
    successful_batches = 1  # First batch was successful
    failed_batches = 0
    
    for i in range(batch_size, total_chunks, batch_size):
        end_idx = min(i + batch_size, total_chunks)
        batch = chunks[i:end_idx]
        
        print(f"Processing batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size} ({len(batch)} chunks)")
        
        # Add documents to existing collection with retry logic
        try:
            add_documents_with_retry(db, batch)
            print(f"Successfully processed batch {i//batch_size + 1}")
            successful_batches += 1
        except Exception as e:
            print(f"Failed to process batch {i//batch_size + 1}: {str(e)}")
            failed_batches += 1
            # Continue with next batch instead of failing completely
            continue
    
    try:
        db.persist()
        print(f"Saved {total_chunks} chunks to {CHROMA_PATH}.")
        print(f"Summary: {successful_batches} successful batches, {failed_batches} failed batches")
    except Exception as e:
        print(f"Failed to persist database: {str(e)}")
        raise e

if __name__ == "__main__":
    main()