# Architecture notes & how to extend

## Why FastAPI + Streamlit + a JSON knowledge base (not a database, not Django)

| Choice | Reason |
|---|---|
| **FastAPI** over Flask/Django | Auto-generated `/docs`, built-in request validation, async-ready. Django would be overkill — you don't need its admin panel, ORM, or templating for an API-only backend. |
| **Streamlit** over raw HTML/JS | You said you want to stay in Python. Streamlit turns a Python script into a working web UI with no separate frontend language to learn, which matches your timeline. |
| **JSON file** over a database (for now) | Your knowledge base is small (~10-50 cases), read far more often than written, and edited by humans (you, researching), not by end users. A database adds real value once you have hundreds of cases or need concurrent writes (e.g. many users submitting feedback at once) — see "When to move to SQLite" below. |

This is also *exactly* the four-layer architecture from Section 16 of your
brief:
- Layer 1 (Curated KB) = `data/knowledge_base.json`
- Layer 2 (Context Matching) = `backend/matcher.py`
- Layer 3 (AI Assistance) = `backend/ai_synthesis.py`
- Layer 4 (Structured Output) = the JSON your API returns, rendered by
  `frontend/app.py`

---

## Translating case content (not just UI labels)

Right now, `backend/translations.py` only translates interface labels
("Sustainable Approaches" → "टेकसई पन्था"). The actual case content
(symptoms, modern_knowledge, etc.) stays in English regardless of the
selected language. To fix this properly:

**Option A (recommended for your timeline):** add per-language fields
directly in `knowledge_base.json`:
```json
"modern_knowledge": "...",
"modern_knowledge_hi": "...",
"modern_knowledge_bn": "..."
```
Then in `matcher.py`'s `match()` function, after finding the best case,
swap in the language-specific fields if they exist for the requested
language, falling back to English if a translation is missing for that
case. This keeps translation as a research/writing task (you and your team
translating ~10 cases by hand or with careful review), not a live API call
that could produce inaccurate agricultural terminology on stage.

**Option B (more automated, riskier for a demo):** call a translation API
live in `ai_synthesis.py`. Not recommended as your primary path — an
external API call is a point of failure right when a judge is watching.

---

## Adding voice input

Streamlit doesn't have native microphone support, but browsers do, via the
JavaScript **Web Speech API**. You embed a small HTML/JS snippet using
`st.components.v1.html()` that:
1. Starts listening when a button is clicked
2. Converts speech to text in the browser
3. Writes the result into a Streamlit text input using Streamlit's
   component communication (`Streamlit.setComponentValue`)

This is a self-contained addition to `frontend/app.py` — it doesn't touch
the backend at all, because by the time text reaches your API, it's just
text, exactly like the free-text box already implemented. Search
"streamlit web speech api component" for a ready template to adapt once
your core demo is stable — treat this as a Section 21-style "add if there's
time" feature, not a blocker.

---

## From web to mobile

Your brief says "web-based first, then mobile." Because the backend is a
plain REST API, you have two real paths, in order of effort:

### Path 1 (recommended for a hackathon/NCSC timeline): Progressive Web App (PWA)
Add two small files to make your Streamlit-served page installable on a
phone's home screen, behaving like a native app (works offline for cached
pages, has its own icon, opens without browser chrome):
- a `manifest.json` describing the app name/icons
- a `service-worker.js` for basic caching

This is genuinely a mobile app in every way a judge cares about (installed
icon, full-screen, app-like), and it requires **zero new backend code** —
it's the same FastAPI + the same knowledge base.

### Path 2 (if you have significantly more time): React Native or Flutter
A true native app calling your existing FastAPI endpoints
(`GET /cases`, `POST /match`, `POST /match/freetext`). Your backend doesn't
change at all — you'd only build a new frontend. This is a multi-week
project on its own, so only pursue it if the PWA path isn't enough for your
goals.

**Either way, the lesson to tell judges:** "we built one backend knowledge
engine, and the same engine now powers both our web and mobile clients" —
this is a genuinely strong architecture story, and it's true.

---

## When to move from JSON to SQLite

Move the knowledge base from `knowledge_base.json` to a SQLite database
(still just a single file, no server to run) once any of these happen:
- You pass ~50-100 cases and searching/filtering the JSON in Python starts
  feeling slow or awkward
- You want the feedback log (`_feedback_log` in `main.py`) to survive a
  server restart — right now it's stored in memory and resets every time
  you stop `uvicorn`
- Multiple teammates need to edit the knowledge base at the same time
  without merge conflicts in a JSON file

Python's built-in `sqlite3` module needs no separate installation. This is
a natural "Phase 2" improvement, not something to do before your first
working demo.

---

## Deployment (so judges can try it before/without your laptop)

- **Backend**: [Render](https://render.com) or
  [Railway](https://railway.app) both have free tiers and deploy a FastAPI
  app directly from a GitHub repo in a few clicks.
- **Frontend**: [Streamlit Community Cloud](https://streamlit.io/cloud) is
  free and built exactly for deploying Streamlit apps from a GitHub repo.
  You'll need to update `API_URL` in `frontend/app.py` from
  `http://127.0.0.1:8000` to your deployed backend's public URL.

Do this only once the local version works end-to-end and your tests pass —
deployment adds a layer of "why is it different online vs. on my laptop"
debugging you don't want mid-development.
