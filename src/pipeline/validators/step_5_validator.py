"""
Step 5 Validator: Character Synopses
"""
from typing import Tuple, List, Dict, Any

class Step5Validator:
    VERSION = "1.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        chars = artifact.get("characters")
        if not isinstance(chars, list) or not chars:
            errors.append("MISSING: characters list")
            return False, errors
        for idx, c in enumerate(chars, 1):
            name = c.get("name", "").strip()
            syn = c.get("synopsis", "").strip()
            if not name:
                errors.append(f"MISSING: character[{idx}].name")
            if len(syn) < 300:
                errors.append(f"TOO SHORT: synopsis for {name or 'character'} (<300 chars)")
        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        out: List[str] = []
        for e in errors:
            if e.startswith("MISSING: characters"):
                out.append("Provide a 'characters' array with objects {name, synopsis}")
            elif e.startswith("MISSING: character"):
                out.append("Include the character's name from Step 3 list")
            elif e.startswith("TOO SHORT"):
                out.append("Expand synopsis to ~0.5–1 page with role, need/lie, conflicts, outcome")
            else:
                out.append("Ensure plain, causal summary tied to plot spine")
        return out
