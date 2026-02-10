# Save the Cat Gap Analysis Report
**Generated**: 2026-02-07 03:03 UTC
**Analyst**: Save the Cat Gap Analysis Agent
**Scope**: Gap analysis for screenplay engine integration

---

## EXECUTIVE SUMMARY

**Zero Save the Cat (Blake Snyder) code exists** in the Snowflake or i2v projects. This is a greenfield opportunity. Two STC PDFs are available as reference. The Scene Engine already has partial STC-inspired fields (emotional polarity, conflict markers) but they are placeholder fields not populated by any pipeline step.

---

## 1. EXISTING STC RESOURCES

### PDFs Available
- `save the cat.pdf` (420 KB) — Scanned copy
- `Save-the-Cat-Goes-to-the-Movies-Blake-Snyder.pdf` — Full reference

### Partial Code References
`src/scene_engine/models.py` (lines 232-250) — SceneCard has STC-inspired fields:
- `emotional_polarity`: "+" or "-" (placeholder, not populated)
- `emotional_start` / `emotional_end`: Emotional state tracking
- `conflict_parties`: Who vs whom
- `conflict_winner`: Who wins the conflict
- `storyline`: A/B/C (main/theme/subplot)

**Status**: Fields exist but are NOT populated by any pipeline step.

---

## 2. SNOWFLAKE OUTPUT → STC INPUT MAPPING

```
Snowflake Step 0 (Category)        → STC Step 2: Genre confirmation
Snowflake Step 1 (Logline)         → STC Step 1: Logline (exact match)
Snowflake Step 3 (Characters)      → STC Step 3: Hero (protagonist + wound/goal)
Snowflake Step 8 (Scene List, 60+) → STC Step 5: Board (filter to 40 key scenes)
Snowflake Step 9 (Scene Briefs)    → STC Step 8: Screenplay (prose → formatted)
```

---

## 3. THE 9 STC STEPS TO BUILD

### Step 1: Logline
- Reuse Snowflake Step 1 output
- Add: protagonist, goal, opposition extraction

### Step 2: Genre (10 Blake Snyder genres)
- Monster in the House, Golden Fleece, Out of the Bottle, Dude with a Problem, Rite of Passage, Buddy Love, Whydunit, Forbidden Love, Superhero, Institutionalized Man
- Each genre has 6 specific rules to enforce downstream

### Step 3: Hero
- Primal wound, external goal, internal goal, false belief, true belief, ghost, breakout moment
- Built from Snowflake Step 3 character data

### Step 4: Beat Sheet (15 beats)
- Opening Image, Theme Stated, Setup, Catalyst, Debate, Break into Two, B Story, Fun & Games, Midpoint, Bad Guys Close In, All Is Lost, Dark Night of Soul, Break into Three, Finale, Final Image
- Page ranges proportional to total screenplay length
- Emotional polarity per beat

### Step 5: Board (40 scene cards, 4 acts)
- ~10 cards Act 1, ~8 cards Act 2a, ~8 cards Act 2b, ~14 cards Act 3
- Each card: emotional_polarity (+/-), conflict_marker (><, <>, =)
- Midpoint and All Is Lost must have opposite polarity

### Step 6: 8 Laws Validation
- Consistent theme, protagonist change, clear opposition, etc.
- Rules engine (not AI-dependent)

### Step 7: 8 Diagnostics
- 8 questions scored 1-10 each
- Identifies weakest areas before finalization

### Step 8: Screenplay
- Industry-standard format: sluglines, action, dialogue, parentheticals, transitions
- Export to PDF/DOCX/Final Draft XML

### Step 9: Marketing
- Logline, poster concept, comp titles, target audience, elevator pitch

---

## 4. RECOMMENDED ARCHITECTURE

### Option A: Standalone Module (RECOMMENDED)

```
src/screenplay_engine/
├── models.py                    # STC data models (~500 lines)
├── orchestrator.py              # Pipeline orchestrator (~400 lines)
├── steps/                       # 9 step implementations
│   ├── step_1_logline.py → step_9_marketing.py
├── prompts/                     # 9 prompt generators (~900 lines)
├── validators/                  # 9 validators (~900 lines)
├── formatters/
│   ├── screenplay_formatter.py  # Industry-standard format
│   ├── slugline_generator.py    # INT/EXT/SETTING/TIME
│   ├── action_formatter.py
│   └── dialogue_formatter.py
├── export/
│   ├── pdf_exporter.py
│   ├── docx_exporter.py
│   └── final_draft_exporter.py
├── adapters/
│   └── snowflake_to_stc_adapter.py
└── tests/
```

Mirrors Snowflake's proven architecture. Clean separation of concerns.

---

## 5. NEW API ROUTES NEEDED

```
POST /api/screenplay/create-project     # Create from Snowflake project
POST /api/screenplay/{id}/execute-step  # Execute STC step N
GET  /api/screenplay/{id}/status        # Project status
GET  /api/screenplay/{id}/artifacts/{n} # Get step artifact
POST /api/screenplay/{id}/export        # Export screenplay (PDF/DOCX)
```

---

## 6. FULL PIPELINE INTEGRATION

```
Story Idea (1-3 sentences)
        ↓
SNOWFLAKE ENGINE (11 steps) — EXISTS
        ↓ (characters, plot, scenes)
SCREENPLAY ENGINE (9 STC steps) — TO BE BUILT
        ↓ (formatted screenplay, beat sheet, 40-scene board)
SHOT ENGINE — TO BE BUILT
        ↓ (shot-by-shot queue with visual direction)
i2V VIDEO ENGINE — EXISTS
        ↓ (video with lip sync, transitions)
Final Video Product
```

---

## 7. WHAT EXISTS vs WHAT'S MISSING

### Exists (reusable patterns)
- Scene data models with STC-inspired fields
- Prompt template architecture (reuse from Steps 0-10)
- Validator architecture (reuse pattern)
- Orchestrator architecture (mirror SnowflakePipeline)
- Artifact persistence (JSON + CSV)
- API integration pattern (FastAPI router)
- Multi-provider AI generation with fallback
- Progress tracking (emit_event)

### Completely Missing
- STC data models (9 step-specific)
- STC prompts (9 generators)
- STC validators (9 validators)
- Screenplay formatters (slugline, action, dialogue)
- Industry-standard export (PDF/DOCX/FDX)
- Screenplay orchestrator
- Snowflake→STC adapter
- Beat sheet generation (15 beats)
- 40-scene board (act structure, polarity enforcement)
- STC Laws evaluation engine (8 laws)
- Diagnostic questions engine (8 questions)
- API routes (`/api/screenplay/*`)

---

## 8. IMPLEMENTATION ESTIMATE

| Component | Hours |
|-----------|-------|
| Models & Schema | 8 |
| 9 Prompts | 16 |
| 9 Validators | 14 |
| Formatters | 12 |
| Orchestrator | 10 |
| Adapters | 6 |
| Export Service | 12 |
| API Routes | 8 |
| Tests | 16 |
| Documentation | 8 |
| **Total** | **~110 dev + 32 test = 142 hours (~3 weeks)** |

Total new code: ~4,700 lines

---

## 9. PHASED APPROACH

### Phase 1: Foundation (Weeks 1-2)
- STC data models, 9 validators, 9 prompts, orchestrator, adapter

### Phase 2: Core Engine (Weeks 2-3)
- All 9 steps, screenplay formatters, export service, tests

### Phase 3: Integration (Week 3-4)
- API routes, database models, i2v integration, docs

### Phase 4: Polish (Ongoing)
- Performance, error recovery, advanced features

---

## 10. SUCCESS CRITERIA

- All 9 STC steps execute from Snowflake artifacts
- Screenplay exports to industry-standard PDF/DOCX
- Passes all 8 STC Laws validation
- 40-scene board has correct emotional polarity pattern
- Beat sheet always generates exactly 15 beats
- Diagnostic average score > 7/10
- Character consistency maintained across screenplay
- Backward compatibility with existing Snowflake pipeline

---

## REFERENCES

- `save the cat.pdf` and `Save-the-Cat-Goes-to-the-Movies-Blake-Snyder.pdf` in project root
- `i2v/docs/PRD_VISUAL_STORY_ENGINE.md` — Full integration architecture
- `src/scene_engine/models.py` lines 232-250 — Existing STC fields
- `src/pipeline/orchestrator.py` — Architecture to mirror
