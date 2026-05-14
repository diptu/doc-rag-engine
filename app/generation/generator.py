import json
import logging
import tiktoken
from typing import List, Dict, Any
from .prompt import RAG_SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .schemas import GenerationResponse

# Initialize logging for ML monitoring
logger = logging.getLogger(__name__)


class RAGGenerator:
    def __init__(
        self, model_client, model_name: str = "gpt-4o", token_limit: int = 4096
    ):
        """
        Args:
            model_client: The LLM client (e.g., OpenAI).
            model_name: Name of the model for tokenization logic.
            token_limit: Maximum allowed tokens for the context injection.
        """
        self.client = model_client
        self.model_name = model_name
        self.token_limit = token_limit
        try:
            self.encoder = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, text: str) -> int:
        """Calculates token count to prevent context window overflow."""
        return len(self.encoder.encode(text))

    def _format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Orchestrates retrieved chunks and applies token-based truncation
        to stay within the engineering constraints of the LLM.
        """
        formatted_chunks = []
        current_tokens = 0

        # Reserve tokens for system prompt and user query (approx 500)
        effective_limit = self.token_limit - 500

        for i, chunk in enumerate(retrieved_chunks):
            chunk_id = chunk.get("metadata", {}).get("source_id", f"idx_{i}")
            content = chunk.get("content", "")

            formatted_entry = f"[Source: {chunk_id}] Content: {content}"
            entry_tokens = self._count_tokens(formatted_entry)

            if current_tokens + entry_tokens > effective_limit:
                logger.warning(f"Context limit reached. Truncating at chunk {i}.")
                break

            formatted_chunks.append(formatted_entry)
            current_tokens += entry_tokens

        return "\n\n".join(formatted_chunks)

    def generate(
        self, query: str, retrieved_chunks: List[Dict[str, Any]]
    ) -> GenerationResponse:
        """
        Orchestration flow: Context Injection -> LLM Inference -> Pydantic Validation.
        """
        context_text = self._format_context(retrieved_chunks)

        # Build user prompt
        user_content = USER_PROMPT_TEMPLATE.format(
            context_text=context_text, query=query
        )

        try:
            # LLM Call with Strict JSON Mode
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for grounded engineering tasks
            )

            raw_content = response.choices[0].message.content
            parsed_data = json.loads(raw_content)

            # Validate against Pydantic schema
            validated_response = GenerationResponse(**parsed_data)

            logger.info(
                f"Generation successful. Confidence: {validated_response.confidence_score}"
            )
            return validated_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM output as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during Grounded Generation: {e}")
            raise
