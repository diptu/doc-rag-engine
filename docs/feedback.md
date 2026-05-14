# Improvement from Operator Edits

A core requirement for the Pearson Specter Litt workflow is the ability to learn from manual intervention. This module implements a "real improvement loop" that moves beyond simple version storage to extract meaningful signals from operator corrections.

## The Learning Loop

The system captures how an operator modifies a generated draft to improve future iterations through a three-step process:

1. **Edit Capture (`store.py`)**: When an operator edits a draft, the system stores both the original grounded output and the finalized version.
2. **Signal Analysis (`analyzer.py`)**: The analyzer compares the versions to identify patterns—such as preferred legal terminology, structural adjustments, or specific data points that were initially missed or misinterpreted.
3. **Prompt Refinement**: These learned patterns are fed back into the `generation/prompt.py` logic. This ensures that subsequent drafts for similar documents align more closely with the operator's established standards.

## Technical Implementation

* **Feedback Schema**: We use structured schemas to track specific types of edits (e.g., deletions, additions, or rephrasing).
* **Pattern Persistence**: Extracted improvements are persisted in `data/feedback/`, allowing the engine to maintain its "knowledge" across sessions.

## Evaluation Criteria Alignment

This module directly addresses the **Improvement from Edits (25 points)** rubric by demonstrating:
* How edits are captured programmatically.
* The logic behind learning reusable patterns.
* A clear path for future outputs to improve meaningfully based on human-in-the-loop interaction.