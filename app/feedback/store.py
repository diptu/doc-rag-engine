import json
import datetime
from pathlib import Path
from typing import Dict, Any, List
from app.generation.schemas import GenerationResponse


class FeedbackStore:
    def __init__(self, storage_path: str = "data/feedback_logs.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_interaction(
        self,
        query: str,
        original_response: GenerationResponse,
        human_edit: str,
        metadata: Dict[str, Any] = None,
    ):
        """Saves the delta between LLM and Human."""
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "query": query,
            "llm_draft": original_response.draft,
            "human_edit": human_edit,
            "citations": original_response.citations,
            "metadata": metadata or {},
        }

        with open(self.storage_path, "a") as f:
            f.write(json.dumps(record) + "\n")
