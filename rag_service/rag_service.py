
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

CHROMA_PATH = "chroma"
TEMPERATURE = 0.2

API_KEY = os.getenv("API_KEY")

PROMPT_TEMPLATE = """
Odpowiedz na pytanie tylko na podstawie poniższych informacji:
{context}
---
Odpowiedz na pytanie tylko na podstawie powyższego kontekstu: {question}
"""

# FastAPI app initialization
app = FastAPI(
    title="PharmaRAG Service",
    description="A RAG service for pharmaceutical information queries",
    version="1.0.0"
)

# Pydantic models for request/response
class RAGRequest(BaseModel):
    question: str

class RAGResponse(BaseModel):
    response: str
    sources: List[Optional[str]]

def query(query_text: str):
    # Prepare the DB.
    embedding_function = OpenAIEmbeddings(api_key=API_KEY)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        raise HTTPException(status_code=404, detail="Unable to find matching results.")

    def _fmt_chunk(doc):
        # Prefer direct h1/h2; fall back to parent_section if you stored it that way
        ps = doc.metadata.get("parent_section", {}) or {}
        h1 = doc.metadata.get("h1") or ps.get("h1") or ""
        h2 = doc.metadata.get("h2") or ps.get("h2") or ""
        src = doc.metadata.get("source") or doc.metadata.get("path") or doc.metadata.get("doc_id") or ""

        title_parts = [p for p in [h1, h2] if p]
        title = " > ".join(title_parts) if title_parts else "Fragment"

        header_lines = [f"## {title}"]
        if src:
            header_lines.append(f"[Source: {src}]")
        header = "\n".join(header_lines)

        body = doc.page_content.strip()
        return f"{header}\n{body}"

    context_text = "\n\n---\n\n".join([_fmt_chunk(doc) for doc, _score in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(f"\n\n PROMPT: \n\n{prompt}")
    model = ChatOpenAI(api_key=API_KEY, temperature=TEMPERATURE)
    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    return response_text, sources

@app.post("/rag/answer", response_model=RAGResponse)
async def get_rag_answer(request: RAGRequest):
    """
    Get RAG answer for a given question
    """
    try:
        response_text, sources = query(request.question)
        return RAGResponse(response=response_text, sources=sources)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "PharmaRAG"}

@app.get("/")
async def root():
    """
    Root endpoint with service information
    """
    return {
        "service": "PharmaRAG Service",
        "version": "1.0.0",
        "endpoints": {
            "rag_answer": "/rag/answer",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

