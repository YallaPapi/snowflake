"""
Step 1 Prompt Template: Logline (Save the Cat Ch.1)
Generates a logline following Blake Snyder's 4 criteria from Snowflake artifacts.

All requirements sourced from Save the Cat! Chapter 1 ("What Is It?").
See docs/stc_audit/ch1_logline_audit.txt for rule-by-rule mapping.
"""

import hashlib
from typing import Dict, Any


class Step1Prompt:
    """Prompt generator for Screenplay Engine Step 1: Logline"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! logline specialist. "
        "Your job is to create a logline and killer title that pass Blake Snyder's "
        "four tests from Chapter 1 of Save the Cat:\n\n"
        "1. IRONY -- an inherent contradiction that hooks interest\n"
        "2. COMPELLING MENTAL PICTURE -- you see the whole movie bloom in your mind\n"
        "3. AUDIENCE AND COST -- who it's for and what it'll cost to make\n"
        "4. KILLER TITLE -- says what it is, has irony, tells the tale\n\n"
        "Plus: the logline must be HIGH CONCEPT -- easy to see from the logline "
        "and poster alone.\n\n"
        "You output ONLY valid JSON. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Generate a Save the Cat logline from the following Snowflake outputs.

SNOWFLAKE STEP 0 (Story Market Position):
Category: {category}
Story Kind: {story_kind}
Audience Delight: {audience_delight}

SNOWFLAKE STEP 1 (One-Sentence Summary):
{snowflake_logline}

=== BLAKE SNYDER'S 4 REQUIREMENTS (FOLLOW EXACTLY) ===

COMPONENT 1 -- IRONY (the hook):
- The logline MUST contain an inherent contradiction or dramatic tension.
- It must be "emotionally intriguing, like an itch you have to scratch."
- If the logline lacks irony, the story concept may be fundamentally off.
- You MUST explicitly state what the ironic element is in the ironic_element field.
- Examples of irony: "a claustrophobic astronaut", "a cop whose own building is seized by terrorists",
  "a businessman falls in love with a hooker he hires for the weekend."

COMPONENT 2 -- COMPELLING MENTAL PICTURE:
- A good logline must "bloom in your mind" -- a whole movie must be implied.
- The logline must show a CHARACTER described by TYPE with an adjective
  (NOT a bare name -- "a risk-averse teacher", "a guilt-ridden bounty hunter",
  "a newly married couple"), facing a DILEMMA with a clear GOAL and OBSTACLE.
- The logline must imply a TIME FRAME -- when the story takes place and how long
  it spans ("Christmas Day", "one night", "the weekend of a retreat").
- From the logline, the reader should see where the story BEGINS and ENDS.
- "Fish out of water" dynamics or opposites facing off are powerful but not required.

COMPONENT 3 -- AUDIENCE AND COST:
- From the logline alone, a reader must be able to infer:
  * TARGET AUDIENCE: Which of the 4 quadrants? (Men Under 25, Men Over 25,
    Women Under 25, Women Over 25). Is it a 4-quadrant movie or niche?
  * BUDGET TIER: Is this a "block comedy" (low budget, one location)? Medium?
    Star-driven? Effects-driven tentpole?
  * GENRE/TONE: Comedy? Thriller? Drama? The tone must be immediately clear.
- Snyder infers ALL of this from loglines like "4 Christmases" and "Die Hard."

COMPONENT 4 -- KILLER TITLE:
- Title and logline form a "one-two punch" -- they must reinforce each other.
- The title MUST have IRONY: "a great title must have irony and tell the tale."
- The title MUST "Say What It Is" -- it must pinpoint what THIS particular movie
  is about. "Legally Blonde" says what it is; "Yuletide" does not.
- The title must TELL THE TALE -- convey the essential story dynamic.
- The title must NOT be vague ("For Love or Money", "Crossroads", "Destiny").
- The title must NOT be "on the nose" or stupid.

HIGH CONCEPT (the overall quality bar):
- The logline + title must be "high concept" -- easy to see from the logline
  and poster alone. 50% of box office comes from international markets where
  the concept must travel without explanation.
- THE POSTER TEST: You should be able to imagine the movie poster from the
  logline and title alone. Describe what that poster looks like.

SNYDER'S LOGLINE EXAMPLES (from the book):
- "A cop comes to L.A. to visit his estranged wife and must single-handedly
  take on a band of terrorists who have seized her building." (Die Hard)
- "A businessman falls in love with a hooker he hires to be his date for
  the weekend." (Pretty Woman)
- "She's the perfect woman -- until she has a drink." (Blind Date)
- "A newly married couple must spend Christmas Day at each of their four
  divorced parent's homes." (4 Christmases)
- "A just-hired employee goes on a company weekend and soon discovers
  someone's trying to kill him." (The Retreat)
- "A risk-averse teacher plans on marrying his dream girl but must first
  accompany his overprotective future brother-in-law -- a cop -- on a ride
  along from hell!" (Ride Along)

THE JEALOUSY TEST: When another writer reads your logline, their reaction
should be "Why didn't I think of that!"

OUTPUT FORMAT (JSON):
{{
  "logline": "<1-2 sentence logline with irony, character type, goal, obstacle, time frame>",
  "title": "<killer title with irony that says what it is and tells the tale>",
  "ironic_element": "<explicit statement of the contradiction/dramatic tension>",
  "hero_adjective": "<adjective for protagonist that creates tension with their situation>",
  "character_type": "<full adjective + type description, e.g. 'guilt-ridden bounty hunter'>",
  "time_frame": "<when the story takes place / deadline>",
  "story_beginning": "<where the story begins, implied by the logline>",
  "story_ending": "<where the story ends, implied by the logline>",
  "target_audience": "<4-quadrant analysis: who is this movie for?>",
  "budget_tier": "<low/medium/high/tentpole with brief justification>",
  "genre_tone": "<genre and tone, e.g. 'sci-fi action thriller'>",
  "poster_concept": "<1-2 sentence visual description of the movie poster>",
  "high_concept_score": 7
}}

Generate ONLY valid JSON. No markdown fences, no commentary outside the JSON."""

    def generate_prompt(self, snowflake_artifacts: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate the full prompt for Screenplay Step 1.

        Args:
            snowflake_artifacts: Dict with 'step_0' and 'step_1' sub-dicts
                step_0 must contain: category, story_kind, audience_delight
                step_1 must contain: logline

        Returns:
            Dict with system and user prompts, prompt_hash, and version
        """
        step_0 = snowflake_artifacts.get("step_0", {})
        step_1 = snowflake_artifacts.get("step_1", {})

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            category=step_0.get("category", "MISSING"),
            story_kind=step_0.get("story_kind", "MISSING"),
            audience_delight=step_0.get("audience_delight", "MISSING"),
            snowflake_logline=step_1.get("logline", "MISSING"),
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
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate prompt for revising a logline that failed validation.

        Args:
            current_artifact: The artifact that failed validation
            validation_errors: List of validation error strings
            snowflake_artifacts: Original Snowflake inputs for context

        Returns:
            Dict with system and user prompts for revision
        """
        step_0 = snowflake_artifacts.get("step_0", {})
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        revision_user = f"""REVISION REQUIRED for Screenplay Step 1 (Logline).

CURRENT ARTIFACT:
Logline: {current_artifact.get('logline', 'MISSING')}
Title: {current_artifact.get('title', 'MISSING')}
Ironic Element: {current_artifact.get('ironic_element', 'MISSING')}
Character Type: {current_artifact.get('character_type', 'MISSING')}
Hero Adjective: {current_artifact.get('hero_adjective', 'MISSING')}
Time Frame: {current_artifact.get('time_frame', 'MISSING')}
Story Beginning: {current_artifact.get('story_beginning', 'MISSING')}
Story Ending: {current_artifact.get('story_ending', 'MISSING')}
Target Audience: {current_artifact.get('target_audience', 'MISSING')}
Budget Tier: {current_artifact.get('budget_tier', 'MISSING')}
Genre Tone: {current_artifact.get('genre_tone', 'MISSING')}
Poster Concept: {current_artifact.get('poster_concept', 'MISSING')}
High Concept Score: {current_artifact.get('high_concept_score', 0)}

CONTEXT (Snowflake Step 0):
Category: {step_0.get('category', 'MISSING')}
Story Kind: {step_0.get('story_kind', 'MISSING')}

VALIDATION ERRORS:
{error_text}

Fix ALL errors while keeping the core story promise intact.
Follow ALL the same requirements as original generation (Snyder's 4 components).

OUTPUT FORMAT (JSON):
{{{{
  "logline": "<1-2 sentence logline with irony>",
  "title": "<killer title with irony that says what it is>",
  "ironic_element": "<explicit statement of the contradiction>",
  "hero_adjective": "<adjective for protagonist>",
  "character_type": "<adjective + type, e.g. 'guilt-ridden bounty hunter'>",
  "time_frame": "<deadline or ticking clock>",
  "story_beginning": "<where the story begins>",
  "story_ending": "<where the story ends>",
  "target_audience": "<4-quadrant analysis>",
  "budget_tier": "<low/medium/high/tentpole with justification>",
  "genre_tone": "<genre and tone>",
  "poster_concept": "<1-2 sentence poster visual>",
  "high_concept_score": 7
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
