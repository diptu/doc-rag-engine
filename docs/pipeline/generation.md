# Draft Generation

The generation module transforms retrieved evidence into professional, legal-style draft outputs. Its primary mandate is to ensure every statement is strictly grounded in the underlying source material.

## Drafting Philosophy

We prioritize accuracy and utility over creative prose. The goal is to provide an operator with a "first-pass" output that requires minimal correction.

* **Fact-Grounded Output**: The engine is configured to only generate text based on the provided retrieval context. If the source documents do not contain the necessary information, the system is designed to acknowledge the gap rather than make assumptions.
* **Persona Alignment**: Drafts are formatted as internal memos or case summaries, maintaining a professional and objective tone suitable for a law firm environment.
* **Traceable Assertions**: The system logic ensures that generated drafts follow the structural logic of the source evidence.

## Implementation Details

* **Prompt Engineering (`prompt.py`)**: Contains the core logic for framing the drafting task. It includes strict instructions for grounding and style consistency.
* **Generator (`generator.py`)**: Manages the interaction with the language model, injecting the retrieved context and ensuring the output conforms to the required schema.
* **Schemas (`schemas.py`)**: Defines the structured format of the draft to ensure consistent API responses.

## Evaluation Focus

This module is assessed based on:
* **Groundedness**: The absence of unsupported assumptions or "hallucinations."
* **Utility**: The overall quality and structure of the draft as a functional starting point for an operator.