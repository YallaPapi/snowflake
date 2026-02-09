"""
Step 3 Validator: Character Summary Sheets
Validates character summaries according to Snowflake Method
"""

import re
from typing import Dict, Any, Tuple, List, Optional

class Step3Validator:
    """
    Validator for Step 3: Character Summaries
    Enforces complete character sheets with all required fields
    """
    
    VERSION = "1.0.0"
    
    # Valid character roles
    VALID_ROLES = [
        "Protagonist", "Antagonist", "Love Interest", 
        "Ally", "Mentor", "Foil", "Supporting"
    ]
    
    # Required principals (minimum)
    REQUIRED_PRINCIPALS = ["Protagonist", "Antagonist"]
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 3 artifact
        
        Args:
            artifact: The Step 3 artifact to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        if 'characters' not in artifact:
            errors.append("MISSING CHARACTERS: No characters array found")
            return False, errors
        
        characters = artifact['characters']
        
        # RULE 1: Minimum character count
        if len(characters) < 2:
            errors.append(f"TOO FEW CHARACTERS: Need at least 2, found {len(characters)}")
        
        artifact['character_count'] = len(characters)
        
        # Track roles for validation
        roles_present = []
        character_names = []
        
        # RULE 2: Validate each character
        for i, character in enumerate(characters):
            char_errors = self.validate_character(character, i)
            errors.extend(char_errors)
            
            if 'role' in character:
                roles_present.append(character['role'])
            if 'name' in character:
                character_names.append(character['name'])
        
        # RULE 3: Required principals must be present
        for required_role in self.REQUIRED_PRINCIPALS:
            if required_role not in roles_present:
                errors.append(f"MISSING {required_role.upper()}: Story must have a {required_role}")
        
        # RULE 4: No duplicate names
        if len(character_names) != len(set(character_names)):
            duplicates = [name for name in character_names if character_names.count(name) > 1]
            errors.append(f"DUPLICATE NAMES: {', '.join(set(duplicates))}")
        
        # RULE 5: Protagonist-Antagonist collision check
        protagonist = self.get_character_by_role(characters, "Protagonist")
        antagonist = self.get_character_by_role(characters, "Antagonist")
        
        if protagonist and antagonist:
            collision_valid, collision_errors = self.validate_collision(protagonist, antagonist)
            errors.extend(collision_errors)
            
            artifact['protagonist_antagonist_collision'] = {
                'collision_verified': collision_valid,
                'collision_point': self.identify_collision_point(protagonist, antagonist)
            }
        
        # RULE 6: Disaster alignment check (informational only, not a gate)
        disaster_alignment = self.check_disaster_alignment(characters)
        artifact['disaster_alignment'] = disaster_alignment
        
        return len(errors) == 0, errors
    
    def validate_character(self, character: Dict[str, Any], index: int) -> List[str]:
        """Validate individual character sheet"""
        errors = []
        char_id = f"Character {index + 1}"
        
        # Check required fields
        required_fields = [
            'role', 'name', 'goal', 'ambition', 'values',
            'conflict', 'epiphany', 'one_sentence_summary', 'one_paragraph_summary'
        ]
        
        for field in required_fields:
            if field not in character or not character[field]:
                errors.append(f"{char_id} MISSING {field.upper()}")
        
        # Validate role
        if 'role' in character:
            if character['role'] not in self.VALID_ROLES:
                errors.append(f"{char_id} INVALID ROLE: '{character['role']}' not in {self.VALID_ROLES}")
        
        # Validate name
        if 'name' in character:
            name = character['name']
            if len(name) < 2:
                errors.append(f"{char_id} NAME TOO SHORT: Must be at least 2 characters")
            if len(name) > 50:
                errors.append(f"{char_id} NAME TOO LONG: Must be under 50 characters")
        
        # Validate goal (must be concrete and testable)
        if 'goal' in character:
            goal_errors = self.validate_goal(character['goal'], char_id)
            errors.extend(goal_errors)
        
        # Validate ambition (must be abstract)
        if 'ambition' in character:
            ambition_errors = self.validate_ambition(character['ambition'], char_id)
            errors.extend(ambition_errors)
        
        # Validate values (exactly 3, specific format)
        if 'values' in character:
            values_errors = self.validate_values(character['values'], char_id)
            errors.extend(values_errors)
        
        # Validate conflict
        if 'conflict' in character:
            conflict_errors = self.validate_conflict(character['conflict'], char_id)
            errors.extend(conflict_errors)
        
        # Validate epiphany
        if 'epiphany' in character:
            epiphany_errors = self.validate_epiphany(
                character['epiphany'], 
                character.get('role', ''),
                character.get('epiphany_justification', ''),
                char_id
            )
            errors.extend(epiphany_errors)
        
        # Validate summaries
        if 'one_sentence_summary' in character:
            if len(character['one_sentence_summary']) < 20:
                errors.append(f"{char_id} ONE-SENTENCE TOO SHORT: Must be at least 20 characters")
        
        if 'one_paragraph_summary' in character:
            paragraph_errors = self.validate_paragraph_summary(
                character['one_paragraph_summary'], char_id
            )
            errors.extend(paragraph_errors)
        
        # Special validation for antagonist interiority
        if character.get('role') == 'Antagonist':
            interiority_errors = self.validate_antagonist_interiority(character, char_id)
            errors.extend(interiority_errors)
        
        return errors
    
    def validate_goal(self, goal: str, char_id: str) -> List[str]:
        """Validate goal is concrete and testable"""
        errors = []

        if len(goal.strip()) < 5:
            errors.append(f"{char_id} GOAL TOO SHORT: Must describe a concrete objective")

        return errors
    
    def validate_ambition(self, ambition: str, char_id: str) -> List[str]:
        """Validate ambition is present"""
        errors = []

        if len(ambition.strip()) < 5:
            errors.append(f"{char_id} AMBITION TOO SHORT: Needs more detail")

        return errors
    
    def validate_values(self, values: List[str], char_id: str) -> List[str]:
        """Validate values format and count"""
        errors = []

        # Must have 2-5 values
        if len(values) < 2:
            errors.append(f"{char_id} TOO FEW VALUES: Need at least 2 values, found {len(values)}")
        elif len(values) > 5:
            errors.append(f"{char_id} TOO MANY VALUES: Maximum 5 values, found {len(values)}")

        for i, value in enumerate(values):
            # Must be non-trivial
            if len(value.strip()) < 5:
                errors.append(f"{char_id} VALUE {i+1} TOO SHORT: Must specify a concrete value")

            # Check for generic values
            generic_values = r'\b(stuff|things|whatever|something|anything)\b'
            if re.search(generic_values, value, re.I):
                errors.append(f"{char_id} VALUE {i+1} TOO GENERIC: Use specific nouns")

        return errors
    
    def validate_conflict(self, conflict: str, char_id: str) -> List[str]:
        """Validate conflict has substance"""
        errors = []

        if len(conflict.strip()) < 10:
            errors.append(f"{char_id} CONFLICT TOO SHORT: Must describe the opposing force")

        return errors
    
    def validate_epiphany(self, epiphany: str, role: str, justification: str, char_id: str) -> List[str]:
        """Validate epiphany or lack thereof"""
        errors = []
        
        if epiphany.upper() == "NONE":
            # Villains can have no epiphany but need justification
            if role == "Antagonist":
                if not justification or len(justification) < 10:
                    errors.append(f"{char_id} EPIPHANY NONE UNJUSTIFIED: Must explain why villain doesn't change")
            else:
                errors.append(f"{char_id} NON-VILLAIN NO EPIPHANY: Only antagonists can have 'NONE'")
        else:
            # Must describe learning/change
            learning_markers = r'\b(learns?|realizes?|discovers?|understands?|accepts?|embraces?|lets? go|stops?|starts?)\b'
            if not re.search(learning_markers, epiphany, re.I):
                errors.append(f"{char_id} EPIPHANY NO CHANGE: Must show what character learns/changes")
        
        return errors
    
    def validate_paragraph_summary(self, paragraph: str, char_id: str) -> List[str]:
        """Validate paragraph summary has substance"""
        errors = []

        # Check minimum length
        if len(paragraph) < 80:
            errors.append(f"{char_id} PARAGRAPH TOO SHORT: Must be at least 80 characters")

        return errors
    
    def validate_antagonist_interiority(self, character: Dict[str, Any], char_id: str) -> List[str]:
        """Special validation for antagonist depth"""
        errors = []
        
        # Check for interiority details
        if 'interiority' not in character:
            errors.append(f"{char_id} ANTAGONIST NO INTERIORITY: Must have motive/justification")
        else:
            interiority = character['interiority']
            
            if 'motive_history' not in interiority or len(interiority.get('motive_history', '')) < 20:
                errors.append(f"{char_id} ANTAGONIST NO MOTIVE: Must explain what made them this way")
            
            if 'justification' not in interiority or len(interiority.get('justification', '')) < 20:
                errors.append(f"{char_id} ANTAGONIST NO JUSTIFICATION: Must show how they justify actions")
        
        # Check that antagonist isn't flat
        if character.get('conflict', '').lower() == 'evil' or character.get('ambition', '').lower() == 'evil':
            errors.append(f"{char_id} ANTAGONIST FLAT: Give specific non-evil motivations")
        
        return errors
    
    def get_character_by_role(self, characters: List[Dict], role: str) -> Optional[Dict]:
        """Get character by role"""
        for char in characters:
            if char.get('role') == role:
                return char
        return None
    
    def validate_collision(self, protagonist: Dict, antagonist: Dict) -> Tuple[bool, List[str]]:
        """Validate protagonist goal collides with antagonist conflict"""
        errors = []
        
        protag_goal = protagonist.get('goal', '').lower()
        antag_conflict = antagonist.get('conflict', '').lower()
        
        # Check if they reference each other
        collision_found = False
        
        # Protagonist goal should relate to what antagonist opposes
        if any(word in antag_conflict for word in protag_goal.split()):
            collision_found = True
        
        # Or antagonist should specifically oppose protagonist
        if 'protagonist' in antag_conflict or protagonist.get('name', '').lower() in antag_conflict:
            collision_found = True
        
        if not collision_found:
            errors.append("NO COLLISION: Protagonist goal doesn't collide with antagonist conflict")
        
        return collision_found, errors
    
    def identify_collision_point(self, protagonist: Dict, antagonist: Dict) -> str:
        """Identify where protagonist and antagonist collide"""
        # Extract key elements
        protag_goal = protagonist.get('goal', '')
        antag_goal = antagonist.get('goal', '')
        
        # Find collision point
        if 'same' in protag_goal and 'same' in antag_goal:
            return "Both want the same thing"
        elif re.search(r'\b(stop|prevent|defeat)\b', protag_goal, re.I):
            return "Protagonist must stop antagonist"
        elif re.search(r'\b(protect|save)\b', protag_goal, re.I):
            return "Protagonist protects what antagonist threatens"
        else:
            return "Direct opposition of goals"
    
    def check_disaster_alignment(self, characters: List[Dict]) -> Dict[str, List[str]]:
        """Check which characters align with which disasters"""
        alignment = {
            'd1_characters': [],
            'd2_characters': [],
            'd3_characters': []
        }
        
        for char in characters:
            name = char.get('name', 'Unknown')
            paragraph = char.get('one_paragraph_summary', '')
            
            if re.search(r'\b(D1|disaster 1|first disaster)\b', paragraph, re.I):
                alignment['d1_characters'].append(name)
            
            if re.search(r'\b(D2|disaster 2|second disaster)\b', paragraph, re.I):
                alignment['d2_characters'].append(name)
            
            if re.search(r'\b(D3|disaster 3|third disaster|final)\b', paragraph, re.I):
                alignment['d3_characters'].append(name)
        
        return alignment
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "TOO FEW CHARACTERS" in error:
                suggestions.append("Add at least protagonist and antagonist")
            elif "MISSING PROTAGONIST" in error:
                suggestions.append("Add a Protagonist character")
            elif "MISSING ANTAGONIST" in error:
                suggestions.append("Add an Antagonist character")
            elif "GOAL NOT CONCRETE" in error:
                suggestions.append("Use action verb: win/stop/find/prove/save")
            elif "GOAL TOO INTERNAL" in error:
                suggestions.append("Convert to external: 'find peace' → 'stop the war'")
            elif "AMBITION TOO CONCRETE" in error:
                suggestions.append("Use abstract concept: security/freedom/justice")
            elif "WRONG VALUE COUNT" in error:
                suggestions.append("Provide exactly 3 value statements")
            elif "VALUE" in error and "WRONG FORMAT" in error:
                suggestions.append("Start with: 'Nothing is more important than...'")
            elif "CONFLICT VAGUE" in error:
                suggestions.append("Name specific person/system/force that opposes")
            elif "CONFLICT NO MECHANISM" in error:
                suggestions.append("Explain HOW it blocks: 'X prevents Y by...'")
            elif "EPIPHANY NO CHANGE" in error:
                suggestions.append("Show learning: 'realizes that...', 'learns to...'")
            elif "PARAGRAPH NO D" in error:
                suggestions.append("Reference all three disasters in paragraph")
            elif "ANTAGONIST NO INTERIORITY" in error:
                suggestions.append("Add motive history and justification")
            elif "ANTAGONIST FLAT" in error:
                suggestions.append("Give relatable non-evil motivations")
            elif "NO COLLISION" in error:
                suggestions.append("Make protagonist goal directly oppose antagonist's plan")
            else:
                suggestions.append("Review Step 3 requirements in guide")
        
        return suggestions