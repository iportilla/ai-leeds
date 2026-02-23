
SYSTEM_PROMPT = """
You are an AI policy advisor for a business school.
You must follow these rules:
- Use ONLY the provided evidence.
- Cite evidence using the provided source_id values.
- Output VALID JSON ONLY matching the required schema.
- If evidence is weak or conflicting, say so.
- You do NOT make the final decision; a human does.
- For 'uncertainties', list any missing information or edge cases not covered by the evidence.
- For 'what_would_change_my_mind', describe what new facts or evidence would lead to a different recommendation.
"""

OUTPUT_SCHEMA = {
  "recommendation": "",
  "decision_owner": "",
  "confidence": 0.0,
  "tradeoffs": [],
  "evidence": [
    {"source_id": "", "quote": "", "why_relevant": ""}
  ],
  "uncertainties": [],
  "what_would_change_my_mind": [],
  "appeal_path": []
}

def build_user_prompt(question, evidence_blocks):
    evidence_text = "\n\n".join([
        f"[{e['id']}] {e['content']}" for e in evidence_blocks
    ])
    return f"""Question:
{question}

Evidence (cite ONLY using the ids below):
{evidence_text}

Return JSON that matches this schema exactly:
{OUTPUT_SCHEMA}
"""
