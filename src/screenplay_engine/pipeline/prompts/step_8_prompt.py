"""
Step 8 Prompt Template: Screenplay Writing (Save the Cat end of Ch.5)

v2.0.0 -- Rewritten against Ch.5 ("Building The Perfect Beast") of Save the Cat!
(2005). The screenplay step expands the 40 board cards into full screenplay scenes.
Snyder's "Deep Sea Dive" checklist (Ch.5 lines 247-261) is the transition from
planning to writing. Each scene is a "mini-movie" with beginning, middle, end,
emotional change (+/- to -/+), and conflict (><).
"""

import hashlib
import json
from typing import Dict, Any, List


class Step8Prompt:
    """Prompt generator for Screenplay Engine Step 8: Screenplay Writing"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! screenwriter. You expand board cards into properly "
        "formatted screenplay scenes following standard industry format. Every scene "
        "is a mini-movie with beginning, middle, and end. Every scene SHOWS, never "
        "tells. You write rich, cinematic scenes with sustained dialogue exchanges, "
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

BOARD CARDS (scene cards to expand):
{board_cards_json}

BEAT PAGE TARGETS (for pacing — 1 page = 60 seconds):
  Opening Image: page 1 | Theme Stated: page 5 | Set-Up: pages 1-10
  Catalyst: page 12 | Debate: pages 12-25 | Break into Two: page 25
  B Story: page 30 | Fun and Games: pages 30-55 | Midpoint: page 55
  Bad Guys Close In: pages 55-75 | All Is Lost: page 75
  Dark Night of the Soul: pages 75-85 | Break into Three: page 85
  Finale: pages 85-110 | Final Image: page 110

SCENE WRITING RULES:

Each scene is a MINI-MOVIE with a beginning, middle, and end. Snyder (Ch.5): "Think of each
scene as a mini-movie. It must have a beginning, middle and an end. And it must also have
something happen that causes the emotional tone to change drastically either from + to - or
from - to +."

1. EMOTIONAL CHANGE: Every scene starts at one emotional polarity and ENDS at the opposite.
   The board card's emotional_start and emotional_end tell you the transition. A scene marked
   + to - means it starts positive and ends negative. Show this change through ACTION.

2. CONFLICT (><): Snyder: "Only one conflict per scene, please. One is plenty." The board
   card specifies who the opposing forces are, what the issue is, and who wins. Build the
   scene around this single conflict.

3. NO INTERNAL MONOLOGUE — everything must be visible or audible on screen.
   WRONG: "She felt nausea rising in her stomach."
   RIGHT: "She grabs the table edge. Her knuckles whiten."
   Snyder (Ch.7): "Character is revealed by action taken not by words spoken."

4. SHOW, DON'T TELL — Snyder: "Movies are stories told in pictures."
   WRONG: "He planned this for months."
   RIGHT: "He opens a drawer. Surveillance photos spill across the desk. Dates circled in red."

5. DIALOGUE must be SPOKEN, SUSTAINED, and CHARACTER-SPECIFIC.
   Each dialogue scene needs MULTIPLE exchanges (3-6 back-and-forth minimum).
   Snyder (Ch.7): "Every character must speak differently. Every character must have a unique
   way of saying even the most mundane chat."
   WRONG: "I need to tell you something important about a matter of great concern."
   RIGHT: "Look, about last night--"

6. VISUAL ENTRY AND EXIT: Every scene opens with a slugline and establishing action (what we
   SEE when we arrive), and ends with a clear reason to cut — a door slam, a look, a revelation,
   a question left hanging.

7. SCENE DENSITY: Each scene should have 5-15 elements. A typical scene includes: slugline,
   establishing action, character introductions, dialogue exchanges, reactive action, and either
   a transition or a strong visual exit. Thin scenes (1-3 elements) are outlines, not screenplay.

8. TIMING: 1 screenplay page = approximately 60 seconds of screen time. An average scene is
   2-3 pages (120-180 seconds). Some scenes are shorter (Opening Image might be 30-60 seconds),
   some are longer (Finale sequences can be 5-10 pages).

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

        # Build board cards JSON
        board_cards = self._extract_board_cards(step_5_artifact)
        board_cards_json = json.dumps(board_cards, indent=2, ensure_ascii=False)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
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
        "You are a Save the Cat! screenwriter. You write ONE screenplay scene at a time "
        "from a board card. Every scene is a mini-movie with beginning, middle, and end. "
        "Every scene SHOWS, never tells. You write rich, cinematic scenes with sustained "
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

CHARACTER VOICE GUIDE (every character MUST sound distinct):
{character_identifiers}

BOARD CARD TO EXPAND:
{board_card_json}

PREVIOUS SCENES (for continuity — do NOT repeat content):
{previous_scenes_summary}
{milestone_guidance}
SCENE WRITING RULES:

1. MINI-MOVIE: Beginning, middle, end. Something happens that changes the emotional tone
   from {emotional_start} to {emotional_end}. Show this change through ACTION.

2. CONFLICT: "{conflict}" — build the entire scene around this single conflict.

3. HERO LEADS: The hero MUST be proactive — making statements, giving commands, driving
   the action. The hero should NOT ask more than 2 questions in this scene. The hero seeks
   information, doesn't wait to receive it. Snyder: "A hero never asks questions."

4. SHOW, DON'T TELL: NO exposition dumps. Characters never explain things the audience or
   other characters already know. NO "as you know" or "let me explain" dialogue. If
   information must be conveyed, show it through action, behavior, or props.
   WRONG: "He planned this for months."
   RIGHT: "He opens a drawer. Surveillance photos spill across the desk."

5. NO INTERNAL MONOLOGUE: Everything must be visible or audible on screen.
   WRONG: "She felt nausea rising in her stomach."
   RIGHT: "She grabs the table edge. Her knuckles whiten."

6. DISTINCT VOICES: Every character speaks differently. Different vocabulary, sentence
   length, rhythm, verbal tics. The Character Voice Guide above tells you HOW each
   character talks. Use it. If you cover the character names, a reader must be able to
   tell who is speaking.

7. CHARACTER IDENTIFIERS: Each recurring character has a visual/behavioral signature from
   the Character Voice Guide. Reference it when they appear in this scene. Snyder: "Every
   character needs 'A Limp and an Eye Patch' — something memorable that sticks them in the
   reader's mind."

8. DIALOGUE: Sustained exchanges — at least 3 back-and-forth (character + dialogue pairs).
   Dialogue serves the scene's conflict, not the writer's need to explain.

9. SCENE DENSITY: 5-15 elements. Slugline, establishing action, character introductions,
   dialogue exchanges, reactive action, visual exit.

10. TIMING: 1 page = 60 seconds. Average scene is 2-3 pages (120-180 seconds).

OUTPUT FORMAT (single scene, valid JSON):
{{
  "scene_number": {scene_number},
  "slugline": "INT./EXT. LOCATION - TIME",
  "int_ext": "INT.",
  "location": "LOCATION NAME",
  "time_of_day": "DAY|NIGHT|DAWN|DUSK|CONTINUOUS",
  "elements": [
    {{"element_type": "slugline", "content": "INT. LOCATION - TIME"}},
    {{"element_type": "action", "content": "Establishing visual."}},
    {{"element_type": "character", "content": "CHARACTER A"}},
    {{"element_type": "dialogue", "content": "Dialogue line."}},
    {{"element_type": "character", "content": "CHARACTER B"}},
    {{"element_type": "dialogue", "content": "Response."}},
    {{"element_type": "action", "content": "Visual exit."}}
  ],
  "estimated_duration_seconds": 150,
  "beat": "{beat}",
  "emotional_start": "{emotional_start}",
  "emotional_end": "{emotional_end}",
  "conflict": "{conflict}",
  "characters_present": [],
  "board_card_number": {card_number}
}}

Write the FULL scene now. Rich, cinematic, with distinct character voices."""

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

        user_prompt = self.SINGLE_SCENE_TEMPLATE.format(
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
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
        "You are a Save the Cat! screenwriter. You expand board cards into properly "
        "formatted screenplay scenes following standard industry format. Every scene "
        "is a mini-movie with beginning, middle, and end. Every scene SHOWS, never "
        "tells. You write rich, cinematic scenes with sustained dialogue exchanges, "
        "specific visual action, and clear emotional transitions.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    ACT_GENERATION_TEMPLATE = """Write ALL scenes for {act_label} from the board cards below.

TITLE: {title}
LOGLINE: {logline}
GENRE: {genre}

HERO:
{hero_summary}

CHARACTERS:
{characters_summary}

CHARACTER VOICE GUIDE (every character MUST sound distinct):
{character_identifiers}

BOARD CARDS TO EXPAND (this act only):
{act_cards_json}

{previous_acts_context}

BEAT PAGE TARGETS (for pacing — 1 page = 60 seconds):
  Opening Image: page 1 | Theme Stated: page 5 | Set-Up: pages 1-10
  Catalyst: page 12 | Debate: pages 12-25 | Break into Two: page 25
  B Story: page 30 | Fun and Games: pages 30-55 | Midpoint: page 55
  Bad Guys Close In: pages 55-75 | All Is Lost: page 75
  Dark Night of the Soul: pages 75-85 | Break into Three: page 85
  Finale: pages 85-110 | Final Image: page 110

SCENE WRITING RULES:

Each scene is a MINI-MOVIE with a beginning, middle, and end. Snyder (Ch.5): "Think of each
scene as a mini-movie."

1. EMOTIONAL CHANGE: Every scene starts at one emotional polarity and ENDS at the opposite.
   The board card's emotional_start and emotional_end tell you the transition.

2. CONFLICT (><): One conflict per scene. The board card specifies opposing forces.

3. HERO LEADS: The hero MUST be proactive — making statements, giving commands, driving
   the action. The hero should NOT ask more than 2 questions per scene. Snyder: "A hero
   never asks questions."

4. SHOW, DON'T TELL: NO exposition dumps. Characters never explain things the audience or
   other characters already know. If information must be conveyed, show it through action.

5. NO INTERNAL MONOLOGUE — everything must be visible or audible on screen.

6. DISTINCT VOICES: Every character speaks differently. Different vocabulary, sentence
   length, rhythm, verbal tics. Use the Character Voice Guide above.

7. CHARACTER IDENTIFIERS: Each recurring character has a visual/behavioral signature from
   the Character Voice Guide. Reference it when they appear.

8. DIALOGUE: Sustained exchanges — at least 3 back-and-forth per dialogue scene.

9. SCENE DENSITY: 5-15 elements per scene.

10. TIMING: 1 page = 60 seconds. Average scene is 2-3 pages (120-180 seconds).

PER-SCENE REQUIRED FIELDS:
scene_number (int), slugline (str), int_ext (str), location (str), time_of_day (str),
elements (array), estimated_duration_seconds (int), beat (str), emotional_start (str),
emotional_end (str), conflict (str), characters_present (array), board_card_number (int)

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
        {{"element_type": "action", "content": "Establishing visual."}},
        {{"element_type": "character", "content": "CHARACTER A"}},
        {{"element_type": "dialogue", "content": "Dialogue line."}},
        {{"element_type": "character", "content": "CHARACTER B"}},
        {{"element_type": "dialogue", "content": "Response."}},
        {{"element_type": "action", "content": "Visual exit."}}
      ],
      "estimated_duration_seconds": 150,
      "beat": "Set-Up",
      "emotional_start": "+",
      "emotional_end": "-",
      "conflict": "Who wants what from whom",
      "characters_present": ["Character A", "Character B"],
      "board_card_number": 1
    }}
  ]
}}

Write ALL {num_cards} scenes for {act_label}. Full scenes, not outlines."""

    ACT_DIAGNOSTIC_SYSTEM = (
        "You are an independent script doctor hired to evaluate a screenplay. You did NOT write "
        "this screenplay — you are reading it with completely fresh eyes. Your job is to be "
        "brutally honest about quality problems. You evaluate against Blake Snyder's Save the Cat "
        "Chapter 7 diagnostic checks.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    ACT_DIAGNOSTIC_TEMPLATE = """Read this act of a screenplay with FRESH EYES and evaluate it against ALL 9 Save the Cat diagnostic checks.

You are NOT the writer. You are an independent evaluator. Be brutally honest.

SCREENPLAY — {act_label}:
{act_scenes_text}

HERO: {hero_name}
ANTAGONIST: {antagonist_name}
CHARACTERS: {characters_summary}
CHARACTER VOICE GUIDE: {character_identifiers}

{previous_acts_note}

RUN ALL 9 DIAGNOSTIC CHECKS:

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

OUTPUT FORMAT (valid JSON):
{{
  "diagnostics": [
    {{
      "check_number": 1,
      "check_name": "The Hero Leads",
      "passed": false,
      "problem_details": "<specific examples from the scenes — quote dialogue, cite scene numbers>",
      "fix_suggestion": "<specific rewrite instructions — which scenes, which lines, what to change>"
    }}
  ],
  "checks_passed_count": 0,
  "total_checks": 9,
  "overall_notes": "<1-2 sentence summary of biggest issues>"
}}

RULES:
- Run ALL 9 checks even if some aren't fully applicable to this act alone.
- For checks that need full-screenplay context (Take a Step Back, Is It Primal), evaluate
  based on what you can see in this act.
- CITE SPECIFIC SCENES AND LINES. Don't be vague.
- Be HARSH. The goal is to catch every problem before the next draft."""

    ACT_REVISION_TEMPLATE = """REVISION REQUIRED for {act_label}.

An independent script doctor found the following problems. Rewrite ALL scenes for this act,
fixing EVERY issue. Keep the same board cards, conflicts, emotional arcs, and characters.

PROBLEMS FOUND BY SCRIPT DOCTOR:
{failures_text}

ORIGINAL SCENES:
{act_scenes_json}

BOARD CARDS (source material):
{act_cards_json}

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

FIX INSTRUCTIONS:
- Address EVERY problem cited by the script doctor
- Keep the same scene count, beat assignments, and emotional arcs
- The hero must be PROACTIVE — commands, declarations, actions. Not questions.
- Characters must sound DIFFERENT from each other. Distinct vocabulary, rhythm, sentence length.
- NO exposition dumps — show through action and behavior, not dialogue explanation
- Each recurring character must display their identifier from the Voice Guide

Output valid JSON with the same format (object with "scenes" array). Write FULL scenes."""

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

        # Build previous acts context
        if previous_scenes:
            prev_parts = []
            for s in previous_scenes:
                num = s.get("scene_number", "?")
                slug = s.get("slugline", "?")
                beat = s.get("beat", "?")
                conflict = s.get("conflict", "?")[:100]
                e_start = s.get("emotional_start", "?")
                e_end = s.get("emotional_end", "?")
                prev_parts.append(f"Scene {num} [{beat}] {slug} | {e_start}->{e_end} | {conflict}")
            previous_acts_context = (
                "PREVIOUS ACTS (already written — do NOT repeat, maintain continuity):\n"
                + "\n".join(prev_parts)
            )
        else:
            previous_acts_context = "(This is the first act — no previous scenes.)"

        user_prompt = self.ACT_GENERATION_TEMPLATE.format(
            act_label=act_label,
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
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

        # Previous acts note
        if previous_scenes:
            prev_summary = []
            for s in previous_scenes:
                prev_summary.append(
                    f"Scene {s.get('scene_number', '?')} [{s.get('beat', '?')}] "
                    f"{s.get('slugline', '?')} | {s.get('emotional_start', '?')}->{s.get('emotional_end', '?')}"
                )
            previous_acts_note = "PREVIOUS ACTS (for context):\n" + "\n".join(prev_summary)
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
    ) -> Dict[str, str]:
        """Generate prompt to revise an act based on Grok's diagnostic feedback."""
        act_scenes_json = json.dumps(act_scenes, indent=2, ensure_ascii=False)
        act_cards_json = json.dumps(act_cards, indent=2, ensure_ascii=False)

        failures_parts = []
        for f in failures:
            name = f.get("check_name", "Unknown")
            problem = f.get("problem_details", "")
            fix = f.get("fix_suggestion", "")
            failures_parts.append(f"[{name}]\nPROBLEM: {problem}\nFIX: {fix}\n")
        failures_text = "\n".join(failures_parts)

        if previous_scenes:
            prev_parts = []
            for s in previous_scenes:
                prev_parts.append(
                    f"Scene {s.get('scene_number', '?')} [{s.get('beat', '?')}] "
                    f"{s.get('slugline', '?')} | {s.get('conflict', '?')[:80]}"
                )
            previous_acts_context = "PREVIOUS ACTS (for continuity):\n" + "\n".join(prev_parts)
        else:
            previous_acts_context = "(First act.)"

        user_prompt = self.ACT_REVISION_TEMPLATE.format(
            act_label=act_label,
            failures_text=failures_text,
            act_scenes_json=act_scenes_json,
            act_cards_json=act_cards_json,
            title=title,
            logline=logline,
            genre=genre,
            hero_summary=hero_summary,
            characters_summary=characters_summary,
            character_identifiers=character_identifiers,
            previous_acts_context=previous_acts_context,
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
