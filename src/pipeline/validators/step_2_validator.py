"""
Step 2 Validator: One Paragraph Summary (Five Sentences)
Validates the five-sentence paragraph structure and moral premise according to Snowflake Method
"""

import re
from typing import Dict, Any, Tuple, List, Optional

class Step2Validator:
    """
    Validator for Step 2: One Paragraph Summary
    Enforces exact five-sentence structure with three disasters and moral premise
    """
    
    VERSION = "1.0.0"
    
    # Disaster marker patterns
    DISASTER_MARKERS = {
        'forces': r'\b(forces?|forced|forcing)\b',
        'must': r'\b(must|has to|have to)\b',
        'drives': r'\b(drives?|drove|driven)\b',
        'compels': r'\b(compels?|compelled|compelling)\b',
        'leaves_no_choice': r'\b(no choice|no option|only way)\b',
        'traps': r'\b(traps?|trapped|trapping)\b'
    }
    
    # Ending type markers
    ENDING_MARKERS = {
        'happy': r'\b(wins?|succeeds?|saves?|achieves?|reunites?|triumphs?)\b',
        'sad': r'\b(loses?|fails?|dies?|sacrifices?|destroyed?|defeated)\b',
        'bittersweet': r'\b(chooses?|walks? away|lets? go|accepts?|survives? but)\b'
    }
    
    # Moral premise patterns (flexible: can use various success/failure language)
    MORAL_PREMISE_PATTERN = r'(succeed|win|thrive|triumph|prosper|grow|flourish|achieve|overcome).+when.+(fail|lose|suffer|fall|struggle|stagnate|destroy|harm|decline).+when'
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 2 artifact
        
        Args:
            artifact: The Step 2 artifact to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        if 'paragraph' not in artifact:
            errors.append("MISSING PARAGRAPH: No paragraph field found")
            return False, errors
        
        if 'moral_premise' not in artifact:
            errors.append("MISSING MORAL PREMISE: Required moral premise statement")
            return False, errors
        
        paragraph = artifact['paragraph']
        moral_premise = artifact['moral_premise']
        
        # Parse sentences
        sentences = self.parse_sentences(paragraph)
        artifact['sentences'] = sentences
        artifact['sentence_count'] = len(sentences['all'])
        
        # RULE 1: Should have 4-6 sentences (target 5)
        if len(sentences['all']) < 4:
            errors.append(f"TOO FEW SENTENCES: Need at least 4 sentences, found {len(sentences['all'])}")
        elif len(sentences['all']) > 7:
            errors.append(f"TOO MANY SENTENCES: Maximum 7 sentences, found {len(sentences['all'])}")
        
        # RULE 2: Setup sentence (S1) requirements
        if sentences.get('setup'):
            setup_errors = self.validate_setup(sentences['setup'])
            errors.extend(setup_errors)
        else:
            errors.append("MISSING SETUP: Sentence 1 must establish time/place + lead + goal urgency")
        
        # RULE 3: Disaster 1 (S2) - Forces commitment
        if sentences.get('disaster_1'):
            d1_errors = self.validate_disaster_1(sentences['disaster_1'])
            errors.extend(d1_errors)
        else:
            errors.append("MISSING DISASTER 1: Sentence 2 must show event that FORCES commitment")
        
        # RULE 4: Disaster 2 (S3) - Moral pivot
        if sentences.get('disaster_2'):
            d2_errors = self.validate_disaster_2(sentences['disaster_2'])
            errors.extend(d2_errors)
        else:
            errors.append("MISSING DISASTER 2: Sentence 3 must show blow that drives FALSE→TRUE belief shift")
        
        # RULE 5: Disaster 3 (S4) - Forces endgame
        if sentences.get('disaster_3'):
            d3_errors = self.validate_disaster_3(sentences['disaster_3'])
            errors.extend(d3_errors)
        else:
            errors.append("MISSING DISASTER 3: Sentence 4 must force commitment to ending")
        
        # RULE 6: Resolution (S5) - Clear ending
        if sentences.get('resolution'):
            res_errors = self.validate_resolution(sentences['resolution'])
            errors.extend(res_errors)
        else:
            errors.append("MISSING RESOLUTION: Sentence 5 must show showdown + outcome")
        
        # RULE 7: Moral premise validation
        moral_errors = self.validate_moral_premise(moral_premise)
        errors.extend(moral_errors)
        
        # RULE 8: Check moral pivot in Disaster 2
        if sentences.get('disaster_2'):
            pivot_shown = self.check_moral_pivot(sentences['disaster_2'], moral_premise)
            artifact['moral_pivot'] = {
                'pivot_shown': pivot_shown,
                'false_belief': self.extract_false_belief(moral_premise),
                'true_belief': self.extract_true_belief(moral_premise)
            }
            if not pivot_shown:
                errors.append("NO MORAL PIVOT: Sentence 3 (Disaster 2) must show the character's shift from false belief to true belief. Use 'realizes', 'discovers', or 'learns' to show the pivot.")
        
        # RULE 9: Check causality
        causality_valid, causality_errors = self.validate_causality(sentences['all'])
        artifact['causality_check'] = {
            'has_coincidence': not causality_valid,
            'causal_chain': causality_valid
        }
        errors.extend(causality_errors)
        
        # RULE 10: Mark disaster presence
        artifact['disasters'] = {
            'd1_present': self.has_disaster_marker(sentences.get('disaster_1', '')),
            'd2_present': self.has_disaster_marker(sentences.get('disaster_2', '')),
            'd3_present': self.has_disaster_marker(sentences.get('disaster_3', '')),
            'd1_type': self.classify_disaster(sentences.get('disaster_1', '')),
            'd2_type': self.classify_disaster(sentences.get('disaster_2', '')),
            'd3_type': self.classify_disaster(sentences.get('disaster_3', ''))
        }
        
        if not artifact['disasters']['d1_present']:
            errors.append("D1 NOT FORCING: Disaster 1 must use forcing language")
        if not artifact['disasters']['d2_present']:
            errors.append("D2 NOT FORCING: Disaster 2 must use forcing language")
        if not artifact['disasters']['d3_present']:
            errors.append("D3 NOT FORCING: Disaster 3 must use forcing language")
        
        return len(errors) == 0, errors
    
    def parse_sentences(self, paragraph: str) -> Dict[str, Any]:
        """Parse paragraph into individual sentences"""
        # Split on sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
        
        result = {
            'all': sentences,
            'setup': sentences[0] if len(sentences) > 0 else None,
            'disaster_1': sentences[1] if len(sentences) > 1 else None,
            'disaster_2': sentences[2] if len(sentences) > 2 else None,
            'disaster_3': sentences[3] if len(sentences) > 3 else None,
            'resolution': sentences[4] if len(sentences) > 4 else None
        }
        
        return result
    
    def validate_setup(self, sentence: str) -> List[str]:
        """Validate setup sentence requirements"""
        errors = []
        
        # Check for time/place markers
        time_markers = r'\b(now|today|currently|recently|after|before|during|when)\b'
        place_markers = r'\b(in|at|from|near|within|outside|inside)\b'
        
        if not re.search(time_markers, sentence, re.I):
            errors.append("SETUP MISSING TIME: Sentence 1 needs time context")
        
        if not re.search(place_markers, sentence, re.I):
            errors.append("SETUP MISSING PLACE: Sentence 1 needs location context")
        
        # Check for urgency markers
        urgency_markers = r'\b(must|urgent|immediately|before|deadline|running out|last chance)\b'
        if not re.search(urgency_markers, sentence, re.I):
            errors.append("SETUP NO URGENCY: Sentence 1 must show why goal matters NOW")
        
        return errors
    
    def validate_disaster_1(self, sentence: str) -> List[str]:
        """Validate Disaster 1 - forces commitment"""
        errors = []
        
        # Must have forcing language
        if not self.has_disaster_marker(sentence):
            errors.append("D1 WEAK: Must use 'forces', 'must', or similar commitment language")
        
        # Check for "burn the ships" moment
        retreat_blockers = r'\b(no turning back|trapped|forced|must|no choice|only way|commits?)\b'
        if not re.search(retreat_blockers, sentence, re.I):
            errors.append("D1 ALLOWS RETREAT: Should remove option to back out")
        
        return errors
    
    def validate_disaster_2(self, sentence: str) -> List[str]:
        """Validate Disaster 2 - moral pivot"""
        errors = []
        
        # Must have forcing language
        if not self.has_disaster_marker(sentence):
            errors.append("D2 WEAK: Must show event that drives belief shift")
        
        # Check for worldview/belief language
        belief_markers = r'\b(realizes?|discovers?|learns?|understands?|sees?|reveals?|forces?.+to)\b'
        if not re.search(belief_markers, sentence, re.I):
            errors.append("D2 NO REALIZATION: Must show character discovering new truth")
        
        # Check for tactic change markers
        tactic_markers = r'\b(new|different|changes?|shifts?|abandons?|embraces?|must now)\b'
        if not re.search(tactic_markers, sentence, re.I):
            errors.append("D2 NO TACTIC CHANGE: Must indicate new approach after realization")
        
        return errors
    
    def validate_disaster_3(self, sentence: str) -> List[str]:
        """Validate Disaster 3 - forces endgame"""
        errors = []
        
        # Must have forcing language
        if not self.has_disaster_marker(sentence):
            errors.append("D3 WEAK: Must force commitment to ending")
        
        # Check for endgame/finality markers
        finality_markers = r'\b(final|last|only|no other|must end|showdown|confrontation|all or nothing)\b'
        if not re.search(finality_markers, sentence, re.I):
            errors.append("D3 NOT FINAL: Must narrow to ONE endgame path")
        
        return errors
    
    def validate_resolution(self, sentence: str) -> List[str]:
        """Validate resolution sentence"""
        errors = []
        
        # Must have clear outcome
        has_outcome = False
        outcome_type = None
        
        for ending_type, pattern in self.ENDING_MARKERS.items():
            if re.search(pattern, sentence, re.I):
                has_outcome = True
                outcome_type = ending_type
                break
        
        if not has_outcome:
            errors.append("VAGUE ENDING: Must state concrete outcome (wins/loses/chooses)")
        
        # Check for showdown/confrontation
        showdown_markers = r'\b(confronts?|faces?|battles?|fights?|challenges?|showdown)\b'
        if not re.search(showdown_markers, sentence, re.I):
            errors.append("NO SHOWDOWN: Sentence 5 should show final confrontation")
        
        return errors
    
    def validate_moral_premise(self, moral_premise: str) -> List[str]:
        """Validate moral premise format and content"""
        errors = []
        
        # Check basic structure (flexible: accept various formulations)
        has_structure = re.search(self.MORAL_PREMISE_PATTERN, moral_premise, re.I)
        has_when = 'when' in moral_premise.lower()
        has_contrast = any(w in moral_premise.lower() for w in ['but', 'while', 'whereas', 'yet', 'however', 'and fail', 'and lose', 'and suffer'])
        if not has_structure and not (has_when and has_contrast):
            errors.append("INVALID MORAL PREMISE: Must show contrast between success and failure beliefs")
        
        # Check length
        if len(moral_premise) < 20:
            errors.append("MORAL PREMISE TOO SHORT: Must be substantive statement")
        
        if len(moral_premise) > 200:
            errors.append("MORAL PREMISE TOO LONG: Keep under 200 characters")
        
        return errors
    
    def has_disaster_marker(self, sentence: str) -> bool:
        """Check if sentence has disaster/forcing language"""
        if not sentence:
            return False
        
        for marker_type, pattern in self.DISASTER_MARKERS.items():
            if re.search(pattern, sentence, re.I):
                return True
        return False
    
    def classify_disaster(self, sentence: str) -> str:
        """Classify the type of disaster"""
        if not sentence:
            return "missing"
        
        # Classify based on content
        if re.search(r'\b(betrayal|discovers?|reveals?|learns?)\b', sentence, re.I):
            return "revelation"
        elif re.search(r'\b(dies?|killed|destroyed?|lost)\b', sentence, re.I):
            return "loss"
        elif re.search(r'\b(captured|trapped|imprisoned)\b', sentence, re.I):
            return "capture"
        elif re.search(r'\b(fails?|loses?|defeated)\b', sentence, re.I):
            return "failure"
        elif re.search(r'\b(deadline|time.+running out|last chance)\b', sentence, re.I):
            return "deadline"
        else:
            return "event"
    
    def check_moral_pivot(self, disaster_2: str, moral_premise: str) -> bool:
        """Check if Disaster 2 shows the moral pivot"""
        if not disaster_2 or not moral_premise:
            return False
        
        # Extract key belief words from moral premise
        false_belief = self.extract_false_belief(moral_premise)
        true_belief = self.extract_true_belief(moral_premise)
        
        # Check if D2 references the shift
        has_false_ref = any(word in disaster_2.lower() for word in false_belief.lower().split())
        has_true_ref = any(word in disaster_2.lower() for word in true_belief.lower().split())
        has_shift_language = re.search(r'\b(realizes?|learns?|discovers?|understands?|must.+instead)\b', disaster_2, re.I)
        
        return (has_false_ref or has_true_ref) and has_shift_language is not None
    
    def extract_false_belief(self, moral_premise: str) -> str:
        """Extract false belief from moral premise"""
        match = re.search(r'fail when they (.+?)(?:\.|$)', moral_premise, re.I)
        return match.group(1) if match else ""
    
    def extract_true_belief(self, moral_premise: str) -> str:
        """Extract true belief from moral premise"""
        match = re.search(r'succeed when they (.+?),', moral_premise, re.I)
        return match.group(1) if match else ""
    
    def validate_causality(self, sentences: List[str]) -> Tuple[bool, List[str]]:
        """Check for causal chain vs coincidence"""
        errors = []
        
        if len(sentences) < 5:
            return False, ["INCOMPLETE PARAGRAPH: Cannot verify causality"]
        
        # Check for coincidence markers
        coincidence_markers = r'\b(suddenly|happens to|coincidentally|by chance|randomly|out of nowhere)\b'
        
        for i, sentence in enumerate(sentences):
            if re.search(coincidence_markers, sentence, re.I):
                errors.append(f"COINCIDENCE IN S{i+1}: Convert to causality or delete")
        
        # Check for causal connectors between sentences
        causal_connectors = r'^(Because|As a result|Therefore|This forces|When|After|Despite)'
        has_connectors = sum(1 for s in sentences[1:] if re.search(causal_connectors, s, re.I))
        
        if has_connectors < 1:
            errors.append("WEAK CAUSALITY: Disasters should causally connect")
        
        return len(errors) == 0, errors
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "WRONG SENTENCE COUNT" in error:
                suggestions.append("Split or combine to exactly 5 sentences")
            elif "SETUP MISSING TIME" in error:
                suggestions.append("Add 'Now', 'Today', or specific time reference")
            elif "SETUP MISSING PLACE" in error:
                suggestions.append("Add 'In [city]' or location marker")
            elif "SETUP NO URGENCY" in error:
                suggestions.append("Add deadline or 'must' language")
            elif "D1 WEAK" in error:
                suggestions.append("Use 'forces her to' or 'leaves no choice but'")
            elif "D1 ALLOWS RETREAT" in error:
                suggestions.append("Make backing out impossible/catastrophic")
            elif "D2 NO REALIZATION" in error:
                suggestions.append("Add 'realizes', 'discovers', or 'learns'")
            elif "D2 NO TACTIC CHANGE" in error:
                suggestions.append("Show new approach: 'must now [new tactic]'")
            elif "D3 NOT FINAL" in error:
                suggestions.append("Add 'final confrontation' or 'only way to end'")
            elif "VAGUE ENDING" in error:
                suggestions.append("State concrete outcome: wins/loses/sacrifices")
            elif "NO SHOWDOWN" in error:
                suggestions.append("Add confrontation: 'faces', 'battles', 'confronts'")
            elif "INVALID MORAL PREMISE" in error:
                suggestions.append("Format: 'People succeed when they [true], and fail when they [false].'")
            elif "NO MORAL PIVOT" in error:
                suggestions.append("Sentence 3 must show character shifting from false to true belief")
            elif "COINCIDENCE" in error:
                suggestions.append("Replace 'suddenly' with causal connector: 'Because of D1...'")
            elif "WEAK CAUSALITY" in error:
                suggestions.append("Start sentences 2-5 with: Because/Therefore/This forces/As a result")
            else:
                suggestions.append("Review Step 2 requirements in guide")
        
        return suggestions