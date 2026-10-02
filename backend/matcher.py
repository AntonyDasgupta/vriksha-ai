"""
matcher.py
==========
This is the "brain" of VRIKSHA-AI, and deliberately contains NO calls to any
AI/LLM API. It is pure, deterministic Python.

WHY THIS MATTERS FOR YOUR PROJECT:
Judges at NCSC will ask "is this just ChatGPT with a plant theme?". This file
is your proof that it isn't. Given a user's context (plant, problem, part,
environment, season), it scores every case in the knowledge base and returns
the best match(es) with a confidence label — using simple, explainable rules,
not a black-box model. You can open this file in front of a judge and explain
exactly why a result was chosen.

The AI layer (see ai_synthesis.py) is only ever given the ALREADY-MATCHED
case from this file. It cannot invent a case that doesn't exist here.
"""

import json
from pathlib import Path
from typing import Optional


# Path to the knowledge base file, relative to this file's location.
# Using Path(__file__).parent makes this work no matter where you run
# the script from — a common beginner gotcha is hardcoding a path that
# only works from one folder.
KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"


def load_knowledge_base(path: Path = KB_PATH) -> list[dict]:
    """Load and return the list of cases from the knowledge base JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]


def _text_match_score(user_value: Optional[str], case_value: str) -> float:
    """Score a simple case-insensitive exact match between two single values."""
    if not user_value:
        return 0.0
    return 1.0 if user_value.strip().lower() == case_value.strip().lower() else 0.0


def _list_overlap_score(user_value: Optional[str], case_values: list[str]) -> float:
    """
    Score whether a single user-selected value (e.g. 'Humid') appears in a
    case's list of relevant values (e.g. ['Humid', 'Rainy']).
    Returns 1.0 for a hit, 0.0 for no hit or no user input.
    """
    if not user_value:
        return 0.0
    lowered = [v.strip().lower() for v in case_values]
    return 1.0 if user_value.strip().lower() in lowered else 0.0


def score_case(case: dict, plant: str, problem: str, affected_part: Optional[str] = None,
               environment: Optional[str] = None, season: Optional[str] = None,
               growing_condition: Optional[str] = None) -> float:
    """
    Compute a weighted match score (0.0 to 1.0) between user input and one
    knowledge base case.

    WEIGHTING LOGIC (this is the "context-aware" part of the project):
    - Plant match and Problem match are the two most important signals
      (0.35 each) because they identify WHICH case we are even talking about.
    - Affected part, environment, season and growing condition are secondary
      signals (smaller weights) that refine confidence and demonstrate that
      context shapes the result, even when plant+problem are already fixed.
    """
    weights = {
        "plant": 0.35,
        "problem": 0.35,
        "affected_part": 0.10,
        "environment": 0.10,
        "season": 0.05,
        "growing_condition": 0.05,
    }

    score = 0.0
    score += weights["plant"] * _text_match_score(plant, case["plant"])
    score += weights["problem"] * _text_match_score(problem, case["problem"])
    score += weights["affected_part"] * _list_overlap_score(affected_part, case["affected_part"])
    score += weights["environment"] * _list_overlap_score(environment, case["environment"])
    score += weights["season"] * _list_overlap_score(season, case["season"])
    score += weights["growing_condition"] * _list_overlap_score(growing_condition, case["growing_condition"])

    return round(score, 4)


def confidence_label(score: float) -> str:
    """
    Convert a numeric score into a human-readable confidence label.
    This directly implements Section 20 of the project brief: the system
    should show uncertainty rather than pretending to be 100% certain.
    """
    if score >= 0.65:
        return "Strong contextual match"
    elif score >= 0.40:
        return "Partial contextual match"
    elif score > 0.0:
        return "Weak match — limited context available"
    else:
        return "No match found"


def match(plant: str, problem: str, affected_part: Optional[str] = None,
          environment: Optional[str] = None, season: Optional[str] = None,
          growing_condition: Optional[str] = None,
          kb: Optional[list[dict]] = None) -> dict:
    """
    The main entry point. Given user context, return the best-matching case
    plus a confidence label, or an "insufficient context" response.

    This is the function the API (main.py) and the tests both call.
    """
    if kb is None:
        kb = load_knowledge_base()

    if not plant or not problem:
        return {
            "matched": False,
            "confidence": "Insufficient context",
            "message": "Please provide at least a plant/crop and a problem to get a result.",
        }

    scored = [(score_case(c, plant, problem, affected_part, environment, season,
                           growing_condition), c) for c in kb]
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_case = scored[0]

    # A minimum threshold before we're willing to show ANY result.
    # This is Section 20 / Section 28 Test 5 in your brief: an unsupported
    # combination should not produce a confident, made-up answer.
    if best_score < 0.30:
        return {
            "matched": False,
            "confidence": "Insufficient context",
            "message": (
                "No sufficiently confident match was found for this combination "
                "in the current knowledge base. This prototype currently covers "
                f"{len(kb)} researched plant/problem cases; try one of the "
                "supported combinations, or this may be a case we haven't "
                "researched yet."
            ),
        }

    return {
        "matched": True,
        "confidence": confidence_label(best_score),
        "score": best_score,
        "case": best_case,
    }


def list_supported_cases(kb: Optional[list[dict]] = None) -> list[dict]:
    """Return a lightweight list of (plant, problem) pairs the KB currently supports.
    Used by the frontend to build dropdowns and by judges to see coverage at a glance."""
    if kb is None:
        kb = load_knowledge_base()
    return [{"id": c["id"], "plant": c["plant"], "problem": c["problem"]} for c in kb]


if __name__ == "__main__":
    # Quick manual smoke test — run this file directly with:
    #   python backend/matcher.py
    # to sanity-check matching without needing the API or frontend running.
    result = match(plant="Tomato", problem="Aphids", affected_part="Leaf",
                    environment="Humid", season="Monsoon")
    print(json.dumps(result, indent=2))
