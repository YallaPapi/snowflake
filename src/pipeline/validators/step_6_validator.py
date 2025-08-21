"""
Step 6 Validator: Long Synopsis
"""
from typing import Tuple, List, Dict, Any

class Step6Validator:
    VERSION = "1.1.0"  # Updated: More flexible keyword matching for AI-generated content

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        text = artifact.get("long_synopsis", "").strip()
        if not text:
            errors.append("MISSING: long_synopsis text")
            return False, errors
        if len(text) < 1000:
            errors.append("TOO SHORT: long_synopsis should be several pages (>=1000 chars for MVP)")
        # Basic presence hints for D1/D2/D3 cues - more flexible keyword matching
        lower = text.lower()
        
        # Check for moral pivot concepts (more flexible)
        pivot_keywords = ["pivot", "new tactic", "realizes", "understands", "learns", 
                         "discovers", "shift", "transformation", "new approach", 
                         "different way", "changes course", "revelation"]
        if not any(keyword in lower for keyword in pivot_keywords):
            errors.append("MISSING MORAL PIVOT cue (needs concept of realization/transformation)")
        
        # Check for bottleneck concepts (more flexible)
        bottleneck_keywords = ["bottleneck", "only path", "no options", "final", 
                              "last chance", "one way", "single choice", "narrowing", 
                              "closing in", "cornered", "ultimatum", "converge"]
        if not any(keyword in lower for keyword in bottleneck_keywords):
            errors.append("MISSING BOTTLENECK cue (needs concept of narrowing options)")
        
        # Check for forcing function concepts (more flexible)
        forcing_keywords = ["forces", "no way back", "cannot retreat", "irreversible", 
                           "must", "trapped", "committed", "no choice", "no escape", 
                           "point of no return", "can't turn back", "locked in"]
        if not any(keyword in lower for keyword in forcing_keywords):
            errors.append("MISSING FORCING FUNCTION cue (needs concept of irreversible commitment)")
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
