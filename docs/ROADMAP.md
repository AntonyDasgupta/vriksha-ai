# VRIKSHA-AI Roadmap

VRIKSHA-AI is being built in three phases. Each phase is independently
useful, and each builds on the one before without requiring the previous
phase to be rewritten.

## Phase 1 — Text-based (current)

**Deliverable:** Structured and free-text input → deterministic matcher →
rendered recommendation combining modern agronomy, sustainable IPM, and
Indian Knowledge Systems.

**Why this comes first:**
Recent systematic reviews of CNN-based plant disease detection
(Shafay et al., 2025; Mehta et al., 2025; Demilie, 2024) report
laboratory accuracies of 95–99% but field deployment accuracies of only
70–85%. The gap is driven by lighting variation, background clutter,
geographic bias in training data, and class imbalance. Hardware cost
alone (USD 500–2000 for RGB systems; USD 20,000–50,000 for hyperspectral)
excludes most smallholder contexts.

A deterministic, explainable text-and-context system that runs on any
smartphone and works offline is therefore both more reliable and more
equitable as a starting point. It is also the only phase whose content
can be fully sourced to peer-reviewed agronomy and traditional texts.

## Phase 2 — Image-based extension

**Deliverable:** An optional image-upload path where the user photographs
a leaf, a lightweight pretrained CNN (MobileNetV2 or EfficientNetB0)
returns a *suggested* problem label, and that label is fed into the same
deterministic matcher as a structured input.

**Critical design constraint:**
The image model is a **triage signal**, not a diagnosis. A 70%–85%
field-accurate model must never produce a confident wrong answer. The
knowledge base remains the authority; the CNN only pre-fills the
`problem` field for a case that the matcher already supports.

**Why this is defensible:**
- Shafay et al. (2025) *Plant Methods* 21:140 — laboratory vs field gap analysis
- Mehta et al. (2025) *Indian Journal of Agricultural Research* — systematic review of ML/DL methods
- Demilie (2024) *Journal of Big Data* 11:5 — comparative survey of CNN/ML performance
- Sun et al. (2022) *Cognitive Robotics* — FL-EfficientNet architecture reference

**Datasets to start from:**
- PlantVillage (54,303 images; 38 classes) — lab-condition baseline
- PlantDoc (2,598 images; 27 classes) — real-field validation
- FieldPlant (5,170 images; 27 classes) — natural backgrounds

## Phase 3 — Mobile application

**Deliverable:** A React Native or Flutter frontend that talks to the
*same* FastAPI backend over HTTP. No backend code changes required.

**Why the architecture already supports this:**
The frontend has never imported backend Python code — it only calls
`/match`, `/match/freetext`, `/cases`, and `/ui-strings/{lang}` over HTTP.
This is the entire reason for the split between `frontend/app.py` and
`backend/`. A mobile app can replace the Streamlit UI without touching
any backend file.

**Planned mobile features:**
- Offline mode via local caching of the knowledge base
- Voice input via the platform's speech-to-text API
- Camera integration for Phase 2 image upload
- Hindi, Bengali, and English UI (already supported by the backend)

## Cross-phase commitments

Regardless of phase, the following remain constant:

1. **The knowledge base is the authority.** Every claim is traceable to a
   primary or peer-reviewed source, and every IKS claim is labelled
   `paraphrase` or `direct_reference`.
2. **The matcher is deterministic.** No AI model chooses a case.
3. **The AI layer only rephrases.** If no API key is set, the app still
   works.
4. **Uncertainty is shown, never hidden.** Confidence labels and
   verification-status fields are visible to the user.