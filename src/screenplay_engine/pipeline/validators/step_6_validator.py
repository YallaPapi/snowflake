"""
Step 6 Validator: Immutable Laws (Save the Cat Ch.6)

v2.0.0 -- Validates that all 7 Immutable Laws of Screenplay Physics have been evaluated.
Checks performed:
  1. Artifact has "laws" list with exactly 7 entries
  2. Each law has law_number (1-7), law_name, passed (bool)
  3. Each failed law has non-empty violation_details
  4. Each failed law has non-empty fix_suggestion
  5. all_passed field exists and matches (all laws passed == True)
  6. All 7 canonical law names are present
  7. Semantic keyword check: failed laws' violation_details must reference
     the law's core concept (catches AI misapplications)
  8. Gate check: all laws must pass for step to succeed
"""

from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import LawResult


# Canonical law names in order — must match exactly
REQUIRED_LAW_NAMES = [
    "Save the Cat",
    "Pope in the Pool",
    "Double Mumbo Jumbo",
    "Black Vet",
    "Watch Out for That Glacier",
    "Covenant of the Arc",
    "Keep the Press Out",
]

# Semantic keywords per law — when a law FAILS, violation_details must
# reference at least one keyword from the corresponding set. This catches
# AI misapplications (e.g., claiming "Save the Cat" fails for exposition reasons).
LAW_SEMANTIC_KEYWORDS = {
    "Save the Cat": [
        "likab", "hero", "audience", "sync", "root", "endear", "cat", "action",
    ],
    "Pope in the Pool": [
        "expos", "bury", "entertain", "backstory", "info", "dump", "pope", "talk the plot",
    ],
    "Double Mumbo Jumbo": [
        "magic", "supernatur", "mumbo", "two", "both", "multiple", "one piece",
        "power", "fantasy", "sci-fi",
    ],
    "Black Vet": [
        "concept", "pile", "simple", "one idea", "too much", "overload", "stack",
        "vet", "marzipan",
    ],
    "Watch Out for That Glacier": [
        "danger", "imminent", "present", "personal", "escalat", "threat",
        "glacier", "slow", "distant", "stakes",
    ],
    "Covenant of the Arc": [
        "change", "arc", "transform", "grow", "static", "evolv", "journey",
        "covenant",
    ],
    "Keep the Press Out": [
        "press", "media", "news", "contain", "world", "fourth wall", "reality",
        "cnn", "report",
    ],
}


class Step6Validator:
    """Validator for Screenplay Engine Step 6: Immutable Laws"""

    VERSION = "2.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate an Immutable Laws evaluation artifact.

        Checks:
            1. Artifact has "laws" list with exactly 7 entries
            2. Each law has law_number (1-7), law_name, passed (bool)
            3. Each failed law has non-empty violation_details
            4. Each failed law has non-empty fix_suggestion
            5. Semantic keyword check: violation_details references the law's concept
            6. all_passed field exists and matches (all laws passed == True)
            7. All 7 canonical law names are present
            8. Gate check: all 7 laws must pass for step to succeed

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # ── 1. "laws" list with exactly 7 entries ──────────────────────────
        laws = artifact.get("laws")
        if laws is None:
            errors.append(
                "MISSING_LAWS: Artifact must contain a 'laws' list with exactly 7 entries."
            )
            return False, errors

        if not isinstance(laws, list):
            errors.append(
                "INVALID_LAWS_TYPE: 'laws' must be a list."
            )
            return False, errors

        if len(laws) != 7:
            errors.append(
                f"WRONG_LAW_COUNT: Expected exactly 7 laws, found {len(laws)}."
            )

        # ── 2 & 3 & 4. Per-law validation ─────────────────────────────────
        seen_numbers: set = set()
        seen_names: set = set()

        for idx, law in enumerate(laws):
            if not isinstance(law, dict):
                errors.append(
                    f"INVALID_LAW_ENTRY: Law at index {idx} must be a dict."
                )
                continue

            # law_number
            law_number = law.get("law_number")
            if law_number is None:
                errors.append(
                    f"MISSING_LAW_NUMBER: Law at index {idx} is missing 'law_number'."
                )
            elif not isinstance(law_number, int) or law_number < 1 or law_number > 7:
                errors.append(
                    f"INVALID_LAW_NUMBER: Law at index {idx} has invalid law_number={law_number}. "
                    f"Must be an integer 1-7."
                )
            else:
                if law_number in seen_numbers:
                    errors.append(
                        f"DUPLICATE_LAW_NUMBER: law_number={law_number} appears more than once."
                    )
                seen_numbers.add(law_number)

            # law_name
            law_name = law.get("law_name")
            if not law_name or not isinstance(law_name, str):
                errors.append(
                    f"MISSING_LAW_NAME: Law at index {idx} is missing 'law_name'."
                )
            else:
                seen_names.add(law_name)

            # passed (bool)
            passed = law.get("passed")
            if passed is None:
                errors.append(
                    f"MISSING_PASSED: Law at index {idx} ('{law_name or '?'}') is missing 'passed' field."
                )
            elif not isinstance(passed, bool):
                errors.append(
                    f"INVALID_PASSED_TYPE: Law at index {idx} ('{law_name or '?'}') 'passed' must be a boolean."
                )

            # For failed laws, require violation_details and fix_suggestion
            if isinstance(passed, bool) and not passed:
                violation_details = (law.get("violation_details") or "").strip()
                if not violation_details:
                    errors.append(
                        f"MISSING_VIOLATION_DETAILS: Law '{law_name or '?'}' (#{law_number or '?'}) "
                        f"failed but has no violation_details."
                    )
                elif law_name and law_name in LAW_SEMANTIC_KEYWORDS:
                    # Semantic relevance check — violation must reference the law's concept
                    violation_lower = violation_details.lower()
                    keywords = LAW_SEMANTIC_KEYWORDS[law_name]
                    if not any(kw in violation_lower for kw in keywords):
                        errors.append(
                            f"WEAK_VIOLATION_DETAILS: Law '{law_name}' (#{law_number}) "
                            f"violation_details does not appear to address the law's core concept."
                        )

                fix_suggestion = (law.get("fix_suggestion") or "").strip()
                if not fix_suggestion:
                    errors.append(
                        f"MISSING_FIX_SUGGESTION: Law '{law_name or '?'}' (#{law_number or '?'}) "
                        f"failed but has no fix_suggestion."
                    )

        # ── 5. all_passed field ────────────────────────────────────────────
        all_passed_field = artifact.get("all_passed")
        if all_passed_field is None:
            errors.append(
                "MISSING_ALL_PASSED: Artifact must contain an 'all_passed' boolean field."
            )
        else:
            # Compute expected value
            actual_all_passed = all(
                law.get("passed") is True
                for law in laws
                if isinstance(law, dict)
            )
            if all_passed_field != actual_all_passed:
                errors.append(
                    f"ALL_PASSED_MISMATCH: 'all_passed' is {all_passed_field} "
                    f"but computed value is {actual_all_passed}."
                )

        # ── 6. All 7 canonical law names present ──────────────────────────
        missing_names = set(REQUIRED_LAW_NAMES) - seen_names
        if missing_names:
            errors.append(
                f"MISSING_LAW_NAMES: The following required law names are missing: "
                f"{sorted(missing_names)}"
            )

        # ── Gate check: all laws must pass ─────────────────────────────────
        failed_laws = []
        for law in laws:
            if isinstance(law, dict) and law.get("passed") is False:
                name = law.get("law_name", "Unknown")
                details = law.get("violation_details", "No details provided")
                failed_laws.append(f"Law '{name}': {details}")

        if failed_laws:
            for violation in failed_laws:
                errors.append(f"LAW_VIOLATION: {violation}")

        return len(errors) == 0, errors

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
            if "MISSING_LAWS" in error:
                suggestions.append(
                    "Add a 'laws' key containing a list of exactly 7 law evaluation objects."
                )
            elif "INVALID_LAWS_TYPE" in error:
                suggestions.append(
                    "Ensure 'laws' is a JSON array (list), not a string or object."
                )
            elif "WRONG_LAW_COUNT" in error:
                suggestions.append(
                    "Ensure the 'laws' list has exactly 7 entries, one for each Immutable Law."
                )
            elif "INVALID_LAW_ENTRY" in error:
                suggestions.append(
                    "Each entry in 'laws' must be a JSON object with keys: "
                    "law_number, law_name, passed, violation_details, fix_suggestion."
                )
            elif "MISSING_LAW_NUMBER" in error:
                suggestions.append(
                    "Add 'law_number' (integer 1-7) to the law entry."
                )
            elif "INVALID_LAW_NUMBER" in error:
                suggestions.append(
                    "Correct 'law_number' to be an integer between 1 and 7 inclusive."
                )
            elif "DUPLICATE_LAW_NUMBER" in error:
                suggestions.append(
                    "Each law_number must appear exactly once. Remove the duplicate."
                )
            elif "MISSING_LAW_NAME" in error:
                suggestions.append(
                    "Add 'law_name' with the canonical name: one of "
                    "'Save the Cat', 'Pope in the Pool', 'Double Mumbo Jumbo', "
                    "'Black Vet', 'Watch Out for That Glacier', "
                    "'Covenant of the Arc', 'Keep the Press Out'."
                )
            elif "MISSING_PASSED" in error:
                suggestions.append(
                    "Add 'passed' boolean (true/false) indicating whether the law is satisfied."
                )
            elif "INVALID_PASSED_TYPE" in error:
                suggestions.append(
                    "Change 'passed' to a boolean value (true or false), not a string."
                )
            elif "MISSING_VIOLATION_DETAILS" in error:
                suggestions.append(
                    "When a law fails (passed=false), 'violation_details' must be a non-empty "
                    "string explaining what specifically violates the law."
                )
            elif "MISSING_FIX_SUGGESTION" in error:
                suggestions.append(
                    "When a law fails (passed=false), 'fix_suggestion' must be a non-empty "
                    "string explaining how to fix the violation."
                )
            elif "MISSING_ALL_PASSED" in error:
                suggestions.append(
                    "Add 'all_passed' boolean field. Set to true only if every law passed."
                )
            elif "ALL_PASSED_MISMATCH" in error:
                suggestions.append(
                    "Recalculate 'all_passed': it must be true only when ALL 7 laws have passed=true."
                )
            elif "MISSING_LAW_NAMES" in error:
                suggestions.append(
                    "Ensure all 7 law names are present with exact spelling: "
                    "'Save the Cat', 'Pope in the Pool', 'Double Mumbo Jumbo', "
                    "'Black Vet', 'Watch Out for That Glacier', "
                    "'Covenant of the Arc', 'Keep the Press Out'."
                )
            elif "WEAK_VIOLATION_DETAILS" in error:
                suggestions.append(
                    "The violation_details for this law does not seem to address the law's "
                    "core concept. Rewrite violation_details to specifically explain how "
                    "the law is violated using terms relevant to that law."
                )
            elif "LAW_VIOLATION" in error:
                suggestions.append(
                    "Fix the Board/Beat Sheet to satisfy the indicated law. "
                    "Review the fix_suggestion in the law evaluation for specific guidance."
                )
            else:
                suggestions.append("Review and fix the indicated issue.")

        return suggestions
