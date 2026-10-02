"""
text_extractor.py
==================
Implements Section 7 of the brief: a free-text box where a user can type
something like "My tomato plant has tiny insects under the leaves and the
weather is humid" and have the system pull out structured context from it.

DESIGN CHOICE: this uses simple keyword matching, NOT an AI call.
Why: it's fast, free, fully explainable to a judge, and works offline.
An AI-based version could replace this later (see ai_synthesis.py for
where that boundary is), but starting with keyword matching keeps your
core pipeline deterministic and demo-safe (no API downtime risk on stage).
"""

import re
from backend.matcher import load_knowledge_base

# Keyword -> canonical value maps. Extend these lists as you add more cases.
ENVIRONMENT_KEYWORDS = {
    "Humid": ["humid", "humidity", "moist"],
    "Dry": ["dry", "arid"],
    "Hot": ["hot", "heat"],
    "Cool": ["cool", "cold"],
    "Rainy": ["rain", "rainy", "raining", "monsoon rain"],
    "Indoor": ["indoor", "inside", "indoors"],
    "Outdoor": ["outdoor", "outside", "outdoors"],
}

SEASON_KEYWORDS = {
    "Summer": ["summer"],
    "Monsoon": ["monsoon", "rainy season"],
    "Winter": ["winter"],
    "Spring": ["spring"],
}

PART_KEYWORDS = {
    "Leaf": ["leaf", "leaves"],
    "Stem": ["stem", "stems", "shoot", "shoots"],
    "Root": ["root", "roots"],
    "Flower": ["flower", "flowers", "bud", "buds"],
    "Fruit": ["fruit", "fruits"],
    "Whole plant": ["whole plant", "entire plant"],
}


def _find_keyword(text: str, keyword_map: dict) -> str | None:
    text_lower = text.lower()
    for canonical, variants in keyword_map.items():
        for variant in variants:
            if re.search(r"\b" + re.escape(variant) + r"\b", text_lower):
                return canonical
    return None


def extract_context_from_text(text: str) -> dict:
    """
    Given a free-text description, try to extract: plant, problem,
    affected_part, environment, season.

    Plant and problem are matched against the actual names present in the
    knowledge base, so this function grows automatically as you add cases —
    you never have to maintain a separate plant/problem keyword list.
    """
    kb = load_knowledge_base()
    text_lower = text.lower()

    plant_match = None
    problem_match = None
    for case in kb:
        if not plant_match and re.search(r"\b" + re.escape(case["plant"].lower()) + r"\b", text_lower):
            plant_match = case["plant"]
        if not problem_match and re.search(r"\b" + re.escape(case["problem"].lower()) + r"\b", text_lower):
            problem_match = case["problem"]

    return {
        "plant": plant_match,
        "problem": problem_match,
        "affected_part": _find_keyword(text, PART_KEYWORDS),
        "environment": _find_keyword(text, ENVIRONMENT_KEYWORDS),
        "season": _find_keyword(text, SEASON_KEYWORDS),
    }


if __name__ == "__main__":
    sample = "My tomato plant has tiny insects under the leaves and the weather is humid."
    print(extract_context_from_text(sample))
