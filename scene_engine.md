# ZAD REPORT — **Snowflake Bot: Scene Engine (SceneForge)**

**Zero-Assumption Documentation (ZAD) PRD — step-by-step, no prior knowledge required.**
**Method fidelity:** Implements Randy Ingermanson’s *How to Write a Dynamite Scene Using the Snowflake Method* with **zero deviation**.
**Format:** ZAD (Zero-Assumption Documentation) with TaskMaster/Context7 compliance notes.&#x20;

---

## 0) Methodology Compliance (ZAD Requirements)

* **Task definition:** `task-master show <SCENE-ENGINE>` → Objective: “Generate a full scene (prose) that is structurally valid under Ingermanson’s method (Proactive or Reactive), chains correctly to adjacent scenes, and respects exposition limits.” *(Documenting the requirement per ZAD framework)*.&#x20;
* **Research expansion:** `task-master expand --id=<SCENE-ENGINE> --research` → Source corpus: user-supplied text “how-to-write-a-dynamite-scene-using-the-snowflake-method-2.txt” (canonical), and Ingermanson’s novel Snowflake step-9 excerpts for worked examples. **All rules and examples below are line-cited to these sources.**       &#x20;
* **Context7 integration:** This document encodes “no-prior-knowledge” definitions, before/after contrasts, concrete examples, and verification steps per ZAD.&#x20;

> **Read this as if you’ve never heard of Randy, “scenes vs sequels”, or Snowflake. Every step tells you exactly what to do, why, how to verify, and how to fix failures.**

---

# PART A — Zero-Assumption Context (What the heck is a “scene” here?)

### A1) Scene vs Story (two “crucibles”)

* **A story** = a character trapped in a big, ongoing pressure cooker (the **Story Crucible**) covering world, history, and long-term danger. **Do not dump this in a scene.** Your reader wants *now.* &#x20;
* **A scene** = a **mini-story**: one POV character inside a **Scene Crucible** (immediate danger **right here, right now**) that lasts exactly one scene and then **breaks**. Include only the backstory/world details absolutely needed to make *this* scene intelligible.  &#x20;

### A2) Two legal scene shapes (you must pick one)

* **Proactive scene** = **Goal → Conflict → Setback (usually) or Victory (sometimes)**. It runs on attempts and obstacles; when you run out of obstacles, end the scene. &#x20;
* **Reactive scene** = **Reaction → Dilemma → Decision**. Emotional reaction, then think through only-bad options, then make a least-bad **firm** decision that seeds the next Goal. &#x20;

### A3) POV, viewpoint, tense — choose once per scene

* Pick **one** POV character; choose viewpoint (first, second, third, third-objective, head-hopping, omniscient) and choose tense (past, present, **or** future). The scene’s emotions are measured through the POV and through effects on the *story’s protagonist*.  &#x20;

> **Broken scene test:** If you can’t write a one-to-two-sentence **Scene Crucible** (what threatens the POV *now*), the scene is broken. Don’t proceed.&#x20;

---

# PART B — Product in Steps (Do this in order, every time)

Each step includes: **WHAT** (action), **WHY** (grounded in source), **HOW** (implementation), **VERIFY** (pass/fail), **IF FAIL** (fix). Use the data structures and prompts in Part C.

---

## STEP 0 — Import upstream context & set the scene envelope

**WHAT:** Load upstream info (previous scene’s **Outcome**, next scene hook, project style), then collect scene parameters:

* `scene_type` (proactive|reactive), `pov_character`, `viewpoint`, `tense`, `place`, `time`, and a draft **crucible facts** list (immediate dangers).
  **WHY:** Every scene needs exactly one POV/tense and a **Scene Crucible** framed in the present. &#x20;
  **HOW:** Create a *Scene Card* (see schema in Step 12).
  **VERIFY:** POV chosen; viewpoint + tense chosen; crucible facts exist.
  **IF FAIL:** Stop. Write a one-sentence **Scene Crucible** (“right here, right now … danger”) or you have a broken scene.&#x20;

---

## STEP 1 — Choose the legal **scene shape**

**WHAT:** Decide **Proactive** vs **Reactive**.
**WHY:** Only two valid shapes. Proactive uses attempts→obstacles; Reactive processes the last Setback and commits to a next action.&#x20;
**HOW:**

* If previous scene ended in **Setback**, you’ll typically write a **Reactive** scene next—or summarize/skip it if pacing demands.&#x20;
* If you already have a clear, time-bounded **Goal**, choose **Proactive**.
  **VERIFY:** `scene_type` set to `proactive` or `reactive`.
  **IF FAIL:** Re-read previous Outcome; if you can’t justify Reactive (or choose to skip), move to Proactive.

---

## STEP 2 — Declare the **Scene Crucible** (one to two sentences)

**WHAT:** Write a present-tense description of the **immediate danger** that traps the POV character *now*.
**WHY:** Readers want *now*; do **not** dump Story Crucible/world/backstory. Include only what’s needed for this scene to make sense.&#x20;
**HOW:** Template: “**Here & now** at `<place>` in `<time>`, `<POV>` faces `<immediate danger>`; if they fail/quit, `<immediate cost>`.”
**VERIFY:** Mentions current place/time/danger; no history lesson.
**IF FAIL:** Cut backstory; add only the minimum legal context to understand this scene.&#x20;

---

## STEP 3 — **Proactive**: Craft a **Goal** that passes 5/5 rules

**WHAT:** Write one sentence for the **Goal** that is:

1. fits the **time** available; 2) **possible**; 3) **difficult**; 4) fits the **POV** (Values/Ambition/Story Goal); 5) **concrete & objective**.&#x20;
   **WHY:** These are the exact criteria for a dynamite Goal.&#x20;
   **HOW (example):** “Reach the radio room before the patrol cycles back” *(fits a few minutes; doable but hard; photo-verifiable).*
   **VERIFY:** Mark each criterion true/false.
   **IF FAIL:** Shrink scope (time), ground in capability (possible), raise stakes (difficult), align to character doctrine (fits POV), rewrite to be observable/actionable (concrete/objective).&#x20;

---

## STEP 4 — **Proactive**: Build the **Conflict** ladder (escalation only)

**WHAT:** List the POV’s attempts and obstacles as an ordered sequence that **raises tension**; when you run out of obstacles, **end the scene**.&#x20;
**WHY:** Conflict = attempts→obstacles, rising tension—this is non-negotiable.&#x20;
**HOW (example ladder):**

1. Locked service door → 2) Keys missing → 3) Footsteps approach → 4) Patrol appears.
   **VERIFY:** Each step is harder than the last.
   **IF FAIL:** Replace plateaued obstacle with a strictly tougher one, or *end the scene now* (legal per method).&#x20;

---

## STEP 5 — **Proactive**: Choose the **Outcome** (default **Setback**; allow **Victory** rarely)

**WHAT:** Resolve with **Setback** (default) or **Victory** (acceptable when Setback is impossible; prefer **mixed Victory**). **Outcome is judged against the *protagonist’s* desire**, not the current POV (e.g., villain-POV winning = Setback for protagonist). &#x20;
**WHY:** Exact outcome policy from the source.&#x20;
**HOW:** Pick `setback | victory | mixed`, add one-line rationale.
**VERIFY:** If Victory, log why Setback is impossible and show tradeoff (mixed).
**IF FAIL:** Convert to Setback or mixed Victory based on protagonist-polarity.&#x20;

---

## STEP 6 — **Reactive**: Write the **Reaction** (emotion first)

**WHAT:** Summarize the POV’s **emotional** Reaction to the prior Setback at a natural speed—neither robotic nor wallowing. It must match personality, values, ambition, and be **proportional** to the hurt. &#x20;
**WHY:** Reaction is the emotive processing phase; source stresses proportionality and character alignment.&#x20;
**HOW:** 1–2 paragraphs, visceral language anchored in POV.
**VERIFY:** Emotion reads true to character; intensity ≈ preceding Setback.
**IF FAIL:** Adjust intensity up/down; swap generic emotion for character-specific tells.&#x20;

---

## STEP 7 — **Reactive**: Construct the **Dilemma** (only bad options)

**WHAT:** Let the POV consider **several options**, all **bad**; possibly get advice they must convince themselves of; possibly do busywork while the subconscious works—still a **Dilemma**.&#x20;
**WHY:** The Dilemma is intellectual analysis of least-bad choices.&#x20;
**HOW:** List 3–5 options; annotate why each is bad.
**VERIFY:** There is **no “obviously good”** option.
**IF FAIL:** Rewrite options until all carry credible costs.

---

## STEP 8 — **Reactive**: Make the **Decision** (least-bad, forcing, firm, risk-aware)

**WHAT:** Choose the least-bad option; **commit** (scene ends on commitment). Prefer a **forcing move** that constrains the opponent; acknowledge risk; create a **good next Goal** for a future Proactive scene. &#x20;
**WHY:** Readers admire decisiveness; Decision ends the scene and **chains** into the next scene’s **Goal**. &#x20;
**HOW:** One paragraph: “I will `<action>` because `<reason>` despite `<risk>`.”
**VERIFY:** The Decision is **firm**; record `next_goal_stub`.
**IF FAIL:** Add explicit commitment and risk acknowledgement; ensure it makes a good future **Goal**.&#x20;

---

## STEP 9 — Decide **Reactive compression** (full / summarized / skip)

**WHAT:** Choose how much to show of a Reactive scene.
**WHY:** Modern trend: **fewer** full Reactive scenes to keep pace brisk. You may **show** (full), **tell briefly** (summary), or **skip**; but you must still know Reaction, Dilemma, Decision internally. &#x20;
**HOW:** Set `compression = full | summarized | skip` and still store the triad.
**VERIFY:** If not `full`, ensure Decision and `next_goal_stub` are recorded.
**IF FAIL:** Add the Decision explicitly even if summarized.

---

## STEP 10 — Exposition budget (**now or never** rule)

**WHAT:** Check that you’ve only included information the reader needs **right here, right now** to understand this scene (place, time, local law/geography, etc.).&#x20;
**WHY:** Resist explaining the Story Crucible/world history here.&#x20;
**HOW:** Annotate `exposition_used[]` with a one-line “why needed now.”
**VERIFY:** No backstory tangents; each item is tied to current comprehension.
**IF FAIL:** Cut or move info to a place where it becomes *currently necessary*.

---

## STEP 11 — Write the **prose** from the approved plan

**WHAT:** Generate the scene text in the chosen POV/tense, preserving **part order** (G-C-S/V or R-D-D), honoring the Scene Crucible, and closing on Setback/Victory **or** firm Decision.
**WHY:** A scene is a **mini-story** designed to give the reader a **powerful emotional experience**; order and closure matter. &#x20;
**HOW:** The writer/LLM cannot reorder parts or invent new ones.
**VERIFY:** Part markers extract cleanly from prose (see Step 13).
**IF FAIL:** Regenerate from the plan without changing structure.

---

## STEP 12 — Store the **Scene Card** (canonical metadata)

**WHAT:** Persist the plan + validations for auditing/exports.
**Schema (JSON)**

```json
{
  "scene_type": "proactive|reactive",
  "pov": "string",
  "viewpoint": "first|second|third|third_objective|head_hopping|omniscient",
  "tense": "past|present|future",
  "scene_crucible": "1-2 sentences (danger now)",
  "place": "string", "time": "string",
  "proactive": {
    "goal": { "text": "", "fits_time": true, "possible": true, "difficult": true,
              "fits_pov": true, "concrete_objective": true },
    "conflict_obstacles": [{"try":1,"obstacle":""}, {"try":2,"obstacle":""}],
    "outcome": {"type": "setback|victory|mixed", "rationale": ""}
  },
  "reactive": {
    "reaction": "string",
    "dilemma_options": [{"option":"", "why_bad":""}],
    "decision": "string",
    "next_goal_stub": "string",
    "compression": "full|summarized|skip"
  },
  "exposition_used": ["each item is needed now because ..."],
  "chain_link": "decision→next goal OR setback→next reactive seed"
}
```

(Fields and rules map 1:1 to the source.)    &#x20;

---

## STEP 13 — Validate (deterministic checks)

**What we check (and why):**

* **Crucible present & “now”:** Current place/time/danger; no Story-Crucible dump. **Fail if missing** (scene is broken). &#x20;
* **Proactive Goal 5/5:** time-fit, possible, difficult, fits POV doctrine, concrete/objective.&#x20;
* **Conflict escalates:** attempts meet harder obstacles; end when out.&#x20;
* **Outcome policy:** default Setback; Victory allowed but prefer mixed; polarity measured against *protagonist*.&#x20;
* **Reactive triad:** emotive Reaction (proportional); Dilemma of only bad options; Decision least-bad, forcing, firm, risk acknowledged; produces `next_goal_stub`. &#x20;
* **Compression:** If summarized/skipped, still store Reaction/Dilemma/Decision internally.&#x20;

**If any check fails →** go to Step 14 (Triage).

---

## STEP 14 — Triage (Yes / No / Maybe) and **Redesign loop**

**WHAT:** Judge each drafted scene:

* **YES:** Design is strong; keep (minor tweaks later).
* **NO:** Doesn’t fit, has no crucible, or isn’t a story → delete.
* **MAYBE:** Follow the **prescribed redesign**: choose correct type; write the correct parts (G-C-S/V or R-D-D); decide whether a full Reactive is needed or should be summarized/skipped; specify target reader emotion; rewrite; re-triage.&#x20;
  **WHY:** This is Ingermanson’s explicit editing protocol for scenes (second draft). &#x20;
  **VERIFY:** Triage verdict recorded; if Maybe, redesign checklist completed; re-validate.

---

## STEP 15 — Chain to adjacent scenes (hard requirement)

**WHAT:** If scene is **Reactive**, its **Decision** becomes next **Proactive Goal**. If **Proactive**, the **Setback** seeds the next Reactive scene (or its summary/skip).&#x20;
**EXAMPLE (from the book):** A tiny Reactive scene ends with **pepper-spray Decision**, which starts the next Proactive Goal immediately.&#x20;
**VERIFY:** `chain_link` is populated and consistent; next scene imports it.

---

# PART C — Concrete Examples (worked end-to-end)

## C1) **Proactive example** (from Ingermanson’s Snowflake novel)

**Context:** Dirk parachutes behind enemy lines.
**Goal:** “Parachute into France and hole up for the night.” *(time-fit, possible, difficult, concrete)*.&#x20;
**Conflict (obstacles):** anti-aircraft fire; German fighter; engine catches fire; Dirk jumps; plane explodes (others die).&#x20;
**Outcome:** **Setback** — Dirk breaks his leg and passes out.&#x20;
**Why legal:** G-C-S order; escalating obstacles; default Setback.
**How to encode (Scene Card):**

```json
{
  "scene_type": "proactive",
  "pov": "Dirk",
  "scene_crucible": "Night drop in occupied France; survival now or capture.",
  "proactive": {
    "goal": {"text":"Hole up for the night after drop","fits_time":true,"possible":true,"difficult":true,"fits_pov":true,"concrete_objective":true},
    "conflict_obstacles":[
      {"try":1,"obstacle":"AA fire"},
      {"try":2,"obstacle":"German fighter"},
      {"try":3,"obstacle":"Engine fire / forced jump"}
    ],
    "outcome":{"type":"setback","rationale":"Breaks leg; unconscious"}
  },
  "chain_link":"setback→Elise hears something (seed for Reactive)"
}
```

---

## C2) **Reactive example** (from Ingermanson’s Snowflake novel)

**Situation:** Goldilocks cornered by Tiny Pig after previous Setback.
**Reaction:** Emotive fear/urgency.&#x20;
**Dilemma options:**

1. Try to slip past (blocked) → fails.&#x20;
2. Back away and use phone → fails (drops it).&#x20;
3. (Busy action) … no luck.
4. **Pepper spray** considered, then—
   **Decision:** **Pepper-spray** (least-bad, **forcing**, **firm**); ends scene. **Chains** into next Proactive Goal immediately. &#x20;

**Encoding:**

```json
{
  "scene_type": "reactive",
  "pov": "Goldilocks",
  "scene_crucible": "Cornered now; if she hesitates, she’s overpowered.",
  "reactive": {
    "reaction":"Adrenaline spike; fear; resolve hardening.",
    "dilemma_options":[
      {"option":"Slip past","why_bad":"Blocked; high risk"},
      {"option":"Call for help","why_bad":"No time; drops phone"},
      {"option":"Wait him out","why_bad":"He advances; cornered"},
      {"option":"Pepper spray","why_bad":"Escalates risk, but creates space"}
    ],
    "decision":"Use pepper spray now despite risk (forcing move)",
    "next_goal_stub":"Escape the corridor before backup arrives",
    "compression":"full"
  },
  "chain_link":"decision→next proactive goal"
}
```

---

# PART D — APIs, Prompts, and Operations

## D1) Generation pipeline (services and prompts)

1. **Planner**

   * **Proactive prompt:** “Write a scene plan with **Goal (5/5 checks)**, 3–6 escalating **obstacles**, and **Outcome** per policy; include 1–2 sentence **Scene Crucible (now-danger)**.”   &#x20;
   * **Reactive prompt:** “Write **Reaction** (emotive, proportional), **Dilemma** (multiple bad options, advice/busywork allowed), **Decision** (least-bad, forcing, firm, risk-aware) + **next\_goal\_stub**.”&#x20;
2. **Validator** (extractive) — run Step-13 checks.
3. **Drafter** — render prose strictly in plan order.
4. **Triage** — run Step-14; auto-redesign for “Maybe”.&#x20;

## D2) Public API (example)

* `POST /scene/plan` → returns Scene Card + validation.
* `POST /scene/draft` → inputs Scene Card id → prose text.
* `POST /scene/triage` → returns {yes|no|maybe} + redesign steps.
* `GET /scene/:id` → Scene Card + chain link.
  (Contracts exactly mirror the schema in Step 12.)

---

# PART E — Verification & QA

## E1) Automated validators (map to sources)

* **CrucibleNowCheck** (must exist; not Story dump).&#x20;
* **GoalFiveCheck** (5/5).&#x20;
* **ConflictEscalationCheck** (strictly rising; end when out).&#x20;
* **OutcomePolarityCheck** (default Setback; Victory rare/mixed; measured vs protagonist).&#x20;
* **ReactiveTriadCheck** (Reaction proportional; Dilemma all bad; Decision least-bad, forcing, firm, risk ack; has next\_goal\_stub).&#x20;
* **CompressionIntegrityCheck** (if summarized/skipped, triad still recorded).&#x20;

## E2) Human triage (editor pass)

* **YES/NO/MAYBE** with the exact battlefield triage metaphor and the **fix-the-Maybe** loop.&#x20;

---

# PART F — Before/After (what changes with this engine)

**Before (broken):** Meandering text, no clear Goal, random obstacles, convenient win/lose, or pages of backstory/world.
**After (working):**

* Proactive: **one** observable Goal → escalating obstacles → Setback/mixed Victory. &#x20;
* Reactive: visceral Reaction → genuine **Dilemma** (all bad) → **Decision** (firm) → **next Goal**. &#x20;
* Exposition constrained to *now*.&#x20;

---

# PART G — Edge cases (and the source-approved answers)

* **Villain POV winning** still counts as a **Setback** if it harms the *protagonist* (judge polarity by protagonist desire).&#x20;
* **Reactive pacing:** Summarize or skip **legally**; still store Reaction/Dilemma/Decision.&#x20;
* **Run out of obstacles:** End the Proactive scene (don’t pad).&#x20;
* **Broken scene:** If you can’t state the Scene Crucible, redesign from Step 2 before drafting.&#x20;

---

# PART H — Deliverables & Definition of Done

**Deliverables**

1. **Planner**, **Validator**, **Drafter**, **Triage** services with tests.
2. **Scene Card JSON** + **Prose** + **Chain link** persisted.
3. Prompt pack (Proactive, Reactive, Validator, Triage).
4. Demo scenes implemented from the two **book** examples above (Dirk parachute; Goldilocks pepper spray). &#x20;

**Definition of Done (all must pass)**

* Scene type is **legal** and parts appear in order.&#x20;
* **Crucible (now)** present; no Story-dump.&#x20;
* **Proactive**: Goal passes 5/5; conflict escalates; outcome policy satisfied. &#x20;
* **Reactive**: Reaction/Dilemma/Decision meet exact rules; Decision yields `next_goal_stub`.&#x20;
* **Chain link** present and imported by the next scene.&#x20;
* Triage verdict recorded; “Maybe” scenes looped through redesign per protocol.&#x20;

---

## Appendix — Quick reference tables (from source)

**How to create a dynamite Goal (must pass all):** fits time; possible; difficult; fits POV; concrete & objective.&#x20;
**Conflict:** attempts → obstacles; tension rises; end when out.&#x20;
**Setback:** defeat for the **protagonist** (not necessarily POV). Victory allowed (prefer **mixed**).&#x20;
**Reaction:** emotional, personality-true, aligned to Values/Ambition/Story Goal, proportional to Setback.&#x20;
**Dilemma:** several options, **all bad**; advice/busywork patterns allowed.&#x20;
**Decision:** least-bad; **forcing move**; makes a good future Goal; risks acknowledged; **firm commitment**; scene ends.&#x20;
**Reactive compression:** full / summarized / skip (but always know/store R-D-D).&#x20;
**Chaining:** Decision ⇒ next Goal (explicit).&#x20;

---

### Final word

This ZAD PRD encodes the method **exactly as written**—structure, allowed shapes, goal/obstacle/outcome logic, reactive processing, exposition limits, triage, and chaining—all with one-click validations and reproducible Scene Cards. A developer with no background in Randy or Snowflake can implement this by following **Steps 0–15** and the schemas herein.
