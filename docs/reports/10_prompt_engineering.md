# Prompt Engineering Report
**Generated**: 2026-02-07 12:00 UTC
**Analyst**: Prompt Analysis Agent
**Scope**: All LLM prompts and interaction patterns in Snowflake project

---

## Executive Summary

The Snowflake project implements a sophisticated prompt engineering system across 11 story generation steps, plus specialized scene engine prompts. The system uses:

- **10 Snowflake Method prompt files** (Step 0-9) with structured templates
- **2 Scene Engine prompt systems** (templates.py + planning/prompts.py)
- **Unified AI interface** supporting both Anthropic and OpenAI models
- **Versioned prompts with hash tracking** for consistency
- **Revision and variation prompts** for iterative refinement

---

## 1. PROMPT TEMPLATE INVENTORY

### Pipeline Prompts (Step 0-9)

Located in: `src/pipeline/prompts/`

| Step | File | Purpose | Output Type |
|------|------|---------|------------|
| 0 | `step_0_prompt.py` | First Things First (market position) | JSON (category, story_kind, audience_delight) |
| 1 | `step_1_prompt.py` | One Sentence Logline | Plain text logline (<=25 words) |
| 2 | `step_2_prompt.py` | Five-Sentence Paragraph + Moral Premise | 5 sentences + 1 moral premise |
| 3 | `step_3_prompt.py` | Character Summary Sheets | JSON array of characters |
| 4 | `step_4_prompt.py` | One-Page Synopsis | JSON (5 synopsis paragraphs) |
| 5 | `step_5_prompt.py` | Character Synopses | JSON (350-700 words per character) |
| 6 | `step_6_prompt.py` | Long Synopsis (4-5 pages) | JSON (2500-3000 word synopsis) |
| 7 | `step_7_prompt.py` | Character Bibles | JSON (detailed character profiles) |
| 8 | `step_8_prompt.py` | Scene List | JSON (60-100 scenes with metadata) |
| 9 | `step_9_prompt.py` | Scene Briefs | JSON (proactive/reactive scene details) |

### Scene Engine Prompts

Located in: `src/scene_engine/generation/templates.py` and `src/scene_engine/planning/prompts.py`

- **TemplateLibrary** (templates.py): 5 built-in scene templates
- **PromptLibrary** (templates.py): Genre-specific prompts (Mystery, Romance, Fantasy)
- **Planning Prompts** (planning/prompts.py): Proactive, Reactive, Validation, Triage prompts

---

## 2. PROMPT STRUCTURE ANALYSIS

### Standard Prompt Format (All Pipeline Steps)

```python
class StepXPrompt:
    VERSION = "1.0.0"

    SYSTEM_PROMPT = """[LLM role and critical rules]"""

    USER_PROMPT_TEMPLATE = """[Input context with placeholders]

REQUIREMENTS (FOLLOW EXACTLY):
[Detailed specifications]

OUTPUT FORMAT (JSON/Plain Text):
{output_schema}
"""

    def generate_prompt(self, ...args) -> Dict[str, str]:
        """Returns {'system': str, 'user': str, 'prompt_hash': str, 'version': str}"""
```

### Key Structural Elements

1. **System Prompt** — Defines LLM role, critical rules, output structure
2. **User Prompt Template** — Context from previous steps, named placeholders, numbered REQUIREMENTS, OUTPUT FORMAT
3. **Revision Prompts** — Takes original artifact + error list, provides fix instructions
4. **Specialized Prompts** — Brainstorm (Step 2), Compression (Step 1), Depth (Step 3), Expansion (Step 3)

---

## 3. VARIABLE SUBSTITUTION PATTERNS

### Step 0: `brief`
### Step 1: `category`, `story_kind`, `audience_delight`, `story_brief`
### Step 2: Step 0 fields + `logline`
### Step 3: Step 0-2 fields + `character_template`
### Step 4: `step2_paragraph` (parsed into s1-s5), `moral_premise`
### Step 5: `character_details` (formatted from Step 3)
### Step 6: `p1-p5` (from Step 4), `target_word_count`
### Step 7: `character_synopses` (from Step 5)
### Step 8: `long_synopsis` + `character_names` + `target_words` + `scene_count`
### Step 9: `scene_list` + `scene_count` + `batch_scenes` + `start_index`

---

## 4. MODEL CONFIGURATION

### Supported Models
- **Anthropic**: Default `claude-3-5-haiku-20241022`
- **OpenAI**: Default `gpt-4o-mini`

### Temperature Settings (from code analysis)
- Steps 0-3: **0.3** (deterministic formatting)
- Steps 4-6: **0.5** (creative expansion)
- Steps 7-9: **0.3** (structured scene generation)

### Token Allocation Estimates

| Step | Est. Input | Est. Output | Total |
|------|-----------|------------|-------|
| 0 | 200 | 150 | 350 |
| 1 | 400 | 50 | 450 |
| 2 | 600 | 300 | 900 |
| 3 | 800 | 1500 | 2300 |
| 4 | 1200 | 1000 | 2200 |
| 5 | 2000 | 2500 | 4500 |
| 6 | 3000 | 3000 | 6000 |
| 7 | 4000 | 3500 | 7500 |
| 8 | 4500 | 2000 | 6500 |
| 9 | 6000 | 4000 | 10000 |

**Total per full run**: ~42,000 tokens

---

## 5. ACTUAL PROMPT TEXT EXAMPLES

### Step 0: System Prompt
```
You are the Snowflake Method Step 0 Planner. Your role is to lock the STORY MARKET POSITION before any plotting.

You must generate EXACTLY THREE FIELDS in plain, literal language:
1. Category: A real bookstore shelf label
2. Story Kind: One sentence with a trope noun
3. Audience Delight: One sentence listing 3-5 concrete satisfiers

NO flowery prose. NO metaphors. This is a product promise, not poetry.
```

### Step 1: Logline Requirements
```
REQUIREMENTS (FOLLOW EXACTLY):
1. START with protagonist name and role: "Name, a/an [functional role]"
2. ADD "must" + EXTERNAL GOAL: Use concrete action verb
3. ADD OPPOSITION with "despite" or "before"
4. COMPRESSION RULES: Start 35-40 words, compress to <=25
5. VALIDATION CHECKS: <=25 words, <=2 named characters, external goal concrete
```

### Step 2: Disaster Brainstorm
```
Generate 8-10 possible story disasters that:
1. Escalate in cost/stakes
2. Compress options
3. Force decisions
4. Match the genre expectations

For each: TYPE, PLACEMENT (D1/D2/D3), FORCING MECHANISM
```

### Step 6: Long Synopsis Requirements
```
ABSOLUTE REQUIREMENT: Write EXACTLY 2500-3000 words. This is MANDATORY.
SECTION 1 - ACT I SETUP (500-600 words)
SECTION 2 - DISASTER 1 CONSEQUENCES (500-600 words)
...
CRITICAL: Use required keywords: "forces", "pivot", "bottleneck"
```

### Step 9: Scene Briefs System
```
CRITICAL: Generate CONCRETE, SPECIFIC scene briefs with:
- Action verbs (steal, find, escape, prove, destroy, capture)
- Named obstacles (guards, alarms, rival gangs, corrupt cops)
- Time constraints (before midnight, within 24 hours, by dawn)
- Physical/emotional reactions (trembles, vomits, collapses)

SAVE THE CAT ENHANCEMENTS:
- emotional_polarity: "+" or "-"
- emotional_start/end: Must differ
- conflict_parties: Who vs whom
- conflict_winner, storyline (A/B/C)
```

---

## 6. PROMPT QUALITY ASSESSMENT

| Step | Clarity | Completeness | Structure | Notes |
|------|---------|------------|-----------|-------|
| 0 | 9/10 | 9/10 | 9/10 | Excellent constraints |
| 1 | 9/10 | 9/10 | 9/10 | Perfect compression rules |
| 2 | 8/10 | 8/10 | 8/10 | Moral premise could be clearer |
| 3 | 7/10 | 8/10 | 8/10 | Character fields excessive |
| 4 | 8/10 | 8/10 | 8/10 | Paragraph mapping good |
| 5 | 7/10 | 7/10 | 7/10 | Synopsis length clear |
| 6 | 9/10 | 9/10 | 9/10 | Word count strictness excellent |
| 7 | 6/10 | 7/10 | 8/10 | Too many fields, limited guidance |
| 8 | 8/10 | 8/10 | 8/10 | Scene conflict clear |
| 9 | 9/10 | 9/10 | 9/10 | Proactive/Reactive excellent |

**Average**: 8.0/10

---

## 7. OUTPUT FORMAT EXPECTATIONS

### Step 0: JSON `{category, story_kind, audience_delight}`
### Step 1: Plain text logline (<=25 words)
### Step 2: 5 sentences + moral premise
### Step 3: JSON array of character objects (name, role, goal, ambition, values, conflict, epiphany, arc)
### Step 4: JSON `{synopsis_paragraphs: {p1-p5}}`
### Step 5: JSON `{characters: [{name, synopsis (350-700 words)}]}`
### Step 6: JSON `{long_synopsis: "2500-3000 words"}`
### Step 7: JSON with extensive character bible fields (physical, personality, environment, psychology, relationships, voice_notes, contradictions, plot_connections)
### Step 8: JSON `{scenes: [{index, chapter_hint, type, pov, summary, time, location, word_target, conflict, hooks}]}`
### Step 9: JSON `{scene_briefs: [{scene_num, type, goal/conflict/setback OR reaction/dilemma/decision, emotional_polarity, storyline}]}`

---

## 8. PROMPT CHAINING & DATA FLOW

```
Step 0 → category, story_kind, audience_delight
  ↓
Step 1 → logline (<=25 words)
  ↓
Step 2 → 5-sentence paragraph + moral premise
  ↓
Step 3 → character array
  ↓
Step 4 → 5 expanded paragraphs (from Step 2 sentences)
  ↓
Step 5 → character synopses (from Step 3)
  ↓
Step 6 → 2500-3000 word synopsis (from Step 4)
  ↓
Step 7 → character bibles (from Step 5)
  ↓
Step 8 → 60-100 scenes (from Step 6 + Step 7)
  ↓
Step 9 → scene briefs (from Step 8)
  ↓
Step 10 → manuscript (from Steps 7-9)
```

---

## 9. SCENE ENGINE PROMPTS

### 5 Built-in Scene Templates
1. **Proactive Opening** — Goal-driven scene opening
2. **Reactive Continuation** — Response to setback
3. **Action Sequence** — Fast-paced, life-or-death
4. **Dialogue-Heavy** — Subtext-driven confrontation
5. **Introspective** — Internal conflict resolution

### Genre-Specific Prompts
- **Mystery**: Clues, red herrings, deduction, suspense
- **Romance**: Emotional connection, relationship development
- **Fantasy**: Magic systems, world-building, mythic tone

### Planning Prompts
- **ProactivePrompt**: Goal → Conflict → Setback (5-criteria goal validation)
- **ReactivePrompt**: Reaction → Dilemma → Decision (next_goal_stub output)
- **ValidationPrompt**: CrucibleNowCheck, GoalFiveCheck, ConflictEscalation, etc.
- **TriagePrompt**: YES/NO/MAYBE evaluation

---

## 10. PROMPT HASH TRACKING

```python
prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
```

All pipeline prompts at **Version 1.0.0**

---

## 11. MISSING PROMPTS & GAPS

1. **Step 10 (First Draft Writer)** — No `step_10_prompt.py` exists, uses inline/different approach
2. **Genre-specific pipeline prompts** — Scene engine has genre templates but pipeline is genre-agnostic
3. **Consistency checking** — No cross-document validation prompts
4. **User feedback loop** — No prompts for incorporating edits
5. **Model-specific tuning** — Same prompts for Claude and GPT-4

---

## 12. RECOMMENDATIONS

1. Integrate Step 10 prompt into versioned system
2. Add genre-specific prompts to pipeline (not just scene engine)
3. Optimize prompt length (some exceed 300 lines)
4. Add model-specific examples for Claude vs GPT-4
5. Create consistency checker prompts for multi-document validation
6. Consider prompt compression for Steps 7-9

---

**Analysis complete: 10 pipeline prompt files, 2 scene engine prompt systems, ~42,000 tokens per full run**
