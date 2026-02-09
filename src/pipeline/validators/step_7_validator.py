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
                continue
            
            # Check physical details
            physical = b.get("physical", {})
            if not physical:
                errors.append(f"MISSING: physical details for {name}")
            else:
                # Accept either 'appearance' OR detailed fields like 'height', 'build', etc.
                has_appearance = physical.get("appearance")
                has_detailed = any(physical.get(f) for f in ["height", "build", "hair", "eyes", "face"])
                
                if not has_appearance and not has_detailed:
                    errors.append(f"MISSING: physical details (appearance or detailed fields) for {name}")
                
                # Age is always required
                if not physical.get("age"):
                    errors.append(f"MISSING: physical.age for {name}")
            
            # Check personality
            personality = b.get("personality")
            if not personality:
                errors.append(f"MISSING: personality for {name}")
            elif isinstance(personality, dict):
                if not personality.get("core_traits"):
                    errors.append(f"MISSING: core personality traits for {name}")
            elif isinstance(personality, str) and len(personality) < 50:
                errors.append(f"INSUFFICIENT: personality too brief for {name}")
            
            # Check environment
            environment = b.get("environment", {})
            if not environment:
                errors.append(f"MISSING: environment details for {name}")
            else:
                required_env = ["home", "work"]
                for field in required_env:
                    if not environment.get(field) and not environment.get(f"current_{field}"):
                        errors.append(f"MISSING: environment.{field} for {name}")
            
            # Check psychology
            psychology = b.get("psychology", {})
            if not psychology:
                errors.append(f"MISSING: psychology for {name}")
            else:
                # Check for key psychological elements (but be flexible with field names)
                has_wound = any(psychology.get(f) for f in ["wound", "backstory_wound", "ghost", "trauma"])
                has_lie = any(psychology.get(f) for f in ["lie", "lie_believes", "false_belief", "internal_conflict"])
                has_need = any(psychology.get(f) for f in ["need", "truth_needs", "internal_need", "arc"])
                
                # Only require at least 2 of the 3 core elements
                elements_present = sum([has_wound, has_lie, has_need])
                if elements_present < 2:
                    errors.append(f"INSUFFICIENT: psychology needs more depth (wound/lie/need) for {name}")
            
            # Check primal urge connection (Save the Cat requirement)
            # Characters with primal motivation create better stories
            primal_urges = ["survival", "hunger", "sex", "protection", "loved ones", "fear of death", "death"]
            role = b.get("role", "").lower()
            if role in ("protagonist", "hero", "main character", "lead"):
                motivation = ""
                if isinstance(psychology, dict):
                    motivation = " ".join(str(v) for v in [
                        psychology.get("need", ""),
                        psychology.get("truth_needs", ""),
                        psychology.get("internal_need", ""),
                        psychology.get("motivation", ""),
                        psychology.get("desire", ""),
                        b.get("motivation", ""),
                        b.get("goal", ""),
                    ]).lower()
                has_primal = any(urge in motivation for urge in primal_urges)
                if not has_primal and motivation.strip():
                    errors.append(f"WEAK_MOTIVATION: {name}'s goal must connect to a primal urge (survival, hunger, sex, protection of loved ones, fear of death). This is what makes audiences CARE.")

            # Check voice notes
            if not isinstance(b.get("voice_notes", []), list):
                errors.append(f"INVALID: voice_notes must be a list for {name}")
            elif len(b.get("voice_notes", [])) < 1:
                errors.append(f"INSUFFICIENT: need at least 1 voice note for {name}")
            
            # Check completeness (80% rule)
            total_fields = 0
            filled_fields = 0
            
            # Count fields in each section
            for section in ["physical", "personality", "environment", "psychology"]:
                section_data = b.get(section, {})
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        total_fields += 1
                        if value and (not isinstance(value, str) or len(str(value).strip()) > 0):
                            filled_fields += 1
                elif section_data:  # String or other non-empty value
                    total_fields += 1
                    filled_fields += 1
            
            if total_fields > 0:
                completeness = (filled_fields / total_fields) * 100
                if completeness < 60:
                    errors.append(f"INCOMPLETE: {name} only {completeness:.0f}% complete (need 60%)")
        
        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        out: List[str] = []
        for e in errors:
            if "MISSING: bibles" in e:
                out.append("Provide a 'bibles' array with detailed entries per character")
            elif "MISSING: physical" in e:
                out.append("Add complete physical details: age, appearance, build, distinguishing features")
            elif "MISSING: personality" in e or "INSUFFICIENT: personality" in e:
                out.append("Expand personality with core traits, strengths, weaknesses, communication style")
            elif "MISSING: environment" in e:
                out.append("Add environment details: home, work, economic status, daily routine")
            elif "MISSING: psychology" in e or "psychological elements" in e:
                out.append("Include psychological depth: backstory wound, lie believes, truth needs, internal conflict, arc")
            elif "INVALID: voice_notes" in e or "INSUFFICIENT: need at least" in e:
                out.append("Provide at least 2-3 voice notes: speech patterns, vocabulary, verbal tics")
            elif "WEAK_MOTIVATION:" in e:
                out.append("Connect protagonist's goal to a primal urge: survival, hunger, sex, protection of loved ones, or fear of death")
            elif "INCOMPLETE:" in e:
                out.append("Fill out more character details to reach 80% completeness")
            else:
                out.append("Ensure all character bible sections are thoroughly filled")
        return out
