import argparse
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pathlib import Path
import os

CHROMA_PATH = "chroma"

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")

PROMPT_TEMPLATE = """
Odpowiedz na pytanie tylko na podstawie poniższych informacji:

{context}

---

Odpowiedz na pytanie tylko na podstawie powyższego kontekstu: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings(api_key=API_KEY)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print("Unable to find matching results.")
        return

    def _fmt_chunk(doc):
        # Prefer direct h1/h2; fall back to parent_section if you stored it that way
        ps = doc.metadata.get("parent_section", {}) or {}
        h1 = doc.metadata.get("h1") or ps.get("h1") or ""
        h2 = doc.metadata.get("h2") or ps.get("h2") or ""
        src = doc.metadata.get("source") or doc.metadata.get("path") or doc.metadata.get("doc_id") or ""

        title_parts = [p for p in [h1, h2] if p]
        title = " › ".join(title_parts) if title_parts else "Fragment"

        header_lines = [f"## {title}"]
        if src:
            header_lines.append(f"[Source: {src}]")
        header = "\n".join(header_lines)

        body = doc.page_content.strip()
        return f"{header}\n{body}"

    context_text = "\n\n---\n\n".join([_fmt_chunk(doc) for doc, _score in results])

    print(context_text)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = ChatOpenAI(api_key=API_KEY, temperature= 0.1)
    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()