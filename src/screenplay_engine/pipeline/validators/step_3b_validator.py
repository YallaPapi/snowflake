"""
Step 3b Validator: World Bible
Validates that the world bible is comprehensive, sensory-rich, and structurally
complete — covering arena, geography, social structure, economy, culture,
language, daily life, history, and rules of conflict.
"""

import json
from typing import Tuple, List, Dict, Any


def _to_str(val) -> str:
    """Coerce a value to string — joins lists, converts others via str()."""
    if val is None:
        return ""
    if isinstance(val, list):
        return " ".join(str(s) for s in val).strip()
    return str(val).strip()


# Valid location types for key_locations entries
VALID_LOCATION_TYPES = {
    "residential", "commercial", "industrial", "institutional",
    "natural", "transit", "entertainment",
}

# All required top-level sections (must be dicts)
REQUIRED_SECTIONS = [
    "arena",
    "geography",
    "social_structure",
    "economy",
    "culture",
    "language_patterns",
    "daily_life",
    "history",
    "rules_of_conflict",
]


class Step3bValidator:
    """Validator for Screenplay Engine Step 3b: World Bible"""

    VERSION = "1.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a world bible artifact.

        Checks:
            1.  All top-level sections exist and are dicts
            2.  arena.description is non-empty string >= 50 chars
            3.  arena.rules is a non-empty list
            4.  geography.key_locations is a list with 5+ entries
            5.  Each key_location has: name, type, description (>= 50 chars),
                atmosphere, significance
            6.  key_location type is one of the valid types
            7.  daily_life.sensory_palette exists and is >= 50 chars
            8.  rules_of_conflict.story_engine exists and is >= 20 chars
            9.  culture.values exists and is >= 20 chars
            10. Total word count of the full artifact (as JSON string) >= 3000

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # ── 1. All top-level sections exist and are dicts ─────────────
        for section in REQUIRED_SECTIONS:
            value = artifact.get(section)
            if value is None:
                errors.append(
                    f"MISSING_SECTION_{section.upper()}: Required top-level section "
                    f"'{section}' is missing from the world bible."
                )
            elif not isinstance(value, dict):
                errors.append(
                    f"INVALID_SECTION_{section.upper()}: '{section}' must be a JSON "
                    f"object (dict), got {type(value).__name__}."
                )

        # If critical sections are missing, return early — downstream
        # checks would all fail with confusing messages
        missing_critical = [
            s for s in REQUIRED_SECTIONS
            if not isinstance(artifact.get(s), dict)
        ]
        if missing_critical:
            return False, errors

        # ── 2. arena.description is non-empty string >= 50 chars ──────
        arena = artifact["arena"]
        arena_desc = (arena.get("description") or "").strip()
        if not arena_desc:
            errors.append(
                "MISSING_ARENA_DESCRIPTION: arena.description is required — "
                "write 2-3 paragraphs of rich sensory prose describing the world."
            )
        elif len(arena_desc) < 50:
            errors.append(
                f"SHORT_ARENA_DESCRIPTION: arena.description is only "
                f"{len(arena_desc)} characters — needs at least 50. Write "
                f"rich, sensory prose describing what a drone camera would see."
            )

        # ── 3. arena.rules is a non-empty list ───────────────────────
        arena_rules = arena.get("rules")
        if arena_rules is None or not isinstance(arena_rules, list):
            errors.append(
                "MISSING_ARENA_RULES: arena.rules must be a non-empty list of "
                "world rules (what is possible, what is impossible)."
            )
        elif len(arena_rules) == 0:
            errors.append(
                "EMPTY_ARENA_RULES: arena.rules list is empty — include at "
                "least one rule about what is possible or impossible in this world."
            )

        # ── 4. geography.key_locations is a list with 5+ entries ─────
        geography = artifact["geography"]
        locations = geography.get("key_locations")
        if locations is None or not isinstance(locations, list):
            errors.append(
                "MISSING_KEY_LOCATIONS: geography.key_locations must be a list "
                "of at least 5 location objects."
            )
            locations = []  # prevent downstream errors
        elif len(locations) < 5:
            errors.append(
                f"TOO_FEW_LOCATIONS: geography.key_locations has only "
                f"{len(locations)} entries — a feature film needs at least 5 "
                f"distinct locations. Think: hero's home, workplace, "
                f"antagonist's territory, B-story location, climax venue."
            )

        # ── 5 & 6. Per-location checks ───────────────────────────────
        required_loc_fields = ["name", "type", "description", "atmosphere", "significance"]
        for idx, loc in enumerate(locations):
            if not isinstance(loc, dict):
                errors.append(
                    f"INVALID_LOCATION_{idx}: Each key_location must be a JSON "
                    f"object with name, type, description, atmosphere, significance."
                )
                continue

            prefix = f"LOCATION_{idx + 1}"
            loc_name = (loc.get("name") or "").strip()

            # Check required fields exist and are non-empty
            for field in required_loc_fields:
                value = (loc.get(field) or "").strip()
                if not value:
                    display_name = loc_name or f"location {idx + 1}"
                    errors.append(
                        f"{prefix}_MISSING_{field.upper()}: '{display_name}' is "
                        f"missing required field '{field}'."
                    )

            # Check description length (>= 50 chars)
            loc_desc = (loc.get("description") or "").strip()
            if loc_desc and len(loc_desc) < 50:
                display_name = loc_name or f"location {idx + 1}"
                errors.append(
                    f"{prefix}_SHORT_DESCRIPTION: '{display_name}' description "
                    f"is only {len(loc_desc)} chars — needs at least 50 chars "
                    f"of concrete visual/sensory detail."
                )

            # Check type is valid
            loc_type = (loc.get("type") or "").strip().lower()
            if loc_type and loc_type not in VALID_LOCATION_TYPES:
                display_name = loc_name or f"location {idx + 1}"
                errors.append(
                    f"{prefix}_INVALID_TYPE: '{display_name}' has type "
                    f"'{loc_type}' — must be one of: "
                    f"{', '.join(sorted(VALID_LOCATION_TYPES))}."
                )

        # ── 7. daily_life.sensory_palette >= 50 chars ─────────────────
        daily_life = artifact["daily_life"]
        sensory = _to_str(daily_life.get("sensory_palette"))
        if not sensory:
            errors.append(
                "MISSING_SENSORY_PALETTE: daily_life.sensory_palette is "
                "required — list the 5-6 signature sounds, smells, textures, "
                "and tastes that define this world."
            )
        elif len(sensory) < 50:
            errors.append(
                f"SHORT_SENSORY_PALETTE: daily_life.sensory_palette is only "
                f"{len(sensory)} chars — needs at least 50. List SPECIFIC "
                f"sensations, not abstractions."
            )

        # ── 8. rules_of_conflict.story_engine >= 20 chars ────────────
        conflict = artifact["rules_of_conflict"]
        story_engine = _to_str(conflict.get("story_engine"))
        if not story_engine:
            errors.append(
                "MISSING_STORY_ENGINE: rules_of_conflict.story_engine is "
                "required — explain why conflict is INEVITABLE in this world, "
                "connecting directly to the logline."
            )
        elif len(story_engine) < 20:
            errors.append(
                f"SHORT_STORY_ENGINE: rules_of_conflict.story_engine is only "
                f"{len(story_engine)} chars — needs at least 20. Explain why "
                f"conflict is unavoidable and how it connects to the logline."
            )

        # ── 9. culture.values >= 20 chars ────────────────────────────
        culture = artifact["culture"]
        values = _to_str(culture.get("values"))
        if not values:
            errors.append(
                "MISSING_CULTURE_VALUES: culture.values is required — "
                "describe what this community prizes above all else."
            )
        elif len(values) < 20:
            errors.append(
                f"SHORT_CULTURE_VALUES: culture.values is only {len(values)} "
                f"chars — needs at least 20. Describe what this community "
                f"prizes above all else."
            )

        # ── 10. Total word count >= 3000 ─────────────────────────────
        # Exclude metadata from word count — we only care about content
        content_artifact = {k: v for k, v in artifact.items() if k != "metadata"}
        artifact_text = json.dumps(content_artifact, ensure_ascii=False)
        word_count = len(artifact_text.split())
        if word_count < 3000:
            errors.append(
                f"INSUFFICIENT_WORD_COUNT: World bible has approximately "
                f"{word_count} words — needs at least 3000. This is the "
                f"foundation of the entire screenplay. Be exhaustive with "
                f"sensory details, location descriptions, and cultural texture."
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
            if "MISSING_SECTION_" in error:
                # Extract section name from error code
                suggestions.append(
                    "Add the missing top-level section as a JSON object. "
                    "Required sections: arena, geography, social_structure, "
                    "economy, culture, language_patterns, daily_life, history, "
                    "rules_of_conflict."
                )
            elif "INVALID_SECTION_" in error:
                suggestions.append(
                    "Convert the section to a JSON object (dict) with the "
                    "required sub-fields. It cannot be a string, list, or null."
                )
            elif "MISSING_ARENA_DESCRIPTION" in error:
                suggestions.append(
                    "Write 2-3 paragraphs of sensory prose for arena.description. "
                    "Describe what a drone camera would see flying over this world."
                )
            elif "SHORT_ARENA_DESCRIPTION" in error:
                suggestions.append(
                    "Expand arena.description to at least 50 characters. Write "
                    "rich, sensory prose — not abstract summaries."
                )
            elif "MISSING_ARENA_RULES" in error or "EMPTY_ARENA_RULES" in error:
                suggestions.append(
                    "Add a 'rules' list to arena with at least one entry. Each "
                    "rule should state what is possible, impossible, or forbidden "
                    "in this world. Sanderson's Second Law: limitations create drama."
                )
            elif "MISSING_KEY_LOCATIONS" in error:
                suggestions.append(
                    "Add a 'key_locations' list to geography with at least 5 "
                    "location objects. Each needs: name, type, description, "
                    "atmosphere, significance."
                )
            elif "TOO_FEW_LOCATIONS" in error:
                suggestions.append(
                    "Add more locations to reach at least 5. Consider: hero's "
                    "home, workplace, antagonist's territory, B-story location, "
                    "climax venue."
                )
            elif "_MISSING_NAME" in error:
                suggestions.append(
                    "Give the location a specific, evocative name."
                )
            elif "_MISSING_TYPE" in error or "_INVALID_TYPE" in error:
                suggestions.append(
                    "Set location type to one of: residential, commercial, "
                    "industrial, institutional, natural, transit, entertainment."
                )
            elif "_MISSING_DESCRIPTION" in error or "_SHORT_DESCRIPTION" in error:
                suggestions.append(
                    "Write at least 3 sentences (50+ chars) of sensory prose "
                    "for the location description. Describe what you see, hear, "
                    "smell, and feel when you walk in."
                )
            elif "_MISSING_ATMOSPHERE" in error:
                suggestions.append(
                    "Describe the mood and energy of the location — how it FEELS "
                    "at different times of day."
                )
            elif "_MISSING_SIGNIFICANCE" in error:
                suggestions.append(
                    "Explain why scenes happen at this location — what it means "
                    "to the story and characters."
                )
            elif "INVALID_LOCATION_" in error:
                suggestions.append(
                    "Each key_location must be a JSON object with fields: name, "
                    "type, description, atmosphere, significance."
                )
            elif "MISSING_SENSORY_PALETTE" in error:
                suggestions.append(
                    "Add sensory_palette to daily_life: list 5-6 signature "
                    "sounds, smells, textures, and tastes. Be specific — not "
                    "'it smells nice' but 'diesel exhaust, jasmine, burnt coffee.'"
                )
            elif "SHORT_SENSORY_PALETTE" in error:
                suggestions.append(
                    "Expand sensory_palette to at least 50 characters with "
                    "SPECIFIC sensations — sounds, smells, textures, tastes."
                )
            elif "MISSING_STORY_ENGINE" in error:
                suggestions.append(
                    "Add story_engine to rules_of_conflict explaining why "
                    "conflict is INEVITABLE in this world. Must connect "
                    "directly to the logline."
                )
            elif "SHORT_STORY_ENGINE" in error:
                suggestions.append(
                    "Expand story_engine to at least 20 characters. Explain "
                    "the structural reason conflict cannot be avoided."
                )
            elif "MISSING_CULTURE_VALUES" in error:
                suggestions.append(
                    "Add values to culture describing what this community "
                    "prizes above all else — reputation, money, family, etc."
                )
            elif "SHORT_CULTURE_VALUES" in error:
                suggestions.append(
                    "Expand culture.values to at least 20 characters describing "
                    "what this community prizes."
                )
            elif "INSUFFICIENT_WORD_COUNT" in error:
                suggestions.append(
                    "The world bible is too short. Expand all sections with "
                    "more sensory detail, longer location descriptions, richer "
                    "cultural texture, and more specific language patterns. "
                    "Target 3000+ words total."
                )
            else:
                suggestions.append("Review and fix the indicated issue.")

        return suggestions
