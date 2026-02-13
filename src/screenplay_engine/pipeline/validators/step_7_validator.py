"""
Step 7 Validator: Diagnostic Checks (Save the Cat Ch.7)

v4.0.0 -- Observational diagnostics. No pass/fail. Validates that all 9
diagnostic checks were executed with correct structure.
Checks performed:
  1. Artifact has "diagnostics" list with exactly 9 entries
  2. Each diagnostic has check_number (1-9), check_name, observations (non-empty string)
  3. Semantic keyword check: observations must reference the check's core concept
  4. rough_spots is a list (can be empty). If non-empty, each entry has scene (int) and issue (non-empty str)
  5. rewrite_suggestions is a dict (can be empty). If rough_spots is non-empty, rewrite_suggestions
     should have entries for each rough_spot scene
  6. Check 5 (Emotional Color Wheel) must have emotion_map (dict of emotion_name -> list of scene ints)
  7. All 9 canonical check names are present
  8. total_checks field exists and equals 9

Step 7 validation succeeds as long as all 9 checks were RUN with proper structure.
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

# Semantic keywords per check — observations must reference at least one keyword
# from the corresponding set. Catches AI misapplications.
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

    VERSION = "4.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a Step 7 diagnostics artifact.

        Checks:
            1. Artifact has "diagnostics" list with exactly 9 entries
            2. Each diagnostic has check_number (1-9), check_name, observations (non-empty)
            3. Semantic keyword check on observations
            4. rough_spots is a list; if non-empty, entries have scene (int) and issue (str)
            5. rewrite_suggestions is a dict; if rough_spots non-empty, must have entries
            6. Check 5 must have emotion_map
            7. All 9 check names present
            8. total_checks field equals 9

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

        # -- 2. Each diagnostic has check_number, check_name, observations --
        seen_numbers: set = set()
        seen_names: set = set()

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

            # -- 3. observations (non-empty string) -------------------------
            observations = (diag.get("observations") or "").strip()
            if not observations:
                errors.append(
                    f"{prefix}_MISSING_OBSERVATIONS: 'observations' field is required "
                    f"and must be a non-empty string describing what the screenplay does "
                    f"for check '{check_name or check_number}'."
                )

            # -- 4. Semantic keyword check on observations ------------------
            if observations and check_name and check_name in CHECK_SEMANTIC_KEYWORDS:
                obs_lower = observations.lower()
                keywords = CHECK_SEMANTIC_KEYWORDS[check_name]
                if not any(kw in obs_lower for kw in keywords):
                    errors.append(
                        f"{prefix}_WEAK_OBSERVATIONS: Check '{check_name}' "
                        f"(#{check_number}) observations does not appear to "
                        f"address the check's core concept."
                    )

            # -- 5. rough_spots is a list -----------------------------------
            rough_spots = diag.get("rough_spots")
            if rough_spots is None:
                errors.append(
                    f"{prefix}_MISSING_ROUGH_SPOTS: 'rough_spots' field is required "
                    f"(can be empty list [] for clean checks)."
                )
            elif not isinstance(rough_spots, list):
                errors.append(
                    f"{prefix}_INVALID_ROUGH_SPOTS: 'rough_spots' must be a list, "
                    f"got {type(rough_spots).__name__}."
                )
            else:
                # Validate each rough spot entry
                for j, spot in enumerate(rough_spots):
                    spot_prefix = f"{prefix}_ROUGH_SPOT_{j + 1}"
                    if not isinstance(spot, dict):
                        errors.append(
                            f"{spot_prefix}_INVALID_TYPE: Each rough_spot must be a dict."
                        )
                        continue
                    scene = spot.get("scene")
                    if scene is None or not isinstance(scene, int):
                        errors.append(
                            f"{spot_prefix}_MISSING_SCENE: Each rough_spot must have "
                            f"a 'scene' field (integer)."
                        )
                    issue = (spot.get("issue") or "").strip()
                    if not issue:
                        errors.append(
                            f"{spot_prefix}_MISSING_ISSUE: Each rough_spot must have "
                            f"a non-empty 'issue' field."
                        )

            # -- 6. rewrite_suggestions is a dict ---------------------------
            rewrite_suggestions = diag.get("rewrite_suggestions")
            if rewrite_suggestions is None:
                errors.append(
                    f"{prefix}_MISSING_REWRITE_SUGGESTIONS: 'rewrite_suggestions' field "
                    f"is required (can be empty dict {{}} for clean checks)."
                )
            elif not isinstance(rewrite_suggestions, dict):
                errors.append(
                    f"{prefix}_INVALID_REWRITE_SUGGESTIONS: 'rewrite_suggestions' must "
                    f"be a dict, got {type(rewrite_suggestions).__name__}."
                )
            elif isinstance(rough_spots, list) and len(rough_spots) > 0:
                # If there are rough spots, rewrite_suggestions should cover them
                if len(rewrite_suggestions) == 0:
                    errors.append(
                        f"{prefix}_EMPTY_REWRITE_SUGGESTIONS: Check has {len(rough_spots)} "
                        f"rough spot(s) but rewrite_suggestions is empty. Provide a "
                        f"rewrite suggestion for each rough spot scene."
                    )
                else:
                    # Check that rough_spot scenes have corresponding rewrite entries
                    rewrite_keys = set(str(k) for k in rewrite_suggestions.keys())
                    spot_scenes = set()
                    if isinstance(rough_spots, list):
                        for spot in rough_spots:
                            if isinstance(spot, dict) and isinstance(spot.get("scene"), int):
                                spot_scenes.add(str(spot["scene"]))
                    missing = spot_scenes - rewrite_keys
                    if missing:
                        errors.append(
                            f"{prefix}_INCOMPLETE_REWRITE_SUGGESTIONS: "
                            f"'rewrite_suggestions' is missing entries for scene(s): "
                            f"{', '.join(sorted(missing))}. Every rough_spot scene "
                            f"should have a rewrite suggestion."
                        )

            # -- 7. Check 5 must have emotion_map ---------------------------
            if check_number == 5:
                emotion_map = diag.get("emotion_map")
                if emotion_map is None:
                    errors.append(
                        f"{prefix}_MISSING_EMOTION_MAP: Check 5 (Emotional Color Wheel) "
                        f"MUST include an 'emotion_map' dict mapping emotion names to "
                        f"lists of scene numbers."
                    )
                elif not isinstance(emotion_map, dict):
                    errors.append(
                        f"{prefix}_INVALID_EMOTION_MAP: 'emotion_map' must be a dict, "
                        f"got {type(emotion_map).__name__}."
                    )

        # -- 8. total_checks field exists and equals 9 ---------------------
        total_checks = artifact.get("total_checks")
        if total_checks is None:
            errors.append(
                "MISSING_TOTAL_CHECKS: 'total_checks' field is required and must be 9."
            )
        elif total_checks != 9:
            errors.append(
                f"WRONG_TOTAL_CHECKS: 'total_checks' must be 9, got {total_checks}."
            )

        # -- 9. All 9 check names are present ------------------------------
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
                    "check_number, check_name, observations, rough_spots, rewrite_suggestions."
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
            elif "MISSING_OBSERVATIONS" in error:
                suggestions.append(
                    "Add a non-empty 'observations' string describing what the screenplay "
                    "does for this check. Observations are required for every check."
                )
            elif "WEAK_OBSERVATIONS" in error:
                suggestions.append(
                    "The observations for this check does not seem to address the check's "
                    "core concept. Rewrite observations to specifically describe how "
                    "the screenplay relates to this diagnostic lens."
                )
            elif "MISSING_ROUGH_SPOTS" in error:
                suggestions.append(
                    "Add a 'rough_spots' field — a list of objects with scene (int), "
                    "issue (str), and current_text (str). Use empty list [] for clean checks."
                )
            elif "INVALID_ROUGH_SPOTS" in error:
                suggestions.append(
                    "Set 'rough_spots' to a JSON array (list), not a string or object."
                )
            elif "MISSING_SCENE" in error:
                suggestions.append(
                    "Each rough_spot must have a 'scene' field with an integer scene number."
                )
            elif "MISSING_ISSUE" in error:
                suggestions.append(
                    "Each rough_spot must have a non-empty 'issue' field describing the problem."
                )
            elif "MISSING_REWRITE_SUGGESTIONS" in error:
                suggestions.append(
                    "Add a 'rewrite_suggestions' field — a dict mapping scene numbers (as strings) "
                    "to concrete rewrite instructions. Use empty dict {} for clean checks."
                )
            elif "INVALID_REWRITE_SUGGESTIONS" in error:
                suggestions.append(
                    "Set 'rewrite_suggestions' to a JSON object (dict), not a list or string."
                )
            elif "EMPTY_REWRITE_SUGGESTIONS" in error:
                suggestions.append(
                    "When rough_spots are present, provide rewrite_suggestions for each "
                    "rough spot scene. Format: 'CURRENT: [quote]. REPLACE WITH: [new text]. "
                    "FIXES: [what this changes].'."
                )
            elif "INCOMPLETE_REWRITE_SUGGESTIONS" in error:
                suggestions.append(
                    "Every scene in rough_spots must have a corresponding entry in "
                    "rewrite_suggestions with concrete rewrite instructions."
                )
            elif "MISSING_EMOTION_MAP" in error:
                suggestions.append(
                    "Check 5 (Emotional Color Wheel) must include an 'emotion_map' dict "
                    "mapping each emotion name to a list of scene numbers where it appears."
                )
            elif "INVALID_EMOTION_MAP" in error:
                suggestions.append(
                    "Set 'emotion_map' to a JSON object (dict) mapping emotion names to "
                    "lists of integers."
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
