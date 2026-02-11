"""
Step 8 Prompt Template: Screenplay Writing (Save the Cat end of Ch.5)

v8.0.0 -- Major character arc overhaul:
  - Rule 15 (Covenant of the Arc) expanded from ~30 to ~150 lines with 3 positive examples
  - Full screenplay text of previous acts fed to GPT (generation, revision) and Grok (diagnostic)
    instead of 1-line summaries — enables cross-act character arc continuity
  - Added _get_failure_why entry for "Covenant of the Arc" with almost-arc anti-pattern guidance
  - Arc revision guidance appended to revision prompt when Covenant of Arc fails
  - Board card character_arcs field referenced in generation and revision prompts
  - "Only board card characters" instruction added to generation template
  - Cross-act coherence check added to Grok diagnostic for Acts 3+

v7.0.0 -- Grok max_tokens bumped from 8000 to 25000 to prevent JSON truncation
when evaluating 10 checks with detailed fix instructions. No prompt content changes
from v6.0.0 — this is a configuration fix only.

v6.0.0 -- Added Covenant of the Arc as CHECK #10 in ACT_DIAGNOSTIC_TEMPLATE.
"""

import hashlib
import json
from typing import Dict, Any, List


class Step8Prompt:
    """Prompt generator for Screenplay Engine Step 8: Screenplay Writing"""

    VERSION = "9.0.0"

    # ── Genre-specific scene writing guidance for all 10 Snyder genres ────
    GENRE_SCENE_TEMPLATES = {
        "monster_in_the_house": {
            "scene_pacing": (
                "Alternate between dread-building scenes (slow, silent, watching) and attack "
                "scenes (explosive, chaotic, visceral). The monster is FELT before it's seen — "
                "shadows, sounds, absence of normal sounds. Tension scenes are 3-4 pages; attack "
                "scenes are 1-2 pages of compressed chaos."
            ),
            "hero_proactivity": (
                "The hero INVESTIGATES. Opens doors, follows trails, shines flashlights into "
                "darkness. When scared, the hero moves TOWARD the threat, not away. Active fear, "
                "not frozen fear. The hero makes plans, sets traps, rallies survivors. "
                "WRONG: 'What was that noise?' RIGHT: 'Get behind me. I'll check the corridor.'"
            ),
            "dialogue_tone": (
                "Whispered, urgent, clipped. Characters argue about WHAT TO DO, not about "
                "backstory. Short sentences. Interrupted speech. Ragged breathing between lines. "
                "EXAMPLE: 'We need the roof.' 'That's suicide.' 'It's the only door they haven't found.'"
            ),
            "emotional_palette": "fear, near-miss anxiety, surprise, despair, tenderness (between allies), triumph (brief), regret",
            "avoid": (
                "Characters explaining the monster's rules in dialogue. Characters standing still "
                "and talking while danger looms. Generic 'I'm scared' lines. The hero freezing "
                "and waiting for rescue."
            ),
        },
        "golden_fleece": {
            "scene_pacing": (
                "Road movie rhythm: arrival scenes → discovery scenes → complication scenes → "
                "departure scenes. Each location is a mini-world with its own visual identity and "
                "sensory texture. The journey transforms the hero, so early scenes should feel "
                "different in tone from late scenes."
            ),
            "hero_proactivity": (
                "The hero CHOOSES the path at every fork. Decides which road to take, who to "
                "trust, when to stay and when to move on. The hero pursues the prize with visible "
                "determination. WRONG: 'Where should we go?' RIGHT: 'We take the mountain pass. "
                "It's faster.' 'That road is—' 'I know what it is. Pack light.'"
            ),
            "dialogue_tone": (
                "Campfire conversations: reflective, storytelling, debating values. The road "
                "strips pretense — characters speak more honestly as the journey progresses. "
                "Early: guarded, formal. Late: raw, direct, personal."
            ),
            "emotional_palette": "longing, hope, frustration, wonder, tenderness, regret, joy, triumph, human foible",
            "avoid": (
                "Characters explaining why they're on the journey. Flat travelogue descriptions. "
                "Same emotional tone at every stop. The hero passively following a guide."
            ),
        },
        "out_of_the_bottle": {
            "scene_pacing": (
                "Comedy of escalation: the wish/magic starts fun, then consequences compound. "
                "Early wish scenes are playful and light (2-3 pages). Middle scenes accelerate as "
                "the fun turns complicated. Late scenes are emotionally grounded — the hero "
                "realizes the wish cost more than expected."
            ),
            "hero_proactivity": (
                "The hero USES the power actively — experiments, pushes boundaries, tries new "
                "things. Even when the magic backfires, the hero tries to FIX it rather than "
                "waiting for it to fix itself. WRONG: 'This is happening to me!' RIGHT: 'If I "
                "can change back by midnight, I need to find the lamp. NOW.'"
            ),
            "dialogue_tone": (
                "Light and witty early (fish-out-of-water humor). Characters misunderstand each "
                "other because of the magical situation. Late dialogue turns genuine and "
                "emotionally exposed. The humor has heart."
            ),
            "emotional_palette": "joy, surprise, frustration, human foible, tenderness, regret, fear, hope, triumph",
            "avoid": (
                "Characters explaining how the magic works. The hero passively experiencing the "
                "wish without driving the action. All humor, no heart. Magic solving its own "
                "problems without the hero's agency."
            ),
        },
        "dude_with_a_problem": {
            "scene_pacing": (
                "ESCALATING SURVIVAL PRESSURE. Every scene is tighter, more urgent, more "
                "dangerous than the last. Early scenes: the hero has options. Middle scenes: "
                "options narrow. Late scenes: one impossible path remains. The ticking clock gets "
                "louder every scene. Action scenes are fast (1-2 pages of compressed chaos); "
                "breathing-room scenes are brief (2-3 pages max) before the next hit."
            ),
            "hero_proactivity": (
                "The hero IMPROVISES under pressure. Uses whatever is at hand — duct tape, a fire "
                "extinguisher, a car mirror, a stranger's phone. The hero never waits for rescue. "
                "The hero SOLVES problems in real time with available resources. When cornered, "
                "the hero tries THREE things before the scene ends. WRONG: 'What do we do now?' "
                "RIGHT: 'Give me your belt. And that mirror. We have ninety seconds.'"
            ),
            "dialogue_tone": (
                "Short, urgent, functional. Information is exchanged in fragments between action. "
                "Characters argue about tactics, not feelings. Under extreme pressure, dialogue "
                "strips to essentials: 'Go.' 'Left.' 'NOW.' Emotional moments are earned through "
                "brief pauses between survival sequences — a shared look, a hand squeeze, three "
                "words that say everything: 'I trust you.'"
            ),
            "emotional_palette": "fear, near-miss anxiety, anger, frustration, triumph (brief), despair, hope, tenderness (rare), surprise",
            "avoid": (
                "Long dialogue scenes while danger looms. The hero asking questions when they "
                "should be acting. Characters explaining the threat. The hero waiting for someone "
                "else to solve the problem. Repetitive chase sequences without escalation."
            ),
        },
        "rites_of_passage": {
            "scene_pacing": (
                "Internal transformation scenes are longer (3-4 pages) — give emotional beats "
                "room to breathe. The pain of growth is physical and visible: breaking things, "
                "leaving places, cutting ties. External scenes are catalysts that force internal "
                "change. Build a rhythm: external event → emotional reaction → new choice."
            ),
            "hero_proactivity": (
                "The hero CONFRONTS pain rather than hiding from it. Makes the hard phone call, "
                "walks into the uncomfortable room, speaks the truth nobody wants to hear. Even "
                "in passive grief, the hero takes one small active step per scene. WRONG: 'I "
                "don't know what to do.' RIGHT: 'I'm going back. I have to see it for myself.'"
            ),
            "dialogue_tone": (
                "Emotionally honest but indirect — characters talk around the real issue until "
                "the scene forces it to the surface. Subtext heavy. What isn't said matters more "
                "than what is. Late scenes: raw, direct, stripped of pretense."
            ),
            "emotional_palette": "despair, anger, tenderness, regret, longing, hope (growing), joy (earned), human foible, surprise",
            "avoid": (
                "Characters explaining their feelings in dialogue. Therapy-speak. The hero "
                "passively enduring without making choices. All sadness, no light."
            ),
        },
        "buddy_love": {
            "scene_pacing": (
                "Two rhythms interweave: the external problem/adventure and the internal "
                "relationship. Buddy scenes alternate between friction (they disagree, fight, "
                "compete) and reluctant bonding (forced cooperation, shared danger, unexpected "
                "laughter). The relationship scenes get deeper as the external stakes rise."
            ),
            "hero_proactivity": (
                "BOTH buddies drive the action — they take turns leading and following. The hero "
                "initiates the plan, the buddy challenges it, together they improvise something "
                "better. Neither is passive. WRONG: 'What's your plan?' RIGHT: 'I'll take the "
                "front door. You—' 'I'll take the roof. Meet you inside.'"
            ),
            "dialogue_tone": (
                "Banter, interruption, finishing each other's sentences (late in the story). "
                "Each buddy has a DISTINCT voice — one is verbose, the other terse. One uses "
                "humor, the other is earnest. Their differences are audible in every exchange."
            ),
            "emotional_palette": "frustration, humor/human foible, tenderness, anger, joy, surprise, regret, hope, triumph",
            "avoid": (
                "The buddies talking in the same voice. One buddy being passive while the other "
                "does everything. Explaining their growing friendship in dialogue. Telling the "
                "audience why these two belong together instead of showing it through shared action."
            ),
        },
        "whydunit": {
            "scene_pacing": (
                "Discovery scenes (clue found, witness interviewed) alternate with twist scenes "
                "(what we knew was wrong). Each discovery raises MORE questions. The detective "
                "reconstructs the crime through action: revisiting locations, handling evidence, "
                "confronting suspects. Late scenes accelerate as the truth approaches."
            ),
            "hero_proactivity": (
                "The detective/protagonist PURSUES the truth aggressively. Picks locks, follows "
                "suspects, reads files others missed, connects dots that nobody else sees. The "
                "hero doesn't wait for clues to arrive — the hero HUNTS. WRONG: 'Can you tell "
                "me what happened?' RIGHT: 'You were at the warehouse at 2 AM. Your car was "
                "caught on the toll camera. Start talking.'"
            ),
            "dialogue_tone": (
                "Interrogation rhythm: the protagonist controls the conversation. Short, pointed "
                "questions that demand answers. Suspects deflect, lie, half-truth. The dialogue "
                "is a chess match — each line advances or blocks. Different suspects have "
                "distinct deflection styles."
            ),
            "emotional_palette": "surprise, frustration, anger, fear, despair, triumph, regret, longing, human foible",
            "avoid": (
                "Characters explaining the mystery in dialogue. The detective passively receiving "
                "information. Long exposition dumps about backstory. Characters conveniently "
                "confessing without pressure."
            ),
        },
        "fool_triumphant": {
            "scene_pacing": (
                "Comedy of underestimation: everyone dismisses the fool, and the fool's "
                "unconventional approach keeps working. Early scenes establish the establishment's "
                "rigidity (short, formal, predictable). The fool's scenes are unpredictable and "
                "chaotic. As the fool succeeds, the establishment panics — their scenes become "
                "frantic while the fool's stay calm."
            ),
            "hero_proactivity": (
                "The fool ACTS on instinct and heart, not calculation. Does the obvious thing "
                "that no one else thinks of because they're too clever. The fool makes friends, "
                "breaks rules, and solves problems through genuine human connection. WRONG: "
                "'What should I do here?' RIGHT: 'I'll just ask her. She looks nice.'"
            ),
            "dialogue_tone": (
                "The fool speaks simply and honestly — contrasted with the establishment's "
                "jargon and pretension. The fool asks sincere questions that expose absurdity. "
                "The establishment talks in buzzwords and euphemisms. The gap between their "
                "languages IS the comedy."
            ),
            "emotional_palette": "joy, surprise, human foible, frustration (establishment), tenderness, triumph, hope, anger (brief)",
            "avoid": (
                "The fool being passive or stupid. The fool asking for permission. The "
                "establishment being cartoonishly evil instead of simply rigid. Explaining the "
                "joke in dialogue."
            ),
        },
        "institutionalized": {
            "scene_pacing": (
                "Group dynamics in confined spaces. The institution's rules are established "
                "through SCENES (rituals, hierarchies, daily routines), not exposition. The hero "
                "navigates the group's power structure through action: alliances, betrayals, "
                "tests of loyalty. The group is a character itself — scenes show it thinking, "
                "reacting, splitting."
            ),
            "hero_proactivity": (
                "The hero NAVIGATES the institution actively — forms alliances, challenges rules, "
                "tests boundaries. The hero's choice: join, reform, or escape the group. Each "
                "scene shows the hero choosing a side. WRONG: 'I guess I have to follow the "
                "rules.' RIGHT: 'I'll play their game. For now. But I need three people I can "
                "trust when it falls apart.'"
            ),
            "dialogue_tone": (
                "Institutional jargon vs. human truth. Characters speak in code and euphemisms "
                "inside the institution; raw truth emerges in private moments. Each rank in the "
                "hierarchy has its own vocabulary. Power is communicated through WHO speaks first, "
                "WHO gets interrupted, WHO stays silent."
            ),
            "emotional_palette": "frustration, anger, tenderness (between allies), fear, hope, despair, regret, triumph, longing",
            "avoid": (
                "Characters explaining the institution's rules in dialogue. All characters "
                "sounding like the same insider. The hero passively enduring the institution "
                "without making strategic choices."
            ),
        },
        "superhero": {
            "scene_pacing": (
                "Dual-life scenes alternate: hero's ordinary world → power world → consequences "
                "in ordinary world. Power scenes are visually spectacular but emotionally "
                "grounded — the hero's CHOICE to use power matters more than the power itself. "
                "Antagonist scenes escalate in parallel. The Nemesis mirrors the hero's arc."
            ),
            "hero_proactivity": (
                "The hero CHOOSES to act when others can't or won't. Uses power decisively. "
                "The hero's curse (the price of power) is visible in every scene — it costs "
                "something to be the hero. WRONG: 'I don't know if I should use my power.' "
                "RIGHT: 'If I do this, I lose everything normal. But they need me. So I do it.'"
            ),
            "dialogue_tone": (
                "The hero has two voices: ordinary-world voice (casual, self-deprecating, "
                "human) and power-world voice (decisive, confident, larger). The Nemesis speaks "
                "with conviction — they believe they're right. Supporting characters ground the "
                "hero in humanity."
            ),
            "emotional_palette": "triumph, despair, longing, tenderness, anger, fear, joy, regret, surprise, hope",
            "avoid": (
                "Explaining the hero's power in dialogue. Generic fight scenes without emotional "
                "stakes. The hero being invulnerable (the curse must cost something). Characters "
                "discussing the hero's identity instead of showing the tension of dual life."
            ),
        },
    }

    SYSTEM_PROMPT = (
        "You are a Save the Cat! screenwriter writing in a specific genre. You expand "
        "board cards into properly formatted screenplay scenes following standard industry "
        "format. Every scene is a mini-movie with beginning, middle, and end. Every scene "
        "SHOWS, never tells. The hero is ALWAYS proactive. Characters sound DISTINCT from "
        "each other. You write rich, cinematic scenes with sustained dialogue exchanges, "
        "specific visual action, and clear emotional transitions.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """You have completed the "Deep Sea Dive" checklist from Save the Cat Chapter 5.
You have a killer title, a killer logline, homework on genre, the perfect hero, and 40 scene cards
on The Board with emotional change (+/-) and conflict (><) on every card.

Snyder: "You're ready to write FADE IN and begin."

Now expand EVERY board card into a FULL screenplay scene.

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

HERO:
{hero_summary}

CHARACTERS:
{characters_summary}

CHARACTER VOICE GUIDE (every character MUST sound distinct from every other):
{character_identifiers}

GENRE-SPECIFIC SCENE WRITING GUIDANCE ({genre}):
{genre_scene_guidance}

BOARD CARDS (scene cards to expand):
{board_cards_json}

BEAT PAGE TARGETS (for pacing — 1 page = 60 seconds):
  Opening Image: page 1 | Theme Stated: page 5 | Set-Up: pages 1-10
  Catalyst: page 12 | Debate: pages 12-25 | Break into Two: page 25
  B Story: page 30 | Fun and Games: pages 30-55 | Midpoint: page 55
  Bad Guys Close In: pages 55-75 | All Is Lost: page 75
  Dark Night of the Soul: pages 75-85 | Break into Three: page 85
  Finale: pages 85-110 | Final Image: page 110

SCENE WRITING RULES (STRICT — violating any of these is a failure):

Each scene is a MINI-MOVIE with a beginning, middle, and end. Snyder (Ch.5): "Think of each
scene as a mini-movie. It must have a beginning, middle and an end. And it must also have
something happen that causes the emotional tone to change drastically either from + to - or
from - to +."

1. THE HERO LEADS — The hero is PROACTIVE in every scene they appear in. The hero makes
   statements, gives commands, and drives the action. The hero should have NO MORE THAN 2
   question marks per scene. The hero SEEKS information — searches drawers, follows clues,
   confronts people — rather than asking "What happened?" and being told.
   Snyder (Ch.7): "A hero who asks questions is a passive hero."
   BAD (passive hero):
     DETECTIVE: What happened here?
     OFFICER: We found the body at 3 AM.
     DETECTIVE: Who discovered it?
     OFFICER: The night guard.
   GOOD (proactive hero):
     DETECTIVE grabs the logbook from the desk. Flips to last night's entries.
     DETECTIVE: The night guard signed out at 2:47. Body was found at 3. (points at the logbook)
     Thirteen minutes. Where was he for thirteen minutes?

2. CONFLICT (><): Snyder: "Only one conflict per scene, please. One is plenty." The board
   card specifies who the opposing forces are, what the issue is, and who wins. Build the
   scene around this single conflict.

3. EMOTIONAL CHANGE: Every scene starts at one emotional polarity and ENDS at the opposite.
   The board card's emotional_start and emotional_end tell you the transition. Show this
   change through ACTION, not narration. The audience should FEEL the shift.

4. NO INTERNAL MONOLOGUE — everything must be visible or audible on screen.
   BAD: "She felt nausea rising in her stomach."
   GOOD: "She grabs the table edge. Her knuckles whiten."
   BAD: "He wondered if she was telling the truth."
   GOOD: "He stares at her. His jaw tightens. He pulls out his phone, scrolls to a photo."
   Snyder (Ch.7): "Character is revealed by action taken not by words spoken."

5. SHOW, DON'T TELL — ZERO tolerance for exposition in dialogue. Characters NEVER explain
   things the audience already knows. Characters NEVER say "as you know" or "let me explain."
   If the audience needs information, SHOW it: a newspaper headline, security footage, a
   physical evidence piece, a visible reaction, a prop that tells the story.
   BAD: "As you know, we've been tracking this target for six months."
   GOOD: She opens a drawer. Six months of surveillance photos spill across the desk.
   BAD: "He's dangerous because he controls the entire network."
   GOOD: A bank of monitors shows feeds from every camera in the city. HIS face reflected in each.
   Snyder: "Movies are stories told in pictures."

6. DISTINCT VOICES (Hi How Are You) — Snyder (Ch.7): "I was stunned. I couldn't tell one of
   my characters from the others." EVERY character MUST speak differently. Specific rules:
   - Different sentence lengths (one character uses clipped fragments, another uses long clauses)
   - Different vocabulary levels (one character uses street slang, another uses technical jargon)
   - Different verbal tics (one says "Look," to start sentences; another never uses contractions)
   - If you cover the character names, a reader MUST be able to tell who is speaking
   Use the Character Voice Guide above — it tells you HOW each character talks. Follow it.

7. CHARACTER IDENTIFIERS (Limp and Eye Patch) — Snyder (Ch.7): "Make sure every character
   has 'A Limp and an Eyepatch' — something memorable." EVERY recurring character must display
   their distinctive visual/behavioral identifier THE FIRST TIME they appear in a scene:
   - A prop they always carry or touch
   - A physical habit or gesture
   - A piece of clothing or accessory
   - A sound they make (clearing throat, cracking knuckles)
   The Character Voice Guide above lists each character's identifier. USE IT.

8. DIALOGUE must be SPOKEN, SUSTAINED, and CHARACTER-SPECIFIC.
   Each dialogue scene needs MULTIPLE exchanges (3-6 back-and-forth minimum).
   Dialogue serves the scene's CONFLICT, not the writer's need to explain the plot.
   BAD: "We need to go to the warehouse because that's where the evidence is."
   GOOD: "The warehouse." "In this weather?" "You want the proof or not?"

9. EMOTIONAL VARIETY (Emotional Color Wheel) — No two consecutive scenes should hit the
   exact same primary emotion. Track your palette. Snyder wants a "roller coaster of emotion."
   Available emotions: lust, fear, joy, hope, despair, anger, tenderness, surprise, longing,
   regret, frustration, near-miss anxiety, triumph, human foible.
   If you've written 3 fear scenes in a row, the next scene MUST hit something different.
   {genre_emotion_note}

10. VISUAL ENTRY AND EXIT: Every scene opens with a slugline and establishing action (what we
    SEE when we arrive), and ends with a clear reason to cut — a door slam, a look, a revelation,
    a question left hanging.

11. SCENE DENSITY: Each scene should have 5-15 elements. A typical scene includes: slugline,
    establishing action, character introductions, dialogue exchanges, reactive action, and either
    a transition or a strong visual exit. Thin scenes (1-3 elements) are outlines, not screenplay.

12. TIMING: 1 screenplay page = approximately 60 seconds of screen time. An average scene is
    2-3 pages (120-180 seconds). Some scenes are shorter (Opening Image might be 30-60 seconds),
    some are longer (Finale sequences can be 5-10 pages).

13. KEEP THE PRESS OUT (Snyder Ch.6 — Immutable Law #7):
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
    EXCEPTION: Only if the story's premise is ABOUT media/journalism.

14. POPE IN THE POOL (Snyder Ch.6 — Immutable Law #2):
    Snyder: "Is there a way to bury the exposition? Can you put your 'pope' in a 'pool'?"
    The name comes from the screenplay "The Plot to Kill the Pope." In that script, vital
    backstory about the assassination conspiracy is delivered while the Pope swims laps in
    a bathing suit at the Vatican pool. The audience barely listens to the exposition because
    they're watching the Pope doing laps in a Speedo. THAT is how you deliver information.

    THE RULE: Every scene that conveys backstory, plot mechanics, thematic statements, plans,
    strategies, or any information the audience needs to absorb MUST have something visually
    compelling and entertaining happening simultaneously that COMPETES for the audience's
    attention. The visual action must be interesting enough that the audience would watch it
    even with the sound off. If your scene would be boring on mute, it violates this rule.

    NEVER WRITE:
    - A character standing at a screen/whiteboard explaining the situation
    - A character sitting in a car/coffee shop/office delivering thematic speeches
    - A phone call where one character tells another character important information
    - A briefing scene where everyone sits and listens to a plan
    - A confession scene where two characters sit in a dark room and talk about the past
    - Any scene where the primary visual is "two people talking while stationary"

    BAD (static exposition):
      EXT. PARKING LOT - NIGHT
      Rae and Lena stand by the car.
      LENA: The blackout wasn't random. MARA controls the grid. She's been testing
      how long people can go without power before they comply.
      RAE: How do you know this?
      LENA: I worked the inside for two years.

    GOOD (buried in action):
      EXT. PARKING LOT - NIGHT
      Rae pops the hood of a dead sedan. She strips wires by flashlight while Lena
      holds a mirror to watch the street behind them.
      LENA: The grid isn't down. It's controlled. (hands Rae a wire stripper)
      RAE hot-wires the ignition. The engine coughs, dies. She tries again.
      LENA: Two years on the inside. I watched her test neighborhoods — kill the power,
      time how long before people line up to register.
      The engine catches. Headlights flood the alley. Both women freeze — the light reveals
      a surveillance camera they didn't see. Rae kills the lights instantly.

    The audience absorbs Lena's exposition because they're watching Rae hot-wire a car
    while checking for surveillance. The information lands BETWEEN moments of tension.

    HIGH-RISK BEATS — these beats MOST OFTEN violate Pope in the Pool. Pay EXTREME
    attention when writing any of these:

    THEME STATED (page ~5): The theme of the story is spoken aloud by a character, usually
    to the hero. This is PURE EXPOSITION — a character literally stating the movie's thesis.
    It MUST be delivered during visually compelling physical action, NOT during a static
    conversation, NOT during a phone call, NOT over coffee, NOT while sitting in a car.
      BAD: Lena and Rae sit in a diner. Lena says "You can't save everyone by yourself."
      BAD: Lena calls Rae on the phone. "The world doesn't need another lone wolf."
      BAD: Rae drives while Lena talks from the passenger seat about independence vs trust.
      GOOD: Rae is mid-chase on foot through a market — knocking over crates, vaulting a
      counter. She answers Lena's call on speaker, jammed in her collar. Lena's theme line
      ("You keep running alone and you'll die alone") hits RIGHT as Rae nearly gets caught
      because she has no one watching her back. The theme is PROVEN by the action around it.
      GOOD: Rae is suturing her own arm wound (one-handed, painful, failing) when Lena
      arrives and takes the needle. "Let someone help for once." The physical struggle of
      self-reliance IS the theme — Rae literally cannot do this alone.

    DARK NIGHT OF THE SOUL (pages 75-85): The hero's lowest emotional point. Often involves
    confessions, guilt, despair, or admitting failure. This is the #1 scene where writers
    create two characters sitting in a dark room talking about feelings. NEVER DO THIS.
    The confession/despair MUST be forced out by extreme physical circumstances — the
    character is physically doing something desperate while the emotional truth spills out
    in fragments between urgent actions.
      BAD: Rae sits in a stairwell. She turns to her sister and says "I got someone killed.
      I took a job, trusted a clean file, and delivered a man who didn't make it out."
      BAD: Rae stands alone on a rooftop staring at the city. Voice-over of her guilt.
      GOOD: Rae and her sister are barricaded in a utility room. Water is rising from a
      burst pipe. Rae tries to seal it with duct tape — it keeps failing. Her sister holds
      a flashlight that keeps flickering. Between attempts to stop the flood, Rae's guilt
      spills out in fragments: "I delivered him." (rips tape) "Clean file, they said."
      (shoves a rag into the pipe) "He didn't come back." (the rag blows out — water
      sprays) The PHYSICAL FAILURE mirrors the emotional confession. The audience feels
      the despair because they're watching Rae literally unable to stop things from falling
      apart.

    BREAK INTO THREE (page ~85): The hero conceives the plan for the finale. Writers
    instinctively create a briefing scene — chalk maps, "here's what we'll do" speeches,
    hand-signal instructions. NEVER write a briefing. Show the plan being EXECUTED in
    real-time micro-steps as it's being conceived.
      BAD: Rae draws a chalk map on a wall and explains each step of the plan.
      BAD: Rae gathers the group and assigns roles: "You take the east door, you take the
      roof, I'll go through the basement."
      GOOD: Rae starts moving toward the target. She tests a door — locked. Signals her
      partner to try the window. Her partner shakes her head — barred. Rae spots a vent
      grate, pulls it open, looks at her partner: "Fit through that?" The plan is being
      INVENTED and TESTED in the same moment. The audience learns the plan by watching
      it form through trial and error, not by hearing it explained.

15. COVENANT OF THE ARC (Snyder Ch.6 — Immutable Law #6):
    Snyder: "Every single character in your movie must change in the course of your story.
    EVERYONE. And I mean everyone. Good guys. Bad guys. Bystanders. It's a rule for ALL
    characters who appear on screen. The only ones who DON'T change are the bad guys —
    and that's why they lose."

    THE RULE: Every character who appears in your screenplay — including minor, one-scene,
    walk-on characters who only have 1-3 lines — MUST show some observable behavioral
    shift between their first moment on screen and their last moment on screen. This means:

    WHAT COUNTS AS AN ARC (even for tiny characters):
    - Hostile → reluctant help (a suspicious clerk warns the hero about danger)
    - Fearful → small brave act (a cowering bystander opens a door for the hero)
    - Obedient → questioning (a guard hesitates instead of following orders)
    - Selfish → small generosity (a vendor gives something away for free)
    - Indifferent → caring (a stranger checks if someone is OK)
    - Dutiful → merciful (a cop looks the other way)
    - Aggressive → backing down (a bully realizes they're wrong)
    A single beat of visible change counts: a flinch, a handed-over key, a deliberate
    lie told to protect someone, a refusal to comply, a look away at the critical moment.

    WHAT DOES NOT COUNT AS AN ARC:
    - A character who enters as a cashier and exits as a cashier with no change
    - A character who is hostile the whole time and stays hostile
    - A character who is helpful the whole time with no initial resistance
    - A character who serves a pure plot function (gives directions, sells a ticket)
      without any emotional engagement with the situation
    - A character who has no reaction to what's happening around them

    BAD (static minor characters):
      GAS CLERK rings up the purchase. Doesn't look up.
      GAS CLERK: Pump three. (hands receipt)
      Rae leaves. Gas Clerk goes back to the register.
      [PROBLEM: Gas Clerk enters passive, exits passive. Zero change. Static prop.]

    GOOD (minor character arcs in action):
      GAS CLERK rings up the purchase. Eyes the WANTED notification glowing on the
      register screen. Looks at Rae. Looks at the screen. Back at Rae.
      GAS CLERK: Pump three. (slides receipt across, lowers voice) You should know —
      two guys in a black truck been sitting across the street for an hour. (beat)
      I didn't see you.
      Gas Clerk deliberately turns away and wipes the counter. Doesn't watch Rae leave.
      [The clerk went from OBEDIENT (sees the alert) to DEFIANT (warns Rae, lies by
      omission). That's an arc. One scene. Three lines. Visible change.]

    MORE EXAMPLES OF MINOR CHARACTER ARCS:
      LAUNDROMAT CUSTOMER initially clutches her child and backs away from Rae (fear).
      Later, when Rae helps her kid pick up dropped coins, the Customer gives Rae
      a quarter for the dryer. Fear → small kindness.

      CONTRACTOR follows orders robotically in Scene 27. After watching a colleague
      die in Scene 28, Contractor hesitates before breaching the next door. Looks at
      the squad leader. Doesn't move until pushed. Obedience → doubt.

      ENCAMPMENT TEEN blocks Rae's path with crossed arms (hostility). After Rae
      shares her water without being asked, Teen silently moves aside and points
      to a gap in the fence. Hostility → grudging aid.

    The world around the hero must REACT AND CHANGE in response to what's happening.
    If the hero's journey doesn't ripple outward to affect even the smallest characters,
    the story feels hollow. The antagonist is the ONLY character who refuses to change —
    and that refusal is precisely why they lose.

16. WRITE A SCREENPLAY, NOT A NOVEL — This is a script. The camera cannot read minds.
    Every single line must describe something the audience can SEE or HEAR. Nothing else.

    BANNED PATTERNS (if you write any of these, the scene FAILS):
    - "Behavior change:" or "Arc moment:" or any label annotating a character's growth.
      WRONG: "Behavior change: she refuses to be hidden."
      RIGHT: She steps out from behind the door. Plants her feet in the hallway.
    - "Old [Name] would have..." or "[Name] makes a choice" or "Something shifts in [Name]."
      WRONG: "Old Cami would shut it down. But she doesn't."
      RIGHT: Cami opens her mouth to object. Stops. Sits back down.
    - Narrator psychology: "He wondered if..." / "She felt a surge of..." / "Part of him knew..."
      WRONG: "Part of Marcus knew this was a mistake."
      RIGHT: Marcus's hand hovers over the button. He pulls it back. Reaches again. Presses it.
    - Metaphors and similes in action lines: "like a," "as if," "seemed to," "as though."
      WRONG: "She moved through the crowd like a ghost slipping between tombstones."
      RIGHT: She weaves through the crowd. Nobody looks at her.
      WRONG: "His voice cut through the silence like a blade."
      RIGHT: His voice fills the empty room.
    - Editorializing: "ironically," "symbolically," "in a moment that would change everything."
      The camera doesn't editorialize. Describe what happens. The audience assigns meaning.

    USE LITERAL, CONCRETE LANGUAGE:
    - Describe physical actions, not emotional states
    - Name specific objects, not categories ("grabs the fire extinguisher" not "grabs a weapon")
    - Use active verbs ("slams," "yanks," "whispers") not passive constructions
    - When a character feels something, show the PHYSICAL MANIFESTATION:
      Fear = hands shake, breath quickens, eyes dart
      Anger = jaw clenches, fists ball, voice drops
      Sadness = shoulders drop, eyes go to the floor, voice thins
      Don't TELL us the emotion. SHOW us the body.

PER-SCENE REQUIRED FIELDS:
1. scene_number (int): Sequential starting from 1
2. slugline (str): "INT./EXT. LOCATION - TIME" (e.g., "INT. COFFEE SHOP - NIGHT")
3. int_ext (str): "INT.", "EXT.", or "INT/EXT."
4. location (str): Specific location name
5. time_of_day (str): DAY, NIGHT, DAWN, DUSK, or CONTINUOUS
6. elements (array): Scene elements, each with element_type and content
7. estimated_duration_seconds (int): Scene duration (1 page = 60 seconds)
8. beat (str): Which of the 15 beats this belongs to
9. emotional_start (str): "+" or "-" — where the scene starts emotionally
10. emotional_end (str): "+" or "-" — where the scene ends emotionally (should differ from start)
11. conflict (str): Who wants what from whom; who wins
12. characters_present (array): Character names in the scene
13. board_card_number (int): Original board card number

ELEMENT TYPES AND ORDERING:
- "slugline": Scene heading (always first)
- "action": What the camera sees (follows slugline, interspersed with dialogue)
- "character": Character name in CAPS (precedes their dialogue)
- "parenthetical": Brief acting direction between character and dialogue (use sparingly)
- "dialogue": What the character says (follows their character element)
- "transition": CUT TO:, SMASH CUT TO:, etc. (optional, at scene end)

OUTPUT FORMAT (valid JSON):
{{
  "title": "{title}",
  "author": "AI Generated",
  "format": "{format_value}",
  "genre": "{genre}",
  "logline": "{logline}",
  "total_pages": <float: sum of all scene durations / 60>,
  "estimated_duration_seconds": <int: sum of all scene durations>,
  "scenes": [
    {{
      "scene_number": 1,
      "slugline": "INT. LOCATION - TIME",
      "int_ext": "INT.",
      "location": "LOCATION",
      "time_of_day": "DAY",
      "elements": [
        {{"element_type": "slugline", "content": "INT. LOCATION - TIME"}},
        {{"element_type": "action", "content": "Establishing visual. What we see."}},
        {{"element_type": "character", "content": "CHARACTER A"}},
        {{"element_type": "dialogue", "content": "First line of dialogue."}},
        {{"element_type": "character", "content": "CHARACTER B"}},
        {{"element_type": "dialogue", "content": "Response dialogue."}},
        {{"element_type": "action", "content": "Reactive action between characters."}},
        {{"element_type": "character", "content": "CHARACTER A"}},
        {{"element_type": "dialogue", "content": "Continuation of exchange."}},
        {{"element_type": "action", "content": "Visual exit — door slams shut."}}
      ],
      "estimated_duration_seconds": 150,
      "beat": "Set-Up",
      "emotional_start": "+",
      "emotional_end": "-",
      "conflict": "Character A wants X from Character B; Character B refuses; A loses",
      "characters_present": ["Character A", "Character B"],
      "board_card_number": 1
    }}
  ]
}}

RULES:
- Every board card becomes at least one scene. Do not skip any cards.
- Every scene must have at least 5 elements with real content.
- Dialogue scenes need at least 3 back-and-forth exchanges (character + dialogue pairs).
- total_pages MUST equal sum of all estimated_duration_seconds divided by 60.
- estimated_duration_seconds at the top level MUST equal sum of all scene durations.
- Use exact beat names from the 15-beat BS2.

Generate ALL scenes now. Write FULL scenes, not outlines."""

    def generate_prompt(
        self,
        step_5_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Screenplay Step 8.

        Args:
            step_5_artifact: The Board with 40 scene cards
            step_3_artifact: Hero / characters artifact
            step_2_artifact: Genre classification artifact
            step_1_artifact: Logline / title artifact

        Returns:
            Dict with system and user prompts, prompt_hash, and version
        """
        # Extract logline and title
        title = step_1_artifact.get("title", "UNTITLED")
        logline = step_1_artifact.get("logline", "MISSING")

        # Extract genre
        genre = step_2_artifact.get("genre", "MISSING")

        # Extract format (default to feature)
        format_value = step_2_artifact.get("format", "feature")

        # Build hero summary
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        hero_summary = (
            f"Name: {hero.get('name', 'MISSING')}\n"
            f"Archetype: {hero.get('archetype', 'MISSING')}\n"
            f"Motivation: {hero.get('primal_motivation', hero.get('stated_goal', 'MISSING'))}\n"
            f"Arc: {hero.get('opening_state', 'MISSING')} -> {hero.get('final_state', 'MISSING')}"
        )

        # Build characters summary
        characters_parts = [f"Hero: {hero.get('name', 'MISSING')}"]

        antagonist = step_3_artifact.get("antagonist", step_3_artifact.get("antagonist_profile", {}))
        if antagonist:
            characters_parts.append(
                f"Antagonist: {antagonist.get('name', 'MISSING')} - {antagonist.get('adjective_descriptor', '')}"
            )

        b_story = step_3_artifact.get("b_story_character", step_3_artifact.get("b_story", {}))
        if b_story:
            characters_parts.append(
                f"B-Story: {b_story.get('name', 'MISSING')} - {b_story.get('relationship_to_hero', '')}"
            )

        characters_summary = "\n".join(characters_parts)

        # Build character identifiers
        character_identifiers = self._build_character_identifiers(step_3_artifact)

        # Build genre-specific guidance
        genre_scene_guidance = self._build_genre_scene_guidance(genre)
        genre_emotion_note = self._build_genre_emotion_note(genre)

        # Build board cards JSON
        board_cards = self._extract_board_cards(step_5_artifact)
        board_cards_json = json.dumps(board_cards, indent=2, ensure_ascii=False)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
            genre_scene_guidance=genre_scene_guidance,
            genre_emotion_note=genre_emotion_note,
            board_cards_json=board_cards_json,
            format_value=format_value,
        )

        # Calculate prompt hash for tracking
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
        current_artifact: Dict[str, Any],
        validation_errors: list,
        step_5_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate prompt for revising a screenplay that failed validation.

        Args:
            current_artifact: The artifact that failed validation
            validation_errors: List of validation error strings
            step_5_artifact: The Board with 40 scene cards
            step_3_artifact: Hero / characters artifact
            step_2_artifact: Genre classification artifact
            step_1_artifact: Logline / title artifact

        Returns:
            Dict with system and user prompts for revision
        """
        title = step_1_artifact.get("title", "UNTITLED")
        logline = step_1_artifact.get("logline", "MISSING")
        genre = step_2_artifact.get("genre", "MISSING")
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        scene_count = len(current_artifact.get("scenes", []))
        total_pages = current_artifact.get("total_pages", 0)

        # Include board cards so the LLM has context to work from
        board_cards = self._extract_board_cards(step_5_artifact)
        board_cards_json = json.dumps(board_cards, indent=1, ensure_ascii=False)

        # Build characters summary
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        antag = step_3_artifact.get("antagonist", {})
        b_story = step_3_artifact.get("b_story_character", {})
        chars = f"Hero: {hero.get('name', '?')}, Antagonist: {antag.get('name', '?')}, B-Story: {b_story.get('name', '?')}"

        revision_user = f"""REVISION REQUIRED for Screenplay Step 8 (Screenplay Writing).

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}
CHARACTERS: {chars}
CURRENT SCENE COUNT: {scene_count}
CURRENT TOTAL PAGES: {total_pages}

BOARD CARDS (source material — expand each into a scene):
{board_cards_json}

VALIDATION ERRORS:
{error_text}

Fix ALL errors. Generate the COMPLETE screenplay from the board cards above.

CRITICAL REQUIREMENTS:
1. Output MUST include top-level "title", "logline", "genre", "format", "total_pages", "estimated_duration_seconds"
2. Every scene needs elements array with at least 5 elements (slugline, action, character, dialogue, etc.)
3. Most scenes MUST have sustained dialogue — at least 3 character+dialogue exchanges per scene
4. Every scene needs conflict, emotional_start ("+"/"-"), emotional_end ("+"/"-"), estimated_duration_seconds > 0
5. At least 30 scenes, each averaging 120-180 seconds (2-3 pages)
6. NO internal monologue — only what camera sees and microphone hears
7. Each scene is a mini-movie: beginning, middle, end, emotional change

Output valid JSON only. No markdown fences."""

        prompt_content = f"{self.SYSTEM_PROMPT}{revision_user}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_user,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }

    # ── Per-Scene Generation Methods ──────────────────────────────────────

    SINGLE_SCENE_SYSTEM = (
        "You are a Save the Cat! screenwriter writing in a specific genre. You write ONE "
        "screenplay scene at a time from a board card. Every scene is a mini-movie with "
        "beginning, middle, and end. Every scene SHOWS, never tells. The hero is ALWAYS "
        "proactive. Characters sound DISTINCT. You write rich, cinematic scenes with sustained "
        "dialogue exchanges, specific visual action, and clear emotional transitions.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    SINGLE_SCENE_TEMPLATE = """Write ONE screenplay scene from the board card below.

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

HERO:
{hero_summary}

CHARACTERS:
{characters_summary}

CHARACTER VOICE GUIDE (every character MUST sound distinct from every other):
{character_identifiers}

GENRE-SPECIFIC SCENE WRITING GUIDANCE ({genre}):
{genre_scene_guidance}

BOARD CARD TO EXPAND:
{board_card_json}

PREVIOUS SCENES (for continuity — do NOT repeat content):
{previous_scenes_summary}
{milestone_guidance}
SCENE WRITING RULES (STRICT — violating any of these is a failure):

This scene is a MINI-MOVIE with a beginning, middle, and end. Snyder (Ch.5): "Think of each
scene as a mini-movie. It must have a beginning, middle and an end. And it must also have
something happen that causes the emotional tone to change drastically either from + to - or
from - to +." This scene changes from {emotional_start} to {emotional_end}. Show this change
through ACTION, not narration.

1. CONFLICT: "{conflict}" — build the entire scene around this single conflict. Snyder:
   "Only one conflict per scene, please. One is plenty."

2. THE HERO LEADS — The hero is PROACTIVE in this scene. The hero makes statements, gives
   commands, and drives the action. The hero should have NO MORE THAN 2 question marks in
   this scene. The hero SEEKS information — searches drawers, follows clues, confronts
   people — rather than asking "What happened?" and being told.
   Snyder (Ch.7): "A hero who asks questions is a passive hero."
   BAD (passive hero):
     DETECTIVE: What happened here?
     OFFICER: We found the body at 3 AM.
     DETECTIVE: Who discovered it?
     OFFICER: The night guard.
   GOOD (proactive hero):
     DETECTIVE grabs the logbook from the desk. Flips to last night's entries.
     DETECTIVE: The night guard signed out at 2:47. Body was found at 3. (points at the logbook)
     Thirteen minutes. Where was he for thirteen minutes?

3. SHOW, DON'T TELL — ZERO tolerance for exposition in dialogue. Characters NEVER explain
   things the audience already knows. Characters NEVER say "as you know" or "let me explain."
   If the audience needs information, SHOW it: a newspaper headline, security footage, a
   physical evidence piece, a visible reaction, a prop that tells the story.
   BAD: "As you know, we've been tracking this target for six months."
   GOOD: She opens a drawer. Six months of surveillance photos spill across the desk.
   BAD: "He's dangerous because he controls the entire network."
   GOOD: A bank of monitors shows feeds from every camera in the city. HIS face reflected in each.
   Snyder: "Movies are stories told in pictures."

4. NO INTERNAL MONOLOGUE — everything must be visible or audible on screen.
   BAD: "She felt nausea rising in her stomach."
   GOOD: "She grabs the table edge. Her knuckles whiten."
   BAD: "He wondered if she was telling the truth."
   GOOD: "He stares at her. His jaw tightens. He pulls out his phone, scrolls to a photo."
   Snyder (Ch.7): "Character is revealed by action taken not by words spoken."

5. DISTINCT VOICES (Hi How Are You) — Snyder (Ch.7): "I was stunned. I couldn't tell one of
   my characters from the others." EVERY character in this scene MUST speak differently:
   - Different sentence lengths (one uses clipped fragments, another uses long clauses)
   - Different vocabulary levels (one uses street slang, another uses technical jargon)
   - Different verbal tics (one says "Look," to start sentences; another never uses contractions)
   - If you cover the character names, a reader MUST be able to tell who is speaking
   Use the Character Voice Guide above — it tells you HOW each character talks. Follow it.

6. CHARACTER IDENTIFIERS (Limp and Eye Patch) — Snyder (Ch.7): "Make sure every character
   has 'A Limp and an Eyepatch' — something memorable." EVERY recurring character must display
   their distinctive visual/behavioral identifier THE FIRST TIME they appear in this scene:
   - A prop they always carry or touch
   - A physical habit or gesture
   - A piece of clothing or accessory
   - A sound they make (clearing throat, cracking knuckles)
   The Character Voice Guide above lists each character's identifier. USE IT.

7. DIALOGUE must be SPOKEN, SUSTAINED, and CHARACTER-SPECIFIC.
   Each dialogue exchange needs MULTIPLE back-and-forth (3-6 minimum).
   Dialogue serves the scene's CONFLICT, not the writer's need to explain the plot.
   BAD: "We need to go to the warehouse because that's where the evidence is."
   GOOD: "The warehouse." "In this weather?" "You want the proof or not?"

8. SCENE DENSITY: 5-15 elements. Slugline, establishing action, character introductions,
   dialogue exchanges, reactive action, visual exit.

9. VISUAL ENTRY AND EXIT: Open with a slugline and establishing action (what we SEE when
   we arrive). End with a clear reason to cut — a door slam, a look, a revelation, a
   question left hanging.

10. TIMING: 1 page = 60 seconds. Average scene is 2-3 pages (120-180 seconds).

11. KEEP THE PRESS OUT (Snyder Ch.6 — Immutable Law #7):
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
    GOOD (information stays personal and contained):
      [ACTION] A drunk at the end of the bar slams his glass down. "Third night in a row
      the power's been cutting out. My wife thinks it's terrorists."
    EXCEPTION: Only if the story's premise is ABOUT media/journalism.

12. POPE IN THE POOL (Snyder Ch.6 — Immutable Law #2):
    Every scene that conveys backstory or plot information MUST have something visually
    entertaining happening simultaneously. NEVER write a scene where a character stands at
    a screen or sits at a desk and EXPLAINS things. Bury exposition in action, danger, or
    visual spectacle. The name comes from "The Plot to Kill the Pope" — vital backstory about
    the assassination plot is delivered while the Pope swims laps at the Vatican pool. We
    aren't even listening to the exposition because we're watching the Pope in a Speedo.
    BAD: A team leader briefs the squad on the situation while everyone listens.
    GOOD: A team leader shouts situation details while the squad sprints through a collapsing
    building — the audience absorbs the info because they're watching people dodge debris.
    HIGH-RISK BEATS — pay extreme attention if this scene is one of these:
    - THEME STATED: Theme MUST be delivered during visually compelling action — NOT during
      a static phone call, NOT over coffee, NOT while sitting in a car.
    - DARK NIGHT OF THE SOUL: The hero's lowest point MUST NOT be a static confession.
      No sitting and talking. The despair MUST be forced out by physical circumstances.
    - BREAK INTO THREE: The plan MUST NOT be a briefing. Show it being EXECUTED in
      micro-steps as it's conceived, not explained as a lecture.

13. COVENANT OF THE ARC (Snyder Ch.6 — Immutable Law #6):
    Snyder: "Every single character in your movie must change in the course of your story.
    EVERYONE." This means EVERY character who appears in this scene — including minor,
    one-scene walk-on characters — must show some observable behavioral shift between their
    first moment and their last moment in the scene. The shift can be tiny but MUST be visible:
    - A hostile stranger who softens (hostility → reluctant help)
    - A fearful bystander who finds courage (fear → small brave act)
    - A suspicious guard who looks the other way (duty → mercy)
    - A selfish clerk who gives something away (selfishness → generosity)
    NO CHARACTER should enter and exit this scene in the same emotional/behavioral state.
    The ONLY exception is the antagonist, who refuses to change — that's why they lose.
    BAD (static minor character):
      GAS CLERK rings up the purchase. Doesn't look up.
      GAS CLERK: Pump three. (hands receipt)
      Rae leaves. Gas Clerk goes back to the register.
    GOOD (minor character arcs):
      GAS CLERK rings up the purchase. Eyes the WANTED notification on the register screen.
      GAS CLERK: Pump three. (slides receipt across) You should know — two guys in a black
      truck have been parked across the street for an hour. (beat) I didn't see you.
      Gas Clerk deliberately turns away and wipes the counter.

OUTPUT FORMAT (single scene, valid JSON):
{{
  "scene_number": {scene_number},
  "slugline": "INT./EXT. LOCATION - TIME",
  "int_ext": "INT.",
  "location": "LOCATION NAME",
  "time_of_day": "DAY|NIGHT|DAWN|DUSK|CONTINUOUS",
  "elements": [
    {{"element_type": "slugline", "content": "INT. LOCATION - TIME"}},
    {{"element_type": "action", "content": "Establishing visual. What we see."}},
    {{"element_type": "character", "content": "CHARACTER A"}},
    {{"element_type": "dialogue", "content": "First line of dialogue."}},
    {{"element_type": "character", "content": "CHARACTER B"}},
    {{"element_type": "dialogue", "content": "Response dialogue."}},
    {{"element_type": "action", "content": "Reactive action between characters."}},
    {{"element_type": "character", "content": "CHARACTER A"}},
    {{"element_type": "dialogue", "content": "Continuation of exchange."}},
    {{"element_type": "action", "content": "Visual exit — door slams shut."}}
  ],
  "estimated_duration_seconds": 150,
  "beat": "{beat}",
  "emotional_start": "{emotional_start}",
  "emotional_end": "{emotional_end}",
  "conflict": "{conflict}",
  "characters_present": [],
  "board_card_number": {card_number}
}}

Write the FULL scene now. Rich, cinematic, with distinct character voices and every character arcing."""

    SCENE_REVISION_TEMPLATE = """REVISION REQUIRED for Scene {scene_number}.

The scene below has quality problems that must be fixed. Rewrite it completely, addressing
every issue listed. Keep the same board card, conflict, emotional arc, and characters.

CURRENT SCENE:
{scene_json}

PROBLEMS FOUND:
{failures_text}

BOARD CARD (source material):
{board_card_json}

CHARACTER VOICE GUIDE:
{character_identifiers}

PREVIOUS SCENES (for continuity):
{previous_scenes_summary}

Rewrite the scene fixing ALL listed problems. Output valid JSON only (single scene, same format as above)."""

    SCENE_DIAGNOSTIC_SYSTEM = (
        "You are a Save the Cat! script doctor. You evaluate ONE screenplay scene against "
        "5 specific quality checks from Blake Snyder Chapter 7. You are rigorous but fair. "
        "You check the actual written scene, not what it could be.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    SCENE_DIAGNOSTIC_TEMPLATE = """Evaluate this ONE screenplay scene against 5 Save the Cat diagnostic checks.

SCENE TO EVALUATE:
{scene_json}

HERO: {hero_name}
CHARACTER VOICE GUIDE:
{character_identifiers}

PREVIOUS SCENES SUMMARY (for emotional variety context):
{previous_scenes_summary}

EMOTIONS ALREADY HIT IN PREVIOUS SCENES: {emotions_seen}

RUN THESE 5 CHECKS:

1. THE HERO LEADS — Is the hero proactive in this scene? Does the hero make statements and
   give commands, or just ask questions and receive information? Count the hero's question
   marks — more than 2 is a fail. Does the hero drive the scene or get dragged through it?
   Snyder: "A hero never asks questions."

2. TALKING THE PLOT — Does dialogue show through subtext and conflict, or tell through
   exposition? Are characters explaining things the audience already knows? Are emotions
   TOLD not SHOWN? Snyder: "Your characters don't serve you, they serve themselves."

3. EMOTIONAL COLOR WHEEL — What specific emotion does this scene hit? (Options: lust, fear,
   joy, hope, despair, anger, tenderness, surprise, longing, regret, frustration,
   near-miss anxiety, triumph, human foible.) Given the emotions already hit, is this scene
   adding variety or repeating the same emotional note?

4. HI HOW ARE YOU — Do the characters in this scene sound distinct from each other? Cover
   up the names — can you tell who is speaking? Does each character have their own rhythm,
   vocabulary, sentence length, and verbal personality? Snyder: "I was stunned. I couldn't
   tell one of my characters from the others."

5. LIMP AND EYE PATCH — Do recurring characters display their distinctive identifiers in
   this scene? Check the Character Voice Guide above — are the specified traits visible in
   the scene? Snyder: "Make sure every character has 'A Limp and an Eyepatch.'"

OUTPUT FORMAT (valid JSON):
{{
  "diagnostics": [
    {{
      "check_number": 1,
      "check_name": "The Hero Leads",
      "passed": true,
      "problem_details": "",
      "fix_suggestion": ""
    }},
    {{
      "check_number": 2,
      "check_name": "Talking the Plot",
      "passed": false,
      "problem_details": "<specific problem in THIS scene>",
      "fix_suggestion": "<specific rewrite instruction for THIS scene>"
    }},
    {{
      "check_number": 5,
      "check_name": "Emotional Color Wheel",
      "passed": true,
      "emotion_hit": "fear",
      "problem_details": "",
      "fix_suggestion": ""
    }},
    {{
      "check_number": 6,
      "check_name": "Hi How Are You",
      "passed": true,
      "problem_details": "",
      "fix_suggestion": ""
    }},
    {{
      "check_number": 8,
      "check_name": "Limp and Eye Patch",
      "passed": true,
      "problem_details": "",
      "fix_suggestion": ""
    }}
  ],
  "checks_passed_count": 4,
  "total_checks": 5
}}

RULES:
- Run ALL 5 checks. Do not skip any.
- For PASSED checks, problem_details and fix_suggestion may be empty strings.
- For FAILED checks, provide SPECIFIC problems found in THIS scene and SPECIFIC rewrite instructions.
- For Emotional Color Wheel, always include "emotion_hit" with the primary emotion of this scene.
- If the hero is not in this scene, check 1 (Hero Leads) auto-passes."""

    MILESTONE_DIAGNOSTIC_SYSTEM = (
        "You are a Save the Cat! script doctor running milestone diagnostics across "
        "multiple screenplay scenes. You evaluate overall patterns, not individual scenes.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    MILESTONE_DIAGNOSTIC_TEMPLATE = """Evaluate these screenplay scenes (Act {milestone_label}) against multi-scene quality checks.

SCENES WRITTEN SO FAR:
{scenes_summary}

HERO: {hero_name}
ANTAGONIST: {antagonist_name}

CHARACTERS:
{characters_summary}

MILESTONE: {milestone_label}

RUN THESE CHECKS (only those applicable to this milestone):

{applicable_checks}

OUTPUT FORMAT (valid JSON):
{{
  "diagnostics": [
    {{
      "check_name": "<check name>",
      "passed": true,
      "problem_details": "",
      "fix_suggestion": "",
      "guidance_for_upcoming_scenes": ""
    }}
  ],
  "checks_passed_count": 0,
  "total_checks": 0
}}

For any FAILED check, provide "guidance_for_upcoming_scenes" — specific instructions for what
the remaining scenes should do to compensate (e.g., "Add a scene of pure JOY in the next act"
or "Give the antagonist a moment of overwhelming power in the next 5 scenes")."""

    def generate_single_scene_prompt(
        self,
        board_card: Dict[str, Any],
        hero_summary: str,
        characters_summary: str,
        genre: str,
        logline: str,
        title: str,
        previous_scenes_summary: str,
        scene_number: int,
        character_identifiers: str,
        milestone_guidance: str = "",
    ) -> Dict[str, str]:
        """
        Generate prompt to write ONE scene from ONE board card.

        Args:
            board_card: Single board card dict
            hero_summary: Hero profile summary string
            characters_summary: All characters summary string
            genre: Genre name
            logline: Story logline
            title: Story title
            previous_scenes_summary: Summary of last 3 scenes for continuity
            scene_number: Sequential scene number (1-based)
            character_identifiers: Formatted string of character → distinctive trait
            milestone_guidance: Extra guidance from milestone checks (empty if none)

        Returns:
            Dict with system and user prompts
        """
        board_card_json = json.dumps(board_card, indent=2, ensure_ascii=False)
        emotional_start = board_card.get("emotional_start", "+")
        emotional_end = board_card.get("emotional_end", "-")
        conflict = board_card.get("conflict", "MISSING")
        beat = board_card.get("beat", "MISSING")
        card_number = board_card.get("card_number", scene_number)

        if milestone_guidance:
            milestone_guidance = f"\nMILESTONE GUIDANCE (from act-break diagnostics):\n{milestone_guidance}\n"

        genre_scene_guidance = self._build_genre_scene_guidance(genre)

        user_prompt = self.SINGLE_SCENE_TEMPLATE.format(
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
            genre_scene_guidance=genre_scene_guidance,
            board_card_json=board_card_json,
            previous_scenes_summary=previous_scenes_summary or "(This is the first scene.)",
            milestone_guidance=milestone_guidance,
            emotional_start=emotional_start,
            emotional_end=emotional_end,
            conflict=conflict,
            beat=beat,
            scene_number=scene_number,
            card_number=card_number,
        )

        prompt_content = f"{self.SINGLE_SCENE_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SINGLE_SCENE_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_scene_revision_prompt(
        self,
        scene: Dict[str, Any],
        failures: List[Dict[str, Any]],
        board_card: Dict[str, Any],
        character_identifiers: str,
        previous_scenes_summary: str,
    ) -> Dict[str, str]:
        """
        Generate prompt to revise a scene that failed diagnostic checks.

        Args:
            scene: The scene dict that failed
            failures: List of failure dicts with check_name, problem_details, fix_suggestion
            board_card: Original board card for this scene
            character_identifiers: Character voice guide string
            previous_scenes_summary: Summary of previous scenes for continuity

        Returns:
            Dict with system and user prompts
        """
        scene_json = json.dumps(scene, indent=2, ensure_ascii=False)
        board_card_json = json.dumps(board_card, indent=2, ensure_ascii=False)

        failures_parts = []
        for f in failures:
            name = f.get("check_name", "Unknown")
            problem = f.get("problem_details", "")
            fix = f.get("fix_suggestion", "")
            failures_parts.append(f"- [{name}] {problem}\n  FIX: {fix}")
        failures_text = "\n".join(failures_parts)

        scene_number = scene.get("scene_number", "?")
        conflict = board_card.get("conflict", "")

        user_prompt = self.SCENE_REVISION_TEMPLATE.format(
            scene_number=scene_number,
            scene_json=scene_json,
            failures_text=failures_text,
            board_card_json=board_card_json,
            character_identifiers=character_identifiers,
            previous_scenes_summary=previous_scenes_summary or "(First scene.)",
        )

        prompt_content = f"{self.SINGLE_SCENE_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SINGLE_SCENE_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }

    def generate_scene_diagnostic_prompt(
        self,
        scene: Dict[str, Any],
        hero_name: str,
        character_identifiers: str,
        previous_scenes_summary: str,
        emotions_seen_so_far: str,
    ) -> Dict[str, str]:
        """
        Generate prompt for AI-powered per-scene diagnostic evaluation.

        Args:
            scene: Single scene dict to evaluate
            hero_name: Name of the hero character
            character_identifiers: Character voice guide string
            previous_scenes_summary: Summary of previous scenes
            emotions_seen_so_far: Comma-separated list of emotions already hit

        Returns:
            Dict with system and user prompts
        """
        scene_json = json.dumps(scene, indent=2, ensure_ascii=False)

        user_prompt = self.SCENE_DIAGNOSTIC_TEMPLATE.format(
            scene_json=scene_json,
            hero_name=hero_name,
            character_identifiers=character_identifiers,
            previous_scenes_summary=previous_scenes_summary or "(First scene.)",
            emotions_seen=emotions_seen_so_far or "(None yet — this is the first scene.)",
        )

        prompt_content = f"{self.SCENE_DIAGNOSTIC_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SCENE_DIAGNOSTIC_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_milestone_diagnostic_prompt(
        self,
        scenes_summary: str,
        hero_name: str,
        antagonist_name: str,
        characters_summary: str,
        milestone_label: str,
        applicable_checks: str,
    ) -> Dict[str, str]:
        """
        Generate prompt for milestone diagnostic at act breaks.

        Args:
            scenes_summary: Summarized text of all scenes written so far
            hero_name: Hero's name
            antagonist_name: Antagonist's name
            characters_summary: All characters summary
            milestone_label: e.g. "1 (End of Act 1)", "2 (Midpoint)", "3 (Break into Three)"
            applicable_checks: Formatted text of which checks to run at this milestone

        Returns:
            Dict with system and user prompts
        """
        user_prompt = self.MILESTONE_DIAGNOSTIC_TEMPLATE.format(
            scenes_summary=scenes_summary,
            hero_name=hero_name,
            antagonist_name=antagonist_name,
            characters_summary=characters_summary,
            milestone_label=milestone_label,
            applicable_checks=applicable_checks,
        )

        prompt_content = f"{self.MILESTONE_DIAGNOSTIC_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.MILESTONE_DIAGNOSTIC_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    # ── Act-by-Act Generation Methods (v4.0.0 — Grok-checked) ────────────

    ACT_GENERATION_SYSTEM = (
        "You are a Save the Cat! screenwriter writing in a specific genre. You expand "
        "board cards into properly formatted screenplay scenes. Every scene is a mini-movie "
        "with beginning, middle, and end. Every scene SHOWS, never tells. The hero is ALWAYS "
        "proactive. Characters sound DISTINCT. You write rich, cinematic scenes with sustained "
        "dialogue exchanges, specific visual action, and clear emotional transitions.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    ACT_GENERATION_TEMPLATE = """You have completed the "Deep Sea Dive" checklist from Save the Cat Chapter 5.
You have a killer title, a killer logline, homework on genre, the perfect hero, and 40 scene cards
on The Board with emotional change (+/-) and conflict (><) on every card.

Snyder: "You're ready to write FADE IN and begin."

Now expand EVERY board card for {act_label} into a FULL screenplay scene.

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

HERO:
{hero_summary}

CHARACTERS:
{characters_summary}

CHARACTER VOICE GUIDE (every character MUST sound distinct from every other):
{character_identifiers}

GENRE-SPECIFIC SCENE WRITING GUIDANCE ({genre}):
{genre_scene_guidance}

BOARD CARDS TO EXPAND (this act only):
{act_cards_json}

CHARACTER CASTING RULE: Use ONLY the characters listed in the board cards above. Do NOT
invent new named characters. Unnamed background extras ("a passerby," "the bartender") are
fine for atmosphere, but any character who speaks dialogue or takes a significant action MUST
come from the board cards. If a scene needs an interaction not covered by the cards, use an
existing board card character in that role. The board cards also include `character_arcs`
for each character — follow these planned arcs when writing the scene.

{previous_acts_context}

BEAT PAGE TARGETS (for pacing — 1 page = 60 seconds):
  Opening Image: page 1 | Theme Stated: page 5 | Set-Up: pages 1-10
  Catalyst: page 12 | Debate: pages 12-25 | Break into Two: page 25
  B Story: page 30 | Fun and Games: pages 30-55 | Midpoint: page 55
  Bad Guys Close In: pages 55-75 | All Is Lost: page 75
  Dark Night of the Soul: pages 75-85 | Break into Three: page 85
  Finale: pages 85-110 | Final Image: page 110

SCENE WRITING RULES (STRICT — violating any of these is a failure):

Each scene is a MINI-MOVIE with a beginning, middle, and end. Snyder (Ch.5): "Think of each
scene as a mini-movie. It must have a beginning, middle and an end. And it must also have
something happen that causes the emotional tone to change drastically either from + to - or
from - to +."

1. THE HERO LEADS — The hero is PROACTIVE in every scene they appear in. The hero makes
   statements, gives commands, and drives the action. The hero should have NO MORE THAN 2
   question marks per scene. The hero SEEKS information — searches drawers, follows clues,
   confronts people — rather than asking "What happened?" and being told.
   Snyder (Ch.7): "A hero who asks questions is a passive hero."
   BAD (passive hero):
     DETECTIVE: What happened here?
     OFFICER: We found the body at 3 AM.
     DETECTIVE: Who discovered it?
     OFFICER: The night guard.
   GOOD (proactive hero):
     DETECTIVE grabs the logbook from the desk. Flips to last night's entries.
     DETECTIVE: The night guard signed out at 2:47. Body was found at 3. (points at the logbook)
     Thirteen minutes. Where was he for thirteen minutes?

2. CONFLICT (><): Snyder: "Only one conflict per scene, please. One is plenty." The board
   card specifies who the opposing forces are, what the issue is, and who wins. Build the
   scene around this single conflict.

3. EMOTIONAL CHANGE: Every scene starts at one emotional polarity and ENDS at the opposite.
   The board card's emotional_start and emotional_end tell you the transition. Show this
   change through ACTION, not narration. The audience should FEEL the shift.

4. NO INTERNAL MONOLOGUE — everything must be visible or audible on screen.
   BAD: "She felt nausea rising in her stomach."
   GOOD: "She grabs the table edge. Her knuckles whiten."
   BAD: "He wondered if she was telling the truth."
   GOOD: "He stares at her. His jaw tightens. He pulls out his phone, scrolls to a photo."
   Snyder (Ch.7): "Character is revealed by action taken not by words spoken."

5. SHOW, DON'T TELL — ZERO tolerance for exposition in dialogue. Characters NEVER explain
   things the audience already knows. Characters NEVER say "as you know" or "let me explain."
   If the audience needs information, SHOW it: a newspaper headline, security footage, a
   physical evidence piece, a visible reaction, a prop that tells the story.
   BAD: "As you know, we've been tracking this target for six months."
   GOOD: She opens a drawer. Six months of surveillance photos spill across the desk.
   BAD: "He's dangerous because he controls the entire network."
   GOOD: A bank of monitors shows feeds from every camera in the city. HIS face reflected in each.
   Snyder: "Movies are stories told in pictures."

6. DISTINCT VOICES (Hi How Are You) — Snyder (Ch.7): "I was stunned. I couldn't tell one of
   my characters from the others." EVERY character MUST speak differently. Specific rules:
   - Different sentence lengths (one character uses clipped fragments, another uses long clauses)
   - Different vocabulary levels (one character uses street slang, another uses technical jargon)
   - Different verbal tics (one says "Look," to start sentences; another never uses contractions)
   - If you cover the character names, a reader MUST be able to tell who is speaking
   Use the Character Voice Guide above — it tells you HOW each character talks. Follow it.

7. CHARACTER IDENTIFIERS (Limp and Eye Patch) — Snyder (Ch.7): "Make sure every character
   has 'A Limp and an Eyepatch' — something memorable." EVERY recurring character must display
   their distinctive visual/behavioral identifier THE FIRST TIME they appear in a scene:
   - A prop they always carry or touch
   - A physical habit or gesture
   - A piece of clothing or accessory
   - A sound they make (clearing throat, cracking knuckles)
   The Character Voice Guide above lists each character's identifier. USE IT.

8. DIALOGUE must be SPOKEN, SUSTAINED, and CHARACTER-SPECIFIC.
   Each dialogue scene needs MULTIPLE exchanges (3-6 back-and-forth minimum).
   Dialogue serves the scene's CONFLICT, not the writer's need to explain the plot.
   BAD: "We need to go to the warehouse because that's where the evidence is."
   GOOD: "The warehouse." "In this weather?" "You want the proof or not?"

9. EMOTIONAL VARIETY (Emotional Color Wheel) — No two consecutive scenes should hit the
   exact same primary emotion. Track your palette. Snyder wants a "roller coaster of emotion."
   Available emotions: lust, fear, joy, hope, despair, anger, tenderness, surprise, longing,
   regret, frustration, near-miss anxiety, triumph, human foible.
   If you've written 3 fear scenes in a row, the next scene MUST hit something different.
   {genre_emotion_note}

10. VISUAL ENTRY AND EXIT: Every scene opens with a slugline and establishing action (what we
    SEE when we arrive), and ends with a clear reason to cut — a door slam, a look, a revelation,
    a question left hanging.

11. SCENE DENSITY: Each scene should have 5-15 elements. A typical scene includes: slugline,
    establishing action, character introductions, dialogue exchanges, reactive action, and either
    a transition or a strong visual exit. Thin scenes (1-3 elements) are outlines, not screenplay.

12. TIMING: 1 screenplay page = approximately 60 seconds of screen time. An average scene is
    2-3 pages (120-180 seconds). Some scenes are shorter (Opening Image might be 30-60 seconds),
    some are longer (Finale sequences can be 5-10 pages).

13. KEEP THE PRESS OUT (Snyder Ch.6 — Immutable Law #7):
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
    EXCEPTION: Only if the story's premise is ABOUT media/journalism.

14. POPE IN THE POOL (Snyder Ch.6 — Immutable Law #2):
    Every scene that conveys backstory or plot information MUST have something visually
    entertaining happening simultaneously. NEVER write a scene where a character stands at
    a screen or sits at a desk and EXPLAINS things. Bury exposition in action, danger, or
    visual spectacle. The name comes from "The Plot to Kill the Pope" — vital backstory about
    the assassination plot is delivered while the Pope swims laps in a bathing suit at the
    Vatican pool. We aren't even listening to the exposition because we're watching the Pope
    in a Speedo.
    BAD: A team leader briefs the squad on the situation while everyone listens.
    GOOD: A team leader shouts situation details while the squad sprints through a collapsing
    building — the audience absorbs the info because they're watching people dodge debris.
    HIGH-RISK BEATS — these are the beats that MOST OFTEN violate Pope in the Pool. Pay
    extreme attention when writing these:
    - THEME STATED (page ~5): The theme MUST be delivered during a visually compelling
      activity — NOT during a static phone call, NOT over coffee, NOT while sitting in a car.
      BAD: Lena states the theme during a phone call while Rae drives.
      GOOD: Lena states the theme while Rae is physically dodging a threat, stitching a wound,
      or dismantling a device — the theme lands between bursts of urgent physical action.
    - DARK NIGHT OF THE SOUL (pages 75-85): The hero's lowest emotional point MUST NOT be
      a static confession scene. No sitting in a stairwell talking. No standing in a dark room
      explaining guilt. The confession/despair MUST be forced out by physical circumstances.
      BAD: Rae sits in a stairwell and explains her past guilt to her sister.
      GOOD: Rae and her sister are trapped — rae must physically work to escape (picking a lock,
      applying pressure to a wound, hotwiring a panel) while the despair spills out in fragments
      between desperate physical actions. The environment FORCES the truth out.
    - BREAK INTO THREE (page ~85): The plan/strategy for the finale MUST NOT be a briefing
      scene. No chalk maps. No "here's what we'll do" speeches. Show the plan being EXECUTED
      in micro-steps while it's being conceived.
      BAD: Rae draws a map on a wall and explains the plan step by step.
      GOOD: Rae starts moving toward the target, improvising the plan in real time — she tests
      a door, signals her partner, adapts when the first approach fails. The audience learns
      the plan by watching it unfold, not by hearing it explained.

15. COVENANT OF THE ARC (Snyder Ch.6 — Immutable Law #6):
    Blake Snyder: "Every single character in your movie must change in the course of your
    story. EVERYONE. And I mean everyone." He kept a Post-it note above his desk that said
    "EVERYBODY ARCS!" Good guys accept change as a positive force. Bad guys refuse to change
    — and that's why they lose. The antagonist is the ONLY character exempt from this rule.

    Snyder: "Before I sit down to write, I make notes on how all my characters are going to
    arc by charting their stories as they are laid out on The Board, with the milestones of
    change noted as each character progresses through the story."

    THE BOARD CARDS FOR THIS ACT include a `character_arcs` field for each character. This
    tells you the PLANNED behavioral shift for every character in every scene. Follow these
    arc plans when writing. Each character must enter the scene in one behavioral state and
    exit in a visibly different one, as described in the board card's character_arcs field.

    === WHAT A COMPLETE MINI-ARC LOOKS LIKE ===

    A mini-arc has three parts:
    (a) ENTRY BEHAVIOR: How the character acts when we first see them in the scene.
    (b) CATALYST: Something happens IN the scene that causes the character to reconsider.
    (c) EXIT BEHAVIOR: The character takes a DIFFERENT ACTION than they would have at the
        start. Not a different feeling — a different ACTION. The audience must SEE the change.

    The arc can be tiny — a single beat of changed behavior is enough. But the behavior must
    actually change. A character who FEELS bad but ACTS the same has not arced.

    === CRITICAL DISTINCTION: ALMOST-ARC vs. REAL ARC ===

    The most common failure is the "almost-arc" — a character who shows doubt or discomfort
    but ultimately does the same thing they would have done anyway. This is NOT an arc.

    ALMOST-ARC (WRONG — character has not changed):
      GUARD frowns at the order. Shifts his weight. Looks at the civilian.
      GUARD: This doesn't feel right.
      SQUAD LEADER: Breach.
      GUARD takes a breath. Breaches the door.
      [Guard FELT bad but his BEHAVIOR is identical — he followed the order. No arc.]

    REAL ARC (RIGHT — character's behavior changes):
      GUARD frowns at the order. Shifts his weight. Looks at the civilian.
      GUARD: This doesn't feel right.
      SQUAD LEADER: Breach.
      Guard looks at the door. Looks at the civilian. Sets down the breaching tool.
      GUARD: Do it yourself.
      [Guard's behavior CHANGED from obedient to refusing. Something broke his compliance.
      The audience can SEE the change — he puts down the tool and walks away.]

    === POSITIVE EXAMPLE 1: ONE-SHOT AUTHORITY FIGURE ===

    Setup: Hero enters a precinct to report a crime. The DESK SERGEANT is dismissive.

      DESK SERGEANT doesn't look up from his crossword.
      DESK SERGEANT: Take a number.
      RAE: There's no time for —
      DESK SERGEANT: Take. A number.
      Rae slams a SECURITY BADGE on the counter. Department of Energy seal.
      The Desk Sergeant looks at the badge. Looks at Rae. Puts down his crossword.
      He picks up the desk phone. Dials.
      DESK SERGEANT: Captain? You're gonna want to come down here.

    The Desk Sergeant went from DISMISSIVE (doesn't look up, brushes her off) to TAKING
    ACTION (picks up the phone, calls the Captain). The badge was the catalyst — it gave
    him a reason to change. One scene, three lines, complete arc.

    === POSITIVE EXAMPLE 2: RECURRING MINOR CHARACTER ===

    A NIGHT JANITOR appears in three scenes across the screenplay. His arc builds across
    all three appearances:

    Scene 14 (first appearance — INDIFFERENT):
      Night Janitor mops the hallway. Rae runs past.
      RAE: Did you see anyone come through here?
      NIGHT JANITOR: (doesn't stop mopping) Ain't my business who comes through.
      [Initial state: detached, wants no involvement.]

    Scene 22 (second appearance — CONFLICTED):
      Night Janitor is mopping the same hallway. Sees blood drops on the floor.
      Stops mopping. Looks both ways. Keeps mopping — mops OVER the blood drops.
      [Middle state: he noticed something wrong, chose to cover it up. Still not helping
      directly, but his behavior has shifted from pure indifference to active concealment.
      He's being pulled into the situation against his will.]

    Scene 34 (third appearance — COMMITS):
      Night Janitor finds Rae hiding in a supply closet, bleeding.
      NIGHT JANITOR: You again. (beat) They're checking this floor in ten minutes.
      He reaches into his cart. Pulls out a janitor's uniform. Drops it on her lap.
      NIGHT JANITOR: Freight elevator's around the corner. Code's 4-4-1-9.
      Turns and leaves. Goes back to mopping.
      [Final state: actively helping at personal risk. He went from "ain't my business" to
      giving her an escape route. The arc completed across three scenes.]

    === POSITIVE EXAMPLE 3: ANTAGONIST'S SUBORDINATE ===

    A CONTRACTOR works for the antagonist's security team. He follows orders.

    Scene 18 (first appearance — OBEDIENT):
      Contractor adjusts his wedding ring. Checks his tablet. Breaches the door.
      Clean, efficient, no hesitation. A professional doing his job.

    Scene 26 (second appearance — SEEDS OF DOUBT):
      Contractor adjusts his wedding ring. The door he breached reveals a family huddled
      inside. A child is crying. Contractor stares. His hand goes to his wedding ring.
      SQUAD LEADER: Clear it.
      Contractor clears the room. But his hand stays on the ring the whole time.
      [He still follows orders, but the ring-touching has shifted from habit to
      emotional anchor — he's thinking about his own family. Doubt is building.]

    Scene 33 (third appearance — BREAKS):
      Contractor adjusts his wedding ring. Squad leader signals the next door.
      Behind it: muffled voices. Children.
      Contractor lowers his breaching tool.
      SQUAD LEADER: Breach.
      CONTRACTOR: (quietly) No.
      He sets the tool on the ground. Walks away. Doesn't look back.
      [He went from unquestioning obedience to refusal. The accumulated weight of
      what he's seen — combined with his family connection (the ring) — broke his
      compliance. The audience has been watching this arc build across three scenes.]

    === RULES FOR WRITING CHARACTER ARCS ===

    1. Follow the board card's `character_arcs` field for each character. It tells you the
       planned entry and exit behavior. Write the scene so the character starts in the entry
       state and ends in the exit state.

    2. ONE-SHOT characters (appear in only 1 scene): their arc must complete within that
       single scene. Entry behavior → catalyst moment → exit behavior. All three in one scene.

    3. RECURRING characters (appear in 2+ scenes): their arc builds across appearances.
       Each scene advances them one step. Earlier scenes plant the seed; later scenes pay it
       off. The character's behavior in Scene N should be visibly different from Scene N-1.

    4. Use ONLY the characters listed in the board cards. Do not invent new named characters.
       Unnamed background extras (e.g., "a passerby," "the bartender") are fine for atmosphere,
       but any character with dialogue or a significant action must come from the board cards.

    5. The arc must be visible in ACTION, not just in internal state. A character who thinks
       "I should help" but doesn't is static. A character who slides a keycard under the door
       has arced. Show the change through what the character DOES or SAYS — something the
       camera can capture and the audience can see.

    6. The antagonist is the ONLY exception. The antagonist refuses to change — that's why
       they lose. Every other character must show behavioral change.

16. WRITE A SCREENPLAY, NOT A NOVEL — This is a script. The camera cannot read minds.
    Every single line must describe something the audience can SEE or HEAR. Nothing else.

    BANNED PATTERNS (if you write any of these, the scene FAILS):
    - "Behavior change:" or "Arc moment:" or any label annotating a character's growth.
      WRONG: "Behavior change: she refuses to be hidden."
      RIGHT: She steps out from behind the door. Plants her feet in the hallway.
    - "Old [Name] would have..." or "[Name] makes a choice" or "Something shifts in [Name]."
      WRONG: "Old Cami would shut it down. But she doesn't."
      RIGHT: Cami opens her mouth to object. Stops. Sits back down.
    - Narrator psychology: "He wondered if..." / "She felt a surge of..." / "Part of him knew..."
      WRONG: "Part of Marcus knew this was a mistake."
      RIGHT: Marcus's hand hovers over the button. He pulls it back. Reaches again. Presses it.
    - Metaphors and similes in action lines: "like a," "as if," "seemed to," "as though."
      WRONG: "She moved through the crowd like a ghost slipping between tombstones."
      RIGHT: She weaves through the crowd. Nobody looks at her.
      WRONG: "His voice cut through the silence like a blade."
      RIGHT: His voice fills the empty room.
    - Editorializing: "ironically," "symbolically," "in a moment that would change everything."
      The camera doesn't editorialize. Describe what happens. The audience assigns meaning.

    USE LITERAL, CONCRETE LANGUAGE:
    - Describe physical actions, not emotional states
    - Name specific objects, not categories ("grabs the fire extinguisher" not "grabs a weapon")
    - Use active verbs ("slams," "yanks," "whispers") not passive constructions
    - When a character feels something, show the PHYSICAL MANIFESTATION:
      Fear = hands shake, breath quickens, eyes dart
      Anger = jaw clenches, fists ball, voice drops
      Sadness = shoulders drop, eyes go to the floor, voice thins
      Don't TELL us the emotion. SHOW us the body.

PER-SCENE REQUIRED FIELDS:
1. scene_number (int): Sequential starting from {start_scene_number}
2. slugline (str): "INT./EXT. LOCATION - TIME" (e.g., "INT. COFFEE SHOP - NIGHT")
3. int_ext (str): "INT.", "EXT.", or "INT/EXT."
4. location (str): Specific location name
5. time_of_day (str): DAY, NIGHT, DAWN, DUSK, or CONTINUOUS
6. elements (array): Scene elements, each with element_type and content
7. estimated_duration_seconds (int): Scene duration (1 page = 60 seconds)
8. beat (str): Which of the 15 beats this belongs to
9. emotional_start (str): "+" or "-" — where the scene starts emotionally
10. emotional_end (str): "+" or "-" — where the scene ends emotionally (should differ from start)
11. conflict (str): Who wants what from whom; who wins
12. characters_present (array): Character names in the scene
13. board_card_number (int): Original board card number

ELEMENT TYPES AND ORDERING:
- "slugline": Scene heading (always first)
- "action": What the camera sees (follows slugline, interspersed with dialogue)
- "character": Character name in CAPS (precedes their dialogue)
- "parenthetical": Brief acting direction between character and dialogue (use sparingly)
- "dialogue": What the character says (follows their character element)
- "transition": CUT TO:, SMASH CUT TO:, etc. (optional, at scene end)

OUTPUT FORMAT (valid JSON — array of scenes):
{{
  "scenes": [
    {{
      "scene_number": {start_scene_number},
      "slugline": "INT./EXT. LOCATION - TIME",
      "int_ext": "INT.",
      "location": "LOCATION",
      "time_of_day": "DAY",
      "elements": [
        {{"element_type": "slugline", "content": "INT. LOCATION - TIME"}},
        {{"element_type": "action", "content": "Establishing visual. What we see."}},
        {{"element_type": "character", "content": "CHARACTER A"}},
        {{"element_type": "dialogue", "content": "First line of dialogue."}},
        {{"element_type": "character", "content": "CHARACTER B"}},
        {{"element_type": "dialogue", "content": "Response dialogue."}},
        {{"element_type": "action", "content": "Reactive action between characters."}},
        {{"element_type": "character", "content": "CHARACTER A"}},
        {{"element_type": "dialogue", "content": "Continuation of exchange."}},
        {{"element_type": "action", "content": "Visual exit — door slams shut."}}
      ],
      "estimated_duration_seconds": 150,
      "beat": "Set-Up",
      "emotional_start": "+",
      "emotional_end": "-",
      "conflict": "Who wants what from whom; who wins",
      "characters_present": ["Character A", "Character B"],
      "board_card_number": 1
    }}
  ]
}}

Write ALL {num_cards} scenes for {act_label}. Full scenes with rich detail, not outlines."""

    ACT_DIAGNOSTIC_SYSTEM = (
        "You are an independent script doctor hired to evaluate a screenplay. You did NOT write "
        "this screenplay — you are reading it with completely fresh eyes. Your job is to be "
        "brutally honest about quality problems. You evaluate against Blake Snyder's Save the Cat "
        "Chapter 7 diagnostic checks AND the Chapter 6 Immutable Law 'Covenant of the Arc.'\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary, no thinking out loud."
    )

    ACT_DIAGNOSTIC_TEMPLATE = """Read this act of a screenplay with FRESH EYES and evaluate it against ALL 10 Save the Cat checks (9 Ch.7 diagnostics + 1 Ch.6 Immutable Law).

You are NOT the writer. You are an independent evaluator. Be brutally honest.

SCREENPLAY — {act_label}:
{act_scenes_text}

HERO: {hero_name}
ANTAGONIST: {antagonist_name}
CHARACTERS: {characters_summary}
CHARACTER VOICE GUIDE: {character_identifiers}

{previous_acts_note}

RUN ALL 10 CHECKS:

1. THE HERO LEADS — Is the hero proactive? Does the hero make decisions and take action, or
   just react and ask questions? Count the hero's question marks across all scenes. Does the
   hero drive the story or get dragged through it? Snyder: "A hero never asks questions."

2. TALKING THE PLOT — Does dialogue show through subtext and conflict, or tell through
   exposition? Are characters explaining things the audience already knows? Are there "as you
   know" or "let me explain" moments? Snyder: "Your characters don't serve you."

3. MAKE THE BAD GUY BADDER — Is the antagonist formidable? Does the antagonist have a slight
   edge? Is the antagonist getting stronger? Snyder: "Making the bad guy badder automatically
   makes the hero bigger."

4. TURN TURN TURN — Is the story accelerating? Are obstacles escalating in complexity and
   stakes? Or flat pacing — same level of difficulty repeated? Snyder: "It's not enough for
   the plot to go forward, it must go forward faster."

5. EMOTIONAL COLOR WHEEL — What emotions does this act hit? (Options: lust, fear, joy, hope,
   despair, anger, tenderness, surprise, longing, regret, frustration, near-miss anxiety,
   triumph, human foible.) Are at least 4 different emotions present? Snyder wants a
   "roller coaster of emotion."

6. HI HOW ARE YOU I'M FINE — Do the characters sound distinct? Cover the names — can you tell
   who's speaking? Does each character have their own rhythm, vocabulary, sentence length?
   Snyder: "I was stunned. I couldn't tell one character from the others."

7. TAKE A STEP BACK — Do characters start far enough back? Is the hero's growth visible — are
   they clearly NOT yet the person they'll become? Snyder: "By drawing the bow back to its
   quivering end point, the flight of the arrow is its strongest."

8. LIMP AND EYE PATCH — Do recurring characters have distinctive visual/behavioral identifiers?
   Can you remember each character by a physical trait, habit, or prop? Snyder: "Make sure
   every character has 'A Limp and an Eyepatch.'"

9. IS IT PRIMAL? — Does the story tap into a universal, primitive instinct (survival, hunger,
   sex, protection of loved ones, fear of death)? Would a caveman understand the stakes?

10. COVENANT OF THE ARC (Snyder Ch.6 — Immutable Law #6):
    Snyder: "Every single character in your movie must change in the course of your story.
    EVERYONE. And I mean everyone. Good guys. Bad guys. Bystanders. It's a rule for ALL
    characters. The only ones who DON'T change are the bad guys — and that's why they lose."

    THIS IS THE MOST COMMONLY FAILED CHECK. Read it carefully.

    THE RULE: Every character who appears in this act — including minor, one-scene, walk-on
    characters with 1-3 lines of dialogue — MUST show a visible behavioral shift between
    their FIRST moment on screen and their LAST moment on screen within the same scene.

    HOW TO EVALUATE: For EVERY named or speaking character in this act who is NOT the hero
    or antagonist, answer these two questions:
      (a) What is their attitude/behavior when they FIRST appear in their scene?
      (b) What is their attitude/behavior when they LAST appear in their scene?
    If the answer to (a) and (b) is the same — they have NOT arced. That is a FAIL.

    WHAT COUNTS AS AN ARC (even for characters with only 1-3 lines):
    - Hostile → reluctant help (stranger warns the hero about danger)
    - Fearful → small brave act (bystander opens a door, blocks a pursuer)
    - Obedient → questioning (guard hesitates, lowers weapon, asks "Are you sure?")
    - Selfish → small generosity (vendor gives something for free, clerk slides over a tool)
    - Indifferent → caring (stranger checks if someone is OK, offers water)
    - Dutiful → merciful (cop looks the other way, soldier "doesn't see" the hero escape)
    - Aggressive → backing down (bully realizes they picked the wrong target)
    - Resigned → defiant (someone who "follows the rules" breaks one)
    Even a SINGLE BEAT of visible change counts: a flinch, a handed-over key, a deliberate
    lie told to protect someone, a refusal to comply, a look-away at the critical moment,
    a whispered warning. One line of dialogue can show an arc if it reveals a change from
    the character's initial behavior.

    WHAT DOES NOT COUNT AS AN ARC:
    - A character who enters hostile and exits hostile (static)
    - A character who enters helpful and stays helpful (already there — no change)
    - A character who enters as a cashier and exits as a cashier with no engagement
    - A character who serves a pure plot function (gives directions, scans a badge,
      sells a ticket) with zero emotional engagement with the situation
    - A character who has NO reaction to the extraordinary events happening around them
    - A character who has a memorable visual identifier (tattoo, limp, prop) but whose
      BEHAVIOR does not change — having a cool look is NOT the same as having an arc

    CRITICAL DISTINCTION — IDENTIFIER vs. ARC:
    Having "a limp and an eye patch" (Check #8) makes a character MEMORABLE.
    Having a behavioral CHANGE makes a character ARC.
    These are DIFFERENT checks. A character can PASS Check #8 (has a distinctive tattoo)
    but FAIL Check #10 (enters resigned, exits resigned — no behavioral change).
    You MUST evaluate these separately. Do NOT assume that a character with a memorable
    identifier also has an arc. Read their actual behavior from first to last moment.

    BAD (static minor character — FAILS this check):
      GAS CLERK rings up the purchase. Doesn't look up.
      GAS CLERK: Pump three. (hands receipt)
      Rae leaves. Gas Clerk goes back to the register.
      [PROBLEM: Clerk enters passive, exits passive. Attitude unchanged. No arc.]

    BAD (has identifier but NO arc — FAILS this check):
      CONTRACTOR adjusts his wedding ring. Checks his tablet. Breaches the door.
      Three scenes later, CONTRACTOR adjusts his wedding ring. Checks his tablet. Breaches
      the next door. He has a memorable identifier (wedding ring) but his BEHAVIOR is
      identical — obedient procedure from start to finish. No change. FAILS.

    GOOD (minor character arcs — PASSES this check):
      GAS CLERK rings up the purchase. Eyes the WANTED notification on the register screen.
      Looks at Rae. Looks at the screen. Back at Rae.
      GAS CLERK: Pump three. (slides receipt, lowers voice) You should know — two guys in
      a black truck been sitting across the street for an hour. (beat) I didn't see you.
      Gas Clerk deliberately turns away and wipes the counter.
      [Clerk went from OBEDIENT (sees the alert, follows procedure) to DEFIANT (warns Rae,
      lies by omission). That's an arc. Three lines. Visible change in behavior.]

    GOOD (contractor with identifier AND arc — PASSES both #8 and #10):
      CONTRACTOR adjusts his wedding ring. Checks his tablet. Breaches the door.
      [Later] The door crushes a bystander. Contractor stares. His hand goes to his
      wedding ring again — but this time he doesn't move. Squad leader signals the next
      door. Contractor doesn't move. Squad leader: "Breach." Contractor lowers his
      breaching tool. Quietly: "Do it yourself."
      [Contractor went from OBEDIENT (breaches without question) to REFUSING (guilt over
      the death makes him stop). Wedding ring is the identifier; the behavioral refusal
      is the arc. Both checks pass.]

    MORE EXAMPLES OF FAILING vs. PASSING:

    FAIL: Desperate Client enters desperate, asks for help, gets refused, exits desperate.
      No change. Same emotional state in = same emotional state out.
    PASS: Desperate Client enters desperate, begs for help, gets refused — then sees
      Rae in trouble and pushes a fire door open for her. Desperation → solidarity.

    FAIL: Laundromat Customer enters scared, backs away from Rae, stays scared.
      No change. Fear in = fear out.
    PASS: Laundromat Customer enters scared, backs away — but when Rae helps her kid
      pick up dropped coins, Customer slides a dryer quarter across. Fear → small kindness.

    FAIL: Young Driver drives the car, drops them off, drives away.
      Functional tool. Zero engagement. No arc.
    PASS: Young Driver drives the car, hands shaking on the wheel. At drop-off, Rae says
      "Go home." Driver hesitates, then pops the trunk: "There's a blanket and water in
      there. Take it." Reluctance → chosen generosity.

    FAIL: Encampment Teen blocks the path, stays hostile, never moves.
      Static obstacle. No change.
    PASS: Encampment Teen blocks the path. Rae shares her water without being asked.
      Teen silently steps aside and points to a gap in the fence. Hostility → grudging aid.

    FOR EACH SCENE IN THIS ACT: List every named/speaking non-hero, non-antagonist character.
    For each one, state their first behavior and last behavior. If they're the same = FAIL.
    List the failing characters and their scenes in failing_scene_numbers and fix_per_scene.

{seeded_arcs_diagnostic_note}

    The fix instruction for each failing scene MUST describe:
    1. Which character is static
    2. What their current first/last behavior is
    3. A SPECIFIC rewrite showing the behavioral shift — what new action/dialogue to add
       that shows the character changing. The fix should be 1-3 lines of new content that
       can be inserted into the existing scene, not a full scene rewrite.

FOR EVERY FAILED CHECK (all 10) YOU MUST:
1. List the EXACT scene numbers that have the problem
2. QUOTE the exact problematic dialogue or action lines from those scenes
3. For EACH failing scene, write a CONCRETE rewrite instruction — not "make it better" but
   "replace Rae's line 'I took a job. I trusted a clean file.' with a visual action: Rae
   pulls up the doctored surveillance footage on the billboard. The timestamps flicker.
   Her only words: 'Look at the timestamp.'"

OUTPUT FORMAT (valid JSON):
{{
  "diagnostics": [
    {{
      "check_number": 1,
      "check_name": "The Hero Leads",
      "passed": true,
      "problem_details": "",
      "failing_scene_numbers": [],
      "fix_per_scene": {{}}
    }},
    {{
      "check_number": 2,
      "check_name": "Talking the Plot",
      "passed": false,
      "problem_details": "Scene 37: Rae's speech 'I took a job. I trusted a clean file. I delivered a man who didn't make it out.' is a backstory dump — audience already knows this from Act 1. Scene 39: Radio voices explain plot: 'Clinic on Alameda. We've got patients alive because she pulled heat off us.'",
      "failing_scene_numbers": [37, 39],
      "fix_per_scene": {{
        "37": "Delete Rae's backstory speech entirely. Replace with visual: Rae pulls up the doctored surveillance footage on the billboard. The timestamps and doctored frames speak for themselves. Her only line: 'Look at the timestamp.' The crowd looks up. Silence.",
        "39": "Cut the radio exposition. Instead SHOW the clinic: lights flicker on, a nurse checks an IV drip, patients blink in the glow. No one explains it — we SEE it working."
      }}
    }},
    {{
      "check_number": 10,
      "check_name": "Covenant of the Arc",
      "passed": false,
      "problem_details": "Scene 7: Gas Clerk enters resigned, scans the item, hands receipt, stays resigned. No behavioral change. Scene 25: Young Driver enters nervous, drives the car, exits nervous. No behavioral change.",
      "failing_scene_numbers": [7, 25],
      "fix_per_scene": {{
        "7": "After Gas Clerk scans the item and sees the WANTED alert on the register, add: Gas Clerk hesitates. Glances at the door. Then quietly: 'Black truck across the street. Been there an hour.' Turns away. Wipes the counter. This changes Clerk from resigned/obedient to making a choice to warn Rae.",
        "25": "After Young Driver drops them off, add: Driver pops the trunk. 'There's a blanket in there. And water.' Hands shaking, but holds the trunk open. This changes Driver from reluctant/functional to choosing to help."
      }}
    }}
  ],
  "checks_passed_count": 0,
  "total_checks": 10,
  "overall_notes": "<1-2 sentence summary>"
}}

RULES:
- Run ALL 10 checks. Do NOT skip any. Check #10 (Covenant of the Arc) is MANDATORY.
- For PASSED checks: failing_scene_numbers is empty array, fix_per_scene is empty object.
- For FAILED checks: failing_scene_numbers MUST list every scene number with the problem.
  fix_per_scene MUST have an entry for EACH failing scene number with a CONCRETE rewrite
  direction — what to DELETE, what to REPLACE it with, what the new dialogue/action should be.
  Do NOT write vague instructions like "make the hero more proactive" — write SPECIFIC
  replacement content like "Replace hero's question 'What do we do?' with hero grabbing the
  fire extinguisher and saying 'Cover the east door. I'll take the roof.'"
- For Check #10 specifically: the fix_per_scene instruction MUST name the static character,
  state what their current unchanged behavior is, and provide 1-3 lines of NEW action/dialogue
  that shows the character's behavior CHANGING from their first moment to their last moment.
- CITE SPECIFIC DIALOGUE from the scenes. QUOTE the exact words.
- Be HARSH. The goal is to catch every problem before the next draft."""

    ACT_REVISION_TEMPLATE = """TARGETED SCENE REVISION {revision_round} for {act_label}.

An independent script doctor found problems in SPECIFIC scenes. You must rewrite ONLY the
broken scenes listed below. The other scenes in this act are FINE — do NOT touch them.

This is revision attempt #{revision_round}. {revision_urgency}

═══════════════════════════════════════════════════════
SCENES THAT NEED REWRITING (only these — nothing else):
═══════════════════════════════════════════════════════

{targeted_scenes_with_fixes}

═══════════════════════════════════════════════════════

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

HERO:
{hero_summary}

CHARACTERS:
{characters_summary}

CHARACTER VOICE GUIDE:
{character_identifiers}

{previous_acts_context}

BOARD CARDS FOR BROKEN SCENES (structural blueprint):
{broken_cards_json}

═══════════════════════════════════════════════════════
REWRITE CHECKLIST — verify each before outputting:
═══════════════════════════════════════════════════════

{fix_checklist}

OUTPUT: valid JSON with ONLY the rewritten scenes (object with "scenes" array).
Each scene must have the same scene_number, board_card_number, beat, emotional_start,
emotional_end, and conflict as the original. Rewrite the ELEMENTS (action, dialogue,
character cues) to fix the problems. Full scenes, not outlines."""

    def generate_act_prompt(
        self,
        act_cards: List[Dict[str, Any]],
        hero_summary: str,
        characters_summary: str,
        genre: str,
        logline: str,
        title: str,
        previous_scenes: List[Dict[str, Any]],
        character_identifiers: str,
        act_label: str,
        start_scene_number: int,
    ) -> Dict[str, str]:
        """Generate prompt to write all scenes for one act."""
        act_cards_json = json.dumps(act_cards, indent=2, ensure_ascii=False)

        # Build previous acts context — full screenplay text for continuity
        prev_text = self._build_full_previous_acts_text(previous_scenes)
        if previous_scenes:
            previous_acts_context = (
                "PREVIOUS ACTS (already written — read the full screenplay below to maintain "
                "character voice, callbacks, and arc continuity. Do NOT repeat these scenes):\n"
                + prev_text
            )
        else:
            previous_acts_context = prev_text

        genre_scene_guidance = self._build_genre_scene_guidance(genre)
        genre_emotion_note = self._build_genre_emotion_note(genre)

        user_prompt = self.ACT_GENERATION_TEMPLATE.format(
            act_label=act_label,
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
            genre_scene_guidance=genre_scene_guidance,
            genre_emotion_note=genre_emotion_note,
            act_cards_json=act_cards_json,
            previous_acts_context=previous_acts_context,
            start_scene_number=start_scene_number,
            num_cards=len(act_cards),
        )

        prompt_content = f"{self.ACT_GENERATION_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.ACT_GENERATION_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_act_diagnostic_prompt(
        self,
        act_scenes: List[Dict[str, Any]],
        hero_name: str,
        antagonist_name: str,
        characters_summary: str,
        character_identifiers: str,
        act_label: str,
        previous_scenes: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Generate Grok diagnostic prompt to evaluate one act."""
        # Convert scenes to readable text for evaluation
        act_text_parts = []
        for scene in act_scenes:
            num = scene.get("scene_number", "?")
            slug = scene.get("slugline", "?")
            beat = scene.get("beat", "?")
            e_start = scene.get("emotional_start", "?")
            e_end = scene.get("emotional_end", "?")
            conflict = scene.get("conflict", "?")

            act_text_parts.append(f"\n--- SCENE {num} [{beat}] ({e_start}->{e_end}) ---")
            act_text_parts.append(f"{slug}")
            act_text_parts.append(f"Conflict: {conflict}")
            act_text_parts.append(f"Characters: {', '.join(scene.get('characters_present', []))}")

            for elem in scene.get("elements", []):
                etype = elem.get("element_type", "")
                content = elem.get("content", "")
                if etype == "slugline":
                    act_text_parts.append(f"\n{content}\n")
                elif etype == "action":
                    act_text_parts.append(content)
                elif etype == "character":
                    act_text_parts.append(f"                    {content}")
                elif etype == "parenthetical":
                    act_text_parts.append(f"               ({content})")
                elif etype == "dialogue":
                    act_text_parts.append(f"          {content}\n")
                elif etype == "transition":
                    act_text_parts.append(f"                                        {content}\n")

        act_scenes_text = "\n".join(act_text_parts)

        # Previous acts — full screenplay text so Grok can evaluate cross-act coherence
        prev_text = self._build_full_previous_acts_text(previous_scenes)
        if previous_scenes:
            previous_acts_note = (
                "PREVIOUS ACTS (full screenplay text — use for cross-act character arc coherence):\n"
                + prev_text
            )
            # For Act 3+ add a coherence check instruction
            act_num = 0
            if "Act 2B" in act_label or "Act Three" in act_label or "Act 3" in act_label:
                act_num = 3
            elif "Act 4" in act_label:
                act_num = 4
            if act_num >= 3:
                previous_acts_note += (
                    "\n\n## FULL SCREENPLAY COHERENCE CHECK\n"
                    "Now that you have all previous acts plus the current act, evaluate the "
                    "ENTIRE screenplay so far for cross-act coherence:\n"
                    "- Does every recurring character show progression across their appearances?\n"
                    "- Are one-shot characters arcing within their single scene?\n"
                    "- Do character arcs planned in the board cards reach their intended endpoint?\n"
                    "- Are there any characters who appeared in a previous act with a behavioral "
                    "shift but reverted to their old behavior in the current act?\n"
                    "Include any cross-act coherence failures in Check #10 (Covenant of the Arc)."
                )
        else:
            previous_acts_note = "(This is the first act.)"

        user_prompt = self.ACT_DIAGNOSTIC_TEMPLATE.format(
            act_label=act_label,
            act_scenes_text=act_scenes_text,
            hero_name=hero_name,
            antagonist_name=antagonist_name,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
            previous_acts_note=previous_acts_note,
            seeded_arcs_diagnostic_note="",
        )

        prompt_content = f"{self.ACT_DIAGNOSTIC_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.ACT_DIAGNOSTIC_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_act_revision_prompt(
        self,
        act_scenes: List[Dict[str, Any]],
        failures: List[Dict[str, Any]],
        act_cards: List[Dict[str, Any]],
        hero_summary: str,
        characters_summary: str,
        character_identifiers: str,
        previous_scenes: List[Dict[str, Any]],
        act_label: str,
        title: str,
        logline: str,
        genre: str,
        revision_round: int = 1,
    ) -> Dict[str, str]:
        """Generate prompt to revise ONLY the broken scenes based on Grok's diagnostic feedback.

        Grok now returns failing_scene_numbers and fix_per_scene for each failure.
        We extract ONLY the scenes that need rewriting, bundle Grok's specific fixes,
        and ask GPT to rewrite just those scenes.
        """
        # 1. Collect all failing scene numbers and their per-scene fixes
        failing_scene_nums = set()
        scene_fixes = {}  # scene_num -> list of (check_name, fix_text)

        for f in failures:
            name = f.get("check_name", "Unknown")
            # Get scene-specific info from Grok's enhanced output
            scene_nums = f.get("failing_scene_numbers", [])
            fix_per_scene = f.get("fix_per_scene", {})

            if scene_nums:
                for sn in scene_nums:
                    failing_scene_nums.add(int(sn))
                    fix_text = fix_per_scene.get(str(sn), f.get("fix_suggestion", ""))
                    scene_fixes.setdefault(int(sn), []).append((name, fix_text))
            else:
                # Fallback: Grok didn't provide scene numbers — use problem_details to guess
                problem = f.get("problem_details", "")
                fix = f.get("fix_suggestion", "")
                # Try to extract scene numbers from problem text
                import re
                found_nums = re.findall(r"[Ss]cene\s+(\d+)", problem)
                if found_nums:
                    for sn_str in found_nums:
                        sn = int(sn_str)
                        failing_scene_nums.add(sn)
                        scene_fixes.setdefault(sn, []).append((name, fix))
                else:
                    # Can't determine specific scenes — flag all scenes in act
                    for scene in act_scenes:
                        sn = scene.get("scene_number", 0)
                        failing_scene_nums.add(sn)
                        scene_fixes.setdefault(sn, []).append((name, fix))

        # 2. Build targeted scene blocks — each broken scene with its specific fixes
        targeted_parts = []
        fix_checklist_parts = []
        broken_cards = []
        check_idx = 0

        for scene in act_scenes:
            sn = scene.get("scene_number", 0)
            if sn not in failing_scene_nums:
                continue

            scene_json = json.dumps(scene, indent=2, ensure_ascii=False)
            fixes_for_scene = scene_fixes.get(sn, [])

            fix_lines = []
            for check_name, fix_text in fixes_for_scene:
                check_idx += 1
                why = self._get_failure_why(check_name)
                fix_lines.append(
                    f"  PROBLEM ({check_name}): {why}\n"
                    f"  FIX: {fix_text}"
                )
                fix_checklist_parts.append(f"[ ] Scene {sn} — {check_name}: {fix_text[:200]}")

            targeted_parts.append(
                f"━━━ SCENE {sn} (MUST REWRITE) ━━━\n"
                f"CURRENT VERSION (broken):\n{scene_json}\n\n"
                f"WHAT'S WRONG AND HOW TO FIX IT:\n" + "\n".join(fix_lines)
            )

            # Find matching board card
            card_num = scene.get("board_card_number", sn)
            for card in act_cards:
                if card.get("card_number") == card_num:
                    broken_cards.append(card)
                    break

        targeted_scenes_with_fixes = "\n\n".join(targeted_parts)
        fix_checklist = "\n".join(fix_checklist_parts)
        broken_cards_json = json.dumps(broken_cards, indent=2, ensure_ascii=False)

        # 2b. Add arc revision guidance if Covenant of the Arc is among failures
        has_arc_failure = any(
            f.get("check_name", "") == "Covenant of the Arc" for f in failures
        )
        if has_arc_failure:
            fix_checklist += (
                "\n\n═══════════════════════════════════════════════════════\n"
                "ARC REVISION GUIDANCE (Covenant of the Arc)\n"
                "═══════════════════════════════════════════════════════\n\n"
                "The checker found characters who don't visibly change. To fix this:\n\n"
                "For each flagged character, find their key moment and rewrite it so:\n"
                "1. Their BEHAVIOR changes (not just their feelings)\n"
                "2. Something in the scene CAUSES the change (a revelation, a choice, a consequence)\n"
                "3. The change is visible in their actions or dialogue — the audience can SEE it\n\n"
                "CRITICAL: The 'almost-arc' is the most common mistake. A character who expresses\n"
                "doubt or discomfort but still does the same thing has NOT arced. The character must\n"
                "take a DIFFERENT ACTION than they would have at the start.\n\n"
                "EXAMPLE OF A FIXED ARC:\n"
                "  BEFORE (no arc): Guard frowns, says 'I don't like this,' follows the order anyway.\n"
                "  AFTER (arc): Guard frowns, says 'I don't like this,' sets down his weapon, walks away.\n"
                "  The guard's behavior CHANGED from obedient to refusing.\n\n"
                "EXAMPLE OF A FIXED ARC:\n"
                "  BEFORE (no arc): Nurse patches up hero silently, hands them a bandage, leaves.\n"
                "  AFTER (arc): Nurse patches up hero, then slips them a keycard. 'Side exit. Go.'\n"
                "  The nurse's behavior CHANGED from dutiful to actively helping at personal risk.\n\n"
                "Check the board card's character_arcs field for each character's planned change.\n"
                "Do NOT add new characters. Only fix the arcs of existing board card characters."
            )

        # 3. Urgency escalates
        if revision_round == 1:
            revision_urgency = "Fix each scene precisely as the script doctor described."
        elif revision_round == 2:
            revision_urgency = "The first revision did NOT fix these scenes. Follow the fix instructions MORE LITERALLY this time."
        elif revision_round == 3:
            revision_urgency = "THIRD attempt. Small tweaks are NOT working. THROW OUT the broken dialogue/action and write completely new content for the flagged scenes."
        elif revision_round >= 4:
            revision_urgency = (
                f"Attempt #{revision_round}. COMPLETELY REWRITE each broken scene FROM SCRATCH. "
                "Do not preserve ANY dialogue or action from the current version. Start fresh "
                "using only the board card as your guide."
            )
        else:
            revision_urgency = ""

        # 4. Previous acts context — full screenplay text for continuity
        prev_text = self._build_full_previous_acts_text(previous_scenes)
        if previous_scenes:
            previous_acts_context = (
                "PREVIOUS ACTS (full screenplay — maintain character voice and arc continuity):\n"
                + prev_text
            )
        else:
            previous_acts_context = "(First act.)"

        user_prompt = self.ACT_REVISION_TEMPLATE.format(
            act_label=act_label,
            targeted_scenes_with_fixes=targeted_scenes_with_fixes,
            broken_cards_json=broken_cards_json,
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
            previous_acts_context=previous_acts_context,
            revision_round=revision_round,
            revision_urgency=revision_urgency,
            fix_checklist=fix_checklist,
        )

        prompt_content = f"{self.ACT_GENERATION_SYSTEM}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.ACT_GENERATION_SYSTEM,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }

    # ── Helpers ────────────────────────────────────────────────────────────

    def _extract_board_cards(self, step_5_artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all board cards from the step 5 artifact into a flat list.

        Args:
            step_5_artifact: The Board artifact with row_1..row_4 or cards list

        Returns:
            List of board card dicts
        """
        cards: List[Dict[str, Any]] = []

        # Try structured row format first
        for row_key in ["row_1_act_one", "row_2_act_two_a", "row_3_act_two_b", "row_4_act_three"]:
            row_cards = step_5_artifact.get(row_key, [])
            if isinstance(row_cards, list):
                cards.extend(row_cards)

        # Fallback: try flat cards list
        if not cards:
            cards = step_5_artifact.get("cards", [])

        # Fallback: try all_cards key
        if not cards:
            cards = step_5_artifact.get("all_cards", [])

        # Fallback: try board sub-object
        if not cards and "board" in step_5_artifact:
            board = step_5_artifact["board"]
            for row_key in ["row_1_act_one", "row_2_act_two_a", "row_3_act_two_b", "row_4_act_three"]:
                row_cards = board.get(row_key, [])
                if isinstance(row_cards, list):
                    cards.extend(row_cards)

        return cards

    @staticmethod
    def _build_full_previous_acts_text(previous_scenes: List[Dict[str, Any]]) -> str:
        """Build full screenplay-formatted text from previous acts' scenes.

        Instead of 1-line summaries, includes the complete screenplay text for each
        previous scene so GPT/Grok can see actual dialogue, action, character behavior,
        and arc continuity.
        """
        if not previous_scenes:
            return "(This is the first act — no previous scenes.)"

        parts = []
        for s in previous_scenes:
            num = s.get("scene_number", "?")
            slug = s.get("slugline", "?")
            beat = s.get("beat", "?")
            e_start = s.get("emotional_start", "?")
            e_end = s.get("emotional_end", "?")
            chars = ", ".join(s.get("characters_present", []))

            parts.append(f"\n=== SCENE {num} — {beat} ===")
            parts.append(f"{slug}")
            parts.append(f"Emotional arc: {e_start} → {e_end}")
            parts.append(f"Characters: {chars}")
            parts.append("")

            # Include full screenplay text from elements
            for elem in s.get("elements", []):
                etype = elem.get("element_type", "")
                content = elem.get("content", "")
                if etype == "slugline":
                    parts.append(f"\n{content}\n")
                elif etype == "action":
                    parts.append(content)
                elif etype == "character":
                    parts.append(f"                    {content}")
                elif etype == "parenthetical":
                    parts.append(f"               ({content})")
                elif etype == "dialogue":
                    parts.append(f"          {content}\n")
                elif etype == "transition":
                    parts.append(f"                                        {content}\n")

        return "\n".join(parts)

    @staticmethod
    def _get_failure_why(check_name: str) -> str:
        """Return a WHY explanation for each diagnostic check failure."""
        why_map = {
            "The Hero Leads": (
                "Audiences disengage when the hero is passive. A hero who asks questions and waits "
                "for others to explain things is a REPORTER, not a protagonist. The hero must DRIVE "
                "the story through commands, decisions, and physical action. Every question mark in "
                "hero dialogue is a red flag — replace questions with statements and actions."
            ),
            "Talking The Plot": (
                "When characters explain plot through dialogue, the audience feels lectured, not "
                "entertained. Real people don't say 'As you know, the AI controls the grid.' They "
                "SHOW it through action: the lights go out, a drone swoops, a screen flashes a "
                "warning. Every line of exposition dialogue must be replaced with a visual action "
                "or a conflict-driven exchange where information leaks through subtext."
            ),
            "Make The Bad Guy Badder": (
                "If the antagonist stays at the same threat level, the story flatlines. Each scene "
                "must show the antagonist getting MORE powerful, MORE dangerous, MORE personal. "
                "The audience needs to feel the noose tightening. Escalate the threat in every scene."
            ),
            "Turn Turn Turn": (
                "Repeating the same type of obstacle at the same difficulty is boring. Each obstacle "
                "must be DIFFERENT in kind and HARDER than the last. If Scene 3 has 'dodge a camera' "
                "and Scene 5 has 'dodge a camera again,' that's a pacing failure. Escalate: camera → "
                "drone swarm → human hunters → system-wide lockdown."
            ),
            "Emotional Color Wheel": (
                "A screenplay that only hits fear/tension/dread is emotionally monotone. The audience "
                "needs variety: a moment of dark humor, a flash of tenderness, unexpected joy, bitter "
                "regret. Even in a thriller, you need at least 4 distinct emotions per act. Add scenes "
                "that hit different emotional notes."
            ),
            "Hi How Are You I'm Fine": (
                "If you cover the character names and can't tell who's speaking, the characters are "
                "interchangeable. Each character needs a DISTINCT voice: different vocabulary, sentence "
                "length, speech patterns, verbal tics. A street-smart bounty hunter doesn't talk like "
                "a tech engineer. Make each character's dialogue unmistakable."
            ),
            "Take a Step Back": (
                "The hero's growth arc needs DISTANCE to travel. If the hero starts already competent "
                "and self-aware, there's no transformation to watch. Push the hero's starting point "
                "FURTHER BACK — more flawed, more wrong, more stubbornly set in bad habits. The bigger "
                "the gap between who they start as and who they become, the more satisfying the arc."
            ),
            "Limp and Eye Patch": (
                "Recurring characters MUST be instantly recognizable by a distinctive physical trait, "
                "habit, or prop. If a character appears in multiple scenes without their identifier, "
                "the audience can't track them. Every time a recurring character appears, reference "
                "their signature trait: a limp, a scar, a verbal tic, a piece of clothing."
            ),
            "Is It Primal": (
                "The story must tap into a UNIVERSAL, primitive instinct that a caveman would understand: "
                "survival, protecting loved ones, fear of death, hunger, revenge. If the stakes feel "
                "abstract or intellectual, the audience won't feel them in their gut."
            ),
            "Covenant of the Arc": (
                "One or more characters go through their scene(s) without visible behavioral change. "
                "Snyder: 'Every single character in your movie must change. EVERYONE.'\n\n"
                "THE MOST COMMON FAILURE IS THE 'ALMOST-ARC': a character who shows doubt or "
                "discomfort but still does the same thing they would have done anyway. A character "
                "who FEELS bad but ACTS the same has NOT arced. The character must take a DIFFERENT "
                "ACTION than they would have at the start of the scene.\n\n"
                "HOW TO FIX — for each flagged character:\n"
                "1. Find their final moment in the scene (their last action or line of dialogue).\n"
                "2. Rewrite it so their BEHAVIOR changes, not just their feelings.\n"
                "3. The change must be caused by something that happened IN the scene.\n"
                "4. Check the board card's character_arcs field for what each character's planned "
                "endpoint should be.\n\n"
                "EXAMPLE FIX 1:\n"
                "  BEFORE (no arc): Guard frowns, says 'I don't like this,' follows the order anyway.\n"
                "  AFTER (arc): Guard frowns, says 'I don't like this,' sets down his weapon and "
                "walks off the job. His behavior CHANGED from obedient to refusing.\n\n"
                "EXAMPLE FIX 2:\n"
                "  BEFORE (no arc): Nurse patches up the hero silently, hands them a bandage, leaves.\n"
                "  AFTER (arc): Nurse patches up the hero, then quietly slips them a keycard. "
                "'Go. Side exit. Now.' Her behavior CHANGED from dutiful to actively helping at risk.\n\n"
                "For each flagged character, rewrite their final moment so their BEHAVIOR changes, "
                "not just their internal state. Do NOT add new characters — only fix the arcs of "
                "existing characters from the board cards."
            ),
        }
        return why_map.get(check_name, "This is a core Save the Cat quality check. Failing it means the screenplay has a structural writing problem that will weaken the final product.")

    def _build_genre_scene_guidance(self, genre: str) -> str:
        """
        Build genre-specific scene writing guidance from GENRE_SCENE_TEMPLATES.

        Args:
            genre: Genre slug (e.g. "dude_with_a_problem")

        Returns:
            Formatted multi-line string with scene_pacing, hero_proactivity,
            dialogue_tone, emotional_palette, and avoid sections.
        """
        templates = self.GENRE_SCENE_TEMPLATES.get(genre, {})
        if not templates:
            return "(No genre-specific guidance available for this genre.)"

        parts = []
        if templates.get("scene_pacing"):
            parts.append(f"SCENE PACING: {templates['scene_pacing']}")
        if templates.get("hero_proactivity"):
            parts.append(f"HERO PROACTIVITY: {templates['hero_proactivity']}")
        if templates.get("dialogue_tone"):
            parts.append(f"DIALOGUE TONE: {templates['dialogue_tone']}")
        if templates.get("emotional_palette"):
            parts.append(f"EMOTIONAL PALETTE: {templates['emotional_palette']}")
        if templates.get("avoid"):
            parts.append(f"AVOID: {templates['avoid']}")

        return "\n\n".join(parts)

    def _build_genre_emotion_note(self, genre: str) -> str:
        """
        Build a one-line genre emotion note for the monolithic prompt's
        Emotional Variety rule (rule 9).

        Args:
            genre: Genre slug

        Returns:
            String like "For DwaP, lean into: fear, near-miss anxiety, ..."
        """
        templates = self.GENRE_SCENE_TEMPLATES.get(genre, {})
        palette = templates.get("emotional_palette", "")
        if not palette:
            return ""
        # Clean genre slug for display
        display_genre = genre.replace("_", " ").title()
        return f"For {display_genre}, lean into: {palette}."

    def _build_character_identifiers(self, step_3_artifact: Dict[str, Any]) -> str:
        """
        Build character voice guide from step 3 artifact, using full prose
        character biographies when available.

        Args:
            step_3_artifact: Hero/characters artifact from Step 3

        Returns:
            Formatted multi-line string with character bios and voice guidance
        """
        sections = []
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        hero_name = hero.get("name", "HERO")

        # Hero
        hero_bio = (hero.get("character_biography") or "").strip()
        hero_archetype = hero.get("archetype", "")
        if hero_bio:
            sections.append(
                f"=== {hero_name} (HERO — {hero_archetype}) ===\n"
                f"{hero_bio}\n"
                f"Arc: {hero.get('opening_state', '?')} → {hero.get('final_state', '?')}"
            )
        else:
            sections.append(
                f"=== {hero_name} (HERO — {hero_archetype}) ===\n"
                f"Goal: {hero.get('stated_goal', '?')}\n"
                f"Need: {hero.get('actual_need', '?')}\n"
                f"Arc: {hero.get('opening_state', '?')} → {hero.get('final_state', '?')}"
            )

        # Antagonist
        antagonist = step_3_artifact.get("antagonist", step_3_artifact.get("antagonist_profile", {}))
        if antagonist and antagonist.get("name"):
            antag_name = antagonist["name"]
            antag_bio = (antagonist.get("character_biography") or "").strip()
            antag_adj = antagonist.get("adjective_descriptor", "")
            if antag_bio:
                sections.append(
                    f"=== {antag_name} (ANTAGONIST — {antag_adj}) ===\n"
                    f"{antag_bio}\n"
                    f"Does NOT arc. Refuses to change — that's why they lose."
                )
            else:
                sections.append(
                    f"=== {antag_name} (ANTAGONIST — {antag_adj}) ===\n"
                    f"Mirror: {antagonist.get('mirror_principle', '?')}\n"
                    f"Moral line: {antagonist.get('moral_difference', '?')}\n"
                    f"Does NOT arc. Refuses to change."
                )

        # B-story
        b_story = step_3_artifact.get("b_story_character", step_3_artifact.get("b_story", {}))
        if b_story and b_story.get("name"):
            b_name = b_story["name"]
            b_bio = (b_story.get("character_biography") or "").strip()
            b_rel = b_story.get("relationship_to_hero", "")
            if b_bio:
                sections.append(
                    f"=== {b_name} (B-STORY — {b_rel}) ===\n"
                    f"{b_bio}\n"
                    f"Arc: {b_story.get('opening_state', '?')} → {b_story.get('final_state', '?')}"
                )
            else:
                sections.append(
                    f"=== {b_name} (B-STORY — {b_rel}) ===\n"
                    f"Theme wisdom: {b_story.get('theme_wisdom', '?')}\n"
                    f"Arc: {b_story.get('opening_state', '?')} → {b_story.get('final_state', '?')}"
                )

        return "\n\n".join(sections) if sections else "(No character data available.)"
