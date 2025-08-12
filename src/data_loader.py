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
from pathlib import Path
from dotenv import load_dotenv

# Try both import locations for Markdown header splitter (depends on langchain version)
try:
    from langchain.text_splitter import MarkdownHeaderTextSplitter
except Exception:
    from langchain_text_splitters import MarkdownHeaderTextSplitter  # pip install langchain-text-splitters

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv('API_KEY')
openai.api_key = API_KEY
os.environ["OPENAI_API_KEY"] = API_KEY

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
    Then sub-split large sections with a character splitter to keep them model-friendly.
    """
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
        ],
        strip_headers=True,  # content won't duplicate the heading line
    )

    all_section_docs: list[Document] = []

    for doc in documents:
        header_docs = header_splitter.split_text(doc.page_content)

        # retain original file/path metadata
        for hd in header_docs:
            meta = dict(hd.metadata or {})
            meta.update({k: v for k, v in doc.metadata.items() if k not in meta})
            hd.metadata = meta

        all_section_docs.extend(header_docs)

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
            sc.metadata = {
                **sec.metadata,
                "parent_section": {
                    "h1": sec.metadata.get("h1"),
                    "h2": sec.metadata.get("h2"),
                },
            }
        final_chunks.extend(subchunks)

    print(f"Split {len(documents)} files into {len(all_section_docs)} header sections and {len(final_chunks)} final chunks.")

    if final_chunks:
        example = final_chunks[min(1, len(final_chunks)-1)]
        print("--- Example chunk content ---")
        print(example.page_content[:500])
        print("--- Example chunk metadata ---")
        print(example.metadata)

    return final_chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first (fresh build)
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(api_key=API_KEY),   # ensure this matches your query-time embedding
        persist_directory=CHROMA_PATH,
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
