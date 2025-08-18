"""
Step 1 Validator: One Sentence Summary (Logline)
Validates logline according to Snowflake Method requirements
"""

import re
from typing import Tuple, List, Dict, Any

# External goal verbs that are concrete and testable
CONCRETE_GOAL_VERBS = {
    'win', 'stop', 'find', 'escape', 'prove', 'steal', 'save', 'restore',
    'defeat', 'rescue', 'destroy', 'capture', 'protect', 'expose', 'prevent',
    'solve', 'survive', 'reach', 'deliver', 'recover', 'uncover', 'eliminate',
    'defend', 'overthrow', 'infiltrate', 'retrieve', 'secure', 'neutralize'
}

# Mood/internal goals that need to be converted
MOOD_GOALS = {
    'find herself', 'find himself', 'find themselves',
    'discover who', 'learn to', 'come to terms',
    'understand', 'accept', 'forgive', 'heal',
    'grow', 'mature', 'realize', 'become'
}

# Ending reveal words that shouldn't appear
ENDING_REVEALS = {
    'successfully', 'finally', 'ultimately', 'in the end',
    'wins', 'loses', 'dies', 'survives', 'marries',
    'kills', 'destroys', 'saves everyone', 'fails'
}

class Step1Validator:
    """Validator for Step 1: One Sentence Summary (Logline)"""
    
    VERSION = "1.0.0"
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 1 artifact according to Snowflake Method requirements
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required field
        if not artifact.get('logline'):
            errors.append("MISSING: Logline is required")
            return False, errors
            
        logline = artifact['logline'].strip()
        
        # 1. WORD COUNT CHECK (≤ 25 words)
        word_count = len(logline.split())
        artifact['word_count'] = word_count  # Store for reference
        
        if word_count > 25:
            errors.append(f"TOO LONG: Logline has {word_count} words (maximum 25). Cut prepositional trails and side facts.")
        
        # 2. SENTENCE STRUCTURE CHECK
        if not re.search(r'[.!?]$', logline):
            errors.append("PUNCTUATION: Logline must end with proper punctuation (.!?)")
        
        # Check for multiple sentences (should be ONE)
        sentence_count = len(re.findall(r'[.!?]+', logline))
        if sentence_count > 1:
            errors.append(f"MULTIPLE SENTENCES: Must be ONE sentence (found {sentence_count})")
        
        # 3. NAMED LEADS CHECK (≤ 2 named characters)
        # Look for capitalized names (rough heuristic)
        # More sophisticated: look for pattern "Name, a/an role"
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_names = re.findall(name_pattern, logline)
        
        # Filter out common words that aren't names
        common_words = {'The', 'A', 'An', 'But', 'And', 'Or', 'When', 'While', 'After', 'Before', 'During'}
        names = [name for name in potential_names if name not in common_words]
        
        artifact['lead_count'] = len(names)  # Store for reference
        
        if len(names) > 2:
            errors.append(f"TOO MANY NAMES: Found {len(names)} named characters (maximum 2). Keep roles for everyone except protagonist.")
        
        if len(names) == 0:
            errors.append("NO PROTAGONIST: Must name at least one lead character")
        
        # 4. EXTERNAL GOAL CHECK
        logline_lower = logline.lower()
        
        # Check for concrete goal verb
        has_concrete_goal = any(f" {verb}" in logline_lower or f" {verb}s" in logline_lower 
                               for verb in CONCRETE_GOAL_VERBS)
        
        # Check for "must" or similar obligation word
        has_must = any(word in logline_lower for word in ['must', 'has to', 'needs to', 'forced to'])
        
        if not has_must:
            errors.append("NO OBLIGATION: Missing 'must' or similar word indicating story necessity")
        
        if not has_concrete_goal:
            # Check if it's a mood goal
            has_mood_goal = any(mood in logline_lower for mood in MOOD_GOALS)
            if has_mood_goal:
                errors.append("MOOD GOAL: Convert internal goal to external proxy (e.g., 'find herself' → 'finish the marathon')")
            else:
                errors.append("NO CONCRETE GOAL: Must include testable external goal (win/stop/find/escape/prove/steal/save/restore)")
        
        # 5. OPPOSITION CHECK
        opposition_words = ['despite', 'against', 'while', 'before', 'without', 'but', 
                          'although', 'even though', 'as', 'when']
        has_opposition = any(word in logline_lower for word in opposition_words)
        
        if not has_opposition:
            # Alternative: Check for conflict-implying phrases
            conflict_phrases = ['must stop', 'must defeat', 'must escape', 'must survive', 
                              'must prevent', 'must overcome']
            has_implicit_conflict = any(phrase in logline_lower for phrase in conflict_phrases)
            
            if not has_implicit_conflict:
                errors.append("NO OPPOSITION: Add entity or constraint that actively blocks the goal")
        
        # 6. ENDING REVEAL CHECK
        reveals_ending = any(reveal in logline_lower for reveal in ENDING_REVEALS)
        if reveals_ending:
            errors.append("ENDING REVEALED: Remove outcome/resolution. End on tension, not conclusion.")
        
        # 7. ROLE AND STRUCTURE CHECK
        # Check for pattern: "Name, a/an role, must..."
        role_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+(?:a|an|the)\s+([^,]+),\s+must\s+'
        has_proper_structure = re.match(role_pattern, logline)
        
        if not has_proper_structure and len(names) > 0:
            # Less strict check - just ensure there's some role description
            if not re.search(r',\s+(?:a|an|the)\s+\w+', logline):
                errors.append("MISSING ROLE: Include functional role after name (e.g., 'Ava, an internal-affairs analyst')")
        
        # 8. PARSE COMPONENTS (for downstream use)
        if has_proper_structure:
            match = re.match(role_pattern, logline)
            if match:
                components = {
                    'lead_name': match.group(1),
                    'lead_role': match.group(2)
                }
                
                # Try to extract goal and opposition
                rest_of_sentence = logline[match.end():]
                
                # Look for goal (usually after "must")
                goal_match = re.search(r'^([^,\.]+?)(?:\s+(?:despite|against|while|before|but)|[,\.])', rest_of_sentence)
                if goal_match:
                    components['external_goal'] = goal_match.group(1).strip()
                
                # Look for opposition (after opposition words)
                opp_match = re.search(r'(?:despite|against|while|before|but|although)\s+(.+?)(?:\.|$)', rest_of_sentence)
                if opp_match:
                    components['opposition'] = opp_match.group(1).strip()
                
                artifact['components'] = components
        
        # CHECK FOR TODO MARKERS
        if "TODO" in logline or "BEST-GUESS" in logline:
            if 'metadata' not in artifact:
                artifact['metadata'] = {}
            if 'todo_markers' not in artifact['metadata']:
                artifact['metadata']['todo_markers'] = []
            artifact['metadata']['todo_markers'].append("TODO or BEST-GUESS marker found in logline")
        
        return len(errors) == 0, errors
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Provide specific fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "TOO LONG" in error:
                suggestions.append("Remove adjectives, prepositional trails, and side facts. Compress clauses into precise nouns.")
            elif "TOO MANY NAMES" in error:
                suggestions.append("Keep only protagonist's name (and maybe antagonist if iconic). Use roles for others.")
            elif "NO PROTAGONIST" in error:
                suggestions.append("Add protagonist name at the beginning: 'Sarah, a detective, must...'")
            elif "NO OBLIGATION" in error:
                suggestions.append("Add 'must' before the goal to show story necessity")
            elif "MOOD GOAL" in error:
                suggestions.append("Convert to external action: 'find herself' → 'win the marathon', 'heal' → 'reconcile with her father'")
            elif "NO CONCRETE GOAL" in error:
                suggestions.append("Use action verb: win/stop/find/escape/prove/steal/save/restore/defeat/rescue")
            elif "NO OPPOSITION" in error:
                suggestions.append("Add 'despite', 'before', or 'while' clause showing what blocks the goal")
            elif "ENDING REVEALED" in error:
                suggestions.append("Remove words like 'successfully', 'finally', 'wins', 'dies'. Keep the outcome uncertain.")
            elif "MISSING ROLE" in error:
                suggestions.append("Format as: 'Name, a/an [role], must [goal] despite [opposition]'")
                
        return suggestions
    
    def compress_logline(self, logline: str) -> str:
        """
        Helper method to compress a logline following the guide's rules
        """
        compressed = logline
        
        # Step 1: Remove unnecessary adjectives
        unnecessary_adjectives = [
            r'\b(?:very|really|quite|rather|somewhat|extremely|incredibly)\s+',
            r'\b(?:beautiful|handsome|young|old|small|large|big)\s+(?=\w+,)',  # Before roles
        ]
        for pattern in unnecessary_adjectives:
            compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)
        
        # Step 2: Compress verbose phrases
        compressions = {
            r'international criminals': 'the cartel',
            r'legal trouble': 'indictment',
            r'recently divorced': 'single',
            r'in order to': 'to',
            r'find a way to': '',
            r'figure out how to': '',
            r'try to': '',
            r'attempt to': '',
            r'manage to': ''
        }
        for verbose, concise in compressions.items():
            compressed = re.sub(verbose, concise, compressed, flags=re.IGNORECASE)
        
        # Step 3: Remove redundant phrases
        compressed = re.sub(r'\s+', ' ', compressed)  # Multiple spaces to single
        compressed = compressed.strip()
        
        return compressed