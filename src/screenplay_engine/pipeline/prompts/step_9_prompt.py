"""
Step 9 Prompt Template: Marketing Validation (Save the Cat Ch.8 "Final Fade In")

v2.0.0 -- Rewritten against Ch.8 ("Final Fade In") and the Glossary of Save the Cat!
(2005). This is the final pipeline step. It validates that the finished screenplay
still delivers on the promise of its logline, genre, and audience.

Snyder (Ch.8): "If you've followed the advice of Chapter One your loglines and
titles are killer. And ready to go."

Key Ch.8 concepts:
  - Product readiness: logline, title, screenplay, and pitch must all be solid
  - "Every sale has a story" (Hilary Wayne)
  - One-sheet / poster test: would a moviegoer stop at the multiplex?
  - 4-quadrant audience analysis (Glossary): Men Over 25, Men Under 25,
    Women Over 25, Women Under 25
  - Hook (Glossary): "the encapsulation of a movie which grabs your attention"
  - "It is what it is" -- met every criteria, done so creatively
"""

import hashlib
from typing import Dict, Any


class Step9Prompt:
    """Prompt generator for Screenplay Engine Step 9: Marketing Validation"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! marketing validator per Blake Snyder's Chapter 8 "
        "(\"Final Fade In\"). You evaluate whether a finished screenplay still delivers "
        "on the promise of its logline, genre, and audience.\n\n"
        "Snyder (Ch.8): \"If you've followed the advice of Chapter One your loglines "
        "and titles are killer. And ready to go.\"\n\n"
        "You apply the Poster Test, the 4-Quadrant analysis, and the Hook test from "
        "the Save the Cat glossary.\n\n"
        "You output ONLY valid JSON. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """You are the final gate. The screenplay is written. Now: can you SELL it?

Snyder (Ch.8): "Selling a script has a lot more to do with thinking of your screenplay
as a 'business plan' than ever before. A catchy one-line and killer title will get you
noticed. A well-structured screenplay will keep you in the game."

ORIGINAL LOGLINE (Step 1 artifact):
Title: {title}
Logline: {logline}
Hero Type: {character_type}
Hero Adjective: {hero_adjective}
Ironic Element: {ironic_element}
Time Frame: {time_frame}
Target Audience: {target_audience}
Genre/Tone: {genre_tone}
High Concept Score: {high_concept_score}/10
Budget Tier: {budget_tier}
Poster Concept (from logline): {poster_concept}

COMPLETED SCREENPLAY (Step 8 artifact):
Title: {screenplay_title}
Genre: {screenplay_genre}
Total Pages: {total_pages}
Scene Count: {scene_count}
Estimated Duration: {estimated_duration} seconds

SCENE SUMMARY:
{scene_summary}

EVALUATION CRITERIA (evaluate each one against the FINISHED screenplay):

1. LOGLINE STILL ACCURATE (bool):
   - Does the logline still describe what actually happens in the screenplay?
   - If the story drifted during development, identify WHERE it diverged.
   - The core promise of the logline must be fulfilled.
   - Snyder (Ch.8): "You've got your product -- your best screenplay -- and several
     pitches... and if you've followed the advice of Chapter One your loglines and
     titles are killer."

2. GENRE CLEAR (bool):
   - Can a viewer immediately identify the genre/tone from the screenplay?
   - Is the genre's core promise delivered? (e.g., Monster in the House must be scary)
   - Does every scene serve the genre's structural requirements?
   - Snyder (Glossary): "Each genre has its own rules, history and expectations
     from an audience."

3. AUDIENCE DEFINED (bool):
   - Is it clear WHO this screenplay is for?
   - Apply the 4 QUADRANT analysis (Snyder Glossary):
     MEN OVER 25, MEN UNDER 25, WOMEN OVER 25, WOMEN UNDER 25.
   - Snyder: "If you can draw audience from all those quadrants... you are
     guaranteeing yourself a hit."
   - Which quadrants does this screenplay target? Is the content appropriate?
   - Would the target audience find this satisfying?

4. TITLE WORKS (bool):
   - Does the title still "say what it is" in a clever way?
   - Does it create intrigue while accurately representing the story?
   - Would the title attract the target audience?
   - Snyder (Ch.1): A title must "say what it is" and have irony.

5. ONE SHEET CONCEPT / POSTER TEST (str):
   - Describe the movie poster in 2-3 sentences.
   - What single IMAGE would sell this story?
   - What TAGLINE would go under the title?
   - THE POSTER TEST: Imagine the one-sheet on the wall at the multiplex.
     Would a moviegoer passing by STOP and want to see this movie?
   - Snyder (Glossary): "A one-sheet is the broad sheet that shows the stars,
     title and tone of the film. A good one is gold."
   - The poster must convey: genre, tone, stakes, and irony in a single glance.
   - THE HOOK TEST (Glossary): "The hook must blossom in your mind with possibility
     and 'hook' you into wanting more."

6. ISSUES (list):
   - List any marketing problems identified.
   - For EACH criterion that fails, provide a specific fix suggestion.
   - Common problems: drift from logline, unclear genre, muddled audience, weak title,
     poster that doesn't convey the story, missing hook.
   - Also flag if callbacks/running gags are missing -- recurring elements strengthen
     audience connection (Glossary: "our appreciation for these gags grows with each use").
   - Snyder (Ch.8): "It is what it is... If you've done your job, if you've covered
     yourself from every angle, if you've met every criteria and done so creatively,
     that's all you can do."

OUTPUT FORMAT (JSON):
{{
  "logline_still_accurate": true,
  "genre_clear": true,
  "audience_defined": true,
  "title_works": true,
  "one_sheet_concept": "<2-3 sentence movie poster: image description + tagline>",
  "issues": []
}}

If any criterion is false, set it to false and add a detailed issue string to the issues list explaining what went wrong and how to fix it."""

    def generate_prompt(
        self,
        step_8_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Screenplay Step 9 (Marketing Validation).

        Args:
            step_8_artifact: Complete screenplay artifact from Step 8.
            step_1_artifact: Original logline artifact from Step 1.

        Returns:
            Dict with system and user prompts, prompt_hash, and version.
        """
        # Extract Step 1 v2.0.0 logline fields
        title = step_1_artifact.get("title", "MISSING")
        logline = step_1_artifact.get("logline", "MISSING")
        hero_adjective = step_1_artifact.get("hero_adjective", "MISSING")
        character_type = step_1_artifact.get("character_type", "MISSING")
        ironic_element = step_1_artifact.get("ironic_element", "MISSING")
        time_frame = step_1_artifact.get("time_frame", "MISSING")
        target_audience = step_1_artifact.get("target_audience", "MISSING")
        genre_tone = step_1_artifact.get("genre_tone", "MISSING")
        high_concept_score = step_1_artifact.get("high_concept_score", "MISSING")
        budget_tier = step_1_artifact.get("budget_tier", "MISSING")
        poster_concept = step_1_artifact.get("poster_concept", "MISSING")

        # Extract screenplay fields
        screenplay_title = step_8_artifact.get("title", "MISSING")
        screenplay_genre = step_8_artifact.get("genre", "MISSING")
        total_pages = step_8_artifact.get("total_pages", 0)
        scenes = step_8_artifact.get("scenes", [])
        scene_count = len(scenes)
        estimated_duration = step_8_artifact.get("estimated_duration_seconds", 0)

        # Build scene summary with emotional_start/emotional_end (v2.0.0)
        scene_lines = []
        for scene in scenes:
            slugline = scene.get("slugline", "UNKNOWN")
            beat = scene.get("beat", "?")
            # Use emotional_start/emotional_end with legacy fallback
            e_start = scene.get("emotional_start", "")
            e_end = scene.get("emotional_end", "")
            if not e_start and not e_end:
                legacy = scene.get("emotional_polarity", "?")
                e_start = legacy
                e_end = legacy
            characters = ", ".join(scene.get("characters_present", []))
            scene_lines.append(
                f"  - [{beat}] {slugline} (emotion: {e_start} -> {e_end}) "
                f"Characters: {characters}"
            )
        scene_summary = "\n".join(scene_lines) if scene_lines else "NO SCENES AVAILABLE"

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            hero_adjective=hero_adjective,
            character_type=character_type,
            ironic_element=ironic_element,
            time_frame=time_frame,
            target_audience=target_audience,
            genre_tone=genre_tone,
            high_concept_score=high_concept_score,
            budget_tier=budget_tier,
            poster_concept=poster_concept,
            screenplay_title=screenplay_title,
            screenplay_genre=screenplay_genre,
            total_pages=total_pages,
            scene_count=scene_count,
            estimated_duration=estimated_duration,
            scene_summary=scene_summary,
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
        step_8_artifact: Dict[str, Any],
        step_1_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate prompt for revising a marketing validation that failed validation.

        Args:
            current_artifact: The artifact that failed validation.
            validation_errors: List of validation error strings.
            step_8_artifact: Complete screenplay artifact from Step 8.
            step_1_artifact: Original logline artifact from Step 1.

        Returns:
            Dict with system and user prompts for revision.
        """
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        revision_user = f"""REVISION REQUIRED for Screenplay Step 9 (Marketing Validation).

CURRENT ARTIFACT:
Logline Still Accurate: {current_artifact.get('logline_still_accurate', 'MISSING')}
Genre Clear: {current_artifact.get('genre_clear', 'MISSING')}
Audience Defined: {current_artifact.get('audience_defined', 'MISSING')}
Title Works: {current_artifact.get('title_works', 'MISSING')}
One Sheet Concept: {current_artifact.get('one_sheet_concept', 'MISSING')}
Issues: {current_artifact.get('issues', [])}

CONTEXT (Original Logline):
Title: {step_1_artifact.get('title', 'MISSING')}
Logline: {step_1_artifact.get('logline', 'MISSING')}
Target Audience: {step_1_artifact.get('target_audience', 'MISSING')}
Genre/Tone: {step_1_artifact.get('genre_tone', 'MISSING')}

CONTEXT (Screenplay):
Title: {step_8_artifact.get('title', 'MISSING')}
Genre: {step_8_artifact.get('genre', 'MISSING')}
Total Pages: {step_8_artifact.get('total_pages', 0)}

VALIDATION ERRORS:
{error_text}

Fix ALL errors while providing an honest assessment of the screenplay's marketing viability.
Apply the Poster Test, 4-Quadrant analysis, and Hook test.

OUTPUT FORMAT (JSON):
{{
  "logline_still_accurate": true,
  "genre_clear": true,
  "audience_defined": true,
  "title_works": true,
  "one_sheet_concept": "<2-3 sentence movie poster description>",
  "issues": []
}}"""

        prompt_content = f"{self.SYSTEM_PROMPT}{revision_user}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_user,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }
