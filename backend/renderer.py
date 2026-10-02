"""
renderer.py
===========
Transforms a matched knowledge-base case into the structured recommendation
layout the frontend displays. This is a PURE presentation layer — it does
not diagnose anything and does not call any AI API.

DESIGN PRINCIPLE (why this file exists):
The KB stores knowledge in a source-traceable form (each iks_context claim
labelled "paraphrase" or "direct_reference" with a citation). The renderer
reshapes that into the display layout WITHOUT adding, softening, or
strengthening any claim. Whatever the KB says about evidence level, the
renderer shows as-is.

This is what lets a judge compare a case's KB entry with its rendered
output and see the same wording — no hidden editorialising.
"""

from typing import Optional


def _normalise_sustainable_options(approaches: list) -> list[dict]:
    """
    Accept either the old format (list of strings) or the new format
    (list of {action, cost, availability}) and return the new format.
    """
    out = []
    for item in approaches:
        if isinstance(item, str):
            out.append({
                "action": item,
                "cost": "Not specified",
                "availability": "Not specified",
            })
        else:
            out.append({
                "action": item.get("action", ""),
                "cost": item.get("cost", "Not specified"),
                "availability": item.get("availability", "Not specified"),
            })
    return out


def _normalise_iks(iks) -> dict:
    """
    Accept either the old string format or the new structured format and
    return a renderable dict with principle / practice / seasonal blocks.
    """
    if isinstance(iks, str):
        # Old format: single string. Wrap as paraphrase without a citation.
        return {
            "principle": {
                "statement": iks,
                "source_type": "paraphrase",
                "source_note": "Legacy format — source not structured."
            },
            "specific_practice": None,
            "seasonal_principle": None,
            "relevance_to_this_case": None,
            "verification_status": "Legacy entry — not structured.",
        }

    return {
        "principle": iks.get("principle"),
        "specific_practice": iks.get("specific_practice"),
        "seasonal_principle": iks.get("seasonal_principle"),
        "relevance_to_this_case": iks.get("relevance_to_this_case"),
        "verification_status": iks.get("verification_status", ""),
    }


def _build_why(user_context: dict, case: dict) -> str:
    """
    Construct the "why this result?" line from the context the user
    actually supplied, plus the matched case's plant/problem.
    """
    bits = [case.get("plant", "")]
    if user_context.get("affected_part"):
        bits.append(f"{user_context['affected_part'].lower()} symptoms")
    if case.get("problem"):
        bits.append(case["problem"].lower() + "-like presentation")
    if user_context.get("growing_condition"):
        bits.append(user_context["growing_condition"].lower() + " environment")
    if user_context.get("environment"):
        bits.append(user_context["environment"].lower() + " conditions")
    if user_context.get("season"):
        bits.append(user_context["season"].lower() + " season")
    return " + ".join(b for b in bits if b) + " matched this recommendation pathway."


def render_recommendation(case: dict, confidence: str, user_context: dict) -> dict:
    """
    Given a matched case, a confidence label, and the user's original
    context dict, return the structured recommendation payload the
    frontend renders.
    """
    return {
        "matched": True,
        "confidence": confidence,
        "problem_summary": f"{case['plant']} — {case['problem']}",

        # Section 1: What to do (numbered priorities)
        "priority_actions": case.get("priority_actions", []),

        # Section 2: Sustainable options with cost + availability
        "sustainable_options": _normalise_sustainable_options(
            case.get("sustainable_approaches", [])
        ),

        # Section 3: IKS block, structured
        "iks": _normalise_iks(case.get("iks_context", "")),

        # Section 4: Connection between modern and traditional
        "connection": case.get("connection", ""),

        # Section 5: Monitoring guidance
        "monitor": case.get("monitor", "Observe the plant for 7-10 days after the recommended action."),

        # Section 6: When to seek expert help
        "seek_expert_if": case.get("seek_expert_if", []),

        # Section 7: Why this result (built from user's context)
        "why": _build_why(user_context, case),

        # Section 8: Sources
        "sources": case.get("sources", []),

        # Extra: surface the symptoms and verification note for judges
        "symptoms": case.get("symptoms", []),
        "sources_verification_status": case.get("sources_verification_status", ""),
    }