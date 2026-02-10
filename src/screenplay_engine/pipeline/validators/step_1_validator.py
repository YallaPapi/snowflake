"""
Step 1 Validator: Logline (Save the Cat Ch.1)
Validates logline according to Blake Snyder's 4 criteria from Save the Cat Ch.1.

All rules traced to specific requirements from Chapter 1.
See docs/stc_audit/ch1_logline_audit.txt for the full rule mapping.

V2.0.0: Replaced keyword-matching proxies with structured field validation.
The prompt now forces the LLM to output explicit fields for each Snyder criterion,
and the validator checks those fields exist and are substantial.
"""

import re
from typing import Tuple, List, Dict, Any

# Expanded generic/vague title blocklist (R14, R18)
# Snyder condemns vague titles like "For Love or Money" that could be any movie
VAGUE_TITLES = {
    # Original generic list
    "the story", "untitled", "my story", "the movie", "the film",
    "the script", "the screenplay", "a story", "story", "title",
    "the book", "the novel", "the tale",
    # Common vague single-concept titles (Snyder: "something vague like that kills your interest")
    "destiny", "crossroads", "reflections", "the journey", "redemption",
    "awakening", "eclipse", "convergence", "the path", "shattered",
    "broken", "rising", "the edge", "the line", "aftermath",
    "inheritance", "the reckoning", "reckoning", "the choice",
    "shadows", "echoes", "the fall", "fallen", "the truth",
    "betrayal", "sacrifice", "the promise", "the secret",
    "the beginning", "the end", "genesis", "revelation",
    "the connection", "the one", "the other side",
    "for love or money",  # Snyder's specific bad example
}

# Valid budget tiers
VALID_BUDGET_TIERS = {"low", "medium", "high", "tentpole"}


class Step1Validator:
    """Validator for Screenplay Engine Step 1: Logline (Save the Cat Ch.1)

    Validation strategy: The prompt forces structured output for each of Snyder's
    4 criteria. The validator checks these fields are present and substantial,
    rather than trying to detect qualities via regex keyword matching.
    """

    VERSION = "2.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a Save the Cat logline artifact.

        Structured around Snyder's 4 components plus supporting requirements:
          Component 1: Irony (R3, R4)
          Component 2: Mental Picture (R5, R6, R7, R25)
          Component 3: Audience and Cost (R9, R10, R11, R12)
          Component 4: Killer Title (R13, R14, R15, R16, R18)
          Plus: High Concept (R19), Poster Test (R23)

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # ── Core fields: Logline (R1, R2) ────────────────────────────────
        logline = (artifact.get("logline") or "").strip()
        if not logline:
            errors.append("MISSING_LOGLINE: Logline field is required and must not be empty")
        else:
            errors.extend(self._check_sentence_count(logline))

        # ── Core fields: Title (R13) ─────────────────────────────────────
        title = (artifact.get("title") or "").strip()
        if not title:
            errors.append("MISSING_TITLE: Title field is required and must not be empty")

        # ══════════════════════════════════════════════════════════════════
        # COMPONENT 1: IRONY (R3, R4)
        # ══════════════════════════════════════════════════════════════════
        ironic_element = (artifact.get("ironic_element") or "").strip()
        if not ironic_element:
            errors.append(
                "MISSING_IRONIC_ELEMENT: You must explicitly state the irony/contradiction "
                "in the ironic_element field. Snyder: 'irony is the hook -- it hooks your interest.' "
                "If there is no irony, the story concept may be fundamentally off."
            )
        elif len(ironic_element.split()) < 5:
            errors.append(
                "WEAK_IRONIC_ELEMENT: The ironic_element must be a substantial explanation "
                "of the contradiction (at least 5 words). Simply naming the hero is not irony."
            )

        hero_adj = (artifact.get("hero_adjective") or "").strip()
        if not hero_adj:
            errors.append(
                "MISSING_HERO_ADJECTIVE: A descriptive adjective for the hero is required "
                "(e.g., 'reluctant', 'guilt-ridden', 'risk-averse'). The adjective should "
                "create tension with the hero's situation."
            )

        # ══════════════════════════════════════════════════════════════════
        # COMPONENT 2: COMPELLING MENTAL PICTURE (R5, R6, R7, R25)
        # ══════════════════════════════════════════════════════════════════
        character_type = (artifact.get("character_type") or "").strip()
        if not character_type:
            errors.append(
                "MISSING_CHARACTER_TYPE: Provide the full 'adjective + type' description "
                "(e.g., 'guilt-ridden bounty hunter', 'risk-averse teacher'). "
                "Snyder: characters in loglines are described by TYPE, not bare name."
            )
        elif " " not in character_type:
            errors.append(
                "INCOMPLETE_CHARACTER_TYPE: character_type must be 'adjective + type' "
                f"(got '{character_type}'). Example: 'guilt-ridden bounty hunter', not just 'Rae'."
            )

        time_frame = (artifact.get("time_frame") or "").strip()
        if not time_frame:
            errors.append(
                "MISSING_TIME_FRAME: Logline must imply a time frame -- when the story takes "
                "place and how long it spans. Snyder: 'All three log lines clearly demarcate "
                "a time frame: Christmas Day, the weekend of a retreat, a single night.'"
            )

        story_beginning = (artifact.get("story_beginning") or "").strip()
        if not story_beginning:
            errors.append(
                "MISSING_STORY_BEGINNING: The logline should imply where the story begins. "
                "Snyder: 'we even see where each film begins and ends, don't we?'"
            )

        story_ending = (artifact.get("story_ending") or "").strip()
        if not story_ending:
            errors.append(
                "MISSING_STORY_ENDING: The logline should imply where the story ends. "
                "Snyder: 'we even see where each film begins and ends, don't we?'"
            )

        # Check that the logline itself contains enough substance for a mental picture
        if logline:
            word_count = len(logline.split())
            if word_count < 12:
                errors.append(
                    "LOGLINE_TOO_SHORT: Logline has only {wc} words. A logline that paints "
                    "a compelling mental picture (character + goal + obstacle + time frame) "
                    "typically needs at least 12 words.".format(wc=word_count)
                )
            elif word_count > 40:
                errors.append(
                    "LOGLINE_TOO_LONG: Logline has {wc} words. Snyder's loglines are 10-25 "
                    "words. If yours exceeds 40, you are explaining HOW instead of hooking "
                    "with WHO + WHAT + irony. Cut the mechanics and trust the reader's "
                    "imagination.".format(wc=word_count)
                )

        # ══════════════════════════════════════════════════════════════════
        # COMPONENT 3: AUDIENCE AND COST (R9, R10, R11, R12)
        # ══════════════════════════════════════════════════════════════════
        target_audience = (artifact.get("target_audience") or "").strip()
        if not target_audience:
            errors.append(
                "MISSING_TARGET_AUDIENCE: Specify who this movie is for. Snyder analyzes "
                "loglines for 4-quadrant appeal (Men Under/Over 25, Women Under/Over 25). "
                "Example: '4-quadrant family comedy', 'male 18-34 action core'."
            )

        budget_tier = (artifact.get("budget_tier") or "").strip()
        if not budget_tier:
            errors.append(
                "MISSING_BUDGET_TIER: Specify the production scale (low/medium/high/tentpole). "
                "Snyder: from the logline of '4 Christmases' he infers it's a medium-budget "
                "block comedy. The logline must communicate what it will cost."
            )
        elif budget_tier:
            # Check that the tier keyword is present somewhere in the value
            tier_lower = budget_tier.lower()
            has_valid_tier = any(t in tier_lower for t in VALID_BUDGET_TIERS)
            if not has_valid_tier:
                errors.append(
                    f"INVALID_BUDGET_TIER: budget_tier must include one of: "
                    f"low, medium, high, tentpole. Got: '{budget_tier}'"
                )

        genre_tone = (artifact.get("genre_tone") or "").strip()
        if not genre_tone:
            errors.append(
                "MISSING_GENRE_TONE: Specify the genre/tone (e.g., 'sci-fi action thriller', "
                "'dark romantic comedy'). Snyder: 'Its tone... should be easy to understand.'"
            )

        # ══════════════════════════════════════════════════════════════════
        # COMPONENT 4: KILLER TITLE (R13, R14, R15, R16, R18)
        # ══════════════════════════════════════════════════════════════════
        if title:
            title_words = title.split()
            if len(title_words) < 2:
                errors.append(
                    "WEAK_TITLE: Title should be at least two words. Good titles hint at irony: "
                    "'Legally Blonde', 'Die Hard', 'Nuclear Family', '4 Christmases'."
                )

            # Vague title check (R18) -- expanded blocklist
            if title.lower() in VAGUE_TITLES:
                errors.append(
                    f"VAGUE_TITLE: '{title}' is too vague -- it could be any movie. "
                    f"Snyder: 'something vague like that kills your interest.' "
                    f"The title must pinpoint what THIS particular movie is about."
                )

        # ══════════════════════════════════════════════════════════════════
        # HIGH CONCEPT (R19) + POSTER TEST (R23)
        # ══════════════════════════════════════════════════════════════════
        hc_score = artifact.get("high_concept_score")
        if hc_score is not None and isinstance(hc_score, (int, float)) and hc_score < 4:
            errors.append(
                "LOW_HIGH_CONCEPT: High concept score is below 4/10. "
                "Snyder: a good logline must be 'high concept' -- easy to see from the "
                "logline and poster alone. If a stranger can't immediately grasp and be "
                "hooked by the premise, it's not high concept enough."
            )

        poster_concept = (artifact.get("poster_concept") or "").strip()
        if not poster_concept:
            errors.append(
                "MISSING_POSTER_CONCEPT: Describe the movie poster in 1-2 sentences. "
                "Snyder: 'All you had to do is look at the one-sheet and you know What is it?' "
                "If you can't imagine the poster, the concept isn't high concept enough."
            )
        elif len(poster_concept.split()) < 5:
            errors.append(
                "WEAK_POSTER_CONCEPT: poster_concept must be a substantial visual description "
                "(at least 5 words). A reader should be able to picture the poster."
            )

        return len(errors) == 0, errors

    def _check_sentence_count(self, logline: str) -> List[str]:
        """Check logline is 1-2 sentences, handling abbreviations properly."""
        errors = []
        # Strip known abbreviations before counting
        abbrev_pattern = (
            r'\b(?:Dr|Mr|Mrs|Ms|Jr|Sr|Prof|Rev|Gen|Sgt|Lt|Col|Capt|Cmdr|Adm|'
            r'St|Ave|Blvd|Dept|Est|Inc|Corp|Ltd|Co|vs|etc|approx|ca|U\.S|L\.A)\.'
        )
        cleaned = re.sub(abbrev_pattern, 'ABBR', logline, flags=re.IGNORECASE)
        # Strip decimal numbers (e.g., "3.5 million")
        cleaned = re.sub(r'\d+\.\d+', 'NUM', cleaned)
        # Strip ellipsis
        cleaned = re.sub(r'\.{2,}', '', cleaned)
        # Strip em-dash patterns that might create false periods
        cleaned = re.sub(r'[—–]', ' ', cleaned)

        sentence_endings = re.findall(r'[.!?]+', cleaned)
        sentence_count = len(sentence_endings)

        if sentence_count == 0:
            errors.append(
                "NO_SENTENCE_ENDING: Logline must end with proper punctuation (.!?) "
                "and be 1-2 complete sentences."
            )
        elif sentence_count > 2:
            errors.append(
                f"TOO_MANY_SENTENCES: Logline must be 1-2 sentences "
                f"(found {sentence_count}). Compress into tighter prose."
            )
        return errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """
        Provide specific fix suggestions for each validation error.

        Args:
            errors: List of error strings from validate()

        Returns:
            List of human-readable fix suggestions
        """
        suggestions: List[str] = []

        for error in errors:
            error_upper = error.upper()

            if "MISSING_LOGLINE" in error_upper:
                suggestions.append(
                    "Write a 1-2 sentence logline with irony, a character type, a goal, "
                    "an obstacle, and a time frame."
                )
            elif "NO_SENTENCE_ENDING" in error_upper:
                suggestions.append(
                    "End the logline with proper punctuation (period, exclamation, or question mark)."
                )
            elif "TOO_MANY_SENTENCES" in error_upper:
                suggestions.append(
                    "Compress the logline into 1-2 sentences. Combine clauses or remove "
                    "secondary information."
                )
            elif "MISSING_TITLE" in error_upper:
                suggestions.append(
                    "Add a title that has irony, 'says what it is', and tells the tale. "
                    "Example: 'Legally Blonde', 'Nuclear Family', '4 Christmases'."
                )
            elif "MISSING_IRONIC_ELEMENT" in error_upper:
                suggestions.append(
                    "State the contradiction explicitly in the ironic_element field. "
                    "Example: 'A bounty hunter becomes the hunted -- the person who tracks "
                    "others is now being tracked by the entire city.' "
                    "If you cannot find irony, the story concept may need rethinking."
                )
            elif "WEAK_IRONIC_ELEMENT" in error_upper:
                suggestions.append(
                    "Expand ironic_element to a full explanation of the contradiction. "
                    "It should be clear WHY this premise is ironic -- what two opposing "
                    "forces or ideas create the 'itch you have to scratch.'"
                )
            elif "MISSING_HERO_ADJECTIVE" in error_upper:
                suggestions.append(
                    "Add a single adjective for the hero that creates tension with their "
                    "situation (e.g., 'reluctant', 'guilt-ridden', 'risk-averse', 'naive')."
                )
            elif "MISSING_CHARACTER_TYPE" in error_upper:
                suggestions.append(
                    "Provide the full 'adjective + type' for the protagonist. "
                    "Snyder: 'a risk-averse teacher', 'a newly married couple', "
                    "'a just-hired employee'. Not a bare name like 'John'."
                )
            elif "INCOMPLETE_CHARACTER_TYPE" in error_upper:
                suggestions.append(
                    "character_type needs both an adjective AND a character type/role. "
                    "Format: 'adjective character-type'. Example: 'guilt-ridden bounty hunter'."
                )
            elif "MISSING_TIME_FRAME" in error_upper:
                suggestions.append(
                    "Add a time frame -- when does the story take place and how long does "
                    "it span? 'Christmas Day', 'one night', 'before midnight', 'the weekend "
                    "of a retreat'. Even 'before it's too late' implies urgency."
                )
            elif "MISSING_STORY_BEGINNING" in error_upper:
                suggestions.append(
                    "Describe where the story begins as implied by the logline. "
                    "Example: 'Rae is a bounty hunter monitoring the city from her car.'"
                )
            elif "MISSING_STORY_ENDING" in error_upper:
                suggestions.append(
                    "Describe where the story ends as implied by the logline. "
                    "Example: 'The AI is shut down and the city's power is restored.'"
                )
            elif "LOGLINE_TOO_LONG" in error_upper:
                suggestions.append(
                    "Cut the logline to under 35 words. Remove explanations of HOW "
                    "things work and keep WHO + WHAT + irony. Snyder's Die Hard logline "
                    "is 25 words. Let the reader's imagination fill in the details."
                )
            elif "LOGLINE_TOO_SHORT" in error_upper:
                suggestions.append(
                    "Expand the logline to include character type + goal + obstacle + "
                    "time frame. A compelling mental picture needs enough detail to "
                    "'bloom in your mind.'"
                )
            elif "MISSING_TARGET_AUDIENCE" in error_upper:
                suggestions.append(
                    "Specify the audience using Snyder's 4-quadrant model. "
                    "Example: '4-quadrant with male 18-34 action core' or "
                    "'women 25+ romantic drama core with crossover appeal.'"
                )
            elif "MISSING_BUDGET_TIER" in error_upper or "INVALID_BUDGET_TIER" in error_upper:
                suggestions.append(
                    "Specify budget as low (block comedy/single location), medium "
                    "(star-driven), high (action + VFX), or tentpole (franchise/epic). "
                    "Include a brief justification for the tier."
                )
            elif "MISSING_GENRE_TONE" in error_upper:
                suggestions.append(
                    "Specify the genre/tone clearly. Examples: 'sci-fi action thriller', "
                    "'dark romantic comedy', 'family adventure', 'political drama'."
                )
            elif "WEAK_TITLE" in error_upper:
                suggestions.append(
                    "Make the title at least two words with irony. Good titles: "
                    "'Legally Blonde', 'Die Hard', 'Nuclear Family', 'Blackout Bounty'."
                )
            elif "VAGUE_TITLE" in error_upper:
                suggestions.append(
                    "Replace the vague title with something specific that pinpoints "
                    "what THIS movie is about. The title must 'Say What It Is' -- "
                    "'Legally Blonde' says it, 'Yuletide' does not."
                )
            elif "LOW_HIGH_CONCEPT" in error_upper:
                suggestions.append(
                    "Raise the high concept score by making the logline more universally "
                    "understandable. A stranger at Starbucks should immediately grasp and "
                    "be hooked by the premise. If they wouldn't say 'that sounds cool!' "
                    "it's not high concept enough."
                )
            elif "MISSING_POSTER_CONCEPT" in error_upper:
                suggestions.append(
                    "Describe the movie poster in 1-2 visual sentences. What image, "
                    "character, setting, and mood would the one-sheet convey? "
                    "If you can't picture the poster, the concept isn't clear enough."
                )
            elif "WEAK_POSTER_CONCEPT" in error_upper:
                suggestions.append(
                    "Expand poster_concept to a fuller visual description. Include the "
                    "key character, setting, mood, and one compelling visual detail."
                )
            else:
                suggestions.append("Review and fix the indicated issue.")

        return suggestions
