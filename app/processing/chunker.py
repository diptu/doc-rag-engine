from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TextChunker:
    """
    Splits document text into overlapping chunks while preserving
    page-level metadata for traceability.
    """

    chunk_size: int = 500
    overlap: int = 100

    def __post_init__(self) -> None:
        """Validate chunking configuration."""
        if self.chunk_size <= 0:
            msg = "chunk_size must be greater than 0"
            raise ValueError(msg)

        if self.overlap < 0:
            msg = "overlap cannot be negative"
            raise ValueError(msg)

        if self.overlap >= self.chunk_size:
            msg = "overlap must be smaller than chunk_size"
            raise ValueError(msg)

    def chunk_document(self, doc_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Processes a document dictionary and returns a list of chunk objects.

        Args:
            doc_data: Dictionary from DocumentLoader containing 'source' and 'pages'.

        Returns:
            List of dictionaries, each containing 'content' and 'metadata'.
        """
        chunks: list[dict[str, Any]] = []
        source: str = doc_data.get("source", "unknown")

        for page in doc_data.get("pages", []):
            text: str = page["content"]
            page_num: int = page["page_number"]

            start: int = 0
            text_length: int = len(text)

            while start < text_length:
                end: int = start + self.chunk_size
                chunk_text = text[start:end]

                chunks.append(
                    {
                        "content": chunk_text,
                        "metadata": {"source": source, "page_number": page_num},
                    }
                )

                # Move start pointer forward, accounting for overlap
                start += self.chunk_size - self.overlap

        return chunks
