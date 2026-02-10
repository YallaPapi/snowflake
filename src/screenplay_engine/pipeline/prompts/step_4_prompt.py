"""
Step 4 Prompt Template: Beat Sheet (BS2)
Generates the 15-beat Blake Snyder Beat Sheet from logline, genre, hero, and Snowflake artifacts.

v3.0.0 -- Genre-specific beat manifestation templates added from "Save the Cat Goes to the Movies."
Each of Snyder's 10 structural genres now has its own beat-by-beat guidance describing HOW each
of the 15 beats plays out specifically for that genre type. No fallback defaults -- all required
fields raise ValueError if missing.
"""

import hashlib
from typing import Dict, Any


class Step4Prompt:
    """Prompt generator for Screenplay Step 4: Beat Sheet (BS2)"""

    VERSION = "3.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! beat sheet architect. "
        "Generate exactly 15 beats following the Blake Snyder Beat Sheet (BS2) "
        "with hard page/percentage targets. Every beat description must be "
        "1-2 sentences MAX -- Snyder: 'if I can't fill in the blank in one or "
        "two sentences, I don't have the beat yet.' "
        "Output ONLY valid JSON. No markdown, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Generate a 15-beat Blake Snyder Beat Sheet (BS2) for the following story.

LOGLINE:
{logline}

TITLE: {title}

GENRE: {genre}
Genre Rules: {genre_rules}

HERO:
- Name: {hero_name}
- Archetype: {hero_archetype}
- Primal Motivation: {hero_motivation}
- Stated Goal: {hero_stated_goal}
- Actual Need: {hero_actual_need}
- Save the Cat Moment: {save_the_cat_moment}
- Six Things That Need Fixing: {six_things}
- Opening State: {opening_state}
- Final State: {final_state}

ANTAGONIST:
- Name: {antagonist_name}
- Power Level: {antagonist_power}
- Mirror Principle: {antagonist_mirror}

B-STORY CHARACTER:
- Name: {b_story_name}
- Relationship: {b_story_relationship}
- Theme Wisdom: {b_story_wisdom}

SNOWFLAKE NARRATIVE STRUCTURE:
- One-Sentence Summary: {snowflake_sentence}
- Moral Premise: {snowflake_moral}
- Disaster 1: {snowflake_disaster_1}
- Disaster 2: {snowflake_disaster_2}
- Disaster 3: {snowflake_disaster_3}
- Synopsis (if available): {snowflake_synopsis}

BEAT SHEET REQUIREMENTS (follow EXACTLY):

Each beat MUST have these fields:
- number (1-15)
- name (exact name from list below)
- act_label ("thesis", "antithesis", or "synthesis")
- target_page (string, e.g. "1" or "30-55")
- target_percentage (string, e.g. "0-1%" or "27-50%")
- description (1-2 sentences MAX -- concise and specific to THIS story)
- snowflake_mapping (which Snowflake output feeds this beat)
- emotional_direction ("up", "down", or "neutral")

THESIS / ANTITHESIS / SYNTHESIS (Snyder's Three-World Model):
- Act 1 = THESIS (the world as it is, the old way of thinking)
- Act 2 = ANTITHESIS (the upside-down world, where the old way is tested and broken)
- Act 3 = SYNTHESIS (the hero merges old and new into something better, a new world order)
- Beats 1-6 are THESIS, Beats 7-12 are ANTITHESIS, Beats 13-15 are SYNTHESIS

THE 15 BEATS (in order):

=== ACT ONE: THESIS (the world as it is) ===

1. Opening Image - page 1, 0-1% - act_label: "thesis"
   Sets the tone, mood, and scope of the film. Shows a "before" snapshot of the hero.
   MUST be the visual OPPOSITE of the Final Image -- these are bookends, "a plus and a minus,
   showing change so dramatic it documents the emotional upheaval that the movie represents."

2. Theme Stated - page 5, ~5% - act_label: "thesis"
   Someone OTHER than the hero poses a question or makes a statement that is the movie's
   thematic premise. It's conversational, an offhand remark the hero doesn't fully grasp yet
   -- but it will have far-reaching impact later. This is the opening bid of the movie's
   central argument. The rest of the movie proves or disproves this statement.

3. Set-Up - pages 1-10, 1-10% - act_label: "thesis"
   Introduce ALL A-story characters. Plant the "Six Things That Need Fixing" -- character
   tics and flaws that will be turned on their heads later. Establish the hero's STAKES and
   GOAL. This is the THESIS world: a full documentation of the hero's life labeled "Before."
   Convey that maintaining the status quo = death; change is coming.

4. Catalyst - page 12, ~10% - act_label: "thesis"
   A single, definite, life-changing EXTERNAL EVENT -- a telegram, getting fired, news of
   a death, a knock at the door. NOT gradual. "The first moment when something happens!"
   Often arrives as BAD NEWS that ultimately leads to the hero's growth. Page 12 -- do it.

5. Debate - pages 12-25, 10-23% - act_label: "thesis"
   The hero's last chance to say no. This section MUST pose a QUESTION: "But can she pull
   it off?", "Should he go?", "Dare I try?" Shows how daunting the feat will be. The answer
   to the Debate question propels the hero into Act Two.

6. Break into Two - page 25, ~23% - act_label: "thesis"
   MUST be the hero's PROACTIVE CHOICE. "The Hero cannot be lured, tricked or drift into
   Act Two. The Hero must make the decision himself." The hero leaves the THESIS world
   behind and steps into the ANTITHESIS -- the upside-down version. Point of no return.
   (Use words like "chooses", "decides", or "commits".)

=== ACT TWO: ANTITHESIS (the upside-down world) ===

7. B Story - page 30, ~27% - act_label: "antithesis"
   Introduces NEW characters we have not met in Act One -- funhouse mirror versions of
   the Thesis world characters. Usually "the love story" and always carries the THEME.
   Provides a needed breather from the A-story -- a "booster rocket" smoothing the jarring
   Act Break. These B-story characters provide vital cutaways from the A-story.

8. Fun and Games - pages 30-55, 27-50% - act_label: "antithesis"
   "The promise of the premise!" The heart of the movie -- the core of the poster, where
   all the trailer moments live. LIGHTER in tone. Forward progress of the story is NOT
   the primary concern here -- stakes won't be raised until the Midpoint. We just want to
   see: what is COOL about this premise?

9. Midpoint - page 55, ~50% - act_label: "antithesis"
   Either a FALSE VICTORY (up) where the hero seemingly peaks, or a FALSE DEFEAT (down)
   where the world collapses. "It's never as good as it seems at the Midpoint." The Fun
   and Games are OVER. Stakes are RAISED -- it's back to the story. Opposite polarity of
   All Is Lost. Must be one or the other -- pick now, it's like nailing a spike into a wall.

10. Bad Guys Close In - pages 55-75, 50-68% - act_label: "antithesis"
    EXTERNAL forces AND INTERNAL forces tighten their grip. The bad guys regroup and send
    in the heavy artillery. Internal dissent, doubt, and jealousy begin to disintegrate
    the hero's team. There is nowhere for the hero to go for help -- he is on his own and
    must endure. Downward trajectory.

11. All Is Lost - page 75, ~68% - act_label: "antithesis"
    OPPOSITE polarity of Midpoint. This is the "False Defeat" (or false victory, if
    Midpoint was down). "It's never as bad as it seems at the All Is Lost point." Must
    contain a "whiff of death" -- literal or symbolic (a death, a flower dying, news of
    a loss). Mentors classically die here so their students discover "they had it in them
    all along." This is the "Christ on the cross" moment: the old world, the old character,
    the old way of thinking dies, clearing the way for Synthesis.

12. Dark Night of the Soul - pages 75-85, 68-77% - act_label: "antithesis"
    The darkness right before the dawn. The hero is at absolute lowest -- hopeless, clueless.
    Can last five seconds or five minutes, but must be there. The hero must be beaten AND
    KNOW IT. Only when the hero yields control and admits humility does the solution emerge.
    "Oh Lord, why hast thou forsaken me?"

=== ACT THREE: SYNTHESIS (the new world -- fusion of old and new) ===

13. Break into Three - page 85, ~77% - act_label: "synthesis"
    A-story and B-story MERGE. Thanks to B-story characters and their conversations about
    theme, the hero finds the solution. An idea to solve the problem has emerged. The world
    of SYNTHESIS is at hand -- the fusion of Thesis and Antithesis into something new.

14. Finale - pages 85-110, 77-100% - act_label: "synthesis"
    The lessons learned from the B-story are APPLIED to solve the A-story problem. Character
    tics planted in the Set-Up are MASTERED -- the Six Things That Need Fixing are RESOLVED.
    Bad guys are dispatched in ascending order: lieutenants and henchmen first, then the Boss.
    The hero is PROACTIVE, not reactive. It's not enough for the hero to triumph -- he must
    CHANGE THE WORLD. A new world order is created. (Description MUST reference the hero
    taking action.)

15. Final Image - page 110, ~100% - act_label: "synthesis"
    MUST be the visual OPPOSITE of the Opening Image. This is your proof that change has
    occurred and it's real. "If you don't have that Final Image, or you can't see how it
    applies, go back and check your math, there is something not adding up in Act Two."

{genre_beat_template}

SNOWFLAKE MAPPINGS (embed in snowflake_mapping field):
- Opening Image: Step 0 + Step 1 (one-sentence summary tone)
- Theme Stated: Step 2 moral premise
- Set-Up: Steps 2-3 (characters and world)
- Catalyst: Step 4 synopsis inciting incident
- Debate: Synopsis hesitation period
- Break into Two: Disaster 1
- B Story: Step 5 characters
- Fun and Games: Synopsis 25-50%
- Midpoint: Disaster 2
- Bad Guys Close In: Synopsis 50-75%
- All Is Lost: Disaster 3
- Final Image: Opening Image opposite

POLARITY RULES:
- If Midpoint is a false victory (up), then All Is Lost MUST be down
- If Midpoint is a false defeat (down), then All Is Lost MUST be up
- Include "midpoint_polarity" and "all_is_lost_polarity" at the top level

OUTPUT FORMAT (strict JSON):
{{
  "beats": [
    {{
      "number": 1,
      "name": "Opening Image",
      "act_label": "thesis",
      "target_page": "1",
      "target_percentage": "0-1%",
      "description": "<1-2 sentences specific to this story>",
      "snowflake_mapping": "<which Snowflake output>",
      "emotional_direction": "neutral"
    }},
    ... (all 15 beats)
  ],
  "midpoint_polarity": "up",
  "all_is_lost_polarity": "down"
}}
"""

    REVISION_PROMPT_TEMPLATE = """Your previous beat sheet had validation errors. Fix them.

ERRORS:
{errors}

FIXES NEEDED:
{fixes}

PREVIOUS OUTPUT:
{previous_output}

Generate the corrected 15-beat BS2 as valid JSON. Follow the same output format.
Every beat needs: number, name, act_label, target_page, target_percentage, description,
snowflake_mapping, emotional_direction. Description must be 1-2 sentences MAX.
"""

    # ── Genre-specific beat manifestation templates ────────────────────
    # Source: "Save the Cat Goes to the Movies" by Blake Snyder (2007)
    # Each genre has its own structural path for how the 15 beats manifest.

    GENRE_BEAT_TEMPLATES = {
        "monster_in_the_house": """
=== GENRE-SPECIFIC BEAT GUIDANCE: MONSTER IN THE HOUSE ===
Required components: a MONSTER (supernatural in power, evil at core), a HOUSE (enclosed space
heroes cannot leave), and a SIN (transgression that invited the monster in).

How each beat manifests in this genre:
1. Opening Image: Establish the 'house' (enclosed world) in its normal state before the monster arrives.
2. Theme Stated: A line hints at the sin or vulnerability that will invite the monster -- often about mortality, trespassing, or the cost of ignorance.
3. Set-Up: Introduce the full cast as potential victims, establish the social hierarchy of the 'house,' and plant the specific sin (greed, lust, career over family, teenage recklessness) that will bring the monster.
4. Catalyst: An external event forces the hero into proximity with the monster's world -- a distress signal, a mysterious death, a stranger's arrival. The door is opened.
5. Debate: The hero wrestles with whether to engage -- investigate or ignore, pursue or walk away. The cautious voice is overruled by desire, duty, or curiosity, and the sin deepens.
6. Break into Two: The monster is physically admitted into the 'house' or the hero crosses into the monster's domain. Point of no return -- the monster is now inside.
7. B Story: Introduces a relationship connected to the monster's origin or a 'Half Man' (a survivor who has encountered the monster before and been damaged by it, like Quint in Jaws or the android Ash in Alien).
8. Fun and Games: The monster's early appearances are disturbing but still manageable -- hide-and-seek, red herrings, close calls. The monster is present but not yet lethal to the hero. This is the 'discovery and escalating discomfort' phase.
9. Midpoint: Stakes raised dramatically -- the monster's true scope is revealed or a false victory turns to horror. A and B stories cross. The 'fun' phase is over; what seemed isolated is now personal and inescapable.
10. Bad Guys Close In: The monster picks off victims one by one in escalating intensity (Turn, Turn, Turn -- the plot must change and intensify, not just go forward). The hero's team fractures under stress. Escape routes close.
11. All Is Lost: The deepest sin is exposed and/or the Half Man dies. The company's true greed is unmasked, the last person who could help is destroyed. 'Whiff of death' pervades every frame.
12. Dark Night of the Soul: Maximum isolation and despair -- the survivors know they may die, the hero is alone in the emptied house, the 'house' feels like a tomb. Despair is amplified by the enclosed space.
13. Break into Three: The hero synthesizes a desperate plan combining Act 1 self with Act 2 lessons -- destroy the house and flee, confess the sin and unite as a team, find the monster's hidden weakness.
14. Finale: The hero confronts the monster directly using Synthesis -- combining original qualities with hard-won wisdom. The sin is atoned for through sacrifice or courage. A and B stories cross for the last time.
15. Final Image: Mirror of the Opening Image showing transformation through survival -- the 'house' is either purged of evil or has consumed its prey entirely.
""",
        "golden_fleece": """
=== GENRE-SPECIFIC BEAT GUIDANCE: GOLDEN FLEECE ===
Required components: a ROAD (journey with chartable milestones), a TEAM (companions who embody
qualities the hero lacks), and a PRIZE (a primal goal that turns out to be a McGuffin once the
hero grows -- the real prize is always friendship and self-discovery).

How each beat manifests in this genre:
1. Opening Image: The hero in pre-journey stasis -- at home, stuck, incomplete. The hero has not yet begun to move.
2. Theme Stated: Someone voices the journey's real lesson before the hero understands it. The prize's true meaning is foreshadowed.
3. Set-Up: The team is introduced, each member with a unique 'Limp and Eyepatch' -- a distinctive skill or trait the hero lacks (heart, brains, soul, muscle). Brilliant individual introductions of each team member are almost required.
4. Catalyst: The journey becomes unavoidable -- the mission is assigned, the season starts, or the plan is laid out. The hero cannot simply stay home.
5. Debate: The hero questions whether the journey is worth taking. 'Can they do it?' The road ahead looks impossible.
6. Break into Two: The hero commits to the road and the journey officially begins. The full team gathers. There is no turning back.
7. B Story: A relationship forms that carries the journey's true theme. The B story character IS the real prize -- in retrospect.
8. Fun and Games: The 'promise of the premise' -- the team on the road hitting milestones. Each stop must have a reason and mean something; there is a lift of adventure and camaraderie. This is why we came to see the movie.
9. Midpoint: A false victory or false defeat that changes the journey's meaning. The prize starts to change meaning at this exact moment -- what started as an external goal begins to look different.
10. Bad Guys Close In: Internal team discord and external obstacles compound. Infighting grows, mutiny threatens. 'Road apples' (obstacles that stop the trip cold) pop up everywhere.
11. All Is Lost: The 'road apple' strikes -- the prize seems lost or meaningless. The journey appears to have been for nothing. A key team member may be lost.
12. Dark Night of the Soul: The team is broken, separated, or demoralized. The hero must decide: was the journey worth anything at all?
13. Break into Three: SYNTHESIS -- the team reunites with new understanding. A and B stories cross: the real prize becomes clear. The hero chooses meaning over the original goal.
14. Finale: The final leg of the journey tests everything learned. The prize transforms into something the hero did not originally seek. Heroes may not even win the literal prize, but they win something more valuable.
15. Final Image: The hero is transformed by the journey. The real fleece was always internal -- friendship, self-knowledge, or a birthright reclaimed.
""",
        "out_of_the_bottle": """
=== GENRE-SPECIFIC BEAT GUIDANCE: OUT OF THE BOTTLE ===
Required components: a WISH (clearly seen need to escape the ordinary), a SPELL (magic with strict
Rules and boundaries), and a LESSON (be careful what you wish for -- the hero must learn to do it
WITHOUT the magic, like Dumbo without the feather).

How each beat manifests in this genre:
1. Opening Image: The hero trapped in Stasis = Death -- an ordinary life that desperately needs change. The hero's current condition must justify magical intervention.
2. Theme Stated: The lesson of the magic is spoken before the hero understands it -- usually about being yourself or appreciating what you have. The real magic is always internal.
3. Set-Up: The hero's ordinary world in detail, showing exactly WHY they need or deserve the magic. Stasis = Death is established so the magic feels earned.
4. Catalyst: The wish is triggered or the curse descends -- often through a deceptively simple mechanism (a birthday wish, a lightning strike, a magic potion, a knock on the head). Suspend disbelief ONCE.
5. Debate: The hero grapples with whether to accept or resist the magic. The conditions are assembling but the full spell has not yet arrived.
6. Break into Two: The hero accepts (or is hit by) the magic and enters the 'upside-down world' of Act Two. The spell is cast. The hero's old life is now impossible.
7. B Story: A relationship that carries the theme and tests the magic's real purpose. The B story character represents what the hero truly needs, not what the magic provides.
8. Fun and Games: The 'promise of the premise' -- exploring the wish in maximum, delightful detail. Systematically work the concept: denial, horror, sharing with a Confidant, testing limits, rejection, then exploitation. This is WHY we came to see the movie.
9. Midpoint: A 'false victory' where the wish seems to be working perfectly -- but the lesson lurks underneath. Having the wish is not enough. The gap between what the hero wished for and what they actually need is revealed.
10. Bad Guys Close In: The Rules of the magic become restrictive; consequences escalate. The magic that seemed like a blessing is becoming a curse. The hero's real relationships suffer.
11. All Is Lost: The wish creates its worst consequence -- the hero is 'worse off than when this movie started.' The 'whiff of death' arrives and the wish has clearly made things worse, not better.
12. Dark Night of the Soul: The hero confronts what they have lost because of the magic. The hero realizes the magic was never the answer.
13. Break into Three: THE CRITICAL OOTB BEAT -- the hero resolves to 'do it without the magic.' This is Dumbo without the feather. The hero REJECTS the magic and commits to solving problems using genuine growth. A and B stories cross.
14. Finale: The hero proves growth by solving problems using what they learned, NOT the magic. The lesson is demonstrated through action, not words.
15. Final Image: The hero is back where they started but changed forever -- the real magic was always inside them. The opposite of the Opening Image's trapped condition.
""",
        "dude_with_a_problem": """
=== GENRE-SPECIFIC BEAT GUIDANCE: DUDE WITH A PROBLEM ===
Required components: an INNOCENT HERO (ordinary person dragged into the mess without asking),
a SUDDEN EVENT (comes without warning and thrusts the hero into a world of hurt), and a
LIFE-OR-DEATH BATTLE (continued existence of the individual, family, or society is at stake).

How each beat manifests in this genre:
1. Opening Image: Establish the hero's ordinary, mundane world -- the normalcy that is about to be shattered. The dude is minding his own business.
2. Theme Stated: The theme is stated as a question about survival, trust, or priorities -- something the hero does not yet understand will become life-or-death.
3. Set-Up: Show the hero's vulnerabilities, relationships, and the 'stasis = death' condition. Meanwhile, ominous forces gather unseen. The hero is stuck in a rut, unaware of what is coming.
4. Catalyst: The sudden event strikes WITHOUT WARNING, dragging the innocent hero into a world of hurt. This is the moment that defines DwaP -- it comes from nowhere and the hero had no part in causing it (terrorists storm the building, assassins kill the colleagues, the diagnosis arrives, the boat leaves).
5. Debate: The hero scrambles to assess the situation. Everyone seems suspicious, nothing makes sense, and the hero grasps for any foothold. The scope of the problem becomes clear.
6. Break into Two: The hero commits to action and enters the 'upside-down world' of survival -- there is no going back to normal life. The dude's problem becomes undeniable and personal.
7. B Story: The 'eye of the storm' relationship is introduced -- the one friendly ally in a sea of trouble. This character provides emotional respite and carries the thematic argument. The B story ally is often a love interest, a walkie-talkie confidant, or the one person who believes the hero.
8. Fun and Games: The 'promise of the premise' delivers the survival scenario we paid to see: the lone person on the run, the resourceful dude improvising against impossible odds. The hero uses ORDINARY-PERSON SKILLS in extraordinary ways. This is the core of the poster and trailer.
9. Midpoint: A 'false victory' where the hero seems to gain ground -- but the stakes are raised and the situation becomes more dangerous. The hero often meets the villain face-to-face for the first time (the 'mano a mano meeting').
10. Bad Guys Close In: External pressure intensifies as the antagonist zeros in, and internal cracks appear in the hero's composure or alliances. The dude's resourcefulness is stretched to its limit. The bad guys adapt and get smarter.
11. All Is Lost: The hero's efforts appear to have been for nothing and a 'whiff of death' signals all hope is gone. The villain gains a critical advantage. The hero is worse off than when the movie started.
12. Dark Night of the Soul: The hero is in a nether world -- neither safe nor able to move forward. A and B stories often cross as the hero's emotional wound is laid bare. The hero must face who they really are.
13. Break into Three: The hero tries Synthesis -- combining old ordinary-person skills with new survival knowledge gained through the ordeal. A and B stories converge as the hero commits to a final plan.
14. Finale: The hero confronts the villain in a climactic showdown, using everything learned to defeat the extraordinary threat with ordinary courage. A and B stories resolve together. The dude wins through individuality and resourcefulness, NOT superior force.
15. Final Image: The bookend image shows how the world has changed. The ordinary person who was minding their own business has become something more -- not by gaining powers, but by discovering inner strength.
""",
        "rites_of_passage": """
=== GENRE-SPECIFIC BEAT GUIDANCE: RITES OF PASSAGE ===
Required components: a LIFE PROBLEM (a universal passage we all understand -- puberty, midlife,
death, divorce, addiction), a WRONG WAY (a diversion from confronting the pain), and ACCEPTANCE
(the counterintuitive move of embracing pain, not avoiding it, is the only cure).

How each beat manifests in this genre:
1. Opening Image: The hero trapped in a life that looks fine on the surface but conceals pain or stagnation. The passage has not yet been acknowledged.
2. Theme Stated: The theme is posed as a question or statement the hero does not yet understand -- usually about acceptance, change, or what really matters in life.
3. Set-Up: Reveal the hero's 'stasis = death' condition and the life problem in full. Show the routines, relationships, and denial that define the hero's world before the passage forces change.
4. Catalyst: An inciting event forces the hero to confront the life problem -- the passage has begun whether the hero wants it or not (a diagnosis, a spouse leaving, a birthday, a death, a sentence to rehab).
5. Debate: The hero resists the change and debates whether to engage with the life problem at all, often making early 'wrong way' attempts. The pain is avoided.
6. Break into Two: The hero makes a choice (or has it forced on them) that plunges them into the 'upside-down world' -- the passage is now fully underway and there is no return to the old life.
7. B Story: A relationship that carries the thematic lesson -- through this person, the hero will eventually learn the truth about acceptance. Often includes a therapist, a group, a new love interest, or a 'false mentor' who embodies the wrong way.
8. Fun and Games: The 'promise of the premise' shows the hero trying the WRONG WAY -- the diversion that seems fun or logical but avoids the real pain. This is where mistakes compound. Each wrong choice makes things worse, but the hero cannot see it yet.
9. Midpoint: A 'false victory' where things seem to be getting better -- but the stakes are raised and the hero's progress is about to be challenged. The wrong way appears to be working.
10. Bad Guys Close In: The 'bad guys' of truth, consequence, and the hero's own compounded mistakes close in. Internal conflict intensifies and the wrong way stops working. The hero's denial crumbles.
11. All Is Lost: The hero is 'worse off than when this movie started' -- the wrong way has led to a dead end, and a 'whiff of death' forces the hero to face the hard truth. Someone may die or attempt to die.
12. Dark Night of the Soul: The hero sits in the ashes of the wrong way and is forced to look inward. The real emotional wound is laid bare. The A and B stories cross.
13. Break into Three: The hero achieves Synthesis -- combining the pain they have endured with a new understanding. Acceptance begins, often through a small but revelatory act. The hero stops running.
14. Finale: The hero confronts the life problem head-on and demonstrates acceptance -- the change they resisted is now embraced. The hero proves growth through action and emotional honesty.
15. Final Image: A bookend showing the transformation -- the hero has passed through the rite and emerged changed. The surface that looked fine in the Opening Image is now genuinely fine.
""",
        "buddy_love": """
=== GENRE-SPECIFIC BEAT GUIDANCE: BUDDY LOVE ===
Required components: an INCOMPLETE HERO (missing something physical, ethical, or spiritual),
a COUNTERPART (a unique catalyst character who makes completion come about), and a COMPLICATION
(the force keeping the two apart -- which is ironically what binds them together).

How each beat manifests in this genre:
1. Opening Image: The hero's world before the counterpart arrives, emphasizing isolation or incompleteness. The hero is not whole.
2. Theme Stated: A line or moment that articulates the lesson of completion the hero must learn -- what love or partnership really means.
3. Set-Up: Both the hero's deficiency AND the counterpart's contrasting nature are established. In a two-hander, we meet both buddies and their problems.
4. Catalyst: The buddies meet or are forced together by an external event -- often disruptive and unwanted. The meeting feels accidental or forced. The complication is present from the first moment.
5. Debate: The hero resists the partnership or questions whether it can work. The buddies clash over styles, values, or territory.
6. Break into Two: The hero chooses to enter the counterpart's world -- or a shared new world. A commitment is made (grudgingly or impulsively) to the partnership.
7. B Story: A secondary character or relationship that carries the theme and pushes the buddies toward each other. Often shows what the buddies' relationship COULD become.
8. Fun and Games: The 'honeymoon' of the relationship -- the promise of the premise. The buddies do things together that neither could do alone. This section sells the audience on WHY these two belong together.
9. Midpoint: Stakes raised as the relationship deepens past the point of no return, often with a public or semi-public acknowledgment. The buddies can no longer deny their connection.
10. Bad Guys Close In: External forces and internal doubts attack the relationship from multiple angles. The complication becomes unbearable. The buddies start to pull apart.
11. All Is Lost: The relationship appears destroyed -- the break-up, the betrayal, the separation, or the 'whiff of death.' The complication has seemingly won. This is the moment the audience fears most.
12. Dark Night of the Soul: The hero faces the void without the counterpart and confronts what is truly at stake. Each buddy realizes what they had and what they lost.
13. Break into Three: A and B stories cross as the hero commits fully to the relationship, fusing what was learned. The hero goes after the counterpart or makes the sacrifice needed.
14. Finale: The hero proves the relationship's value through action -- a race, a rescue, a confrontation, a confession. The complication is overcome through ego surrender and vulnerability.
15. Final Image: The hero is transformed by having known the counterpart -- the mirror opposite of the Opening Image's isolation. The incomplete person is now whole.
""",
        "whydunit": """
=== GENRE-SPECIFIC BEAT GUIDANCE: WHYDUNIT ===
Required components: a DETECTIVE (a hero who starts thinking he has seen it all but is unprepared
for what he will find), a SECRET (a dark truth about human nature), and a DARK TURN (the moment the
detective breaks his own rules in pursuit of the secret, making himself part of the crime).

How each beat manifests in this genre:
1. Opening Image: The world before the case begins, often establishing the seat of power or normalcy that will be dismantled.
2. Theme Stated: A line that hints at the dark truth the investigation will uncover. The theme is often about subterfuge, the cost of knowledge, or human darkness.
3. Set-Up: The detective's world and capabilities are established, along with initial clues that seem small but will prove enormous.
4. Catalyst: The detective gets the case -- often reluctantly or by accident. A crime, a disappearance, a mystery that demands investigation.
5. Debate: The detective questions whether the case is worth pursuing or whether he is in over his head. The scope of the investigation is assessed.
6. Break into Two: The detective commits to the case and crosses into the world of the investigation. The first story is filed, the first real lead is followed, the first real danger appears.
7. B Story: A relationship (mentor, love interest, or parallel investigator) where the theme is discussed and tested. The B story character often represents the detective's own vulnerability.
8. Fun and Games: The 'promise of the premise' -- the first blush of investigation as clues are turned over and the case can go anywhere. 'Follow the money,' trace the evidence, interview witnesses. Each answer spawns two new questions.
9. Midpoint: Stakes raised as A and B stories cross -- often a 'false victory' that conceals a deeper problem, or the 'dark turn' begins. The detective starts breaking his own rules or crossing moral lines to get closer to the truth.
10. Bad Guys Close In: The 'dark turn' takes full hold -- the detective uses subterfuge, breaks rules, and the investigation's danger escalates. The detective is now 'swimming in the same water' as the criminals.
11. All Is Lost: The investigation's progress is destroyed -- a lead collapses, a source dies, or the truth seems lost. The detective is 'worse off than when the movie started' and the darkness he pursued has touched him personally.
12. Dark Night of the Soul: The detective faces the lowest point and must decide whether to press on into the final chamber. The cost of knowing the truth becomes personal.
13. Break into Three: A and B stories cross as the detective makes a final commitment to uncover the truth, armed with what the B story taught. The detective chooses to go all the way.
14. Finale: The last little room is opened -- the truth is revealed and it implicates the detective or destroys assumptions. The trail doubles back onto those investigating the crime. The revelation is about US, not just the criminal.
15. Final Image: The revelation has changed the world -- or at least how we see it. The detective may not have changed, but WE have. The truth is now public, but the cost is permanent.
""",
        "fool_triumphant": """
=== GENRE-SPECIFIC BEAT GUIDANCE: FOOL TRIUMPHANT ===
Required components: a FOOL (an overlooked underdog who is naive about his own powers), an
ESTABLISHMENT (the powerful institution or group the fool comes up against), and a TRANSMUTATION
(the fool becomes someone or something new, often including a 'name change' or disguise).
Special character: the INSIDER -- a jealous figure who knows the fool has magic powers and tries to stop him.

How each beat manifests in this genre:
1. Opening Image: The fool in his limited, pre-adventure world where his 'foolishness' is on full display -- the underdog living a small life, overlooked by all.
2. Theme Stated: Someone voices the prejudice the fool will overcome -- 'We're looking for somebody else,' 'You'll never get in,' 'Nobody takes you seriously.'
3. Set-Up: The fool's naivete, isolation, overlooked talents, and Stasis=Death condition are established. The establishment's values and the Insider's jealousy are planted.
4. Catalyst: An inciting event propels the fool toward the establishment's world -- being expelled, dumped, embarrassed, or receiving a challenge that seems absurd.
5. Debate: The fool hesitates or prepares for the plunge -- the fool's inadequacy for the establishment's world is laid bare, making the leap seem absurd.
6. Break into Two: The fool physically enters the establishment's alien territory. The mismatch between fool and environment is maximum and promises fireworks (think: pink clothes at a gray institution).
7. B Story: The fool meets a love interest or mentor who will teach the thematic lesson -- someone from within the establishment who sees the fool's true value.
8. Fun and Games: The 'promise of the premise' delivers the comedy of the mismatch -- the fool's native values (honesty, naivete, unique skills) are consistently MISREAD by the establishment as something they are not. Near-misses of identity exposure. Only the Insider is suspicious. The fool accidentally succeeds by applying his own values in the establishment's world.
9. Midpoint: A 'false victory' where the fool accidentally reaches a pinnacle of success that he cannot fully claim -- promoted, famous, or celebrated, but unable to cash in as his true self. Stakes are raised.
10. Bad Guys Close In: The establishment fights back and the fool's ruse or position is threatened from multiple angles -- external investigation AND internal dishonesty converge. The Insider gets closer to exposing the truth.
11. All Is Lost: The fool's secret is about to be exposed or his borrowed world collapses. A 'whiff of death' threatens the fool's progress and the disguise is crumbling.
12. Dark Night of the Soul: The fool hits bottom and considers retreat -- furthest from both his old identity and his new one.
13. Break into Three: A and B stories cross to give the fool the push into the finale -- a dying mentor's blessing, an ally's encouragement, or the fool's own decision to stop pretending. The fool synthesizes who he was with what he has learned.
14. Finale: The fool triumphs by being authentically himself -- the fool's original 'foolish' qualities (honesty, naivete, unique knowledge) are revealed as wisdom. The establishment is changed. The Insider is won over or defeated. The transmutation is complete.
15. Final Image: Mirror of the opening showing total transformation -- the fool was never really a fool at all. The establishment's definition of 'fool' has been proven wrong.
""",
        "institutionalized": """
=== GENRE-SPECIFIC BEAT GUIDANCE: INSTITUTIONALIZED ===
Required components: a GROUP (a family, organization, or business with its own rules, ethics,
and bonds of loyalty), a CHOICE (will the hero stick with the group or quit? -- the ongoing
conflict pitting the individual against the system), and a SACRIFICE (a decision: them or me?
-- leading to one of three endings: join, burn it down, or commit spiritual 'suicide').
Key characters: the BRANDO (anti-hero who reveals the system's flaws), the NAIF (audience
surrogate who knows nothing of the rules), and the COMPANY MAN (automaton entrenched in the system).

How each beat manifests in this genre:
1. Opening Image: The institution's world is established through its atmosphere and the hero's position relative to it. The opening often contains a thematic image of what the institution costs.
2. Theme Stated: Someone articulates the central question of individual vs. group -- 'Can you remain yourself inside this machine?' The theme is always about whether conformity destroys or saves.
3. Set-Up: The institution's rules, hierarchy, and cast of characters are introduced. The Company Man is identified. The Naif's eagerness or reluctance is shown. The Brando is established as the anti-establishment force.
4. Catalyst: An event forces the hero to engage with the institution's power structure. The catalyst often frames the institution's first explicit demand for conformity.
5. Debate: The hero questions whether to engage, resist, or go along. The Naif weighs the cost of belonging against the cost of standing alone.
6. Break into Two: The hero enters the institution's 'upside-down world' with a decisive act of joining or commitment. The hero crosses from observer to participant.
7. B Story: A relationship that will carry the thematic argument -- often the character who represents what the hero could become, for better or worse.
8. Fun and Games: The hero exploring the institution's world and testing its boundaries -- the seduction of belonging. The institution seems manageable, even fun, while the cracks are only beginning to show.
9. Midpoint: A 'false victory' that raises the stakes and reveals what the institution truly demands -- not just loyalty, but complicity. A/B stories cross. The hero now sees the institution's true cost but is already in too deep.
10. Bad Guys Close In: The institution tightens its grip and the hero's position becomes untenable. The 'bad guys' are often internal -- the hero's own moral compromises closing in. The group's loyalty rules become impossible to follow honestly.
11. All Is Lost: The institution's ultimate betrayal is revealed. The 'whiff of death' is often literal in this genre -- someone dies, or the hero faces the real possibility of death (physical or spiritual). The institution has shown its true face.
12. Dark Night of the Soul: The hero is alone, stripped of illusions about the group. The hero must decide: join, resist, or destroy.
13. Break into Three: The hero makes the decisive choice -- them or me -- synthesizing Act One self with Act Two experience. A and B stories cross as the hero chooses to act on the inner voice rather than the group's rules.
14. Finale: The hero's choice plays out as one of three options: (1) JOIN the institution with eyes open, (2) BURN IT DOWN and destroy the system, or (3) SACRIFICE individuality (spiritual 'suicide'). The institution is confronted with its own hypocrisy.
15. Final Image: A mirror of the opening showing what the institution cost and what the hero gained or lost. The final image asks: Was the sacrifice worth it? Who really won -- the individual or the institution?
""",
        "superhero": """
=== GENRE-SPECIFIC BEAT GUIDANCE: SUPERHERO ===
Required components: a POWER (a gift or mission that makes the hero more than human -- for every
superpower there is a cosmic payback), a NEMESIS (an equally powerful opponent driven by self-will
rather than faith -- the nemesis is the 'self-made' dark mirror of the hero), and a CURSE (an
Achilles heel that balances the power -- being special means giving something up).
Note: This is the EXACT OPPOSITE of Dude with a Problem -- extraordinary person in ordinary circumstances.

How each beat manifests in this genre:
1. Opening Image: Establishes the hero BEFORE the power or in a fallen/diminished condition that bookends the Final Image. Show what 'ordinary' looks like for this extraordinary person.
2. Theme Stated: Someone voices the core tension of being special: the price of power, the meaning of duty, or the burden of being different. 'With great power comes great responsibility.'
3. Set-Up: The hero's world before transformation or during the curse's burden. The 'six things that need fixing,' the Nemesis introduced or hinted at, and the MASCOT (the ordinary person who humanizes the hero) appears.
4. Catalyst: An external event ignites the hero's path toward super-ness or introduces the opposing force. The call to use powers, or the nemesis's first move.
5. Debate: The hero hesitates at the threshold -- should he believe, accept, pursue? A series of refusals where the hero drags his feet about accepting the burden of being extraordinary.
6. Break into Two: The hero commits to the upside-down world, often PROCLAIMING a new identity. The curse of being special begins here as a painful, scary rebirth. The hero cannot go back to ordinary.
7. B Story: A relationship that mirrors or tests super-ness -- a super mate, love interest, or mentor group. Poses the question 'Can the Superhero have love AND a mission?' The answer is almost always complicated.
8. Fun and Games: The promise of the premise -- we watch the hero USE his power and it seems glorious. But the curse lurks beneath every triumph. This is the 'showcase the powers' phase.
9. Midpoint: False victory or false defeat; A and B stories cross, stakes are raised. The curse of human weakness begins to corrode the mission. The hero's dual identity creates unbearable tension.
10. Bad Guys Close In: Internal team fractures AND external Nemesis tightens the vise. The Superhero cannot outrun who he is. The Nemesis mirrors the hero -- same power, different motivation.
11. All Is Lost: The hero is stripped of his advantage -- the power is gone, the team is broken, or the hero faces the ultimate cost of his gift. The 'whiff of death' arrives as the curse exacts its price.
12. Dark Night of the Soul: The hero must decide who he truly is. Self-will alone cannot restore the power -- only faith, love, or surrender can. The hero is at his most human.
13. Break into Three: The hero recommits with new understanding. The missing component is always faith, love, or acceptance of the curse. The hero chooses to be extraordinary despite the cost.
14. Finale: The ultimate showdown with the Nemesis, always including a CRUCIFIXION BEAT where the hero is tortured, broken, or killed and then transcends. The hero proves that faith and selflessness defeat self-will and machination.
15. Final Image: Mirror-opposite of the Opening Image. The Superhero's journey ends in either glorious transcendence or sacrificial grace. The burden of being special is accepted.
""",
    }

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate the full prompt for Step 4 from previous step artifacts.

        All required fields are validated -- missing data raises ValueError
        instead of silently defaulting to placeholder text.
        """

        # ── Step 1 fields (required) ──────────────────────────────────
        logline = step_1_artifact.get("logline")
        if not logline:
            raise ValueError("Step 1 artifact is missing required field: 'logline'")
        title = step_1_artifact.get("title")
        if not title:
            raise ValueError("Step 1 artifact is missing required field: 'title'")

        # ── Step 2 fields (required) ──────────────────────────────────
        genre = step_2_artifact.get("genre")
        if not genre:
            raise ValueError("Step 2 artifact is missing required field: 'genre'")
        rules = step_2_artifact.get("rules")
        if not rules:
            raise ValueError("Step 2 artifact is missing required field: 'rules'")
        genre_rules = ", ".join(rules)

        # ── Step 3 fields (required) ──────────────────────────────────
        hero = step_3_artifact.get("hero")
        if not hero:
            raise ValueError("Step 3 artifact is missing required field: 'hero'")
        antagonist = step_3_artifact.get("antagonist")
        if not antagonist:
            raise ValueError("Step 3 artifact is missing required field: 'antagonist'")
        b_story = step_3_artifact.get("b_story_character")
        if not b_story:
            raise ValueError("Step 3 artifact is missing required field: 'b_story_character'")

        hero_name = hero.get("name")
        if not hero_name:
            raise ValueError("Step 3 hero is missing required field: 'name'")
        hero_archetype = hero.get("archetype")
        if not hero_archetype:
            raise ValueError("Step 3 hero is missing required field: 'archetype'")
        hero_motivation = hero.get("primal_motivation")
        if not hero_motivation:
            raise ValueError("Step 3 hero is missing required field: 'primal_motivation'")
        hero_stated_goal = hero.get("stated_goal")
        if not hero_stated_goal:
            raise ValueError("Step 3 hero is missing required field: 'stated_goal'")
        hero_actual_need = hero.get("actual_need")
        if not hero_actual_need:
            raise ValueError("Step 3 hero is missing required field: 'actual_need'")
        save_the_cat_moment = hero.get("save_the_cat_moment")
        if not save_the_cat_moment:
            raise ValueError("Step 3 hero is missing required field: 'save_the_cat_moment'")
        six_things = hero.get("six_things_that_need_fixing")
        if not six_things or len(six_things) != 6:
            raise ValueError("Step 3 hero must have exactly 6 'six_things_that_need_fixing'")
        opening_state = hero.get("opening_state")
        if not opening_state:
            raise ValueError("Step 3 hero is missing required field: 'opening_state'")
        final_state = hero.get("final_state")
        if not final_state:
            raise ValueError("Step 3 hero is missing required field: 'final_state'")

        antagonist_name = antagonist.get("name")
        if not antagonist_name:
            raise ValueError("Step 3 antagonist is missing required field: 'name'")
        antagonist_power = antagonist.get("power_level")
        if not antagonist_power:
            raise ValueError("Step 3 antagonist is missing required field: 'power_level'")
        antagonist_mirror = antagonist.get("mirror_principle")
        if not antagonist_mirror:
            raise ValueError("Step 3 antagonist is missing required field: 'mirror_principle'")

        b_story_name = b_story.get("name")
        if not b_story_name:
            raise ValueError("Step 3 b_story_character is missing required field: 'name'")
        b_story_relationship = b_story.get("relationship_to_hero")
        if not b_story_relationship:
            raise ValueError("Step 3 b_story_character is missing required field: 'relationship_to_hero'")
        b_story_wisdom = b_story.get("theme_wisdom")
        if not b_story_wisdom:
            raise ValueError("Step 3 b_story_character is missing required field: 'theme_wisdom'")

        # ── Snowflake fields (optional -- empty string if missing) ────
        snowflake_sentence = snowflake_artifacts.get("step_1", {}).get("one_sentence_summary", "")
        snowflake_moral = snowflake_artifacts.get("step_2", {}).get("moral_premise", "")

        step2_data = snowflake_artifacts.get("step_2", {})
        sentences = step2_data.get("sentences", {})
        snowflake_disaster_1 = sentences.get("disaster_1", "")
        snowflake_disaster_2 = sentences.get("disaster_2", "")
        snowflake_disaster_3 = sentences.get("disaster_3", "")

        snowflake_synopsis = snowflake_artifacts.get("step_4", {}).get(
            "synopsis_paragraphs", snowflake_artifacts.get("step_4", {}).get("content", "")
        )
        if isinstance(snowflake_synopsis, dict):
            snowflake_synopsis = " ".join(snowflake_synopsis.values())

        # ── Build genre-specific beat template ────────────────────────
        genre_beat_template = self._build_genre_beat_template(genre)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            logline=logline,
            title=title,
            genre=genre,
            genre_rules=genre_rules,
            hero_name=hero_name,
            hero_archetype=hero_archetype,
            hero_motivation=hero_motivation,
            hero_stated_goal=hero_stated_goal,
            hero_actual_need=hero_actual_need,
            save_the_cat_moment=save_the_cat_moment,
            six_things=", ".join(six_things),
            opening_state=opening_state,
            final_state=final_state,
            antagonist_name=antagonist_name,
            antagonist_power=antagonist_power,
            antagonist_mirror=antagonist_mirror,
            b_story_name=b_story_name,
            b_story_relationship=b_story_relationship,
            b_story_wisdom=b_story_wisdom,
            snowflake_sentence=snowflake_sentence,
            snowflake_moral=snowflake_moral,
            snowflake_disaster_1=snowflake_disaster_1,
            snowflake_disaster_2=snowflake_disaster_2,
            snowflake_disaster_3=snowflake_disaster_3,
            snowflake_synopsis=snowflake_synopsis,
            genre_beat_template=genre_beat_template,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def _build_genre_beat_template(self, genre: str) -> str:
        """Return genre-specific beat manifestation guidance.

        If the genre is not recognized, returns a notice that the LLM should
        follow the generic 15-beat structure above.
        """
        genre_key = genre.lower().strip()
        template = self.GENRE_BEAT_TEMPLATES.get(genre_key)
        if template:
            return template
        return (
            f"\n=== GENRE NOTE: '{genre}' does not have a genre-specific beat template. ===\n"
            f"Follow the generic 15-beat structure above faithfully.\n"
        )

    def generate_revision_prompt(
        self,
        errors: list,
        fixes: list,
        previous_output: str,
    ) -> Dict[str, str]:
        """Generate a revision prompt incorporating validation errors."""

        error_text = "\n".join(f"- {e}" for e in errors)
        fix_text = "\n".join(f"- {f}" for f in fixes)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            errors=error_text,
            fixes=fix_text,
            previous_output=previous_output,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
