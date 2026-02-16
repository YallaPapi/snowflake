"""
Step 5 Prompt Template: The Board -- 40 Scene Cards (Save the Cat Ch.5)

v3.0.0 -- Genre-specific board construction guidance added from "Save the Cat Goes to the Movies."
Each of Snyder's 10 structural genres now has its own board guidance describing how to DISTRIBUTE
and STRUCTURE the 40 scene cards for that genre type. Logline and genre now passed through as
required inputs. No fallback defaults -- all required fields raise ValueError if missing.
"""

import json
import hashlib
from typing import Dict, Any, List


class Step5Prompt:
    """Prompt generator for Screenplay Engine Step 5: The Board (40 Scene Cards)"""

    VERSION = "6.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! Board architect. "
        "Snyder: 'The Board is a way for you to see your movie before you start writing.' "
        "Build exactly 40 scene cards organized in 4 rows with emotional change (+/-) "
        "and conflict markers (><) on every card.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Build The Board (40 scene cards) for the following screenplay.

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

BEAT SHEET (Step 4 Artifact -- the 15 beats that define this story's structure):
{beat_sheet_summary}

CHARACTERS (Step 3 Artifact):
{character_summary}

GENRE RULES (Step 2 Artifact):
{genre_rules}

{genre_board_guidance}

INSTRUCTIONS:

1. PLACE 5 LANDMARK CARDS FIRST (Snyder: "The next cards you really must nail are the hinge
   points. Midpoint, Act Two Break, Act One Break."):
   - Catalyst (~card 4): The inciting incident -- "a telegram, getting fired, news of a death"
   - Break into Two (~card 10): End of Column 1. Hero's PROACTIVE CHOICE to enter Act Two
   - Midpoint (~card 20): End of Column 2. False victory (up) or false defeat (down) -- stakes raised
   - All Is Lost (~card 28): Opposite polarity of Midpoint -- "the flip" -- whiff of death
   - Break into Three (~card 30): End of Column 3. A and B stories merge -- hero has the solution

2. FILL remaining scenes around landmarks to reach exactly 40 cards total (~10 per row).
   Snyder: "You've got nine to ten cards per column that you need to fill."

3. COLOR-CODE by storyline (Snyder: "Color code each story."):
   - A (main plot / hero's external journey)
   - B (theme / love story / B-story character -- carries the theme)
   - C, D, E (subplots -- minor character arcs, recurring imagery)

ROW ASSIGNMENTS (Snyder: "Column #1 is Act One (pages 1-25)"):
- Row 1 (Act One / THESIS): cards 1-10, pages 1-25
- Row 2 (Act Two A / ANTITHESIS): cards 11-20, pages 25-55
- Row 3 (Act Two B / ANTITHESIS): cards 21-30, pages 55-85
- Row 4 (Act Three / SYNTHESIS): cards 31-40, pages 85-110

CARD CONTENT RULES:
- Scene heading: "INT. JOE'S APARTMENT - DAY" -- every card starts with INT./EXT. LOCATION - TIME
- Description: "the basic action of the scene told in simple declarative sentences" -- brief enough
  to fit on a physical index card (max 50 words)
- Beat: which of the 15 BS2 beats this scene belongs to -- use EXACT canonical beat names:
  Opening Image, Theme Stated, Set-Up, Catalyst, Debate, Break into Two,
  B Story, Fun and Games, Midpoint, Bad Guys Close In, All Is Lost,
  Dark Night of the Soul, Break into Three, Finale, Final Image
- Conflict (><): ONE conflict per scene. Snyder: "Only one conflict per scene, please. One is
  plenty." Specify who the opposing forces are, what the issue is, and who wins by the end.
  "Man vs. Man, Man vs. Nature, and Man vs. Society" all apply.
- Emotional change (+/-): every scene is a "mini-movie" with beginning, middle, and end. The
  emotional tone MUST change from start to end -- from + to - or from - to +.
  Snyder: "an emotional change like this must occur in every scene. And if you don't have it,
  you don't know what the scene is about." emotional_start and emotional_end MUST differ.
- Characters present: at least one character on screen per scene
- Character arcs: For EACH character present, describe the behavioral shift that happens
  to them in this scene. Snyder: "Before I sit down to write, I make notes on how all my
  characters are going to arc by charting their stories as they are laid out on The Board,
  with the milestones of change noted as each character progresses through the story."
  Snyder: "Every single character in your movie must change. EVERYONE." This is the
  Covenant of the Arc — plan each character's change ON the Board, before you write.

  For ONE-SHOT characters (appear in only 1 card): the arc_moment describes their full
  within-scene change. Example: "Starts dismissive of hero → shown evidence → makes a call
  they wouldn't have made before."

  For RECURRING characters (appear on 2+ cards): the arc_moment describes THIS SCENE's step
  in their overall journey. Example: "Still guarded and evasive (from Card 12) → opens up
  after hero shows genuine concern."

  The arc_moment must describe a BEHAVIORAL change — not just a feeling. The character must
  DO something different at the end of the scene than they would have done at the start.
  "Feels bad but follows orders anyway" is NOT an arc. "Sets down weapon and walks away" IS.

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
  "Hero's team leader briefs the squad on the blackout's origin, timeline, and infrastructure."
  This is a character standing at a screen talking AT the audience. There is nothing visual
  or entertaining happening. The audience will tune out.

GOOD CARD (exposition buried in visual entertainment):
  Card 12: EXT. ROOFTOP WATER TOWER - DAY
  "Hero climbs a swaying water tower to manually reset a relay while her partner shouts
  infrastructure details from below — the grid is failing in sectors, hospitals are next."
  The exposition (grid sectors, hospital timeline) is delivered while we watch Hero dangling
  from a water tower. The audience absorbs the info because they're worried she'll fall.

GOOD CARD (exposition buried in conflict):
  Card 12: INT. SERVER FARM - DAY
  "Hero interrogates a captured technician about the blackout while the building's backup
  generator sputters and dies around them, plunging sections into darkness one by one."
  The exposition (blackout origin, timeline) is delivered while physical danger escalates.

RULE: If a card's description contains ANY of these words — "briefs," "explains," "debriefs,"
"informs," "reveals to the team," "goes over the plan," "lays out the situation" — the card
is PROBABLY a Pope in the Pool violation. Rewrite it so the information is delivered during
action, danger, comedy, or visual spectacle.

ZERO TOLERANCE: Do NOT create any card where characters sit/stand and talk about the plot.
Every card must have PHYSICAL ACTION happening alongside any information delivery.

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
  "A CNN anchor reports on the citywide blackout as Hero watches from a bar TV."
  This breaks containment. The audience now thinks "why doesn't the government/military
  handle this?" The hero's personal stakes are diluted by institutional awareness.

GOOD CARD:
  Card 35: INT. DIVE BAR - NIGHT
  "Hero overhears two strangers arguing about whether the blackout is a cyberattack or
  a transformer failure. Nobody knows the truth except Hero — and she can't tell anyone."
  The information about public perception is conveyed through CHARACTERS, not media.
  The containment stays intact — the audience knows what Hero knows, and the secret stays
  between Hero and us.

EXCEPTION: If the logline's premise IS about media/journalism (e.g., the hero is a
reporter, the story is about a media scandal), then press scenes are part of the premise
and this rule does not apply. For ALL other stories: zero news/media/press cards.

BANNED WORDS in card descriptions: "news," "reporter," "broadcast," "coverage," "press
conference," "media," "journalist," "anchor," "breaking news," "goes viral," "trending."
If your card contains any of these words, DELETE the card and replace it with a scene
that conveys the same information through personal, contained interactions.

STRUCTURAL RULES:
- EXACTLY 40 cards total. Snyder: "Forty cards. That's all I'm going to give you for your
  finished board. So if you've got fifty or if you've got twenty you've got problems."
- 9-10 cards per row (minimum 7). Snyder: "nine cards in column #1, nine in column #2, nine in
  column #3 and nine in column #4 -- wait! That's only 36 cards. I'm giving you four extra."
- Act Three MUST NOT be light. Snyder: "in the early going, you almost always have a light Act
  Three. It's usually two cards. Ha! Kills me every time." Nine or ten cards required in Row 4.
- Sequences (chases, set pieces) count as ONE card. Snyder: "Things like 'a chase' involve many
  scenes... it's actually only one beat."
- Set-Up should be 3-4 cards covering pages 1-10, getting to the Catalyst. Snyder: "I give myself
  three or four cards for the first ten pages."
- Storylines woven together: A and B must not disappear for more than 3 consecutive cards.
  C/D/E subplots must not disappear for more than 6 consecutive cards.
- Every storyline used in Acts 1-2 MUST appear at least once in Row 4 (Act Three) for payoff.
  Snyder: "Whether it's the true love story or the thematic center of the movie, this must be
  paid off, too. In fact, the more you think about tying up all the loose ends, the C, D and E
  stories, recurring images etc."
- Midpoint and All Is Lost MUST have OPPOSITE emotional polarity. Snyder: "It's the flip of
  the Midpoint."
- Six Things That Need Fixing from Set-Up MUST be paid off in Act Three. Snyder: "Go back to
  Act One and look at all your set-ups and the 'Six Things That Need Fixing.' Are these 'paid
  off' in Act Three? If not, they should be."
- Bad guys dispatched in ascending order in Act Three -- lieutenants first, then the boss.
  Snyder: "Did you off all the Lieutenants on your way to killing the Uber-Villain?"
- Card numbers must be unique (1 through 40, one per card).

THESIS / ANTITHESIS / SYNTHESIS:
- Row 1 (Act One) = THESIS: the world as it is, the old way of thinking
- Rows 2-3 (Act Two) = ANTITHESIS: the upside-down world where the old way is tested and broken
- Row 4 (Act Three) = SYNTHESIS: the hero merges old and new into something better, new world order

OUTPUT FORMAT (JSON):
{{
  "row_1_act_one": [
    {{
      "card_number": 1,
      "row": 1,
      "scene_heading": "INT./EXT. LOCATION - TIME",
      "description": "1-2 sentences of what happens (simple declarative)",
      "beat": "Opening Image",
      "emotional_start": "+",
      "emotional_end": "-",
      "conflict": "Hero vs. Force over Issue; Force wins",
      "storyline_color": "A",
      "characters_present": ["Character Name"],
      "character_arcs": {{
        "Character Name": "Enters [initial behavior] → [event/cause] → exits [changed behavior]"
      }}
    }}
  ],
  "row_2_act_two_a": [ ... ],
  "row_3_act_two_b": [ ... ],
  "row_4_act_three": [ ... ]
}}

Generate exactly 40 cards total across all 4 rows. Respond with valid JSON only."""

    REVISION_PROMPT_TEMPLATE = """Your previous Board (40 scene cards) had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

BEAT SHEET (Step 4 Artifact):
{beat_sheet_summary}

CHARACTERS (Step 3 Artifact):
{character_summary}

Provide a corrected JSON response that fixes ALL listed errors.

Maintain all HARD RULES:
- Exactly 40 cards total across 4 rows (~10 per row, minimum 7 per row)
- Every card has conflict (ONE per scene), emotional_start ('+'/'-'), emotional_end ('+'/'-')
- emotional_start and emotional_end MUST differ (every scene = emotional change)
- Every card has scene_heading (INT./EXT. LOCATION - TIME format), storyline_color (A-E)
- Every card has at least one character in characters_present
- Beat names must be one of the 15 canonical BS2 beats (exact names)
- Description: simple declarative sentences, brief enough for an index card (max 50 words)
- Card numbers must be unique (1 through 40)
- 5 landmark beats at approximately correct positions:
  Catalyst (~4), Break into Two (~10), Midpoint (~20), All Is Lost (~28), Break into Three (~30)
- A/B storylines: max 3 consecutive card gap; C/D/E: max 6
- Act Three (row 4) must have at least 7 cards
- Midpoint and All Is Lost MUST have opposite polarity
- Every storyline used in Acts 1-2 must appear in Act Three (payoff)

Respond with valid JSON only. No markdown, no commentary."""

    # ── Genre-Specific Board Construction Templates ───────────────────────
    # Each template describes HOW to distribute and structure the 40 scene cards
    # for that genre type. This is about card placement, scene types, and
    # escalation patterns -- not about what each beat MEANS (that was Step 4's job).

    GENRE_BOARD_TEMPLATES = {
        "monster_in_the_house": """
=== GENRE-SPECIFIC BOARD GUIDANCE: MONSTER IN THE HOUSE ===

The Board for a MITH story must create a TIGHTENING CAGE. The three required components
(Monster, House, Sin) must each be established and escalated across the 40 cards.

ROW 1 (Act One) -- ESTABLISH THE HOUSE AND THE SIN:
- Cards 1-3 (Set-Up): Establish the enclosed space ("the House") and why the characters are
  trapped in it. Show the sin or transgression that will invite the monster. The audience must
  feel the walls before the monster arrives.
- Card 4 (Catalyst): The monster is UNLEASHED -- not necessarily seen, but its first effect is
  felt. A door is opened, a rule is broken, something goes wrong.
- Cards 5-10 (Debate → Break into Two): Characters debate whether the threat is real. Some
  dismiss it. The hero commits to staying or investigating.

ROW 2 (Act Two A) -- ESCALATE THE MONSTER'S PRESENCE:
- Fun and Games cards: The "promise of the premise" is HIDE AND SEEK with the monster. Each
  card should escalate: unseen threat → glimpsed → direct encounter. The monster picks off
  secondary characters, each death more shocking than the last.
- B Story cards: The relationship that carries the theme should develop UNDER PRESSURE -- trust
  tested by fear, alliances formed in hiding.
- The House should feel SMALLER with each card -- exits sealed, resources dwindling.

ROW 3 (Act Two B) -- THE MONSTER DOMINATES:
- Bad Guys Close In: The monster becomes fully visible and dominant. The hero's early strategies
  fail. The group fractures as fear turns people against each other.
- The "Half Man" (the team member who secretly caused the sin or aids the monster) is revealed.
- All Is Lost: The monster seems unbeatable. A key ally is killed or the escape route is destroyed.
  Whiff of death is LITERAL in this genre -- someone close to the hero dies.

ROW 4 (Act Three) -- CONFRONT OR ESCAPE:
- Finale cards must show the hero CONFRONTING the monster directly using knowledge gained from
  surviving Acts 1-3. The sin must be acknowledged or atoned for.
- The House is either destroyed or the hero escapes it, but the monster is dealt with BECAUSE
  of what the hero learned about the sin that created it.
- Dispatch pattern: minor threats first, then the monster itself in the climax.
""",

        "golden_fleece": """
=== GENRE-SPECIFIC BOARD GUIDANCE: GOLDEN FLEECE ===

The Board for a Golden Fleece story must create a JOURNEY STRUCTURE. Each card is a waypoint.
The three required components (Road, Team, Prize) must be tracked across all 40 cards.

ROW 1 (Act One) -- ESTABLISH THE ORDINARY WORLD AND THE CALL:
- Cards 1-3 (Set-Up): Show the hero's stagnant life and what they lack. Establish the Road
  (where they're going) and the Prize (what they think they want).
- Card 4 (Catalyst): The hero receives the call to adventure -- a map, an invitation, a mission.
- Cards 5-10 (Debate → Break into Two): The hero assembles the team (or is forced to travel
  with unlikely companions). The journey begins.

ROW 2 (Act Two A) -- THE ROAD AND ITS CHALLENGES:
- Fun and Games cards: EACH CARD IS A DISTINCT WAYPOINT with its own location, challenge, and
  lesson. The road should feel like it's moving geographically. Each waypoint tests the team
  differently. The hero accumulates skills and allies.
- B Story: The relationship deepens through shared adversity on the road. Theme wisdom is
  delivered through road encounters, not speeches.
- Midpoint: A false victory -- the team reaches what they think is the Prize, or gets halfway
  there and celebrates. But the real journey is internal.

ROW 3 (Act Two B) -- THE TEAM FRACTURES:
- Bad Guys Close In: External threats intensify AND the team's internal tensions explode.
  Characters reveal hidden agendas or past betrayals.
- The road becomes hostile. Waypoints become traps. The Prize seems farther away.
- All Is Lost: The team splits apart, or the Prize is revealed to be a trap/illusion.
  The hero must face the road alone.

ROW 4 (Act Three) -- THE REAL PRIZE:
- The hero discovers the real Prize was what they gained on the journey itself (growth, love,
  community). Finale cards show the hero using accumulated road lessons to win.
- The team reunites for the final challenge if applicable.
- Final Image: The hero returns home (literally or metaphorically) transformed.
""",

        "out_of_the_bottle": """
=== GENRE-SPECIFIC BOARD GUIDANCE: OUT OF THE BOTTLE ===

The Board for an OOTB story must create a WISH ARC. The three required components
(Wish, Spell, Lesson) must be tracked. Fun and Games = wish fulfillment. BGCI = wish backfire.

ROW 1 (Act One) -- ESTABLISH THE WISH AND THE LACK:
- Cards 1-3 (Set-Up): Show what the hero desperately wishes for and why their current life
  is intolerable. Establish the specific dissatisfaction that makes the wish feel justified.
- Card 4 (Catalyst): The wish is GRANTED -- a spell, a swap, a magical event. The rules of
  the wish must be clear (or deliberately unclear, to be revealed later).
- Cards 5-10 (Debate → Break into Two): The hero discovers the wish is real. Initial delight
  mixed with confusion. The hero commits to exploiting the wish.

ROW 2 (Act Two A) -- WISH FULFILLMENT (THE FUN PART):
- Fun and Games cards: THIS IS THE TRAILER SEQUENCE. Each card shows the hero gleefully
  exploiting the wish. The audience lives vicariously through the wish fulfillment. Make it
  specific and escalating -- each use of the wish is bigger, bolder, more outrageous.
- B Story: The relationship that will deliver the lesson develops in contrast to the wish.
  The B-story character sees through the wish or is unaffected by it.
- Midpoint: False victory -- the wish seems to have solved everything. The hero has what they
  wanted. But something feels hollow.

ROW 3 (Act Two B) -- THE WISH BACKFIRES:
- Bad Guys Close In: The wish's CONSEQUENCES emerge. Each card reveals a new cost. The wish
  was a monkey's paw -- what the hero gained in one area, they lost in another. Relationships
  suffer, identity erodes, the hero loses what they actually needed.
- All Is Lost: The wish becomes a prison. The hero would give anything to undo it. The "death"
  is the death of the wished-for life -- the hero realizes the wish destroyed what mattered.

ROW 4 (Act Three) -- THE LESSON:
- The hero must earn their way back to reality. The Finale is NOT just undoing the wish -- it's
  the hero actively choosing to give up the wish because they've learned the lesson.
- The lesson: what you wished for was never what you needed. What you had (or could earn through
  growth) was the real prize.
- Final Image shows the hero in their original world, but transformed by the lesson.
""",

        "dude_with_a_problem": """
=== GENRE-SPECIFIC BOARD GUIDANCE: DUDE WITH A PROBLEM ===

The Board for a DwaP story must create ESCALATING SURVIVAL SET PIECES. The three required
components (Innocent Hero, Sudden Event, Life-or-Death Battle) must drive every card.

ROW 1 (Act One) -- ESTABLISH THE ORDINARY PERSON:
- Cards 1-3 (Set-Up): Show the hero's MUNDANE, RELATABLE life. They are competent in their
  small world but clearly not equipped for what's coming. Show their specific skills that will
  later become both asset and liability.
- Card 4 (Catalyst): The SUDDEN EVENT strikes -- an attack, a disaster, a kidnapping. It must
  be external, overwhelming, and impossible to ignore. The ordinary day is destroyed.
- Cards 5-10 (Debate → Break into Two): The hero tries to respond with normal-world tools and
  fails. They realize the scale of the problem is far beyond anything they've faced. They
  commit to fighting because there's no other choice.

ROW 2 (Act Two A) -- RESOURCEFULNESS UNDER PRESSURE:
- Fun and Games cards: THIS IS THE POSTER SEQUENCE. Each card is a SURVIVAL SET PIECE where
  the hero uses improvisation, street smarts, and personal ingenuity to stay alive. Each
  escape creates a new complication. The audience should think "what would I do?" The hero's
  ordinary skills are repurposed in extraordinary ways.
- B Story: The relationship develops UNDER FIRE -- trust built through shared danger.
- Midpoint: False victory -- the hero achieves a tactical win, thinks they've turned the tide.
  But the antagonist was testing them, learning their patterns.

ROW 3 (Act Two B) -- THE NET TIGHTENS:
- Bad Guys Close In: The antagonist ADAPTS to the hero's tactics. Each card shows a previous
  advantage being neutralized. Allies are compromised, safe houses are blown, escape routes
  are sealed. The hero is being herded.
- The hero's flaws (from Six Things That Need Fixing) become active liabilities under pressure.
- All Is Lost: The hero is trapped, outgunned, and exposed. All tools and allies are gone.
  Whiff of death: someone close to the hero is killed or the hero faces direct mortal danger.

ROW 4 (Act Three) -- INDIVIDUALITY AS THE WEAPON:
- Finale cards must show the hero winning through PERSONAL, IDIOSYNCRATIC means -- not by
  acquiring bigger weapons or calling in reinforcements. The hero's unique humanity (their
  relationships, their moral choices, their improvisation) is what the antagonist cannot counter.
- Dispatch pattern: the antagonist's lieutenants/proxies are neutralized in ascending order,
  then the hero faces the main antagonist directly.
- The climactic confrontation must hinge on a CLEVER, PERSONAL SOLUTION rather than brute force.
- Final Image shows the hero transformed by the ordeal -- no longer ordinary, but earned.
""",

        "rites_of_passage": """
=== GENRE-SPECIFIC BOARD GUIDANCE: RITES OF PASSAGE ===

The Board for a RoP story must create an INTERNAL PAIN ARC that manifests externally. The three
required components (Life Problem, Wrong Way, Acceptance) drive the structure.

ROW 1 (Act One) -- ESTABLISH THE LIFE PROBLEM:
- Cards 1-3 (Set-Up): Show the hero's surface-level life that hides a deep, universal pain
  (death, loss, addiction, aging, betrayal). The pain is present but the hero is in DENIAL --
  they have a coping mechanism that appears to work.
- Card 4 (Catalyst): An event FORCES the pain to the surface. A diagnosis, a breakup, a death,
  a rejection. The hero can no longer pretend things are fine.
- Cards 5-10 (Debate → Break into Two): The hero tries to return to denial. They resist
  acknowledging the pain. They choose the WRONG WAY to cope.

ROW 2 (Act Two A) -- THE WRONG WAY:
- Fun and Games cards: The hero doubles down on the wrong approach. Each card shows a SPECIFIC
  manifestation of the wrong coping mechanism. It may appear to work at first (this is the "fun"
  -- the audience relates to choosing the easy path). External consequences accumulate.
- B Story: Someone who has been through this pain (or a contrasting character who handles pain
  differently) enters the hero's life. They offer a mirror.
- Midpoint: False victory -- the wrong way seems to have solved the problem. Or false defeat --
  the hero hits bottom early and thinks they've accepted reality, but they're still avoiding it.

ROW 3 (Act Two B) -- PAIN CATCHES UP:
- Bad Guys Close In: The consequences of the Wrong Way multiply. Relationships crack. The
  hero's external world crumbles as the internal pain demands attention. The hero's coping
  mechanism stops working.
- All Is Lost: Complete breakdown. The hero has lost everything the Wrong Way was supposed
  to protect. The pain is fully exposed, raw, undeniable.

ROW 4 (Act Three) -- ACCEPTANCE:
- Finale cards must show the hero CHOOSING to face the pain directly instead of running.
  Acceptance is not giving up -- it's choosing to grow through the pain rather than around it.
- The hero applies the B-story lesson and rebuilds with honesty rather than avoidance.
- Final Image shows the hero at peace -- not that the pain is gone, but that it's integrated.
""",

        "buddy_love": """
=== GENRE-SPECIFIC BOARD GUIDANCE: BUDDY LOVE ===

The Board for a Buddy Love story must create a RELATIONSHIP ARC. The three required
components (Incomplete Hero, Counterpart, Complication) drive every card.

ROW 1 (Act One) -- ESTABLISH THE INCOMPLETE HERO:
- Cards 1-3 (Set-Up): Show what the hero is MISSING in their life. They are functioning but
  incomplete. Establish the specific gap that only the counterpart can fill.
- Card 4 (Catalyst): The hero MEETS the counterpart (or is forced together with them). First
  impressions are usually wrong -- the counterpart seems like the opposite of what the hero needs.
- Cards 5-10 (Debate → Break into Two): The hero resists the relationship. They try to get
  away from the counterpart. But circumstances force them together.

ROW 2 (Act Two A) -- THE RELATIONSHIP DEVELOPS:
- Fun and Games cards: The "promise of the premise" is the ODD COUPLE DYNAMIC. Each card
  shows the hero and counterpart forced into situations where their differences create both
  comedy and unexpected synergy. They begin to complement each other.
- B Story: A secondary relationship or external force that PRESSURES the main relationship.
- Midpoint: False victory -- the relationship seems to be working. They solve a problem
  together. But the Complication (the thing that should keep them apart) hasn't been faced yet.

ROW 3 (Act Two B) -- THE RELATIONSHIP FRACTURES:
- Bad Guys Close In: The Complication emerges full force. Social pressure, past secrets, third-
  party interference, or fundamental incompatibility threatens to break the relationship apart.
  Each card shows a new crack.
- All Is Lost: The relationship shatters. The hero and counterpart separate. The hero realizes
  what they've lost -- they were MORE with the counterpart, not less.

ROW 4 (Act Three) -- REUNION AND COMMITMENT:
- Finale cards show the hero CHOOSING the relationship despite the Complication. The hero must
  sacrifice something (pride, status, safety) to win the counterpart back.
- The Complication is resolved not by removing it but by the hero deciding it doesn't matter
  compared to what they gain.
- Final Image: The hero and counterpart together, both transformed by the relationship.
""",

        "whydunit": """
=== GENRE-SPECIFIC BOARD GUIDANCE: WHYDUNIT ===

The Board for a Whydunit story must create an INVESTIGATION ARC. The three required
components (Detective, Secret, Dark Turn) drive every card.

ROW 1 (Act One) -- ESTABLISH THE DETECTIVE AND THE CASE:
- Cards 1-3 (Set-Up): Show the detective's world and their specific flaw that will blind them
  to the truth. The detective believes they can see through anyone.
- Card 4 (Catalyst): The case arrives -- a crime, a mystery, an anomaly that demands investigation.
  The detective is drawn in by intellectual curiosity or obligation.
- Cards 5-10 (Debate → Break into Two): The detective begins investigating. Initial clues point
  in the wrong direction. The detective commits to following the trail.

ROW 2 (Act Two A) -- GATHERING CLUES:
- Fun and Games cards: Each card is a CLUE SCENE -- an interview, a discovery, a revelation.
  The detective assembles pieces of the puzzle. RED HERRINGS and genuine clues interleave.
  Each scene should make the audience think they know the answer -- then shift.
- B Story: The relationship that will reveal the detective's own dark truth. Often the detective
  develops a connection to someone involved in the case.
- Midpoint: A major clue breaks the case wide open -- but in the wrong direction. The detective
  thinks they've solved it. False victory.

ROW 3 (Act Two B) -- THE DARK TURN:
- Bad Guys Close In: The REAL truth begins to emerge, and it's darker than the detective
  expected. The investigation leads uncomfortably close to home. The detective's own secrets
  or complicity surface.
- The detective's certainty crumbles. Each card reveals another layer of deception.
- All Is Lost: The detective discovers they've been used, or that the truth implicates someone
  they trusted. The "death" is the death of certainty.

ROW 4 (Act Three) -- THE DARK TRUTH:
- Finale cards show the detective confronting the FULL TRUTH, which requires confronting their
  own flaw. The secret is revealed to have a WHY that is deeply human (not just "whodunit").
- The detective must choose between comfortable lies and painful truth.
- Final Image: The detective changed by what they learned about human nature -- usually darker,
  but more honest.
""",

        "fool_triumphant": """
=== GENRE-SPECIFIC BOARD GUIDANCE: FOOL TRIUMPHANT ===

The Board for a Fool Triumphant story must create an UNDERDOG ARC. The three required
components (Fool, Establishment, Transmutation) drive every card.

ROW 1 (Act One) -- ESTABLISH THE FOOL AND THE ESTABLISHMENT:
- Cards 1-3 (Set-Up): Show the Fool in their innocent, underestimated state. Establish the
  ESTABLISHMENT (the powerful, rigid system that looks down on the Fool). Show why the Fool
  seems utterly unsuited to win.
- Card 4 (Catalyst): The Fool is thrust into the Establishment's world -- through accident,
  opportunity, or obligation. The Establishment doesn't take them seriously.
- Cards 5-10 (Debate → Break into Two): The Fool tries to fit in and fails spectacularly.
  But their failures inadvertently expose the Establishment's absurdities.

ROW 2 (Act Two A) -- THE FOOL'S INNOCENT APPROACH WORKS:
- Fun and Games cards: The "promise of the premise" is watching the Fool succeed DESPITE
  themselves. Each card shows the Fool's naive, unconventional approach accidentally solving
  problems that the Establishment's rigid methods cannot. The audience roots for the underdog.
- B Story: Someone within the Establishment sees the Fool's value and becomes an ally.
- Midpoint: The Fool achieves a major win. The Establishment is shaken. The Fool begins to
  believe in themselves -- but this is dangerous because they might start trying to BE the
  Establishment instead of disrupting it.

ROW 3 (Act Two B) -- THE ESTABLISHMENT FIGHTS BACK:
- Bad Guys Close In: The Establishment mobilizes against the Fool. Humiliation, sabotage,
  formal opposition. The Fool's victories are reversed. The Fool may try to play the
  Establishment's game and lose their innocence.
- All Is Lost: The Fool is crushed by the Establishment's power. They've lost their advantage
  (innocence) and their allies. The "transmutation" -- the Fool must become something new.

ROW 4 (Act Three) -- THE FOOL TRIUMPHS BY BEING THEMSELVES:
- Finale cards show the Fool winning NOT by becoming what the Establishment respects, but by
  doubling down on what makes them different. The Fool's "weakness" becomes their weapon.
- The Establishment is changed or toppled by the Fool's example.
- Final Image: The Fool remains true to themselves but has earned genuine respect.
""",

        "institutionalized": """
=== GENRE-SPECIFIC BOARD GUIDANCE: INSTITUTIONALIZED ===

The Board for an Institutionalized story must create a GROUP DYNAMICS ARC. The three required
components (Group, Choice, Sacrifice) drive every card.

ROW 1 (Act One) -- ESTABLISH THE GROUP AND ITS SEDUCTION:
- Cards 1-3 (Set-Up): Show the hero as an outsider. Establish the GROUP (family, company, cult,
  military unit, gang) and why it's attractive. The group offers belonging, purpose, identity.
- Card 4 (Catalyst): The hero is invited or inducted into the group. The initiation.
- Cards 5-10 (Debate → Break into Two): The hero weighs joining fully. They see the group's
  rules and power. The hero commits to becoming a member.

ROW 2 (Act Two A) -- SEDUCTION AND ASCENT:
- Fun and Games cards: The hero rises within the group. Each card shows the benefits of
  belonging -- status, camaraderie, power, purpose. The group's code makes sense. The hero
  becomes invested in the group identity.
- B Story: A relationship that exists OUTSIDE the group, representing the hero's individual
  identity that the group threatens to consume.
- Midpoint: The hero reaches peak status within the group. False victory: they've arrived.
  They have power, respect, belonging.

ROW 3 (Act Two B) -- THE GROUP TURNS TOXIC:
- Bad Guys Close In: The dark side of the group emerges. Each card reveals a new demand:
  loyalty tests, moral compromises, punishment of dissent. The group requires the hero to
  choose between the group's code and their own conscience.
- The B-story relationship is threatened by the group's demands.
- All Is Lost: The hero is forced to commit an act that violates their core identity, or they
  witness the group destroy someone. The seduction is fully broken.

ROW 4 (Act Three) -- CHOICE AND SACRIFICE:
- Finale cards show the hero CHOOSING individual identity over group belonging. This choice
  comes at a SACRIFICE -- the hero loses the benefits of the group (status, safety, belonging).
- The hero may try to reform the group from within, or escape, or expose it.
- Final Image: The hero standing alone (or with the B-story person) -- poorer in status but
  richer in integrity.
""",

        "superhero": """
=== GENRE-SPECIFIC BOARD GUIDANCE: SUPERHERO ===

The Board for a Superhero story must create a POWERS-AND-NEMESIS ARC. The three required
components (Power, Nemesis, Curse) drive every card.

ROW 1 (Act One) -- ESTABLISH THE ORDINARY PERSON AND THE POWER:
- Cards 1-3 (Set-Up): Show the hero BEFORE the power. Establish their specific wound or
  inadequacy that the power will appear to solve. Show why they feel powerless.
- Card 4 (Catalyst): The hero GAINS the power (or is revealed to have it). The origin event.
- Cards 5-10 (Debate → Break into Two): The hero experiments with the power. They don't
  understand it yet. They debate whether to use it, hide it, or exploit it.

ROW 2 (Act Two A) -- USING THE POWER:
- Fun and Games cards: The "promise of the premise" is SEEING THE POWER IN ACTION. Each card
  is a set piece where the hero uses their power in increasingly impressive ways. But the
  Curse (the cost of the power) also appears in small doses.
- B Story: The relationship that grounds the hero in their human identity. The person who
  loves the hero for WHO they are, not WHAT they can do.
- Midpoint: The hero achieves public triumph with the power. But the NEMESIS (the equal and
  opposite force) is revealed or escalates. The nemesis is a dark mirror of the hero.

ROW 3 (Act Two B) -- THE NEMESIS AND THE CURSE:
- Bad Guys Close In: The Nemesis targets the hero's vulnerabilities. The Curse worsens -- each
  use of the power costs the hero something (health, relationships, sanity, humanity). The hero
  is torn between using the power and the damage it causes.
- The Nemesis attacks through the hero's human connections (B-story character is threatened).
- All Is Lost: The power fails, or the Curse reaches its peak. The hero is stripped of their
  power (temporarily or fully) and must face the Nemesis as their ordinary, wounded self.

ROW 4 (Act Three) -- THE CURSE BECOMES THE GIFT:
- Finale cards show the hero accepting BOTH the power AND its cost. The Curse is not removed --
  it's reframed. The hero learns that the power was always an expression of who they are, not
  a replacement for who they were.
- The final confrontation with the Nemesis is won not through raw power but through the hero's
  human qualities (the thing the Nemesis lacks).
- Final Image: The hero integrated -- powerful AND human, accepting the Curse as part of the gift.
""",
    }

    # ── Summarizers with no fallbacks ─────────────────────────────────────

    def _summarize_beat_sheet(self, step_4_artifact: Dict[str, Any]) -> str:
        """Build a formatted summary of the beat sheet for the prompt.

        Raises ValueError if the beat sheet is missing or empty.
        """
        beats = step_4_artifact.get("beats")
        if not beats or not isinstance(beats, list):
            raise ValueError(
                "Step 4 artifact is missing required field: 'beats' (list of 15 beats). "
                "Cannot build the Board without a beat sheet."
            )

        lines = []
        for beat in beats:
            if not isinstance(beat, dict):
                raise ValueError(f"Each beat must be a dict, got: {type(beat)}")
            num = beat.get("number")
            name = beat.get("name")
            desc = beat.get("description")
            if not name or not desc:
                raise ValueError(
                    f"Beat {num} is missing required fields 'name' and/or 'description'."
                )
            page = beat.get("target_page", "")
            polarity = beat.get("emotional_direction", "")
            act = beat.get("act_label", "")
            act_tag = f" [{act}]" if act else ""
            lines.append(
                f"  Beat {num} ({name}) [page {page}] [{polarity}]{act_tag}: {desc}"
            )

        midpoint_pol = step_4_artifact.get("midpoint_polarity", "")
        ail_pol = step_4_artifact.get("all_is_lost_polarity", "")
        if midpoint_pol:
            lines.append(f"\n  Midpoint polarity: {midpoint_pol}")
        if ail_pol:
            lines.append(f"  All Is Lost polarity: {ail_pol}")

        return "\n".join(lines)

    def _summarize_characters(self, step_3_artifact: Dict[str, Any]) -> str:
        """Build a formatted summary of characters for the prompt, including Six Things.

        Raises ValueError if hero data is missing.
        """
        hero = step_3_artifact.get("hero")
        if not hero or not isinstance(hero, dict):
            raise ValueError(
                "Step 3 artifact is missing required field: 'hero' (dict with hero profile). "
                "Cannot build the Board without hero data."
            )

        hero_name = hero.get("name")
        if not hero_name:
            raise ValueError("Step 3 hero is missing required field: 'name'.")

        lines = []
        lines.append(
            f"  HERO: {hero_name} -- {hero.get('adjective_descriptor', '')} "
            f"({hero.get('archetype', '')})"
        )
        lines.append(f"    Goal: {hero.get('stated_goal', '')}")
        lines.append(f"    Need: {hero.get('actual_need', '')}")
        lines.append(f"    Save the Cat moment: {hero.get('save_the_cat_moment', '')}")
        lines.append(f"    Opening State: {hero.get('opening_state', '')}")
        lines.append(f"    Final State: {hero.get('final_state', '')}")
        hero_bio = (hero.get("character_biography") or "").strip()
        if hero_bio:
            lines.append(f"    Character biography: {hero_bio}")

        six_things = hero.get("six_things_that_need_fixing", [])
        if isinstance(six_things, list) and six_things:
            lines.append("    Six Things That Need Fixing:")
            for i, thing in enumerate(six_things, 1):
                lines.append(f"      {i}. {thing}")

        # Antagonist
        antag = step_3_artifact.get("antagonist")
        if isinstance(antag, dict) and antag.get("name"):
            lines.append(
                f"  ANTAGONIST: {antag.get('name')} -- {antag.get('adjective_descriptor', '')}"
            )
            lines.append(f"    Power: {antag.get('power_level', '')}")
            lines.append(f"    Moral difference: {antag.get('moral_difference', '')}")
            lines.append(f"    Mirror: {antag.get('mirror_principle', '')}")
            antag_bio = (antag.get("character_biography") or "").strip()
            if antag_bio:
                lines.append(f"    Character biography: {antag_bio}")

        # B-story character
        b_char = step_3_artifact.get("b_story_character")
        if isinstance(b_char, dict) and b_char.get("name"):
            lines.append(
                f"  B-STORY: {b_char.get('name')} -- {b_char.get('relationship_to_hero', '')}"
            )
            lines.append(f"    Theme wisdom: {b_char.get('theme_wisdom', '')}")
            b_opening = b_char.get("opening_state", "")
            b_final = b_char.get("final_state", "")
            if b_opening:
                lines.append(f"    Opening State: {b_opening}")
            if b_final:
                lines.append(f"    Final State: {b_final}")
            b_bio = (b_char.get("character_biography") or "").strip()
            if b_bio:
                lines.append(f"    Character biography: {b_bio}")

        # Supporting cast (Step 3b) merged into Step 3 context by the orchestrator
        supporting_chars = step_3_artifact.get("supporting_characters")
        if not isinstance(supporting_chars, list):
            supporting_cast = step_3_artifact.get("supporting_cast", {})
            if isinstance(supporting_cast, dict):
                supporting_chars = supporting_cast.get("characters", [])

        if isinstance(supporting_chars, list) and supporting_chars:
            lines.append("  SUPPORTING CAST:")
            for idx, char in enumerate(supporting_chars, 1):
                if not isinstance(char, dict):
                    continue
                name = (char.get("name") or "").strip()
                if not name:
                    continue
                role = char.get("role", "")
                rel = char.get("relationship_to_hero", "")
                lines.append(f"    {idx}. {name} ({role}) -- {rel}")

                trait = (char.get("distinctive_trait") or "").strip()
                if trait:
                    lines.append(f"       Distinctive trait: {trait}")

                voice = (char.get("voice_profile") or "").strip()
                if voice:
                    lines.append(f"       Voice profile: {voice}")

                arc = (char.get("arc_summary") or "").strip()
                if arc:
                    lines.append(f"       Arc summary: {arc}")

                first_beat = (char.get("first_appearance_beat") or "").strip()
                if first_beat:
                    lines.append(f"       First appearance beat: {first_beat}")

        return "\n".join(lines)

    def _build_genre_board_guidance(self, genre: str) -> str:
        """Look up genre-specific board construction guidance.

        Returns the genre template if found, or a note that no template exists.
        """
        genre_key = genre.lower().strip()
        template = self.GENRE_BOARD_TEMPLATES.get(genre_key)
        if template:
            return template
        return (
            f"\n=== GENRE NOTE: '{genre}' does not have a genre-specific board template. ===\n"
            f"Follow the generic structural rules above faithfully.\n"
        )

    def _summarize_genre_rules(self, step_2_artifact: Dict[str, Any]) -> str:
        """Extract genre rules and conventions from Step 2 for board context."""
        lines = []

        rules = step_2_artifact.get("rules", [])
        if isinstance(rules, list):
            for rule in rules:
                lines.append(f"  - {rule}")

        conventions = step_2_artifact.get("conventions", [])
        if isinstance(conventions, list):
            for conv in conventions:
                lines.append(f"  - {conv}")

        working_parts = step_2_artifact.get("working_parts", [])
        if isinstance(working_parts, list):
            for wp in working_parts:
                if isinstance(wp, dict):
                    part_name = wp.get("part_name", "")
                    story_element = wp.get("story_element", "")
                    if part_name and story_element:
                        lines.append(f"  - {part_name}: {story_element}")

        return "\n".join(lines) if lines else "No genre rules available"

    # ── World & Cast Context Builders ──────────────────────────────────────

    def _build_world_context(self, step_3b_artifact):
        """Build world bible context for board construction prompt."""
        if not step_3b_artifact:
            return ""

        lines = []

        # Arena
        arena = step_3b_artifact.get("arena", {})
        if isinstance(arena, dict):
            desc = arena.get("description", "")
            if desc:
                lines.append(f"Arena: {desc}")
            scope = arena.get("scope", "")
            if scope:
                lines.append(f"Scope: {scope}")
            time_period = arena.get("time_period", "")
            if time_period:
                lines.append(f"Time Period: {time_period}")

        # Key locations — these are the places scenes should take place in
        geography = step_3b_artifact.get("geography", {})
        if isinstance(geography, dict):
            landscape = geography.get("landscape", "")
            if landscape:
                lines.append(f"Landscape: {landscape}")
            climate = geography.get("climate", "")
            if climate:
                lines.append(f"Climate: {climate}")
            locations = geography.get("key_locations", [])
            if isinstance(locations, list) and locations:
                lines.append("Key Locations (use these for scene headings):")
                for loc in locations:
                    if isinstance(loc, dict):
                        name = loc.get("name", "")
                        loc_type = loc.get("type", "")
                        atmosphere = loc.get("atmosphere", "")
                        significance = loc.get("significance", "")
                        if name:
                            entry = f"  - {name}"
                            if loc_type:
                                entry += f" [{loc_type}]"
                            if atmosphere:
                                entry += f" — {atmosphere}"
                            lines.append(entry)
                            if significance:
                                lines.append(f"    Significance: {significance}")

        # Culture and daily life for atmosphere
        culture = step_3b_artifact.get("culture", {})
        if isinstance(culture, dict):
            values = culture.get("values", "")
            if values:
                lines.append(f"Cultural Values: {values}")

        daily_life = step_3b_artifact.get("daily_life", {})
        if isinstance(daily_life, dict):
            sensory = daily_life.get("sensory_palette", "")
            if sensory:
                lines.append(f"Sensory Palette: {sensory}")

        # Rules of conflict
        conflict = step_3b_artifact.get("rules_of_conflict", {})
        if isinstance(conflict, dict):
            engine = conflict.get("story_engine", "")
            if engine:
                lines.append(f"Story Engine: {engine}")
            stakes = conflict.get("stakes", "")
            if stakes:
                lines.append(f"Stakes: {stakes}")

        if not lines:
            return ""
        return "\n".join(lines)

    def _build_cast_context(self, step_3c_artifact):
        """Build supporting cast context for board construction prompt."""
        if not step_3c_artifact:
            return ""

        lines = []

        # Tier 1 — Major Supporting (full details for board placement)
        tier1 = step_3c_artifact.get("tier_1_major_supporting", [])
        if isinstance(tier1, list) and tier1:
            lines.append("MAJOR SUPPORTING CHARACTERS (use in board cards):")
            for char in tier1:
                if not isinstance(char, dict):
                    continue
                name = char.get("name", "")
                role = char.get("role", "")
                rel = char.get("relationship_to_hero", "")
                arc = char.get("arc_summary", "")
                scenes = char.get("scenes_likely", [])
                if name:
                    entry = f"  - {name}"
                    if role:
                        entry += f" ({role})"
                    if rel:
                        entry += f" — {rel}"
                    lines.append(entry)
                    if arc:
                        lines.append(f"    Arc: {arc}")
                    if scenes:
                        lines.append(f"    Likely appears in cards: {scenes}")

        # Tier 2 — Minor Supporting (with micro_arc for board arc tracking)
        tier2 = step_3c_artifact.get("tier_2_minor_supporting", [])
        if isinstance(tier2, list) and tier2:
            lines.append("MINOR SUPPORTING CHARACTERS (include in board cards with arc tracking):")
            for char in tier2:
                if not isinstance(char, dict):
                    continue
                name = char.get("name", "")
                role = char.get("role", "")
                micro_arc = char.get("micro_arc", "")
                if name:
                    entry = f"  - {name}"
                    if role:
                        entry += f" ({role})"
                    lines.append(entry)
                    if micro_arc:
                        lines.append(f"    Micro-arc: {micro_arc}")
                    else:
                        lines.append(f"    (No micro-arc defined — assign a within-scene arc)")

        # Tier 3 — Background Types
        tier3 = step_3c_artifact.get("tier_3_background_types", [])
        if isinstance(tier3, list) and tier3:
            type_names = []
            for t in tier3:
                if isinstance(t, dict):
                    tn = t.get("type_name", "")
                    if tn:
                        type_names.append(tn)
            if type_names:
                lines.append("BACKGROUND TYPES: " + ", ".join(type_names))

        if not lines:
            return ""
        return "\n".join(lines)

    # ── Prompt Generation ─────────────────────────────────────────────────

    def generate_prompt(
        self,
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3b_artifact: Dict[str, Any] = None,
        step_3c_artifact: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Step 5: The Board.

        Args:
            step_4_artifact: The validated Step 4 beat sheet artifact.
            step_3_artifact: The validated Step 3 hero/character artifact.
            step_1_artifact: The validated Step 1 logline artifact.
            step_2_artifact: The validated Step 2 genre artifact.

        Returns:
            Dict with system and user prompts plus metadata.

        Raises:
            ValueError: If any required upstream field is missing.
        """
        # Extract required fields from Step 1
        title = step_1_artifact.get("title")
        if not title:
            raise ValueError("Step 1 artifact is missing required field: 'title'")
        logline = step_1_artifact.get("logline")
        if not logline:
            raise ValueError("Step 1 artifact is missing required field: 'logline'")

        # Extract required fields from Step 2
        genre = step_2_artifact.get("genre")
        if not genre:
            raise ValueError("Step 2 artifact is missing required field: 'genre'")

        beat_sheet_summary = self._summarize_beat_sheet(step_4_artifact)
        character_summary = self._summarize_characters(step_3_artifact)
        genre_rules = self._summarize_genre_rules(step_2_artifact)
        genre_board_guidance = self._build_genre_board_guidance(genre)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            genre=genre,
            beat_sheet_summary=beat_sheet_summary,
            character_summary=character_summary,
            genre_rules=genre_rules,
            genre_board_guidance=genre_board_guidance,
        )

        # Inject world and cast context if available
        world_context = self._build_world_context(step_3b_artifact)
        cast_context = self._build_cast_context(step_3c_artifact)

        extra_context = ""
        if world_context:
            extra_context += f"\nWORLD CONTEXT (Step 3b — World Bible — use these locations for scene headings):\n{world_context}\n"
        if cast_context:
            extra_context += f"\nSUPPORTING CAST (Step 3c — Full Cast — include in characters_present):\n{cast_context}\n"

        if extra_context:
            # Insert before "INSTRUCTIONS:" section
            marker = "INSTRUCTIONS:"
            if marker in user_prompt:
                user_prompt = user_prompt.replace(
                    marker,
                    extra_context + "\n" + marker,
                    1,  # Only replace first occurrence
                )
            else:
                user_prompt += extra_context

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_revision_prompt(
        self,
        previous_response: Dict[str, Any],
        validation_errors: List[str],
        fix_suggestions: List[str],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3b_artifact: Dict[str, Any] = None,
        step_3c_artifact: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """
        Generate a revision prompt to fix validation errors.

        Args:
            previous_response: The artifact that failed validation.
            validation_errors: List of validation error strings.
            fix_suggestions: List of fix suggestion strings.
            step_4_artifact: The Step 4 beat sheet artifact.
            step_3_artifact: The Step 3 hero/character artifact.
            step_1_artifact: The Step 1 logline artifact.
            step_2_artifact: The Step 2 genre artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        title = step_1_artifact.get("title", "")
        logline = step_1_artifact.get("logline", "")
        genre = step_2_artifact.get("genre", "")

        beat_sheet_summary = self._summarize_beat_sheet(step_4_artifact)
        character_summary = self._summarize_characters(step_3_artifact)

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2),
            errors=error_text,
            suggestions=suggestion_text,
            title=title,
            logline=logline,
            genre=genre,
            beat_sheet_summary=beat_sheet_summary,
            character_summary=character_summary,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }

