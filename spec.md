# Feature Spec: Session Archive

## Overview

Add an **Archive** section to the Responsible AI site that surfaces past workshop sessions and their associated materials (slides, recordings, notes, links, etc.). This gives returning and new visitors a persistent record of what has been covered and provides on-demand access to resources after each session concludes.

---

## Goals

- Allow visitors to browse all completed sessions in one place.
- Surface materials (slides, recordings, readings, notebooks, etc.) attached to each session.
- Keep the archive low-maintenance — adding a new past session should be as simple as adding a data entry.
- Match the visual style of the existing Schedule section.

---

## Non-Goals

- Real-time event registration (handled by the existing Schedule section / LibCal).
- User accounts or personalized history.
- Video hosting (links to external platforms such as MediaSpace or YouTube are sufficient).

---

## User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|----------|
| 1 | First-time visitor | Browse what topics have already been covered | I can understand the scope of the series |
| 2 | Workshop attendee | Download slides or re-watch a recording after the session | I can revisit content I found useful |
| 3 | Researcher who missed a session | Access readings and materials from a past session | I can catch up on my own |
| 4 | Site maintainer | Add a past session by editing a single data file | The site stays current without touching layout code |

---

## Content Model

Each archived session entry should capture:

| Field | Type | Notes |
|-------|------|-------|
| `title` | string | Session title |
| `date` | date | ISO 8601 (e.g. `2026-01-28`) |
| `time` | string | Human-readable time + timezone (e.g. `3–4 pm ET`) |
| `description` | string | Short summary of the session |
| `materials` | array | List of material objects (see below) |
| `tags` | array | Optional topic tags (e.g. `vision`, `audio`, `reasoning`) |

Each **material** object:

| Field | Type | Notes |
|-------|------|-------|
| `label` | string | Display name (e.g. `Slides`, `Recording`, `Notebook`) |
| `url` | string | Absolute URL to the resource |
| `icon` | string | Optional Bootstrap Icon name (e.g. `bi-camera-video`) |

---

## Data Storage

Archive entries will live in a Nunjucks-compatible data file:

```
_data/
  archive.json
```

The template will iterate over `archive` (sorted by date descending) to render each session card.

---

## UI / Layout

### Placement
A new `#archive` section below the existing `#schedule` section on `index.njk`.

### Section Header
- Heading: **Past Sessions**
- Sub-copy: brief description inviting visitors to explore past workshop materials.

### Session Card
Each past session renders as a card or accordion row (consistent with `.schedule-item` styling) containing:
- **Date & time** (left column, `<time>` element)
- **Title** (bold heading)
- **Description** (paragraph)
- **Material buttons** — one pill/button per material linking to the resource, with an optional icon prefix.
- **Tags** — small badges for topic tags (optional, can be deferred).

### Empty State
If no archive entries exist yet, display a short message: *"Past session materials will appear here after each workshop."*

---

## Template Implementation (Nunjucks)

```nunjucks
<!-- ======= Archive Section ======= -->
<section id="archive">
  <div class="container" data-aos="fade-up">
    <div class="section-header">
      <h2>Past Sessions</h2>
      <p>Browse recordings, slides, and other materials from previous workshops.</p>
    </div>

    {% if archive and archive.length %}
      {% for session in archive | sort(true, false, "date") %}
      <div class="row schedule-item">
        <div class="col-md-2">
          <time>{{ session.date | readableDate }}</time>
        </div>
        <div class="col-md-10">
          <h4>{{ session.title }}</h4>
          <p>{{ session.description }}</p>
          {% for material in session.materials %}
            <a href="{{ material.url }}" target="_blank">
              <button type="button" class="btn btn-outline-secondary btn-sm me-1">
                {% if material.icon %}<i class="bi {{ material.icon }}"></i> {% endif %}
                {{ material.label }}
              </button>
            </a>
          {% endfor %}
        </div>
      </div>
      {% endfor %}
    {% else %}
      <p class="text-center text-muted">Past session materials will appear here after each workshop.</p>
    {% endif %}
  </div>
</section>
```

---

## Navigation

Add an **Archive** anchor link to the navbar alongside the existing **Schedule** link:

```html
<li><a class="nav-link scrollto" href="#archive">Archive</a></li>
```

---

## Implementation Checklist

- [ ] Create `_data/archive.json` with initial entries for completed sessions
- [ ] Add a `readableDate` filter to `.eleventy.js` (or equivalent config) if not already present
- [ ] Add the `#archive` section to `index.njk`
- [ ] Add the **Archive** nav link to `_includes/partials/navbar.html`
- [ ] Populate `archive.json` with all sessions completed so far (dates, materials)
- [ ] Style review — verify card layout matches existing Schedule section
- [ ] Test empty state (empty array in `archive.json`)
- [ ] QA on mobile breakpoints

---

## Open Questions

1. **Recordings** — Are session recordings hosted publicly (e.g. MediaSpace)? Should links be gated or open?
2. **Tags / filtering** — Is client-side filtering by tag in scope for v1, or deferred?
3. **Materials availability** — Will all past sessions have slides/recordings, or should missing materials be gracefully hidden?
4. **Pagination** — As the archive grows, will a single long list remain acceptable, or should we plan for pagination / grouping by semester?

---

## Notebooks

### Inventory

The `notebooks/` folder currently contains 11 notebooks (several are Colab-first):

| Filename | Short Link | Description | Colab-specific? |
|----------|-----------|-------------|-----------------|
| `Anatomy_of_a_Chatbot.ipynb` | — | Foundational walkthrough of transformer architecture, GPT-2, fine-tuning, and RLHF. Conceptual + hands-on. | No |
| `Visual_Reasoning.ipynb` | `bit.ly/visual-reasoning` | Introduces visual chain-of-thought reasoning with multimodal models (VLMs); uses LLaVA-CoT training examples. | No |
| `Visual_Tool_Calling.ipynb` | `tinyurl.com/visual-tool-calling` | Multimodal tool use: zoom tools, reverse image search, contextual metadata retrieval with Qwen3-VL. Feb 2026. | Yes (`userdata`, `dashscope`) |
| `video_understanding_qwen_vl.ipynb` | `tinyurl.com/video-understanding` | Deep-dive into video understanding with Qwen-VL: frame sampling, vision encoder pipeline, mRoPE temporal embeddings. Apr 2026. | No |
| `discovery_steering.ipynb` | `tinyurl.com/llm-steering` | LLM activation/concept steering with `nnsight` and `sae-lens`; tinkering with hidden-state concept vectors. | No |
| `translation_workshop.ipynb` | `tinyurl.com/translation-notebook` | Three translation approaches for scholarly texts: `deep-translator`, MarianMT (offline), and LLM-based (Claude). | No |
| `Upenn_History_Workshop.ipynb` | `tinyurl.com/upenn-history-workshop` | Historian-focused workshop: loading IIIF manifests from UPenn's Colenda repository, processing archival images. | Yes (`google.colab`) |
| `Images_to_MD.ipynb` | — | Converts uploaded images (incl. HEIC) to Markdown text using Qwen3-VL. File upload via Colab widget. | Yes (`files.upload`) |
| `Images_to_MD_(Load_and_Save_in_Drive).ipynb` | — | Drive-integrated variant of `Images_to_MD`: reads from and writes results back to a user's Google Drive folder. | Yes (`drive.mount`) |
| `Images_to_Structured_data.ipynb` | — | Extracts structured data from images (e.g. Indonesian census pages); can start from PDFs or raw images in Drive. | Yes (`drive.mount`) |
| `PDF_to_MD.ipynb` | — | Converts uploaded PDFs page-by-page to Markdown via PyMuPDF + VLM. Minimal UI, upload via Colab. | Yes (`google.colab`) |

---

### Suggested Groupings

Organizing notebooks by theme rather than alphabetically makes the archive more navigable for researchers:

#### 1. Foundations
Conceptual primers that require no prior ML background.
- `Anatomy_of_a_Chatbot` — how chatbots work, transformers, RLHF
- `discovery_steering` — model internals, concept steering

#### 2. Visual & Multimodal AI
Sessions focused on vision-language models and image/video understanding.
- `Visual_Reasoning` — chain-of-thought over images
- `Visual_Tool_Calling` — tool use with VLMs
- `video_understanding_qwen_vl` — video + temporal reasoning (deepest technical content)

#### 3. Practical Document Processing (Tool Notebooks)
Hands-on utility notebooks researchers can reuse on their own materials.
- `PDF_to_MD` — PDF → Markdown transcription
- `Images_to_MD` — image upload → Markdown transcription
- `Images_to_MD_(Load_and_Save_in_Drive)` — Drive-backed variant of the above
- `Images_to_Structured_data` — image/PDF → structured data extraction

> **Note:** `Images_to_MD` and `Images_to_MD_(Load_and_Save_in_Drive)` are variants of the same workflow. They should appear as a single archive entry with two notebook links ("Upload files" / "Use Google Drive").

#### 4. Domain & Collaborative Workshops
Notebooks built for specific audiences or partner institutions.
- `translation_workshop` — scholarly translation for humanists
- `Upenn_History_Workshop` — IIIF + archival image analysis for historians

---

### Platform-Agnostic Access Strategy

Each notebook is available in **three forms**, all generated automatically by `scripts/build_notebooks.py`:

| Format | Location in repo | Served at | Purpose |
|--------|-----------------|-----------|---------|
| **HTML preview** | `assets/notebooks/html/<name>.html` | `/assets/notebooks/html/<name>.html` | Read-only, no runtime needed |
| **Open in Colab** | Original `notebooks/<name>.ipynb` on GitHub | External (Colab URL) | One-click interactive run on Google infrastructure |
| **Run anywhere** | `notebooks/run-anywhere/<name>.ipynb` | `/notebooks/run-anywhere/<name>.ipynb` | Portable Jupyter/VS Code/JupyterHub use |

#### The build script (`scripts/build_notebooks.py`)

Run with `npm run build:notebooks` (or automatically via `npm run build` / `npm start`).  
For each notebook it:

1. **Strips Colab-specific output metadata** (`errorDetails`, Colab widget MIME types) that would break `nbconvert`, then exports a clean **HTML file** to `assets/notebooks/html/`.
2. **Replaces Colab-only source patterns** with portable equivalents (see table below) and writes the result to `notebooks/run-anywhere/` as a standalone `.ipynb`.

#### Colab → portable substitutions applied automatically

| Colab pattern | Portable replacement |
|---------------|----------------------|
| `from google.colab import drive` + `drive.mount(...)` | `os.environ.get('DATA_FOLDER', 'data/')` path variable |
| `from google.colab import files; files.upload()` | `ipywidgets`-free glob over a local `data/` folder |
| `from google.colab import userdata` + `userdata.get(...)` | `os.environ.get(...)` + optional `python-dotenv` loader |

A **preamble cell** is inserted at the top of any run-anywhere notebook that had substitutions, explaining what changed and how to set up local paths and API keys.

#### What to link from the archive

Each notebook entry in `archive.json` should carry three material objects:

```json
[
  {
    "label": "Preview",
    "url": "/assets/notebooks/html/Visual_Tool_Calling.html",
    "icon": "bi-eye"
  },
  {
    "label": "Open in Colab",
    "url": "https://colab.research.google.com/github/PULdischo/responsible-ai/blob/main/notebooks/Visual_Tool_Calling.ipynb",
    "icon": "bi-google"
  },
  {
    "label": "Download Notebook",
    "url": "/notebooks/run-anywhere/Visual_Tool_Calling.ipynb",
    "icon": "bi-download"
  }
]
```

The **Colab URL** is derived automatically from the GitHub path — no manual export needed. It always reflects the latest committed version of the notebook.

#### Longer-term options (deferred)
- **Binder** (`mybinder.org`) — fully interactive, no Google account required; slower cold starts, suitable for lighter notebooks.
- **JupyterHub** — if Princeton provides a shared hub, a direct JupyterHub link is the cleanest institutional option.
- **Static HTML export with Quarto** — for richer rendered previews with navigation sidebars.

---

### Updated Implementation Checklist Additions

- [x] `scripts/build_notebooks.py` written — strips Colab metadata, exports HTML, writes run-anywhere variants
- [x] `npm run build:notebooks` wired into `package.json`; `npm run build` and `npm start` run it automatically
- [x] `assets/notebooks/html/` and `notebooks/run-anywhere/` populated for all 11 notebooks
- [x] Eleventy configured to passthrough `notebooks/` so `.ipynb` files are served
- [ ] Populate `_data/archive.json` with all completed sessions, including the three notebook material objects per entry
- [ ] Decide on canonical notebook groupings (use the four categories above or revise)
- [ ] Verify all `tinyurl`/`bit.ly` shortlinks still resolve and point to the correct notebooks
- [ ] Confirm `Visual_Tool_Calling.ipynb` does not contain a live API key before committing to a public repo (line ~14 currently has a hardcoded key)
- [ ] Merge or clearly cross-link `Images_to_MD` and `Images_to_MD_(Load_and_Save_in_Drive)` as variants in the archive entry

