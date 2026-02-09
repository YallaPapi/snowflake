"""
Step 7 Validator: Diagnostic Checks (Save the Cat Ch.7)

v2.0.0 -- Validates that all 9 diagnostic checks were executed and structured correctly.
Checks performed:
  1. Artifact has "diagnostics" list with exactly 9 entries
  2. Each diagnostic has check_number (1-9), check_name, passed (bool)
  3. Each failed diagnostic has non-empty problem_details
  4. Each failed diagnostic has non-empty fix_suggestion
  5. Semantic keyword check: failed diagnostics' problem_details must reference
     the check's core concept (catches AI misapplications)
  6. checks_passed_count field exists and matches actual count
  7. total_checks field exists and equals 9
  8. All 9 canonical check names are present

Step 7 validation succeeds as long as all 9 checks were RUN (not necessarily
all passed). The diagnostic results inform the user what to fix.
"""

from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import DiagnosticResult


# Canonical check names that must appear in the diagnostics
REQUIRED_CHECK_NAMES = [
    "The Hero Leads",
    "Talking the Plot",
    "Make the Bad Guy Badder",
    "Turn Turn Turn",
    "Emotional Color Wheel",
    "Hi How Are You I'm Fine",
    "Take a Step Back",
    "Limp and Eye Patch",
    "Is It Primal",
]

# Semantic keywords per check — when a check FAILS, problem_details must
# reference at least one keyword from the corresponding set. Catches AI
# misapplications (e.g., claiming "The Hero Leads" fails for dialogue reasons).
CHECK_SEMANTIC_KEYWORDS = {
    "The Hero Leads": [
        "proactiv", "hero", "passive", "reactive", "goal", "lead", "drag",
        "question mark", "direct", "motiv",
    ],
    "Talking the Plot": [
        "expos", "dialogue", "tell", "show", "talk", "plot", "visual",
        "backstory", "info", "unnatural",
    ],
    "Make the Bad Guy Badder": [
        "antag", "villain", "bad guy", "mirror", "match", "power",
        "threat", "weak", "stronger", "badder",
    ],
    "Turn Turn Turn": [
        "acceler", "pace", "escal", "complica", "intensi", "midpoint",
        "flat", "stakes", "speed", "reveal",
    ],
    "Emotional Color Wheel": [
        "emotion", "monotone", "one-note", "palette", "color", "feel",
        "lust", "fear", "joy", "anger", "tone",
    ],
    "Hi How Are You I'm Fine": [
        "dialogue", "voice", "speak", "talk", "same", "distinguish",
        "interchang", "flat", "character", "tic",
    ],
    "Take a Step Back": [
        "arc", "start", "back", "grow", "change", "transform", "journey",
        "begin", "far", "bow",
    ],
    "Limp and Eye Patch": [
        "trait", "distinct", "memor", "visual", "limp", "eye", "patch",
        "forget", "generic", "recogni",
    ],
    "Is It Primal": [
        "primal", "caveman", "surviv", "hunger", "sex", "protect", "fear",
        "death", "biolog", "basic", "drive",
    ],
}


class Step7Validator:
    """Validator for Screenplay Engine Step 7: 9 Diagnostic Checks (Save the Cat Ch.7)"""

    VERSION = "2.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a Step 7 diagnostics artifact.

        Checks:
            1. Artifact has "diagnostics" list with exactly 9 entries
            2. Each diagnostic has check_number (1-9), check_name, passed (bool)
            3. Each failed diagnostic has non-empty problem_details
            4. Each failed diagnostic has non-empty fix_suggestion
            5. checks_passed_count field exists and matches actual count
            6. All 9 check names are present

        Step 7 validation succeeds as long as all 9 checks were RUN
        (not necessarily all passed). The diagnostic results inform the
        user what to fix.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # -- 1. Artifact has "diagnostics" list with exactly 9 entries ------
        diagnostics = artifact.get("diagnostics")
        if diagnostics is None:
            errors.append(
                "MISSING_DIAGNOSTICS: Artifact must contain a 'diagnostics' list "
                "with exactly 9 diagnostic check entries."
            )
            return False, errors

        if not isinstance(diagnostics, list):
            errors.append(
                "INVALID_DIAGNOSTICS_TYPE: 'diagnostics' must be a list, "
                f"got {type(diagnostics).__name__}."
            )
            return False, errors

        if len(diagnostics) != 9:
            errors.append(
                f"WRONG_DIAGNOSTIC_COUNT: Expected exactly 9 diagnostic entries, "
                f"found {len(diagnostics)}. All 9 checks must be run."
            )

        # -- 2. Each diagnostic has check_number (1-9), check_name, passed --
        seen_numbers: set = set()
        seen_names: set = set()
        actual_passed_count = 0

        for i, diag in enumerate(diagnostics):
            prefix = f"DIAGNOSTIC_{i + 1}"

            if not isinstance(diag, dict):
                errors.append(
                    f"{prefix}_INVALID_TYPE: Each diagnostic entry must be a dict, "
                    f"got {type(diag).__name__}."
                )
                continue

            # check_number
            check_number = diag.get("check_number")
            if check_number is None:
                errors.append(
                    f"{prefix}_MISSING_CHECK_NUMBER: 'check_number' field is required."
                )
            elif not isinstance(check_number, int) or check_number < 1 or check_number > 9:
                errors.append(
                    f"{prefix}_INVALID_CHECK_NUMBER: 'check_number' must be an integer "
                    f"from 1 to 9, got {check_number!r}."
                )
            else:
                if check_number in seen_numbers:
                    errors.append(
                        f"{prefix}_DUPLICATE_CHECK_NUMBER: check_number {check_number} "
                        f"appears more than once."
                    )
                seen_numbers.add(check_number)

            # check_name
            check_name = diag.get("check_name")
            if not check_name or not isinstance(check_name, str):
                errors.append(
                    f"{prefix}_MISSING_CHECK_NAME: 'check_name' field is required "
                    f"and must be a non-empty string."
                )
            else:
                seen_names.add(check_name)

            # passed (bool)
            passed = diag.get("passed")
            if passed is None:
                errors.append(
                    f"{prefix}_MISSING_PASSED: 'passed' field is required and must be a boolean."
                )
            elif not isinstance(passed, bool):
                errors.append(
                    f"{prefix}_INVALID_PASSED: 'passed' must be a boolean, "
                    f"got {type(passed).__name__}."
                )
            else:
                if passed:
                    actual_passed_count += 1

                # -- 3 & 4. Failed checks need problem_details and fix_suggestion
                if not passed:
                    problem_details = (diag.get("problem_details") or "").strip()
                    if not problem_details:
                        errors.append(
                            f"{prefix}_MISSING_PROBLEM_DETAILS: Failed diagnostic "
                            f"(check_number={check_number}) must have non-empty "
                            f"'problem_details' describing the specific issue."
                        )

                    # -- 5. Semantic keyword check for failed diagnostics
                    if problem_details and check_name and check_name in CHECK_SEMANTIC_KEYWORDS:
                        details_lower = problem_details.lower()
                        keywords = CHECK_SEMANTIC_KEYWORDS[check_name]
                        if not any(kw in details_lower for kw in keywords):
                            errors.append(
                                f"{prefix}_WEAK_PROBLEM_DETAILS: Check '{check_name}' "
                                f"(#{check_number}) problem_details does not appear to "
                                f"address the check's core concept."
                            )

                    fix_suggestion = (diag.get("fix_suggestion") or "").strip()
                    if not fix_suggestion:
                        errors.append(
                            f"{prefix}_MISSING_FIX_SUGGESTION: Failed diagnostic "
                            f"(check_number={check_number}) must have non-empty "
                            f"'fix_suggestion' describing how to fix the issue."
                        )

        # -- 6. checks_passed_count exists and matches actual count ---------
        checks_passed_count = artifact.get("checks_passed_count")
        if checks_passed_count is None:
            errors.append(
                "MISSING_CHECKS_PASSED_COUNT: 'checks_passed_count' field is required."
            )
        elif not isinstance(checks_passed_count, int):
            errors.append(
                f"INVALID_CHECKS_PASSED_COUNT: 'checks_passed_count' must be an integer, "
                f"got {type(checks_passed_count).__name__}."
            )
        elif checks_passed_count != actual_passed_count:
            errors.append(
                f"MISMATCHED_CHECKS_PASSED_COUNT: 'checks_passed_count' is "
                f"{checks_passed_count} but actual passed count is {actual_passed_count}."
            )

        # -- 7. total_checks field exists and equals 9 ---------------------
        total_checks = artifact.get("total_checks")
        if total_checks is None:
            errors.append(
                "MISSING_TOTAL_CHECKS: 'total_checks' field is required and must be 9."
            )
        elif total_checks != 9:
            errors.append(
                f"WRONG_TOTAL_CHECKS: 'total_checks' must be 9, got {total_checks}."
            )

        # -- 8. All 9 check names are present ------------------------------
        missing_names = []
        for required_name in REQUIRED_CHECK_NAMES:
            if required_name not in seen_names:
                missing_names.append(required_name)

        if missing_names:
            errors.append(
                f"MISSING_CHECK_NAMES: The following required check names are missing: "
                f"{', '.join(missing_names)}. All 9 diagnostic checks must be present "
                f"with their exact canonical names."
            )

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
            if "MISSING_DIAGNOSTICS" in error:
                suggestions.append(
                    "Add a 'diagnostics' key containing a list of 9 diagnostic check objects."
                )
            elif "INVALID_DIAGNOSTICS_TYPE" in error:
                suggestions.append(
                    "Ensure 'diagnostics' is a JSON array (list), not a string or object."
                )
            elif "WRONG_DIAGNOSTIC_COUNT" in error:
                suggestions.append(
                    "Include exactly 9 diagnostic entries, one for each check: "
                    "The Hero Leads, Talking the Plot, Make the Bad Guy Badder, "
                    "Turn Turn Turn, Emotional Color Wheel, Hi How Are You I'm Fine, "
                    "Take a Step Back, Limp and Eye Patch, Is It Primal."
                )
            elif "INVALID_TYPE" in error:
                suggestions.append(
                    "Each diagnostic entry must be a JSON object with keys: "
                    "check_number, check_name, passed, problem_details, fix_suggestion."
                )
            elif "MISSING_CHECK_NUMBER" in error:
                suggestions.append(
                    "Add a 'check_number' integer field (1-9) to the diagnostic entry."
                )
            elif "INVALID_CHECK_NUMBER" in error:
                suggestions.append(
                    "Set 'check_number' to an integer between 1 and 9 inclusive."
                )
            elif "DUPLICATE_CHECK_NUMBER" in error:
                suggestions.append(
                    "Each check_number must appear exactly once. Remove duplicates "
                    "and ensure all 9 checks (1-9) are represented."
                )
            elif "MISSING_CHECK_NAME" in error:
                suggestions.append(
                    "Add a 'check_name' string field matching one of the 9 canonical names."
                )
            elif "MISSING_PASSED" in error:
                suggestions.append(
                    "Add a 'passed' boolean field (true or false) to the diagnostic entry."
                )
            elif "INVALID_PASSED" in error:
                suggestions.append(
                    "Set 'passed' to a boolean value (true or false), not a string."
                )
            elif "MISSING_PROBLEM_DETAILS" in error:
                suggestions.append(
                    "Failed diagnostics (passed=false) must include 'problem_details' "
                    "with a specific description of what is wrong."
                )
            elif "MISSING_FIX_SUGGESTION" in error:
                suggestions.append(
                    "Failed diagnostics (passed=false) must include 'fix_suggestion' "
                    "with a specific, actionable recommendation to fix the problem."
                )
            elif "MISSING_CHECKS_PASSED_COUNT" in error:
                suggestions.append(
                    "Add a 'checks_passed_count' integer field at the top level "
                    "equal to the number of diagnostics where passed is true."
                )
            elif "INVALID_CHECKS_PASSED_COUNT" in error:
                suggestions.append(
                    "Set 'checks_passed_count' to an integer, not a string or other type."
                )
            elif "MISMATCHED_CHECKS_PASSED_COUNT" in error:
                suggestions.append(
                    "Update 'checks_passed_count' to match the actual number of "
                    "diagnostics where passed is true."
                )
            elif "WEAK_PROBLEM_DETAILS" in error:
                suggestions.append(
                    "The problem_details for this check does not seem to address the check's "
                    "core concept. Rewrite problem_details to specifically explain how "
                    "the screenplay fails this particular diagnostic."
                )
            elif "MISSING_TOTAL_CHECKS" in error:
                suggestions.append(
                    "Add a 'total_checks' integer field at the top level, set to 9."
                )
            elif "WRONG_TOTAL_CHECKS" in error:
                suggestions.append(
                    "Set 'total_checks' to 9 (there are always exactly 9 diagnostic checks)."
                )
            elif "MISSING_CHECK_NAMES" in error:
                suggestions.append(
                    "Ensure all 9 check names are present with exact canonical names: "
                    "The Hero Leads, Talking the Plot, Make the Bad Guy Badder, "
                    "Turn Turn Turn, Emotional Color Wheel, Hi How Are You I'm Fine, "
                    "Take a Step Back, Limp and Eye Patch, Is It Primal."
                )
            else:
                suggestions.append("Review and fix the indicated issue.")

        return suggestions
