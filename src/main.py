"""
Document Q&A API - Main Application.

Endpoints:
  GET  /health              - Service health check
  POST /documents           - Upload a new document
  GET  /documents           - List all documents
  GET  /documents/{id}      - Get a specific document
  DELETE /documents/{id}    - Delete a document
  POST /documents/{id}/ask  - Ask a question about a document
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
import logging

from src.config import settings
from src.models import (
    DocumentUploadRequest,
    DocumentMetadata,
    DocumentDetail,
    DocumentListResponse,
    QuestionRequest,
    AnswerResponse,
    Confidence,
    HealthResponse,
)
from src.document_store import document_store
from src.qa_service import qa_service


# ================================================================
# SETUP
# ================================================================
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Upload documents and ask questions about their content. "
        "The AI answers based ONLY on the document, not general knowledge."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# HEALTH CHECK
# ================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the service is running and report stats."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        documents_stored=document_store.count(),
        timestamp=datetime.utcnow().isoformat(),
    )


# ================================================================
# DOCUMENT ENDPOINTS (CRUD)
# ================================================================

@app.post("/documents", response_model=DocumentMetadata, status_code=201)
async def upload_document(request: DocumentUploadRequest):
    """
    Upload a new document.

    The document is stored in memory and can then be queried
    using the /documents/{id}/ask endpoint.
    """
    # Check if we have reached the document limit
    if document_store.count() >= settings.max_documents:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum number of documents ({settings.max_documents}) reached. "
                   f"Please delete some documents first.",
        )

    doc_id = document_store.add(
        content=request.content,
        title=request.title,
    )

    doc = document_store.get(doc_id)

    return DocumentMetadata(
        id=doc_id,
        title=doc["title"],
        word_count=doc["word_count"],
        character_count=doc["character_count"],
        created_at=doc["created_at"],
    )


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents (metadata only, not content)."""
    docs = document_store.list_all()
    return DocumentListResponse(
        documents=[DocumentMetadata(**d) for d in docs],
        total_count=len(docs),
    )


@app.get("/documents/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: str):
    """Get a specific document by ID, including its full content."""
    doc = document_store.get(doc_id)

    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {doc_id}. "
                   f"Use GET /documents to see available documents.",
        )

    return DocumentDetail(
        id=doc_id,
        title=doc["title"],
        content=doc["content"],
        word_count=doc["word_count"],
        character_count=doc["character_count"],
        created_at=doc["created_at"],
    )


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document by ID."""
    deleted = document_store.delete(doc_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {doc_id}",
        )

    return {"message": f"Document {doc_id} deleted successfully"}


# ================================================================
# Q&A ENDPOINT
# ================================================================

@app.post("/documents/{doc_id}/ask", response_model=AnswerResponse)
async def ask_question(doc_id: str, request: QuestionRequest):
    """
    Ask a question about a specific document.

    The AI will answer based ONLY on the document content.
    If the information is not in the document, it will say so.
    """
    # First, check if the document exists
    doc = document_store.get(doc_id)

    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {doc_id}. "
                   f"Upload a document first using POST /documents.",
        )

    start_time = time.time()

    try:
        # Call the Q&A service
        result = qa_service.answer_question(
            document_content=doc["content"],
            question=request.question,
            document_title=doc["title"],
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return AnswerResponse(
            answer=result.get("answer", "Unable to generate answer"),
            confidence=Confidence(result.get("confidence", "low")),
            relevant_quotes=result.get("relevant_quotes", []),
            not_found=result.get("not_found", False),
            document_title=doc["title"],
            question=request.question,
            model_used=settings.openai_model,
            processing_time_ms=elapsed_ms,
        )

    except ValueError as e:
        logger.error(f"Q&A processing error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected Q&A error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. "
                   "Please try again.",
        )


# ================================================================
# STARTUP
# ================================================================

@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Model: {settings.openai_model}")
    logger.info(f"Max documents: {settings.max_documents}")
