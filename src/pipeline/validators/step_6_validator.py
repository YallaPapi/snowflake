"""
Step 6 Validator: Long Synopsis
"""
from typing import Tuple, List, Dict, Any

class Step6Validator:
    VERSION = "1.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        text = artifact.get("long_synopsis", "").strip()
        if not text:
            errors.append("MISSING: long_synopsis text")
            return False, errors
        if len(text) < 1000:
            errors.append("TOO SHORT: long_synopsis should be several pages (>=1000 chars for MVP)")
        # Basic presence hints for D1/D2/D3 cues
        lower = text.lower()
        if "pivot" not in lower and "new tactic" not in lower:
            errors.append("MISSING MORAL PIVOT cue (mention 'pivot' or 'new tactic')")
        if "bottleneck" not in lower and "only path" not in lower:
            errors.append("MISSING BOTTLENECK cue (mention 'bottleneck' or 'only path')")
        if "forces" not in lower and "no way back" not in lower:
            errors.append("MISSING FORCING FUNCTION cue (mention 'forces' or 'no way back')")
        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        out: List[str] = []
        for e in errors:
            if e.startswith("MISSING: long_synopsis"):
                out.append("Provide multi-paragraph long synopsis expanding Step 4")
            elif e.startswith("TOO SHORT"):
                out.append("Expand each act with causal beats and observable outcomes")
            elif "PIVOT" in e:
                out.append("Show values/identity hit and pivot to new tactic in Act IIa")
            elif "BOTTLENECK" in e:
                out.append("Collapse options in Act IIb and name the bottleneck to endgame")
            elif "FORCING" in e:
                out.append("Name the forcing function at end of Act I that makes retreat impossible")
            else:
                out.append("Ensure cause→effect; avoid coincidences; keep plain language")
        return out
