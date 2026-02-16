# Snowflake Project - AI Screenplay & Video Generation System

## Project Overview

**What:** AI-powered screenplay generation pipeline implementing Blake Snyder's "Save the Cat" method, with automated shot planning and visual bible generation for video production.

**Where:** C:\Users\asus\Desktop\projects\snowflake

**Related:** i2v video generation platform at C:\Users\asus\Desktop\projects\i2v

**Pipeline:** Story (Snowflake) → Screenplay (Save the Cat) → Shot Engine → Visual Bible → Video (i2v)

## Architecture

### Five Engines

1. **Snowflake Engine** (src/pipeline/) - Randy Ingermanson's 11-step novel generation method
2. **Screenplay Engine** (src/screenplay_engine/) - Blake Snyder's 9-step Save the Cat method (970 tests)
3. **Shot Engine** (src/shot_engine/) - 6-step deterministic shot planning (V1-V6)
4. **Visual Bible Engine** (src/visual_bible/) - Image prompt generation and asset manifesting
5. **AI Layer** (src/ai/) - Multi-provider LLM abstraction (OpenAI, Anthropic, xAI)

### Pipeline Order

**Screenplay Steps:**
1. Logline (Ch.1)
2. Genre (Ch.2)
3. Hero (Ch.3)
4. Beat Sheet (Ch.4)
5. Board (Ch.5)
6. Screenplay (end Ch.5)
7. Laws (Ch.6)
8. Diagnostics (Ch.7)
9. Marketing (Ch.8)

**Optional Steps:**
- 3b: World Bible (geography, culture, economy, history)
- 3c: Full Cast (3-tier supporting characters, layered generation)
- 5b: Visual Bible (style bible, color script, location designs)
- 8b: Targeted Rewrite (Grok-powered act-level revision)

**Shot Engine Steps:**
- V1: Scene Decomposition (parse screenplay into shot segments)
- V2: Shot Type Assignment (wide, medium, close-up, etc.)
- V3: Camera Behavior (movement, lens, height)
- V4: Duration & Pacing (beat-aware timing)
- V5: Transition Planning (cut, dissolve, fade)
- V6: Prompt Generation (T2I, I2I, I2V prompts)

### Artifacts Directory

All generated content saved to: `artifacts/<project_id>/`

**Screenplay artifacts:**
- sp_step_1_logline.json
- sp_step_2_genre.json
- sp_step_3_hero.json
- sp_step_3b_world_bible.json
- sp_step_3c_full_cast.json
- sp_step_4_beat_sheet.json
- sp_step_5_board.json
- sp_step_5b_visual_bible.json
- sp_step_6_laws.json
- sp_step_7_diagnostics.json
- sp_step_8_screenplay.json
- sp_step_9_marketing.json

**Shot/Visual artifacts:**
- shot_list.json (754 shots for 40-scene screenplay)
- visual_manifest.json
- prompt_batch.json

## Critical Technical Rules

### Save the Cat Method is THE Authority

1. **No assumptions about how Save the Cat works** - If unsure, check the book text in temp_pages/stc_chapters/
2. **Characters emerge organically** - NO bulk supporting cast generation. Characters develop through beats → board → screenplay (the "layers" approach user requested)
3. **7 Immutable Laws, NOT 8** - "Laying Pipe" was fabricated and removed
4. **9 Diagnostic Checks, NOT 8** - "Is It Primal?" was missing and added
5. **Write FIRST, then diagnose** - Chapter 7 diagnostics run AFTER screenplay writing, not before
6. **Emotional polarity is a before/after pair** - emotional_start and emotional_end (+/-), not a single direction
7. **Structure naturally produces length** - DO NOT add meta-instructions like "this is a feature film, needs to be 90-110 pages"

### Shot Engine is Deterministic

- **NO LLM calls in V1-V6** - Shot engine uses rule-based shot selection only
- Content trigger determines default shot type/camera/duration
- Emotional intensity modulates shot choices
- Format multipliers adjust pacing (TikTok 0.5x, Feature 1.2x)
- Beat curve modulates pacing (Opening moderate, Midpoint rapid)

### AI/LLM Rules

- **OpenAI GPT uses max_completion_tokens** (not max_tokens)
- **Screenplay generation takes ~10-15 min** with GPT 5.2 (128K token call)
- **Timeout settings:** OpenAI 1200s, Anthropic streaming, xAI 600s
- **Bulletproof failover:** Claude Sonnet → Haiku → GPT-4 → GPT-3.5 → Emergency content

## File Organization

**NEVER save files to the root folder.**

- **Source code:** src/
- **Tests:** tests/
- **Scripts:** scripts/
- **Documentation:** docs/
- **Generated artifacts:** artifacts/
- **Book reference:** temp_pages/stc_chapters/*.txt

## Testing

**Run all tests:**
```bash
python -m pytest tests/ -v
```

**Screenplay engine tests (970 tests):**
```bash
python -m pytest tests/screenplay_engine/ -v
```

**Always run tests before declaring something fixed.**

## Common Commands

**Full screenplay pipeline:**
```bash
python scripts/test_screenplay_live.py
```

**Shot engine:**
```bash
python scripts/test_shot_engine.py
```

**Visual bible:**
```bash
python scripts/test_visual_bible.py
```

**Specific step test:**
```bash
python scripts/test_step_X.py
```

## Important Files

**Orchestrators:**
- src/screenplay_engine/pipeline/orchestrator.py (876 lines, main STC pipeline)
- src/shot_engine/pipeline/orchestrator.py (155 lines, shot planning)
- src/visual_bible/pipeline/orchestrator.py (474 lines, asset manifest)

**AI Layer:**
- src/ai/generator.py (549 lines, multi-provider with failover)
- src/ai/bulletproof_generator.py (294 lines, 5-tier failover)

**Models:**
- src/screenplay_engine/models.py (Pydantic data models for all STC artifacts)
- src/shot_engine/models.py (Shot, ShotSegment, ShotList, ContentTrigger enums)
- src/visual_bible/models.py (VisualManifest, CharacterState, SettingState)

**STC Book Text:**
- temp_pages/stc_chapters/ch1.txt through ch8.txt
- savethecat.docx (source document)

## Known Issues & Context

### Persistent Diagnostic Failures (5/9)

These are GPT writing tendencies, not structural problems:
1. **Hero Leads** - AI evaluator too strict about hero proactivity
2. **Talking the Plot** - Characters explain plot in dialogue (hard to fix without human rewrite)
3. **Emotional Color Wheel** - Tech thrillers naturally lean fear/tension/dread
4. **Hi How Are You** - Introductory dialogue feels generic
5. **Limp and Eye Patch** - Supporting characters lack distinctive visual identifiers

**Attempted fixes:** Monolithic (v2), scene-by-scene (v3), act-by-act+Grok (v4) all produce same 4-5/9 pass rate.

**Next steps:** Better prompts with concrete examples, or different writer model.

### Shot Engine V6 Bugs (Critical)

1. **Garbage video_prompt** - Motion extraction fails on 2/754 shots (e.g., "figure skip turns, they slam into the")
2. **Missing characters_in_frame** - 296/754 shots (39%) have empty character lists despite characters in content
3. **Speaking duplication** - "speaking, speaking" in some dialogue prompts

**Fix locations:** src/shot_engine/pipeline/steps/step_v6_prompts.py

### Environment Notes

- save the cat.pdf is scanned - use savethecat.docx instead
- OpenAI GPT 5.2 uses max_completion_tokens (not max_tokens)
- Screenplay generation takes ~10 min with GPT 5.2 (128K token call)

## DO NOT

1. **Do not create documentation files** unless explicitly asked
2. **Do not save files to the root folder** - use appropriate subdirectories
3. **Do not make assumptions about Save the Cat methodology** - check the book text
4. **Do not add Step 3b "Supporting Cast"** to the main screenplay pipeline (user explicitly rejected this as non-STC)
5. **Do not try to save tokens or reduce API calls** - Quality over cost (user directive: "I don't give a fuck about that right now")
6. **Do not assume steps can be skipped** - Go step by step, put more effort into each step (user directive)

## User Directives (MUST Follow)

From prior sessions, the user has given these CRITICAL directives:

1. "from here on out, no assumptions at all as far as how save the cat does things"
2. "the Save the Cat method is what we want. Whatever order that goes in... that's exactly how we need to do it"
3. "one api call for all the supporting cast seems like it won't do a good job. i feel like they should be added in layers"
4. "regarding the api calls and trying to save money or save tokens, i don't give a fuck about that right now"
5. "I want you to go step by step now, from now on. put more effort into each step"
6. "it should not need to say 'this is a feature film, needs to be 90-110 pages'" - structure naturally produces length

## Documentation References

**For understanding the codebase:**
- docs/SNOWFLAKE_CODEBASE_DIGEST.md (full architecture, 34,000+ LOC, 202 files)
- docs/PIPELINE_ARCHITECTURE_DIAGRAM.md (visual pipeline flow, gap analysis)

**For STC methodology:**
- temp_pages/stc_chapters/*.txt (book text for all 8 chapters)
- docs/stc_audit/*.txt (step-by-step audit reports)

**For progress tracking:**
- docs/stc_audit/PROGRESS_REPORT_20260208.txt (v2.0.0 completion status)
- docs/stc_audit/MASTER_FIX_PLAN.txt (partially superseded)

## Version History

**Screenplay Engine:** v2.0.0 (all 9 steps + checkpoint system complete)
**Shot Engine:** v12.0.0 (setting-per-location architecture)
**Total Tests:** 970 passing (all steps validated)

---

**Remember:** This is a Save the Cat screenplay engine first, shot planner second, video generator third. The methodology is sacred - no shortcuts, no assumptions.
