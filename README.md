# VRIKSHA-AI

Context-aware plant-care knowledge system combining Modern Agricultural
Knowledge, Sustainable Approaches, and Indian Knowledge Systems
(Vrikshayurveda). Built for NCSC — Science and Innovation for Sustainability.

---

## 1. Project structure

```
vriksha-ai/
├── data/
│   └── knowledge_base.json      ← your researched plant/problem cases
├── backend/
│   ├── matcher.py                ← context matching engine (no AI, pure Python)
│   ├── text_extractor.py         ← free-text keyword extraction
│   ├── translations.py           ← English/Hindi/Bengali UI strings
│   ├── ai_synthesis.py           ← the ONLY file that calls an AI API
│   ├── models.py                 ← request/response data shapes
│   └── main.py                   ← FastAPI app (the API server)
├── frontend/
│   └── app.py                    ← Streamlit web UI
├── tests/
│   └── test_matcher.py           ← automated tests
├── docs/
│   └── ARCHITECTURE.md           ← deeper design notes + how to add mobile
├── requirements.txt
├── .env.example
└── .gitignore
```

**Why this shape:** the backend has zero knowledge of Streamlit, and the
frontend never imports backend Python code directly — it only calls the
API over HTTP. This is what lets you later build a mobile app that talks to
the *exact same* backend without changing a single backend file.

---

## 2. First-time setup in VS Code (do this once)

Open the `vriksha-ai` folder in VS Code (`File → Open Folder`), then open a
terminal inside VS Code: `` Terminal → New Terminal `` (or `` Ctrl+` ``).

### 2.1 Create a virtual environment

A virtual environment is an isolated Python install just for this project,
so its dependencies don't clash with other projects on your machine.

```bash
python -m venv venv
```

This creates a `venv/` folder (already excluded from Git via `.gitignore`).

**Activate it** — you must do this every time you open a new terminal for
this project:

- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Windows (cmd): `venv\Scripts\activate.bat`
- macOS / Linux: `source venv/bin/activate`

You'll know it worked because your terminal prompt now starts with `(venv)`.

VS Code tip: after creating the venv, press `Ctrl+Shift+P` → "Python: Select
Interpreter" → choose the one inside `./venv`. Then VS Code's built-in
terminal will auto-activate it for you every time.

### 2.2 Install dependencies

```bash
pip install -r requirements.txt
```

This reads `requirements.txt` and installs FastAPI, Streamlit, pytest, etc.
— everything the project needs, at the exact versions that are known to
work together.

### 2.3 Set up your API key (optional, for AI-smoothed text)

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

Then open `.env` and paste your real key from
[console.anthropic.com](https://console.anthropic.com). If you skip this
step entirely, the app still works — it just shows the raw researched text
instead of an AI-rephrased version (see `backend/ai_synthesis.py`).

---

## 3. Running the project

You need **two terminals** running at the same time — the backend and the
frontend are separate processes, just like in a real product.

**Terminal 1 — start the API:**
```bash
uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000/docs — this is FastAPI's automatic interactive
documentation. You can test every endpoint here directly, no frontend
needed.

**Terminal 2 — start the web UI:**
```bash
streamlit run frontend/app.py
```
This opens your browser at http://localhost:8501 automatically.

---

## 4. Running the tests

```bash
pytest -v
```

`-v` means "verbose" — it prints each test name and whether it passed.
This is your Section 28/29 testing evidence, generated for real instead of
filled in by hand.

---

## 5. About the knowledge base — and about Kaggle

You asked about Kaggle specifically, so here's the honest picture:

**What Kaggle IS good for here:** if you later add the optional image-upload
feature (Section 21 of the brief), the **PlantVillage dataset** on Kaggle
(search "PlantVillage dataset") is the standard, well-known, free dataset of
~50,000+ labeled leaf images across many crops and diseases, used to train
plant disease image classifiers. If you want that feature, that's where
you'd start — but per your own brief (Section 21), only add it if it can be
done *reliably*; a working text-based prototype beats a flaky image feature.

**What Kaggle is NOT good for here:** your knowledge base needs *textual,
structured* information — symptoms, sustainable approaches, and especially
Vrikshayurveda/IKS context. This kind of curated text data essentially
doesn't exist as a ready-made dataset anywhere, Kaggle included, because
it's a niche synthesis of traditional Indian texts + modern agronomy that
nobody has packaged before. **This is actually good news for your project**
— it means your knowledge base itself, done carefully, IS original research
contribution, which is exactly what NCSC judges want to see. It is not
something you can (or should) shortcut by downloading a dataset.

**Where to actually source the content** (for the 10 starter cases already
in `data/knowledge_base.json`, and for expanding it):
- **Modern agricultural knowledge**: ICAR (Indian Council of Agricultural
  Research) publications, state agricultural university extension bulletins,
  and Krishi Vigyan Kendra (KVK) advisories — all publicly available and
  citable.
- **Sustainable approaches**: FAO's Integrated Pest Management (IPM)
  guidelines, and the same ICAR/KVK sources above.
- **IKS/Vrikshayurveda**: look for the Surapala's *Vrikshayurveda* (a
  translated classical Sanskrit text on plant science) and academic papers
  that discuss it — search terms like "Vrikshayurveda Surapala translation"
  or "Indian traditional plant science texts." Your school/college library
  or a professor in botany/Sanskrit studies may also have access to
  translated excerpts. **Cross-check with your mentor (sir)** before citing
  anything as authoritative traditional knowledge — this is exactly the
  kind of thing worth getting a second opinion on, as your own brief
  (Section 30) already plans for.

The 10 cases already in the knowledge base are a realistic *starting
structure* — you and your team should review, correct, and expand them
with your own research before the final submission. Treat them as a
template to fill in, not a finished, citable product.

---

## 5b. If a judge asks "what is your source for the knowledge base?"

Here is the honest, defensible answer:

**For Modern Agricultural Knowledge:**
- ICAR ePubs — *Integrated Pest Management approaches for major tomato pests* (epubs.icar.org.in)
- NICRA-ICAR — *Manual for Tomato Pest Surveillance* (nicra-icar.in)

These are real, publicly available ICAR publications. Extend this list with
the specific ICAR/KVK/university bulletin for each new crop/problem you add
— search `"ICAR [your crop] [your problem] IPM"` and cite the exact
publication.

**For Indian Knowledge Systems / Vrikshayurveda:**
- ***Surapala's Vrikshayurveda: The Science of Plant Life***, translated by
  Nalini Sadhale, published by the Asian Agri-History Foundation (1996).
  This is the real, primary source: an ancient Sanskrit text (~10th century
  CE) that was lost for centuries until Dr. Y.L. Nene located the only
  surviving manuscript at the Bodleian Library, Oxford, and had it
  translated. This is the single most citable, authentic source for
  Vrikshayurveda content, and the correct answer if a judge asks "where does
  your IKS content actually come from."
- Nene, Y.L. — *Potential of Some Methods Described in Vrikshayurvedas in
  Crop Yield Increase and Disease Management*, Asian Agri-History
  Foundation. This paper documents specific traditional formulations (e.g.
  "Kunapajala," a liquid preparation using neem, milk, and other
  ingredients) that genuinely match the kind of content referenced in this
  knowledge base's `iks_context` fields.

**What you should say honestly, and what you should NOT claim:**
- ✅ "Our IKS content is grounded in Surapala's Vrikshayurveda, the
  primary surviving Sanskrit text on plant science, translated and
  published by the Asian Agri-History Foundation."
- ❌ Do NOT claim that every specific sentence in `iks_context` for every
  case has been individually verified against a specific page/verse of
  that text. **It has not.** Each case currently has a field called
  `sources_verification_status` in the JSON flagging exactly this — the
  general sources are real, but case-by-case claims still need your team to
  cross-check them against the actual translated text (or a summary of it)
  before you present specific claims as verified.

**What to do before your final submission:** get a copy of Sadhale's
translation (search "Surapala Vrikshayurveda Sadhale pdf" or check with a
Sanskrit/agriculture faculty member — many university libraries carry it),
and for each case in your knowledge base, either (a) find and cite the
actual relevant passage, or (b) soften the `iks_context` wording to
something you can honestly defend, like "consistent with the general
principles of soil and plant vitality described in Vrikshayurveda" rather
than a specific claim. This is real academic practice, not a weakness to
hide — showing you understand the difference between "inspired by" and
"verbatim sourced from" a text will impress judges more than pretending
everything is footnoted.

---

## 6. How to extend the knowledge base

Open `data/knowledge_base.json` and add a new object to the `"cases"` array,
following the exact same field structure as the existing entries. That's
it — no code changes needed. The matcher, the API, and the frontend all
read from this file dynamically, so a new case appears in dropdowns and
becomes matchable immediately after you save the file and restart the
backend.

---

## 7. Git — saving your work properly

If you haven't already, set up version control so you have a history of
your work (and can collaborate with teammates):

```bash
git init
git add .
git commit -m "Initial VRIKSHA-AI prototype"
```

Then create an empty repository on GitHub and follow GitHub's instructions
to push (`git remote add origin ...`, `git push -u origin main`). Because
of `.gitignore`, your `venv/` folder and `.env` secrets will never be
uploaded — only your actual project code.

---

## 8. Next steps (in priority order)

1. **Review and expand the knowledge base** with your own team's research
   (see Section 5 above) — this is the highest-value thing you can do.
2. **Add Hindi/Bengali translations of the actual case content**, not just
   the UI labels — see `docs/ARCHITECTURE.md` "Translating case content."
3. **Add voice input** in the Streamlit frontend — see
   `docs/ARCHITECTURE.md` "Adding voice input."
4. **Package as a mobile-installable PWA** — see
   `docs/ARCHITECTURE.md` "From web to mobile."
5. **Deploy online** so judges can try it on their own device before the
   demo — see `docs/ARCHITECTURE.md` "Deployment."
