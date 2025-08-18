# CLAUDE OPERATIONS MANUAL — Auto-Novel Snowflake Engine

NOTE: Always refer to How to Write a Novel Using the Snowflake Method - PDF Room and how-to-write-a-dynamite-scene-using-the-snowflake-method-2. They are the single sources of truth regarding the strategy. Never hallucinate, never assume, never make shit up. Always check first. 

## Scope

This manual defines how to operate, extend, and troubleshoot the Auto-Novel Snowflake Engine that generates complete novels end to end using the Snowflake Method. It standardizes step gates, prompt packs, validation, error cycles, and export protocols.

---

## System overview

Auto-Novel consumes a minimal brief and returns a full draft. It performs each Snowflake step in order, saves every artifact, validates conformance, and only then proceeds. It never drafts prose that is not traceable to a prior artifact.

Pipeline tiers:

1. Planner: Steps 0 to 4
2. Character Engine: Steps 3, 5, 7
3. Outline Engine: Steps 6 and 8
4. Scene Logic: Step 9
5. Draft Writer: Step 10
6. Conformance Validator: persistent at every gate

Artifacts are stored as JSON with human readable mirrors.

---

## Mandatory methodology

Never bypass or merge Snowflake steps. Never “jump ahead.” Every downstream change can only come from a revision to its upstream artifact and must be re-validated.

When debugging or extending:

1. Always begin from the current core codebase and the latest project schema.
2. If a task passes tests, reset the cycle counter to zero.
3. If an error occurs, start an Error Cycle:

   1. Use TaskMaster to research the specific failure mode.
   2. Use Context7 to load SDK docs, file format specs, MCP parameters.
   3. Apply the fix and retest.
   4. Increment the cycle counter and log what changed.
4. After twenty failed cycles for a unique error, mark as Blocked and escalate with reproducible evidence.

Never create “simplified” throwaway pipelines. Fix the real system.

---

## Session startup checklist

1. Confirm branch is synced with main.
2. Load environment variables:
   • `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
   • `VECTOR_DB_URL` if using RAG for internal canon retrieval
   • `FILES_BUCKET_URL` and credentials for artifact storage
3. Run smoke tests:
   • Model reachability
   • JSON schema validation for all artifacts
   • Step to step handoffs on a tiny sample project
4. Open TaskMaster and load the Snowflake task list.
5. Review all items that are Blocked.

---

## TaskMaster integration

Core commands:

```bash
task-master init
task-master parse-prd docs/prd.md --research
task-master list
task-master next
task-master show <id>
task-master set-status --id=<id> --status=done
task-master research "Step 9 brief missing Conflict field"
task-master research "EPUB export fails on images in front matter"
```

All technical research is initiated via TaskMaster. Record findings and link to the fix in the cycle log.

---

## Context7 integration

Use Context7 to retrieve:

• Claude Code MCP parameters and examples
• File format specs for DOCX and EPUB export
• JSON Schema snippets for artifacts
• Vector store function signatures

Connect Claude Code to Context7:

```
claude mcp add --transport http context7 https://mcp.context7.com/mcp
```

Or SSE:

```
claude mcp add --transport sse context7 https://mcp.context7.com/sse
```

Local:

```
claude mcp add context7 -- npx -y @upstash/context7-mcp
```

---

## Development rules

1. Snowflake fidelity is absolute. Steps 0 through 10 are distinct and ordered.
2. No prose generation may occur before Step 10.
3. Each scene must be Proactive or Reactive and must pass its triad checks before drafting.
4. The draft uses only the frozen scene list and scene briefs.
5. Do not hardcode secrets. Use environment variables.
6. All outputs must pass schema validation.
7. Always test with a minimal seed before a full run.
8. Keep prompts and validators versioned. Record the step hash in every artifact.

---

## Artifacts and formats

Project bundle:

• `project.json` top level fields
• `step_0_first_things_first.json`
• `step_1_logline.json`
• `step_2_one_paragraph.json` and `moral_premise.json`
• `step_3_character_summaries.json`
• `step_4_one_page_synopsis.md`
• `step_5_character_synopses.json`
• `step_6_long_synopsis.md`
• `step_7_character_bibles.json`
• `step_8_scenes.csv` and `step_8_scenes.json`
• `step_9_scene_briefs.jsonl`
• `step_10_manuscript.md`, `manuscript.docx`, `manuscript.epub`

Scene CSV required columns:

`index, chapter_hint, type, pov, summary, time, location, word_target, status, inbound_hook, outbound_hook`

---

## Step gates and acceptance checks

Step 0 First Things First
• Required: `category`, `target_audience`, `story_kind`, `delight_statement`
• Gate: all present and within length limits

Step 1 One sentence summary
• Required: at most twenty five words, no more than two named leads, no ending revealed
• Gate: token count and named entity limit pass

Step 2 One paragraph summary
• Required: five sentences mapping setup, Disaster 1, Disaster 2, Disaster 3, ending
• Required: a single sentence moral premise
• Gate: disasters detected and moral premise aligns with Disaster 2

Step 3 Character summaries
• Required per character: role, name, goal, conflict, epiphany, a one-line arc, a one-paragraph arc
• Gate: all fields present, no duplicates of role for principals unless specified

Step 4 One page synopsis
• Required: each Step 2 sentence expanded to a paragraph
• Gate: paragraph to sentence mapping intact

Step 5 Character synopses
• Required: half to one page each, with backstory, plot role, psychology, special attention to the antagonist
• Gate: antagonist interiority present

Step 6 Long synopsis
• Required: four to five pages, each Step 4 paragraph expanded to about one page
• Gate: mapping intact, no new story beats that break prior steps without an upstream revision

Step 7 Character bibles
• Required groups: physical, personality, environment, psychological
• Gate: each principal has at least eighty percent of fields filled

Step 8 Scene list
• Required: one row per planned scene, includes POV and summary
• Gate: conflict flag present for every row and at least three scene rows anchor the three disasters

Step 9 Scene briefs
• Required for Proactive: Goal, Conflict, Setback
• Required for Reactive: Reaction, Dilemma, Decision
• Gate: triads non-empty, stakes stated, linked to character goals or disaster chain

Step 10 First draft
• Required: each scene drafted in order from the frozen list
• Gate: chapter assembly complete, no orphan scenes, exports compile

---

## Prompt pack blueprint

Each step uses a canonical prompt. Prompts always include:

• Step name and objective
• The relevant upstream artifacts as locked context
• The acceptance checks for that step, written as checklist items
• A refusal clause that blocks generation if upstream is missing or invalid

Skeleton example for Step 9 Scene brief, Proactive:

```
System:
You are the Scene Logic agent for the Snowflake Engine. Only produce a Proactive brief that passes the triad checks.

User:
Context:
- Character summaries: {{json: step_3_character_summaries}}
- Long synopsis: {{md: step_6_long_synopsis}}
- Scene row: {{json: step_8_scene_row}}

Task:
Write a Proactive brief with Goal, Conflict, Setback.
Enforce:
- Goal is explicit and time bound
- Conflict is credible and opposes the Goal
- Setback changes the situation and increases stakes
Return JSON:
{ "goal": "...", "conflict": "...", "setback": "...", "stakes": "...", "links": { "character_goal_id": "...", "disaster_anchor": 1|2|3 } }
```

All prompts have sibling validators that mirror the checklist.

---

## Validators

Implement deterministic functions for each gate. Examples:

• `validate_logline(text)`
• `validate_paragraph_structure(text)` checks count and labels
• `validate_character_summary(obj)`
• `validate_scene_row(row)` ensures POV and conflict flags
• `validate_brief_proactive(obj)` checks triad and stakes
• `validate_brief_reactive(obj)` checks triad and turning decision

Validators return a pass or a list of exact failures that the agent must fix.

---

## Drafting rules

• Draft only from the scene brief and the frozen scene list.
• Keep the scene goal explicit, conflict on the page, and stakes rising.
• Respect POV as declared in the row.
• Alternate action and reflection with Scene versus Sequel rhythm where appropriate.
• No filler scenes. Every scene must change the state meaningfully.

---

## Error recovery workflow

When an error occurs:

1. Identify the failing tier: Planner, Character, Outline, Scene, Draft, Export.
2. Start a fix cycle: research with TaskMaster, reference with Context7, apply the patch, retest.
3. Log the cycle number and the hypothesis.
4. If fixed, reset the counter.
5. After twenty cycles without resolution, escalate as Blocked with a minimal reproducible project and artifact bundle.

---

## Escalation triggers

• Persistent model refusal to follow triad constraints
• Repeated invalid scene rows or briefs after regeneration
• Exporters that cannot produce valid DOCX or EPUB from a known good manuscript
• Schema migrations that break persisted bundles

---

## QA and benchmarks

Automated:

• Run the full step chain on a seed project and assert all gates pass
• Validate that Step 10 manuscript word count is within five percent of target
• Ensure disaster anchors resolve to at least one scene each
• Verify EPUB and DOCX with external validators

Manual:

• Structural review for disaster placement, moral premise echo, POV balance
• Scene spot checks for goal and conflict clarity

---

## Security and privacy

All content is private. Encrypt at rest and in transit. Keep per tenant isolation. Prompts and artifacts remain within the project scope and are not used for training.

---

## Build and run

Local smoke test:

```bash
make setup
make test:smoke
make run:tiny  # generates a 3 chapter micro project for pipeline verification
```

Full generation:

```bash
make run:novel PROJECT=seed_rom_suspense TARGET_WORDS=90000
```

Exports:

```bash
make export:csv
make export:docx
make export:epub
```

---

## Task Master AI instructions

Import Task Master development workflow commands and guidelines. Treat the import as if it is part of this manual.

`@./.taskmaster/CLAUDE.md`

---

## Appendix A. JSON schemas

Provide machine readable JSON Schema files in `schemas/` for:

• `project.json`
• `character.summary.json` and `character.bible.json`
• `synopsis.one_page.json` and `synopsis.long.json`
• `scene.row.json`
• `scene.brief.proactive.json` and `scene.brief.reactive.json`
• `manuscript.json`

---

## Appendix B. Naming and versioning

• All artifacts include `project_id`, `step`, `version`, `created_at`, `hash_upstream`.
• Regeneration creates a new version and preserves the previous artifact.
• The Draft Writer reads only artifacts with the same upstream hash to guarantee traceability.

---

## Appendix C. Reproducibility

• Deterministic seeds per step
• Temperature and sampling ranges locked per tier
• Record the model name, prompt hash, and validator version with every artifact

---

This manual must be followed exactly for all work on the Auto-Novel Snowflake Engine.

- NEVER RUN PARSE-PRD AND RESEARCH IN THE SAME COMMAND WITH TASKMASTER, NEVER NEVER NEVER
- Don't say the project is ready until it's fully E2E tested and working from start to finish and succeeding with the core mandate.