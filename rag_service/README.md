# PharmaRAG FastAPI Service

A FastAPI-based service that provides RAG (Retrieval-Augmented Generation) capabilities for pharmaceutical information queries.

## Features

- **RAG Endpoint**: POST `/rag/answer` - Get AI-generated answers based on pharmaceutical documents

## Architecture

The service is organized into modular components:

- **`rag_service.py`** - Main orchestrator and FastAPI application
- **`ask.py`** - OpenAI service for RAG queries and embeddings

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file in the parent directory with your OpenAI API key:
   ```
   API_KEY=your_openai_api_key_here
   ```

3. **Start the service**:
   ```bash
   python rag_service.py
   ```
   
   The service will start on `http://localhost:8000`

## API Usage

### RAG Answer Endpoint

**POST** `/rag/answer`

Request body:
```json
{
  "question": "Jakie są skutki uboczne metforminy?"
}
```

Response:
```json
{
  "response": "AI-generated answer based on pharmaceutical documents...",
  "sources": ["metformina", "other_source"],
  "metadata": [
    {
      "h1": "Metformina",
      "h2": "Skutki uboczne",
      "source": "metformina.md",
      "relevance_score": 0.85,
      "chunk_content": "Metformina może powodować..."
    }
  ]
}
```

### Health Check

**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "service": "PharmaRAG"
}
```

### Service Information

**GET** `/`

Response:
```json
{
  "service": "PharmaRAG Service",
  "version": "1.0.0",
  "endpoints": {
    "rag_answer": "/rag/answer",
    "health": "/health"
  }
}
```

## Architecture

The service uses:
- **FastAPI** for the web framework
- **Chroma** as the vector database
- **OpenAI** for embeddings and language model
- **LangChain** for RAG orchestration

## Notes

- The Chroma database is already populated with pharmaceutical documents
- Make sure your OpenAI API key has sufficient credits for embeddings and completions
- The service runs on port 8000 by default
- CORS is enabled for localhost:3000 for frontend integration
