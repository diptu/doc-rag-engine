import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.feedback.analyzer import FeedbackAnalyzer
from app.feedback.schemas import FeedbackCategory, FeedbackEntry


@pytest.fixture
def mock_llm_client():
    """Provides a mocked async LLM client."""
    client = MagicMock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def analyzer(mock_llm_client):
    return FeedbackAnalyzer(mock_llm_client)


def test_edit_distance_calculation(analyzer):
    """Verifies that the mechanical edit distance is accurate."""
    original = "The model uses ResNet-50."
    edited = "The model uses ResNet-101."

    ratio = analyzer.calculate_edit_distance(original, edited)
    assert 0.0 < ratio < 1.0

    # Test identical strings
    assert analyzer.calculate_edit_distance("Same", "Same") == 1.0


def test_diff_highlights(analyzer):
    """Checks if the added/removed words are correctly identified."""
    original = "CNNs are fast"
    edited = "CNNs are extremely fast"

    diffs = analyzer.get_diff_highlights(original, edited)
    assert "extremely" in diffs["added"]
    assert len(diffs["removed"]) == 0


@pytest.mark.asyncio
async def test_analyze_and_map_full_flow(analyzer, mock_llm_client):
    """Tests the full orchestration from raw interaction to validated FeedbackEntry."""

    # Mock LLM response for categorization
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({"category": "FACTUAL"})
    mock_llm_client.chat.completions.create.return_value = mock_response

    interaction_id = "test_123"
    query = "How many layers in ResNet-50?"
    original = "It has 100 layers."
    edited = "It has 50 layers."
    context_ids = ["he_et_al_2015"]

    entry = await analyzer.analyze_and_map(
        interaction_id=interaction_id,
        query=query,
        original_draft=original,
        edited_version=edited,
        context_ids=context_ids,
    )

    # Assertions
    assert isinstance(entry, FeedbackEntry)
    assert entry.interaction_id == interaction_id
    assert entry.category == FeedbackCategory.FACTUAL
    assert entry.edit_ratio < 1.0
    assert "he_et_al_2015" in entry.context_used


@pytest.mark.asyncio
async def test_skip_llm_on_no_changes(analyzer, mock_llm_client):
    """Engineering Optimization: Ensure LLM is not called if there are no edits."""

    await analyzer.analyze_and_map(
        interaction_id="ident_1",
        query="No change query",
        original_draft="The sky is blue.",
        edited_version="The sky is blue.",
        context_ids=[],
    )

    # Verify the LLM was never contacted
    mock_llm_client.chat.completions.create.assert_not_called()


def test_invalid_feedback_schema():
    """Ensures Pydantic catches invalid data (e.g., impossible edit_ratio)."""
    with pytest.raises(ValueError):
        FeedbackEntry(
            interaction_id="id",
            query="q",
            original_draft="o",
            edited_version="e",
            edit_ratio=1.5,  # Invalid: ge=0.0, le=1.0
            context_used=[],
        )
