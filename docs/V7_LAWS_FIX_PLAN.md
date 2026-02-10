# v7.0.0 Fix Plan: Immutable Laws Failures

**Date**: 2026-02-10
**Status**: PLAN (not yet implemented)
**Target**: Fix the 3 failing Immutable Laws from Step 7 (Pope in the Pool, Covenant of the Arc, Keep the Press Out)

---

## Current State (v6.0.0)

Step 6 (Screenplay Writing) now scores **9/9** on all 4 acts with Grok checker after targeted scene revisions. Step 7 (Immutable Laws) fails **3 of 7** laws:

| Law | Status | Root Cause |
|-----|--------|------------|
| 1. Save the Cat | PASS | |
| 2. Pope in the Pool | **FAIL** | Step 5 Board prompt has NO rule against pure exposition scenes |
| 3. Double Mumbo Jumbo | PASS | |
| 4. Black Vet | PASS | |
| 5. Watch Out for That Glacier | PASS | |
| 6. Covenant of the Arc | **FAIL** | Step 3 generates NO arc fields for B-story or supporting characters |
| 7. Keep the Press Out | **FAIL** | Neither Step 5 nor Step 8 prompts forbid news/media scenes |

---

## Fix 1: Pope in the Pool (Step 5 Board Prompt)

### Problem

Step 5 (`step_5_prompt.py`) generates 40 board cards. Nothing in the prompt tells GPT that **pure exposition/briefing scenes are forbidden**. So GPT designs cards like:

> Card 12: INT. SITUATION ROOM - DAY
> "Rae's team leader briefs the squad on the blackout's origin, timeline, and affected infrastructure."

This card is a pure information dump. No visual distraction, no entertainment — just characters talking about the plot. The Pope in the Pool law says every exposition scene MUST have something visually entertaining happening simultaneously so the audience forgets they're being fed backstory.

### Where to Fix

**File**: `src/screenplay_engine/pipeline/prompts/step_5_prompt.py`
**Location**: Add to `CARD CONTENT RULES` section in `USER_PROMPT_TEMPLATE` (after the emotional change rule, before STRUCTURAL RULES)

### Exact Prompt Text to Add

```
POPE IN THE POOL RULE (Snyder Ch.6 — Immutable Law #2):
Every scene that conveys backstory, exposition, or plot information MUST simultaneously
have something visually entertaining, surprising, or distracting happening. The audience
should be so distracted by what they SEE that they absorb the information without noticing
they're being told things.

The name comes from "The Plot to Kill the Pope" — vital backstory about the assassination
plot is delivered while the Pope swims laps in a bathing suit at the Vatican pool. We aren't
even listening to the exposition because we're watching the Pope in a Speedo.

BAD CARD (pure exposition — this is what you must NEVER write):
  Card 12: INT. SITUATION ROOM - DAY
  "Rae's team leader briefs the squad on the blackout's origin, timeline, and infrastructure."
  This is a character standing at a screen talking AT the audience. There is nothing visual
  or entertaining happening. The audience will tune out.

GOOD CARD (exposition buried in visual entertainment):
  Card 12: EXT. ROOFTOP WATER TOWER - DAY
  "Rae climbs a swaying water tower to manually reset a relay while her partner shouts
  infrastructure details from below — the grid is failing in sectors, hospitals are next."
  The exposition (grid sectors, hospital timeline) is delivered while we watch Rae dangling
  from a water tower. The audience absorbs the info because they're worried she'll fall.

GOOD CARD (exposition buried in conflict):
  Card 12: INT. SERVER FARM - DAY
  "Rae interrogates a captured technician about the blackout while the building's backup
  generator sputters and dies around them, plunging sections into darkness one by one."
  The exposition (blackout origin, timeline) is delivered while physical danger escalates.

RULE: If a card's description contains ANY of these words — "briefs," "explains," "debriefs,"
"informs," "reveals to the team," "goes over the plan," "lays out the situation" — the card
is PROBABLY a Pope in the Pool violation. Rewrite it so the information is delivered during
action, danger, comedy, or visual spectacle.

ZERO TOLERANCE: Do NOT create any card where characters sit/stand and talk about the plot.
Every card must have PHYSICAL ACTION happening alongside any information delivery.
```

### Validator Change

**No validator change needed.** Pope in the Pool is an AI-evaluated law (Step 7 prompt already checks for it). The fix is preventive — stop GPT from creating exposition-dump board cards in the first place.

---

## Fix 2: Covenant of the Arc (Step 3 Hero Prompt + Validator)

### Problem

Step 3 (`step_3_prompt.py`) generates detailed arc fields for the **hero** (opening_state, final_state, six_things_that_need_fixing) but the **B-story character** only gets 3 fields:

```json
"b_story_character": {
  "name": "Juno",
  "relationship_to_hero": "estranged younger sister",
  "theme_wisdom": "Trust isn't control — it's letting go"
}
```

No `opening_state`. No `final_state`. No arc whatsoever.

Snyder Ch.6 is explicit: **"Every single character in your movie must change. The only characters who don't change are the Bad Guys."** His Post-it note on his iMac said "EVERYBODY arcs." He gives Pretty Woman as an example: Richard Gere, Julia Roberts, Laura San Giacomo, AND Hector Elizondo ALL have arcs. Only Jason Alexander (the villain) "learns exactly zero."

The B-story character MUST have an arc. The antagonist MUST NOT have one (Snyder: "that's why they lose" — they refuse to change).

### Where to Fix

**File**: `src/screenplay_engine/pipeline/prompts/step_3_prompt.py`

#### Change 1: Add arc fields to B-story character section

**Location**: In `USER_PROMPT_TEMPLATE`, after item 25 (THEME_WISDOM), add items 26-27.

Replace the current B-story section:

```
=== B-STORY CHARACTER ===

23. NAME: The B-story character's name

24. RELATIONSHIP_TO_HERO: Must be a PRIMAL relationship. [...]

25. THEME_WISDOM: The specific lesson this character teaches that solves the A-story. [...]
```

With:

```
=== B-STORY CHARACTER ===

Snyder Ch.6: "Every single character in your movie must change in the course of your story.
The only characters who don't change are the Bad Guys." His Post-it note: "EVERYBODY arcs."

Pretty Woman example: Richard Gere arcs (cold businessman → opens his heart), Julia Roberts
arcs (lost woman → self-respecting person), Laura San Giacomo arcs (cynical friend → supportive
ally), Hector Elizondo arcs (rule-following hotel manager → someone who bends rules for love).
ONLY Jason Alexander (the villain) "learns exactly zero."

The B-story character MUST have an arc. They change through their relationship with the hero.
The B-story character starts the movie one way, and by the Final Image they are different.

23. NAME: The B-story character's name

24. RELATIONSHIP_TO_HERO: Must be a PRIMAL relationship. Snyder: "husbands and wives, fathers
    and daughters, mothers and sons, ex-boyfriends and girlfriends, brothers and sisters."
    NOT a colleague, mentor, or stranger. We respond to these because "you say 'father' and
    I see MY father."

25. THEME_WISDOM: The specific lesson this character teaches that solves the A-story. The
    B-story carries the theme — the wisdom learned here is what the hero needs to win the
    A-story climax.

26. OPENING_STATE: Who the B-story character is when we first meet them. Be specific.
    BAD: "She's distant." (Too vague — distant how? Why? What does it look like?)
    GOOD: "Juno avoids eye contact with Rae, communicates only through one-word texts,
    and has physically moved 3,000 miles away to avoid dealing with their father's death."

27. FINAL_STATE: Who the B-story character becomes by the Final Image. MUST show clear
    change from opening_state — they are NOT the same person.
    BAD: "She's closer to Rae." (Vague, tells us nothing about HOW she changed.)
    GOOD: "Juno initiates a hug with Rae for the first time in years, has moved back to
    the same city, and openly talks about their father — the grief she was running from is
    now something she faces with her sister."
```

#### Change 2: Add explicit NO-ARC rule to antagonist section

**Location**: In `USER_PROMPT_TEMPLATE`, after item 22 (MIRROR_PRINCIPLE), add a note.

After:
```
22. MIRROR_PRINCIPLE: How the antagonist and hero are "two halves of the same person." [...]
```

Add:
```
IMPORTANT — THE ANTAGONIST DOES NOT ARC:
Snyder Ch.6: "Good guys accept change as a positive force. Bad guys refuse to change — that's
why they lose." The antagonist is the SAME person at the end as at the beginning. They do not
learn, they do not grow, they do not have an epiphany. Their refusal to change is what makes
them the villain and what ultimately causes their defeat.

Do NOT give the antagonist an opening_state/final_state — they have NONE. They are static.
Jason Alexander in Pretty Woman "learns exactly zero" — that IS the point.
```

#### Change 3: Update JSON output format

Add the new fields to the b_story_character JSON template:

```json
"b_story_character": {
    "name": "<B-story character name>",
    "relationship_to_hero": "<primal relationship>",
    "theme_wisdom": "<lesson that solves A-story>",
    "opening_state": "<who they are when we first meet them — specific behaviors>",
    "final_state": "<who they become by Final Image — MUST differ from opening_state>"
}
```

### Validator Change

**File**: `src/screenplay_engine/pipeline/validators/step_3_validator.py`

Add two new checks after the existing B-story checks (check 9):

```python
# After checking theme_wisdom, name, relationship_to_hero...

# B-story opening_state
bs_opening = (b_story.get("opening_state") or "").strip()
if not bs_opening:
    errors.append(
        "MISSING_B_STORY_OPENING_STATE: B-story character must have "
        "opening_state — who they are when we first meet them. "
        "Snyder Ch.6: 'Every single character must change.'"
    )
elif len(bs_opening) < 20:
    errors.append(
        "VAGUE_B_STORY_OPENING_STATE: B-story opening_state is too short "
        f"({len(bs_opening)} chars). Be specific: what do they DO, avoid, believe?"
    )

# B-story final_state
bs_final = (b_story.get("final_state") or "").strip()
if not bs_final:
    errors.append(
        "MISSING_B_STORY_FINAL_STATE: B-story character must have "
        "final_state — who they become by the Final Image. "
        "Snyder Ch.6: 'Everybody arcs.'"
    )
elif len(bs_final) < 20:
    errors.append(
        "VAGUE_B_STORY_FINAL_STATE: B-story final_state is too short "
        f"({len(bs_final)} chars). Be specific: what changed?"
    )

# B-story opening and final must differ
if bs_opening and bs_final:
    if bs_opening.lower() == bs_final.lower():
        errors.append(
            "IDENTICAL_B_STORY_ARC: B-story opening_state and final_state "
            "are identical — the character MUST change."
        )
```

Also add `fix_suggestions` entries for these new error codes.

### Downstream Impact

- **Step 5 Board prompt** (`step_5_prompt.py`): The `_summarize_characters()` method already outputs B-story character info. Add `Opening State` and `Final State` to the B-story summary so the Board knows the B-story character's arc and can design cards showing their transformation.
- **Step 8 Screenplay prompt** (`step_8_prompt.py`): The character identifiers already include B-story info. The arc fields will flow through naturally since we pass `step_3_artifact` to the scene generation prompts.
- **Step 7 Laws prompt** (`step_6_prompt.py`): Already checks Covenant of Arc. Now that the B-story character HAS arc data, the evaluator can actually verify it. No prompt change needed — just having the data will let the existing check pass.

### Test Updates

**File**: `tests/steps/test_sp_step_3_hero.py`
- All test fixtures that include `b_story_character` must add `opening_state` and `final_state` fields.
- Add test cases for the new validator checks (missing opening_state, missing final_state, identical arc states, vague states).
- Version bump test to match new prompt version.

---

## Fix 3: Keep the Press Out (Step 5 Board + Step 8 Screenplay Prompts)

### Problem

GPT adds news crews, reporters, and media coverage to screenplay scenes even when the board cards don't call for it. Snyder Ch.6 is explicit: bringing in the press "blew the reality of the premise." He learned this from Spielberg during development of Nuclear Family — keeping the supernatural contained "between them and us, the audience" made "the magic stay real."

Exception: "Unless it's about the press, unless your movie involves a world-wide problem." If the story IS about media (e.g., Network, Wag the Dog), then press is part of the premise.

### Where to Fix

#### Change 1: Step 5 Board Prompt

**File**: `src/screenplay_engine/pipeline/prompts/step_5_prompt.py`
**Location**: Add to `CARD CONTENT RULES` section, right after the Pope in the Pool rule.

```
KEEP THE PRESS OUT (Snyder Ch.6 — Immutable Law #7):
Do NOT design any card that includes news reporters, TV crews, press conferences, media
coverage, social media going viral, or journalists covering the story's events. Snyder
learned this from Steven Spielberg: "By keeping it contained among the family and on the
block, by essentially keeping this secret between them and us, the audience, the magic
stayed real." When you bring the press in, you "blow the reality of the premise."

E.T. example: Spielberg catches a REAL ALIEN — no news crews show up. The story stays
between Elliott, his family, and the alien. This containment is what makes it magical.

Signs VIOLATES this: CNN coverage of worldwide alien landings makes the Hess family's
private crisis feel less desperate. The global scope dilutes the personal stakes.

BAD CARD:
  Card 35: INT. NEWS STUDIO - NIGHT
  "A CNN anchor reports on the citywide blackout as Rae watches from a bar TV."
  This breaks containment. The audience now thinks "why doesn't the government/military
  handle this?" The hero's personal stakes are diluted by institutional awareness.

GOOD CARD:
  Card 35: INT. DIVE BAR - NIGHT
  "Rae overhears two strangers arguing about whether the blackout is a cyberattack or
  a transformer failure. Nobody knows the truth except Rae — and she can't tell anyone."
  The information about public perception is conveyed through CHARACTERS, not media.
  The containment stays intact — the audience knows what Rae knows, and the secret stays
  between Rae and us.

EXCEPTION: If the logline's premise IS about media/journalism (e.g., the hero is a
reporter, the story is about a media scandal), then press scenes are part of the premise
and this rule does not apply. For ALL other stories: zero news/media/press cards.

BANNED WORDS in card descriptions: "news," "reporter," "broadcast," "coverage," "press
conference," "media," "journalist," "anchor," "breaking news," "goes viral," "trending."
If your card contains any of these words, DELETE the card and replace it with a scene
that conveys the same information through personal, contained interactions.
```

#### Change 2: Step 8 Screenplay Prompt

**File**: `src/screenplay_engine/pipeline/prompts/step_8_prompt.py`
**Location**: Add to the scene writing rules in the act generation prompt (where the other diagnostic-prevention rules are).

Add to the `SCENE_WRITING_RULES` or equivalent section:

```
KEEP THE PRESS OUT (Snyder Ch.6 — Immutable Law #7):
Do NOT write any scene element that includes:
- TV news broadcasts playing in the background
- Radio news reports the characters overhear
- Journalists or reporters appearing as characters
- Press conferences or media scrums
- Social media posts, trending topics, or viral content about the story's events
- Any character watching/reading/hearing news coverage of what's happening

Snyder: "By keeping it contained among the family and on the block, the magic stayed
real." E.T. has a real alien and ZERO news crews. That's why it works.

BAD (press breaks containment):
  [ACTION] A TV in the corner shows a news anchor reporting on the citywide blackout.
  RAE glances at the screen, jaw tightening.

GOOD (information stays personal and contained):
  [ACTION] A drunk at the end of the bar slams his glass down. "Third night in a row
  the power's been cutting out. My wife thinks it's terrorists." Rae says nothing.
  She knows the truth is worse.

EXCEPTION: Only if the story's premise is ABOUT media/journalism. For all other stories,
the press does not exist in this world.
```

### Validator Change

No validator change needed. Keep the Press Out is AI-evaluated by the Step 7 Laws prompt, which already checks for it. The fix is preventive — stop GPT from creating media scenes in the first place, at both the Board level (Step 5) and the Screenplay level (Step 8).

### Test Updates

No new test cases needed — the existing Laws evaluation tests already cover the Keep the Press Out check. The prompt changes are preventive.

---

## Fix 4: Step 7 Laws Evaluation Robustness

### Problem

Step 7 (`step_6_immutable_laws.py`) currently uses `generate_with_validation()` with the default `max_attempts=2`. This means if GPT's evaluation returns an invalid JSON format, it retries once and gives up. There is NO Grok-based revision loop — unlike Step 6 (Screenplay) which has a 5-round Grok revision loop.

Additionally, the Step 7 prompt (`step_6_prompt.py`) asks the evaluator to check the screenplay, but when a law FAILS, there is no mechanism to actually FIX the screenplay. Step 7 just reports the failures and returns `success=False`. The orchestrator then... does nothing with that information.

### What to Change

**This is a bigger architectural change that should be implemented AFTER the upstream fixes (1-3) are verified to work.** The upstream fixes should eliminate most law violations at the source. If laws still fail after v7.0.0 upstream fixes, then we add a revision loop to Step 7.

For now, the plan is:
1. Implement Fixes 1-3 (upstream prevention)
2. Run the pipeline
3. If any laws STILL fail, add a Grok-based targeted revision loop to Step 7 (similar to the Step 6 act-by-act loop but for specific law violations)

---

## Fix 5: Step 5 Board Character Summary Enhancement

### Problem

The `_summarize_characters()` method in `step_5_prompt.py` currently outputs B-story character info but only shows `name`, `relationship_to_hero`, and `theme_wisdom`. Once Fix 2 adds `opening_state` and `final_state` to the B-story character, the Board prompt should include these so GPT can design cards showing the B-story character's transformation arc.

### Where to Fix

**File**: `src/screenplay_engine/pipeline/prompts/step_5_prompt.py`
**Method**: `_summarize_characters()`

After the existing B-story lines:
```python
lines.append(
    f"  B-STORY: {b_char.get('name')} -- {b_char.get('relationship_to_hero', '')}"
)
lines.append(f"    Theme wisdom: {b_char.get('theme_wisdom', '')}")
```

Add:
```python
b_opening = b_char.get("opening_state", "")
b_final = b_char.get("final_state", "")
if b_opening:
    lines.append(f"    Opening State: {b_opening}")
if b_final:
    lines.append(f"    Final State: {b_final}")
```

---

## Implementation Order

1. **Fix 2** (Step 3: B-story character arcs) — FIRST, because downstream fixes depend on this data existing
2. **Fix 5** (Step 5: character summary enhancement) — immediately after Fix 2
3. **Fix 1** (Step 5: Pope in the Pool rule) — independent, can be done in parallel with Fix 3
4. **Fix 3** (Step 5 + Step 8: Keep the Press Out rule) — independent
5. **Fix 4** (Step 7: revision loop) — LAST, only if needed after upstream fixes
6. **Run all tests** — verify no regressions (currently 970+ passing)
7. **Run E2E pipeline** — verify all 7 laws pass
8. **Commit as v7.0.0**

## Files Changed

| File | Fix | Change |
|------|-----|--------|
| `src/screenplay_engine/pipeline/prompts/step_3_prompt.py` | Fix 2 | Add opening_state/final_state to B-story, add NO-ARC rule to antagonist, update JSON template |
| `src/screenplay_engine/pipeline/validators/step_3_validator.py` | Fix 2 | Add validation checks for B-story opening_state/final_state |
| `src/screenplay_engine/pipeline/prompts/step_5_prompt.py` | Fix 1, 3, 5 | Add Pope in Pool rule, Keep Press Out rule, enhance B-story summary |
| `src/screenplay_engine/pipeline/prompts/step_8_prompt.py` | Fix 3 | Add Keep Press Out scene writing rule |
| `tests/steps/test_sp_step_3_hero.py` | Fix 2 | Add B-story arc fields to fixtures, add new validator test cases |

## Version Bumps

| File | Current | New |
|------|---------|-----|
| `step_3_prompt.py` | 2.0.0 | 3.0.0 |
| `step_3_validator.py` | 2.0.0 | 3.0.0 |
| `step_5_prompt.py` | 3.0.0 | 4.0.0 |
| `step_8_prompt.py` | 3.0.0 | 4.0.0 |

## Success Criteria

- All existing 970+ tests still pass
- New B-story arc validator tests pass
- E2E pipeline run: Step 7 Laws = 7/7 PASS
- Specifically: Pope in Pool PASS, Covenant of Arc PASS, Keep Press Out PASS
