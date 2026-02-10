# API & Observability Deep Dive Report
**Generated**: 2026-02-07 09:30 UTC
**Analyst**: API/Observability Explorer Agent
**Scope**: Complete API and monitoring system analysis

---

## EXECUTIVE SUMMARY

The Snowflake project implements a dual-server architecture:
1. **FastAPI Server** (src/api/main.py) - REST API for novel generation pipeline
2. **Flask Observability Server** (src/observability/server.py) - Real-time monitoring dashboard

The system handles 11-step novel generation with comprehensive event tracking, performance metrics, and health monitoring.

---

## SECTION 1: API LAYER ARCHITECTURE (src/api/)

### 1.1 Server Configuration

**Framework**: FastAPI with Uvicorn
**File**: src/api/main.py (435 lines)

#### Startup/Shutdown Lifecycle (Lines 59-79)
- Uses `@asynccontextmanager` lifespan handler
- **Startup**: Initializes SnowflakePipeline, ManuscriptExporter, and active_generations dict
- **API Key Check**: Warns if neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set
- **Shutdown**: Gracefully cancels any active background tasks

#### FastAPI Configuration (Lines 82-87)
```python
app = FastAPI(
    title="Snowflake Novel Generation API",
    description="Generate complete novels using the Snowflake Method",
    version="1.0.0",
    lifespan=lifespan
)
```

### 1.2 CORS Configuration

**Status**: CONFIGURED (Lines 89-96)
```python
CORSMiddleware(
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Analysis**:
- SECURITY GAP: Default is "*" (allow all origins) - should be restricted in production
- All HTTP methods allowed
- Credentials enabled for CORS requests
- Any header accepted

### 1.3 Running the Server

**Command**:
```bash
python -m src.api.main
```

**Configuration from Environment**:
- API_HOST (default: "0.0.0.0")
- API_PORT (default: 8000)
- RELOAD (default: "false")

---

## SECTION 2: API ENDPOINTS - COMPLETE INVENTORY

### 2.1 Health & Status Endpoints

#### GET /health
- **Returns**: HealthCheck response
- **Fields**: status, timestamp, version
- **Response Code**: 200

### 2.2 Project Management Endpoints

#### POST /projects
**Purpose**: Create a new novel project

**Request Model** (NovelBrief):
- project_name: str (required)
- brief: str (required, one-line story concept)
- target_words: int (default: 90000)
- model_provider: Optional[str] (None, "anthropic" or "openai")

**Response Model** (ProjectStatus):
- project_id: str
- project_name: str
- current_step: int (0-10)
- steps_completed: List[int]
- is_complete: bool
- total_word_count: Optional[int]
- created_at: str (ISO timestamp)
- last_updated: Optional[str] (ISO timestamp)

#### GET /projects
**Purpose**: List all projects
**Order**: By creation date, descending

#### GET /projects/{project_id}
**Purpose**: Get status of specific project
**Status Codes**: 200, 404, 500

### 2.3 Step Execution Endpoints

#### POST /execute/step/{step_number}
**Purpose**: Execute a specific pipeline step

**Request Model** (StepExecutionRequest):
- project_id: str
- step_number: int
- additional_params: Optional[Dict[str, Any]] (default: {})

**Step-Specific Handling**:
- Steps 0-1: Load initial_brief.json and pass brief
- Steps 2-9: Execute directly
- Step 10: Accepts target_words in additional_params (default: 90000)

**Status Codes**: 200, 400, 422, 500

#### POST /generate/full
**Purpose**: Generate complete novel (async background task)

**Async Behavior**:
- Uses FastAPI BackgroundTasks (safe on Windows)
- Emits events: "generation_progress", "generation_failed", "generation_complete", "generation_error"

### 2.4 Export & Download Endpoints

#### POST /export
**Supported Formats**: docx, epub, markdown
**Prerequisites**: step_10_manuscript.json must exist

#### GET /download/{project_id}/{format}
**Format Mapping**: docx, epub, markdown, json, text

### 2.5 Validation Endpoints

#### GET /validate/{project_id}/step/{step_number}

---

## SECTION 3: SCENE ENGINE API (src/api/scene_engine_endpoints.py)

**Router**: APIRouter(prefix="/scene", tags=["Scene Engine"])

### POST /scene/plan (Task 47.2)
**Request Model** (ScenePlanRequest):
- scene_type: str (regex: "^(proactive|reactive)$")
- scene_crucible: str (min_length: 10)
- pov_character: str (min_length: 1)
- pov: str (default: "third_limited")
- tense: str (default: "past")
- setting: Optional[str]
- context: Optional[Dict[str, Any]]

### POST /scene/draft (Task 47.3)
**Request Model** (SceneDraftRequest):
- scene_card: Dict[str, Any] (required)
- style_preferences: Optional[Dict[str, Any]]
- target_word_count: int (1000, ge=100, le=5000)

### POST /scene/triage (Task 47.4)
**Decision Types**: YES, MAYBE, NO

### GET /scene/{scene_id} (Task 47.5)
### GET /scene/ (List Scenes with pagination)
### DELETE /scene/{scene_id}

---

## SECTION 4: OBSERVABILITY SYSTEM (src/observability/)

### 4.1 Event System (events.py)

**PerformanceMetrics Dataclass**:
- timestamp, cpu_percent, memory_mb, disk_usage_mb
- step_duration, tokens_processed, api_calls, error_count
- Collected every 5 seconds by background thread

**HealthStatus Dataclass**:
- ai_provider_healthy, disk_space_healthy (>1GB free)
- memory_healthy (<90% usage), pipeline_active, last_error

**MetricsCollector Class**:
- Background daemon thread
- Keeps last 1000 entries in memory
- Periodic disk snapshots (last 100 entries)

### 4.2 Event Emission Functions
- emit_event() — Core event emission with metrics enrichment
- emit_step_start() — "step_started" events
- emit_step_complete() — "step_completed" events
- emit_step_progress() — "step_progress" events
- emit_error() — "error" events
- start_monitoring() / stop_monitoring()
- save_metrics_snapshot()
- get_project_summary()

### 4.3 Observability Server (server.py)

**Framework**: Flask + CORS, Port 5000

**Endpoints**:
- GET /health — System health check
- GET /projects — List all projects
- GET /projects/<id>/status — Project status
- GET /projects/<id>/events — Recent events (n parameter)
- GET /metrics — Prometheus-style metrics export
- GET /projects/<id>/summary — Comprehensive summary
- GET /projects/<id>/metrics — Project-specific metrics
- GET / — HTML dashboard with real-time updates (3-5s refresh)

---

## SECTION 5: COMPLETE ENDPOINT SUMMARY TABLE

| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| GET | /health | Health check | No | 200 |
| POST | /projects | Create project | No | 200/500 |
| GET | /projects | List projects | No | 200 |
| GET | /projects/{id} | Get status | No | 200/404/500 |
| POST | /execute/step/{n} | Execute step | No | 200/400/422/500 |
| POST | /generate/full | Full generation | No | 200/500 |
| POST | /export | Export manuscript | No | 200/404/500 |
| GET | /download/{id}/{fmt} | Download file | No | 200/400/404/500 |
| GET | /validate/{id}/step/{n} | Validate step | No | 200/500 |
| POST | /scene/plan | Plan scene | No | 200/422/500 |
| POST | /scene/draft | Draft scene | No | 200/400/422/500 |
| POST | /scene/triage | Triage scene | No | 200/400/422/500 |
| GET | /scene/{id} | Get scene | No | 200/404/500 |
| GET | /scene/ | List scenes | No | 200/500 |
| DELETE | /scene/{id} | Delete scene | No | 200/404/500 |
| GET | /health (obs) | System health | No | 200/503 |
| GET | /projects (obs) | List projects | No | 200 |
| GET | /projects/{id}/status | Project status | No | 200/404 |
| GET | /projects/{id}/events | Get events | No | 200 |
| GET | /metrics | Prometheus metrics | No | 200/500 |
| GET | /projects/{id}/summary | Project summary | No | 200 |
| GET | /projects/{id}/metrics | Project metrics | No | 200/404/500 |
| GET | / (obs) | Dashboard HTML | No | 200 |

**Total API Endpoints**: 23

---

## SECTION 6: CRITICAL FINDINGS & GAPS

### Security Issues (HIGH PRIORITY)
1. **No Authentication** — Anyone can call any endpoint
2. **Default CORS allows all origins**
3. **No rate limiting** — DDoS vulnerable
4. **No request signing**
5. **Direct file access** — No path validation

### Functional Issues (MEDIUM PRIORITY)
1. No request tracking / correlation IDs
2. No async operation tracking
3. Minimal error logging
4. No input sanitization beyond Pydantic

### Observability Gaps (MEDIUM PRIORITY)
1. No request count/latency metrics
2. Limited error rate tracking
3. No distributed tracing
4. Basic health checks only

---

## SECTION 7: FILE STRUCTURE

```
src/api/
├── __init__.py
├── main.py                        # FastAPI server (435 lines)
├── scene_engine_endpoints.py      # Scene API endpoints (446 lines)
└── tests/
    ├── __init__.py
    ├── conftest.py               # Test fixtures & config (341 lines)
    ├── test_scene_engine_integration.py  # Integration tests (537 lines)
    ├── test_scene_engine_performance.py  # Performance tests (516 lines)
    └── run_tests.py              # Test runner CLI (326 lines)

src/observability/
├── events.py                     # Event system & metrics (328 lines)
└── server.py                     # Flask dashboard (433 lines)

artifacts/
└── {project_id}/
    ├── events.log                # JSONL event stream
    ├── status.json               # Current project status
    ├── metrics.json              # Periodic metrics snapshots
    ├── initial_brief.json        # Novel brief input
    ├── step_0_* through step_10_*  # Step outputs
    └── step_10_manuscript.json   # Final manuscript
```
