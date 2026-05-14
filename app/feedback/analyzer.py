import difflib
import json
import logging
from typing import Dict, Any, List
from .schemas import FeedbackCategory, FeedbackEntry

logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    def __init__(self, llm_client, model_name: str = "gpt-4o"):
        self.client = llm_client
        self.model_name = model_name

    def calculate_edit_distance(self, original: str, edited: str) -> float:
        """
        Calculates the Levenshtein-based similarity ratio.
        1.0 means identical, 0.0 means completely different.
        """
        return difflib.SequenceMatcher(None, original, edited).ratio()

    def get_diff_highlights(self, original: str, edited: str) -> Dict[str, List[str]]:
        """Identifies specific words added or removed by the human operator."""
        diff = difflib.ndiff(original.split(), edited.split())
        return {
            "added": [w[2:] for w in diff if w.startswith("+ ")],
            "removed": [w[2:] for w in diff if w.startswith("- ")],
        }

    async def analyze_and_map(
        self,
        interaction_id: str,
        query: str,
        original_draft: str,
        edited_version: str,
        context_ids: List[str],
        metadata: Dict[str, Any] = None,
    ) -> FeedbackEntry:
        """
        Orchestrates the full analysis flow:
        1. Calculates mechanical edit distance.
        2. Uses LLM to categorize the 'intent' behind the edit.
        3. Returns a validated FeedbackEntry object.
        """
        edit_ratio = self.calculate_edit_distance(original_draft, edited_version)

        # Skip LLM analysis if no changes were made to save tokens
        if edit_ratio > 0.99:
            category = FeedbackCategory.OTHER
        else:
            category = await self._get_category_from_llm(original_draft, edited_version)

        return FeedbackEntry(
            interaction_id=interaction_id,
            query=query,
            original_draft=original_draft,
            edited_version=edited_version,
            category=category,
            edit_ratio=edit_ratio,
            context_used=context_ids,
            metadata=metadata,
        )

    async def _get_category_from_llm(
        self, original: str, edited: str
    ) -> FeedbackCategory:
        """Internal helper to categorize the edit using LLM reasoning."""
        prompt = f"""
        Compare the LLM-generated draft and the human-edited version.
        Identify the PRIMARY reason for the human's changes.

        LLM Draft: {original}
        Human Edited: {edited}

        Rules:
        - FACTUAL: Human corrected a technical error or hallucination.
        - CLARITY: Human made the text easier to understand without changing facts.
        - STYLE: Human changed tone, brevity, or formatting.
        - CITATION: Human corrected a source reference.

        Return valid JSON with the key "category" matching one of the rules above.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert ML auditor."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            res_json = json.loads(response.choices[0].message.content)
            # Map string from LLM to FeedbackCategory Enum
            cat_str = res_json.get("category", "OTHER").lower()
            return FeedbackCategory(cat_str)

        except Exception as e:
            logger.error(f"Signal extraction failed: {e}")
            return FeedbackCategory.OTHER
