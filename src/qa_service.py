"""
Q&A Service - Document-grounded question answering.

This is the CORE of the application. It implements the pattern:
  User Question + Document Content -> Grounded Answer

WHY THIS MATTERS:
Without grounding, an AI answers from general knowledge and may
hallucinate (make things up). By providing the document as context,
we constrain the AI to answer ONLY from the provided text.
This is the fundamental principle behind RAG systems.
"""
from src.llm_service import llm_service
from src.config import settings
from src.models import AnswerResponse, Confidence
import logging

logger = logging.getLogger(__name__)


# ================================================================
# SYSTEM PROMPT
# ================================================================
# This prompt is carefully designed to:
# 1. Force the AI to answer ONLY from the document
# 2. Admit when information is not found (instead of making it up)
# 3. Return structured JSON we can parse
# 4. Include supporting quotes for transparency

QA_SYSTEM_PROMPT = """You are a precise document analyst working in a
financial services environment. You answer questions ONLY based on
the document provided. You prioritize accuracy over helpfulness -
it is better to say "not found" than to guess.

STRICT RULES:
1. ONLY use information explicitly stated in the document
2. If the answer is NOT in the document, say so clearly
3. Include short relevant quotes from the document to support your answer
4. If the question is ambiguous, state what you found and note the ambiguity
5. NEVER use external knowledge - only what is in the document

RESPONSE FORMAT - Return ONLY valid JSON with this structure:
{
  "answer": "Your answer based on the document",
  "confidence": "high or medium or low",
  "relevant_quotes": ["short quote 1 from document", "short quote 2"],
  "not_found": false
}

If the information is NOT in the document:
{
  "answer": "This information is not present in the provided document.",
  "confidence": "high",
  "relevant_quotes": [],
  "not_found": true
}

CONFIDENCE GUIDELINES:
- high: The answer is directly and clearly stated in the document
- medium: The answer requires some interpretation or inference
- low: The document only partially addresses the question"""


class QAService:
    """Service for answering questions based on document content."""

    def answer_question(
        self, document_content: str, question: str, document_title: str
    ) -> dict:
        """
        Answer a question based on a specific document.

        Args:
            document_content: The full text of the document
            question: The user's question
            document_title: Title of the document (for logging)

        Returns:
            dict: Parsed JSON with answer, confidence, quotes, not_found
        """
        logger.info(
            f"Answering question about \"{document_title}\": "
            f"\"{question[:80]}...\""
        )

        # ---- CONTEXT WINDOW MANAGEMENT ----
        # The AI has a limited context window (how much text it can process).
        # Sending a 100-page document wastes tokens and reduces quality.
        # In Phase 2, you'll use vector search to find only relevant chunks.
        # For now, we simply truncate if too long.
        max_chars = settings.context_max_chars
        if len(document_content) > max_chars:
            logger.warning(
                f"Document truncated from {len(document_content)} "
                f"to {max_chars} chars"
            )
            document_content = document_content[:max_chars]
            document_content += "\n\n[... Document truncated for processing ...]"

        # ---- BUILD THE PROMPT ----
        # We use clear delimiters (=== DOCUMENT ===) so the AI knows
        # exactly where the document starts and ends.
        # This prevents the AI from confusing the question with the document.
        prompt = (
            f"=== DOCUMENT TITLE: {document_title} ===\n\n"
            f"{document_content}\n\n"
            f"=== END OF DOCUMENT ===\n\n"
            f"=== QUESTION ===\n"
            f"{question}\n"
            f"=== END OF QUESTION ===\n\n"
            f"Answer the question using ONLY the document above."
        )

        # ---- CALL THE AI ----
        result = llm_service.generate_json(
            prompt=prompt,
            system_message=QA_SYSTEM_PROMPT,
            temperature=0.1,  # Very low for maximum accuracy
        )

        logger.info(
            f"Answer generated: confidence={result.get('confidence')}, "
            f"not_found={result.get('not_found', False)}"
        )

        return result


# Single shared instance
qa_service = QAService()
