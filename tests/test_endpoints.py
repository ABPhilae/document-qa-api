"""Tests for the API endpoints."""


class TestHealthEndpoint:

    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_healthy(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_includes_document_count(self, client):
        data = client.get("/health").json()
        assert "documents_stored" in data


class TestDocumentEndpoints:

    def test_upload_document(self, client, clean_store):
        response = client.post("/documents", json={
            "title": "Test Doc",
            "content": "This is a test document with enough characters to pass validation."
        })
        assert response.status_code == 201
        assert "id" in response.json()

    def test_upload_rejects_short_content(self, client, clean_store):
        response = client.post("/documents", json={
            "title": "Short",
            "content": "Too short"
        })
        assert response.status_code == 422

    def test_list_documents(self, client, clean_store):
        # Upload two documents
        client.post("/documents", json={
            "title": "Doc 1",
            "content": "First document content that is long enough for validation."
        })
        client.post("/documents", json={
            "title": "Doc 2",
            "content": "Second document content that is long enough for validation."
        })

        response = client.get("/documents")
        assert response.status_code == 200
        assert response.json()["total_count"] == 2

    def test_get_document_by_id(self, client, clean_store):
        upload = client.post("/documents", json={
            "title": "Findable Doc",
            "content": "Content that we will retrieve later by its unique identifier."
        }).json()

        response = client.get(f"/documents/{upload['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == "Findable Doc"

    def test_get_nonexistent_returns_404(self, client, clean_store):
        response = client.get("/documents/nonexistent")
        assert response.status_code == 404

    def test_delete_document(self, client, clean_store):
        upload = client.post("/documents", json={
            "title": "Deletable",
            "content": "This document will be deleted in the next step of the test."
        }).json()

        response = client.delete(f"/documents/{upload['id']}")
        assert response.status_code == 200

        # Verify it's gone
        response = client.get(f"/documents/{upload['id']}")
        assert response.status_code == 404


class TestQuestionEndpoint:

    def test_ask_rejects_nonexistent_document(self, client, clean_store):
        response = client.post("/documents/nonexistent/ask", json={
            "question": "What is this about?"
        })
        assert response.status_code == 404

    def test_ask_rejects_short_question(self, client, clean_store, sample_document):
        upload = client.post("/documents", json=sample_document).json()
        response = client.post(f"/documents/{upload['id']}/ask", json={
            "question": "Hi"
        })
        assert response.status_code == 422
