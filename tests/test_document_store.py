"""Tests for the document store module."""


class TestDocumentStore:

    def test_add_document(self, clean_store):
        """Adding a document should return an ID."""
        doc_id = clean_store.add("Test content here", "Test Doc")
        assert doc_id is not None
        assert len(doc_id) == 8

    def test_get_document(self, clean_store):
        """Should retrieve a stored document."""
        doc_id = clean_store.add("Test content", "My Doc")
        doc = clean_store.get(doc_id)
        assert doc is not None
        assert doc["title"] == "My Doc"
        assert doc["content"] == "Test content"

    def test_get_nonexistent_returns_none(self, clean_store):
        """Getting a non-existent document should return None."""
        result = clean_store.get("nonexistent")
        assert result is None

    def test_list_documents(self, clean_store):
        """Should list all documents with metadata."""
        clean_store.add("Content 1", "Doc 1")
        clean_store.add("Content 2", "Doc 2")
        docs = clean_store.list_all()
        assert len(docs) == 2
        # List should not include content (only metadata)
        assert "content" not in docs[0]

    def test_delete_document(self, clean_store):
        """Deleting should remove the document."""
        doc_id = clean_store.add("Content", "Title")
        assert clean_store.delete(doc_id) is True
        assert clean_store.get(doc_id) is None

    def test_delete_nonexistent_returns_false(self, clean_store):
        """Deleting non-existent doc should return False."""
        assert clean_store.delete("nonexistent") is False

    def test_count(self, clean_store):
        """Count should track number of documents."""
        assert clean_store.count() == 0
        clean_store.add("Content", "Title")
        assert clean_store.count() == 1
