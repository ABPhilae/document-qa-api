"""
Document Store - In-memory storage for uploaded documents.

ARCHITECTURE NOTE:
This module uses a simple Python dictionary for storage.
In production, you would replace this with:
  - PostgreSQL for structured document metadata
  - ChromaDB or Pinecone for vector-based semantic search
  - Redis for caching frequently accessed documents

The interface (add, get, list, delete) stays the same regardless
of the underlying storage. This is the 'Repository Pattern' -
a very common design pattern in professional software.
"""
from datetime import datetime
from typing import Optional, Dict, List
import uuid
import logging

logger = logging.getLogger(__name__)


class DocumentStore:
    """
    In-memory document storage.

    WARNING: Data is lost when the server restarts.
    This is intentional for learning purposes.
    In Phase 2, you will replace this with a persistent database.
    """

    def __init__(self):
        self._documents: Dict[str, dict] = {}
        logger.info("Document store initialized (in-memory)")

    def add(self, content: str, title: str = "Untitled") -> str:
        """
        Store a new document.

        Args:
            content: The full text of the document
            title: A human-readable title

        Returns:
            The unique document ID (8 characters)
        """
        doc_id = str(uuid.uuid4())[:8]

        self._documents[doc_id] = {
            "content": content,
            "title": title,
            "word_count": len(content.split()),
            "character_count": len(content),
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Document stored: id={doc_id}, title={title}, "
                    f"{len(content)} chars")
        return doc_id

    def get(self, doc_id: str) -> Optional[dict]:
        """
        Retrieve a document by ID.

        Returns None if the document does not exist.
        This is safer than raising an exception because
        the calling code can decide how to handle 'not found'.
        """
        doc = self._documents.get(doc_id)
        if doc:
            logger.info(f"Document retrieved: {doc_id}")
        else:
            logger.warning(f"Document not found: {doc_id}")
        return doc

    def get_content(self, doc_id: str) -> Optional[str]:
        """Get only the document content (used for Q&A)."""
        doc = self._documents.get(doc_id)
        return doc["content"] if doc else None

    def list_all(self) -> List[dict]:
        """
        List all documents (metadata only, not content).

        Returns metadata only to keep responses small.
        If you have 100 documents, you don't want to
        send all their full content in one response.
        """
        return [
            {
                "id": doc_id,
                "title": doc["title"],
                "word_count": doc["word_count"],
                "character_count": doc["character_count"],
                "created_at": doc["created_at"],
            }
            for doc_id, doc in self._documents.items()
        ]

    def delete(self, doc_id: str) -> bool:
        """
        Delete a document by ID.

        Returns True if the document existed and was deleted,
        False if it was not found.
        """
        if doc_id in self._documents:
            title = self._documents[doc_id]["title"]
            del self._documents[doc_id]
            logger.info(f"Document deleted: {doc_id} ({title})")
            return True
        logger.warning(f"Delete failed - document not found: {doc_id}")
        return False

    def count(self) -> int:
        """Return the number of stored documents."""
        return len(self._documents)


# Single shared instance
document_store = DocumentStore()
