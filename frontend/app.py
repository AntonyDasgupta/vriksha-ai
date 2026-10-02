"""
app.py (Streamlit frontend)
============================
Web UI. Talks to FastAPI over HTTP only. The backend returns a rendered
recommendation (see backend/renderer.py) — this file just displays it.

HOW TO RUN (from the project root, in a SEPARATE terminal from the backend):
    streamlit run frontend/app.py
"""

import streamlit as st
import requests

# API_URL = "http://127.0.0.1:8000"
API_URL = "https://vriksha-ai-backend.onrender.com"

st.set_page_config(page_title="VRIKSHA-AI", page_icon="🌿", layout="centered")


# --- Language selection ---
LANGUAGES = {"English": "en", "हिन्दी": "hi", "বাংলা": "bn"}
lang_display = st.sidebar.selectbox("Language / भाषा / ভাষা", list(LANGUAGES.keys()))
lang_code = LANGUAGES[lang_display]


@st.cache_data(ttl=60)
def get_ui_strings(language: str) -> dict:
    resp = requests.get(f"{API_URL}/ui-strings/{language}")
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=60)
def get_supported_cases() -> list:
    resp = requests.get(f"{API_URL}/cases")
    resp.raise_for_status()
    return resp.json()


try:
    ui = get_ui_strings(lang_code)
    cases = get_supported_cases()
except requests.exceptions.ConnectionError:
    st.error(
        "⚠️ Cannot reach the backend API. Make sure it's running:\n\n"
        "`uvicorn backend.main:app --reload`\n\nin a separate terminal, "
        "then refresh this page."
    )
    st.stop()


# --- Header ---
st.title(f"🌿 {ui['app_title']}")
st.subheader(ui["app_subtitle"])
st.caption(ui["tagline"])
st.divider()


# --- Input section ---
plants = sorted(set(c["plant"] for c in cases))
tab_structured, tab_freetext, tab_image = st.tabs(["📋 Structured input", "⌨️ Describe in your own words","📷 Upload Leaf Image"])

result = None

with tab_structured:
    col1, col2 = st.columns(2)
    with col1:
        plant = st.selectbox(ui["plant_label"], plants)
        problems_for_plant = sorted(set(c["problem"] for c in cases if c["plant"] == plant))
        problem = st.selectbox(ui["problem_label"], problems_for_plant)
        part = st.selectbox(ui["part_label"],
                             ["", "Leaf", "Stem", "Root", "Flower", "Fruit", "Whole plant"])
    with col2:
        environment = st.selectbox(ui["environment_label"],
                                    ["", "Humid", "Dry", "Hot", "Cool", "Rainy", "Indoor", "Outdoor"])
        season = st.selectbox(ui["season_label"], ["", "Summer", "Monsoon", "Winter", "Spring"])
        condition = st.selectbox(ui["condition_label"],
                                  ["", "Pot", "Garden", "Field", "Terrace", "Nursery"])

    if st.button(ui["submit_button"], type="primary", key="structured_submit"):
        payload = {
            "plant": plant, "problem": problem,
            "affected_part": part or None, "environment": environment or None,
            "season": season or None, "growing_condition": condition or None,
            "language": lang_code,
        }
        result = requests.post(f"{API_URL}/match", json=payload).json()

with tab_freetext:
    free_text = st.text_area(
        ui["freetext_label"],
        placeholder="e.g. My tomato plant has tiny insects under the leaves and the weather is humid.",
        height=100,
    )
    if st.button(ui["submit_button"], type="primary", key="freetext_submit"):
        if free_text.strip():
            result = requests.post(
                f"{API_URL}/match/freetext",
                json={"text": free_text, "language": lang_code},
            ).json()
        else:
            st.warning("Please type a description first.")

with tab_image:
    st.write("Upload a clear photo of the infected leaf or plant part.")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    # Optional additional context dropdowns to refine confidence
    col1, col2 = st.columns(2)
    with col1:
        img_part = st.selectbox(ui["part_label"], ["", "Leaf", "Stem", "Fruit"], key="img_part")
        img_env = st.selectbox(ui["environment_label"], ["", "Humid", "Dry", "Hot", "Cool"], key="img_env")
    with col2:
        img_season = st.selectbox(ui["season_label"], ["", "Summer", "Monsoon", "Winter", "Spring"], key="img_season")
        img_condition = st.selectbox(ui["condition_label"], ["", "Pot", "Garden", "Field"], key="img_condition")

    if st.button("Analyze Image & Get Solution", type="primary", key="image_submit"):
        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {
                "affected_part": img_part or None,
                "environment": img_env or None,
                "season": img_season or None,
                "growing_condition": img_condition or None,
                "language": lang_code
            }
            
            with st.spinner("Analyzing image and fetching diagnostic recommendation..."):
                response = requests.post(f"{API_URL}/match/image", files=files, data=data)
                result = response.json()
        else:
            st.warning("Please upload an image file first.")

# --- Result rendering (target layout) ---
def render_iks_block(iks: dict, ui: dict):
    """Render the structured IKS block consistently."""
    if not iks:
        return

    principle = iks.get("principle")
    if principle:
        st.markdown(f"**{principle.get('statement', '')}**")
        st.caption(f"_Source type: {principle.get('source_type', '')} — {principle.get('source_note', '')}_")

    practice = iks.get("specific_practice")
    if practice:
        st.markdown(f"**{practice.get('name', '')}**")
        st.write(practice.get("description", ""))
        st.caption(f"_Primary citation: {practice.get('primary_citation', '')}_")
        if practice.get("secondary_citation"):
            st.caption(f"_Secondary citation: {practice.get('secondary_citation', '')}_")
        if practice.get("modern_evidence"):
            st.caption(f"_Modern evidence: {practice.get('modern_evidence', '')}_")

    seasonal = iks.get("seasonal_principle")
    if seasonal:
        st.markdown(f"**{seasonal.get('name', '')}**")
        st.write(seasonal.get("description", ""))
        st.caption(f"_Citation: {seasonal.get('source_citation', '')}_")
        if seasonal.get("verification_status"):
            st.warning(seasonal.get("verification_status"))

    relevance = iks.get("relevance_to_this_case")
    if relevance:
        st.markdown(f"_{ui.get('label_relevance','Relevance to this case')}: {relevance}_")

    verification = iks.get("verification_status")
    if verification:
        st.caption(f"{ui.get('label_verification','Verification note')}: {verification}")


if result is not None:
    st.divider()

    if not result.get("matched"):
        st.warning(f"**{ui['insufficient_context']}**\n\n{result.get('message', '')}")
        if "extracted_context" in result:
            st.caption(f"What we understood from your text: {result['extracted_context']}")
    else:
        confidence = result.get("confidence", "")

        # Header
        st.markdown(f"### ⚠️ {ui['section_likely_problem']}: **{result['problem_summary']}**")
        st.markdown(f"**{ui['confidence_label']}:** {confidence}")

        # Priority actions
        st.markdown(f"#### ⚡ {ui['section_what_to_do']}")
        for i, step in enumerate(result.get("priority_actions", []), 1):
            st.markdown(f"**{ui['label_priority']} {i}:** {step}")

        # Sustainable options
        st.markdown(f"#### 🌿 {ui['section_sustainable']}")
        for opt in result.get("sustainable_options", []):
            st.markdown(f"- {opt.get('action', '')}")
            st.caption(f"{ui['label_cost']}: {opt.get('cost', '')}  ·  {ui['label_availability']}: {opt.get('availability', '')}")

        # IKS
        st.markdown(f"#### 🇮🇳 {ui['section_iks']}")
        render_iks_block(result.get("iks", {}), ui)

        # Connection
        st.markdown(f"#### 🔬 {ui['section_connection']}")
        st.write(result.get("connection", ""))

        # Monitor
        st.markdown(f"#### 👀 {ui['section_monitor']}")
        st.write(result.get("monitor", ""))

        # Seek expert
        st.markdown(f"#### 🚨 {ui['section_seek_expert']}")
        for item in result.get("seek_expert_if", []):
            st.markdown(f"- {item}")

        # Why this result
        st.markdown(f"#### 💡 {ui['section_why']}")
        st.write(result.get("why", ""))

        # Sources
        with st.expander(f"📚 {ui['section_sources']}"):
            for src in result.get("sources", []):
                st.markdown(f"- {src}")
            if result.get("sources_verification_status"):
                st.caption(f"Verification: {result['sources_verification_status']}")

        # Feedback
        st.divider()
        st.caption("Was this information useful?")
        case_id = result.get("case_id", "unknown")
        fcol1, fcol2 = st.columns(2)
        if fcol1.button("👍 Yes", key=f"fb_yes_{case_id}"):
            requests.post(f"{API_URL}/feedback",
                          json={"case_id": case_id, "was_useful": True})
            st.success("Thanks for your feedback!")
        if fcol2.button("👎 No", key=f"fb_no_{case_id}"):
            requests.post(f"{API_URL}/feedback",
                          json={"case_id": case_id, "was_useful": False})
            st.success("Thanks — we'll use this to improve the knowledge base.")

if result is not None and result.get("matched"):
    # Show Image Classifier Detection tag if present
    if "prediction_info" in result:
        pred_info = result["prediction_info"]
        st.info(
            f"🖼️ **Image Classification Result:** Identified **{pred_info['predicted_class']}** "
            f"with {pred_info['confidence_score']*100:.1f}% confidence."
        )