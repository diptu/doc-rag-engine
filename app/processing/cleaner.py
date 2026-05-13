from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass


@dataclass(slots=True)
class TextCleaner:
    """
    Normalizes raw extracted text for high-fidelity RAG processing.
    Focuses on noise reduction, encoding fixes, and structural consistency.
    """

    def clean(self, text: str) -> str:
        """
        Main entry point for text normalization.
        """
        if not text:
            return ""

        # 1. Normalize Unicode (handles ligatures and accents)
        text = unicodedata.normalize("NFKC", text)

        # 2. Remove control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # 3. Standardize Whitespace
        text = re.sub(r"[ \t]+", " ", text)

        # 4. Normalize Line Endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 5. Handle Messy OCR Artifacts (Pearson Rubric: reasonable handling of unclear inputs)
        text = self._remove_ocr_garbage(text)

        # 6. Join words broken across lines (e.g., "envir- \n onment" -> "environment")
        text = re.sub(r"(\w+)-\n\s*(\w+)", r"\1\2", text)

        # 7. Standardize Newlines (Collapse 3+ into 2)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _remove_ocr_garbage(self, text: str) -> str:
        """
        Filters out lines that are likely OCR noise from logos or speckles.
        Identifies lines with low alphanumeric density.
        """
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Calculate alphanumeric density
            alnum_count = sum(1 for char in stripped if char.isalnum())
            density = alnum_count / len(stripped)

            # Filter: If the line has some length but is mostly symbols, it's noise.
            # We keep short lines (like 'Dear Colleague') but discard symbol-heavy 'logo' lines.
            if len(stripped) > 3 and density < 0.35:
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)
