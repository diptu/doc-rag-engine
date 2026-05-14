import pytest
import json
from unittest.mock import MagicMock
from app.generation.generator import RAGGenerator
from app.generation.schemas import GenerationResponse

# ML-Specific Mock Data: Simulating retrieved chunks from a Deep Learning paper
MOCK_ML_CHUNKS = [
    {
        "content": "ResNet-50 utilizes residual connections to mitigate the vanishing gradient problem in deep networks.",
        "metadata": {"source_id": "he_et_al_2015", "page": 4},
    },
    {
        "content": "The bottleneck design in ResNet-50 consists of 1x1, 3x3, and 1x1 convolutions to reduce parameter count.",
        "metadata": {"source_id": "resnet_docs", "section": "architecture"},
    },
]


@pytest.fixture
def generator_instance():
    """Provides a RAGGenerator with a mocked LLM client and Pydantic validation."""
    mock_client = MagicMock()

    # Mocking a valid RAG response focusing on ML architecture
    content_json = json.dumps(
        {
            "draft": "ResNet-50 addresses vanishing gradients using residual connections and optimizes parameters via a bottleneck design.",
            "citations": ["he_et_al_2015", "resnet_docs"],
            "confidence_score": 0.98,
        }
    )

    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = content_json
    # Initializing with a small token limit for testing truncation
    return RAGGenerator(mock_client, token_limit=4096), mock_client


def test_ml_context_serialization(generator_instance):
    """Verify that ML-specific metadata and technical terms are preserved in context injection."""
    generator, _ = generator_instance
    formatted = generator._format_context(MOCK_ML_CHUNKS)

    assert "[Source: he_et_al_2015]" in formatted
    assert "vanishing gradient" in formatted
    assert "bottleneck design" in formatted


def test_token_truncation_logic(generator_instance):
    """Ensures the generator respects the token limit and drops excessive chunks."""
    mock_client = MagicMock()
    # Set an artificially low limit to force truncation
    small_limit_gen = RAGGenerator(mock_client, token_limit=100)

    # Large chunk that exceeds 100 tokens
    large_chunks = [
        {
            "content": "Extremely long text... " * 50,
            "metadata": {"source_id": "long_doc"},
        }
    ]

    formatted = small_limit_gen._format_context(large_chunks)
    assert (
        formatted == ""
    )  # Should be empty because the single chunk exceeded the reserved safety buffer


def test_grounded_ml_synthesis_object(generator_instance):
    """Ensure the generator returns a validated GenerationResponse object (not a dict)."""
    generator, _ = generator_instance
    query = "Explain the architecture of ResNet-50."

    result = generator.generate(query, MOCK_ML_CHUNKS)

    # Now asserting against Pydantic model attributes
    assert isinstance(result, GenerationResponse)
    assert "residual connections" in result.draft.lower()
    assert "he_et_al_2015" in result.citations
    assert result.confidence_score >= 0.9


def test_pydantic_validation_error(generator_instance):
    """Checks that a ValidationError (via Pydantic) is raised if the LLM returns bad data types."""
    generator, mock_client = generator_instance

    # Mock invalid data: confidence_score as a string instead of a float
    bad_json = json.dumps(
        {"draft": "Bad data", "citations": [], "confidence_score": "high"}
    )
    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = bad_json

    with pytest.raises(Exception):  # Pydantic will raise ValidationError
        generator.generate("Query", MOCK_ML_CHUNKS)


def test_llm_hyperparameter_integrity(generator_instance):
    """Validates that ML system instructions and temperature are correctly sent."""
    generator, mock_client = generator_instance
    query = "How do residual blocks work?"

    generator.generate(query, MOCK_ML_CHUNKS)

    _, kwargs = mock_client.chat.completions.create.call_args

    # Check Engineering Constraints
    assert kwargs["temperature"] == 0.1
    assert kwargs["response_format"] == {"type": "json_object"}

    messages = kwargs.get("messages", [])
    system_prompt = messages[0]["content"]
    assert "grounding" in system_prompt.lower()


def test_zero_shot_hallucination_prevention(generator_instance):
    """Test behavior when no relevant chunks are provided."""
    generator, mock_client = generator_instance

    no_info_json = json.dumps(
        {
            "draft": "I do not have enough information.",
            "citations": [],
            "confidence_score": 0.0,
        }
    )
    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = no_info_json

    result = generator.generate("What about Transformer-XL?", [])
    assert "do not have enough information" in result.draft
    assert len(result.citations) == 0
