"""
Step 7 Validator: Character Bibles
"""
from typing import Tuple, List, Dict, Any

class Step7Validator:
    VERSION = "1.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        bibles = artifact.get("bibles")
        if not isinstance(bibles, list) or not bibles:
            errors.append("MISSING: bibles list")
            return False, errors
        for idx, b in enumerate(bibles, 1):
            name = b.get("name", "").strip()
            if not name:
                errors.append(f"MISSING: bibles[{idx}].name")
            if not b.get("personality"):
                errors.append(f"MISSING: personality for {name or 'character'}")
            if not isinstance(b.get("voice_notes", []), list):
                errors.append(f"INVALID: voice_notes must be a list for {name or 'character'}")
        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        out: List[str] = []
        for e in errors:
            if e.startswith("MISSING: bibles"):
                out.append("Provide a 'bibles' array with detailed entries per character")
            elif e.startswith("MISSING: bibles") or e.startswith("MISSING: personality"):
                out.append("Add personality with concrete adjectives and behavioral cues")
            elif e.startswith("INVALID: voice_notes"):
                out.append("Provide voice_notes as a list of short bullet strings")
            else:
                out.append("Ensure physical, environment, psychology, and voice are filled")
        return out
