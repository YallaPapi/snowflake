# Architecture Analysis Report

**Generated**: 2026-02-07 12:00 UTC
**Analyst**: Architecture Reviewer Agent
**Scope**: Full system architecture review

---

## Table of Contents

1. [Overall System Architecture](#1-overall-system-architecture)
2. [Pipeline Architecture](#2-pipeline-architecture)
3. [Scene Engine Architecture](#3-scene-engine-architecture)
4. [API Layer](#4-api-layer)
5. [Observability System](#5-observability-system)
6. [Configuration and Dependencies](#6-configuration-and-dependencies)
7. [Design Patterns Used](#7-design-patterns-used)
8. [Coupling and Cohesion Assessment](#8-coupling-and-cohesion-assessment)
9. [Architectural Gaps and Inconsistencies](#9-architectural-gaps-and-inconsistencies)
10. [Integration Points](#10-integration-points)
11. [Recommendations](#11-recommendations)

---

## 1. Overall System Architecture

### Architecture Overview

```
Pattern: Layered Architecture + Pipeline Pattern + Parallel Subsystems
Layers: AI Abstraction, Pipeline Orchestration, Scene Engine, API, Observability, Export
Health: Functional but structurally fragmented -- two major subsystems (Pipeline and Scene Engine)
        operate largely in isolation with duplicated capabilities
```

### Project Statistics

| Metric | Value |
|--------|-------|
| Total Python source files (src/) | ~105 files |
| Pipeline step implementations | 14 files (including variants) |
| Pipeline validators | 11 files |
| Pipeline prompts | 9 files |
| Scene Engine modules | ~55 files across 10 subpackages |
| AI abstraction files | 6 files |
| API files | 4 files |
| Observability files | 2 files |
| Test files | ~15 files |
| Broad `except Exception` handlers | 157 occurrences across 40 files |

### High-Level Component Map

```
C:\Users\asus\Desktop\projects\snowflake\
  src/
    ai/                      # AI Provider Abstraction Layer
      generator.py           # Core AIGenerator (Anthropic + OpenAI)
      bulletproof_generator.py  # 100% reliability wrapper
      bulletproof_prose_generator.py  # Prose-specific reliability
      model_selector.py      # Tier-based model selection
      prose_generator.py     # Prose generation utilities
      generator_openrouter.py  # OpenRouter provider
    pipeline/                # Snowflake Method Pipeline (Steps 0-10)
      orchestrator.py        # Central pipeline coordinator
      error_recovery.py      # Retry and recovery logic
      progress_tracker.py    # Checkpoint-based progress
      steps/                 # 14 step implementation files
      validators/            # 11 validator files
      prompts/               # 9 prompt template files
    scene_engine/            # Independent Scene Management System
      models.py              # Pydantic SceneCard models
      validators.py          # PRD-based scene validation
      schema.py              # JSON Schema generation
      chaining/              # Scene chain link management
      drafting/              # Prose drafting (POV, exposition)
      export/                # Scene-level export
      generation/            # Scene generation engine
      integration/           # Master service facade
      persistence/           # SQLAlchemy database layer
      planning/              # Scene planning
      quality/               # Quality assessment
      triage/                # Scene triage and corrections
      validation/            # Validation pipeline
      examples/              # Reference implementations
    api/                     # FastAPI REST API
      main.py                # Main API server
      scene_engine_endpoints.py  # Scene engine routes
    observability/           # Monitoring and Dashboards
      events.py              # Event emission + metrics collection
      server.py              # Flask dashboard server
    export/                  # Manuscript export
      manuscript_exporter.py # DOCX, EPUB, Markdown export
```

### Data Flow Architecture

```
User Brief (text)
    |
    v
[Step 0: First Things First] --> step_0_first_things_first.json
    |
    v
[Step 1: One Sentence Summary] --> step_1_one_sentence_summary.json
    |
    v
[Step 2: One Paragraph Summary] --> step_2_one_paragraph_summary.json
    |
    v
[Step 3: Character Summaries] --> step_3_character_summaries.json
    |
    v
[Step 4: One Page Synopsis] --> step_4_one_page_synopsis.json
    |
    v
[Step 5: Character Synopses] --> step_5_character_synopses.json
    |
    v
[Step 6: Long Synopsis] --> step_6_long_synopsis.json
    |
    v
[Step 7: Character Bibles] --> step_7_character_bibles.json
    |
    v
[Step 8: Scene List] --> step_8_scene_list.json
    |
    v
[Step 9: Scene Briefs] --> step_9_scene_briefs.json
    |
    v
[Step 10: First Draft] --> step_10_manuscript.json + manuscript.md
    |
    v
[Export] --> manuscript.docx / manuscript.epub
```

### Artifact Storage Pattern

All pipeline state is persisted as flat JSON files under the `artifacts/` directory:

```
artifacts/
  <project-uuid>/
    project.json                        # Project metadata
    initial_brief.json                  # Original user brief
    status.json                         # Current pipeline status
    events.jsonl                        # Event stream log
    step_0_first_things_first.json      # Step 0 output
    step_0_first_things_first.txt       # Human-readable version
    step_1_one_sentence_summary.json    # Step 1 output
    ...
    step_10_manuscript.json             # Final manuscript data
    manuscript.md                       # Markdown manuscript
    snapshots/                          # Version snapshots
    change_log.txt                      # Change history
```

---

## 2. Pipeline Architecture

### 2.1 Orchestrator

**File**: `src/pipeline/orchestrator.py` (647 lines)

The `SnowflakePipeline` class is the central coordinator. It manages the lifecycle of novel generation projects through 11 sequential steps (Steps 0-10).

**Key responsibilities**:
- Project creation with UUID-based identification
- Sequential step execution (`execute_step_0` through `execute_step_10`)
- Artifact loading between steps (each step reads upstream artifacts from disk)
- Project state tracking via `project.json`
- Event emission for observability
- Full pipeline execution via `execute_all_steps()`

**Dependency map** (defined at line 527):
```python
dependencies = {
    1: [0],           # Step 1 depends on Step 0
    2: [0, 1],        # Step 2 depends on Steps 0 and 1
    3: [0, 1, 2],     # Step 3 depends on Steps 0, 1, and 2
    4: [0, 1, 2],     # Step 4 depends on Steps 0, 1, and 2
    5: [3],           # Step 5 depends on Step 3
    6: [2, 4],        # Step 6 depends on Steps 2 and 4
    7: [3, 5],        # Step 7 depends on Steps 3 and 5
    8: [6, 7],        # Step 8 depends on Steps 6 and 7
    9: [8],           # Step 9 depends on Step 8
    10: [8, 9]        # Step 10 depends on Steps 8 and 9
}
```

**Notable issue**: The `regenerate_downstream()` method (line 504) is a stub -- it identifies which steps need regeneration but does not actually re-execute them.

### 2.2 Step Implementations

Each step follows a consistent internal pattern:

| Step | Class | File | Purpose |
|------|-------|------|---------|
| 0 | `Step0FirstThingsFirst` | `step_0_first_things_first.py` | Story market position |
| 1 | `Step1OneSentenceSummary` | `step_1_one_sentence_summary.py` | One-sentence story hook |
| 2 | `Step2OneParagraphSummary` | `step_2_one_paragraph_summary.py` | Five-sentence paragraph summary |
| 3 | `Step3CharacterSummaries` | `step_3_character_summaries.py` | Character sheets |
| 4 | `Step4OnePageSynopsis` | `step_4_one_page_synopsis.py` | Expanded story synopsis |
| 5 | `Step5CharacterSynopses` | `step_5_character_synopses.py` | Per-character synopses |
| 6 | `Step6LongSynopsis` | `step_6_long_synopsis.py` | Multi-page synopsis |
| 7 | `Step7CharacterBibles` | `step_7_character_bibles.py` | Complete character dossiers |
| 8 | `Step8SceneList` | `step_8_scene_list.py` | Scene list with chapters |
| 9 | `Step9SceneBriefsV2` | `step_9_scene_briefs_v2.py` | Individual scene briefs |
| 10 | `Step10FirstDraft` | `step_10_first_draft.py` | Full prose manuscript |

**Step template pattern** (repeated in every step class):
```
__init__(project_dir)  --> Sets up validator, prompt generator, AI generator
execute(inputs)        --> Generate prompt -> Call AI -> Validate -> Save
revise(project_id)     --> Load current -> Snapshot -> Regenerate -> Validate -> Save
save_artifact()        --> Write JSON + human-readable text
load_artifact()        --> Read JSON from disk
snapshot_artifact()    --> Save versioned backup
validate_only()        --> Run validator without generation
```

**Notable step variants**:
- `step_9_scene_briefs.py` (original batch) and `step_9_scene_briefs_v2.py` (individual) both exist. Orchestrator imports V2.
- `step_10_draft_writer.py` and `step_10_first_draft.py` both exist. Orchestrator imports `step_10_first_draft.py`.

### 2.3 Validators

Each step has a corresponding validator. Validators implement:
- `validate(artifact) -> (bool, List[str])` -- Returns validation status and error list
- `fix_suggestions(errors) -> List[str]` -- Returns actionable remediation
- A `VERSION` class attribute for tracking schema versions

### 2.4 Prompt Templates

Prompt files exist for Steps 0-9. Each prompt class generates:
- `system` prompt: Role instructions for the AI model
- `user` prompt: Step-specific context and instructions
- `prompt_hash`: SHA-256 hash for reproducibility tracking

**Gap**: There is no `step_10_prompt.py`. Step 10 constructs prompts inline, breaking the separation of concerns.

### 2.5 Error Recovery

**File**: `src/pipeline/error_recovery.py` (403 lines)

- Retry with exponential backoff (base 2, max 5 retries)
- Step-specific auto-fix strategies
- Custom exception hierarchy: `ValidationError`, `RateLimitError`, `APIError`
- Recovery state tracking per project

### 2.6 Progress Tracking

**File**: `src/pipeline/progress_tracker.py` (231 lines)

- Checkpoint-based resumption via `checkpoint.json`
- Time estimation with step-specific multipliers (Step 9: 2x, Step 10: 3x)

---

## 3. Scene Engine Architecture

### 3.1 Overview

The Scene Engine is a fully independent subsystem at `src/scene_engine/`. It contains ~55 Python files across 10 subpackages.

**Critical architectural observation**: The Scene Engine is largely disconnected from the main pipeline. The pipeline generates scenes through its own step classes (Steps 8-10), while the Scene Engine provides a parallel, more sophisticated scene management stack. The two systems share no common interfaces.

### 3.2 Core Models

**File**: `src/scene_engine/models.py` (372 lines)

- **`SceneCard`**: Main model with scene_type, pov, viewpoint, tense, scene_crucible, place, time
- **`ProactiveScene`**: Goal (5-point criteria) -> Conflict (escalating obstacles) -> Outcome
- **`ReactiveScene`**: Reaction -> Dilemma (2+ bad options) -> Decision -> Next goal stub
- **Save the Cat enhancements**: emotional_polarity, emotional_start/end, conflict_parties, storyline

### 3.3 Subpackage Architecture

| Subpackage | Purpose |
|------------|---------|
| `chaining/` | Scene-to-scene chain link management |
| `drafting/` | Prose drafting with POV consistency and exposition tracking |
| `export/` | Scene-level export |
| `generation/` | AI-driven scene generation with template system |
| `integration/` | Master service facade |
| `persistence/` | SQLAlchemy database persistence |
| `planning/` | Scene sequence planning |
| `quality/` | Quality assessment and scoring |
| `triage/` | Scene triage and corrections |
| `validation/` | Multi-rule validation pipeline |

### 3.4 Master Service (Facade)

**File**: `src/scene_engine/integration/master_service.py` (907 lines)

Contains four major inner systems:
1. **`EventSystem`**: Pub/sub event bus with background thread processing
2. **`WorkflowEngine`**: Automated workflow with dependency resolution and retry
3. **`SceneEngineAPI`**: Internal route-based API (NOT connected to FastAPI)
4. **`EngineConfiguration`**: Centralized config dataclass

---

## 4. API Layer

### 4.1 FastAPI Server (Primary)

**File**: `src/api/main.py` (435 lines)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/projects` | Create new novel project |
| GET | `/projects` | List all projects |
| GET | `/projects/{project_id}` | Get project status |
| POST | `/execute/step/{step_number}` | Execute a pipeline step |
| POST | `/generate/full` | Start full novel generation (background) |
| POST | `/export` | Export manuscript |
| GET | `/download/{project_id}/{format}` | Download exported file |
| GET | `/validate/{project_id}/step/{step_number}` | Validate a step artifact |

**API Design Issues**:
1. Large if/elif chain for step dispatch (violates open/closed principle)
2. No authentication or authorization
3. No API versioning (no `/v1/` prefix)
4. No rate limiting
5. CORS allows all origins by default (`*`)
6. Background task uses `async def` calling synchronous methods (blocks event loop)

### 4.2 Flask Observability Server (Secondary)

**File**: `src/observability/server.py` (434 lines)

Separate Flask server on port 5000 with `/projects`, `/health`, `/metrics`, `/events` endpoints and embedded HTML dashboard.

**Architectural concern**: Two separate web servers creates operational complexity.

---

## 5. Observability System

**File**: `src/observability/events.py` (328 lines)

- **`MetricsCollector`**: Background thread collecting system metrics every 5 seconds via `psutil`
- **`emit_event()`**: Enriches events with metrics, writes JSONL, updates status.json
- Events stored as append-only JSONL files
- No log rotation, no structured logging framework, no distributed tracing

---

## 6. Configuration and Dependencies

### Dependencies (requirements.txt)

```
openai>=1.99.9,<2.0.0
anthropic>=0.21.0
httpx>=0.27.0,<0.28.0
python-dotenv>=1.0.0
pydantic>=2.0.0
tqdm>=4.60.0
agency-swarm>=0.7.0
psutil>=5.9.0
flask>=2.3.0
flask-cors>=4.0.0
```

**Missing from requirements.txt** (used in code but not declared):
- `fastapi`, `uvicorn`, `sqlalchemy`, `python-docx`, `ebooklib`

### Configuration Management

No centralized configuration system. Config is scattered across environment variables, hardcoded defaults, and class constructors.

---

## 7. Design Patterns Used

| Pattern | Location | Quality |
|---------|----------|---------|
| Orchestrator/Pipeline | orchestrator.py | Correct |
| Template Method (informal) | All step files | Partial - no abstract base class |
| Strategy | generator.py, model_selector.py | Correct |
| Circuit Breaker | bulletproof_generator.py | Correct (5 failures, 5min reset) |
| Facade | master_service.py | Correct |
| Observer/Event | master_service.py EventSystem | Correct |
| Builder (informal) | All prompt files | Partial |
| Chain of Responsibility | error_recovery.py | Partial |
| Singleton | bulletproof_generator.py, events.py | Correct |
| Repository | persistence/crud.py | Correct |
| Workflow Engine | master_service.py WorkflowEngine | Correct |

---

## 8. Coupling and Cohesion Assessment

### High Coupling Issues

1. **`sys.path.insert` hack** in orchestrator.py and server.py - fragile import mechanism
2. **Phantom import `src.ui.progress_tracker`** - module doesn't exist, will crash at runtime
3. **Hardcoded `"artifacts"` path** across 15+ classes
4. **Duplicate `generate_scene_prose()`** method in generator.py (lines 292 and 440)
5. **Dual web servers** (FastAPI + Flask) not connected
6. **Pipeline and Scene Engine isolation** - overlapping capabilities with no shared interfaces

### Pipeline vs Scene Engine Capability Overlap

| Capability | Pipeline | Scene Engine |
|------------|----------|--------------|
| Scene data models | Dict-based JSON | Pydantic SceneCard |
| Scene generation | Steps 9-10 | SceneGenerationService |
| Validation | Step validators | SceneValidationService |
| Persistence | Flat JSON files | SQLAlchemy database |
| Export | ManuscriptExporter | ExportService |
| Quality assessment | None | QualityAssessmentService |
| Scene chaining | chain_link field | ChainLinkGenerator |

### Low Cohesion Issues

1. **`AIGenerator`** (559 lines) - handles provider detection, API calls, JSON parsing, validation retry, prose generation
2. **`master_service.py`** (907 lines) - contains EventSystem, WorkflowEngine, SceneEngineAPI, and facade
3. **Step 3** (738 lines) - character generation + JSON parsing + emergency fallbacks + logline parsing

---

## 9. Architectural Gaps and Inconsistencies

### Critical Gaps

| ID | Gap | Impact |
|----|-----|--------|
| G-01 | `src.ui.progress_tracker` doesn't exist | Runtime ImportError crashes orchestrator, Steps 9-10 |
| G-02 | Missing deps in requirements.txt | Installation fails for API and persistence |
| G-03 | No `__init__.py` in observability/ | Package import may fail |
| G-04 | `regenerate_downstream()` is a stub | Cascade invalidation doesn't work |
| G-05 | Duplicate `generate_scene_prose()` | Second definition silently shadows first |

### Inconsistencies

| ID | Inconsistency |
|----|---------------|
| I-01 | Two web frameworks (FastAPI + Flask) |
| I-02 | Two scene generation systems (Pipeline + Scene Engine) |
| I-03 | Two event systems (observability vs master_service) |
| I-04 | Two persistence approaches (JSON files vs SQLAlchemy) |
| I-05 | Two validation frameworks (tuple vs Pydantic) |
| I-06 | Step 10 has no prompt file (all others do) |
| I-07 | Two Step 9 implementations coexist |
| I-08 | Two Step 10 implementations coexist |

### Security Concerns

| ID | Concern |
|----|---------|
| S-01 | No authentication on API endpoints |
| S-02 | CORS allows all origins by default |
| S-03 | No input sanitization on user briefs |
| S-04 | Path traversal potential in download endpoint |
| S-05 | 157 broad `except Exception` handlers |

---

## 10. Integration Points

### External Integrations

| Integration | Protocol | Files |
|-------------|----------|-------|
| OpenAI API | REST (SDK) | generator.py, bulletproof_generator.py |
| Anthropic API | REST (SDK) | generator.py, bulletproof_generator.py |
| OpenRouter API | REST (httpx) | generator_openrouter.py |
| File system | Local I/O | All step files, orchestrator, events |
| SQLAlchemy DB | SQL (SQLite) | scene_engine/persistence/ |

### Missing Integration Points

| Gap | Description |
|-----|-------------|
| Pipeline <-> Scene Engine | No connection between Steps 8-10 and Scene Engine |
| FastAPI <-> Flask | Two servers with no shared state |
| Scene Engine API <-> FastAPI | Internal routes not connected to HTTP |
| Observability <-> Logging | No integration with Python logging module |

---

## 11. Recommendations

### Critical (Must Fix)

1. **Resolve `src.ui.progress_tracker` phantom import** - create module or wrap in try/except
2. **Complete `requirements.txt`** - add fastapi, uvicorn, sqlalchemy
3. **Fix duplicate `generate_scene_prose()`** - remove duplicate, verify callers
4. **Add `__init__.py` to `src/observability/`**

### Important (Should Fix)

5. **Unify web server stack** - consolidate Flask into FastAPI
6. **Bridge Pipeline and Scene Engine** - use SceneCard validation in Steps 9-10
7. **Create `BaseStep` abstract base class** - formalize step interface
8. **Centralize configuration** - Pydantic BaseSettings with typed defaults
9. **Implement `regenerate_downstream()`** - complete cascade invalidation
10. **Reduce broad exception handling** - replace 157 `except Exception` with targeted catches

### Nice-to-Have

11. Add API authentication
12. Add API versioning (`/v1/` prefix)
13. Integrate structured logging
14. Remove dead code (old Step 9, old Step 10, unused agency-swarm)
15. Split `master_service.py` into 4 separate files
16. Split `AIGenerator` into provider-specific implementations
17. Add proper Python packaging via pyproject.toml

---

## Appendix: Dependency Graph (Simplified)

```
                    [User Brief]
                        |
                   [API Layer]
                   /         \
          [FastAPI]         [Flask Dashboard]
              |                    |
      [SnowflakePipeline]    [events.py]
         /    |    \              |
   [Steps] [Validators] [Prompts]
      |
   [AIGenerator] --> [BulletproofGenerator]
      |                    |
   [OpenAI SDK]      [Anthropic SDK]


   [SceneEngineMaster] (DISCONNECTED from pipeline)
      |
   [SceneGenerationService]
   [PersistenceService] --> [SQLAlchemy]
   [SceneValidationService]
   [QualityAssessmentService]
   [ExportService]
   [ChainLinkGenerator]
```

---

*End of Architecture Analysis Report*
