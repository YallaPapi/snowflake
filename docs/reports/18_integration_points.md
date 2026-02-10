# Integration Points Report

**Timestamp**: 2026-02-07
**Project**: Snowflake Novel Generation Engine
**Location**: C:\Users\asus\Desktop\projects\snowflake

---

## 1. LLM PROVIDER INTEGRATIONS

### Architecture
The system implements a **multi-provider strategy** with fallback chains:
- **Primary**: Anthropic (Claude)
- **Secondary**: OpenAI (GPT-4o-mini)
- **Tertiary**: OpenRouter (uncensored models for adult content)
- **Fallback**: Ollama (local inference)

### Connection Mechanism

**File**: `src/ai/generator.py`
- **Client Library**: `anthropic.Anthropic` / `openai.OpenAI`
- **API Key Loading**: Environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)
- **Auto-Detection**: If provider not specified, detects based on available API keys (prefers OpenAI for GPT-4)
- **Error Handling**: Exponential backoff retry logic (max 3 retries with 2^n second delays)

**File**: `src/ai/generator_openrouter.py`
- **API Endpoint**: `https://openrouter.ai/api/v1`
- **Headers**: Authorization, HTTP-Referer, X-Title for site tracking
- **Uncensored Models Support**: MythoMax, Nous-Hermes, Dolphin, Midnight-Rose, Erebus, Goliath
- **Configuration**: `OPENROUTER_API_KEY`, `OPENROUTER_SITE_NAME`, `OPENROUTER_SITE_URL`

**File**: `src/ai/model_selector.py`
- **Smart Model Routing**: Maps pipeline steps (0-10) to appropriate model tiers
- **Model Tiers**:
  - **Fast**: Haiku-20240229 (Anthropic), GPT-4o-mini (OpenAI), Llama-3.2-3B (OpenRouter)
  - **Balanced**: Same as fast (stability-focused)
  - **Quality**: Sonnet-20240620 (Anthropic), GPT-4o (OpenAI), Claude-3.5-Sonnet (OpenRouter)
- **Current Strategy**: All steps routed to "fast" tier for stability
- **Configuration**: Temperature (0.3-0.5), max_tokens (1500-4000 per step)

### Issues Found
1. **Mixed Model Versions**: Haiku model references outdated versions alongside new Sonnet refs
2. **No Circuit Breaker**: Failed API calls trigger retries without provider health checks
3. **No Token Counting**: Estimations in model_selector.py are hardcoded, not actual token usage
4. **OpenRouter Integration Incomplete**: Site metadata required but not always configured

---

## 2. FILE-BASED PERSISTENCE (Artifacts Directory)

### Directory Structure
**Base Path**: `artifacts/` (created dynamically)

```
artifacts/
├── {project_id}/
│   ├── project.json                           # Project metadata
│   ├── initial_brief.json                     # User's story concept
│   ├── status.json                            # Pipeline execution status
│   ├── events.log                             # JSONL event stream
│   ├── metrics.json                           # Performance metrics
│   ├── health.json                            # Health status
│   ├── step_0_first_things_first.json        # Snowflake step outputs
│   ├── step_1_one_sentence_summary.json
│   ├── ... (steps 2-9)
│   ├── step_10_manuscript.json                # Final draft
│   ├── manuscript.docx                        # Export formats
│   ├── manuscript.epub
│   └── manuscript.md
```

### Connection Points
- `SnowflakePipeline._load_step_artifact()`: Loads JSON artifacts from disk
- `SnowflakePipeline._update_project_state()`: Updates project.json after each step
- `src/observability/events.emit_event()`: Appends to events.log and updates status.json

### Issues Found
1. **No Concurrent Write Protection**: Multiple threads could write events.log simultaneously
2. **Hash-Based Caching**: upstream_hash computed but never used for skip logic
3. **No Artifact Validation on Load**: Malformed JSON would crash steps
4. **No Cleanup**: Old projects/artifacts accumulate indefinitely

---

## 3. DATABASE PERSISTENCE (SQLAlchemy)

### Architecture
**ORM Framework**: SQLAlchemy with SQLite backend
**Location**: `src/scene_engine/persistence/`
**Engine**: `sqlite:///scene_engine.db` (local file)

### Core Models (`src/scene_engine/persistence/models.py`)

- **Project**: project_id, title, genre, target_word_count, status
- **SceneCardDB**: scene_id, scene_type, pov, proactive_data (JSON), reactive_data (JSON)
- **ProseContent**: content (text), word_count, readability_score, version
- **ChainLinkDB**: source_scene_id, target_scene_id, transition_type
- **Character**: name, role, goals (JSON), conflicts (JSON)
- **SceneSequenceDB**: scene_order (stored sequence)
- **ValidationLog**: target_type, target_id, is_valid, errors (JSON)

### CRUD Operations (`src/scene_engine/persistence/crud.py`)
- `ProjectCRUD`, `SceneCardCRUD`, `ProseContentCRUD`, `ChainLinkCRUD`, `CharacterCRUD`, `SceneSequenceCRUD`

### Issues Found
1. **No Migration System**: No Alembic migrations
2. **No Connection Pooling**: Default pool_size=5 could bottleneck
3. **No Transaction Management**: Implicit auto-commit
4. **No Backup Strategy**: Single SQLite file
5. **Unused Versioning**: ProseContent has version field but no history retrieval

---

## 4. API ENDPOINTS

### FastAPI Main Server (`src/api/main.py`, Port 8000)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/projects` | Create new project |
| GET | `/projects` | List all projects |
| GET | `/projects/{project_id}` | Get project status |
| POST | `/execute/step/{step_number}` | Execute pipeline step |
| POST | `/generate/full` | Full pipeline (async background) |
| POST | `/export` | Export manuscript |
| GET | `/download/{project_id}/{format}` | Download exported file |
| GET | `/validate/{project_id}/step/{step_number}` | Validate step artifact |

### Scene Engine API (`src/api/scene_engine_endpoints.py`)

- `POST /scene/plan` - Scene planning
- `POST /scene/draft` - Scene drafting
- `POST /scene/triage` - Scene evaluation/redesign
- `GET /scene/{scene_id}` - Retrieve scene

### Issues Found
1. **No Rate Limiting**: Multiple concurrent `/generate/full` calls could overload
2. **Background Task Queue Not Persistent**: Tasks lost on server restart
3. **Error Responses Not Standardized**: HTTP 500 returns raw exception strings
4. **No API Versioning**: No `/v1/` prefix
5. **CORS Config**: Hardcoded `"*"` for origins

---

## 5. OBSERVABILITY INTEGRATION

### Event System (`src/observability/events.py`)

- `emit_event(project_id, event_type, payload)` with automatic metrics enrichment
- **Storage**: JSONL at `artifacts/{project_id}/events.log`, status at `status.json`
- **Metrics**: CPU, memory, disk, step duration, tokens, API calls, errors
- **Collection**: Background thread every 5 seconds via psutil

### Dashboard (`src/observability/server.py`, Port 5000)

| Path | Purpose |
|------|---------|
| `/` | HTML dashboard |
| `/health` | System health |
| `/metrics` | Prometheus-style metrics |
| `/projects/{id}/status` | Project status |
| `/projects/{id}/events` | Event stream |
| `/projects/{id}/summary` | Comprehensive summary |

### Issues Found
1. **Metrics Injection Overhead**: Every event enriched with system metrics
2. **No Metrics Persistence**: Lost on restart
3. **Health Checks Simplistic**: Only checks API keys, no connectivity test
4. **No Alerting**: Metrics collected but no threshold-based alerting

---

## 6. EXPORT INTEGRATIONS

### Manuscript Exporter (`src/export/manuscript_exporter.py`)

| Format | Library | Status |
|--------|---------|--------|
| DOCX | `python-docx` | Full support |
| EPUB | `ebooklib` | Full support |
| Markdown | Built-in | Full support |
| PDF | None | Not implemented |
| JSON | Built-in | Full support |

### Issues Found
1. **Optional Dependencies**: DOCX/EPUB export fail silently if libraries missing
2. **No Template System**: Hardcoded structure
3. **No Streaming Export**: Entire file buffered in memory

---

## 7. PIPELINE STEP-TO-STEP DATA FLOW

### Dependency Chain
```
Step 0 (brief→concept) → Step 1 (→logline) → Step 2 (→5 sentences+moral)
  → Step 3 (→characters) → Step 5 (→character synopses) → Step 7 (→bibles)
  Step 2 → Step 4 (→5 paragraphs) → Step 6 (→long synopsis)
  Steps 6,7 → Step 8 (→scene list) → Step 9 (→scene briefs) → Step 10 (→manuscript)
```

### Data Flow Mechanism
- Each step reads upstream JSON artifacts from disk
- No in-memory pipeline state
- Upstream hash tracking computed but never used for cache/skip logic

### Issues Found
1. **Inefficient Re-Loading**: Each step re-reads all upstream artifacts
2. **No Parallel Execution**: Steps 4, 5, 7 could run concurrently but forced sequential
3. **No Rollback**: Failed step N doesn't invalidate downstream steps

---

## 8. SCENE ENGINE INTERNAL INTEGRATION

### Master Service (`src/scene_engine/integration/master_service.py`)

**Component Initialization:**
- EventSystem (daemon thread for event processing)
- PersistenceService (SQLAlchemy database)
- SceneValidationService (7 validation rules)
- QualityAssessmentService (6 dimensions)
- ChainLinkGenerator (scene transitions)
- ExportService (format conversion)
- SceneGenerationService (AI-powered generation)
- WorkflowEngine (multi-step with dependencies/retry)
- SceneEngineAPI (internal route-based API, 26+ endpoints)

### Issues Found
1. **Event System Race Condition**: Subscriber list modified while dispatching
2. **Incomplete Workflow Steps**: Quality/Export/Persistence steps return mock success
3. **No Circuit Breaker**: Failed workflow steps don't stop dependent steps

---

## 9. EXTERNAL TOOL INTEGRATIONS

### TaskMaster MCP (`.mcp.json`)
- Configured but not actively called by pipeline
- API keys in .mcp.json (security risk)

### Agency Swarm (`demo_agency_collaboration.py`)
- 7 agent types: NovelDirector, ConceptMaster, StoryArchitect, CharacterCreator, etc.
- Demo/PoC only, not integrated into main pipeline

---

## 10. MISSING INTEGRATIONS BETWEEN PIPELINE AND SCENE ENGINE

### Critical Gaps

| # | Gap | Current State | Fix Needed |
|---|-----|--------------|------------|
| 1 | Step 10 → Scene Engine | Step 10 uses AIGenerator directly | Use SceneGenerationService |
| 2 | No SceneCard from Snowflake | Steps 8-9 produce text briefs | Map Step 9 output → SceneCard |
| 3 | Database not used by pipeline | Artifacts stored as JSON files | Use PersistenceService |
| 4 | Dual event systems | emit_event() vs EventSystem class | Unified event bridge |
| 5 | Validation not shared | Each step has custom validator | Centralize in SceneValidationService |
| 6 | No quality assessment | Step 10 has no quality check | Run QualityAssessmentService |
| 7 | No scene chaining | Scenes generated independently | Apply ChainLinkGenerator |
| 8 | Config mismatch | Pipeline uses artifacts/, Scene Engine uses SQLite | Unified EngineConfiguration |
| 9 | Error recovery isolated | Two separate retry systems | Cross-system recovery |
| 10 | Export duplication | ManuscriptExporter vs ExportService | Single export facade |

---

## CONCLUSION

**Total Integration Points**: 40+ sub-integrations across 10 major categories

**Strengths**:
- Multi-LLM provider support with graceful degradation
- Comprehensive observability (events, metrics, dashboard)
- RESTful API with OpenAPI specification
- Background task handling for long operations

**Weaknesses**:
- Pipeline and Scene Engine operate in parallel without integration
- Event systems duplicated
- Validation/quality services not used by pipeline
- Database persistence isolated from artifact storage
- No error recovery coordination between systems

**Priority Fixes**:
1. Integrate SceneGenerationService into Step 10
2. Unify event systems with adapter pattern
3. Map Step 9 outputs to SceneCard objects
4. Implement PersistenceService for pipeline artifacts
5. Add quality assessment before export
