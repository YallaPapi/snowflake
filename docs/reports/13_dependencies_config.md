# Dependencies & Configuration Report

**Generated**: 2026-02-07 12:45 UTC
**Analyst**: Dependencies Explorer Agent
**Scope**: All dependencies, configuration, and environment analysis

## 1. Python Dependencies

### Core Runtime Dependencies (from requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| openai | >=1.99.9,<2.0.0 | OpenAI API client for GPT models |
| anthropic | >=0.21.0 | Anthropic Claude API client |
| httpx | >=0.27.0,<0.28.0 | HTTP client (pinned to prevent proxies argument conflicts) |
| python-dotenv | >=1.0.0 | Environment variable loading from .env |
| pydantic | >=2.0.0 | Data validation and settings management |
| tqdm | >=4.60.0 | Progress bar visualization |
| agency-swarm | >=0.7.0 | Collaborative AI agents framework |
| psutil | >=5.9.0 | System and process utilities for monitoring |
| flask | >=2.3.0 | Web framework for observability server |
| flask-cors | >=4.0.0 | CORS support for Flask |

### Optional/Implicit Dependencies (detected from imports)

| Package | Purpose | Status |
|---------|---------|--------|
| uvicorn | ASGI server for FastAPI | Not explicitly in requirements.txt but used in main.py |
| fastapi | Web framework for REST API | Not in requirements.txt but imported |
| docx (python-docx) | Word document generation | Conditionally imported with fallback |
| ebooklib | EPUB book generation | Conditionally imported with fallback |
| requests | HTTP requests library | Used by OpenRouter generator |

### Development/Test Dependencies

From analysis of conftest.py and test imports:
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | (implicit) | Test framework |
| unittest | (standard library) | Unit test framework |

### System-Level Dependencies Detected

- **Standard Library**: json, os, sys, pathlib, typing, datetime, asyncio, threading, uuid, hashlib, time, enum
- **System Packages**: Git (for version control), Node.js/npm (for task-master-ai MCP integration)

---

## 2. Python Version Requirements

- **Required**: Python 3.10+ (minimum based on project structure and async features)
- **Current Environment**: Python 3.14.0
- **Compatibility**: Project uses async/await extensively, requires modern Python

---

## 3. Environment Variables

### Required API Keys

| Variable | Format | Purpose | Provider |
|----------|--------|---------|----------|
| ANTHROPIC_API_KEY | sk-ant-api03-* | Claude model API authentication | Anthropic (REQUIRED for main pipeline) |
| OPENAI_API_KEY | sk-proj-* | GPT model API authentication | OpenAI (optional, auto-detects) |

### Optional API Keys

| Variable | Format | Purpose | Provider |
|----------|--------|---------|----------|
| PERPLEXITY_API_KEY | pplx-* | Research and analysis | Perplexity |
| GOOGLE_API_KEY | (varies) | Gemini models | Google |
| MISTRAL_API_KEY | (varies) | Mistral models | Mistral AI |
| XAI_API_KEY | (varies) | Grok models | xAI |
| GROQ_API_KEY | (varies) | Groq models | Groq |
| OPENROUTER_API_KEY | (varies) | OpenRouter platform | OpenRouter |
| AZURE_OPENAI_API_KEY | (varies) | Azure OpenAI endpoint | Microsoft Azure |
| OLLAMA_API_KEY | (varies) | Ollama local server auth | Ollama |
| GITHUB_API_KEY | ghp_* or github_pat_* | GitHub API access | GitHub |

### Configuration Environment Variables

| Variable | Default | Purpose | Used In |
|----------|---------|---------|---------|
| ALLOWED_ORIGINS | * | CORS allowed origins (comma-separated) | API server |
| API_HOST | 0.0.0.0 | FastAPI server host | api/main.py |
| API_PORT | 8000 | FastAPI server port | api/main.py |
| RELOAD | false | FastAPI auto-reload on changes | api/main.py |
| TESTING | false | Test mode flag | Conftest |
| OPENROUTER_SITE_NAME | snowflake-novel-generator | Site name for OpenRouter | generator_openrouter.py |
| OPENROUTER_SITE_URL | http://localhost | Site URL for OpenRouter | generator_openrouter.py |

### Environment Variable Usage Pattern

The project uses `os.getenv()` with fallback defaults for optional variables and `os.environ[]` with exception handling for required keys. Environment variables are loaded via `python-dotenv` at module initialization in `src/ai/generator.py`.

---

## 4. Configuration Files

### .env Files

- **Location**: `C:\Users\asus\Desktop\projects\snowflake\.env` (contains actual API keys)
- **Template**: `.env.example` (documented template with all possible keys)
- **Status**: Present and populated with real credentials

### .taskmaster Configuration

**File**: `.taskmaster/config.json`
```
Models Configuration:
- main: claude-3-5-sonnet-20241022 (Anthropic, 8192 max_tokens, temp=0.2)
- research: sonar-pro (Perplexity, 8700 max_tokens, temp=0.1)
- fallback: claude-3-5-sonnet-20241022 (Anthropic, 8192 max_tokens, temp=0.2)

Global Settings:
- logLevel: info
- debug: false
- projectName: Snowflake
- ollamaBaseURL: http://localhost:11434/api
- defaultNumTasks: 10
- defaultSubtasks: 5
- defaultPriority: medium
- responseLanguage: English
- defaultTag: master
```

### MCP Configuration

**File**: `.mcp.json`
- Defines task-master-ai MCP server
- Command: `npx --package=task-master-ai task-master-ai`
- All API keys passed as environment variables to MCP server

### Project Configuration

**File**: `pyproject.toml`
```
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests", "src"]
```

---

## 5. Project Structure & File Organization

### Core Source Directories

```
src/
├── ai/                          # AI model integration
│   ├── generator.py             # Base AI generator (Anthropic/OpenAI)
│   ├── model_selector.py        # Model selection by step
│   ├── generator_openrouter.py  # OpenRouter support
│   ├── prose_generator.py       # Prose generation utilities
│   ├── bulletproof_generator.py # Robust generation wrapper
│   └── bulletproof_prose_generator.py
│
├── api/                         # FastAPI REST API
│   ├── main.py                  # API server with endpoints
│   ├── scene_engine_endpoints.py# Scene engine specific endpoints
│   └── tests/                   # API tests with conftest
│
├── pipeline/                    # Snowflake Method pipeline
│   ├── orchestrator.py          # Main pipeline orchestrator
│   ├── error_recovery.py        # Error handling/recovery
│   ├── steps/                   # 11 Snowflake steps (step_0 to step_10)
│   ├── prompts/                 # Step-specific prompts
│   └── validators/              # Step-specific validators
│
├── scene_engine/                # Scene generation system
│   ├── models.py                # Pydantic scene card models
│   ├── generation/              # Scene generation engine
│   ├── persistence/             # Database persistence
│   ├── validation/              # Scene validation
│   ├── chaining/                # Scene chaining/transitions
│   ├── drafting/                # Prose drafting
│   ├── planning/                # Scene planning
│   ├── quality/                 # Quality assessment
│   ├── triage/                  # Scene triage/classification
│   ├── integration/             # Master service integration
│   └── export/                  # Scene export formats
│
├── export/                      # Manuscript export
│   └── manuscript_exporter.py   # DOCX/EPUB export
│
├── observability/               # Monitoring & metrics
│   ├── server.py                # Flask observability server
│   └── events.py                # Event logging and metrics
│
├── schemas/                     # JSON schemas
└── ui/                          # UI utilities
    └── progress_tracker.py      # Progress tracking
```

---

## 6. Import Map & Dependency Graph

### Core Import Patterns

**API Layer** (src/api/main.py):
```
fastapi → pydantic → src.pipeline.orchestrator
↓        ↓           ↓
uvicorn  BaseModel   AIGenerator
cors                 ManuscriptExporter
                     observability.events
```

**Pipeline Layer** (src/pipeline/orchestrator.py):
```
orchestrator → step_0 through step_10 executors
            → observability.events
            → ui.progress_tracker
            → AIGenerator
```

**AI Layer** (src/ai/generator.py):
```
anthropic.Anthropic
openai.OpenAI
dotenv.load_dotenv
os (for env var access)
```

### Potential Circular Dependencies: NONE DETECTED

- Project uses clear layer separation
- No circular imports detected
- All imports follow hierarchical pattern: api → pipeline → steps → generator

---

## 7. External Services & APIs

### AI Services (Required)

| Service | API Key | Models | Purpose |
|---------|---------|--------|---------|
| Anthropic | ANTHROPIC_API_KEY | claude-3-5-sonnet-20241022, claude-3-haiku-20240229, claude-3-5-haiku-20241022 | Primary novel generation |
| OpenAI | OPENAI_API_KEY | gpt-4o, gpt-4o-mini | Alternative to Anthropic |

### AI Services (Optional)

| Service | API Key | Purpose |
|---------|---------|---------|
| OpenRouter | OPENROUTER_API_KEY | Uncensored model access (MythoMax, Nous-Hermes, etc.) |
| Perplexity | PERPLEXITY_API_KEY | Research and real-time information |
| Google Gemini | GOOGLE_API_KEY | Alternative LLM provider |
| xAI Grok | XAI_API_KEY | Alternative LLM provider |
| Groq | GROQ_API_KEY | Fast inference |
| Mistral | MISTRAL_API_KEY | Alternative LLM provider |
| Azure OpenAI | AZURE_OPENAI_API_KEY | Enterprise OpenAI endpoint |
| Ollama | OLLAMA_API_KEY | Local model serving (http://localhost:11434) |

---

## 8. Model Configuration by Pipeline Step

From `src/ai/model_selector.py`:

**All Steps** (0-10): Fast tier
```
Fast Models:
- Anthropic: claude-3-haiku-20240229
- OpenAI: gpt-4o-mini
- OpenRouter: meta-llama/llama-3.2-3b-instruct

Balanced Models:
- Anthropic: claude-3-haiku-20240229
- OpenAI: gpt-4o-mini
- OpenRouter: meta-llama/llama-3.1-8b-instruct

Quality Models:
- Anthropic: claude-3-5-sonnet-20240620
- OpenAI: gpt-4o
- OpenRouter: anthropic/claude-3.5-sonnet
```

Default Configuration Per Step:
- Temperature: 0.3 (consistent, low variance)
- Max Tokens: 2000 (most steps)
- Model Tier: Fast (for stability)

---

## 9. Test Configuration

### pytest Configuration

From `pyproject.toml`:
- asyncio_mode: auto
- asyncio_default_fixture_loop_scope: function
- testpaths: ["tests", "src"]

### Test Setup

From `tests/conftest.py`:
- **Mock API Keys**: Session-scoped fixtures set test keys
  - ANTHROPIC_API_KEY = 'test-key-mock-anthropic-12345'
  - OPENAI_API_KEY = 'test-key-mock-openai-67890'
- **Mock API Clients**: All Anthropic and OpenAI calls mocked
- **Default Response**: Common Step 0 response template
- **Cleanup**: Test keys removed after session

---

## 10. Dependency Issues & Warnings

### Potential Issues Identified

1. **Missing Explicit Dependencies**
   - FastAPI not in requirements.txt (imported in main.py)
   - python-docx not in requirements.txt (optional, conditionally imported)
   - ebooklib not in requirements.txt (optional, conditionally imported)
   - Recommendation: Add to requirements.txt or document as optional

2. **httpx Version Pinning**
   - Pinned to >=0.27.0,<0.28.0 due to proxies argument conflict
   - This is a workaround, monitor for updates

3. **Agency Swarm Version**
   - Required >= 0.7.0 but no upper bound
   - May have breaking changes in future versions

4. **Python Version**
   - Requires 3.10+, environment has 3.14.0
   - No explicit version constraint in pyproject.toml

### No Circular Dependencies Detected

---

## 11. Security Considerations

### API Key Management

- Keys stored in .env (gitignored)
- .env.example provides template without secrets
- Fallback detection: Anthropic > OpenAI
- No hardcoded API keys in source (validated through grep)

### Environment Variable Exposure

- Test environment uses test-key-mock-* pattern
- Production keys must be set via .env before runtime
- Warning emitted if no API keys found at startup

---

## 12. Summary

### Dependency Health

| Category | Status | Notes |
|----------|--------|-------|
| API Keys | Present | All configured in .env |
| Python Version | Compatible | 3.14.0 meets 3.10+ requirement |
| Core Dependencies | Installed | All in requirements.txt |
| Optional Dependencies | Conditional | Some not in requirements.txt |
| Configuration Files | Present | All config files found |
| Import Structure | Healthy | No circular dependencies |
| Tests | Functional | Conftest and mocking in place |
| External Services | Configured | Multiple AI providers available |

### Recommendations

1. Add missing dependencies (FastAPI, optional doc generators) to requirements.txt
2. Add explicit Python version constraint to pyproject.toml
3. Implement API key encryption at rest for artifacts
4. Add upper bounds to major dependencies (agency-swarm)
5. Document optional dependencies separately
6. Consider moving TaskMaster config to environment variables for flexibility
