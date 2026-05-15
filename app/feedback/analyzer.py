import difflib
import json
import logging
from typing import Any, Dict, List

from .schemas import FeedbackCategory, FeedbackEntry
from .store import FeedbackStore  # Import the store

logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    def __init__(self, llm_client, model_name: str = "gpt-4o"):
        self.client = llm_client
        self.model_name = model_name
        # Initialize the store to persist analysis results
        self.store = FeedbackStore()

    def calculate_edit_distance(self, original: str, edited: str) -> float:
        return difflib.SequenceMatcher(None, original, edited).ratio()

    async def analyze_and_map(
        self, interaction_id, query, original_draft, edited_version, context_ids
    ):
        # 1. Calculate the actual ratio (Character-based similarity)
        # Original (83 chars) vs Edited (215 chars)
        edit_ratio = self.calculate_edit_distance(original_draft, edited_version)

        # DEBUG: Add a print here to see it in your terminal
        print(f"DEBUG: Calculated edit_ratio for {interaction_id} is {edit_ratio}")

        # 2. Get category from LLM
        category = await self._get_category_from_llm(original_draft, edited_version)

        # 3. Create the entry using the CALCULATED ratio, not a default
        entry = FeedbackEntry(
            interaction_id=interaction_id,
            query=query,
            original_draft=original_draft,
            edited_version=edited_version,
            category=category,
            edit_ratio=edit_ratio,  # Ensure this is the variable from step 1
            context_used=context_ids,
        )

        # 4. Save to store
        self.store.save_feedback(entry.model_dump())

    async def _get_category_from_llm(
        self, original: str, edited: str
    ) -> FeedbackCategory:
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
            # FIX: Ensure we await the async client
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert ML auditor."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            res_json = json.loads(response.choices[0].message.content)
            cat_str = res_json.get("category", "OTHER").lower()

            # Map string to enum safely
            try:
                return FeedbackCategory(cat_str)
            except ValueError:
                return FeedbackCategory.OTHER

        except Exception as e:
            logger.error(f"Signal extraction failed: {e}")
            return FeedbackCategory.OTHER
