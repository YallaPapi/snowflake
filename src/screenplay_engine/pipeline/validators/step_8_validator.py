"""
Step 8 Validator: Screenplay Writing (Save the Cat end of Ch.5)

v2.0.0 -- Validates screenplay scenes follow proper industry format and Save the Cat
principles. Each scene is a "mini-movie" with beginning, middle, end, emotional change,
and conflict. Scenes must be rich (5+ elements) with sustained dialogue.

Checks performed:
  1.  Screenplay has title and logline
  2.  Scenes list exists and has at least 30 scenes
  3.  Every scene has a valid slugline starting with INT./EXT./INT/EXT.
  4.  Every scene has at least 3 elements
  5.  Every scene has estimated_duration_seconds > 0
  6.  Every scene has non-empty conflict field
  7.  Every scene has emotional_start and emotional_end ("+" or "-")
  8.  No scene contains internal monologue markers
  9.  Total estimated_duration_seconds is at least 2400 (40 minutes minimum)
  10. total_pages field exists and is > 0
  11. At least 50% of scenes have dialogue elements
  12. Average elements per scene is at least 5
"""

import re
from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import ScreenplayScene, ScreenplayElement, Screenplay

# Internal monologue markers that should never appear in screenplay action lines.
# These are multi-word phrases that describe unfilmable internal states.
# Single words like "thinks" are too aggressive — "She thinks for a beat" is visible.
INTERNAL_MONOLOGUE_MARKERS = [
    "thinks to himself",
    "thinks to herself",
    "thinks to themselves",
    "thinks about",
    "feels inside",
    "internally",
    "in her mind",
    "in his mind",
    "in their mind",
    "in her head",
    "in his head",
    "in their head",
    "wonders to himself",
    "wonders to herself",
]

# Valid slugline prefixes
VALID_SLUGLINE_PREFIXES = ("INT.", "EXT.", "INT/EXT.")

# Valid element types
VALID_ELEMENT_TYPES = {
    "slugline", "action", "character", "dialogue",
    "parenthetical", "transition",
}

# Valid emotional polarity values
VALID_POLARITIES = {"+", "-"}


class Step8Validator:
    """Validator for Screenplay Engine Step 8: Screenplay Writing (Save the Cat end of Ch.5)"""

    VERSION = "2.0.0"

    # Minimum scene count — 40 board cards should produce at least 30 scenes
    MIN_SCENES = 30

    # Minimum elements per scene — a real scene needs at least 3 elements
    MIN_ELEMENTS_PER_SCENE = 3

    # Minimum average elements across all scenes — ensures overall density
    MIN_AVG_ELEMENTS = 5

    # Minimum total duration in seconds (40 minutes — lenient floor)
    MIN_TOTAL_DURATION = 2400

    # Minimum dialogue ratio — at least 50% of scenes should have dialogue
    MIN_DIALOGUE_RATIO = 0.5

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a screenplay artifact.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # -- 1. Screenplay has title and logline --------------------------------
        title = (artifact.get("title") or "").strip()
        if not title:
            errors.append(
                "MISSING_TITLE: Screenplay must have a non-empty title field"
            )

        logline = (artifact.get("logline") or "").strip()
        if not logline:
            errors.append(
                "MISSING_LOGLINE: Screenplay must have a non-empty logline field"
            )

        # -- 2. Scenes list exists and has at least MIN_SCENES scenes -----------
        scenes = artifact.get("scenes")
        if not isinstance(scenes, list):
            errors.append(
                "MISSING_SCENES: Screenplay must contain a 'scenes' array"
            )
            # Cannot continue scene-level checks without a list
            return False, errors

        if len(scenes) < self.MIN_SCENES:
            errors.append(
                f"TOO_FEW_SCENES: Screenplay must have at least {self.MIN_SCENES} scenes "
                f"(found {len(scenes)}). Each board card should expand into a full scene."
            )

        # Per-scene validation
        total_duration = 0
        total_elements = 0
        scenes_with_dialogue = 0

        for idx, scene in enumerate(scenes):
            scene_label = f"Scene {idx + 1}"

            # -- 3. Valid slugline -----------------------------------------------
            slugline = (scene.get("slugline") or "").strip()
            if not slugline:
                errors.append(
                    f"MISSING_SLUGLINE [{scene_label}]: Every scene must have a slugline"
                )
            else:
                slugline_upper = slugline.upper()
                if not any(slugline_upper.startswith(prefix) for prefix in VALID_SLUGLINE_PREFIXES):
                    errors.append(
                        f"INVALID_SLUGLINE [{scene_label}]: Slugline must start with "
                        f"INT., EXT., or INT/EXT. (got: '{slugline}')"
                    )

            # -- 4. At least MIN_ELEMENTS_PER_SCENE elements --------------------
            elements = scene.get("elements", [])
            elem_count = len(elements) if isinstance(elements, list) else 0
            total_elements += elem_count

            if elem_count < self.MIN_ELEMENTS_PER_SCENE:
                errors.append(
                    f"TOO_FEW_ELEMENTS [{scene_label}]: Every scene needs at least "
                    f"{self.MIN_ELEMENTS_PER_SCENE} elements (found {elem_count}). "
                    f"A scene is a mini-movie: slugline, action, dialogue, exit."
                )

            # Check for dialogue in this scene
            has_dialogue = False
            if isinstance(elements, list):
                for element in elements:
                    etype = (element.get("element_type") or "").strip()
                    if etype == "dialogue":
                        has_dialogue = True
                        break
            if has_dialogue:
                scenes_with_dialogue += 1

            # -- 5. estimated_duration_seconds > 0 ------------------------------
            duration = scene.get("estimated_duration_seconds", 0)
            if not isinstance(duration, (int, float)) or duration <= 0:
                errors.append(
                    f"INVALID_DURATION [{scene_label}]: estimated_duration_seconds "
                    f"must be > 0 (got: {duration})"
                )
            else:
                total_duration += duration

            # -- 6. Non-empty conflict field ------------------------------------
            raw_conflict = scene.get("conflict") or ""
            conflict = str(raw_conflict).strip() if raw_conflict else ""
            if not conflict:
                errors.append(
                    f"MISSING_CONFLICT [{scene_label}]: Every scene must have a "
                    f"non-empty conflict field describing who wants what from whom"
                )

            # -- 7. Emotional start and end are "+" or "-" ----------------------
            # Support both new (emotional_start/emotional_end) and legacy (emotional_polarity)
            e_start = (scene.get("emotional_start") or "").strip()
            e_end = (scene.get("emotional_end") or "").strip()

            # Fallback to emotional_polarity for backward compatibility
            if not e_start and not e_end:
                legacy = (scene.get("emotional_polarity") or "").strip()
                if legacy in VALID_POLARITIES:
                    e_start = legacy
                    e_end = legacy

            if e_start not in VALID_POLARITIES:
                errors.append(
                    f"INVALID_EMOTIONAL_START [{scene_label}]: emotional_start must be "
                    f"'+' or '-' (got: '{e_start}')"
                )
            if e_end not in VALID_POLARITIES:
                errors.append(
                    f"INVALID_EMOTIONAL_END [{scene_label}]: emotional_end must be "
                    f"'+' or '-' (got: '{e_end}')"
                )

            # -- 8. No internal monologue markers --------------------------------
            # Only check ACTION elements — dialogue is spoken aloud, characters can
            # say "thinks", "feels" etc. when talking about others. Internal monologue
            # markers are only invalid in action lines (unfilmable internal states).
            if isinstance(elements, list):
                for elem_idx, element in enumerate(elements):
                    content = (element.get("content") or "").lower()
                    etype = (element.get("element_type") or "").strip()
                    if etype == "action":
                        for marker in INTERNAL_MONOLOGUE_MARKERS:
                            if marker in content:
                                errors.append(
                                    f"INTERNAL_MONOLOGUE [{scene_label}, element {elem_idx + 1}]: "
                                    f"Found internal monologue marker '{marker}' in {etype} element. "
                                    f"Screenplays show only what camera sees and microphone hears."
                                )

        # -- 9. Total duration at least MIN_TOTAL_DURATION ----------------------
        if total_duration < self.MIN_TOTAL_DURATION:
            errors.append(
                f"DURATION_TOO_SHORT: Total estimated duration is {total_duration}s. "
                f"Minimum is {self.MIN_TOTAL_DURATION} seconds ({self.MIN_TOTAL_DURATION // 60} minutes)."
            )

        # -- 10. total_pages field exists and > 0 -------------------------------
        total_pages = artifact.get("total_pages")
        if total_pages is None:
            errors.append(
                "MISSING_TOTAL_PAGES: Screenplay must have a 'total_pages' field"
            )
        elif not isinstance(total_pages, (int, float)) or total_pages <= 0:
            errors.append(
                f"INVALID_TOTAL_PAGES: total_pages must be > 0 (got: {total_pages})"
            )

        # -- 11. At least MIN_DIALOGUE_RATIO of scenes have dialogue ------------
        if len(scenes) > 0:
            dialogue_ratio = scenes_with_dialogue / len(scenes)
            if dialogue_ratio < self.MIN_DIALOGUE_RATIO:
                errors.append(
                    f"INSUFFICIENT_DIALOGUE: At least {self.MIN_DIALOGUE_RATIO:.0%} of scenes must have "
                    f"dialogue elements. Only {scenes_with_dialogue}/{len(scenes)} "
                    f"scenes ({dialogue_ratio:.0%}) have dialogue."
                )

        # -- 12. Average elements per scene >= MIN_AVG_ELEMENTS -----------------
        if len(scenes) > 0:
            avg_elements = total_elements / len(scenes)
            if avg_elements < self.MIN_AVG_ELEMENTS:
                errors.append(
                    f"LOW_SCENE_DENSITY: Average elements per scene is {avg_elements:.1f}, "
                    f"minimum is {self.MIN_AVG_ELEMENTS}. Scenes need richer content: "
                    f"action, dialogue exchanges, visual details."
                )

        return len(errors) == 0, errors

    def validate_scene(self, scene: Dict[str, Any], scene_index: int = 0) -> Tuple[bool, List[str]]:
        """
        Validate a SINGLE screenplay scene (structural format checks only).

        Runs checks 3-8 from the full validate() method on one scene.
        Used by scene-by-scene generation to validate each scene immediately
        after it's written, before moving to the next.

        Args:
            scene: Single scene dict with slugline, elements, duration, etc.
            scene_index: Zero-based index for error labeling.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []
        scene_label = f"Scene {scene_index + 1}"

        # -- 3. Valid slugline
        slugline = (scene.get("slugline") or "").strip()
        if not slugline:
            errors.append(
                f"MISSING_SLUGLINE [{scene_label}]: Every scene must have a slugline"
            )
        else:
            slugline_upper = slugline.upper()
            if not any(slugline_upper.startswith(prefix) for prefix in VALID_SLUGLINE_PREFIXES):
                errors.append(
                    f"INVALID_SLUGLINE [{scene_label}]: Slugline must start with "
                    f"INT., EXT., or INT/EXT. (got: '{slugline}')"
                )

        # -- 4. At least MIN_ELEMENTS_PER_SCENE elements
        elements = scene.get("elements", [])
        elem_count = len(elements) if isinstance(elements, list) else 0
        if elem_count < self.MIN_ELEMENTS_PER_SCENE:
            errors.append(
                f"TOO_FEW_ELEMENTS [{scene_label}]: Every scene needs at least "
                f"{self.MIN_ELEMENTS_PER_SCENE} elements (found {elem_count}). "
                f"A scene is a mini-movie: slugline, action, dialogue, exit."
            )

        # -- 5. estimated_duration_seconds > 0
        duration = scene.get("estimated_duration_seconds", 0)
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(
                f"INVALID_DURATION [{scene_label}]: estimated_duration_seconds "
                f"must be > 0 (got: {duration})"
            )

        # -- 6. Non-empty conflict field
        raw_conflict = scene.get("conflict") or ""
        conflict = str(raw_conflict).strip() if raw_conflict else ""
        if not conflict:
            errors.append(
                f"MISSING_CONFLICT [{scene_label}]: Every scene must have a "
                f"non-empty conflict field describing who wants what from whom"
            )

        # -- 7. Emotional start and end are "+" or "-"
        e_start = (scene.get("emotional_start") or "").strip()
        e_end = (scene.get("emotional_end") or "").strip()

        if not e_start and not e_end:
            legacy = (scene.get("emotional_polarity") or "").strip()
            if legacy in VALID_POLARITIES:
                e_start = legacy
                e_end = legacy

        if e_start not in VALID_POLARITIES:
            errors.append(
                f"INVALID_EMOTIONAL_START [{scene_label}]: emotional_start must be "
                f"'+' or '-' (got: '{e_start}')"
            )
        if e_end not in VALID_POLARITIES:
            errors.append(
                f"INVALID_EMOTIONAL_END [{scene_label}]: emotional_end must be "
                f"'+' or '-' (got: '{e_end}')"
            )

        # -- 8. No internal monologue markers in action elements
        if isinstance(elements, list):
            for elem_idx, element in enumerate(elements):
                content = (element.get("content") or "").lower()
                etype = (element.get("element_type") or "").strip()
                if etype == "action":
                    for marker in INTERNAL_MONOLOGUE_MARKERS:
                        if marker in content:
                            errors.append(
                                f"INTERNAL_MONOLOGUE [{scene_label}, element {elem_idx + 1}]: "
                                f"Found internal monologue marker '{marker}' in {etype} element. "
                                f"Screenplays show only what camera sees and microphone hears."
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
            if "MISSING_TITLE" in error:
                suggestions.append(
                    "Add a 'title' field with the screenplay's title."
                )
            elif "MISSING_LOGLINE" in error:
                suggestions.append(
                    "Add a 'logline' field with the 1-2 sentence logline."
                )
            elif "MISSING_SCENES" in error:
                suggestions.append(
                    "Add a 'scenes' array containing all screenplay scenes."
                )
            elif "TOO_FEW_SCENES" in error:
                suggestions.append(
                    "Expand ALL board cards into individual scenes. Each of the "
                    "40 board cards should become at least one scene."
                )
            elif "MISSING_SLUGLINE" in error:
                suggestions.append(
                    "Add a slugline to the scene in standard format: "
                    "INT. LOCATION - TIME or EXT. LOCATION - TIME."
                )
            elif "INVALID_SLUGLINE" in error:
                suggestions.append(
                    "Fix the slugline to start with INT., EXT., or INT/EXT. "
                    "followed by LOCATION - TIME OF DAY."
                )
            elif "TOO_FEW_ELEMENTS" in error:
                suggestions.append(
                    f"Add at least {self.MIN_ELEMENTS_PER_SCENE} elements to each scene. "
                    f"A scene is a mini-movie: slugline, establishing action, "
                    f"character+dialogue exchanges, and a visual exit."
                )
            elif "INVALID_DURATION" in error:
                suggestions.append(
                    "Set estimated_duration_seconds to a positive integer. "
                    "Average scene is 120-180 seconds (2-3 pages). 1 page = 60 seconds."
                )
            elif "MISSING_CONFLICT" in error:
                suggestions.append(
                    "Add a conflict description: who wants what from whom, "
                    "and who wins or loses in this scene."
                )
            elif "INVALID_EMOTIONAL_START" in error:
                suggestions.append(
                    "Set emotional_start to exactly '+' or '-' "
                    "(where the scene begins emotionally)."
                )
            elif "INVALID_EMOTIONAL_END" in error:
                suggestions.append(
                    "Set emotional_end to exactly '+' or '-' "
                    "(where the scene ends emotionally — should differ from start)."
                )
            elif "INTERNAL_MONOLOGUE" in error:
                suggestions.append(
                    "Remove internal monologue. Replace thoughts/feelings with "
                    "visible actions: 'She felt sick' -> 'She grabs the table. "
                    "Steadies herself.' Only show what camera sees."
                )
            elif "DURATION_TOO_SHORT" in error:
                suggestions.append(
                    f"Increase scene durations. Total screenplay must be at least "
                    f"{self.MIN_TOTAL_DURATION} seconds ({self.MIN_TOTAL_DURATION // 60} minutes). "
                    f"Average scene is 120-180 seconds (2-3 pages)."
                )
            elif "MISSING_TOTAL_PAGES" in error:
                suggestions.append(
                    "Add a 'total_pages' field. Calculate as total_duration / 60."
                )
            elif "INVALID_TOTAL_PAGES" in error:
                suggestions.append(
                    "Set total_pages to a positive number. "
                    "Calculate as sum of all scene durations divided by 60."
                )
            elif "INSUFFICIENT_DIALOGUE" in error:
                suggestions.append(
                    f"Add dialogue to more scenes. At least {self.MIN_DIALOGUE_RATIO:.0%} of scenes "
                    f"should contain spoken dialogue. Write sustained exchanges "
                    f"(3+ back-and-forth), not single lines."
                )
            elif "LOW_SCENE_DENSITY" in error:
                suggestions.append(
                    f"Add more elements to scenes. Each scene needs at least "
                    f"{self.MIN_AVG_ELEMENTS} elements on average: slugline, establishing "
                    f"action, character+dialogue pairs, reactive action, exit."
                )
            else:
                suggestions.append("Review and fix the indicated issue.")

        return suggestions
