"""
Shared test configuration and fixtures.

Fixtures are reusable setup functions that pytest automatically
injects into your test functions. This avoids repeating setup
code in every test.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.document_store import document_store


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def clean_store():
    """Reset the document store before each test."""
    document_store._documents.clear()
    yield document_store
    document_store._documents.clear()


@pytest.fixture
def sample_document():
    """Return sample document content for testing."""
    return {
        "title": "Test Audit Report",
        "content": (
            "Internal Audit Report Q3 2025. "
            "The audit identified three critical findings in the APAC "
            "trade reconciliation system. Finding 1: Timestamp mismatch "
            "between Hong Kong and Singapore offices affecting 345 trades "
            "per day. Finding 2: Missing 12 of 47 required HKMA validation "
            "rules. Finding 3: Three former employees retained system "
            "access for an average of 47 days after departure. All critical "
            "findings must be remediated by March 31, 2026."
        ),
    }

