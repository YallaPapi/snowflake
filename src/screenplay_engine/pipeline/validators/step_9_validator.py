"""
Step 9 Validator: Marketing Validation (Save the Cat Ch.8 "Final Fade In")

v2.0.0 -- Validates that the marketing validation artifact contains all required fields
and that the screenplay passes all marketing checks per Chapter 8 and the Glossary.

Checks performed:
  1.  logline_still_accurate exists and is boolean
  2.  genre_clear exists and is boolean
  3.  audience_defined exists and is boolean
  4.  title_works exists and is boolean
  5.  one_sheet_concept exists, is string, >= 30 chars, >= 8 words
  6.  All 4 boolean fields are True (marketing gate)
  7.  issues list exists (can be empty if all pass)
  8.  If issues is non-empty, each issue is a non-empty string
"""

from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import MarketingValidation


class Step9Validator:
    """Validator for Step 9: Marketing Validation (Save the Cat Ch.8)"""

    VERSION = "2.0.0"

    # Minimum length for one_sheet_concept (chars) — must describe image + tagline
    MIN_ONE_SHEET_CHARS = 30

    # Minimum word count for one_sheet_concept — prevents vague descriptions
    MIN_ONE_SHEET_WORDS = 8

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 9 artifact according to Save the Cat marketing requirements.

        Checks:
            1. logline_still_accurate exists and is boolean
            2. genre_clear exists and is boolean
            3. audience_defined exists and is boolean
            4. title_works exists and is boolean
            5. one_sheet_concept exists, is non-empty (>= 30 chars, >= 8 words)
            6. All 4 boolean fields are True (if any False, validation fails)
            7. issues list exists (can be empty if all pass)
            8. If issues is non-empty, each issue is a non-empty string

        Args:
            artifact: The marketing validation artifact to check.

        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors: List[str] = []

        # 1. logline_still_accurate exists and is boolean
        if "logline_still_accurate" not in artifact:
            errors.append("MISSING: logline_still_accurate field is required")
        elif not isinstance(artifact["logline_still_accurate"], bool):
            errors.append(
                "TYPE ERROR: logline_still_accurate must be a boolean, "
                f"got {type(artifact['logline_still_accurate']).__name__}"
            )

        # 2. genre_clear exists and is boolean
        if "genre_clear" not in artifact:
            errors.append("MISSING: genre_clear field is required")
        elif not isinstance(artifact["genre_clear"], bool):
            errors.append(
                "TYPE ERROR: genre_clear must be a boolean, "
                f"got {type(artifact['genre_clear']).__name__}"
            )

        # 3. audience_defined exists and is boolean
        if "audience_defined" not in artifact:
            errors.append("MISSING: audience_defined field is required")
        elif not isinstance(artifact["audience_defined"], bool):
            errors.append(
                "TYPE ERROR: audience_defined must be a boolean, "
                f"got {type(artifact['audience_defined']).__name__}"
            )

        # 4. title_works exists and is boolean
        if "title_works" not in artifact:
            errors.append("MISSING: title_works field is required")
        elif not isinstance(artifact["title_works"], bool):
            errors.append(
                "TYPE ERROR: title_works must be a boolean, "
                f"got {type(artifact['title_works']).__name__}"
            )

        # 5. one_sheet_concept exists, is non-empty (>= 30 chars, >= 8 words)
        if "one_sheet_concept" not in artifact:
            errors.append("MISSING: one_sheet_concept field is required")
        elif not isinstance(artifact["one_sheet_concept"], str):
            errors.append(
                "TYPE ERROR: one_sheet_concept must be a string, "
                f"got {type(artifact['one_sheet_concept']).__name__}"
            )
        else:
            stripped = artifact["one_sheet_concept"].strip()
            if len(stripped) < self.MIN_ONE_SHEET_CHARS:
                errors.append(
                    f"TOO SHORT: one_sheet_concept must be at least "
                    f"{self.MIN_ONE_SHEET_CHARS} characters, "
                    f"got {len(stripped)} characters"
                )
            word_count = len(stripped.split())
            if word_count < self.MIN_ONE_SHEET_WORDS:
                errors.append(
                    f"TOO FEW WORDS: one_sheet_concept must be at least "
                    f"{self.MIN_ONE_SHEET_WORDS} words to describe image and tagline, "
                    f"got {word_count} words"
                )

        # 6. All 4 boolean fields must be True
        bool_fields = {
            "logline_still_accurate": "Logline no longer matches the screenplay",
            "genre_clear": "Genre is unclear or genre promise is not delivered",
            "audience_defined": "Target audience is not clearly defined",
            "title_works": "Title does not effectively represent the story",
        }
        for field, failure_msg in bool_fields.items():
            value = artifact.get(field)
            if isinstance(value, bool) and not value:
                errors.append(f"MARKETING FAIL: {field} is False - {failure_msg}")

        # 7. issues list exists
        if "issues" not in artifact:
            errors.append("MISSING: issues field is required (use empty list if no issues)")
        elif not isinstance(artifact["issues"], list):
            errors.append(
                "TYPE ERROR: issues must be a list, "
                f"got {type(artifact['issues']).__name__}"
            )
        else:
            # 8. If issues is non-empty, each issue must be a non-empty string
            for i, issue in enumerate(artifact["issues"]):
                if not isinstance(issue, str):
                    errors.append(
                        f"TYPE ERROR: issues[{i}] must be a string, "
                        f"got {type(issue).__name__}"
                    )
                elif len(issue.strip()) == 0:
                    errors.append(f"EMPTY ISSUE: issues[{i}] is an empty string")

        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """
        Provide specific fix suggestions for each validation error.

        Args:
            errors: List of error strings from validate().

        Returns:
            List of fix suggestion strings, one per error.
        """
        suggestions: List[str] = []

        for error in errors:
            if "logline_still_accurate field is required" in error:
                suggestions.append(
                    "Add 'logline_still_accurate': true/false to indicate whether "
                    "the logline still describes the screenplay."
                )
            elif "genre_clear field is required" in error:
                suggestions.append(
                    "Add 'genre_clear': true/false to indicate whether "
                    "the genre is immediately identifiable."
                )
            elif "audience_defined field is required" in error:
                suggestions.append(
                    "Add 'audience_defined': true/false to indicate whether "
                    "the target audience is clear."
                )
            elif "title_works field is required" in error:
                suggestions.append(
                    "Add 'title_works': true/false to indicate whether "
                    "the title effectively represents the story."
                )
            elif "one_sheet_concept field is required" in error:
                suggestions.append(
                    "Add 'one_sheet_concept' with a 2-3 sentence movie poster "
                    "description including image and tagline."
                )
            elif "TOO SHORT: one_sheet_concept" in error:
                suggestions.append(
                    f"Expand one_sheet_concept to at least "
                    f"{self.MIN_ONE_SHEET_CHARS} characters. "
                    f"Describe the poster image and include a tagline."
                )
            elif "TOO FEW WORDS: one_sheet_concept" in error:
                suggestions.append(
                    f"Expand one_sheet_concept to at least "
                    f"{self.MIN_ONE_SHEET_WORDS} words. "
                    f"A good one-sheet describes a visual image AND a tagline."
                )
            elif "TYPE ERROR" in error:
                suggestions.append(
                    "Fix the field type to match the expected schema. "
                    "Boolean fields must be true/false, strings must be quoted, "
                    "issues must be a list of strings."
                )
            elif "MARKETING FAIL: logline_still_accurate" in error:
                suggestions.append(
                    "The screenplay has drifted from its logline. Revise scenes "
                    "to realign with the original promise, or update the logline "
                    "to match the actual story."
                )
            elif "MARKETING FAIL: genre_clear" in error:
                suggestions.append(
                    "Strengthen genre signals in the screenplay. Ensure the "
                    "genre's structural requirements and core promise are met "
                    "in every act."
                )
            elif "MARKETING FAIL: audience_defined" in error:
                suggestions.append(
                    "Clarify the target audience by adjusting tone, content "
                    "intensity, and thematic complexity to match a specific "
                    "demographic. Consider the 4 quadrants: Men Over/Under 25, "
                    "Women Over/Under 25."
                )
            elif "MARKETING FAIL: title_works" in error:
                suggestions.append(
                    "Revise the title to 'say what it is' while creating "
                    "intrigue. The title should evoke the irony or hook of "
                    "the story."
                )
            elif "issues field is required" in error:
                suggestions.append(
                    "Add 'issues': [] (empty list if no issues, or list of "
                    "strings describing marketing problems)."
                )
            elif "EMPTY ISSUE" in error:
                suggestions.append(
                    "Remove empty strings from the issues list or replace "
                    "them with meaningful issue descriptions."
                )
            else:
                suggestions.append(
                    "Review the marketing validation artifact structure and "
                    "ensure it matches the MarketingValidation schema."
                )

        return suggestions
