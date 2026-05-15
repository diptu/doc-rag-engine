import pytest

from app.processing.loader import DocumentLoader


class TestDocumentLoader:
    @pytest.fixture
    def loader(self):
        return DocumentLoader()

    def test_loader_initialization(self, loader):
        """Verifies that the loader correctly identifies Tesseract availability."""
        assert hasattr(loader, "_tesseract_available")
        assert isinstance(loader._tesseract_available, bool)

    def test_loader_returns_correct_structure(self, loader):
        """Ensures the loader returns the new structured dictionary schema."""
        path = "tests/files/single_page.pdf"
        result = loader.load(path)

        assert isinstance(result, dict)
        assert result["source"] == path
        assert "metadata" in result
        assert "pages" in result
        # 'text' key is intentionally removed in favor of structured 'pages'
        assert "text" not in result

    def test_loader_handles_single_page_pdf(self, loader):
        """Validates extraction and metadata for single-page documents."""
        result = loader.load("tests/files/single_page.pdf")
        pages = result["pages"]
        metadata = result["metadata"]

        assert metadata["page_count"] == 1
        assert len(pages) == 1
        assert pages[0]["page_number"] == 1
        assert "single page document" in pages[0]["content"].lower()

    def test_loader_handles_multipage_pdf(self, loader):
        """Validates sequential extraction and per-page metadata trace."""
        result = loader.load("tests/files/multipage.pdf")
        pages = result["pages"]
        metadata = result["metadata"]

        assert metadata["page_count"] == 2
        assert len(pages) == 2

        # Verify page 1
        assert pages[0]["page_number"] == 1
        assert "page one" in pages[0]["content"].lower()

        # Verify page 2
        assert pages[1]["page_number"] == 2
        assert "page two" in pages[1]["content"].lower()

    def test_loader_cleaning_integration(self, loader):
        """Verifies that the TextCleaner is applied to page content."""
        result = loader.load("tests/files/single_page.pdf")
        page_content = result["pages"][0]["content"]

        # Ensure normalization logic (like stripping) is applied
        assert page_content == page_content.strip()
        assert "\n\n\n" not in page_content

    def test_loader_file_not_found(self, loader):
        """Ensures the loader raises a RuntimeError for missing files."""
        with pytest.raises(RuntimeError, match="Failed to open PDF"):
            loader.load("tests/files/non_existent.pdf")
