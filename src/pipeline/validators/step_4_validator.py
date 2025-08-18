"""
Step 4 Validator: One Page Synopsis
Validates the five-paragraph synopsis according to Snowflake Method
"""

import re
from typing import Dict, Any, Tuple, List

class Step4Validator:
    """
    Validator for Step 4: One Page Synopsis
    Enforces exactly five paragraphs expanding Step 2 sentences
    """
    
    VERSION = "1.0.0"
    
    # Target word counts
    MIN_TOTAL_WORDS = 500
    MAX_TOTAL_WORDS = 700
    MIN_PARA_WORDS = 80
    MAX_PARA_WORDS = 160
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 4 artifact
        
        Args:
            artifact: The Step 4 artifact to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        if 'synopsis' not in artifact:
            errors.append("MISSING SYNOPSIS: No synopsis text found")
            return False, errors
        
        if 'paragraphs' not in artifact:
            errors.append("MISSING PARAGRAPHS: No paragraph breakdown found")
            return False, errors
        
        synopsis = artifact['synopsis']
        paragraphs = artifact['paragraphs']
        
        # RULE 1: Word count validation
        word_count = len(synopsis.split())
        artifact['word_count'] = word_count
        
        if word_count < self.MIN_TOTAL_WORDS:
            errors.append(f"TOO SHORT: Synopsis has {word_count} words (minimum {self.MIN_TOTAL_WORDS})")
        elif word_count > self.MAX_TOTAL_WORDS:
            errors.append(f"TOO LONG: Synopsis has {word_count} words (maximum {self.MAX_TOTAL_WORDS})")
        
        # RULE 2: Exactly 5 paragraphs
        para_count = self.count_paragraphs(synopsis)
        artifact['paragraph_count'] = para_count
        
        if para_count != 5:
            errors.append(f"WRONG PARAGRAPH COUNT: Must be exactly 5 paragraphs, found {para_count}")
        
        # RULE 3: Validate each paragraph
        para_errors = self.validate_paragraphs(paragraphs)
        errors.extend(para_errors)
        
        # RULE 4: Disaster mapping validation
        disaster_mapping = self.validate_disaster_mapping(paragraphs)
        artifact['disaster_mapping'] = disaster_mapping
        
        if not disaster_mapping['d1_forcing']['present']:
            errors.append("D1 NOT FORCING: Paragraph 2 must show event that FORCES commitment")
        
        if not disaster_mapping['d2_pivot']['present']:
            errors.append("D2 NO PIVOT: Paragraph 3 must show moral pivot and tactic change")
        
        if not disaster_mapping['d3_bottleneck']['present']:
            errors.append("D3 NO BOTTLENECK: Paragraph 4 must narrow to one path")
        
        # RULE 5: Causality check
        causality = self.check_causality(paragraphs)
        artifact['causality_check'] = causality
        
        if causality['has_coincidence']:
            errors.append("COINCIDENCE FOUND: Replace with causal setup")
        
        if not causality['para_1_to_2']:
            errors.append("BROKEN CHAIN 1→2: Paragraph 2 doesn't follow from Paragraph 1")
        if not causality['para_2_to_3']:
            errors.append("BROKEN CHAIN 2→3: Paragraph 3 doesn't follow from Paragraph 2")
        if not causality['para_3_to_4']:
            errors.append("BROKEN CHAIN 3→4: Paragraph 4 doesn't follow from Paragraph 3")
        if not causality['para_4_to_5']:
            errors.append("BROKEN CHAIN 4→5: Paragraph 5 doesn't follow from Paragraph 4")
        
        # RULE 6: Expansion quality
        quality = self.check_expansion_quality(synopsis, paragraphs)
        artifact['expansion_quality'] = quality
        
        if not quality['maintains_spine']:
            errors.append("SPINE DRIFT: Synopsis deviates from Step 2 core story")
        
        if not quality['adds_specificity']:
            errors.append("TOO VAGUE: Add concrete details and specific events")
        
        if not quality['observable_outcomes']:
            errors.append("THEMATIC ENDING: Make outcomes observable, not abstract")
        
        return len(errors) == 0, errors
    
    def count_paragraphs(self, text: str) -> int:
        """Count paragraphs in text"""
        # Split on double newlines or common paragraph markers
        paragraphs = re.split(r'\n\s*\n', text.strip())
        # Filter out empty paragraphs
        paragraphs = [p for p in paragraphs if len(p.strip()) > 50]
        return len(paragraphs)
    
    def validate_paragraphs(self, paragraphs: Dict[str, str]) -> List[str]:
        """Validate individual paragraphs"""
        errors = []
        
        required_paras = [
            'para_1_setup',
            'para_2_disaster_1',
            'para_3_disaster_2',
            'para_4_disaster_3',
            'para_5_resolution'
        ]
        
        for para_key in required_paras:
            if para_key not in paragraphs:
                errors.append(f"MISSING {para_key.upper()}")
            else:
                para_text = paragraphs[para_key]
                word_count = len(para_text.split())
                
                if word_count < self.MIN_PARA_WORDS:
                    errors.append(f"{para_key.upper()} TOO SHORT: {word_count} words (minimum {self.MIN_PARA_WORDS})")
                elif word_count > self.MAX_PARA_WORDS:
                    errors.append(f"{para_key.upper()} TOO LONG: {word_count} words (maximum {self.MAX_PARA_WORDS})")
                
                # Specific validation per paragraph
                if para_key == 'para_1_setup':
                    setup_errors = self.validate_setup_paragraph(para_text)
                    errors.extend(setup_errors)
                elif para_key == 'para_2_disaster_1':
                    d1_errors = self.validate_disaster_1_paragraph(para_text)
                    errors.extend(d1_errors)
                elif para_key == 'para_3_disaster_2':
                    d2_errors = self.validate_disaster_2_paragraph(para_text)
                    errors.extend(d2_errors)
                elif para_key == 'para_4_disaster_3':
                    d3_errors = self.validate_disaster_3_paragraph(para_text)
                    errors.extend(d3_errors)
                elif para_key == 'para_5_resolution':
                    resolution_errors = self.validate_resolution_paragraph(para_text)
                    errors.extend(resolution_errors)
        
        return errors
    
    def validate_setup_paragraph(self, text: str) -> List[str]:
        """Validate setup paragraph requirements"""
        errors = []
        
        # Must establish situation
        if not re.search(r'\b(situation|problem|challenge|threat|opportunity)\b', text, re.I):
            errors.append("PARA_1 NO SITUATION: Must establish the opening situation")
        
        # Must show why goal matters NOW
        urgency_markers = r'\b(now|today|deadline|running out|last chance|urgent|immediately)\b'
        if not re.search(urgency_markers, text, re.I):
            errors.append("PARA_1 NO URGENCY: Must show why goal matters NOW")
        
        # Must identify first step
        action_markers = r'\b(first|begins?|starts?|initial|decides? to|must)\b'
        if not re.search(action_markers, text, re.I):
            errors.append("PARA_1 NO FIRST STEP: Must identify first visible step toward goal")
        
        return errors
    
    def validate_disaster_1_paragraph(self, text: str) -> List[str]:
        """Validate Disaster 1 paragraph"""
        errors = []
        
        # Must have forcing language
        forcing_markers = r'\b(forces?|forced|must|no choice|trapped|compelled|leaves? no)\b'
        if not re.search(forcing_markers, text, re.I):
            errors.append("PARA_2 NOT FORCING: Must use forcing language for D1")
        
        # Must explain why retreat impossible
        retreat_blockers = r'\b(no turning back|impossible to|cannot|no other|only way|committed)\b'
        if not re.search(retreat_blockers, text, re.I):
            errors.append("PARA_2 RETREAT POSSIBLE: Must explain why retreat is impossible")
        
        return errors
    
    def validate_disaster_2_paragraph(self, text: str) -> List[str]:
        """Validate Disaster 2 paragraph with moral pivot"""
        errors = []
        
        # Must show values/identity hit
        values_markers = r'\b(values?|beliefs?|identity|realizes?|discovers?|understands?|learns?)\b'
        if not re.search(values_markers, text, re.I):
            errors.append("PARA_3 NO VALUES HIT: Must show impact on values/identity")
        
        # Must show pivot to new tactic
        pivot_markers = r'\b(new|different|changes?|shifts?|pivots?|instead|abandons?|embraces?)\b'
        if not re.search(pivot_markers, text, re.I):
            errors.append("PARA_3 NO PIVOT: Must show change to new tactic")
        
        # Should reference moral premise
        moral_markers = r'\b(false|true|wrong|right|belief|approach|way)\b'
        if not re.search(moral_markers, text, re.I):
            errors.append("PARA_3 NO MORAL TIE: Should connect to moral premise")
        
        return errors
    
    def validate_disaster_3_paragraph(self, text: str) -> List[str]:
        """Validate Disaster 3 paragraph"""
        errors = []
        
        # Must stack pressures
        pressure_markers = r'\b(pressures?|tensions?|stakes|worse|desperate|critical|final)\b'
        if not re.search(pressure_markers, text, re.I):
            errors.append("PARA_4 NO PRESSURE: Must stack pressures")
        
        # Must name bottleneck
        bottleneck_markers = r'\b(only|one way|no other|must|final|last|single path)\b'
        if not re.search(bottleneck_markers, text, re.I):
            errors.append("PARA_4 NO BOTTLENECK: Must narrow to one path")
        
        return errors
    
    def validate_resolution_paragraph(self, text: str) -> List[str]:
        """Validate resolution paragraph"""
        errors = []
        
        # Must stage showdown
        showdown_markers = r'\b(confronts?|faces?|battles?|showdown|final|climax)\b'
        if not re.search(showdown_markers, text, re.I):
            errors.append("PARA_5 NO SHOWDOWN: Must stage the confrontation")
        
        # Must have immediate outcome
        outcome_markers = r'\b(wins?|loses?|succeeds?|fails?|saves?|dies?|escapes?|defeats?)\b'
        if not re.search(outcome_markers, text, re.I):
            errors.append("PARA_5 NO OUTCOME: Must show immediate outcome")
        
        # Must have emotional landing
        emotion_markers = r'\b(feels?|realizes?|understands?|accepts?|embraces?|chooses?)\b'
        if not re.search(emotion_markers, text, re.I):
            errors.append("PARA_5 NO LANDING: Must show emotional landing")
        
        return errors
    
    def validate_disaster_mapping(self, paragraphs: Dict[str, str]) -> Dict[str, Any]:
        """Validate that disasters are properly expanded"""
        mapping = {
            'd1_forcing': {
                'present': False,
                'retreat_impossible': ''
            },
            'd2_pivot': {
                'present': False,
                'old_tactic': '',
                'new_tactic': ''
            },
            'd3_bottleneck': {
                'present': False,
                'final_path': ''
            }
        }
        
        # Check D1
        if 'para_2_disaster_1' in paragraphs:
            text = paragraphs['para_2_disaster_1']
            if re.search(r'\b(forces?|no choice)\b', text, re.I):
                mapping['d1_forcing']['present'] = True
                # Extract why retreat impossible
                match = re.search(r'(no turning back|cannot retreat|only way).+?\.', text, re.I)
                if match:
                    mapping['d1_forcing']['retreat_impossible'] = match.group(0)
        
        # Check D2
        if 'para_3_disaster_2' in paragraphs:
            text = paragraphs['para_3_disaster_2']
            if re.search(r'\b(realizes?|discovers?|learns?)\b', text, re.I):
                mapping['d2_pivot']['present'] = True
                # Extract old/new tactics
                # This would need more sophisticated parsing
        
        # Check D3
        if 'para_4_disaster_3' in paragraphs:
            text = paragraphs['para_4_disaster_3']
            if re.search(r'\b(only|one way|final)\b', text, re.I):
                mapping['d3_bottleneck']['present'] = True
                # Extract final path
        
        return mapping
    
    def check_causality(self, paragraphs: Dict[str, str]) -> Dict[str, bool]:
        """Check causal connections between paragraphs"""
        causality = {
            'para_1_to_2': False,
            'para_2_to_3': False,
            'para_3_to_4': False,
            'para_4_to_5': False,
            'has_coincidence': False
        }
        
        # Check for coincidence markers
        coincidence_markers = r'\b(suddenly|happens to|coincidentally|by chance|randomly|out of nowhere)\b'
        
        for para_text in paragraphs.values():
            if re.search(coincidence_markers, para_text, re.I):
                causality['has_coincidence'] = True
                break
        
        # Check causal connectors
        causal_connectors = r'^(Because|As a result|Therefore|This leads|When|After|Due to|Following)'
        
        # Check connections
        if 'para_2_disaster_1' in paragraphs:
            if re.search(causal_connectors, paragraphs['para_2_disaster_1'], re.I):
                causality['para_1_to_2'] = True
        
        if 'para_3_disaster_2' in paragraphs:
            if re.search(causal_connectors, paragraphs['para_3_disaster_2'], re.I):
                causality['para_2_to_3'] = True
        
        if 'para_4_disaster_3' in paragraphs:
            if re.search(causal_connectors, paragraphs['para_4_disaster_3'], re.I):
                causality['para_3_to_4'] = True
        
        if 'para_5_resolution' in paragraphs:
            if re.search(causal_connectors, paragraphs['para_5_resolution'], re.I):
                causality['para_4_to_5'] = True
        
        return causality
    
    def check_expansion_quality(self, synopsis: str, paragraphs: Dict[str, str]) -> Dict[str, bool]:
        """Check quality of expansion from Step 2"""
        quality = {
            'maintains_spine': True,
            'adds_specificity': False,
            'observable_outcomes': False
        }
        
        # Check for specific details
        specificity_markers = r'\b(named|specific|exact|particular|[A-Z][a-z]+\'s)\b'
        if re.search(specificity_markers, synopsis):
            quality['adds_specificity'] = True
        
        # Check for observable outcomes
        if 'para_5_resolution' in paragraphs:
            observable_markers = r'\b(wins?|loses?|saves?|dies?|destroys?|builds?|escapes?)\b'
            if re.search(observable_markers, paragraphs['para_5_resolution'], re.I):
                quality['observable_outcomes'] = True
        
        return quality
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "TOO SHORT" in error:
                suggestions.append("Expand with specific details and concrete events")
            elif "TOO LONG" in error:
                suggestions.append("Trim excess description, focus on key events")
            elif "WRONG PARAGRAPH COUNT" in error:
                suggestions.append("Split or combine to exactly 5 paragraphs")
            elif "NO SITUATION" in error:
                suggestions.append("Open with clear problem/challenge/opportunity")
            elif "NO URGENCY" in error:
                suggestions.append("Add deadline or 'why now' element")
            elif "NOT FORCING" in error:
                suggestions.append("Use 'forces', 'must', 'no choice' language")
            elif "RETREAT POSSIBLE" in error:
                suggestions.append("Explain why backing out is impossible")
            elif "NO VALUES HIT" in error:
                suggestions.append("Show impact on character's beliefs/identity")
            elif "NO PIVOT" in error:
                suggestions.append("Show clear change from old to new approach")
            elif "NO BOTTLENECK" in error:
                suggestions.append("Narrow options to single path forward")
            elif "NO SHOWDOWN" in error:
                suggestions.append("Stage the final confrontation clearly")
            elif "NO OUTCOME" in error:
                suggestions.append("State concrete win/loss/escape")
            elif "COINCIDENCE FOUND" in error:
                suggestions.append("Replace 'suddenly' with causal setup")
            elif "BROKEN CHAIN" in error:
                suggestions.append("Add causal connector: Because/Therefore/As a result")
            elif "SPINE DRIFT" in error:
                suggestions.append("Return to Step 2 core story")
            elif "TOO VAGUE" in error:
                suggestions.append("Add names, places, specific actions")
            elif "THEMATIC ENDING" in error:
                suggestions.append("Make outcome concrete and observable")
            else:
                suggestions.append("Review Step 4 requirements in guide")
        
        return suggestions