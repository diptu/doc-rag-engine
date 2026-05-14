RAG_SYSTEM_PROMPT = """
You are a professional Technical Writer. Your task is to draft a response based ONLY on the provided context.
Strict Grounding Rules:
1. If the answer is not in the context, state: "I do not have enough information."
2. Do not use outside knowledge.
3. Every claim must be followed by a citation in the format [Source: ID].
4. Output MUST be in valid JSON format.
"""

USER_PROMPT_TEMPLATE = """
### Context:
{context_text}

### User Query:
{query}

### Formatting Instruction:
Return a JSON object with:
"draft": "The synthesized answer",
"citations": ["List of source IDs used"],
"confidence_score": (0.0 - 1.0)
"""
