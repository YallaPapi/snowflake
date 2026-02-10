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
- Snyder: "The number one thing a good logline must have is irony."
- Irony is "emotionally intriguing, like an itch you have to scratch."
- If the logline lacks irony, the story concept may be fundamentally off.
- You MUST explicitly state what the ironic element is in the ironic_element field.
- GOOD irony examples from the book:
  * "A cop comes to L.A. to visit his estranged wife and must single-handedly
    take on a band of terrorists who have seized HER building." (Die Hard)
    -- Irony: The cop's personal visit becomes a war zone in his wife's workplace.
  * "A businessman falls in love with a hooker he hires to be his date for
    the weekend." (Pretty Woman)
    -- Irony: Paid transaction becomes real love.
  * "She's the perfect woman -- until she has a drink." (Blind Date)
    -- Irony: Perfection conceals chaos.
  * "A holiday season of supposed family joy is turned on its cynical head." (4 Christmases)
    -- Irony: Christmas = joy, but four Christmases = hell.

COMPONENT 2 -- COMPELLING MENTAL PICTURE:
- Snyder: "A good logline, once said, blossoms in your brain."
- The logline must make you SEE the whole movie -- beginning, middle, and end.
- STRUCTURE RULE: The logline MUST start with the character, described by TYPE
  with an adjective. NEVER start with setting or time. The character is the
  subject of the first clause.
  * CORRECT: "A guilt-ridden bounty hunter must..." (starts with character)
  * CORRECT: "A risk-averse teacher plans on..." (starts with character)
  * CORRECT: "A newly married couple must spend..." (starts with character)
  * WRONG: "In near-future Los Angeles, a bounty hunter..." (starts with setting)
  * WRONG: "When a blackout threatens the city..." (starts with event)
- The logline must imply a TIME FRAME -- when the story takes place and how long
  it spans ("Christmas Day", "one night", "the weekend of a retreat").
- From the logline, the reader should see where the story BEGINS and ENDS.
- "Fish out of water" dynamics or opposites facing off are powerful. Snyder:
  "This is why fish out of water stories are so popular -- you can see the
  potential fireworks of one type of person being thrust into a world outside
  his ken."

COMPONENT 2B -- BREVITY (CRITICAL):
- COUNT YOUR WORDS. The logline must be 15-35 words maximum.
- Study the word counts of Snyder's examples:
  * "She's the perfect woman -- until she has a drink." = 10 words
  * "A newly married couple must spend Christmas Day at each of their four
    divorced parent's homes." = 17 words
  * "A just-hired employee goes on a company weekend and soon discovers
    someone's trying to kill him." = 17 words
  * "A cop comes to L.A. to visit his estranged wife and must single-handedly
    take on a band of terrorists who have seized her building." = 25 words
- If your logline exceeds 35 words, you are EXPLAINING too much. Cut the
  HOW and keep the WHO + WHAT + WHY-IT'S-IRONIC. Let the reader's
  imagination fill in the details.
- BAD (too long, explains mechanics): "In near-future Los Angeles, a bounty
  hunter has one night to hunt a rogue AI hiding inside the city's power grid
  before it triggers a permanent blackout while it hijacks cameras, drones and
  police dispatch to turn the entire city into her pursuer." (48 words, explains
  HOW the AI works instead of hooking with irony)
- GOOD (tight, ironic): "A guilt-ridden bounty hunter must capture a target
  that has no body -- a rogue AI inside the power grid -- in one night, while
  it turns the whole city against her." (31 words, hooks with the "target with
  no body" irony)

COMPONENT 3 -- AUDIENCE AND COST:
- From the logline alone, a reader must be able to infer:
  * TARGET AUDIENCE: Which of the 4 quadrants? (Men Under 25, Men Over 25,
    Women Under 25, Women Over 25). Is it a 4-quadrant movie or niche?
  * BUDGET TIER: Is this a "block comedy" (low budget, one location)? Medium?
    Star-driven? Effects-driven tentpole?
  * GENRE/TONE: Comedy? Thriller? Drama? The tone must be immediately clear.
- Snyder: "That's a whole lot to ask from one lousy line of description, don't
  you think? But it's right there." He infers audience, cost, tone, and genre
  ALL from a single logline like "4 Christmases."

COMPONENT 4 -- KILLER TITLE:
- Title and logline are a "one-two punch" -- they must reinforce each other.
- Snyder: "A great title must have irony and tell the tale."
- The title MUST "Say What It Is" -- pinpoint what THIS particular movie is about.
- The title must TELL THE TALE -- convey the essential story dynamic.
- GOOD TITLES (from the book):
  * "Legally Blonde" -- ironic (blonde = dumb stereotype, legally = smart profession), says what it is, tells the tale.
  * "Nuclear Family" -- ironic double meaning (nuclear = family unit AND radioactive), says what it is.
  * "4 Christmases" -- says exactly what it is (four Christmas celebrations), implies the comedy.
  * "Ride Along" -- says what it is (a ride along with a cop), double meaning (being taken for a ride).
- BAD TITLES (from the book):
  * "For Love or Money" -- Snyder: "Seriously, isn't that title awful? You could call every movie ever made For Love or Money."
  * "Yuletide" -- "says Christmas, but doesn't pinpoint what THIS Christmas movie is about."
  * "The Devil's Own" -- vague, doesn't say what it is despite having Brad Pitt + Harrison Ford.
  * "Crossroads", "Destiny", "Reflections" -- vague, could be anything.
- The title must NOT be "on the nose" or stupid. Compare: "Legally Blonde" (clever)
  vs. "Barbie Goes To Harvard" (stupid) vs. "Totally Law School" (on the nose).

HIGH CONCEPT (the overall quality bar):
- Snyder: "All you had to do is look at the one-sheet and you know 'What is it?'"
- The logline + title must be "high concept" -- easy to see from the logline
  and poster alone. 50% of box office comes from international markets where
  the concept must travel without explanation.
- THE POSTER TEST: You should be able to imagine the movie poster from the
  logline and title alone.
- THE STARBUCKS TEST: If you pitched this logline to a stranger at Starbucks,
  would they lean in or drift away? Snyder road-tested his loglines on strangers:
  "When they start to drift, when they look away, I've lost them."

THE JEALOUSY TEST: When another writer reads your logline, their reaction
should be "Why didn't I think of that!"

OUTPUT FORMAT (JSON):
{{
  "logline": "<1-2 sentence logline, 15-35 words MAX. Start with character type, not setting.>",
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

        Raises:
            ValueError: If required Snowflake artifacts are missing.
        """
        step_0 = snowflake_artifacts.get("step_0")
        if not step_0:
            raise ValueError("Snowflake step_0 artifact is required but missing")
        step_1 = snowflake_artifacts.get("step_1")
        if not step_1:
            raise ValueError("Snowflake step_1 artifact is required but missing")

        # Validate required fields exist — no silent fallbacks
        required_step_0 = ["category", "story_kind", "audience_delight"]
        for field in required_step_0:
            if not step_0.get(field):
                raise ValueError(f"Snowflake step_0 is missing required field: '{field}'")

        if not step_1.get("logline"):
            raise ValueError("Snowflake step_1 is missing required field: 'logline'")

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            category=step_0["category"],
            story_kind=step_0["story_kind"],
            audience_delight=step_0["audience_delight"],
            snowflake_logline=step_1["logline"],
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
        step_0 = snowflake_artifacts.get("step_0")
        if not step_0:
            raise ValueError("Snowflake step_0 artifact is required for revision")
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        revision_user = f"""REVISION REQUIRED for Screenplay Step 1 (Logline).

CURRENT ARTIFACT:
Logline: {current_artifact.get('logline', '')}
Title: {current_artifact.get('title', '')}
Ironic Element: {current_artifact.get('ironic_element', '')}
Character Type: {current_artifact.get('character_type', '')}
Hero Adjective: {current_artifact.get('hero_adjective', '')}
Time Frame: {current_artifact.get('time_frame', '')}
Story Beginning: {current_artifact.get('story_beginning', '')}
Story Ending: {current_artifact.get('story_ending', '')}
Target Audience: {current_artifact.get('target_audience', '')}
Budget Tier: {current_artifact.get('budget_tier', '')}
Genre Tone: {current_artifact.get('genre_tone', '')}
Poster Concept: {current_artifact.get('poster_concept', '')}
High Concept Score: {current_artifact.get('high_concept_score', 0)}

CONTEXT (Snowflake Step 0):
Category: {step_0.get('category', '')}
Story Kind: {step_0.get('story_kind', '')}

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
