from __future__ import annotations

import pytest
from app.processing.chunker import TextChunker


class TestTextChunker:
    """Test suite for TextChunker validating metadata-aware segmentation."""

    @pytest.fixture
    def sample_doc(self):
        """Mock document structure matching DocumentLoader.load() output."""
        return {
            "source": "tests/files/multipage.pdf",
            "pages": [
                {"page_number": 1, "content": "abcdefghij"},  # 10 chars
                {"page_number": 2, "content": "klmnopqrst"},  # 10 chars
            ],
        }

    def test_should_split_document_into_metadata_chunks(self, sample_doc) -> None:
        """Validates that chunks contain correct content and page metadata."""
        chunker = TextChunker(chunk_size=5, overlap=1)
        result = chunker.chunk_document(sample_doc)

        # Total expected chunks: 3 from page 1 ("abcde", "efghi", "ij")
        # + 3 from page 2 ("klmno", "opqrs", "st")
        assert len(result) == 6

        # Verify first chunk of first page
        assert result[0]["content"] == "abcde"
        assert result[0]["metadata"]["page_number"] == 1
        assert result[0]["metadata"]["source"] == "tests/files/multipage.pdf"

        # Verify first chunk of second page
        assert result[3]["content"] == "klmno"
        assert result[3]["metadata"]["page_number"] == 2

    def test_should_return_single_chunk_for_short_page(self) -> None:
        """Ensures short pages don't produce unnecessary splits."""
        doc = {"source": "test.pdf", "pages": [{"page_number": 1, "content": "hello"}]}
        chunker = TextChunker(chunk_size=10, overlap=2)
        result = chunker.chunk_document(doc)

        assert len(result) == 1
        assert result[0]["content"] == "hello"

    def test_should_handle_empty_pages(self) -> None:
        """Ensures the chunker gracefully ignores pages with no content."""
        doc = {"source": "empty.pdf", "pages": [{"page_number": 1, "content": ""}]}
        chunker = TextChunker()
        result = chunker.chunk_document(doc)

        assert result == []

    @pytest.mark.parametrize(
        ("chunk_size", "overlap"),
        [
            (0, 0),
            (-1, 0),
            (5, 5),
            (5, 10),
            (5, -1),
        ],
    )
    def test_should_raise_value_error_for_invalid_config(
        self,
        chunk_size: int,
        overlap: int,
    ) -> None:
        """Validates configuration guardrails in __post_init__."""
        with pytest.raises(ValueError):
            TextChunker(chunk_size=chunk_size, overlap=overlap)
