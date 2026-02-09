"""
Step 2 Validator: Genre Classification (Save the Cat Ch.2)
Validates genre classification against Blake Snyder's 10 structural genres.

VERSION 2.0.0 — Adds substance checks, runner-up genre, comparable films,
sub-type validation. Maps to audit findings C5-C12.
"""

from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import SnyderGenre, GENRE_DEFINITIONS


class Step2Validator:
    """Validator for Step 2: Genre Classification"""

    VERSION = "2.0.0"

    # Set of valid genre string values for quick lookup
    VALID_GENRES = {g.value for g in SnyderGenre}

    # Minimum word counts for substance checks
    MIN_STORY_ELEMENT_WORDS = 8
    MIN_TWIST_WORDS = 10
    MIN_RULE_WORDS = 8
    MIN_CONVENTION_WORDS = 5

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 2 artifact against genre classification rules.

        Checks:
            1. Genre is one of the 10 valid SnyderGenre values.
            2. Working parts list exists, has enough items, each with substance.
            3. Rules list exists, is non-empty, each rule has substance.
            4. Core question exists and is non-empty.
            5. Working parts match the expected parts for the selected genre.
            6. Twist is identified and substantive (references convention).
            7. Conventions list exists with minimum 2 substantive items.
            8. Genre justification is present and substantive.
            9. Runner-up genre is provided with elimination reasoning.
           10. Comparable films list with at least 3 films.
           11. Sub-type matches genre definition if applicable.

        Args:
            artifact: The genre classification artifact to validate.

        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors: List[str] = []

        # ── 1. Genre value check ──────────────────────────────────────────
        genre_value = artifact.get("genre")
        if not genre_value:
            errors.append("MISSING_GENRE: 'genre' field is required")
        elif genre_value not in self.VALID_GENRES:
            errors.append(
                f"INVALID_GENRE: '{genre_value}' is not a valid Snyder genre. "
                f"Must be one of: {', '.join(sorted(self.VALID_GENRES))}"
            )

        # ── 2. Working parts check ────────────────────────────────────────
        working_parts = artifact.get("working_parts")
        if working_parts is None:
            errors.append("MISSING_WORKING_PARTS: 'working_parts' list is required")
        elif not isinstance(working_parts, list):
            errors.append("INVALID_WORKING_PARTS: 'working_parts' must be a list")
        elif len(working_parts) < 2:
            errors.append(
                f"INSUFFICIENT_WORKING_PARTS: Found {len(working_parts)} working part(s), "
                f"need at least 2"
            )
        else:
            # Check each working part has substantive story_element
            for i, part in enumerate(working_parts):
                if isinstance(part, dict):
                    story_element = part.get("story_element", "")
                    if isinstance(story_element, str):
                        word_count = len(story_element.split())
                        if word_count < self.MIN_STORY_ELEMENT_WORDS:
                            errors.append(
                                f"WEAK_WORKING_PART: working_parts[{i}] story_element "
                                f"has {word_count} words, need at least {self.MIN_STORY_ELEMENT_WORDS}. "
                                f"Explain HOW this part manifests in the story."
                            )

        # ── 3. Rules check ────────────────────────────────────────────────
        rules = artifact.get("rules")
        if rules is None:
            errors.append("MISSING_RULES: 'rules' list is required")
        elif not isinstance(rules, list):
            errors.append("INVALID_RULES: 'rules' must be a list")
        elif len(rules) < 3:
            errors.append(
                f"INSUFFICIENT_RULES: Found {len(rules)} rule(s), "
                f"need at least 3 genre-specific structural constraints"
            )
        else:
            for i, rule in enumerate(rules):
                if isinstance(rule, str) and len(rule.split()) < self.MIN_RULE_WORDS:
                    errors.append(
                        f"WEAK_RULE: rules[{i}] has fewer than {self.MIN_RULE_WORDS} words. "
                        f"Rules must be specific structural constraints, not placeholders."
                    )

        # ── 4. Core question check ────────────────────────────────────────
        core_question = artifact.get("core_question")
        if not core_question:
            errors.append("MISSING_CORE_QUESTION: 'core_question' field is required and must be non-empty")
        elif not isinstance(core_question, str) or not core_question.strip():
            errors.append("EMPTY_CORE_QUESTION: 'core_question' must be a non-empty string")

        # ── 5. Cross-reference working parts with genre definition ────────
        if genre_value and genre_value in self.VALID_GENRES and isinstance(working_parts, list) and len(working_parts) >= 2:
            try:
                genre_enum = SnyderGenre(genre_value)
                expected_definition = GENRE_DEFINITIONS.get(genre_enum, {})
                expected_parts = expected_definition.get("working_parts", [])

                if expected_parts:
                    # Extract part names from the working_parts list
                    provided_part_names = []
                    for part in working_parts:
                        if isinstance(part, dict):
                            name = part.get("part_name", "")
                            provided_part_names.append(name.lower().strip())
                        elif isinstance(part, str):
                            provided_part_names.append(part.lower().strip())

                    # Check that each expected part is accounted for
                    missing_parts = []
                    for expected in expected_parts:
                        expected_lower = expected.lower()
                        found = any(
                            expected_lower in provided or provided in expected_lower
                            for provided in provided_part_names
                        )
                        if not found:
                            missing_parts.append(expected)

                    if missing_parts:
                        errors.append(
                            f"MISSING_GENRE_PARTS: Genre '{genre_value}' requires these working parts "
                            f"that are not present: {', '.join(missing_parts)}"
                        )
            except ValueError:
                pass  # Already caught by check 1

        # ── 6. Twist check (with substance) ──────────────────────────────
        twist = artifact.get("twist")
        if not twist:
            errors.append("MISSING_TWIST: 'twist' field is required and must be non-empty")
        elif not isinstance(twist, str) or not twist.strip():
            errors.append("EMPTY_TWIST: 'twist' must be a non-empty string")
        elif len(twist.split()) < self.MIN_TWIST_WORDS:
            errors.append(
                f"WEAK_TWIST: twist has {len(twist.split())} words, need at least "
                f"{self.MIN_TWIST_WORDS}. Must reference a specific genre convention "
                f"being subverted — 'Give me the same thing, only different.'"
            )

        # ── 7. Conventions check (minimum 2, each substantive) ──────────
        conventions = artifact.get("conventions")
        if conventions is None:
            errors.append("MISSING_CONVENTIONS: 'conventions' list is required")
        elif not isinstance(conventions, list):
            errors.append("INVALID_CONVENTIONS: 'conventions' must be a list")
        elif len(conventions) < 2:
            errors.append(
                f"INSUFFICIENT_CONVENTIONS: Found {len(conventions)} convention(s), "
                f"need at least 2 audience expectations"
            )
        else:
            for i, conv in enumerate(conventions):
                if isinstance(conv, str) and len(conv.split()) < self.MIN_CONVENTION_WORDS:
                    errors.append(
                        f"WEAK_CONVENTION: conventions[{i}] has fewer than "
                        f"{self.MIN_CONVENTION_WORDS} words. Conventions must be "
                        f"substantive audience expectations."
                    )

        # ── 8. Genre justification check ──────────────────────────────────
        justification = artifact.get("genre_justification")
        if not justification:
            errors.append(
                "MISSING_GENRE_JUSTIFICATION: 'genre_justification' field is required — "
                "explain in 1-2 sentences why this genre fits best"
            )
        elif not isinstance(justification, str) or len(justification.strip()) < 20:
            errors.append(
                "WEAK_GENRE_JUSTIFICATION: 'genre_justification' must be at least 20 characters — "
                "provide a substantive explanation of why this genre was chosen"
            )

        # ── 9. Runner-up genre check ─────────────────────────────────────
        runner_up = artifact.get("runner_up_genre")
        if not runner_up:
            errors.append(
                "MISSING_RUNNER_UP: 'runner_up_genre' field is required — "
                "Snyder says borderline cases are where writers get lost"
            )
        elif runner_up not in self.VALID_GENRES:
            errors.append(
                f"INVALID_RUNNER_UP: '{runner_up}' is not a valid Snyder genre"
            )
        elif runner_up == genre_value:
            errors.append(
                "SAME_RUNNER_UP: 'runner_up_genre' must be different from 'genre'"
            )

        runner_up_elim = artifact.get("runner_up_elimination")
        if not runner_up_elim:
            errors.append(
                "MISSING_ELIMINATION: 'runner_up_elimination' is required — "
                "explain why the runner-up genre was eliminated"
            )
        elif isinstance(runner_up_elim, str) and len(runner_up_elim.split()) < 8:
            errors.append(
                "WEAK_ELIMINATION: 'runner_up_elimination' needs at least 8 words — "
                "provide a substantive structural reason for eliminating the runner-up"
            )

        # ── 10. Comparable films check ────────────────────────────────────
        comparable = artifact.get("comparable_films")
        if comparable is None:
            errors.append(
                "MISSING_COMPARABLE_FILMS: 'comparable_films' list is required — "
                "name 3+ films in the same genre this story resembles"
            )
        elif not isinstance(comparable, list):
            errors.append("INVALID_COMPARABLE_FILMS: 'comparable_films' must be a list")
        elif len(comparable) < 3:
            errors.append(
                f"INSUFFICIENT_COMPARABLE_FILMS: Found {len(comparable)} film(s), "
                f"need at least 3 comparable films in the genre lineage"
            )

        # ── 11. Sub-type check (if genre has sub-types) ──────────────────
        if genre_value and genre_value in self.VALID_GENRES:
            try:
                genre_enum = SnyderGenre(genre_value)
                expected_definition = GENRE_DEFINITIONS.get(genre_enum, {})
                defined_sub_types = expected_definition.get("sub_types", [])

                if defined_sub_types:
                    sub_type = artifact.get("sub_type")
                    if not sub_type:
                        errors.append(
                            f"MISSING_SUB_TYPE: Genre '{genre_value}' has sub-types "
                            f"({', '.join(defined_sub_types)}). Identify which sub-type "
                            f"this story belongs to."
                        )
            except ValueError:
                pass

        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """
        Provide specific fix suggestions for each validation error.

        Args:
            errors: List of error strings from validate().

        Returns:
            List of actionable fix suggestions.
        """
        suggestions: List[str] = []

        for error in errors:
            if "MISSING_GENRE" == error.split(":")[0] or "INVALID_GENRE" in error:
                suggestions.append(
                    "Set 'genre' to exactly one of: "
                    "monster_in_the_house, golden_fleece, out_of_the_bottle, "
                    "dude_with_a_problem, rites_of_passage, buddy_love, "
                    "whydunit, fool_triumphant, institutionalized, superhero"
                )
            elif "MISSING_WORKING_PARTS" in error or "INVALID_WORKING_PARTS" in error:
                suggestions.append(
                    "Add a 'working_parts' list with at least 2 items, "
                    "each containing 'part_name' and 'story_element' (8+ words)"
                )
            elif "INSUFFICIENT_WORKING_PARTS" in error:
                suggestions.append(
                    "Add more working parts. Each genre requires at least 2 structural components."
                )
            elif "WEAK_WORKING_PART" in error:
                suggestions.append(
                    "Expand the story_element to at least 8 words explaining "
                    "how this working part manifests in THIS specific story."
                )
            elif "MISSING_GENRE_PARTS" in error:
                suggestions.append(
                    "Ensure all required working parts for the selected genre are included. "
                    "Check GENRE_DEFINITIONS for the expected parts."
                )
            elif "MISSING_RULES" in error or "INVALID_RULES" in error:
                suggestions.append(
                    "Add a 'rules' list with at least 3 genre-specific constraints."
                )
            elif "INSUFFICIENT_RULES" in error:
                suggestions.append(
                    "Add at least 3 rules. Each rule should be a specific structural "
                    "constraint that this screenplay must follow based on its genre."
                )
            elif "WEAK_RULE" in error:
                suggestions.append(
                    "Expand each rule to at least 8 words. Rules must be specific "
                    "structural constraints, not generic placeholders."
                )
            elif "EMPTY_RULES" in error:
                suggestions.append(
                    "Add a 'rules' list with at least 3 genre constraint/rules."
                )
            elif "MISSING_CORE_QUESTION" in error or "EMPTY_CORE_QUESTION" in error:
                suggestions.append(
                    "Add a 'core_question' string stating the central question this genre asks."
                )
            elif "MISSING_TWIST" in error or "EMPTY_TWIST" in error:
                suggestions.append(
                    "Add a 'twist' string explaining what makes this story 'the same thing, only different.'"
                )
            elif "WEAK_TWIST" in error:
                suggestions.append(
                    "Expand twist to at least 10 words. Reference a specific genre "
                    "convention that is being subverted or given a fresh spin."
                )
            elif "MISSING_CONVENTIONS" in error or "INVALID_CONVENTIONS" in error:
                suggestions.append(
                    "Add a 'conventions' list of audience expectations for this genre."
                )
            elif "INSUFFICIENT_CONVENTIONS" in error:
                suggestions.append(
                    "Add at least 2 audience conventions/expectations for the chosen genre."
                )
            elif "WEAK_CONVENTION" in error:
                suggestions.append(
                    "Expand each convention to at least 5 words describing what "
                    "the audience expects to see in this type of story."
                )
            elif "MISSING_GENRE_JUSTIFICATION" in error:
                suggestions.append(
                    "Add a 'genre_justification' string (1-2 sentences) explaining why this "
                    "genre is the best fit for this story."
                )
            elif "WEAK_GENRE_JUSTIFICATION" in error:
                suggestions.append(
                    "Expand genre_justification to at least 20 characters with a substantive "
                    "explanation of why this genre fits."
                )
            elif "MISSING_RUNNER_UP" in error or "INVALID_RUNNER_UP" in error:
                suggestions.append(
                    "Add 'runner_up_genre' — a valid Snyder genre that was your second choice."
                )
            elif "SAME_RUNNER_UP" in error:
                suggestions.append(
                    "runner_up_genre must be a DIFFERENT genre from the primary classification."
                )
            elif "MISSING_ELIMINATION" in error:
                suggestions.append(
                    "Add 'runner_up_elimination' explaining why the runner-up genre was "
                    "eliminated. What structural element disqualifies it?"
                )
            elif "WEAK_ELIMINATION" in error:
                suggestions.append(
                    "Expand runner_up_elimination to at least 8 words with a substantive "
                    "structural reason for eliminating the runner-up genre."
                )
            elif "MISSING_COMPARABLE_FILMS" in error or "INVALID_COMPARABLE_FILMS" in error:
                suggestions.append(
                    "Add 'comparable_films' list with 3+ films in the same genre lineage."
                )
            elif "INSUFFICIENT_COMPARABLE_FILMS" in error:
                suggestions.append(
                    "Add at least 3 comparable films. Name specific movies in the same "
                    "genre that this story structurally resembles."
                )
            elif "MISSING_SUB_TYPE" in error:
                suggestions.append(
                    "This genre has sub-types. Add 'sub_type' field identifying which "
                    "sub-type this story belongs to (check genre definition for valid sub-types)."
                )
            else:
                suggestions.append(f"Review and fix: {error}")

        return suggestions
