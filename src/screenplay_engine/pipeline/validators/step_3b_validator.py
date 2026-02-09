"""
Step 3b Validator: Supporting Cast
Validates that the supporting cast is complete, diverse, and well-defined
before proceeding to the Beat Sheet.
"""

from typing import Tuple, List, Dict, Any


VALID_ROLES = {
    "ally", "mentor", "rival", "love_interest", "authority",
    "victim", "comic_relief", "henchman", "witness", "other",
}


class Step3bValidator:
    """Validator for Screenplay Engine Step 3b: Supporting Cast"""

    VERSION = "1.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a supporting cast artifact.

        Checks:
            1. 'characters' list exists with 4-20 entries
            2. Each character has required fields: name, role, relationship_to_hero
            3. Each role is one of the valid role types
            4. Each character has a distinctive_trait (Limp and Eye Patch)
            5. Each character has a voice_profile
            6. No duplicate character names
            7. total_speaking_roles and total_non_speaking fields exist

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        # 1. Characters list exists
        characters = artifact.get("characters")
        if characters is None:
            errors.append(
                "MISSING_CHARACTERS: Artifact must contain a 'characters' list."
            )
            return False, errors

        if not isinstance(characters, list):
            errors.append(
                "INVALID_CHARACTERS_TYPE: 'characters' must be a list."
            )
            return False, errors

        if len(characters) < 4:
            errors.append(
                f"TOO_FEW_CHARACTERS: Supporting cast has {len(characters)} characters, "
                f"minimum is 4. A feature screenplay needs at least 6-8 supporting roles."
            )
        elif len(characters) > 20:
            errors.append(
                f"TOO_MANY_CHARACTERS: Supporting cast has {len(characters)} characters, "
                f"maximum is 20. Consolidate roles or remove minor characters."
            )

        # Per-character checks
        seen_names: set = set()
        for idx, char in enumerate(characters):
            if not isinstance(char, dict):
                errors.append(f"INVALID_CHARACTER_{idx}: Each character must be a dict.")
                continue

            prefix = f"Character {idx + 1}"

            # 2. Required fields
            name = (char.get("name") or "").strip()
            if not name:
                errors.append(f"{prefix}_MISSING_NAME: Character must have a non-empty name.")
            else:
                # 6. Duplicate names
                name_lower = name.lower()
                if name_lower in seen_names:
                    errors.append(f"{prefix}_DUPLICATE_NAME: '{name}' appears more than once.")
                seen_names.add(name_lower)

            role = (char.get("role") or "").strip().lower()
            if not role:
                errors.append(f"{prefix}_MISSING_ROLE: Character '{name or '?'}' must have a role.")
            elif role not in VALID_ROLES:
                errors.append(
                    f"{prefix}_INVALID_ROLE: '{role}' is not a valid role. "
                    f"Must be one of: {', '.join(sorted(VALID_ROLES))}"
                )

            relationship = (char.get("relationship_to_hero") or "").strip()
            if not relationship:
                errors.append(
                    f"{prefix}_MISSING_RELATIONSHIP: Character '{name or '?'}' must have "
                    f"relationship_to_hero defined."
                )

            # 4. Distinctive trait (from Ch.7 "Limp and Eye Patch" diagnostic)
            trait = (char.get("distinctive_trait") or "").strip()
            if not trait:
                errors.append(
                    f"{prefix}_MISSING_TRAIT: Character '{name or '?'}' must have a "
                    f"distinctive_trait (Limp and Eye Patch: physical, behavioral, or verbal)."
                )

            # 5. Voice profile
            voice = (char.get("voice_profile") or "").strip()
            if not voice:
                errors.append(
                    f"{prefix}_MISSING_VOICE: Character '{name or '?'}' must have a "
                    f"voice_profile describing how they speak differently."
                )

        # 7. Count fields
        speaking = artifact.get("total_speaking_roles")
        if speaking is None:
            errors.append("MISSING_SPEAKING_COUNT: 'total_speaking_roles' field is required.")
        non_speaking = artifact.get("total_non_speaking")
        if non_speaking is None:
            errors.append("MISSING_NON_SPEAKING_COUNT: 'total_non_speaking' field is required.")

        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Provide specific fix suggestions for each validation error."""
        suggestions: List[str] = []
        for error in errors:
            if "MISSING_CHARACTERS" in error or "INVALID_CHARACTERS_TYPE" in error:
                suggestions.append("Add a 'characters' list with 4-20 supporting character objects.")
            elif "TOO_FEW" in error:
                suggestions.append("Add more supporting characters. A feature film typically needs 8-12.")
            elif "TOO_MANY" in error:
                suggestions.append("Reduce to 20 or fewer. Merge similar roles.")
            elif "MISSING_NAME" in error:
                suggestions.append("Give the character a full name.")
            elif "DUPLICATE_NAME" in error:
                suggestions.append("Each character must have a unique name. Rename the duplicate.")
            elif "MISSING_ROLE" in error or "INVALID_ROLE" in error:
                suggestions.append(
                    "Set role to one of: ally, mentor, rival, love_interest, authority, "
                    "victim, comic_relief, henchman, witness, other."
                )
            elif "MISSING_RELATIONSHIP" in error:
                suggestions.append("Describe how this character relates to the protagonist.")
            elif "MISSING_TRAIT" in error:
                suggestions.append(
                    "Add a distinctive_trait: one memorable physical, behavioral, or verbal trait. "
                    "Per Snyder's 'Limp and Eye Patch' diagnostic, every character needs one."
                )
            elif "MISSING_VOICE" in error:
                suggestions.append(
                    "Add a voice_profile: describe their speech pattern, vocabulary, "
                    "sentence length, and any verbal tics."
                )
            elif "SPEAKING_COUNT" in error or "NON_SPEAKING_COUNT" in error:
                suggestions.append("Add the total_speaking_roles and total_non_speaking integer fields.")
            else:
                suggestions.append("Review and fix the indicated issue.")
        return suggestions
