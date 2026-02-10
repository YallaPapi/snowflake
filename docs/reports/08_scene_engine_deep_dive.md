# Scene Engine Deep Dive Report
**Generated**: 2026-02-07 14:30 UTC
**Analyst**: Scene Engine Explorer Agent
**Scope**: Complete scene engine module analysis

---

## Executive Summary

The Scene Engine is a comprehensive 12-subsystem module with 72 Python files implementing Randy Ingermanson's Scene Card specification. It provides AI-powered scene generation, validation, persistence, quality assessment, triage, export, and chaining capabilities.

---

## 1. MODULE STRUCTURE

```
src/scene_engine/
├── models.py                 # Core data models (SceneCard, proactive/reactive)
├── schema.py                 # JSON schema generation
├── validators.py             # Runtime validation rules
├── __init__.py              # Public API exports
│
├── generation/              # AI-powered scene generation
│   ├── engine.py            # Core generation logic with AI model integration
│   ├── service.py           # High-level workflow orchestration
│   ├── templates.py         # Scene and prompt templates
│   ├── refinement.py        # Post-generation content improvement
│   └── tests/
│
├── validation/              # Scene validation and reporting
│   ├── service.py           # Validation orchestration
│   ├── pipeline.py          # Validation pipeline definition
│   └── tests/
│
├── persistence/             # Database storage and retrieval
│   ├── service.py           # High-level persistence API
│   ├── models.py            # SQLAlchemy database models
│   ├── crud.py              # CRUD operations
│   ├── query.py             # Advanced querying
│   ├── backup.py            # Backup/recovery
│   └── tests/
│
├── chaining/                # Scene-to-scene linking
│   ├── models.py            # Chain link data structures
│   ├── generator.py         # Chain generation logic
│   ├── service.py           # Chaining service
│   ├── transitions.py       # Transition rules
│   ├── validator.py         # Chain validation
│   ├── serialization.py     # Chain serialization
│   └── tests/
│
├── drafting/                # Scene card to prose conversion
│   ├── service.py           # Main drafting service
│   ├── prose_generators.py  # Proactive/reactive prose generators
│   ├── pov_handler.py       # POV and tense management
│   ├── exposition_tracker.py # Exposition budget tracking
│   └── tests/
│
├── quality/                 # Quality assessment
│   ├── service.py           # Quality scoring system
│   ├── coherence.py         # Narrative coherence analysis
│   ├── readability.py       # Readability metrics
│   └── engine.py            # Quality assessment engine
│
├── triage/                  # Scene YES/NO/MAYBE classification
│   ├── service.py           # Triage orchestration
│   ├── classifier.py        # Classification logic
│   ├── corrections.py       # Auto-correction
│   ├── emotion_targeting.py # Emotional targeting
│   ├── redesign.py          # Redesign pipeline
│   └── tests/
│
├── planning/                # Scene planning interface
│   ├── service.py           # Planning service interface
│   ├── planner.py           # Planning logic
│   └── prompts.py           # Planning prompts
│
├── export/                  # Multi-format export
│   ├── service.py           # Export orchestration
│   ├── formats.py           # Format handlers
│   └── templates.py         # Export templates
│
├── integration/             # Master integration layer
│   ├── master_service.py    # Master integration service
│   └── __init__.py
│
└── examples/                # Example usage
    ├── example_scenes.py
    ├── ingermanson_reference_scenes.py
    ├── prose_generation.py
    ├── scene_chaining.py
    └── validate_examples.py
```

**Total: 72 Python files across 12 subsystems**

---

## 2. DATA MODELS (models.py)

### Enumerations
- **SceneType**: PROACTIVE, REACTIVE
- **ViewpointType**: FIRST, SECOND, THIRD, THIRD_OBJECTIVE, HEAD_HOPPING, OMNISCIENT
- **TenseType**: PAST, PRESENT, FUTURE
- **OutcomeType**: SETBACK, VICTORY, MIXED
- **CompressionType**: FULL, SUMMARIZED, SKIP

### Core Structures

**GoalCriteria** (Proactive scenes — 5 mandatory criteria):
1. `fits_time`: Achievable in available time
2. `possible`: Actually achievable
3. `difficult`: Presents genuine challenge
4. `fits_pov`: Matches character capabilities/values
5. `concrete_objective`: Measurable and specific

**ProactiveScene**: goal (GoalCriteria) → conflict_obstacles (List[ConflictObstacle], escalating) → outcome (Outcome)

**ReactiveScene**: reaction (10+ chars) → dilemma_options (List[DilemmaOption], min 2) → decision (10+ chars) → next_goal_stub → compression

**SceneCard** (main model):
- Required: scene_type, pov, viewpoint, tense, scene_crucible (10+ chars), place, time, exposition_used, chain_link
- Save the Cat: emotional_polarity (+/-), emotional_start, emotional_end, conflict_parties, conflict_winner, storyline (A/B/C)
- Metadata: id, created_at, updated_at, version

---

## 3. GENERATION SERVICE

### engine.py: SceneGenerationEngine
- AI-powered generation with Snowflake compliance
- Generation modes: CREATIVE, STRUCTURED, ADAPTIVE, TEMPLATE_BASED
- AI models: CLAUDE (default), GPT4, GEMINI, LOCAL
- Quality metrics: snowflake_compliance_score, narrative_coherence, character_consistency

### service.py: SceneGenerationService
- Complete workflow orchestration: context → template → generation → refinement → validation → persistence → chaining
- Batch processing support
- Regeneration with user feedback

### templates.py: TemplateManager
- 5 built-in scene templates: Proactive Opening, Reactive Continuation, Action Sequence, Dialogue-Heavy, Introspective
- 3 genre-specific prompts: Mystery, Romance, Fantasy
- Template selection by scene type, genre, complexity
- Usage tracking and rating system

### refinement.py: ContentRefiner
- Issue detection: Structure, Style, Consistency, Dialogue, Pacing, Snowflake compliance
- RefinementSuggestion with confidence scores
- Automatic and manual refinement modes

---

## 4. VALIDATION SERVICE

7 validation rules from PRD Section E1:
1. **CrucibleNowCheck**: Immediate "now" focus, not backstory
2. **GoalFiveCheck**: All 5 criteria pass
3. **ConflictEscalationCheck**: Obstacles escalate
4. **OutcomePolarityCheck**: Rationale for outcome
5. **ReactiveTriadCheck**: Complete R-D-D with goal stub
6. **CompressionIntegrityCheck**: Compressed scenes still complete
7. **ExpositionBudgetCheck**: "Now or never" principle

---

## 5. PERSISTENCE LAYER

### Database Models (SQLAlchemy ORM)
- Project, SceneCardDB, ProseContent, ChainLinkDB, Character, SceneSequenceDB, ValidationLog, BackupRecord

### Features
- ProseAnalyzer: Word count, readability, sentiment, keywords, dialogue ratio
- ProseVersionManager: Version control and history
- Advanced querying with SceneCardQueryBuilder, ChainLinkQueryBuilder, AggregationQueryBuilder
- Backup: FULL, INCREMENTAL, DIFFERENTIAL; Formats: JSON, SQLite, Gzip

---

## 6. CHAINING SYSTEM

### ChainLinkType (7 types)
1. SETBACK_TO_REACTIVE
2. DECISION_TO_PROACTIVE
3. VICTORY_TO_PROACTIVE
4. MIXED_TO_REACTIVE/PROACTIVE
5. SEQUEL_BRIDGE
6. CHAPTER_BREAK

### ChainStrength: STRONG, MODERATE, WEAK, BROKEN
### TransitionType: IMMEDIATE, COMPRESSED, SEQUEL, TIME_CUT, POV_SHIFT, LOCATION_SHIFT

---

## 7. DRAFTING SYSTEM

- ProactiveProseGenerator: Goal-conflict-setback prose
- ReactiveProseGenerator: Reaction-dilemma-decision prose
- POV consistency validation
- Tense consistency checking
- Exposition budget enforcement ("now or never")

---

## 8. QUALITY ASSESSMENT

6 quality dimensions:
1. **Readability**: Flesch-Kincaid, sentence variety, vocabulary
2. **Coherence**: Narrative flow, cause-effect
3. **Structure**: Scene structure adherence, pacing
4. **Engagement**: Tension, emotional impact
5. **Technical**: Grammar, spelling, formatting
6. **Snowflake Compliance**: Method principles adherence

---

## 9. TRIAGE SYSTEM

- **YES**: Scene ready for production
- **NO**: Scene rejected/replaced
- **MAYBE**: Needs redesign

Redesign Pipeline: type correction → part rewriting → compression → emotion targeting → re-validation → re-triage (recursive)

---

## 10. EXPORT SYSTEM

Supported formats: DOCX, EPUB, PDF, HTML, MARKDOWN, TEXT, JSON, CSV
Export scopes: SINGLE_SCENE, CHAPTER, PROJECT, MANUSCRIPT, SCENE_LIST

---

## 11. INTEGRATION LAYER (master_service.py)

- EventSystem: 10 event types, pub/sub pattern, event queue, history tracking
- EngineConfiguration: Centralized config (DB URL, AI model, feature flags, performance tuning)
- Workflow System: Multi-step with dependencies and retry logic

---

## 12. CURRENT STATUS

### Implemented
- All core models and enumerations
- Scene card validation system (7 validators)
- Generation engine with AI model interface
- Template system (5 scene + 3 genre)
- Persistence layer (SQLAlchemy, CRUD, queries, backup)
- Chain linking system
- Content refinement system
- Quality assessment framework
- Triage classification
- Export service (multi-format)
- Integration/master service
- Event-driven architecture

### Partially Implemented
- AI model integration (placeholders for Claude/GPT4/Gemini — not real API calls)
- Drafting service (structure defined, prose generation needs completion)
- Planning service (interface defined, implementation pending)

### Not Fully Tested
- Generation tests (fixtures defined, not all test cases)
- End-to-end workflow integration tests
- Export format generation
- Chaining validation rules

---

## 13. CONNECTION TO PIPELINE

```
Snowflake Method (Steps 0-10) → Scene Engine → Screenplay Engine → Shot Engine → Video Engine
```

- **Upstream**: Receives story/character data from pipeline Steps 7-9
- **Downstream**: Outputs prose for screenplay/visual production
- **Horizontal**: Integrates Save the Cat emotional polarity in SceneCard model

---

## 14. CRITICAL OBSERVATIONS

### Strengths
1. Comprehensive data model closely following Snowflake Method spec
2. Extensive validation system with detailed error reporting
3. Modular architecture with clear separation of concerns
4. Template-based approach enables customization
5. Multi-format export capability
6. Event-driven async operations
7. Quality assessment across 6 dimensions

### Weaknesses
1. AI model integration incomplete (mocked responses)
2. Prose generation partially implemented
3. Some services have placeholder implementations
4. Limited error recovery mechanisms
5. Performance optimization needed for batch operations

### Dependencies
- Pydantic (data validation)
- SQLAlchemy (ORM)
- Python async/await (asyncio)
- Optional: python-docx, ebooklib, reportlab (export)
