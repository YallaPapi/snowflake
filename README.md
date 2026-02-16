# Snowflake: AI-Powered Screenplay Generation and Shot Planning Pipeline

AI-powered pipeline that transforms story ideas into production-ready screenplay packages with complete shot lists and visual specifications.

---

## What It Does

Snowflake takes a simple story idea and processes it through multiple AI engines to produce:

- **A structured story** using Randy Ingermanson's 11-step Snowflake Method
- **A feature-length screenplay** (90-110 pages) following Blake Snyder's Save the Cat method
- **Supporting artifacts**: World Bible, Full Cast profiles, Visual Bible with style specifications
- **A complete shot list** with 754+ shots for a feature film, generated via 6 deterministic steps
- **All prompts needed** for image and video generation via external APIs

The system outputs everything needed to generate a film, except the actual image/video generation (which happens in the i2v platform).

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    SNOWFLAKE PIPELINE SYSTEM                     │
│                 "From Story Idea → Shot List"                     │
└──────────────────────────────────────────────────────────────────┘

USER INPUT (2-3 sentence story idea)
    │
    ├────────────────────────────────────────────────────────┐
    │                                                         │
    ▼                                                         ▼
┌────────────────────┐                          ┌────────────────────┐
│  SNOWFLAKE ENGINE  │                          │ SCREENPLAY ENGINE  │
│ (Randy Ingermanson)│                          │ (Save the Cat)     │
│  11-step pipeline  │                          │  9-step pipeline   │
│ src/pipeline/      │                          │src/screenplay_     │
└────────────────────┘                          │    engine/         │
    │                                           └────────────────────┘
    │ Artifacts:                                    │
    │ • Opening/final image                         │ Artifacts:
    │ • Character summaries                          │ • Logline + title
    │ • Scene list                                  │ • Genre classification
    │                                               │ • Hero/antagonist/B-story
    │                                               │ • World Bible
    │                                               │ • Full Cast (3 tiers)
    │                                               │ • 15 Blake Snyder beats
    │                                               │ • 40 scene cards (4 acts)
    │                                               │ • Visual Bible (style)
    │                                               │ • Screenplay (90-110 pages)
    │                                               │ • Laws/diagnostics
    │                                               │
    │                                               ▼
    │                                   ┌────────────────────┐
    │                                   │   SHOT ENGINE      │
    └──────────────────────────────────►│ (Screenplay→Shots) │
                                        │ src/shot_engine/   │
                                        │ 6-step pipeline    │
                                        └────────────────────┘
                                               │
                                               │ Artifact:
                                               │ • shot_list.json (754 shots)
                                               │   - shot type/camera
                                               │   - duration/pacing
                                               │   - transitions
                                               │   - video prompts
                                               │
                                               ▼
                                   ┌────────────────────┐
                                   │  VISUAL BIBLE      │
                                   │ (Prompts/Assets)   │
                                   │ src/visual_bible/  │
                                   └────────────────────┘
                                               │
                                               │ Artifacts:
                                               │ • visual_manifest.json
                                               │ • prompt_batch.json
                                               │
                                               ▼
                                   ┌────────────────────┐
                                   │  VIDEO ENGINE      │
                                   │ (i2v project)      │
                                   │ External system    │
                                   └────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     CROSS-CUTTING SYSTEMS                        │
├──────────────────────────────────────────────────────────────────┤
│ • AI LAYER (src/ai/) - Multi-provider LLM abstraction           │
│   - OpenAI (GPT 5.2)                                             │
│   - Anthropic (Claude Sonnet 4.5)                                │
│   - xAI (Grok 4.1)                                               │
│   - Bulletproof failover & retry logic                           │
│                                                                  │
│ • API (src/api/) - FastAPI REST endpoints                       │
│ • OBSERVABILITY (src/observability/) - Real-time dashboard      │
│ • EXPORT (src/export/) - DOCX, EPUB, Markdown export           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Engine Breakdown

### 1. Snowflake Engine (src/scene_engine/)

Implements Randy Ingermanson's 11-step Snowflake Method for novel/story generation.

**Status**: Complete

**Steps**:
- Step 0: Meta-questions (opening/final image, word count)
- Step 1: 15-word story summary
- Step 2: 5-sentence paragraph (setup, disasters, ending)
- Step 3: 1-sentence character summaries
- Step 4: Expand paragraph to 1 page
- Step 5: 1-page character synopses
- Step 6: 4-page synopsis
- Step 7: Full character bibles
- Step 8: Scene list with POV, goal, conflict
- Step 9: Scene briefs (proactive/reactive structure)
- Step 10: Full novel prose generation

**Key Features**:
- Service-based architecture (planning, generation, drafting, chaining, quality, validation, persistence)
- Event-driven master service
- POV/tense handling
- Chain link generation (sequels, time skips, POV shifts)
- Multi-format export (DOCX, EPUB, Markdown, JSON, TXT)

### 2. Screenplay Engine (src/screenplay_engine/)

Implements Blake Snyder's "Save the Cat" screenplay method.

**Status**: Complete (v2.0.0, 970 passing tests)

**Steps**:
1. Logline (Ch.1) - Ironic logline with killer title
2. Genre (Ch.2) - 10 STC structural genres
3. Hero (Ch.3) - Hero, antagonist, B-story character
4. Beat Sheet (Ch.4) - 15 Blake Snyder beats
5. Board (Ch.5) - 40 scene cards in 4 acts
6. Screenplay (end Ch.5) - Full screenplay (90-110 pages)
7. Laws (Ch.6) - 7 Immutable Laws validation
8. Diagnostics (Ch.7) - 9 Diagnostic Checks validation
9. Marketing (Ch.8) - Poster test, hook test, 4-quadrant

**Optional Steps**:
- 3b: World Bible (geography, culture, economy, history)
- 3c: Full Cast (3-tier supporting cast)
- 5b: Visual Bible (style bible, color script, location designs)
- 8b: Targeted Rewrite (Grok-powered act-level revision)

**Key Features**:
- Multiple screenplay modes (monolithic, scene-by-scene, act-by-act)
- Checkpoint system (incremental diagnostics after steps 1-6)
- Emotional polarity tracking (every scene has +/- emotional arc)
- Character emergence (no bulk cast generation - characters emerge through board/screenplay)
- World-building with step 3b
- Visual preparedness with step 5b

### 3. Shot Engine (src/shot_engine/)

Converts screenplay scenes into shot lists for video generation.

**Status**: Complete (v12.0.0)

**Steps**:
1. V1: Scene Decomposition - Parse scenes into shot segments, detect content triggers
2. V2: Shot Type Assignment - Map trigger to shot type (wide, medium, close-up, etc.)
3. V3: Camera Behavior - Assign camera movement (static, pan, push-in, etc.)
4. V4: Duration & Pacing - Calculate duration per shot (base + format + beat curve)
5. V5: Transitions - Plan transitions (cut, dissolve, match cut, etc.)
6. V6: Prompts - Generate video prompts (T2V/I2V) per shot

**Key Features**:
- Rule-based shot selection (content trigger drives shot type/camera/duration)
- Emotional intensity mapping (high intensity → close-ups)
- Format-aware pacing (TikTok 0.5x, Feature 1.2x multipliers)
- Beat-aware pacing (Opening moderate, Midpoint rapid)
- Visual bible integration (cinematography hints from step 5b)
- Prompt enrichment (pulls character descriptions, world bible, visual bible)

**Output**: shot_list.json with 754 shots for a 40-scene feature film

### 4. Visual Bible Engine (src/visual_bible/)

Parses screenplay/shot list into image generation prompts and asset manifests.

**Status**: Complete

**Phases**:
- Phase 0: Parse screenplay → VisualManifest
- Phases 1-6: Generate all image prompts (character sheets, settings, init frames)
- Phase 7: Bundle Veo clips with generation order

**Key Features**:
- Stateful character tracking (cumulative state changes - injuries persist)
- Stateful setting tracking (cumulative damage, non-cumulative weather)
- Setting-per-location architecture (1 SettingBase per unique location)
- Silhouette test compliance (characters recognizable from outline)
- Veo clip bundling (groups shots into 4s/8s blocks)

**Outputs**:
- visual_manifest.json - Summary (character count, setting count, image count)
- visual_manifest_full.json - Reloadable full manifest
- prompt_batch.json - All T2I prompts for characters/settings/init frames

### 5. AI Layer (src/ai/)

Multi-provider LLM abstraction with bulletproof failover.

**Status**: Complete

**Providers**:
- Anthropic Claude (Sonnet 4.5, Haiku)
- OpenAI GPT (5.2, 4, 3.5)
- xAI Grok (4.1)
- OpenRouter (100+ models via single API)

**Key Features**:
- Bulletproof failover (5-tier: Claude Sonnet → Haiku → GPT-4 → GPT-3.5 → Emergency content)
- Retry logic with exponential backoff
- Streaming for large requests (>16K tokens)
- Timeout handling (up to 1200s for large screenplay generations)
- Auto-detect provider from environment variables

### 6. API Layer (src/api/)

FastAPI REST API for scene generation.

**Status**: Complete

**Endpoints**:
- `GET /` - Health check
- `POST /scene/generate` - Generate scene prose
- `GET /scene/{scene_id}` - Get scene by ID
- `POST /scene/validate` - Validate scene structure

### 7. Observability (src/observability/)

Real-time event tracking and dashboard.

**Status**: Complete

**Features**:
- Event publishing (project_created, step_start, step_complete, step_failed)
- Web dashboard (port 5000) with live updates
- Event stream endpoint
- Performance metrics

### 8. Export (src/export/)

Manuscript export to multiple formats.

**Status**: Complete

**Formats**:
- DOCX (Microsoft Word)
- EPUB (e-book)
- Markdown (GitHub-flavored)
- JSON (structured data)
- TXT (plain text)

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export XAI_API_KEY=xai-...
```

### Run Screenplay Pipeline

```bash
python scripts/test_screenplay_live.py
```

This runs the full 9-step Save the Cat pipeline and produces:
- `artifacts/sp_{project_id}/sp_step_1_logline.json` through `sp_step_9_marketing.json`
- `artifacts/sp_{project_id}/sp_step_8_screenplay.json` (90-110 page screenplay)

### Run Shot Engine

```bash
python scripts/test_shot_engine.py
```

This takes the screenplay output and produces:
- `artifacts/sp_{project_id}/shot_list.json` (754 shots with prompts, durations, transitions)

### Run Tests

```bash
python -m pytest tests/ -v
```

970+ tests across all engines.

---

## Project Structure

```
snowflake/
├── src/
│   ├── ai/                       # AI layer (6 files)
│   │   ├── generator.py          # Main AI generator (multi-provider)
│   │   ├── bulletproof_generator.py  # Multi-tier failover
│   │   └── model_selector.py     # Optimal model selection
│   ├── api/                      # FastAPI REST API (6 files)
│   ├── export/                   # Manuscript export (2 files)
│   ├── observability/            # Event tracking & dashboard (2 files)
│   ├── pipeline/                 # Snowflake Engine (41 files)
│   │   ├── steps/                # 11 Snowflake steps
│   │   ├── prompts/              # Step prompts
│   │   └── validators/           # Step validators
│   ├── scene_engine/             # Scene Engine (72 files)
│   │   ├── chaining/             # Chain link generation
│   │   ├── drafting/             # Prose drafting
│   │   ├── generation/           # Scene generation
│   │   ├── integration/          # Master service
│   │   ├── persistence/          # Database layer
│   │   ├── planning/             # Scene planning
│   │   ├── quality/              # Quality assessment
│   │   └── triage/               # Scene triage
│   ├── screenplay_engine/        # Screenplay Engine (50 files)
│   │   ├── pipeline/             # STC pipeline
│   │   │   ├── checkpoint/       # Diagnostic checkpoint system
│   │   │   ├── steps/            # 9 STC steps + 3b/3c/5b/8b
│   │   │   ├── prompts/          # Step prompts
│   │   │   └── validators/       # Step validators
│   │   └── models.py             # Pydantic models
│   ├── shot_engine/              # Shot Engine (13 files)
│   │   ├── pipeline/             # Shot planning pipeline
│   │   │   ├── steps/            # 6 shot steps (V1-V6)
│   │   │   └── validators/       # Shot list validator
│   │   └── models.py             # Shot data models
│   ├── visual_bible/             # Visual Bible Engine (6 files)
│   │   ├── pipeline/             # Visual Bible pipeline
│   │   ├── manifest.py           # Manifest parser
│   │   ├── models.py             # Visual data models
│   │   └── prompt_builder.py    # Prompt builder
│   └── ui/                       # UI layer (1 file)
├── tests/                        # Test suite (22 files, 1,140 tests)
│   ├── screenplay_engine/        # Screenplay tests (970)
│   ├── integration/              # Integration tests
│   └── steps/                    # Step-level tests
├── scripts/                      # Test/demo scripts
│   ├── test_screenplay_live.py   # Run screenplay pipeline
│   ├── test_shot_engine.py       # Run shot engine
│   └── run_scene.py              # Run scene generation
├── docs/                         # Documentation
│   ├── SNOWFLAKE_CODEBASE_DIGEST.md
│   ├── PIPELINE_ARCHITECTURE_DIAGRAM.md
│   ├── I2V_CODEBASE_DIGEST.md
│   └── stc_audit/                # Save the Cat compliance audits
├── artifacts/                    # Generated project artifacts
│   └── sp_*_*/                   # Screenplay projects
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| Screenplay Engine | 970 | All 9 steps + checkpoint system |
| Snowflake Engine | ~50 | Steps 0-3 integration |
| Scene Engine | ~100 | All services |
| API | ~20 | Integration, performance |
| **Total** | **~1,140** | **970+ passing** |

---

## Documentation

- **SNOWFLAKE_CODEBASE_DIGEST.md** - Full codebase architecture (all engines)
- **I2V_CODEBASE_DIGEST.md** - Video generation platform architecture
- **PIPELINE_ARCHITECTURE_DIAGRAM.md** - End-to-end pipeline with gap analysis
- **docs/stc_audit/** - Save the Cat compliance audits (8 chapters)

---

## Integration with i2v

The shot engine output (shot_list.json) is designed to feed into the i2v video generation platform for actual image/video production.

**Workflow**:
1. Snowflake generates shot list with prompts
2. i2v platform:
   - Generates setting images (T2I, once per location)
   - Generates character portraits (T2I, once per character)
   - Inpaints characters into settings (I2I compositing)
   - Animates frames (I2V via Veo/Kling/Wan)
   - Generates dialogue audio (TTS)
   - Applies lip sync
   - Stitches shots into scenes
   - Stitches scenes into final film

See `docs/I2V_CODEBASE_DIGEST.md` for complete i2v integration guide.

---

## Status

**Complete**:
- Snowflake Engine (11 steps)
- Screenplay Engine (9 steps + checkpoint system)
- Shot Engine (6 steps)
- Visual Bible (manifest parsing, prompt generation)
- Scene Engine (9 services)
- AI Layer (multi-provider, bulletproof failover)
- API (scene generation endpoints)
- Observability (dashboard, event tracking)
- Export (DOCX, EPUB, Markdown, JSON, TXT)

**Next**:
- Video generation orchestrator (in i2v platform)
- End-to-end pipeline runner (Snowflake → Screenplay → Shots → Video)

---

## Environment Variables

```bash
# AI Providers
OPENAI_API_KEY=sk-...           # OpenAI API key (GPT models)
ANTHROPIC_API_KEY=sk-ant-...    # Anthropic API key (Claude models)
XAI_API_KEY=xai-...             # xAI API key (Grok models)
OPENROUTER_API_KEY=sk-or-...    # OpenRouter API key (optional)

# Database (Scene Engine)
DATABASE_URL=sqlite:///scene_engine.db  # SQLite default

# API (Scene Engine)
API_PORT=8000                   # FastAPI port
API_HOST=0.0.0.0                # API host

# Observability
OBSERVABILITY_PORT=5000         # Flask dashboard port

# Logging
LOG_LEVEL=INFO                  # Logging level
```

---

## Performance Notes

**Typical Generation Times**:
- Screenplay (Steps 1-9): 30-40 min (monolithic), 45-60 min (act-by-act)
- Shot Engine (V1-V6): 2-3 min for 40 scenes (245 shots)
- Visual Bible (Phases 0-7): ~20s

**Costs** (for feature film):
- Screenplay generation: ~$5-10 in API costs (GPT/Claude)
- Shot list generation: $0 (deterministic, no LLM calls)
- Video generation: ~$75-277 per film (via i2v platform, depending on model)

---

## Known Issues

**Screenplay Engine** (5 persistent diagnostic failures):
1. Hero Leads - AI evaluator too strict about hero proactivity
2. Talking the Plot - Characters explain plot in dialogue
3. Emotional Color Wheel - Tech thrillers lean fear/tension/dread
4. Hi How Are You - Introductory dialogue feels generic
5. Limp and Eye Patch - Supporting characters lack distinctive traits

**Cause**: GPT writing tendencies don't self-correct via revision prompts

**Next steps**: Better prompts with concrete examples, or different writer model

---

## License

MIT License

---

## Contributors

Built with Claude Code (Sonnet 4.5)

Project: C:\Users\asus\Desktop\projects\snowflake

Date: 2026-02-16
