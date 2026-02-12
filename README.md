# Document Q&A API

An AI-powered API that lets you upload documents and ask natural
language questions about their content. The AI answers based
**only** on the document, not general knowledge.

Built as part of my AI Engineering learning journey - this is a
simplified RAG (Retrieval-Augmented Generation) system using
FastAPI and OpenAI.

## Features

- **Document Management**: Upload, list, retrieve, and delete documents
- **AI-Powered Q&A**: Ask questions and get answers grounded in document content
- **Confidence Scoring**: Each answer includes a confidence level
- **Source Quotes**: Relevant document passages are included in responses
- **Hallucination Prevention**: AI explicitly states when information is not found
- **Health Monitoring**: Built-in health check endpoint
- **Dockerized**: Run anywhere with Docker Compose

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/document-qa-api.git
cd document-qa-api

# Configure
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run
docker-compose up --build

# Open http://localhost:8000/docs for interactive API documentation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Service health check |
| POST | /documents | Upload a new document |
| GET | /documents | List all documents |
| GET | /documents/{id} | Get document details + content |
| DELETE | /documents/{id} | Delete a document |
| POST | /documents/{id}/ask | Ask a question about a document |

## Tech Stack

- **Python 3.11** + **FastAPI** - High-performance async API framework
- **OpenAI API** (gpt-4o-mini) - AI language model
- **Pydantic v2** - Data validation and serialization
- **Docker** + **Docker Compose** - Containerized deployment
- **pytest** - Automated testing

## Architecture

```
User Request -> FastAPI (validation) -> Q&A Service (prompt engineering)
                                              |
                                    Document Store (retrieval)
                                              |
                                    OpenAI API (generation)
                                              |
                                    Structured Response (Pydantic)
```

## Running Tests

```bash
pytest tests/ -v
```

## Next Steps (Phase 2)

This project will be upgraded with:
- Vector database (ChromaDB) for semantic document search
- Document chunking and embeddings
- Proper RAG pipeline with relevant passage retrieval
- Conversation memory across multiple questions

