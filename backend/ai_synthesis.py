"""
ai_synthesis.py
================
This is the ONLY file in the whole backend that calls an external AI API.
Everywhere else in the project (matcher.py, text_extractor.py) is plain,
deterministic Python.

WHAT THIS FILE DOES: it takes an ALREADY-MATCHED case from matcher.py and
asks Claude to phrase it as smoother, more natural sentences for the result
screen. It does NOT ask Claude to diagnose the problem, and it is explicitly
instructed not to add facts that are not already in the matched case.

WHY THIS BOUNDARY MATTERS FOR NCSC:
This is exactly the "Layer 3 - AI Assistance" from Section 16 of your brief.
AI organises/rephrases already-researched knowledge; it does not generate
the knowledge itself. You can show a judge this file and say: "the AI never
sees the full knowledge base and never picks the case — it only receives
one matched case and rewrites it in plain language."

SETUP:
1. Get an API key from https://console.anthropic.com (Anthropic's developer
   console). This is a DIFFERENT key from a claude.ai subscription.
2. Put it in a file called `.env` in the project root (see .env.example):
       ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
3. This file loads it via python-dotenv, so it never gets hardcoded or
   committed to GitHub (see .gitignore).

THIS LAYER IS OPTIONAL: the app works perfectly well without it — main.py
falls back to returning the matched case's fields exactly as written if no
API key is configured, or if the call fails. Never make the core demo
depend on network access to a paid API.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    import anthropic
    _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) \
        if os.getenv("ANTHROPIC_API_KEY") else None
except ImportError:
    _client = None


SYSTEM_PROMPT = """You are a rephrasing assistant for an agricultural knowledge app.
You will be given a JSON object containing ALREADY-RESEARCHED plant-care information.
Your ONLY job is to rewrite the fields into warmer, clearer, more natural sentences
for a farmer or home gardener to read.

STRICT RULES:
- Do NOT add any fact, cause, treatment, or claim that is not already present in the input JSON.
- Do NOT mention percentages, guarantees, or certainty beyond what is given.
- Keep the same section structure as the input.
- Keep each section under 3 sentences.
- If a field is a list, you may combine it into flowing sentences, but do not drop any item.
- Output plain text for each section, no markdown, no extra commentary.
Return ONLY a JSON object with the same keys as the input, and rewritten string values."""


def synthesize(case: dict) -> dict:
    """
    Rephrase a matched knowledge-base case using Claude.
    Falls back to the original case (unchanged) if no API key is set or
    the call fails for any reason — the app must never break because of this.
    """
    if _client is None:
        return case  # No API key configured — return original researched text.

    fields_to_rewrite = {
        "symptoms": case.get("symptoms"),
        "modern_knowledge": case.get("modern_knowledge"),
        "sustainable_approaches": case.get("sustainable_approaches"),
        "iks_context": case.get("iks_context"),
        "precautions": case.get("precautions"),
        "expert_guidance": case.get("expert_guidance"),
    }

    try:
        response = _client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": str(fields_to_rewrite)}
            ],
        )
        text = response.content[0].text
        import json
        rewritten = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
        merged = {**case, **rewritten}
        return merged
    except Exception as e:
        print(f"[ai_synthesis] Falling back to original text due to: {e}")
        return case
