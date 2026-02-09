"""
Step 4 Prompt Template: Beat Sheet (BS2)
Generates the 15-beat Blake Snyder Beat Sheet from logline, genre, hero, and Snowflake artifacts.

v2.0.0 -- Rewritten against Ch.4 ("Let's Beat It Out!") of Save the Cat! (2005).
Every beat instruction now includes ALL rules, constraints, and guidance that
Blake Snyder provides in the original text. The 5-part Finale structure from
"Save the Cat! Strikes Back" (2009) has been removed; only original-book rules
remain. Thesis/Antithesis/Synthesis three-world framework codified per beat.
"""

import hashlib
from typing import Dict, Any


class Step4Prompt:
    """Prompt generator for Screenplay Step 4: Beat Sheet (BS2)"""

    VERSION = "2.0.0"

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

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate the full prompt for Step 4 from previous step artifacts."""

        # Extract logline data
        logline = step_1_artifact.get("logline", "")
        title = step_1_artifact.get("title", "")

        # Extract genre data
        genre = step_2_artifact.get("genre", "")
        genre_rules = ", ".join(step_2_artifact.get("rules", []))

        # Extract hero data
        hero = step_3_artifact.get("hero", {})
        antagonist = step_3_artifact.get("antagonist", {})
        b_story = step_3_artifact.get("b_story_character", {})

        # Extract Snowflake narrative data
        snowflake_sentence = snowflake_artifacts.get("step_1", {}).get("one_sentence_summary", "")
        snowflake_moral = snowflake_artifacts.get("step_2", {}).get("moral_premise", "")

        # Disasters from Step 2 paragraph or Step 4 synopsis
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

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            logline=logline,
            title=title,
            genre=genre,
            genre_rules=genre_rules,
            hero_name=hero.get("name", "Unknown"),
            hero_archetype=hero.get("archetype", "Unknown"),
            hero_motivation=hero.get("primal_motivation", "Unknown"),
            hero_stated_goal=hero.get("stated_goal", "Unknown"),
            hero_actual_need=hero.get("actual_need", "Unknown"),
            save_the_cat_moment=hero.get("save_the_cat_moment", "Unknown"),
            six_things=", ".join(hero.get("six_things_that_need_fixing", [])),
            opening_state=hero.get("opening_state", "Unknown"),
            final_state=hero.get("final_state", "Unknown"),
            antagonist_name=antagonist.get("name", "Unknown"),
            antagonist_power=antagonist.get("power_level", "Unknown"),
            antagonist_mirror=antagonist.get("mirror_principle", "Unknown"),
            b_story_name=b_story.get("name", "Unknown"),
            b_story_relationship=b_story.get("relationship_to_hero", "Unknown"),
            b_story_wisdom=b_story.get("theme_wisdom", "Unknown"),
            snowflake_sentence=snowflake_sentence,
            snowflake_moral=snowflake_moral,
            snowflake_disaster_1=snowflake_disaster_1,
            snowflake_disaster_2=snowflake_disaster_2,
            snowflake_disaster_3=snowflake_disaster_3,
            snowflake_synopsis=snowflake_synopsis,
        )

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
