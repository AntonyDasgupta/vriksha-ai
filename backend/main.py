"""
main.py
=======
The FastAPI application. This is the single entry point the frontend
(web today, mobile later) talks to over HTTP.

Endpoints:
  GET  /health                    — health check
  GET  /ui-strings/{language}     — translated UI strings
  GET  /cases                      — list of supported plant/problem cases
  POST /match                      — structured-input matching
  POST /match/freetext             — free-text matching
  POST /feedback                   — usefulness feedback
  GET  /feedback                   — view collected feedback

The /match and /match/freetext endpoints return a RENDERED recommendation
(see renderer.py), not the raw KB case. This keeps the frontend layout
logic centralised in one place and identical across the web and future
mobile frontends.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.matcher import match, list_supported_cases, load_knowledge_base
from backend.text_extractor import extract_context_from_text
from backend.translations import get_ui_strings
from backend.ai_synthesis import synthesize
from backend.renderer import render_recommendation
from backend.models import MatchRequest, FreeTextRequest, FeedbackRequest
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
from backend.image_classifier import classifier

app = FastAPI(
    title="VRIKSHA-AI API",
    description="Context-aware plant-care knowledge API combining modern "
                 "agricultural knowledge, sustainable approaches and Indian "
                 "Knowledge Systems (Vrikshayurveda).",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_feedback_log: list[dict] = []


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ui-strings/{language}")
def ui_strings(language: str):
    return get_ui_strings(language)


@app.get("/cases")
def get_cases():
    return list_supported_cases()


@app.post("/match")
def match_context(req: MatchRequest):
    """Structured-input matching. Returns a rendered recommendation."""
    user_context = {
        "plant": req.plant,
        "problem": req.problem,
        "affected_part": req.affected_part,
        "environment": req.environment,
        "season": req.season,
        "growing_condition": req.growing_condition,
    }
    result = match(**user_context)

    if not result["matched"]:
        return result  # unchanged "insufficient context" shape

    # Optional AI rephrasing of the raw case (only if API key set)
    case = synthesize(result["case"])

    # Rendered recommendation
    rendered = render_recommendation(case, result["confidence"], user_context)
    rendered["case_id"] = case.get("id")
    return rendered


@app.post("/match/freetext")
def match_freetext(req: FreeTextRequest):
    """Extract context from free text, then run the same pipeline."""
    extracted = extract_context_from_text(req.text)
    if not extracted["plant"] or not extracted["problem"]:
        return {
            "matched": False,
            "confidence": "Insufficient context",
            "extracted_context": extracted,
            "message": (
                "Could not confidently identify both the plant and the problem "
                "from the description. Try naming the plant and the specific "
                "problem (e.g. 'aphids', 'leaf spot') more directly, or use the "
                "structured form instead."
            ),
        }

    result = match(**extracted)
    if not result["matched"]:
        result["extracted_context"] = extracted
        return result

    case = synthesize(result["case"])
    rendered = render_recommendation(case, result["confidence"], extracted)
    rendered["case_id"] = case.get("id")
    rendered["extracted_context"] = extracted
    return rendered


@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    valid_ids = {c["id"] for c in list_supported_cases()}
    if req.case_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Unknown case_id")
    _feedback_log.append(req.model_dump())
    return {"status": "recorded", "total_feedback_count": len(_feedback_log)}


@app.get("/feedback")
def get_feedback():
    return _feedback_log


@app.post("/match/image")
async def match_image(
    file: UploadFile = File(...),
    affected_part: Optional[str] = Form(None),
    environment: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    growing_condition: Optional[str] = Form(None),
    language: Optional[str] = Form("en")
):
    """
    Accepts an uploaded image file, identifies plant and disease, 
    and uses the deterministic matcher to fetch the recommendation.
    """
    # 1. Read file bytes
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image file uploaded.")

    # 2. Run Image Classification Model
    prediction = classifier.predict(contents)
    
    plant = prediction["extracted_plant"]
    problem = prediction["extracted_problem"]

    if not plant or not problem:
        return {
            "matched": False,
            "confidence": "Insufficient context",
            "prediction_info": prediction,
            "message": f"Detected class '{prediction['predicted_class']}', but no matching knowledge base case exists."
        }

    # 3. Match against Knowledge Base deterministically
    user_context = {
        "plant": plant,
        "problem": problem,
        "affected_part": affected_part,
        "environment": environment,
        "season": season,
        "growing_condition": growing_condition,
    }
    
    result = match(**user_context)

    if not result["matched"]:
        result["prediction_info"] = prediction
        return result

    # 4. Synthesize (Optional LLM rephrasing) & Render
    case = synthesize(result["case"])
    rendered = render_recommendation(case, result["confidence"], user_context)
    rendered["case_id"] = case.get("id")
    rendered["prediction_info"] = prediction
    
    return rendered