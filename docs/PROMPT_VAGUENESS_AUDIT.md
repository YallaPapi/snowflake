# Save the Cat Prompt Vagueness Audit
**Generated:** 2026-02-10
**Purpose:** Identify where each prompt falls short of Blake Snyder's methodology

---

## STEP 1: LOGLINE (step_1_prompt.py)

### What the prompt tells GPT to do
- Generate a logline with irony, mental picture, audience/cost, killer title
- Follow Blake Snyder's 4 requirements from Chapter 1
- Output a structured JSON with logline, title, ironic_element, hero_adjective, character_type, time_frame, story_beginning/ending, target_audience, budget_tier, genre_tone, poster_concept, high_concept_score

### What's MISSING

**1. The Jealousy Test (Ch.1)**
- Prompt mentions it (line 100) but doesn't explain HOW to apply it
- Missing: "When another writer reads your logline, their reaction should be 'Why didn't I think of that!'" — what makes a logline jealousy-inducing? The prompt never breaks this down into actionable criteria

**2. The Stasis = Death Opening (Ch.1)**
- Snyder's formula: "On the verge of [stasis=death], a [adjective] [hero] must [action] before [time limit]"
- The prompt asks for a "time_frame" but doesn't explain the "stasis=death" opening — that the hero's starting position must be shown as unsustainable

**3. Logline Sentence Structure Guidance**
- Prompt gives examples but doesn't teach the PATTERN: adjective + character type + ironic situation + goal + obstacle + time frame
- Missing: explicit instruction on how to ORDER these elements in the sentence

**4. What "High Concept" Actually Means**
- Prompt says "high concept — easy to see from the logline and poster alone" but doesn't define the mechanics
- Missing: Snyder's criterion that 50% of box office comes from international markets where concept must travel WITHOUT explanation — this is WHY high concept matters
- Missing: The "poster test" is mentioned but not explained as a LITMUS TEST — if you can't imagine the poster from the logline, the concept isn't high enough

**5. "Compelling Mental Picture" Breakdown**
- Prompt says the logline must "bloom in your mind" but doesn't explain WHAT must bloom
- Missing: You should see WHERE the story begins, WHERE it ends, WHAT the journey looks like, WHO the characters are, and WHEN it all happens — all from the logline alone

**6. Irony vs. Contradiction**
- Prompt defines irony as "an inherent contradiction" but doesn't explain the EMOTIONAL component
- Missing: Snyder says irony must be "emotionally intriguing, like an itch you have to scratch" — it's not just intellectual contradiction, it's EMOTIONAL tension

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 43-46 | "The logline MUST contain an inherent contradiction" | MEDIUM | Doesn't explain what makes a contradiction "inherent" vs. superficial |
| 51-59 | "A good logline must 'bloom in your mind'" | HIGH | "Bloom" is metaphorical — no concrete checklist of what must be visible |
| 62-68 | "Audience and cost — from the logline alone" | MEDIUM | Says WHAT to infer but not HOW to make it inferable |
| 70-77 | "Title MUST have IRONY" | HIGH | Says title needs irony but doesn't explain how title irony differs from logline irony |
| 79-84 | "High concept — easy to see from logline and poster alone" | HIGH | No definition of what "high concept" mechanically means |
| 100-101 | "Jealousy Test: 'Why didn't I think of that!'" | CRITICAL | Mentions the test but gives zero guidance on how to invoke jealousy |

### Example Quality
- Examples are GOOD (Die Hard, Pretty Woman, Blind Date, 4 Christmases, The Retreat, Ride Along)
- All examples include character adjectives, goals, obstacles, time frames
- BUT: Prompt doesn't DISSECT the examples to show WHY they work

### Schema Completeness
- Schema is COMPLETE for Step 1's own outputs
- But missing the "stasis=death" opening position field that downstream steps (Beat Sheet) will need

### Character Voice Instructions
N/A for this step (character voice happens in Step 3/8)

---

## STEP 2: GENRE CLASSIFICATION (step_2_prompt.py)

### What the prompt tells GPT to do
- Classify story into one of Blake Snyder's 10 structural genres
- Identify ALL required working parts for the chosen genre
- List structural rules and constraints
- State the core question the genre asks
- Identify the "twist" (what makes this story different from others in the genre)
- List audience conventions and expectations
- Provide a runner-up genre and explain why it was eliminated
- List 3-5 comparable films in the same genre

### What's MISSING

**1. Genre Working Parts Are Severely Underspecified**
- Per ch2_genre_audit.txt: **42 working parts MISSING** across all 10 genres
- Example (Monster in the House):
  - Prompt says: "Sin invites a monster into an INESCAPABLE space; structure is run and hide"
  - Book says: Sin (greed/carnal) → monster creation → monster as avenging angel → kills sinners, spares those who realize the sin → trapped victims desperate to kill monster → no escape
  - ENGINE MISSING: trapped_victims, no-escape constraint, monster must be sufficiently powerful/supernatural, sin causally linked to monster creation, monster spares the righteous
- This applies to ALL 10 genres — the prompt gives 1-sentence summaries where the book gives 5-10 structural elements per genre

**2. Sub-Types Barely Explained**
- Prompt mentions "Out of the Bottle has wish-fulfillment vs. comeuppance" (line 59)
- Missing: WHAT makes each sub-type structurally different
  - Wish-fulfillment: underdog Cinderella → magic wish granted → learns magic isn't everything
  - Comeuppance: jerk → curse (presented as magic) → learns lesson, redeemed
  - The prompt doesn't explain these ARCS or how to identify which sub-type a story is

**3. Genre "Twist" Instruction Is Too Vague**
- Prompt (line 55): "Identify the 'twist' — what makes this story 'the same thing, only different' from other films in this genre. Reference a SPECIFIC convention you are subverting."
- Missing: HOW to identify a convention worth subverting
- Missing: Snyder's method — "You can be near the cliché, you can dance around it, you can run right up to it and almost embrace it. But at the last second you must turn away." The prompt doesn't teach this "dance with cliché" technique

**4. Borderline Cases Not Explained**
- Prompt says "When in doubt, ask: what is the STRUCTURAL ENGINE of this story?" (line 35)
- But doesn't explain WHAT a "structural engine" is or HOW to identify it
- Book gives borderline examples (Breakfast Club: Rites of Passage NOT Institutionalized; Rain Man: Buddy Love NOT Golden Fleece) and explains WHY — prompt just mentions they exist

**5. Comparable Films Lineage**
- Prompt asks for 3-5 comparable films (line 87-91)
- Missing: Snyder's "what movie begat what" concept — you must know the LINEAGE, the family tree of your genre, to know where your story fits

**6. No Guidance on How to Use Genre for Writing**
- Prompt asks GPT to classify the genre but doesn't explain WHY the writer needs to know this
- Missing: "When you are stuck in your story or when you're preparing to write, you will 'screen' a dozen movies that are like the one you're working on to get clues about why certain plot elements are important" — genre is a TOOL for solving screenplay problems, not just a label

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 51-52 | "Identify ALL required working parts" | CRITICAL | Working parts are barely defined in the prompt — GPT has no reference for what "ALL" means |
| 53 | "List the genre's structural rules and constraints that this screenplay must follow" | CRITICAL | Rules are 1-sentence summaries; book has 5-10 rules per genre |
| 55-56 | "Identify the 'twist' — what SPECIFIC convention you are subverting" | HIGH | Doesn't explain how to identify conventions or what makes a twist effective |
| 59 | "If the genre has sub-types, identify which sub-type this story is" | HIGH | Sub-types mentioned but not explained structurally |
| 35 | "What is the STRUCTURAL ENGINE of this story?" | CRITICAL | "Structural engine" undefined — no method for identifying it |

### Example Quality
- Examples are PRESENT (Jaws, Alien, Star Wars, Wizard of Oz, Liar Liar, Bruce Almighty, Die Hard, Titanic)
- But examples are NOT DISSECTED — prompt doesn't explain WHY each example fits its genre
- Missing: Counter-examples (Arachnophobia as a FAILED Monster in the House)

### Schema Completeness
- Schema is INCOMPLETE
- Missing: sub_type_justification (why this sub-type and not the other)
- Missing: structural_engine_description (what makes this genre fit structurally)
- Missing: cliche_inventory (what are the genre clichés you're avoiding)

### Character Voice Instructions
N/A for this step

---

## STEP 3: HERO CONSTRUCTION (step_3_prompt.py)

### What the prompt tells GPT to do
- Build a protagonist following Snyder's 3 criteria: most conflict, longest journey, most demographically pleasing
- Identify primal motivation (one of 5: survival, hunger, sex, protection of loved ones, fear of death)
- Create "Save the Cat" moment, plant "Six Things That Need Fixing", define Opening State vs. Final State (opposites)
- Explain surface-to-primal connection (how stated goal connects to primal urge)
- Build antagonist (equal/superior power, mirror principle, moral difference)
- Build B-story character (relationship to hero, theme wisdom)

### What's MISSING

**1. Archetype Selection Guidance**
- Prompt lists 10 ActorArchetype values (young_man_on_the_rise, good_girl_tempted, etc.) with NO explanation of what each means
- Missing: Snyder's full archetype catalog from Ch.3 with historical actor lineage
  - "Young man on the rise": Harold Lloyd → Steve Martin → Adam Sandler → Ashton Kutcher (plucky, a little dumb, Horatio Alger-esque)
  - "Sex goddess": Mae West → Marilyn Monroe → Bridget Bardot → Halle Berry
  - "Wounded soldier": Paul Newman → Clint Eastwood (going back for last redemptive mission)
- The prompt expects GPT to SELECT an archetype without teaching WHAT each archetype represents or how they function in stories

**2. "Most Conflict" Criterion Not Operationalized**
- Prompt asks for "maximum_conflict_justification" (line 89-90) but doesn't explain HOW to measure conflict potential
- Missing: Snyder's method — put different character types in the same situation, ask "who would suffer the most?" or "who would face the biggest obstacles?"
- Example from book: Third Grade — who needs to go back to third grade most? A successful businessman who hasn't grown up emotionally, not a random adult

**3. "Longest Journey" Criterion Vague**
- Prompt asks for "longest_journey_justification" (line 91) but doesn't explain what "longest" means
- Missing: The journey is EMOTIONAL DISTANCE from Opening State to Final State
- Missing: "Take A Step Back" diagnostic (from Ch.7) should be referenced here — the hero must start as FAR as possible from who they'll become

**4. "Demographically Pleasing" Criterion Barely Explained**
- Prompt asks for "demographic_appeal_justification" (line 92-93) and says "skew young for mass market appeal" (line 72)
- Missing: Snyder's 4-QUADRANT breakdown (Men Over 25, Men Under 25, Women Over 25, Women Under 25)
- Missing: "This is who shows up for movies" — not about political correctness, about box office reality
- Missing: The "blind spot" warning — Snyder admits he defaults to 40-year-old heroes and has to catch himself

**5. "Save the Cat" Moment Instructions Too General**
- Prompt says: "A specific early scene (at least 20 characters) showing likability through ACTION, not words" (line 95-97)
- Missing: The FUNCTION of the scene — it must make the audience "in sync" with the hero so we root for them to win
- Missing: The anti-hero corollary (from Ch.6 Laws): "When your hero is slightly damaged goods, or even potentially unlikable, make his enemy even more horrible!" (Pulp Fiction: Travolta/Jackson are funny discussing McDonald's before killing someone)

**6. "Six Things That Need Fixing" Origin and Purpose Not Explained**
- Prompt asks for exactly 6 flaws/needs (line 97-98)
- Missing: WHERE do these come from? They're character tics and flaws planted in the Set-Up (Act One, pages 1-10)
- Missing: WHAT happens to them? They're paid off in Act Three — each flaw is mastered or resolved
- Missing: WHY six? Snyder doesn't explain the number, but it's a concrete structural element

**7. Surface-to-Primal Connection Explained But Not Taught**
- Prompt includes Snyder's quote: "if it's a promotion at work, it better damn well be related to winning the hand of X's beloved" (line 33-34, line 87-88)
- But doesn't teach HOW to make that connection transparent
- Missing: The connection must be VISIBLE to the audience, not a backstory secret — the surface goal should OBVIOUSLY link to primal stakes

**8. Primal Relationships Mentioned But Not Enforced**
- Prompt says "Use PRIMAL relationships: husbands/wives, fathers/daughters, mothers/sons" (line 35)
- But this is only mentioned in the SYSTEM_PROMPT — the USER_PROMPT doesn't reinforce it for the B-story character
- Missing: WHY these relationships are primal (Ch.3: "You say 'father' and I see my father. We all have 'em — it gets our attention because we have a primal reaction to those words")

**9. Antagonist "Mirror Principle" Not Explained**
- Prompt asks for "mirror_principle: how they are two halves of the same person" (line 115)
- Missing: WHAT this means structurally — hero and antagonist want the same thing OR have the same flaw expressed differently
- Missing: Examples (Batman/Joker, Die Hard Willis/Rickman, Pretty Woman Gere/Alexander)

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 75-80 | "ARCHETYPE: Must be EXACTLY one of these 10 ActorArchetype values" | CRITICAL | No explanation of what each archetype means or how to select |
| 89 | "Why THIS hero offers the most conflict" | HIGH | No method for measuring conflict potential |
| 91 | "Why THIS hero has the longest emotional distance" | MEDIUM | "Longest" undefined; should reference opening/final state gap |
| 92-93 | "Why THIS hero is most demographically pleasing" | HIGH | Mentions target audience but no 4-quadrant analysis guidance |
| 95-97 | "Save the Cat moment: specific early scene showing likability through ACTION" | MEDIUM | Says WHAT but not HOW to make the audience root for the hero |
| 97-98 | "Six Things That Need Fixing: Exactly 6 flaws" | MEDIUM | No explanation of where they come from or how they're paid off |
| 87-88 | "Surface-to-primal connection" | MEDIUM | Quote included but no instruction on making it transparent |
| 115 | "Mirror principle: two halves of the same person" | HIGH | Metaphorical; no structural explanation |

### Example Quality
- NO EXAMPLES given for archetypes, Save the Cat moments, or mirror principle
- This is a CRITICAL gap — GPT has no models to follow

### Schema Completeness
- Schema is MOSTLY COMPLETE for Step 3's outputs
- Missing: archetype_justification (why this archetype fits the story)
- Missing: save_the_cat_scene_number (which scene in the Set-Up it occurs)

### Character Voice Instructions
N/A for this step (character voice happens in Step 3b/8)

---

## STEP 3b: SUPPORTING CAST (step_3b_prompt.py)

### What the prompt tells GPT to do
- Define ALL supporting characters beyond hero, antagonist, B-story character
- Assign roles: ally, mentor, rival, love_interest, authority, victim, comic_relief, henchman, witness, other
- For each character: relationship to hero, arc summary, distinctive trait, voice profile, first appearance beat
- Minimum 6, maximum 15, typical 8-12 for a feature film

### What's MISSING

**1. Character Role Functions Not Explained**
- Prompt lists 10 role types (ally, mentor, rival, etc.) but doesn't explain WHAT each role DOES in a story
- Missing: Story function definitions
  - Ally: helps hero achieve goal, provides support/resources
  - Mentor: provides wisdom/guidance, often dies at All Is Lost
  - Rival: competes with hero (distinct from antagonist who BLOCKS the goal)
  - Love interest: romantic subplot, often carries theme
  - Authority: gatekeeper, enforces rules
  - Victim: threatened/needs saving, raises stakes
  - Comic relief: provides levity, "booster rocket" between dramatic beats
  - Henchman: serves antagonist, dispatched in ascending order in Finale
  - Witness: observes key events, provides outside perspective

**2. "Distinctive Trait" Instruction Too Vague**
- Prompt (line 71): "ONE memorable trait per 'Limp and Eye Patch' diagnostic (physical, behavioral, or verbal)"
- Missing: EXAMPLES of what makes a trait memorable vs. generic
- Missing: The full "Limp and Eye Patch" principle from Ch.7 — "The reader has to have a visual clue, often a running visual reminder, that makes remembering them easier" (black t-shirt and wispy soul-patch example)

**3. "Voice Profile" Instruction Vague**
- Prompt (line 72): "How they speak differently from everyone else (vocabulary, rhythm, verbal tics)"
- Missing: CONCRETE examples of voice profiles
  - One character stutters
  - One does malapropisms
  - One is an Okie versed in Sartre
  - Alien parents always YELL with at least one word CAPITALIZED (from Snyder's Big Ugly Baby example)

**4. Character Count Guidance Weak**
- Prompt says "MINIMUM: 6, MAXIMUM: 15, TYPICAL: 8-12 for a feature film" (lines 75-77)
- Missing: WHY these numbers — what happens if you have too few (thin world) or too many (confusing, characters blend together)?
- Missing: Snyder's advice from Ch.7 "Hi, How Are You? I'm Fine" — if you can't tell characters apart by covering the names, you have too many OR they're not distinct enough

**5. Arc Summary for Static Characters**
- Prompt allows "arc_summary: empty string if they're static" (line 70)
- But doesn't explain which characters SHOULD be static
- Missing: Snyder's "Covenant of the Arc" (Ch.6 Law 6) — "Every single character in your movie must change EXCEPT the bad guys. Bad guys refuse to change — that's why they lose."

**6. First Appearance Beat Constraint Not Explained**
- Prompt asks for "first_appearance_beat: Which of the 15 beats they first appear in" (line 73)
- Missing: Structural guidance on WHEN to introduce characters
  - Set-Up (Beat 3): A-story characters
  - B Story (Beat 7): B-story characters (new faces, NOT from Act One)
  - Characters introduced in Finale look ad-hoc

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 55-64 | "For each character, provide: role, relationship, arc, distinctive trait, voice profile" | HIGH | Role types listed but not functionally defined |
| 71 | "ONE memorable trait per 'Limp and Eye Patch' diagnostic" | HIGH | Diagnostic mentioned but not explained; no examples |
| 72 | "Voice profile: How they speak differently" | CRITICAL | Says WHAT to provide but no examples of HOW to make voices distinct |
| 75-77 | "MINIMUM: 6, MAXIMUM: 15, TYPICAL: 8-12" | MEDIUM | Numbers given but no explanation of why or consequences of violating |

### Example Quality
- ONE example given (lines 82-90) showing the JSON structure
- But the example uses GENERIC placeholder text ("Character Name", "ally", "Best friend since childhood")
- MISSING: A REAL example with concrete, memorable trait and distinct voice profile

### Schema Completeness
- Schema is COMPLETE for this step
- Fields cover: name, role, relationship, arc, distinctive trait, voice profile, first appearance beat

### Character Voice Instructions
- Present but VAGUE (line 72)
- No examples of what makes a voice profile distinct
- Missing the "Bad Dialogue Test" from Ch.7: "Cover up the names. Can you tell who is speaking?"

---

## STEP 4: BEAT SHEET (step_4_prompt.py)

### What the prompt tells GPT to do
- Generate exactly 15 beats following the Blake Snyder Beat Sheet (BS2)
- Each beat description must be 1-2 sentences MAX
- Follow Thesis/Antithesis/Synthesis three-world framework
- Specify target pages, percentages, act labels, emotional direction
- Map to Snowflake artifacts

### What's MISSING

**1. Polarity Assignment Guidance**
- Prompt says Midpoint must be "FALSE VICTORY (up) or FALSE DEFEAT (down)" and All Is Lost must be the opposite polarity (lines 138-143, 151-157)
- But doesn't explain HOW to decide which polarity to use
- Missing: Snyder's directive — "pick now, it's like nailing a spike into a wall" — this is a CHOICE the writer makes, not an inference
- Missing: "It's never as good as it seems at the Midpoint" / "It's never as bad as it seems at the All Is Lost point" — these are LIES the story tells

**2. Beat 6 "Break into Two" — Proactive Choice Not Explained**
- Prompt says: "MUST be the hero's PROACTIVE CHOICE. 'The Hero cannot be lured, tricked or drift into Act Two.'" (line 119-120)
- Missing: WHAT makes a choice proactive vs. reactive
- Missing: Examples of WRONG ways to do this (hero is lured, tricked, or drifts)

**3. Beat 7 "B Story" — New Characters Not Emphasized**
- Prompt says: "Introduces NEW characters we have not met in Act One" (line 127-128)
- But doesn't explain WHY this is a hard rule
- Missing: Snyder's reasoning — B Story is a "funhouse mirror" of the Thesis world, and NEW faces signal to the audience that we're in the Antithesis now

**4. Beat 8 "Fun and Games" — Trailer Moments**
- Prompt says: "The promise of the premise! The heart of the movie — the core of the poster, where all the trailer moments live" (line 133-135)
- Missing: WHAT makes a scene a "trailer moment"
- Missing: "Forward progress of the story is NOT the primary concern here — stakes won't be raised until the Midpoint" — Fun and Games is about TONE, not PLOT

**5. Beat 11 "All Is Lost" — Whiff of Death**
- Prompt says: "Must contain a 'whiff of death' — literal or symbolic (a death, a flower dying, news of a loss)" (line 153-155)
- Missing: WHY the whiff of death is required — it's the "old world, old character, old way of thinking DIES" (line 155-157)
- Missing: Mentors classically die here "so their students discover they had it in them all along" (line 154)

**6. Beat 12 "Dark Night of the Soul" — Duration Guidance**
- Prompt says: "Can last five seconds or five minutes, but must be there" (line 160)
- Missing: HOW to make this beat feel earned vs. rushed
- Missing: The beat is about the hero yielding control and admitting humility — "Oh Lord, why hast thou forsaken me?" (line 163)

**7. Beat 14 "Finale" — Ascending Order of Bad Guys**
- Prompt says: "Bad guys are dispatched in ascending order: lieutenants and henchmen first, then the Boss" (line 173-174)
- But doesn't explain WHY this order matters
- Missing: Structural logic — you can't defeat the boss before defeating the minions, or the boss looks weak

**8. Beat 15 "Final Image" — Opposite of Opening Image**
- Prompt says: "MUST be the visual OPPOSITE of the Opening Image. If you don't have that Final Image, go back and check your math" (line 179-183)
- Missing: EXAMPLES of opening/final pairs
- Missing: The opposites are PROOF of change — "a plus and a minus, showing change so dramatic it documents the emotional upheaval the movie represents"

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 91-94 | "Opening Image: Sets the tone, mood, and scope. Shows 'before' snapshot." | MEDIUM | Says WHAT but not HOW to choose the image |
| 97-100 | "Theme Stated: Someone OTHER than the hero poses a question or makes a statement" | MEDIUM | Says who states it but not how to identify the theme |
| 108-110 | "Catalyst: A single, definite, life-changing EXTERNAL EVENT. NOT gradual." | LOW | Good — explicit and clear |
| 119-122 | "Break into Two: MUST be hero's PROACTIVE CHOICE" | HIGH | Doesn't explain what makes a choice proactive |
| 127-130 | "B Story: NEW characters, funhouse mirror of Thesis world" | MEDIUM | Says "new" but not why |
| 133-137 | "Fun and Games: The promise of the premise! Trailer moments." | HIGH | "Trailer moments" undefined |
| 138-143 | "Midpoint: FALSE VICTORY (up) or FALSE DEFEAT (down)" | MEDIUM | Doesn't explain how to decide which |
| 153-157 | "All Is Lost: Whiff of death — literal or symbolic" | MEDIUM | Examples given but function not explained |
| 173-174 | "Bad guys dispatched in ascending order" | MEDIUM | Says WHAT but not WHY |
| 179-183 | "Final Image: OPPOSITE of Opening Image" | MEDIUM | Says it must be opposite but no examples |

### Example Quality
- NO EXAMPLES of actual beat descriptions
- Prompt gives extensive RULES but no MODELS for GPT to follow

### Schema Completeness
- Schema is COMPLETE
- Fields: number, name, act_label, target_page, target_percentage, description, snowflake_mapping, emotional_direction
- Plus top-level: midpoint_polarity, all_is_lost_polarity

### Character Voice Instructions
N/A for this step

---

## STEP 5: THE BOARD (step_5_prompt.py)

### What the prompt tells GPT to do
- Build exactly 40 scene cards organized in 4 rows
- Place 5 landmark cards first (Catalyst, Break into Two, Midpoint, All Is Lost, Break into Three)
- Fill remaining scenes around landmarks (~10 per row)
- Color-code by storyline (A, B, C, D, E)
- Every card has: scene heading, description, beat, emotional_start/emotional_end (must differ), conflict (one per scene), characters present

### What's MISSING

**1. Scene Heading Format Not Taught**
- Prompt says: "Scene heading: 'INT. JOE'S APARTMENT - DAY' — every card starts with INT./EXT. LOCATION - TIME" (line 62)
- Missing: WHEN to use INT. vs. EXT. vs. INT/EXT.
- Missing: How to choose specificity of location (JOE'S APARTMENT vs. JOE'S APARTMENT - BEDROOM vs. APARTMENT BUILDING)

**2. "Description: Simple Declarative Sentences" — No Examples**
- Prompt says: "the basic action of the scene told in simple declarative sentences — brief enough to fit on a physical index card (max 50 words)" (lines 62-64)
- Missing: EXAMPLES of what this looks like
- Missing: What NOT to do (no camera directions, no dialogue, no character thoughts)

**3. Conflict Types Not Explained**
- Prompt says: "Conflict (><): ONE conflict per scene. 'Man vs. Man, Man vs. Nature, and Man vs. Society' all apply. Specify who the opposing forces are, what the issue is, and who wins." (lines 69-71)
- Missing: EXAMPLES of well-defined conflicts
- Missing: What a BAD conflict description looks like ("tension" without specific opposing forces)

**4. Emotional Change (+/-) Enforcement Weak**
- Prompt says: "Emotional change (+/-): every scene is a 'mini-movie' with beginning, middle, and end. The emotional tone MUST change from start to end — from + to - or from - to +." (lines 72-76)
- Missing: HOW to represent emotional change in a 1-2 sentence scene description
- Missing: Examples of scenes that START positive and END negative (and vice versa)

**5. Storyline Weaving Rules Complex**
- Prompt gives multiple rules:
  - A and B must not disappear for more than 3 consecutive cards (line 89)
  - C/D/E must not disappear for more than 6 consecutive cards (line 90)
  - Every storyline used in Acts 1-2 MUST appear at least once in Row 4 (line 91-94)
- Missing: WHY these numbers (3 for A/B, 6 for C/D/E)
- Missing: HOW to balance storylines — what if you have too many threads?

**6. "Six Things That Need Fixing" Payoff Not Operationalized**
- Prompt says: "Six Things That Need Fixing from Set-Up MUST be paid off in Act Three" (line 97-99)
- But doesn't explain HOW to pay them off in scene cards
- Missing: Each of the 6 flaws should have a corresponding scene in Row 4 where the hero masters or resolves it

**7. Bad Guys Dispatched in Ascending Order — Not Detailed**
- Prompt says: "Bad guys dispatched in ascending order in Act Three — lieutenants first, then the boss" (line 100-101)
- Missing: HOW to structure this in scene cards — do you need one scene per henchman? Can multiple be dispatched in one scene?

**8. Landmark Card Placement — Approximate Positions Given**
- Prompt says Catalyst is "~card 4", Break into Two "~card 10", Midpoint "~card 20", All Is Lost "~card 28", Break into Three "~card 30" (lines 40-45)
- Missing: What happens if these landmarks drift? How much tolerance is allowed?
- Missing: The "9-10 cards per column" math from Snyder (line 81-83) — if you have 9 per column × 4 columns = 36 cards, but the prompt requires 40, where do the extra 4 go?

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 62-64 | "Description: simple declarative sentences, max 50 words" | HIGH | No examples of what this looks like |
| 69-71 | "Conflict: ONE conflict per scene. Specify opposing forces, issue, who wins." | MEDIUM | Good structure but no examples |
| 72-76 | "Emotional change: must change from + to - or - to +" | MEDIUM | Says WHAT but not HOW to show it in description |
| 89-90 | "A/B: max 3 consecutive gap; C/D/E: max 6" | HIGH | Numbers given but no reasoning |
| 97-99 | "Six Things paid off in Act Three" | HIGH | Says WHAT but not HOW to structure payoff scenes |
| 100-101 | "Bad guys dispatched in ascending order" | MEDIUM | Says order but not scene-by-scene structure |

### Example Quality
- ONE example given (lines 111-123) showing the JSON structure
- But the example uses PLACEHOLDER text ("INT./EXT. LOCATION - TIME", "1-2 sentences of what happens", "Hero vs. Force over Issue; Force wins")
- MISSING: A REAL example with concrete scene heading, vivid description, specific conflict

### Schema Completeness
- Schema is COMPLETE
- Fields: card_number, row, scene_heading, description, beat, emotional_start, emotional_end, conflict, storyline_color, characters_present

### Character Voice Instructions
N/A for this step (characters were defined in Step 3b)

---

## STEP 6: IMMUTABLE LAWS (step_6_prompt.py)

### What the prompt tells GPT to do
- Evaluate finished screenplay against 7 Immutable Laws from Chapter 6
- For each law: law_number, law_name, passed (true/false), violation_details (if failed), fix_suggestion (if failed)
- Laws are: Save the Cat, Pope in the Pool, Double Mumbo Jumbo, Black Vet, Watch Out for That Glacier, Covenant of the Arc, Keep the Press Out

### What's MISSING

**1. Law 1 "Save the Cat" — Anti-Hero Corollary Placement**
- Prompt includes the anti-hero rule: "When your hero is slightly damaged goods, make his enemy even more horrible!" (lines 51-53)
- But doesn't explain WHEN this applies — it's a CONDITIONAL rule (if hero is unlikable → antagonist must be worse)
- Missing: How to evaluate if the hero IS likable enough to skip the corollary

**2. Law 2 "Pope in the Pool" — What Counts as "Entertaining"?**
- Prompt says: "All exposition must be buried inside entertaining action or visuals" (line 58)
- Missing: WHAT makes action "entertaining enough" to distract from exposition
- Missing: Examples beyond the Pope swimming (Austin Powers' "Basil Exposition" character, Pirates of the Caribbean's two funny guards)

**3. Law 3 "Double Mumbo Jumbo" — Single Source Not Defined**
- Prompt says: "All supernatural/magical/sci-fi elements must derive from a SINGLE source" (lines 66-70)
- Missing: What constitutes a "source"? Is radioactive spider bite (Spider-Man) + unrelated chemical lab accident (Green Goblin) ONE source (science) or TWO sources (biology vs. chemistry)?
- Missing: The "God and aliens don't mix" rule (Signs example) — supernatural vs. sci-fi are incompatible

**4. Law 4 "Black Vet" — Too Much Marzipan Not Explained**
- Prompt says: "One concept at a time, please. You can not digest too much information." (lines 76-78)
- Missing: HOW to identify when you have multiple concepts competing
- Missing: The SNL parody example is mentioned but not EXPLAINED — a black veterinarian who is also a military veteran is TOO MANY CONCEPTS (race + profession + military background)

**5. Law 5 "Watch Out for That Glacier" — Slow Threat Examples Weak**
- Prompt gives examples: Dante's Peak (volcano might blow "any minute"), Outbreak (virus headed toward US), Open Range (Costner/Duvall talk for an hour) (lines 85-87)
- But doesn't explain WHY these fail — the threat is TOO FAR AWAY or TOO SLOW
- Missing: The fix — make the threat PRESENT and ACTIVE from the start

**6. Law 6 "Covenant of the Arc" — Who Arcs, Who Doesn't**
- Prompt says: "Every single character must change EXCEPT the Bad Guys" (lines 89-93)
- Missing: WHAT counts as change — Pretty Woman example has Richard Gere, Julia Roberts, Laura San Giacomo, Hector Elizondo ALL arc, but Jason Alexander (bad guy) "learns exactly zero" (line 92-93)
- Missing: How to show arc in supporting characters (not just the hero)

**7. Law 7 "Keep the Press Out" — Exception Not Clear**
- Prompt says: "Exception: 'Unless it's about the press, unless your movie involves a world-wide problem.'" (line 100-102)
- Missing: WHEN to apply the exception vs. when to enforce the rule
- Missing: E.T. vs. Signs as contrasting examples — E.T. has NO news crews despite catching a real alien (Spielberg kept it contained); Signs VIOLATES this with CNN coverage of worldwide alien landings

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 51-53 | "Anti-hero corollary: make his enemy even more horrible" | MEDIUM | Conditional rule not flagged as conditional |
| 58-63 | "Pope in the Pool: exposition buried in entertaining action" | HIGH | "Entertaining" undefined; no criteria for what distracts well |
| 66-70 | "Double Mumbo Jumbo: single source" | HIGH | "Source" undefined; biology vs. chemistry ambiguity |
| 76-78 | "Black Vet: one concept at a time" | CRITICAL | No method for identifying competing concepts |
| 85-87 | "Glacier: threat must be present danger" | MEDIUM | Says WHAT but not HOW to make threat immediate |
| 100-102 | "Keep Press Out: exception for world-wide problems" | HIGH | Exception poorly defined; when to apply unclear |

### Example Quality
- Examples are GOOD (Jaws, Alien, Exorcist, Fatal Attraction, Pulp Fiction, Aladdin, Spider-Man, Signs, Austin Powers, Pirates of Caribbean, Dante's Peak, Outbreak, Open Range, Pretty Woman, E.T.)
- But examples are NOT DISSECTED in the prompt — GPT has to infer why each passes/fails

### Schema Completeness
- Schema is COMPLETE
- Fields: law_number, law_name, passed, violation_details, fix_suggestion, all_passed

### Character Voice Instructions
N/A for this step

---

## STEP 7: DIAGNOSTIC CHECKS (step_7_prompt.py)

### What the prompt tells GPT to do
- Run 9 diagnostic checks from Chapter 7 ("What's Wrong With This Picture?") against the finished screenplay
- For each check: check_number, check_name, passed, problem_details, fix_suggestion
- Checks: The Hero Leads, Talking the Plot, Make the Bad Guy Badder, Turn Turn Turn, Emotional Color Wheel, Hi How Are You I'm Fine, Take a Step Back, Limp and Eye Patch, Is It Primal

### What's MISSING

**1. Check 1 "The Hero Leads" — Question Mark Count**
- Prompt says: "Count the hero's question marks — more than 2 is a fail" (line 58)
- Missing: WHY question marks indicate passivity — Snyder says "A hero never asks questions" because questions are REACTIVE (seeking information) vs. PROACTIVE (taking action)
- Missing: The fix — replace questions with statements, commands, declarations

**2. Check 2 "Talking the Plot" — Bad Dialogue Examples**
- Prompt gives two bad examples: "Well, you're my sister, you should know!" and "This sure isn't like the time I was the star fullback for the N.Y. Giants until my... accident." (lines 66-68)
- But doesn't explain WHY these are bad
- Missing: The first is ON THE NOSE (character explains something the listener already knows); the second is FORCED BACKSTORY (character awkwardly reminds listener of shared history)

**3. Check 2 "Show, Don't Tell" — Technique Not Operationalized**
- Prompt says: "Show a husband eyeing a pretty young thing instead of three pages of marriage counseling" (line 70-71)
- Missing: HOW to convert a "telling" scene into a "showing" scene — the PROCESS of visual translation

**4. Check 3 "Make the Bad Guy Badder" — Mirror Principle**
- Prompt says: "Hero and bad guy are 'two halves of the same person struggling for supremacy'" (line 81-82)
- But doesn't explain HOW to check if they're mirrors
- Missing: Examples dissected (Batman/Joker: both outsiders, both use fear; Die Hard Willis/Rickman: both intelligent, both resourceful)

**5. Check 4 "Turn, Turn, Turn" — Velocity vs. Acceleration**
- Prompt quotes Snyder: "It's not enough for the plot to go forward, it must go forward faster, and with more complexity, to the climax." (lines 92-94)
- Missing: HOW to measure if the pace is accelerating — what does "faster" look like in scenes?
- Missing: The Cat in the Hat counter-example: "tons of kinetic action without anything happening" — a CHASE with no stakes (lines 97-98)

**6. Check 5 "Emotional Color Wheel" — Emotion List**
- Prompt lists emotions: lust, fear, joy, hope, despair, anger, tenderness, surprise, longing, regret, frustration, near-miss anxiety, triumph, human foible (lines 110-111)
- Missing: HOW MANY of these must be present — the prompt implies "all of them" but doesn't specify a minimum
- Missing: The "recoloring technique" — "Take a scene that's just funny or just dramatic and try to play it for one of the missing colors... use the same action, the same +/-, the same conflict and result, but play it for lust instead of laughs" (lines 112-115)

**7. Check 6 "Hi, How Are You? I'm Fine" — Bad Dialogue Test**
- Prompt includes the test: "Cover up the names of the people speaking. Read the repartee back and forth. Can you tell who is speaking without seeing the name?" (lines 120-122)
- Missing: WHAT to do if they all sound the same — the FIX is to give each character a verbal tic, unique vocabulary, sentence length, and speech rhythm (lines 126-130)
- Missing: Snyder's confession: "I was stunned. God damn it, he was right. I couldn't tell one of my characters from the others... all the characters had MY voice!!" (lines 122-124)

**8. Check 7 "Take a Step Back" — Bow-and-Arrow Metaphor**
- Prompt includes the metaphor: "By drawing the bow back to its very quivering end point, the flight of the arrow is its strongest, longest, best flight." (lines 135-137)
- Missing: WHAT this means in practice — take the hero (and ALL characters) back as far as possible emotionally at the START so the arc is visible
- Missing: The 7-draft mistake — Sheldon & Blake's Golden Fleece kid was already nice from the start, took 7 drafts to fix by making him emotionally further back (lines 141-143)

**9. Check 8 "Limp and Eye Patch" — Running Visual Reminder**
- Prompt says: "Make sure every character has 'A Limp and an Eyepatch.' The reader has to have a visual clue, often a running visual reminder." (lines 149-153)
- Missing: EXAMPLES — the lead boy in Deadly Mean Girls needed a black t-shirt and wispy soul-patch; manager Andy Cohen said "the boy jumped off the page" (lines 153-156)
- Missing: The identifier must be REFERENCED each time the character appears

**10. Check 9 "Is It Primal?" — Caveman Test**
- Prompt says: "Would a Caveman Understand? At the root of anyone's goal must be something basic." (lines 162-167)
- Missing: HOW to reframe a non-primal goal to make it primal — if the hero wants "a promotion at work," connect it to "winning the hand of X's beloved" (Ch.3)
- Missing: Examples of surface-to-primal translation (Die Hard = desire to save family, Home Alone = protect home, Sleepless in Seattle = find a mate, Gladiator = exact revenge, Titanic = survive) (lines 167-170)

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 58 | "Count question marks; more than 2 is a fail" | LOW | Clear and specific |
| 66-68 | "Bad dialogue examples" | MEDIUM | Examples given but WHY they're bad not explained |
| 70-74 | "Show, Don't Tell: Show X instead of saying X" | HIGH | Says WHAT but not HOW to translate |
| 81-82 | "Two halves of the same person" | HIGH | Metaphorical; no structural check |
| 92-94 | "Plot must go forward faster, with more complexity" | HIGH | "Faster" and "more complexity" undefined |
| 110-115 | "Emotional Color Wheel: check for all these emotions" | MEDIUM | List given but no minimum count specified |
| 120-122 | "Bad Dialogue Test: Cover the names" | LOW | Clear and testable |
| 135-137 | "Bow-and-arrow: draw back to quivering end point" | MEDIUM | Metaphor not operationalized |
| 149-153 | "Limp and Eye Patch: running visual reminder" | MEDIUM | Principle stated but no examples in prompt |
| 162-167 | "Is It Primal? Caveman test." | MEDIUM | Test stated but no method for reframing non-primal goals |

### Example Quality
- Examples are PRESENT (Johnny Entropy, Big Ugly Baby, Deadly Mean Girls, Cat in the Hat, Farrelly Brothers films, Die Hard, Home Alone, Sleepless in Seattle, Gladiator, Titanic)
- But examples are NOT FULLY DISSECTED — GPT has to infer the lesson

### Schema Completeness
- Schema is COMPLETE
- Fields: check_number, check_name, passed, problem_details, fix_suggestion, checks_passed_count, total_checks

### Character Voice Instructions
- Check 6 ("Hi, How Are You? I'm Fine") IS the character voice diagnostic
- Good coverage of the "Bad Dialogue Test"
- Missing: concrete examples of distinct character voices (stuttering, malapropisms, Okie versed in Sartre, alien parents YELLING)

---

## STEP 8: SCREENPLAY WRITING (step_8_prompt.py)

### What the prompt tells GPT to do
- Expand every board card into a FULL screenplay scene
- Each scene is a mini-movie (beginning, middle, end, emotional change, conflict)
- Show, don't tell; no internal monologue; sustained dialogue exchanges (3-6 back-and-forth minimum)
- Visual entry and exit; 5-15 elements per scene; 1 page = 60 seconds

### What's MISSING

**1. Mini-Movie Structure Not Operationalized**
- Prompt says: "Each scene is a MINI-MOVIE with a beginning, middle, and end" (lines 60-64)
- Missing: WHAT the beginning/middle/end look like in a screenplay scene
- Missing: Beginning = establishing what's at stake; Middle = conflict escalates; End = someone wins/loses

**2. Emotional Change Mechanics Not Explained**
- Prompt says: "Every scene starts at one emotional polarity and ENDS at the opposite. The board card's emotional_start and emotional_end tell you the transition. Show this change through ACTION." (lines 66-70)
- Missing: HOW to show emotional change through action — EXAMPLES of + to - scenes and - to + scenes
- Missing: The change must be VISIBLE — not told through dialogue ("I'm so angry now!") but shown through behavior

**3. "Conflict (><): One Per Scene" — Conflict Types**
- Prompt says: "Only one conflict per scene, please. One is plenty. The board card specifies who the opposing forces are, what the issue is, and who wins." (lines 70-73)
- Missing: WHAT counts as "one conflict" — if two characters argue about X while also dealing with external threat Y, is that one or two?
- Missing: Examples of well-constructed single-conflict scenes

**4. "No Internal Monologue" — Translation Examples**
- Prompt gives two examples:
  - WRONG: "She felt nausea rising in her stomach."
  - RIGHT: "She grabs the table edge. Her knuckles whiten." (lines 74-77)
- Missing: MORE examples — this is a critical skill and one example isn't enough
- Missing: Common mistakes (emotions, thoughts, backstory, motivations) and how to externalize each

**5. "Show, Don't Tell" — Process Not Taught**
- Prompt gives two examples:
  - WRONG: "He planned this for months."
  - RIGHT: "He opens a drawer. Surveillance photos spill across the desk. Dates circled in red." (lines 79-81)
- Missing: The PROCESS — how to identify "telling" and convert it to "showing"
- Missing: More examples across different categories (backstory, relationships, emotions, character traits)

**6. Dialogue Must Be "SPOKEN, SUSTAINED, and CHARACTER-SPECIFIC"**
- Prompt says: "Each dialogue scene needs MULTIPLE exchanges (3-6 back-and-forth minimum)" (line 84-85)
- Missing: WHAT counts as an exchange — is it character name + dialogue? Or a full back-and-forth pair?
- Missing: HOW to make dialogue feel natural while avoiding exposition

**7. Character Voice Distinctiveness**
- Prompt says: "Every character must speak differently. Every character must have a unique way of saying even the most mundane chat." (lines 85-87)
- Missing: HOW to make voices distinct in practice — the prompt references CHARACTER_IDENTIFIERS but doesn't explain how to USE them in dialogue
- Missing: The "Bad Dialogue Test" — "Cover up the names — can you tell who is speaking?" (from Ch.7)

**8. Visual Entry and Exit — Examples Missing**
- Prompt says: "Every scene opens with a slugline and establishing action (what we SEE when we arrive), and ends with a clear reason to cut — a door slam, a look, a revelation, a question left hanging." (lines 90-93)
- Missing: EXAMPLES of strong visual entries and exits
- Missing: Common mistakes (scenes that just "start talking" or "fade to black" without purpose)

**9. Scene Density — 5-15 Elements**
- Prompt says: "Each scene should have 5-15 elements. Thin scenes (1-3 elements) are outlines, not screenplay." (lines 94-97)
- Missing: WHAT counts as an element — is it just the JSON element_type count, or does it include back-and-forth dialogue exchanges?
- Missing: HOW to add density without padding — what makes a scene feel FULL vs. THIN

**10. Element Ordering Not Taught**
- Prompt lists element types: slugline, action, character, parenthetical, dialogue, transition (lines 117-124)
- Missing: The RULES of ordering — character MUST precede dialogue, parenthetical goes between character and dialogue, action can go anywhere
- Missing: When to use parentheticals (sparingly!) vs. when to use action lines

**11. Screenplay Format Examples Weak**
- Prompt gives ONE output format example (lines 126-161) with placeholder text
- Missing: A REAL scene with rich action, sustained dialogue, emotional change, and conflict resolution
- Missing: Counter-examples showing what NOT to do

### SCENE-BY-SCENE GENERATION PROMPTS (SINGLE_SCENE_TEMPLATE, lines 344-429)

**What This Does:**
- Used when generating ONE scene at a time instead of the whole screenplay
- Includes character identifiers, previous scenes for continuity, milestone guidance from act diagnostics

**What's MISSING:**

**1. Milestone Guidance Not Explained**
- Prompt includes a {milestone_guidance} parameter (line 631) but doesn't explain WHAT this is
- Missing: How milestone diagnostics feed back into scene generation

**2. Previous Scenes Summary — Continuity Rules**
- Prompt includes {previous_scenes_summary} (line 362, line 641) but doesn't explain HOW to maintain continuity
- Missing: What to check for (character positions, time of day, unresolved plot threads, emotional carryover)

**3. Character Voice Guide Format**
- Prompt includes {character_identifiers} (line 356, line 602) — a formatted string of character → distinctive trait
- Missing: HOW this should be formatted and WHAT level of detail it needs
- Missing: Example of a complete character identifier guide

### ACT-BY-ACT GENERATION PROMPTS (ACT_GENERATION_TEMPLATE, lines 810-903)

**What This Does:**
- Generate all scenes for one act at a time (Act 1, Act 2a, Act 2b, Act 3)
- Includes previous acts context for continuity

**What's MISSING:**

**1. Act Boundaries Not Structurally Defined**
- Prompt says "Write ALL scenes for {act_label}" (line 810) but doesn't define WHAT scenes belong in each act
- Missing: Row 1 = cards 1-10 (Act One), Row 2 = cards 11-20 (Act Two A), Row 3 = cards 21-30 (Act Two B), Row 4 = cards 31-40 (Act Three)

**2. Act-Specific Tone Guidance Missing**
- Each act has a different structural function (Thesis, Antithesis, Synthesis) but the prompt doesn't explain how this affects SCENE WRITING
- Missing: Act 1 tone (establishing status quo), Act 2 tone (upside-down world), Act 3 tone (synthesis, resolution)

### ACT DIAGNOSTIC PROMPTS (ACT_DIAGNOSTIC_TEMPLATE, lines 913-986)

**What This Does:**
- Grok evaluates one act against all 9 Save the Cat diagnostics
- Identifies problems with specific scene/line citations

**What's MISSING:**

**1. Context-Dependent Checks**
- Some diagnostics (Take a Step Back, Is It Primal) need full-screenplay context but the prompt says "evaluate based on what you can see in this act" (line 983-985)
- Missing: Guidance on which checks are act-local vs. screenplay-global

**2. Citation Format Not Specified**
- Prompt says "CITE SPECIFIC SCENES AND LINES. Don't be vague." (line 985)
- Missing: WHAT format citations should take — scene numbers, dialogue quotes, action line excerpts?

### Vagueness Audit (Main Screenplay Prompt)

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 60-64 | "Each scene is a mini-movie: beginning, middle, end" | HIGH | Structure not operationalized |
| 66-70 | "Emotional change from + to - or - to +" | HIGH | Says WHAT but not HOW to show it |
| 70-73 | "Conflict: one per scene" | MEDIUM | "One conflict" boundary unclear |
| 74-77 | "No internal monologue" example | MEDIUM | One example given; need more |
| 79-81 | "Show, don't tell" example | MEDIUM | One example given; need more |
| 84-87 | "Dialogue: SPOKEN, SUSTAINED, CHARACTER-SPECIFIC" | HIGH | "Sustained" and "character-specific" not operationalized |
| 90-93 | "Visual entry and exit" | HIGH | No examples given |
| 94-97 | "Scene density: 5-15 elements" | HIGH | "Element" definition unclear; no guidance on adding density |

### Example Quality
- ONE output format example (lines 126-161) with PLACEHOLDER text
- CRITICAL GAP: No real screenplay scene example showing best practices

### Schema Completeness
- Schema is COMPLETE for individual scenes
- Fields: scene_number, slugline, int_ext, location, time_of_day, elements, estimated_duration_seconds, beat, emotional_start, emotional_end, conflict, characters_present, board_card_number
- Top-level fields: title, author, format, genre, logline, total_pages, estimated_duration_seconds, scenes

### Character Voice Instructions
- PRESENT but VAGUE (lines 85-87)
- References CHARACTER_IDENTIFIERS but doesn't explain how to use them
- Missing: The "Bad Dialogue Test" (cover names, can you tell who's speaking?)
- Missing: Concrete examples of distinct character voices

---

## STEP 9: MARKETING VALIDATION (step_9_prompt.py)

### What the prompt tells GPT to do
- Evaluate whether the finished screenplay delivers on the promise of its logline, genre, and audience
- Apply the Poster Test, 4-Quadrant analysis, and Hook test
- Check: logline_still_accurate, genre_clear, audience_defined, title_works, one_sheet_concept
- List issues and fixes

### What's MISSING

**1. Poster Test Not Operationalized**
- Prompt says: "THE POSTER TEST: Imagine the one-sheet on the wall at the multiplex. Would a moviegoer passing by STOP and want to see this movie?" (line 106-108)
- Missing: WHAT elements make a poster stop-worthy — the prompt asks for a description but doesn't explain the CRITERIA for a good poster

**2. Hook Test Mentioned But Not Applied**
- Prompt says: "THE HOOK TEST (Glossary): 'The hook must blossom in your mind with possibility and hook you into wanting more.'" (line 111-113)
- Missing: HOW to test if the hook actually "blossoms" — is it the logline? The title? The poster concept?

**3. 4-Quadrant Analysis Weak**
- Prompt mentions the 4 quadrants (Men Over 25, Men Under 25, Women Over 25, Women Under 25) (line 89-94)
- Missing: HOW to determine which quadrants the screenplay actually appeals to — what in the screenplay signals "Men Under 25" vs. "Women Over 25"?
- Missing: Snyder's point: "If you can draw audience from all those quadrants... you are guaranteeing yourself a hit" (line 92-93)

**4. "Logline Still Accurate" — Drift Detection**
- Prompt asks: "Does the logline still describe what actually happens in the screenplay? If the story drifted during development, identify WHERE it diverged." (line 73-75)
- Missing: COMMON drift patterns — hero's goal changed, antagonist became different, tone shifted, etc.
- Missing: HOW to identify drift — compare logline promises to actual screenplay beats

**5. "Genre Clear" — Structural Delivery**
- Prompt asks: "Can a viewer immediately identify the genre/tone? Does every scene serve the genre's structural requirements?" (line 81-84)
- Missing: WHAT "serving the genre" looks like — if it's Monster in the House, are there run-and-hide scenes? If it's Golden Fleece, does the hero learn about himself?

**6. "Title Works" — Criteria Vague**
- Prompt asks: "Does the title still 'say what it is' in a clever way? Does it create intrigue while accurately representing the story?" (line 97-99)
- Missing: EXAMPLES of titles that work vs. titles that don't
- Missing: Snyder's warnings from Ch.1 — title must have IRONY, must "tell the tale," must NOT be vague ("For Love or Money", "Crossroads", "Destiny" are bad)

**7. One-Sheet Concept — Image + Tagline**
- Prompt asks: "Describe the movie poster in 2-3 sentences. What single IMAGE would sell this story? What TAGLINE would go under the title?" (line 103-105)
- Missing: WHAT makes a strong image (character in iconic situation, visual irony, stakes visible)
- Missing: WHAT makes a strong tagline (encapsulates hook in 5-10 words)

**8. Issues List — Common Marketing Problems**
- Prompt says: "Common problems: drift from logline, unclear genre, muddled audience, weak title, poster that doesn't convey the story, missing hook." (line 117-120)
- Missing: HOW to diagnose each problem — what are the SYMPTOMS in the screenplay?

**9. Callbacks and Running Gags**
- Prompt mentions: "Also flag if callbacks/running gags are missing — recurring elements strengthen audience connection" (line 120-122)
- Missing: WHAT callbacks/running gags are — visual motifs, repeated phrases, character tics that pay off later
- Missing: WHERE they should appear (Set-Up and Finale for maximum impact)

**10. "Every Sale Has a Story" — Pitch Readiness**
- Prompt includes Snyder's quote: "Every sale has a story" (Hilary Wayne) (line 12-14)
- Missing: WHAT this means — you need a compelling STORY about how this screenplay came to be, why it matters, why it's urgent
- Missing: This is a MARKETING element separate from the screenplay itself

### Vagueness Audit

| Line | Instruction | Vagueness Level | Problem |
|------|-------------|-----------------|---------|
| 73-75 | "Logline still accurate? Identify WHERE it diverged." | MEDIUM | Says WHAT but not HOW to identify drift |
| 81-84 | "Genre clear? Does every scene serve the genre?" | HIGH | "Serve the genre" undefined |
| 89-94 | "4-Quadrant analysis" | HIGH | Quadrants listed but no method for determining appeal |
| 97-99 | "Title works? 'Say what it is' in a clever way" | MEDIUM | Criteria vague; no examples |
| 103-108 | "Poster Test: describe the one-sheet, would a moviegoer STOP?" | HIGH | "Stop-worthy" criteria not defined |
| 111-113 | "Hook Test: must blossom in your mind with possibility" | CRITICAL | "Blossom" metaphorical; no concrete test |
| 117-120 | "Common problems: drift, unclear genre, muddled audience, weak title" | MEDIUM | Problems listed but symptoms not explained |
| 120-122 | "Flag if callbacks/running gags are missing" | HIGH | Callbacks/running gags not defined |

### Example Quality
- NO EXAMPLES given for posters, taglines, hooks, 4-quadrant analysis
- This is a CRITICAL gap — GPT has no models for what marketing validation looks like

### Schema Completeness
- Schema is MINIMAL
- Fields: logline_still_accurate, genre_clear, audience_defined, title_works, one_sheet_concept, issues
- Missing: 4_quadrant_breakdown (which quadrants and why)
- Missing: hook_strength_score (numeric rating)
- Missing: callback_inventory (list of recurring elements)

### Character Voice Instructions
N/A for this step

---

## CROSS-CUTTING ISSUES (All Prompts)

### 1. **No Real Examples Across the Board**
- Almost every prompt gives RULES but not MODELS
- GPT is expected to generate high-quality output without seeing what "good" looks like
- This is like teaching someone to paint by describing color theory without showing them a painting

### 2. **Vague Success Criteria**
- Prompts say "make it good" or "ensure it's compelling" without defining WHAT makes it good/compelling
- Examples:
  - "Ironic element must be emotionally intriguing" — what makes something intriguing?
  - "Title must have irony" — what is title irony?
  - "Logline must bloom in your mind" — what does blooming look like?
  - "Dialogue must be sustained" — how many exchanges?
  - "Scene must be dense" — how many elements?

### 3. **Process vs. Product Confusion**
- Prompts describe WHAT the output should be but not HOW to create it
- Example: "Show, don't tell" is explained as a goal but the PROCESS of converting telling to showing is not taught

### 4. **Missing Snyder's Voice and Reasoning**
- Prompts quote Snyder extensively but often don't include his REASONING
- Example: "Six Things That Need Fixing" — the prompt requires exactly 6 but doesn't explain WHY six or HOW they function structurally

### 5. **Character Voice Is Mentioned But Not Taught**
- Step 3b asks for "voice_profile" for each character
- Step 8 asks for "CHARACTER-SPECIFIC" dialogue
- But NEITHER step teaches HOW to make voices distinct
- The "Bad Dialogue Test" (Ch.7) is mentioned in Step 7 diagnostics but not operationalized in Step 8 writing

### 6. **Schema Fields Don't Match Prompt Content**
- Some prompts ask for information in the text that doesn't have a corresponding JSON field
- Example: Step 4 asks to explain Midpoint/All Is Lost polarity CHOICE but the schema only has the result (up/down), not the reasoning

### 7. **Downstream Dependencies Not Explained**
- Prompts don't explain HOW each step's output feeds into the next
- Example: Step 1 asks for "story_beginning" and "story_ending" but doesn't explain that these feed into Beat Sheet's Opening Image and Final Image
- Example: Step 3 asks for "Six Things That Need Fixing" but doesn't explain that Step 5 Board must pay them off in Row 4

### 8. **Counter-Examples Missing**
- Snyder uses BAD examples extensively (Arachnophobia, The Cat in the Hat, Signs) to show what NOT to do
- The prompts rarely include counter-examples — they only show the POSITIVE path

---

## RECOMMENDATIONS

### Priority 1: Add Real Examples to Every Prompt
- Step 1: Include 3-5 DISSECTED loglines showing why they work
- Step 2: Include genre examples with working parts IDENTIFIED in the text
- Step 3: Include archetype examples with actor lineage
- Step 4: Include beat description examples (1-2 sentences each)
- Step 5: Include 3-5 board card examples with vivid descriptions
- Step 8: Include 2-3 FULL screenplay scenes showing best practices

### Priority 2: Operationalize Vague Criteria
- "Ironic" → define with 3+ examples of ironic vs. non-ironic
- "Compelling mental picture" → checklist of what must be visible
- "High concept" → mechanics (international appeal, no explanation needed, poster-worthy)
- "Sustained dialogue" → minimum exchange count (3-6 back-and-forth)
- "Dense scene" → element count range (5-15) + examples

### Priority 3: Teach Process, Not Just Product
- "Show, don't tell" → 5-step conversion process with examples
- "Character voice" → technique library (stuttering, malapropisms, sentence length, vocabulary level, verbal tics)
- "Surface-to-primal connection" → how to identify surface goals and trace them to primal urges

### Priority 4: Include Snyder's Reasoning
- WHY each rule exists (not just WHAT the rule is)
- WHAT happens if you violate the rule (consequences, common failures)
- HOW to fix violations (concrete repair techniques)

### Priority 5: Add Counter-Examples
- For every rule, show a WRONG example and explain why it fails
- Use Snyder's own counter-examples (Arachnophobia, Cat in the Hat, Signs, etc.)
- Dissect the failure to make the rule concrete

### Priority 6: Link Steps Explicitly
- Each prompt should reference HOW its output feeds downstream
- Example: Step 1 should say "story_beginning/story_ending will become Opening Image/Final Image in Step 4"
- Example: Step 3 should say "Six Things That Need Fixing must be paid off in Act Three cards in Step 5"

### Priority 7: Character Voice Tutorial
- Create a dedicated section in Step 3b or Step 8 that TEACHES character voice differentiation
- Include the "Bad Dialogue Test" with examples
- Provide a technique library (vocabulary, rhythm, verbal tics, sentence length)
- Show 3-5 character voice profiles from real movies

---

## SEVERITY SUMMARY

| Step | Critical Issues | High Issues | Medium Issues | Low Issues |
|------|----------------|-------------|---------------|-----------|
| Step 1 (Logline) | 1 (Jealousy Test) | 3 (High concept, mental picture, irony) | 3 | 0 |
| Step 2 (Genre) | 3 (Working parts, structural engine, twist) | 2 (Sub-types, lineage) | 1 | 0 |
| Step 3 (Hero) | 1 (Archetype selection) | 3 (Conflict, journey, demographic) | 4 | 0 |
| Step 3b (Supporting Cast) | 1 (Voice profile) | 2 (Distinctive trait, role functions) | 1 | 0 |
| Step 4 (Beat Sheet) | 0 | 0 | 8 | 2 |
| Step 5 (Board) | 0 | 4 (Description, conflict, weaving, payoff) | 4 | 0 |
| Step 6 (Laws) | 1 (Black Vet) | 3 (Pope, Mumbo Jumbo, Press) | 3 | 0 |
| Step 7 (Diagnostics) | 0 | 4 (Talking Plot, Mirror, Velocity, Bow) | 5 | 1 |
| Step 8 (Screenplay) | 1 (Real scene example) | 6 (Mini-movie, emotional change, voice, entry/exit, density, format) | 3 | 0 |
| Step 9 (Marketing) | 1 (Hook Test) | 5 (Poster, 4-quadrant, drift, genre, callbacks) | 3 | 0 |

**Total across all steps:**
- **Critical:** 8 issues that will cause structurally broken output
- **High:** 32 issues that will cause weak/generic output
- **Medium:** 35 issues that will cause missed opportunities
- **Low:** 3 issues that are nice-to-haves

---

**END OF AUDIT**
