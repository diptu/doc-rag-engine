import json
import datetime
from pathlib import Path
from typing import Dict, Any, List


class FeedbackStore:
    def __init__(self, storage_path: str = "data/feedback_logs.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_feedback(self, entry: Dict[str, Any]):
        """
        Appends a complete FeedbackEntry (including analysis) to the log.
        Uses default=str to handle datetime and Enum serialization.
        """
        # Ensure a timestamp exists and is in a serializable format
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.datetime.utcnow().isoformat()
        elif isinstance(entry["timestamp"], datetime.datetime):
            entry["timestamp"] = entry["timestamp"].isoformat()

        with open(self.storage_path, "a") as f:
            # default=str handles datetime, Enums, and UUIDs by converting them to strings
            f.write(json.dumps(entry, default=str) + "\n")

    def get_stats(self) -> Dict[str, Any]:
        """
        Parses the logs to generate alignment metrics.
        """
        if not self.storage_path.exists():
            return {
                "total_interactions_analyzed": 0,
                "status": "No feedback data available yet.",
            }

        stats = {
            "total_interactions_analyzed": 0,
            "alignment_metrics": {
                "average_edit_ratio": 0.0,
                "total_corrections_submitted": 0,
            },
            "category_distribution": {},
            "status": "Active",
        }

        total_ratio = 0.0
        count = 0

        with open(self.storage_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    count += 1

                    # Aggregate categories (Factual vs Style)
                    # Note: Enums saved as strings via default=str will match here
                    category = entry.get("category", "unclassified")
                    stats["category_distribution"][category] = (
                        stats["category_distribution"].get(category, 0) + 1
                    )

                    # Accumulate edit ratio for averaging
                    total_ratio += entry.get("edit_ratio", 0.0)
                except json.JSONDecodeError:
                    continue

        if count > 0:
            stats["total_interactions_analyzed"] = count
            stats["alignment_metrics"]["total_corrections_submitted"] = count
            stats["alignment_metrics"]["average_edit_ratio"] = round(
                total_ratio / count, 3
            )

            # Simple heuristic for health status
            if stats["alignment_metrics"]["average_edit_ratio"] > 0.8:
                stats["status"] = "High Alignment - Minimal corrections needed"
            else:
                stats["status"] = "Active Alignment - Model requires frequent tuning"

        return stats
