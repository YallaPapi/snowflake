# Data Models & Schemas Report
**Generated**: 2026-02-07 15:30 UTC
**Analyst**: Data Models Explorer Agent
**Scope**: All data structures and data flow analysis

---

## Executive Summary

The Snowflake project contains **66+ Python data model classes** organized across multiple layers: Pydantic models (24), dataclasses (18), SQLAlchemy ORM models (8), enumerations (15+), and API models (12). The system implements comprehensive validation, persistence, quality assessment, and export capabilities.

---

## 1. CORE SCENE CARD MODELS (`src/scene_engine/models.py`)

### Enumerations
- **SceneType**: PROACTIVE, REACTIVE
- **ViewpointType**: FIRST, SECOND, THIRD, THIRD_OBJECTIVE, HEAD_HOPPING, OMNISCIENT
- **TenseType**: PAST, PRESENT, FUTURE
- **OutcomeType**: SETBACK, VICTORY, MIXED
- **CompressionType**: FULL, SUMMARIZED, SKIP

### Key Models
| Model | Type | Fields | Purpose |
|-------|------|--------|---------|
| GoalCriteria | Pydantic | text + 5 bool criteria | Proactive scene goal validation |
| ConflictObstacle | Pydantic | try_number, obstacle | Escalating obstacles |
| Outcome | Pydantic | type, rationale | Scene outcome |
| DilemmaOption | Pydantic | option, why_bad | Reactive dilemma choices |
| ProactiveScene | Pydantic | goal, conflict_obstacles[], outcome | Goal→Conflict→Setback |
| ReactiveScene | Pydantic | reaction, dilemma_options[], decision, next_goal_stub, compression | Reaction→Dilemma→Decision |
| **SceneCard** | Pydantic | scene_type, pov, viewpoint, tense, scene_crucible, place, time, proactive/reactive, STC fields | **MAIN DATA STRUCTURE** |
| ValidationResult | Pydantic | is_valid, errors[], warnings[] | Validation output |

### SceneCard Save the Cat Fields
- `emotional_polarity`: "+" or "-"
- `emotional_start` / `emotional_end`: Must differ
- `conflict_parties`, `conflict_winner`, `storyline` (A/B/C)

---

## 2. CHAIN LINKING MODELS (`src/scene_engine/chaining/models.py`)

- **ChainLinkType** (7 types): SETBACK_TO_REACTIVE, DECISION_TO_PROACTIVE, VICTORY_TO_PROACTIVE, MIXED variants, SEQUEL_BRIDGE, CHAPTER_BREAK
- **TransitionType** (6): IMMEDIATE, COMPRESSED, SEQUEL, TIME_CUT, POV_SHIFT, LOCATION_SHIFT
- **ChainStrength**: STRONG, MODERATE, WEAK, BROKEN
- **ChainLink** (Pydantic): chain_id, chain_type, source/target scenes, trigger/bridging content, metadata
- **ChainSequence** (Pydantic): scenes[], chain_links[], quality metrics, word counts

---

## 3. GENERATION MODELS (`src/scene_engine/generation/`)

- **GenerationMode**: CREATIVE, STRUCTURED, ADAPTIVE, TEMPLATE_BASED
- **AIModel**: CLAUDE, GPT4, GEMINI, LOCAL
- **GenerationContext** (dataclass): project info, previous scenes, character profiles, story outline
- **GenerationRequest** (dataclass): scene_type, pov, purpose, context, word_count_target, creativity_level
- **GenerationResponse** (dataclass): scene_card, prose, compliance/coherence/consistency scores, validation results
- **GenerationWorkflowRequest/Response**: Full workflow orchestration with chain linking support

---

## 4. TEMPLATE MODELS (`src/scene_engine/generation/templates.py`)

- **TemplateType** (10): OPENING, CONTINUATION, CLIMAX, RESOLUTION, TRANSITION, FLASHBACK, DIALOGUE_HEAVY, ACTION_SEQUENCE, INTROSPECTIVE, REVEAL
- **GenreTemplate** (10): LITERARY through ADVENTURE
- **PromptTemplate** (dataclass): system/structure/style/ending prompts, word count, complexity, usage tracking
- **SceneTemplate** (dataclass): opening/development/climax/resolution patterns, POV/tense recommendations, genre considerations

---

## 5. VALIDATION MODELS (`src/scene_engine/validation/`)

- **ValidationSeverity**: ERROR, WARNING, INFO
- **ValidationStageType**: STRUCTURAL, SEMANTIC, BUSINESS_RULE, QUALITY
- **ValidationReport**: scene_id, is_valid, errors[], warnings[], rule_citations[], metrics, recommendations
- **PipelineResult**: overall_success, stage_results[], durations

---

## 6. QUALITY ASSESSMENT MODELS

- **QualityDimension** (6): READABILITY, COHERENCE, STRUCTURE, ENGAGEMENT, TECHNICAL, SNOWFLAKE_COMPLIANCE
- **QualityScore**: dimension, score (0-1), confidence, factors, recommendations
- **QualityReport**: Individual scores for all 6 dimensions, overall quality, content statistics

---

## 7. TRIAGE MODELS

- **TriageDecision**: YES, NO, MAYBE
- **TriageRequest**: scene_card, prose, criteria, auto_redesign settings
- **TriageResponse**: decision, classification_score, quality_metrics, redesign results, final scene/prose

---

## 8. DRAFTING MODELS

- **DraftingStatus**: SUCCESS, FAILED, PARTIAL
- **DraftingRequest**: scene_card, POV/tense overrides, exposition budget, word count target
- **DraftingResponse**: prose_content, structure_adherence, POV/tense consistency, exposition usage, quality metrics

---

## 9. API REQUEST/RESPONSE MODELS (`src/api/`)

| Model | Type | Key Fields |
|-------|------|-----------|
| NovelBrief | Request | project_name, brief, target_words, model_provider |
| StepExecutionRequest | Request | project_id, step_number, additional_params |
| ProjectStatus | Response | project_id, current_step, steps_completed, is_complete, word_count |
| ExportRequest | Request | project_id, formats[] |
| ScenePlanRequest | Request | scene_type, scene_crucible, pov_character, pov, tense |
| SceneDraftRequest | Request | scene_card, style_preferences, target_word_count |
| SceneTriageRequest | Request | scene_card, prose_content, triage_options |

---

## 10. DATABASE MODELS (`src/scene_engine/persistence/models.py`)

SQLAlchemy ORM with SQLite:

| Model | Key Fields | Relationships |
|-------|-----------|---------------|
| Project | project_id, title, genre, target_word_count, status | scene_cards, chain_links, sequences, characters |
| Character | name, role, goals (JSON), conflicts (JSON), arc_phase | project |
| SceneCardDB | scene_id, scene_type, pov, proactive_data (JSON), reactive_data (JSON), quality_score | project, prose_content |
| ProseContent | content, word_count, readability_score, sentiment_score, version | scene_card |
| ChainLinkDB | chain_id, chain_type, source/target scene IDs, chain_strength, validation_score | project |
| SceneSequenceDB | sequence_id, scene_ids (JSON), narrative_cohesion, pacing_score | project |
| ValidationLog | target_type, target_id, is_valid, errors (JSON), warnings (JSON) | project |
| BackupRecord | backup_id, backup_type, backup_path, checksum, status | project |

---

## 11. OBSERVABILITY MODELS

- **PerformanceMetrics** (dataclass): timestamp, cpu_percent, memory_mb, disk_usage_mb, step_duration, tokens_processed, api_calls, error_count
- **HealthStatus** (dataclass): ai_provider_healthy, disk_space_healthy, memory_healthy, pipeline_active, last_error

---

## 12. PIPELINE DATA FLOW

```
Step 0 (brief→concept) → Step 1 (→logline) → Step 2 (→5 sentences+moral)
  → Step 3 (→characters) → Step 4 (→5 paragraphs) → Step 5 (→character synopses)
  → Step 6 (→long synopsis) → Step 7 (→character bibles) → Step 8 (→scene list)
  → Step 9 (→scene briefs) → Step 10 (→manuscript)
```

### Scene Engine Flow
```
Planning → Generation → Drafting → Quality Assessment → Triage → Chain Linking → Persistence → Export
```

---

## 13. FILE FORMATS

| File | Format | Location |
|------|--------|----------|
| project.json | JSON | artifacts/{project_id}/ |
| status.json | JSON | artifacts/{project_id}/ |
| events.log | JSONL | artifacts/{project_id}/ |
| metrics.json | JSON | artifacts/{project_id}/ |
| step_N_*.json | JSON | artifacts/{project_id}/ |
| step_N_*.txt/.md | Text | artifacts/{project_id}/ |
| scene_engine.db | SQLite | Project root |

---

## 14. SCHEMA INCONSISTENCIES

1. **Pydantic v2 Compatibility**: Mixed Config class vs ConfigDict usage
2. **JSON Serialization**: Custom encoders needed for datetime/Enum in ChainLink
3. **Database-Pydantic Mismatch**: ProactiveScene/ReactiveScene stored as JSON blobs, not normalized
4. **POVType/ViewpointType**: Multiple definitions across drafting vs models modules
5. **Optional Field Defaults**: Some dataclass optional fields lack proper initialization

---

## 15. SUMMARY TABLE

| Layer | Count | Pattern | Key Files |
|-------|-------|---------|-----------|
| Pydantic Models | 24 | BaseModel + validators | models.py, chaining/models.py |
| Dataclasses | 18 | Config + Result objects | generation/, validation/, quality/ |
| SQLAlchemy ORM | 8 | Base + relationships | persistence/models.py |
| Enumerations | 15+ | Field constraints | Distributed across modules |
| API Models | 12 | FastAPI req/res | api/main.py, scene_engine_endpoints.py |
| **TOTAL** | **66+** | **Mixed** | **Distributed** |
