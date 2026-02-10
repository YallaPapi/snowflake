# Technical Debt Report
**Generated**: 2026-02-07 19:00 UTC
**Analyst**: Evolution Tracker Agent
**Scope**: Technical debt and code evolution analysis

---

## Executive Summary

The Snowflake project -- an AI-powered novel generation engine implementing Randy Ingermanson 11-step Snowflake Method -- carries **significant technical debt** across multiple dimensions. The codebase grew explosively over a 4-day development sprint (2025-08-18 to 2025-08-21, 15 commits totaling ~120,000 lines), resulting in large amounts of scaffolding code, duplicated implementations, 79 orphaned root-level Python scripts, 212 tracked .pyc files, and stub-only subsystems that were never completed. The ratio of production source code (~44,000 lines in src/) to throwaway root-level scripts (~13,000 lines) is approximately 3.4:1, which is abnormally low.

**Total Debt Score: 72/100** (higher = more debt)
**Trend: Stagnant** (no commits since August 2025; debt is accumulating through bitrot)
**Estimated Cleanup Time: 15-20 developer-days**

---

## Debt Breakdown

| Category       | Score | Items     | Priority   |
|----------------|-------|-----------|------------|
| Design         | 16/20 | 12 issues | High       |
| Code           | 15/20 | 18 issues | High       |
| Test           | 14/20 | 9 issues  | High       |
| Docs           | 10/20 | 6 issues  | Low        |
| Dependencies   | 17/20 | 8 issues  | Critical   |

---

## 1. Code Churn Hotspots

### Top Changed Files (All Time, by Commit Count)

| File | Commits | Lines Churned | Analysis |
|------|---------|---------------|----------|
| src/pipeline/steps/step_2_one_paragraph_summary.py | 6 | ~400 | Rewritten multiple times across sprints |
| src/pipeline/steps/step_1_one_sentence_summary.py | 5 | ~350 | Frequent prompt/validator adjustments |
| src/pipeline/steps/step_0_first_things_first.py | 5 | ~300 | Input handling changed repeatedly |
| src/pipeline/steps/step_10_draft_writer.py | 5 | ~250 | Eventually superseded by step_10_first_draft.py |
| src/pipeline/orchestrator.py | 5 | ~650 | Core orchestration logic reworked |
| src/ai/generator.py | 5 | ~560 | Provider detection and retry logic evolved |
| requirements.txt | 5 | ~50 | Dependency additions each commit |
| src/pipeline/steps/step_3_character_summaries.py | 4 | 1020 | One of the most churned by line count |
| src/pipeline/steps/step_4_one_page_synopsis.py | 4 | ~500 | Synopsis expansion logic |
| src/pipeline/steps/step_6_long_synopsis.py | 4 | ~450 | Long-form generation |

### Highest Lines-Churned Files (Source Only)

| File | Total Lines Added+Removed | Current Size |
|------|---------------------------|--------------|
| src/scene_engine/persistence/tests/test_persistence_complete.py | 1287 | ~640 lines |
| src/scene_engine/persistence/backup.py | 1138 | ~560 lines |
| src/pipeline/steps/step_14_panel_composition.py | 1090 | ~545 lines |
| src/scene_engine/chaining/tests/test_chain_system.py | 1024 | ~510 lines |
| src/pipeline/steps/step_3_character_summaries.py | 1020 | ~510 lines |
| src/scene_engine/quality/service.py | 1015 | ~508 lines |

**Analysis**: The pipeline steps (steps 0-3 especially) and the orchestrator are the most-touched files, indicating design instability. The scene engine test files have very high churn-to-size ratios, suggesting tests were rewritten rather than incrementally improved. Files with 5+ commits in a 15-commit history means they were touched in every third commit -- a sign of unclear requirements or premature implementation.

---

## 2. TODO / FIXME / HACK Comments

### In Production Source (src/)

| File | Line | Type | Comment |
|------|------|------|---------|
| src/scene_engine/generation/engine.py | 205 | TODO | Implement actual Claude API integration |
| src/scene_engine/generation/engine.py | 245 | TODO | Implement actual GPT-4 API integration |

**Total: 2 TODOs in src/, 0 FIXME, 0 HACK**

### In Root-Level Scripts

The 79 root-level Python scripts were not systematically audited for TODOs since they are throwaway code, but manual sampling found several inline comments marking incomplete logic.

### Analysis

The low TODO count is misleading. The codebase does not use TODO markers to track incomplete work. Instead, incomplete features are left as stub implementations with pass bodies or hardcoded placeholder returns (see Section 7: Incomplete Features). A codebase-wide convention for marking technical debt with TODO/FIXME comments would significantly improve visibility.

---

## 3. Deprecated Patterns

### Stale Model References

| File | Location | Stale Reference | Current Model |
|------|----------|-----------------|---------------|
| src/ai/model_selector.py | MODEL_REGISTRY | claude-3-haiku-20240229 | claude-3-5-haiku-20241022 |
| src/ai/model_selector.py | MODEL_REGISTRY | claude-3-5-sonnet-20240620 | claude-3-5-sonnet-20241022 |
| src/scene_engine/generation/engine.py | _generate_claude() | claude-3-sonnet-20240229 | claude-3-5-sonnet-20241022 |
| src/scene_engine/generation/engine.py | _generate_gpt4() | gpt-4 | gpt-4o or gpt-4-turbo |

### Dead Module Pairs (Superseded Files Still Present)

| Dead File | Active Replacement | Status |
|-----------|--------------------|--------|
| src/pipeline/steps/step_10_draft_writer.py | src/pipeline/steps/step_10_first_draft.py | Orphaned, never imported |
| src/pipeline/steps/step_9_scene_briefs.py | src/pipeline/steps/step_9_scene_briefs_v2.py | Imported as alias in orchestrator |
| src/pipeline/progress_tracker.py | src/ui/progress_tracker.py | Both exist, unclear which is canonical |

### Abandoned Subsystems

| Subsystem | Location | Status |
|-----------|----------|--------|
| Novel Agency (agency-swarm) | src/novel_agency/ | Fully abandoned, never functional |
| Graphic Novel Pipeline (Steps 11-15) | src/pipeline/steps/step_11_* through step_15_* | Scaffolded but untested |

### sys.path Manipulation (Anti-Pattern)

| File | Line | Code |
|------|------|------|
| src/pipeline/orchestrator.py | 12 | sys.path.insert(0, str(Path(__file__).resolve().parents[2])) |
| src/api/main.py | ~10 | sys.path.insert(0, ...) |
| src/observability/server.py | ~8 | sys.path.insert(0, ...) |
| src/scene_engine/integration/master_service.py | ~5 | sys.path.insert(0, ...) |
| tests/integration/test_pipeline_steps_0_to_3.py | ~5 | sys.path.insert(0, ...) |
| tests/steps/test_step_0.py | ~5 | sys.path.insert(0, ...) |

**Total: 6 sys.path hacks** -- all compensating for the lack of proper Python packaging (no setup.py, no pyproject.toml [project] section, no installable package).

---

## 4. Version Conflicts and Dependency Issues

### requirements.txt Analysis

| Package | Pinned Version | Issue | Severity |
|---------|---------------|-------|----------|
| openai | >=1.99.9,<2.0.0 | **Version 1.99.9 does not exist**. Latest openai is ~1.58.x. This pin will fail on every install. | **Critical** |
| agency-swarm | >=0.7.0 | Novel Agency subsystem is abandoned. Dead dependency. | Medium |
| flask / flask-cors | >=2.3.0 / >=4.0.0 | API uses FastAPI, not Flask. These are unused. | Medium |
| fastapi | (missing) | API server at src/api/main.py imports fastapi but it is not in requirements.txt | **Critical** |
| uvicorn | (missing) | Required to run the FastAPI server, not in requirements.txt | **Critical** |
| httpx | >=0.27.0,<0.28.0 | Tight upper bound may conflict with other packages | Low |
| psutil | >=5.9.0 | Only used in root-level scripts, not in src/ | Low |

### Missing requirements-test.txt or Test Dependencies

There is no requirements-test.txt or [project.optional-dependencies] section. Test dependencies (pytest, pytest-asyncio, pytest-mock) are not documented anywhere.

### pyproject.toml Incompleteness

The pyproject.toml only contains pytest configuration:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests", "src"]
```

Missing sections: [project], [build-system], [tool.setuptools]. The project is not installable as a Python package.

---

## 5. Configuration Debt

### Hardcoded Values

| File | Issue |
|------|-------|
| src/pipeline/error_recovery.py | Max retries hardcoded to 5, backoff multiplier hardcoded |
| src/ai/model_selector.py | All 11 pipeline steps mapped to fast tier -- no differentiation |
| src/ai/bulletproof_generator.py | Circuit breaker thresholds hardcoded (failure_threshold=3, reset_timeout=60) |
| src/scene_engine/generation/engine.py | Temperature, max_tokens hardcoded per model |
| src/pipeline/orchestrator.py | Output directory hardcoded as artifacts |

### Missing .gitignore Entries

Current .gitignore is 31 lines and missing critical patterns:

| Pattern | Why Needed |
|---------|------------|
| *.pyc / __pycache__/ | 212 .pyc files are currently tracked in git |
| artifacts/ | Generated novel manuscripts should not be tracked |
| *.pdf | Two PDFs are untracked in root |
| venv/ / .venv/ | Standard Python virtual environment |
| .pytest_cache/ | Pytest cache directory |
| pdf_pages/ / temp_pages/ | Temporary processing directories |
| nul | Windows artifact from > nul redirect |

### No Logging Framework

The codebase uses **165 print() calls** across src/ with zero usage of the Python logging module. There is no log level control, no log formatting, no file logging, and no structured logging. The observability subsystem (src/observability/) implements custom event tracking but does not integrate with Python standard logging.

### Environment Variable Handling

Environment variables are accessed via os.environ.get() and os.getenv() throughout the codebase with no centralized configuration management. There is no .env.example file documenting required variables. The python-dotenv library is in requirements but .env loading is scattered across multiple entry points.

---

## 6. Refactoring Opportunities

### [DEBT-001] Orchestrator Step Execution Duplication
- **Location**: src/pipeline/orchestrator.py (lines 122-359)
- **Type**: Design Debt
- **Severity**: High
- **Description**: 11 nearly identical execute_step_N() methods, each following the same pattern: load prompt, call AI, validate, save artifact. Only the step class and prompt template vary.
- **Estimated Effort**: 1 developer-day
- **Recommendation**: Replace with a single execute_step(step_number) method using a step registry/factory pattern.

### [DEBT-002] Duplicate generate_scene_prose Method
- **Location**: src/ai/generator.py (lines 292 and 440)
- **Type**: Code Debt
- **Severity**: Medium
- **Description**: The generate_scene_prose method appears twice in the same file with slightly different implementations.
- **Estimated Effort**: 0.5 developer-days
- **Recommendation**: Remove the duplicate, keep the more complete version, add tests.

### [DEBT-003] Scene Engine AI Stubs (Placeholder Code)
- **Location**: src/scene_engine/generation/engine.py (lines 180-380)
- **Type**: Design Debt
- **Severity**: High
- **Description**: Four AI model methods (_generate_claude, _generate_gpt4, _generate_gemini, _generate_local) all return hardcoded placeholder JSON strings. This is ~200 lines of dead code that gives the false impression of multi-model support.
- **Estimated Effort**: 2 developer-days (integrate with src/ai/generator.py) or 0.5 days (delete stubs)
- **Recommendation**: Either integrate with the existing AI generator in src/ai/ or delete the stubs and document the gap.

### [DEBT-004] Root-Level Script Cleanup
- **Location**: Project root (79 .py files, 27 .md files)
- **Type**: Code Debt
- **Severity**: Medium
- **Description**: 79 Python scripts (~12,911 lines) in the project root. These are one-off test scripts, smoke tests, and experiments that were never moved to proper locations. They clutter the project and confuse navigation.
- **Estimated Effort**: 1 developer-day
- **Recommendation**: Archive to scripts/legacy/ or delete entirely. Move any still-useful scripts to scripts/ or tests/.

### [DEBT-005] Tracked .pyc Files
- **Location**: Throughout __pycache__/ directories
- **Type**: Code Debt
- **Severity**: Medium
- **Description**: 212 compiled Python bytecode files are tracked in git. These are build artifacts that should never be committed.
- **Estimated Effort**: 0.25 developer-days
- **Recommendation**: Add __pycache__/ and *.pyc to .gitignore, then git rm -r --cached **/__pycache__/.

### [DEBT-006] Broad Exception Handling
- **Location**: Throughout src/ (141 instances of except Exception as e)
- **Type**: Code Debt
- **Severity**: Medium
- **Description**: 141 catch-all exception handlers in production code, plus 21+ bare except: clauses in root scripts. These suppress errors, making debugging extremely difficult.
- **Estimated Effort**: 3 developer-days
- **Recommendation**: Replace with specific exception types. At minimum, log the exception before re-raising or handling.

### [DEBT-007] Missing Python Packaging
- **Location**: pyproject.toml (incomplete), no setup.py
- **Type**: Design Debt
- **Severity**: High
- **Description**: The project is not installable as a Python package. This forces sys.path hacks (6 instances), prevents proper imports, and makes testing harder.
- **Estimated Effort**: 0.5 developer-days
- **Recommendation**: Add [project] and [build-system] sections to pyproject.toml. Make src/ an installable package with pip install -e .

### [DEBT-008] Replace print() with Logging
- **Location**: 165 print() calls across src/
- **Type**: Code Debt
- **Severity**: Medium
- **Description**: No structured logging. All output goes through print() with no level control.
- **Estimated Effort**: 2 developer-days
- **Recommendation**: Introduce logging.getLogger(__name__) in each module. Replace print() calls with appropriate log levels.

---

## 7. Incomplete Features

### Scene Engine AI Integration (Stubbed)

The scene engine at src/scene_engine/ spans ~25,000 lines across 50+ files, but the core AI generation layer is entirely stubbed. The AIModelInterface class in src/scene_engine/generation/engine.py has four model-specific methods that all return hardcoded JSON:

```python
# src/scene_engine/generation/engine.py, line ~205
async def _generate_claude(self, prompt, config):
    # TODO: Implement actual Claude API integration
    return {"scene_text": "[Placeholder Claude scene]", ...}
```

The scene engine relies on src/ai/generator.py for actual AI calls, but the scene engine was also built with its own parallel AI abstraction that was never connected. This represents a significant design split.

### Graphic Novel Extension (Steps 11-15)

Five additional pipeline steps were scaffolded for graphic novel / comic script generation:
- step_11_script_conversion.py
- step_12_visual_directions.py
- step_13_storyboard.py
- step_14_panel_composition.py
- step_15_final_production.py

These files exist and contain class definitions, but they have never been tested, are not wired into the orchestrator, and are not referenced by any test. They were added in two commits on the graphic-novel branch and merged but never activated.

### Novel Agency System (Abandoned)

The src/novel_agency/ directory contains an agent-based novel generation system built on the agency-swarm library. This includes:
- Agent definitions (editor, researcher, writer)
- Agency orchestration
- Custom tools

This subsystem is completely abandoned. It is never imported by any active code, has no tests, and the agency-swarm dependency exists only for this dead code.

### Observability Dashboard (Partial)

The src/observability/ subsystem implements event emission and a Flask-based server, but:
- The Flask dependency conflicts with the FastAPI server in src/api/
- Event persistence is in-memory only (lost on restart)
- No integration with the pipeline orchestrator
- The dashboard frontend is minimal HTML served by Flask

### Error Recovery Regeneration (Unimplemented)

The regenerate_downstream() method in src/pipeline/orchestrator.py is declared but only returns a list of step names. It does not actually re-execute downstream steps when an upstream step is modified. This was likely planned for interactive editing workflows.

---

## 8. Git History Analysis

### Commit Timeline

| Date | Hash | Message | Lines Changed |
|------|------|---------|---------------|
| 2025-08-18 | c406396 | Initial commit: Snowflake Method novel generation engine | ~15,000 |
| 2025-08-18 | bcb5037 | Add comprehensive ZAD report documenting implementation | ~2,000 |
| 2025-08-18 | 43d01ce | Implement Steps 4-9, wire all steps 0-10 in orchestrator | ~8,000 |
| 2025-08-19 | 8a50f74 | Major pipeline improvements: E2E functionality, performance | ~5,000 |
| 2025-08-19 | 8a0c93d | Add comprehensive changelog documenting v2.0.0 | ~1,000 |
| 2025-08-19 | 1ea2500 | Implement bulletproof 100% reliability system | ~3,000 |
| 2025-08-19 | 5d822e1 | Configure GPT-5 as primary model | ~500 |
| 2025-08-20 | a1118a2 | Implement complete Scene Engine system | ~25,000 |
| 2025-08-20 | 6aeb33c | Fix misleading ZAD report | ~200 |
| 2025-08-20 | 27cc8ba | Scene Engine v2.1.0: Complete Randy Ingermanson | ~5,000 |
| 2025-08-21 | bfbde67 | Complete Scene Engine 100% functionality + observability | ~15,000 |
| 2025-08-21 | 9d123f3 | Revolutionary AI Publishing House: Agent-Based System | ~20,000 |
| 2025-08-21 | 4972664 | update | ~500 |
| 2025-08-21 | a0f21ce | COMPLETE: Fixed entire pipeline and generated 50k novel | ~8,000 |
| 2025-08-21 | ffdb224 | Add comprehensive progress update | ~2,000 |

Plus 2 later commits on a graphic-novel branch:

| Date | Hash | Message | Lines Changed |
|------|------|---------|---------------|
| Unknown | 253f2d6 | Add graphic novel extension: Steps 11-12 | ~3,000 |
| Unknown | 78cae02 | Add graphic novel generation pipeline (Steps 13-15) | ~5,000 |

### Pattern Analysis

1. **Mega-commits**: 5 commits add 15,000+ lines each. This indicates bulk code generation (likely AI-assisted) rather than incremental development.
2. **No feature branches**: All 15 main commits are on master. No pull requests, no code review.
3. **Hyperbolic commit messages**: Messages like Revolutionary AI Publishing House and 100% reliability system overstate the actual implementation state.
4. **4-day sprint**: The entire codebase was created in 4 days (Aug 18-21, 2025), then abandoned for 6 months.
5. **No bug fix commits**: Despite the --grep=fix search, only 2 commits mention fix and those are in the commit message rather than actual bugfix work. The bug fix frequency by file analysis returned only .pyc files, confirming that systematic bug fixing has never occurred.
6. **Stagnation**: No commits since August 2025. The codebase is experiencing bitrot (stale model references, impossible dependency pins, no security patches).

---

## 9. Documentation Debt

### Root-Level Documentation Clutter

27 markdown files exist in the project root, including:
- Multiple ZAD (Zero-Architecture Document) reports
- Changelogs
- Progress updates
- Implementation summaries
- How-to guides

These should be consolidated into docs/ with a clear structure.

### Missing Documentation

| Document | Status |
|----------|--------|
| README.md (setup guide) | Exists but references non-functional install steps |
| API documentation | None. FastAPI auto-docs exist but are not documented. |
| Architecture overview | Missing. No diagram of pipeline flow. |
| .env.example | Missing. Required environment variables undocumented. |
| Contributing guide | Missing |
| Test running guide | Missing |
| Deployment guide | Missing |

### Misleading Documentation

Several documents in the root make claims that do not match the code:
- 100% reliability (bulletproof_generator.py has never been stress-tested)
- Complete Scene Engine (AI integration is stubbed)
- 50,000 word novel generated (artifacts exist but pipeline reliability is unverified)
- ZAD reports describe features as complete that are actually stubs

### Inline Documentation

- Most classes have docstrings (positive)
- Method-level documentation is sparse
- No type hints in ~40% of function signatures
- No module-level documentation explaining subsystem boundaries

---

## 10. Dependency Freshness

### Current Dependencies (from requirements.txt)

| Package | Pinned | Latest (Feb 2026) | Age | Security Issues | Action |
|---------|--------|-------------------|-----|-----------------|--------|
| openai | >=1.99.9 | ~1.60.x | **Broken pin** | N/A (cannot install) | **Fix immediately** |
| anthropic | >=0.21.0 | ~0.40.x | ~12 months behind | Likely patched issues | Update |
| httpx | >=0.27.0,<0.28.0 | ~0.28.x | ~6 months behind | Check advisories | Relax upper bound |
| python-dotenv | >=1.0.0 | ~1.0.1 | Current | None known | OK |
| pydantic | >=2.0.0 | ~2.10.x | OK (floor only) | None known | OK |
| tqdm | >=4.60.0 | ~4.67.x | OK (floor only) | None known | OK |
| agency-swarm | >=0.7.0 | ~0.8.x | Dead dependency | Unknown | **Remove** |
| psutil | >=5.9.0 | ~5.9.8 | OK | None known | OK |
| flask | >=2.3.0 | ~3.1.x | ~1 year behind | Security patches | Remove or update |
| flask-cors | >=4.0.0 | ~4.0.1 | OK | None known | Remove (unused) |

### Missing Dependencies

| Package | Required By | Reason Missing |
|---------|-------------|----------------|
| fastapi | src/api/main.py | API server cannot start without it |
| uvicorn | src/api/main.py | ASGI server for FastAPI |
| pytest | tests/ | Test runner |
| pytest-asyncio | tests/ | Async test support |
| pytest-mock | tests/ | Mock fixtures |

### Dependency Graph Issues

1. **Flask vs FastAPI conflict**: The project includes both Flask (for observability) and FastAPI (for API). These serve the same purpose and should be consolidated.
2. **agency-swarm pull**: This package pulls in OpenAI, instructor, and other heavy dependencies for an abandoned subsystem.
3. **No dependency lockfile**: No requirements.lock, no poetry.lock, no pip-compile output. Builds are not reproducible.

---

## Refactoring Roadmap

### Phase 1: Critical Fixes (1-2 days)

- [ ] Fix openai>=1.99.9 pin to openai>=1.50.0,<2.0.0
- [ ] Add fastapi and uvicorn to requirements.txt
- [ ] Remove agency-swarm, flask, flask-cors from requirements.txt
- [ ] Add __pycache__/, *.pyc, artifacts/, *.pdf, nul to .gitignore
- [ ] Run git rm -r --cached on all tracked .pyc files
- [ ] Delete nul file artifact from root

### Phase 2: Quick Wins (2-3 days)

- [ ] Add [project] and [build-system] to pyproject.toml
- [ ] Remove all 6 sys.path hacks (replace with proper package install)
- [ ] Delete dead modules: step_10_draft_writer.py, step_9_scene_briefs.py (old), src/pipeline/progress_tracker.py
- [ ] Delete or archive 79 root-level Python scripts to scripts/legacy/
- [ ] Consolidate 27 root-level markdown files into docs/
- [ ] Create .env.example documenting required variables

### Phase 3: Medium Effort (1 week)

- [ ] Refactor orchestrator: replace 11 execute_step_N() methods with single parameterized method
- [ ] Remove duplicate generate_scene_prose method from generator.py
- [ ] Replace 165 print() calls with Python logging
- [ ] Narrow top-20 broadest exception handlers to specific types
- [ ] Update stale model references in model_selector.py and engine.py
- [ ] Add missing tests for AI generator module (currently 0% unit test coverage)

### Phase 4: Major Refactoring (2+ weeks)

- [ ] Delete or properly integrate scene engine AI stubs (~200 lines)
- [ ] Decide fate of graphic novel pipeline (Steps 11-15): complete or remove
- [ ] Remove abandoned Novel Agency subsystem entirely
- [ ] Consolidate Flask observability server into FastAPI
- [ ] Implement actual downstream regeneration in orchestrator
- [ ] Achieve 60%+ test coverage (currently ~33% of tests pass due to unmocked API calls)

---

## Recommendations

### Immediate (This Sprint)
1. **Fix the broken openai dependency pin** -- the project literally cannot be installed from requirements.txt
2. **Add fastapi/uvicorn to requirements** -- the API server cannot start
3. **Fix .gitignore and clean tracked .pyc files** -- 212 files polluting the repository

### Short-term (Next Month)
1. **Make the project installable** -- proper pyproject.toml eliminates sys.path hacks
2. **Clean root directory** -- move/delete 79 scripts and 27 markdown files
3. **Replace print() with logging** -- enable proper debugging and monitoring
4. **Refactor orchestrator** -- the 11 duplicate methods are the single largest design debt item

### Long-term (Next Quarter)
1. **Resolve the dual AI abstraction** -- scene engine stubs vs src/ai/generator.py
2. **Achieve test coverage** -- mock API calls, reach 60%+ coverage
3. **Decide on abandoned subsystems** -- Novel Agency and graphic novel pipeline need a keep-or-kill decision
4. **Consolidate web frameworks** -- pick FastAPI or Flask, not both

---

*Report generated from actual git history analysis, file enumeration, and code inspection of the Snowflake project at C:\\Users\\asus\\Desktop\\projects\\snowflake.*
