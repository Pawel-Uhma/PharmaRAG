# PharmaRAG FastAPI Service

A FastAPI-based service that provides RAG (Retrieval-Augmented Generation) capabilities for pharmaceutical information queries.

## Features

- **RAG Endpoint**: POST `/rag/answer` - Get AI-generated answers based on pharmaceutical documents
- **Health Check**: GET `/health` - Service health monitoring
- **Root Endpoint**: GET `/` - Service information and available endpoints

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requrements.txt
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
  "sources": ["metformina.md", "other_source.md"]
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

## Testing

Run the test script to verify the service is working:

```bash
python test_service.py
```

## API Documentation

Once the service is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## Architecture

The service uses:
- **FastAPI** for the web framework
- **Chroma** as the vector database
- **OpenAI** for embeddings and language model
- **LangChain** for RAG orchestration

## Error Handling

- **404**: No matching results found in the database
- **500**: Internal server errors
- **422**: Validation errors for malformed requests

## Notes

- The service expects pharmaceutical documents to be ingested into the Chroma database
- Make sure your OpenAI API key has sufficient credits for embeddings and completions
- The service runs on port 8000 by default
