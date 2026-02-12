"""
Data models for the Document Q&A API.

This API has TWO main resources:
1. Documents - users upload, list, get, and delete documents
2. Questions - users ask questions about specific documents
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ================================================================
# DOCUMENT MODELS
# ================================================================

class DocumentUploadRequest(BaseModel):
    """What the user sends to upload a new document."""
    content: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="The text content of the document"
    )
    title: str = Field(
        default="Untitled Document",
        max_length=200,
        description="A title for the document"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Q4 Audit Report",
                    "content": "This report covers the audit findings for Q4 2025..."
                }
            ]
        }
    }


class DocumentMetadata(BaseModel):
    """Metadata about a stored document (returned in list view)."""
    id: str
    title: str
    word_count: int
    character_count: int
    created_at: str


class DocumentDetail(BaseModel):
    """Full document detail including content."""
    id: str
    title: str
    content: str
    word_count: int
    character_count: int
    created_at: str


class DocumentListResponse(BaseModel):
    """Response for listing all documents."""
    documents: List[DocumentMetadata]
    total_count: int


# ================================================================
# Q&A MODELS
# ================================================================

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class QuestionRequest(BaseModel):
    """A question about a specific document."""
    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Your question about the document"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"question": "What were the main findings?"}
            ]
        }
    }


class AnswerResponse(BaseModel):
    """The AI answer to a question."""
    answer: str = Field(description="The AI-generated answer")
    confidence: Confidence = Field(description="How confident the AI is")
    relevant_quotes: List[str] = Field(
        default_factory=list,
        description="Direct quotes from the document supporting the answer"
    )
    not_found: bool = Field(
        default=False,
        description="True if the answer was not in the document"
    )
    document_title: str
    question: str
    model_used: str
    processing_time_ms: float


# ================================================================
# GENERAL MODELS
# ================================================================

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    documents_stored: int
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
