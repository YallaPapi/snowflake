"""
Step 3 Prompt Template: Hero Construction (Save the Cat Ch.3)
Generates prompts for building the protagonist, antagonist, and B-story character
from logline, genre classification, and Snowflake character data.

VERSION 2.0.0 — Adds demographic criterion (R9c/R10), surface-to-primal connection
(R12), fixes Step 1 field references (villain_adjective/primal_goal removed).
"""

import json
import hashlib
from typing import Dict, Any


class Step3Prompt:
    """Prompt generator for Screenplay Engine Step 3: Hero Construction"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! character architect. Build protagonists with "
        "primal motivations, clear arcs, and maximum conflict potential.\n\n"
        "You construct heroes following Blake Snyder's Chapter 3 principles:\n"
        "- Every hero's goal MUST reduce to one of 5 primal urges: "
        "survival, hunger, sex, protection of loved ones, fear of death\n"
        "- THE THREE CRITERIA for the perfect hero (all three required):\n"
        "  1. Offers the MOST CONFLICT in the situation\n"
        "  2. Has the LONGEST EMOTIONAL JOURNEY\n"
        "  3. Is the most DEMOGRAPHICALLY PLEASING (skew young for mass market)\n"
        "- A 'Save the Cat' moment makes the audience root for the hero early\n"
        "- Six things that need fixing are planted in the Set-Up\n"
        "- Opening Image and Final Image must be OPPOSITES\n"
        "- Surface goals MUST connect to primal stakes: 'if it's a promotion at work, "
        "it better damn well be related to winning the hand of X's beloved'\n"
        "- Use PRIMAL relationships: husbands/wives, fathers/daughters, mothers/sons\n"
        "- The antagonist must have an adjective descriptor and block the hero's goal\n\n"
        "Snyder's log line requirement: 'an adjective to describe the hero, "
        "an adjective to describe the bad guy, and a compelling goal we identify "
        "with as human beings.'\n\n"
        "You output ONLY valid JSON. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Construct a complete Save the Cat hero profile from the following inputs.

LOGLINE (from Screenplay Step 1):
Title: {title}
Logline: {logline}
Hero Adjective: {hero_adjective}
Character Type: {character_type}
Ironic Element: {ironic_element}
Time Frame: {time_frame}
Target Audience: {target_audience}

GENRE CLASSIFICATION (from Screenplay Step 2):
Genre: {genre}
Core Question: {core_question}
Working Parts: {working_parts}
Rules: {genre_rules}

SNOWFLAKE CHARACTER DATA:
{snowflake_character_data}

{genre_hero_constraints}

REQUIREMENTS (FOLLOW EXACTLY):

=== SNYDER'S 3 CRITERIA FOR THE PERFECT HERO ===

Snyder says the hero must satisfy ALL THREE criteria. Do not skip any.

CRITERION 1 — MOST CONFLICT: "What person would offer the most conflict given that situation?" (Ch.3)
- In "Third Grade," the guy who needs to go back most is someone who has yet to grow up.
- In "Ride Along," a risk-averse teacher on a ride-along with an overprotective cop offers more conflict than an ex-Green Beret would.
- WRONG character = wrong movie. The hero must be the WORST possible person for the situation, not the best.

CRITERION 2 — LONGEST EMOTIONAL JOURNEY: "The longest way to go emotionally" (Ch.3)
- The hero who starts farthest from the truth has the biggest arc.
- Snyder: in "Third Grade," the hero is "a guy who needs to go back to third grade, but doesn't know it yet."

CRITERION 3 — MOST DEMOGRAPHICALLY PLEASING: Snyder is blunt: "youth-obsessed Hollywood." (Ch.3)
- "Whenever I find myself drifting into thinking about writing starring roles for Tim Allen, Steve Martin or Chevy Chase, I catch myself."
- "This is who shows up for movies" — skew YOUNG (early-to-mid 20s preferred).
- "If you don't know what 'demographic' means, find out."
- The polo story: a wealthy client said "No one watches TV on Sunday — everyone's out playing polo!" Don't assume your bubble is the market.
- DO NOT just assert "plays strongly across genders." Instead: name 3 comparable films with similar leads that opened well. What age/type were those leads? THAT is your demographic evidence.

=== PRIMAL MOTIVATION (Ch.3) ===

Snyder: "survival, hunger, sex, protection of loved ones, fear of death grab us."

CRITICAL: The primal stake must be PRESENT IN or DERIVABLE FROM the logline itself. It cannot be a new detail invented at the hero-construction stage.

TEST: Can you point to a word or phrase in the logline that directly implies the primal relationship? If not, the connection is manufactured.

- GOOD: In "Ride Along," the logline says the teacher is wooing the cop's sister. The primal stake (love of the woman) is stated in the premise. You can point to it.
- GOOD: In "4 Christmases," the logline says a couple visits four families on Christmas. The primal stake (staying together despite family chaos) is the premise itself.
- BAD: The logline says "bounty hunter hunts a criminal in the power grid," then the hero profile invents "her brother depends on powered medical equipment." The brother does not exist in the logline. He was added after the fact specifically to manufacture primal stakes. This is a coincidence designed to force emotional weight that the premise does not naturally contain.
- BAD: The logline is about a corporate heist, then the hero profile adds "the hero's daughter will lose her scholarship if this fails." The daughter was not part of the premise.

If the logline does NOT contain a primal relationship, you must either:
  (a) Derive one that is a NECESSARY CONSEQUENCE of the premise (e.g., a city blackout naturally threatens everyone the hero knows — that IS the premise), or
  (b) Flag that the logline itself needs revision to include primal stakes.

Snyder: "if it's a promotion at work, it better damn well be related to winning the hand of X's beloved."

PRIMAL RELATIONSHIPS: Snyder says audiences respond to these relationship types because "you say 'father' and I see MY father":
  - husbands/wives, fathers/daughters, mothers/sons, brothers/sisters, ex-boyfriends/girlfriends
  - NOT: colleagues, mentors, bosses, strangers, contacts, informants
  - The B-story character MUST be one of these primal relationship types.

=== HERO PROFILE ===

1. NAME: The protagonist's full name

2. ADJECTIVE_DESCRIPTOR: A short phrase for the logline. Snyder's examples:
   - "risk-averse teacher" (tells you he'll have to face risk)
   - "agoraphobic stenographer" (tells you she'll have to go outside)
   - "milquetoast banker" (tells you he'll have to grow a spine)
   - "henpecked husband" (tells you he'll have to stand up for himself)
   The adjective must telegraph WHERE THE ARC IS GOING. It reveals the flaw the story will fix.

3. AGE_RANGE: The hero's approximate age (e.g. "early 20s", "late 20s"). Snyder: skew YOUNG. "This is who shows up for movies." Early-to-mid 20s is the sweet spot for mass market.

4. GENDER: The hero's gender

5. ARCHETYPE: Must be EXACTLY one of these 10 Snyderian archetypes:
   - young_man_on_the_rise: Harold Lloyd, Adam Sandler, Ashton Kutcher — Horatio Alger, a little dumb but plucky
   - good_girl_tempted: Betty Grable, Doris Day, Reese Witherspoon — pure of heart, cute as a bug
   - the_imp: Jackie Coogan, Macaulay Culkin — clever, resourceful child (or Bad Seed evil opposite)
   - sex_goddess: Mae West, Marilyn Monroe, Halle Berry
   - the_hunk: Rudolph Valentino, Clark Gable, Robert Redford, Vin Diesel
   - wounded_soldier: Paul Newman, Clint Eastwood — going back for one last redemptive mission
   - troubled_sexpot: Veronica Lake, Angelina Jolie
   - lovable_fop: Cary Grant, Hugh Grant
   - court_jester: Danny Kaye, Woody Allen, Rob Schneider
   - wise_grandfather: Alec Guinness, Ian McKellen
   Snyder: "forget the stars and concentrate on the archetypes." The archetype's story arc is sewn into our DNA.

6. PRIMAL_MOTIVATION: Must be EXACTLY one of these 5 PrimalUrge values:
   survival, hunger, sex, protection_of_loved_ones, fear_of_death

7. STATED_GOAL: What the hero consciously says they want

8. ACTUAL_NEED: What the hero actually needs (learned through the theme — often the opposite of stated_goal)

9. SURFACE_TO_PRIMAL_CONNECTION: Explain HOW the stated goal connects to the primal motivation. The connection must be ORGANIC to the premise, not a convenient coincidence. See the primal motivation rules above.

10. MAXIMUM_CONFLICT_JUSTIFICATION: Why THIS hero offers the most conflict. Consider: what other character COULD star in this story? Why would they offer LESS conflict? (Snyder: the ex-Green Beret in "Ride Along" would offer less conflict than the risk-averse teacher.)

11. LONGEST_JOURNEY_JUSTIFICATION: Why THIS hero travels the farthest emotionally. What is the maximum distance from their starting flaw to the truth they must learn?

12. DEMOGRAPHIC_APPEAL_JUSTIFICATION: Name 3 comparable films with similar leads that opened well at the box office. What age/type were those leads? Use THAT as evidence, not assertions about "playing across genders." Snyder: "my solution is to make that great character a teenager, and make that married couple a twenty-something married couple."

13. SAVE_THE_CAT_MOMENT: A specific early scene showing likability through ACTION, not words. Be concrete — what happens? Keep it simple. Snyder's example is literally someone saving a cat. It should cost the hero something small and show they care without seeking credit.

14. SIX_THINGS_THAT_NEED_FIXING: Exactly 6 flaws, needs, or issues planted in the Set-Up that the story will address. Each must be:
   - Specific enough to show in a single scene
   - Plantable in Act 1 (Opening Image through Catalyst)
   - Payable off by the Final Image

15. OPENING_STATE: Who the hero is at the Opening Image. Be specific — not "she's unhappy" but "she does X, avoids Y, and believes Z."

16. FINAL_STATE: Who the hero is at the Final Image. MUST be the EXACT OPPOSITE of opening_state — point for point.

17. THEME_CARRIER: How the protagonist embodies the story's central thematic question

=== ANTAGONIST ===

18. NAME: The antagonist's name

19. ADJECTIVE_DESCRIPTOR: Snyder requires "an adjective to describe the bad guy" in the logline.
    - GOOD: "overprotective cop," "megalomaniac terrorist," "homicidal baker" — these imply PERSONALITY and FLAW
    - BAD: "all-seeing," "powerful," "dangerous" — these describe CAPABILITY, not character
    The adjective must reveal the antagonist's CHARACTER FLAW or twisted worldview, not just their power.

20. POWER_LEVEL: Must indicate the antagonist is "equal" or "superior" to the hero. Snyder: "when in doubt, make the bad guy as bad as possible. Always! The bigger the problem, the greater the odds for our dude to overcome."

21. MORAL_DIFFERENCE: What the antagonist is willing to do that the hero is not. This is the LINE the hero refuses to cross.

22. MIRROR_PRINCIPLE: How the antagonist and hero are "two halves of the same person." They should want the same thing or face the same flaw expressed in opposite ways. Ideally they are COMPETING for the same prize.

=== B-STORY CHARACTER ===

23. NAME: The B-story character's name

24. RELATIONSHIP_TO_HERO: Must be a PRIMAL relationship. Snyder: "husbands and wives, fathers and daughters, mothers and sons, ex-boyfriends and girlfriends, brothers and sisters." NOT a colleague, mentor, or stranger. We respond to these because "you say 'father' and I see MY father."

25. THEME_WISDOM: The specific lesson this character teaches that solves the A-story. The B-story carries the theme — the wisdom learned here is what the hero needs to win the A-story climax.

OUTPUT FORMAT (JSON):
{{
  "hero": {{
    "name": "<full name>",
    "adjective_descriptor": "<for logline>",
    "age_range": "<approximate age e.g. 'late 20s'>",
    "gender": "<gender>",
    "archetype": "<one of 10 ActorArchetype values>",
    "primal_motivation": "<one of 5 PrimalUrge values>",
    "stated_goal": "<what hero says they want>",
    "actual_need": "<what hero actually needs>",
    "surface_to_primal_connection": "<how stated goal connects to primal motivation>",
    "maximum_conflict_justification": "<why this hero offers the most conflict>",
    "longest_journey_justification": "<why this hero has the longest arc>",
    "demographic_appeal_justification": "<why this hero is most demographically pleasing>",
    "save_the_cat_moment": "<specific early scene showing likability through action>",
    "six_things_that_need_fixing": [
      "<flaw/need 1>",
      "<flaw/need 2>",
      "<flaw/need 3>",
      "<flaw/need 4>",
      "<flaw/need 5>",
      "<flaw/need 6>"
    ],
    "opening_state": "<who hero is at Opening Image>",
    "final_state": "<who hero is at Final Image — OPPOSITE of opening_state>",
    "theme_carrier": "<how protagonist embodies the central question>"
  }},
  "antagonist": {{
    "name": "<antagonist name>",
    "adjective_descriptor": "<short descriptor>",
    "power_level": "<equal or superior — explain>",
    "moral_difference": "<what they'll do that hero won't>",
    "mirror_principle": "<how they are two halves of the same person>"
  }},
  "b_story_character": {{
    "name": "<B-story character name>",
    "relationship_to_hero": "<relationship>",
    "theme_wisdom": "<the lesson that solves the A-story>"
  }}
}}"""

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Screenplay Step 3: Hero Construction.

        Args:
            step_1_artifact: Output from Screenplay Step 1 (logline v2.0.0).
                Must contain: logline, title, hero_adjective, character_type,
                ironic_element, time_frame, target_audience.
            step_2_artifact: Output from Screenplay Step 2 (genre classification)
            snowflake_artifacts: Dict with Snowflake pipeline outputs.
                Uses step_3 (character summaries), step_5 (character synopses),
                and step_7 (character bibles) if available.

        Returns:
            Dict with system and user prompts, prompt_hash, and version
        """
        # Extract logline data (Step 1 v2.0.0 fields) — no silent fallbacks
        logline = step_1_artifact.get("logline")
        if not logline:
            raise ValueError("Step 1 artifact is missing required field: 'logline'")
        title = step_1_artifact.get("title")
        if not title:
            raise ValueError("Step 1 artifact is missing required field: 'title'")
        hero_adjective = step_1_artifact.get("hero_adjective")
        if not hero_adjective:
            raise ValueError("Step 1 artifact is missing required field: 'hero_adjective'")
        character_type = step_1_artifact.get("character_type")
        if not character_type:
            raise ValueError("Step 1 artifact is missing required field: 'character_type'")
        ironic_element = step_1_artifact.get("ironic_element")
        if not ironic_element:
            raise ValueError("Step 1 artifact is missing required field: 'ironic_element'")
        time_frame = step_1_artifact.get("time_frame")
        if not time_frame:
            raise ValueError("Step 1 artifact is missing required field: 'time_frame'")
        target_audience = step_1_artifact.get("target_audience")
        if not target_audience:
            raise ValueError("Step 1 artifact is missing required field: 'target_audience'")

        # Extract genre data — no silent fallbacks
        genre = step_2_artifact.get("genre")
        if not genre:
            raise ValueError("Step 2 artifact is missing required field: 'genre'")
        core_question = step_2_artifact.get("core_question")
        if not core_question:
            raise ValueError("Step 2 artifact is missing required field: 'core_question'")
        working_parts = step_2_artifact.get("working_parts")
        if not working_parts:
            raise ValueError("Step 2 artifact is missing required field: 'working_parts'")
        genre_rules = step_2_artifact.get("rules")
        if not genre_rules:
            raise ValueError("Step 2 artifact is missing required field: 'rules'")

        # Format working parts and rules as readable strings
        # Handle both plain strings and dicts with part_name/story_element
        if isinstance(working_parts, list):
            parts = []
            for wp in working_parts:
                if isinstance(wp, dict):
                    parts.append(wp.get("part_name", wp.get("story_element", str(wp))))
                else:
                    parts.append(str(wp))
            working_parts_str = ", ".join(parts)
        else:
            working_parts_str = str(working_parts)

        if isinstance(genre_rules, list):
            rules = []
            for r in genre_rules:
                rules.append(str(r) if not isinstance(r, dict) else r.get("rule", str(r)))
            rules_str = "; ".join(rules)
        else:
            rules_str = str(genre_rules)

        # Build Snowflake character data section
        snowflake_character_data = self._format_snowflake_characters(snowflake_artifacts)

        # Build genre-specific hero constraints
        genre_hero_constraints = self._build_genre_hero_constraints(genre)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            hero_adjective=hero_adjective,
            character_type=character_type,
            ironic_element=ironic_element,
            time_frame=time_frame,
            target_audience=target_audience,
            genre=genre,
            core_question=core_question,
            working_parts=working_parts_str,
            genre_rules=rules_str,
            snowflake_character_data=snowflake_character_data,
            genre_hero_constraints=genre_hero_constraints,
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
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate prompt for revising a hero profile that failed validation.

        Args:
            current_artifact: The artifact that failed validation
            validation_errors: List of validation error strings
            step_1_artifact: Logline artifact for context
            step_2_artifact: Genre artifact for context
            snowflake_artifacts: Original Snowflake inputs for context

        Returns:
            Dict with system and user prompts for revision
        """
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        hero = current_artifact.get("hero", {})
        antagonist = current_artifact.get("antagonist", {})
        b_story = current_artifact.get("b_story_character", {})

        revision_user = f"""REVISION REQUIRED for Screenplay Step 3 (Hero Construction).

CURRENT HERO:
Name: {hero.get('name', 'MISSING')}
Adjective: {hero.get('adjective_descriptor', 'MISSING')}
Age Range: {hero.get('age_range', 'MISSING')}
Gender: {hero.get('gender', 'MISSING')}
Archetype: {hero.get('archetype', 'MISSING')}
Primal Motivation: {hero.get('primal_motivation', 'MISSING')}
Stated Goal: {hero.get('stated_goal', 'MISSING')}
Actual Need: {hero.get('actual_need', 'MISSING')}
Surface to Primal: {hero.get('surface_to_primal_connection', 'MISSING')}
Demographic Appeal: {hero.get('demographic_appeal_justification', 'MISSING')}
Save the Cat Moment: {hero.get('save_the_cat_moment', 'MISSING')}
Opening State: {hero.get('opening_state', 'MISSING')}
Final State: {hero.get('final_state', 'MISSING')}
Theme Carrier: {hero.get('theme_carrier', 'MISSING')}
Six Things: {json.dumps(hero.get('six_things_that_need_fixing', []))}

CURRENT ANTAGONIST:
Name: {antagonist.get('name', 'MISSING')}
Power Level: {antagonist.get('power_level', 'MISSING')}
Mirror Principle: {antagonist.get('mirror_principle', 'MISSING')}

CURRENT B-STORY CHARACTER:
Name: {b_story.get('name', 'MISSING')}
Theme Wisdom: {b_story.get('theme_wisdom', 'MISSING')}

CONTEXT (Logline):
Title: {step_1_artifact.get('title', 'MISSING')}
Logline: {step_1_artifact.get('logline', 'MISSING')}

CONTEXT (Genre):
Genre: {step_2_artifact.get('genre', 'MISSING')}
Core Question: {step_2_artifact.get('core_question', 'MISSING')}

VALIDATION ERRORS:
{error_text}

Fix ALL errors while keeping the core character concept intact.
Follow ALL the same requirements as original generation.

Remember:
- archetype must be EXACTLY one of: young_man_on_the_rise, good_girl_tempted, the_imp, sex_goddess, the_hunk, wounded_soldier, troubled_sexpot, lovable_fop, court_jester, wise_grandfather
- primal_motivation must be EXACTLY one of: survival, hunger, sex, protection_of_loved_ones, fear_of_death
- six_things_that_need_fixing must have EXACTLY 6 items
- opening_state and final_state must be OPPOSITES
- save_the_cat_moment must be at least 20 characters
- age_range and gender are required
- surface_to_primal_connection must explain how stated goal links to primal urge (10+ words)
- demographic_appeal_justification must explain why this hero is demographically pleasing (10+ words)
- antagonist power_level must say "equal" or "superior"
- antagonist must have mirror_principle

OUTPUT FORMAT (JSON):
{{{{
  "hero": {{{{
    "name": "<full name>",
    "adjective_descriptor": "<for logline>",
    "age_range": "<approximate age>",
    "gender": "<gender>",
    "archetype": "<one of 10 ActorArchetype values>",
    "primal_motivation": "<one of 5 PrimalUrge values>",
    "stated_goal": "<what hero says they want>",
    "actual_need": "<what hero actually needs>",
    "surface_to_primal_connection": "<how stated goal connects to primal urge>",
    "maximum_conflict_justification": "<why this hero offers the most conflict>",
    "longest_journey_justification": "<why this hero has the longest arc>",
    "demographic_appeal_justification": "<why this hero is demographically pleasing>",
    "save_the_cat_moment": "<specific early scene showing likability through action>",
    "six_things_that_need_fixing": ["<1>", "<2>", "<3>", "<4>", "<5>", "<6>"],
    "opening_state": "<who hero is at Opening Image>",
    "final_state": "<who hero is at Final Image — OPPOSITE>",
    "theme_carrier": "<how protagonist embodies the central question>"
  }}}},
  "antagonist": {{{{
    "name": "<name>",
    "adjective_descriptor": "<descriptor>",
    "power_level": "<equal or superior>",
    "moral_difference": "<what they'll do that hero won't>",
    "mirror_principle": "<two halves of the same person>"
  }}}},
  "b_story_character": {{{{
    "name": "<name>",
    "relationship_to_hero": "<relationship>",
    "theme_wisdom": "<lesson that solves A-story>"
  }}}}
}}}}"""

        prompt_content = f"{self.SYSTEM_PROMPT}{revision_user}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_user,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }

    def _format_snowflake_characters(self, snowflake_artifacts: Dict[str, Any]) -> str:
        """
        Format Snowflake character data from steps 3, 5, and 7 into readable text.

        Args:
            snowflake_artifacts: Dict with 'step_3', 'step_5', 'step_7' sub-dicts

        Returns:
            Formatted string of character data for the prompt
        """
        sections = []

        # Step 3: Character Summaries (one-paragraph per character)
        step_3 = snowflake_artifacts.get("step_3", {})
        if step_3:
            characters = step_3.get("characters", [])
            if isinstance(characters, list) and characters:
                lines = ["Snowflake Step 3 - Character Summaries:"]
                for char in characters:
                    if isinstance(char, dict):
                        name = char.get("name", "Unknown")
                        summary = char.get("summary", char.get("one_paragraph_summary", ""))
                        if summary:
                            lines.append(f"  - {name}: {summary}")
                sections.append("\n".join(lines))
            elif isinstance(step_3, dict) and "characters" not in step_3:
                # Step 3 might be structured differently
                sections.append(
                    f"Snowflake Step 3 - Character Data:\n{json.dumps(step_3, indent=2)}"
                )

        # Step 5: Character Synopses (expanded character descriptions)
        step_5 = snowflake_artifacts.get("step_5", {})
        if step_5:
            characters = step_5.get("characters", [])
            if isinstance(characters, list) and characters:
                lines = ["Snowflake Step 5 - Character Synopses:"]
                for char in characters:
                    if isinstance(char, dict):
                        name = char.get("name", "Unknown")
                        synopsis = char.get("synopsis", char.get("character_synopsis", ""))
                        if synopsis:
                            # Truncate long synopses for prompt efficiency
                            if len(synopsis) > 500:
                                synopsis = synopsis[:500] + "..."
                            lines.append(f"  - {name}: {synopsis}")
                sections.append("\n".join(lines))

        # Step 7: Character Bibles (full character details)
        step_7 = snowflake_artifacts.get("step_7", {})
        if step_7:
            bibles = step_7.get("bibles", step_7.get("characters", []))
            if isinstance(bibles, list) and bibles:
                lines = ["Snowflake Step 7 - Character Bibles:"]
                for bible in bibles:
                    if isinstance(bible, dict):
                        name = bible.get("name", "Unknown")
                        role = bible.get("role", bible.get("story_role", ""))
                        motivation = bible.get("motivation", "")
                        arc = bible.get("arc", bible.get("character_arc", ""))
                        details = []
                        if role:
                            details.append(f"Role: {role}")
                        if motivation:
                            details.append(f"Motivation: {motivation}")
                        if arc:
                            details.append(f"Arc: {arc}")
                        if details:
                            lines.append(f"  - {name}: {'; '.join(details)}")
                sections.append("\n".join(lines))

        if not sections:
            return "(No Snowflake character data available — generate characters from logline and genre context)"

        return "\n\n".join(sections)

    def _build_genre_hero_constraints(self, genre: str) -> str:
        """
        Build genre-specific hero constraints that tell the AI what kind of
        hero the chosen genre structurally requires.

        Each genre has a different relationship between the hero and the premise.
        Snyder is explicit about what makes the hero "work" for each genre type.
        These constraints prevent the AI from building a hero that contradicts
        the genre's structural engine.

        Args:
            genre: The Snyder genre value (e.g. "dude_with_a_problem")

        Returns:
            A formatted string of genre-specific hero constraints to inject
            into the prompt, or empty string if genre is not recognized.
        """
        constraints = {
            "dude_with_a_problem": """=== GENRE-SPECIFIC HERO CONSTRAINT: DUDE WITH A PROBLEM ===

Snyder defines this genre as: "An ordinary person finds himself in extraordinary circumstances."

The hero MUST be an ORDINARY PERSON. This is the genre's structural requirement — not optional.

What "ordinary" means:
  - The hero does NOT have specialized training that matches the threat.
  - The hero does NOT have professional expertise in the domain of the problem.
  - The hero is someone the audience sees as "just like me."

Snyder's examples:
  - Die Hard: John McClane is an off-duty cop visiting his wife. He has basic police training, but he is NOT a counter-terrorism specialist. He is outgunned, outnumbered, and out of his element.
  - Titanic: Jack Dawson is a penniless artist. He has zero maritime or survival expertise.
  - Breakdown: Kurt Russell is a regular driver. "No super powers or skills, no police training. Nada."
  - The Terminator: Sarah Connor is a waitress. She has no combat training whatsoever.

What to do if the logline's character_type implies professional expertise (e.g., "bounty hunter," "spy," "soldier," "hacker"):
  1. DE-SKILL the hero: make them a rookie, a desk worker, retired, or civilian in that world.
     Example: instead of "expert bounty hunter," make them "a bail-bonds clerk who has never done a field extraction."
  2. Or NEUTRALIZE their expertise: the extraordinary problem must render their professional skills completely useless, forcing them to rely on basic human qualities (courage, stubbornness, love) instead of training.
     Example: a bounty hunter whose digital tracking tools are all controlled by the AI — her expertise is not just unhelpful, it actively works against her. She must survive using only analog instincts, street smarts, and human connections.
  3. Justify explicitly in maximum_conflict_justification WHY this professional is effectively ordinary relative to this specific threat.

The rule: "The more average the person, the bigger the challenge should be." If the hero is already skilled, the problem must be so far outside their skill domain that they are functionally a civilian.""",

            "monster_in_the_house": """=== GENRE-SPECIFIC HERO CONSTRAINT: MONSTER IN THE HOUSE ===

The hero is one of the TRAPPED VICTIMS. They are inside the inescapable space when the monster appears.

Key requirements:
  - The hero (or someone they care about) must have committed or be connected to the SIN that invites the monster. The monster is an avenging force — it punishes transgression.
  - The hero must be TRAPPED — they cannot simply leave. The "house" must be inescapable (a beach town during tourist season, a spaceship in deep space, a family unit bound by blood).
  - The hero's arc is: denial of the monster → confrontation → survival through acknowledging the sin.

Snyder's warning: In Arachnophobia, the residents could leave town at any time. No house = no tension. The hero MUST be unable to escape.""",

            "golden_fleece": """=== GENRE-SPECIFIC HERO CONSTRAINT: GOLDEN FLEECE ===

The hero goes "on the road" in search of one thing and discovers something else: HIMSELF.

Key requirements:
  - The hero has a STATED QUEST (the MacGuffin, the treasure, the destination) but the real story is their internal transformation.
  - Every episode on the road must connect thematically to the hero's inner growth — the incidents are not random adventures.
  - The hero's actual_need is always self-knowledge. They think they want the Golden Fleece; they actually need to understand themselves.

Snyder: "It's not the mileage we're racking up that makes a good Golden Fleece — it's the way the hero changes as he goes." """,

            "out_of_the_bottle": """=== GENRE-SPECIFIC HERO CONSTRAINT: OUT OF THE BOTTLE ===

There are TWO sub-types. The hero must match the correct one:

WISH-FULFILLMENT sub-type:
  - Hero must be a "put-upon Cinderella who is so under the thumb of those around him that we are really rooting for anyone, or anything, to get him a little happiness."
  - Magic grants the wish, but lesson is that "magic isn't everything, it's better to be just like us."
  - Hero must learn the moral: being ordinary is enough.

COMEUPPANCE sub-type:
  - Hero is a JERK who "needs a swift kick in the ass."
  - BUT there must be something redeemable — include a Save the Cat moment showing what's worth saving.
  - The curse IS the lesson: the hero must change to survive it.
  - Example: Jim Carrey in Liar Liar is a lying lawyer cursed to tell the truth.""",

            "rites_of_passage": """=== GENRE-SPECIFIC HERO CONSTRAINT: RITES OF PASSAGE ===

The "monster" is INVISIBLE — it is life itself. The hero faces a painful life transition.

Key requirements:
  - The hero does NOT know they have a problem. Everyone around them sees it except them. This dramatic irony is the genre's engine.
  - The hero's arc follows the Kubler-Ross stages: denial → anger → bargaining → depression → acceptance.
  - Victory = SURRENDER and ACCEPTANCE, not defeating an enemy. "The hero's ability to ultimately smile" is the ending.
  - The "monster" cannot be confronted directly because it has no form — it is aging, addiction, grief, puberty, mid-life crisis.

Examples: Ordinary People (grief), 10 (mid-life crisis), 28 Days (addiction).""",

            "buddy_love": """=== GENRE-SPECIFIC HERO CONSTRAINT: BUDDY LOVE ===

This is about TWO characters who are incomplete halves of a whole.

Key requirements:
  - The two leads must START BY HATING or RESENTING each other. Attraction (if romantic) or friendship comes later.
  - Each character has what the other lacks. Together they are complete; apart they are broken.
  - There must be an EGO SURRENDER moment where one or both give up their pride/independence.
  - These are love stories in disguise — even non-romantic buddy films (Rain Man, E.T., Lethal Weapon).

Construct BOTH leads as a paired unit, not just the "hero." The B-story character IS the other half.""",

            "whydunit": """=== GENRE-SPECIFIC HERO CONSTRAINT: WHYDUNIT ===

The hero is an INVESTIGATOR or AUDIENCE SURROGATE. The audience is the real detective.

Key requirements:
  - The question is WHY, not who. The mystery is about human nature, not puzzle-solving.
  - The hero investigates and discovers a dark truth that is more disturbing than the crime itself.
  - The hero must be drawn into the investigation unwillingly or have a personal connection to the truth.
  - The audience must be able to piece together the truth alongside (or ahead of) the hero.

Examples: Chinatown (Jake discovers institutional evil), Citizen Kane (reporter discovers emptiness behind power).""",

            "fool_triumphant": """=== GENRE-SPECIFIC HERO CONSTRAINT: FOOL TRIUMPHANT ===

The hero is an UNDERDOG FOOL — someone underestimated by everyone.

Key requirements:
  - The hero is dismissed, mocked, or ignored by the INSTITUTION they are up against.
  - There must be an INSIDER ACCOMPLICE — someone inside the institution who secretly helps the fool.
  - The fool wins through luck, pluck, and pure-heartedness, NOT through skill or intelligence.
  - The institution represents rigid rules; the fool represents authentic humanity.

Examples: Forrest Gump (fool vs. history), Being There (fool vs. politics), Amadeus (fool vs. court).""",

            "institutionalized": """=== GENRE-SPECIFIC HERO CONSTRAINT: INSTITUTIONALIZED ===

The story is about a GROUP, not just one hero. There are three required character types:

Key requirements:
  - The GROUP: the institution/family/organization with its own rules and culture.
  - The NEWCOMER: enters the group and either joins or rebels.
  - The BREAKOUT CHARACTER: the one who exposes the fraud/corruption at the heart of the institution.
  - The story must both HONOR the institution (show what draws people to it) and EXPOSE it (show what it costs them).

Examples: One Flew Over the Cuckoo's Nest (McMurphy as newcomer), American Beauty (Lester as breakout), M*A*S*H (Hawkeye navigates the institution).""",

            "superhero": """=== GENRE-SPECIFIC HERO CONSTRAINT: SUPERHERO ===

The hero is an EXTRAORDINARY being in an ORDINARY world. The opposite of Dude with a Problem.

Key requirements:
  - The hero has a POWER or GIFT that sets them apart from everyone else.
  - The nemesis is driven by JEALOUS MEDIOCRITY — they resent the hero's specialness.
  - The story must emphasize the PAIN of being different, not the thrill of having powers.
  - There must be a CREATION MYTH: how did the hero get their power/gift?
  - There must be a CURSE: the power comes at a personal cost.

Examples: Superman (alien isolated by his powers), Gladiator (extraordinary warrior cursed to slavery), A Beautiful Mind (genius cursed by schizophrenia).""",
        }

        return constraints.get(genre, "")
