"""
Step 2 Prompt Template: Genre Classification (Save the Cat Ch.2)
Generates AI prompts to classify story into one of Blake Snyder's 10 structural genres.
"""

import hashlib
from typing import Dict, Any, List

from src.screenplay_engine.models import SnyderGenre, GENRE_DEFINITIONS


class Step2Prompt:
    """Prompt generator for Step 2: Genre Classification"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! genre classification expert. "
        "Classify stories into Blake Snyder's 10 structural genres.\n\n"
        "The 10 genres are:\n"
        "1. monster_in_the_house - Sin invites a monster into an INESCAPABLE space; structure is run and hide (Jaws, Alien, The Exorcist)\n"
        "2. golden_fleece - Hero goes on a road journey searching for one thing, discovers himself; episodes thematically connected (Star Wars, Wizard of Oz)\n"
        "3. out_of_the_bottle - Wish/magic with moral lesson; TWO sub-types: wish-fulfillment (Cinderella underdog) OR comeuppance (jerk gets cursed) (Liar Liar, Bruce Almighty)\n"
        "4. dude_with_a_problem - Ordinary person vs. extraordinary problem; hero wins through individuality not force (Die Hard, Titanic)\n"
        "5. rites_of_passage - Life transition where the monster is INVISIBLE and unnamed; everyone knows except the hero; victory = acceptance (Ordinary People, 28 Days)\n"
        "6. buddy_love - Two characters who START BY HATING each other, are incomplete halves of a whole; these are love stories in disguise (Rain Man, E.T., Lethal Weapon)\n"
        "7. whydunit - Investigation into WHY, not who; audience is the real detective; reveals dark truth about human nature (Chinatown, Citizen Kane)\n"
        "8. fool_triumphant - Underdog fool + institution + insider accomplice; fool wins through luck and pluck (Forrest Gump, Being There, Amadeus)\n"
        "9. institutionalized - Group + newcomer + BREAKOUT CHARACTER who exposes the fraud; both honors AND exposes the institution (Cuckoo's Nest, American Beauty, MASH)\n"
        "10. superhero - Extraordinary being in ordinary world; nemesis is jealous mediocrity; must stress PAIN of being different (Superman, Gladiator, A Beautiful Mind)\n\n"
        "Snyder warns about borderline cases:\n"
        "  - Breakfast Club: Rites of Passage (NOT Institutionalized)\n"
        "  - Rain Man: Buddy Love (NOT Golden Fleece)\n"
        "  - Zoolander: Superhero\n"
        "When in doubt, ask: what is the STRUCTURAL ENGINE of this story?\n\n"
        "You MUST respond with valid JSON only. No markdown, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Classify this story into exactly ONE of Blake Snyder's 10 structural genres.

LOGLINE:
{logline}

TITLE:
{title}

SNOWFLAKE SYNOPSIS:
{synopsis}

INSTRUCTIONS:
1. Classify into exactly ONE genre from: monster_in_the_house, golden_fleece, out_of_the_bottle, dude_with_a_problem, rites_of_passage, buddy_love, whydunit, fool_triumphant, institutionalized, superhero
2. Identify ALL required working parts for the chosen genre and explain how they appear in this story
3. List the genre's structural rules and constraints that this screenplay must follow
4. State the core question the genre asks of the audience
5. Identify the "twist" — what makes this story "the same thing, only different" from other films in this genre. Reference a SPECIFIC convention you are subverting.
6. List audience conventions and expectations for this genre
7. RUNNER-UP: What genre was your second choice? Why did you eliminate it? (Snyder says borderline cases are where writers get lost.)
8. COMPARABLE FILMS: Name 3-5 films in the same genre that this story is most like. State the lineage — "what movie begat what."
9. If the genre has sub-types (e.g. Out of the Bottle has wish-fulfillment vs. comeuppance), identify which sub-type this story is.

GENRE REFERENCE:
{genre_reference}

OUTPUT FORMAT (JSON):
{{
    "genre": "<one of the 10 genre values>",
    "sub_type": "<specific sub-type if applicable, e.g. 'comeuppance_curse', 'catalyst_buddy', or null if genre has no sub-types>",
    "working_parts": [
        {{
            "part_name": "<working part name matching genre definition>",
            "story_element": "<2+ sentences: how this part manifests in THIS story>"
        }}
    ],
    "rules": [
        "<specific structural rule for this genre — how it constrains THIS screenplay>",
        "<another rule — be specific to this story, not generic>"
    ],
    "core_question": "<the central question this genre asks of the audience>",
    "twist": "<what SPECIFIC convention are you subverting, and how? Reference the genre tradition.>",
    "conventions": [
        "<audience expectation 1>",
        "<audience expectation 2>"
    ],
    "genre_justification": "<1-2 sentences explaining why this genre fits best>",
    "runner_up_genre": "<second-choice genre>",
    "runner_up_elimination": "<why the runner-up was eliminated — what structural element disqualifies it?>",
    "comparable_films": [
        "<film 1 in same genre that this story resembles>",
        "<film 2>",
        "<film 3>"
    ]
}}"""

    REVISION_PROMPT_TEMPLATE = """Your previous genre classification had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

LOGLINE:
{logline}

TITLE:
{title}

SNOWFLAKE SYNOPSIS:
{synopsis}

Provide a corrected JSON response that fixes ALL listed errors.
Respond with valid JSON only. No markdown, no commentary."""

    def _build_genre_reference(self) -> str:
        """Build a formatted reference of all genre definitions."""
        lines = []
        for genre, definition in GENRE_DEFINITIONS.items():
            lines.append(f"  {genre.value}:")
            lines.append(f"    Working parts: {', '.join(definition['working_parts'])}")
            lines.append(f"    Core question: {definition['core_question']}")
            lines.append(f"    Core rule: {definition['core_rule']}")
            if definition.get("sub_types"):
                lines.append(f"    Sub-types: {', '.join(definition['sub_types'])}")
            if definition.get("example_films"):
                lines.append(f"    Example films: {', '.join(definition['example_films'][:5])}")
            if definition.get("rules"):
                for i, rule in enumerate(definition["rules"][:3], 1):
                    lines.append(f"    Rule {i}: {rule}")
            lines.append("")
        return "\n".join(lines)

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Step 2 genre classification.

        Args:
            step_1_artifact: The validated Step 1 logline artifact.
            snowflake_artifacts: Snowflake pipeline outputs (synopsis data).

        Returns:
            Dict with system and user prompts plus metadata.
        """
        logline = step_1_artifact.get("logline", step_1_artifact.get("content", ""))
        title = step_1_artifact.get("title", "Untitled")

        # Extract synopsis from snowflake artifacts
        synopsis = ""
        if "step_4" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_4"].get(
                "one_page_synopsis",
                snowflake_artifacts["step_4"].get("synopsis", ""),
            )
        elif "step_2" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_2"].get(
                "paragraph_summary",
                snowflake_artifacts["step_2"].get("summary", ""),
            )

        if not synopsis and "step_1" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_1"].get("logline", "")

        genre_reference = self._build_genre_reference()

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            logline=logline,
            title=title,
            synopsis=synopsis or "No synopsis available",
            genre_reference=genre_reference,
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
        previous_response: Dict[str, Any],
        validation_errors: List[str],
        fix_suggestions: List[str],
        step_1_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate a revision prompt to fix validation errors.

        Args:
            previous_response: The artifact that failed validation.
            validation_errors: List of validation error strings.
            fix_suggestions: List of fix suggestion strings.
            step_1_artifact: The Step 1 logline artifact.
            snowflake_artifacts: Snowflake pipeline outputs.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        import json

        logline = step_1_artifact.get("logline", step_1_artifact.get("content", ""))
        title = step_1_artifact.get("title", "Untitled")

        synopsis = ""
        if "step_4" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_4"].get(
                "one_page_synopsis",
                snowflake_artifacts["step_4"].get("synopsis", ""),
            )
        elif "step_2" in snowflake_artifacts:
            synopsis = snowflake_artifacts["step_2"].get(
                "paragraph_summary",
                snowflake_artifacts["step_2"].get("summary", ""),
            )

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2),
            errors=error_text,
            suggestions=suggestion_text,
            logline=logline,
            title=title,
            synopsis=synopsis or "No synopsis available",
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
