"""
test_matcher.py
================
Implements Section 28 ("What can be tested?") and Section 29 ("Testing
table") of the brief as REAL, automated pytest tests instead of a manually
filled-in table.

HOW TO RUN (from the project root, in VS Code's terminal):
    pytest -v

WHY THIS MATTERS FOR NCSC:
Anyone can claim "our system works." A judge can ask you to run this file
live, watch every test pass in front of them, and see the actual pass/fail
evidence — this is real measurable testing, not a claim.
"""

from backend.matcher import match


def test_tomato_aphids_pathway():
    """Test 1 (Section 29): correct plant+problem should give the aphid pathway."""
    result = match(plant="Tomato", problem="Aphids")
    assert result["matched"] is True
    assert result["case"]["id"] == "tomato_aphids"


def test_rose_powdery_mildew_pathway():
    """Test 2 (Section 29): different plant+problem gives a different pathway."""
    result = match(plant="Rose", problem="Powdery mildew")
    assert result["matched"] is True
    assert result["case"]["id"] == "rose_powdery_mildew"


def test_chilli_thrips_pathway():
    """Test 3 (Section 29): a third, distinct combination is matched correctly."""
    result = match(plant="Chilli", problem="Thrips")
    assert result["matched"] is True
    assert result["case"]["id"] == "chilli_thrips"


def test_context_changes_confidence():
    """
    Section 15: context should actually matter. The same plant+problem
    should score HIGHER when environment/season also match the case's
    documented context, proving the system isn't ignoring context.
    """
    with_context = match(plant="Tomato", problem="Aphids",
                          environment="Humid", season="Monsoon")
    without_context = match(plant="Tomato", problem="Aphids")
    assert with_context["score"] > without_context["score"]


def test_unknown_combination_does_not_invent_answer():
    """
    Test 5 (Section 29): an unsupported combination should trigger
    'insufficient context' rather than a false confident answer.
    """
    result = match(plant="Cactus", problem="Alien invasion")
    assert result["matched"] is False
    assert result["confidence"] == "Insufficient context"


def test_missing_required_fields_is_handled_gracefully():
    """Empty plant/problem should not crash the system."""
    result = match(plant="", problem="")
    assert result["matched"] is False


def test_every_case_has_required_fields():
    """
    A structural/data-quality test: every case in the knowledge base must
    have all the sections the result page depends on, so the UI never
    breaks on a missing field.
    """
    from backend.matcher import load_knowledge_base
    required_fields = [
        "plant", "problem", "affected_part", "environment", "season",
        "symptoms", "modern_knowledge", "sustainable_approaches",
        "iks_context", "precautions", "expert_guidance", "sources",
    ]
    kb = load_knowledge_base()
    for case in kb:
        for field in required_fields:
            assert field in case, f"Case '{case.get('id')}' missing field '{field}'"
            assert case[field], f"Case '{case.get('id')}' has empty field '{field}'"
