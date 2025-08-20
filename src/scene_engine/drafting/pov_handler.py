"""
POV and Tense Handler

TaskMaster Task 44.4: Implement POV and Tense Handling Logic
Ensures generated prose consistently applies specified POV and tense from Scene Cards.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
import re
import logging


class POVType(Enum):
    """Point of view types"""
    FIRST_PERSON = "first_person"
    THIRD_LIMITED = "third_limited" 
    THIRD_OMNISCIENT = "third_omniscient"


class TenseType(Enum):
    """Tense types"""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class POVHandler:
    """
    TaskMaster Task 44.4: POV and Tense Handling Logic
    
    Ensures generated prose consistently applies the specified POV and tense.
    Supports multiple POV types (first, third limited, third omniscient) and tenses.
    Validates consistency and provides correction capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("POVHandler")
        
        # POV patterns for detection and validation
        self.pov_patterns = {
            POVType.FIRST_PERSON: {
                'pronouns': ['I', 'me', 'my', 'mine', 'myself'],
                'verbs': ['am', 'was', 'will be'],
                'indicators': ['I ', 'my ', 'me ']
            },
            POVType.THIRD_LIMITED: {
                'pronouns': ['he', 'she', 'they', 'him', 'her', 'them', 'his', 'hers', 'their'],
                'verbs': ['is', 'was', 'will be'],
                'indicators': ['he ', 'she ', 'they ', 'his ', 'her ', 'their ']
            },
            POVType.THIRD_OMNISCIENT: {
                'pronouns': ['he', 'she', 'they', 'him', 'her', 'them', 'his', 'hers', 'their'],
                'verbs': ['is', 'was', 'will be'],
                'indicators': ['everyone ', 'all of them ', 'each person ']
            }
        }
        
        # Tense conversion patterns
        self.tense_patterns = {
            TenseType.PAST: {
                'be_verbs': {'am': 'was', 'is': 'was', 'are': 'were', 'will be': 'was'},
                'regular_endings': {'s': 'ed', 'es': 'ed'},
                'irregular_verbs': {
                    'go': 'went', 'come': 'came', 'see': 'saw', 'know': 'knew',
                    'take': 'took', 'get': 'got', 'give': 'gave', 'find': 'found',
                    'think': 'thought', 'say': 'said', 'feel': 'felt', 'make': 'made'
                }
            },
            TenseType.PRESENT: {
                'be_verbs': {'was': 'is', 'were': 'are', 'will be': 'is'},
                'regular_endings': {'ed': 's'},
                'irregular_verbs': {
                    'went': 'go', 'came': 'come', 'saw': 'see', 'knew': 'know',
                    'took': 'take', 'got': 'get', 'gave': 'give', 'found': 'find',
                    'thought': 'think', 'said': 'say', 'felt': 'feel', 'made': 'make'
                }
            },
            TenseType.FUTURE: {
                'be_verbs': {'am': 'will be', 'is': 'will be', 'are': 'will be', 'was': 'will be', 'were': 'will be'},
                'regular_verbs': lambda verb: f'will {verb}',
                'irregular_verbs': {
                    'go': 'will go', 'come': 'will come', 'see': 'will see',
                    'know': 'will know', 'take': 'will take', 'get': 'will get'
                }
            }
        }
    
    def process_prose(self, prose: str, pov_type: POVType, tense_type: TenseType) -> str:
        """
        Process prose to ensure consistent POV and tense application
        
        Args:
            prose: Raw prose text to process
            pov_type: Target POV type
            tense_type: Target tense type
            
        Returns:
            Processed prose with consistent POV and tense
        """
        
        self.logger.debug(f"Processing prose for {pov_type.value} POV and {tense_type.value} tense")
        
        # Split into sentences for processing
        sentences = self._split_sentences(prose)
        processed_sentences = []
        
        for sentence in sentences:
            # Apply POV conversion
            pov_corrected = self._apply_pov_conversion(sentence, pov_type)
            
            # Apply tense conversion
            tense_corrected = self._apply_tense_conversion(pov_corrected, tense_type)
            
            processed_sentences.append(tense_corrected)
        
        return " ".join(processed_sentences)
    
    def validate_consistency(self, prose: str, expected_pov: POVType) -> bool:
        """
        Validate POV consistency throughout prose
        
        Args:
            prose: Prose text to validate
            expected_pov: Expected POV type
            
        Returns:
            True if POV is consistent, False otherwise
        """
        
        sentences = self._split_sentences(prose)
        inconsistencies = 0
        
        for sentence in sentences:
            detected_pov = self._detect_pov(sentence)
            if detected_pov and detected_pov != expected_pov:
                inconsistencies += 1
                self.logger.warning(f"POV inconsistency detected: expected {expected_pov.value}, found {detected_pov.value} in: {sentence[:50]}...")
        
        # Allow up to 10% inconsistencies (for dialogue, quotes, etc.)
        consistency_threshold = 0.9
        consistency_rate = 1.0 - (inconsistencies / len(sentences)) if sentences else 1.0
        
        return consistency_rate >= consistency_threshold
    
    def validate_tense_consistency(self, prose: str, expected_tense: TenseType) -> bool:
        """
        Validate tense consistency throughout prose
        
        Args:
            prose: Prose text to validate
            expected_tense: Expected tense type
            
        Returns:
            True if tense is consistent, False otherwise
        """
        
        sentences = self._split_sentences(prose)
        inconsistencies = 0
        
        for sentence in sentences:
            detected_tense = self._detect_tense(sentence)
            if detected_tense and detected_tense != expected_tense:
                inconsistencies += 1
                self.logger.warning(f"Tense inconsistency detected: expected {expected_tense.value}, found {detected_tense.value} in: {sentence[:50]}...")
        
        # Allow up to 15% inconsistencies (for dialogue, complex sentences, etc.)
        consistency_threshold = 0.85
        consistency_rate = 1.0 - (inconsistencies / len(sentences)) if sentences else 1.0
        
        return consistency_rate >= consistency_threshold
    
    def _split_sentences(self, prose: str) -> List[str]:
        """Split prose into sentences for processing"""
        
        # Simple sentence splitting (could be enhanced with more sophisticated NLP)
        sentences = re.split(r'[.!?]+\s+', prose)
        return [s.strip() for s in sentences if s.strip()]
    
    def _apply_pov_conversion(self, sentence: str, target_pov: POVType) -> str:
        """Convert sentence to target POV"""
        
        current_pov = self._detect_pov(sentence)
        if not current_pov or current_pov == target_pov:
            return sentence
        
        converted = sentence
        
        # Convert from first person to third person
        if current_pov == POVType.FIRST_PERSON and target_pov in [POVType.THIRD_LIMITED, POVType.THIRD_OMNISCIENT]:
            converted = self._convert_first_to_third(converted)
        
        # Convert from third person to first person
        elif current_pov in [POVType.THIRD_LIMITED, POVType.THIRD_OMNISCIENT] and target_pov == POVType.FIRST_PERSON:
            converted = self._convert_third_to_first(converted)
        
        return converted
    
    def _apply_tense_conversion(self, sentence: str, target_tense: TenseType) -> str:
        """Convert sentence to target tense"""
        
        current_tense = self._detect_tense(sentence)
        if not current_tense or current_tense == target_tense:
            return sentence
        
        converted = sentence
        patterns = self.tense_patterns.get(target_tense, {})
        
        # Convert be verbs
        be_verbs = patterns.get('be_verbs', {})
        for old_verb, new_verb in be_verbs.items():
            converted = re.sub(r'\b' + old_verb + r'\b', new_verb, converted, flags=re.IGNORECASE)
        
        # Convert irregular verbs
        irregular_verbs = patterns.get('irregular_verbs', {})
        for old_verb, new_verb in irregular_verbs.items():
            converted = re.sub(r'\b' + old_verb + r'\b', new_verb, converted, flags=re.IGNORECASE)
        
        return converted
    
    def _detect_pov(self, sentence: str) -> Optional[POVType]:
        """Detect POV type in a sentence"""
        
        sentence_lower = sentence.lower()
        
        # Check for first person indicators
        first_person_count = sum(1 for indicator in self.pov_patterns[POVType.FIRST_PERSON]['indicators'] 
                                if indicator.lower() in sentence_lower)
        
        # Check for third person indicators  
        third_person_count = sum(1 for indicator in self.pov_patterns[POVType.THIRD_LIMITED]['indicators']
                                if indicator.lower() in sentence_lower)
        
        # Check for omniscient indicators
        omniscient_count = sum(1 for indicator in self.pov_patterns[POVType.THIRD_OMNISCIENT]['indicators']
                              if indicator.lower() in sentence_lower)
        
        if first_person_count > 0:
            return POVType.FIRST_PERSON
        elif omniscient_count > 0:
            return POVType.THIRD_OMNISCIENT
        elif third_person_count > 0:
            return POVType.THIRD_LIMITED
        
        return None
    
    def _detect_tense(self, sentence: str) -> Optional[TenseType]:
        """Detect primary tense in a sentence"""
        
        sentence_lower = sentence.lower()
        
        # Count tense indicators
        past_indicators = ['was', 'were', 'had', 'did', 'went', 'came', 'saw', 'ed ']
        present_indicators = ['am', 'is', 'are', 'do', 'does', 'go', 'come', 'see']
        future_indicators = ['will', 'shall', 'going to', 'will be']
        
        past_count = sum(1 for indicator in past_indicators if indicator in sentence_lower)
        present_count = sum(1 for indicator in present_indicators if indicator in sentence_lower) 
        future_count = sum(1 for indicator in future_indicators if indicator in sentence_lower)
        
        if future_count > 0:
            return TenseType.FUTURE
        elif past_count > present_count:
            return TenseType.PAST
        elif present_count > 0:
            return TenseType.PRESENT
        
        return None
    
    def _convert_first_to_third(self, sentence: str) -> str:
        """Convert first person sentence to third person"""
        
        # Simple conversion patterns
        conversions = {
            r'\bI\b': 'they',
            r'\bme\b': 'them', 
            r'\bmy\b': 'their',
            r'\bmine\b': 'theirs',
            r'\bmyself\b': 'themselves',
            r'\bI\'m\b': 'they are',
            r'\bI\'ve\b': 'they have',
            r'\bI\'d\b': 'they would',
            r'\bI\'ll\b': 'they will'
        }
        
        converted = sentence
        for pattern, replacement in conversions.items():
            converted = re.sub(pattern, replacement, converted, flags=re.IGNORECASE)
        
        # Fix capitalization at sentence start
        if converted and converted[0].islower():
            converted = converted[0].upper() + converted[1:]
        
        return converted
    
    def _convert_third_to_first(self, sentence: str) -> str:
        """Convert third person sentence to first person"""
        
        # Simple conversion patterns (assuming single character focus)
        conversions = {
            r'\bthey\b': 'I',
            r'\bthem\b': 'me',
            r'\btheir\b': 'my', 
            r'\btheirs\b': 'mine',
            r'\bthemselves\b': 'myself',
            r'\bthey are\b': 'I am',
            r'\bthey have\b': 'I have',
            r'\bthey would\b': 'I would',
            r'\bthey will\b': 'I will'
        }
        
        converted = sentence
        for pattern, replacement in conversions.items():
            converted = re.sub(pattern, replacement, converted, flags=re.IGNORECASE)
        
        # Fix capitalization
        if converted and converted[0].islower() and converted.startswith('i '):
            converted = 'I' + converted[1:]
        
        return converted
    
    def get_pov_statistics(self, prose: str) -> Dict[str, Any]:
        """Get POV usage statistics for prose"""
        
        sentences = self._split_sentences(prose)
        pov_counts = {pov.value: 0 for pov in POVType}
        
        for sentence in sentences:
            detected_pov = self._detect_pov(sentence)
            if detected_pov:
                pov_counts[detected_pov.value] += 1
        
        total_sentences = len(sentences)
        pov_percentages = {pov: (count / total_sentences * 100) if total_sentences > 0 else 0 
                          for pov, count in pov_counts.items()}
        
        return {
            'total_sentences': total_sentences,
            'pov_counts': pov_counts,
            'pov_percentages': pov_percentages,
            'dominant_pov': max(pov_counts, key=pov_counts.get) if any(pov_counts.values()) else None
        }
    
    def get_tense_statistics(self, prose: str) -> Dict[str, Any]:
        """Get tense usage statistics for prose"""
        
        sentences = self._split_sentences(prose)
        tense_counts = {tense.value: 0 for tense in TenseType}
        
        for sentence in sentences:
            detected_tense = self._detect_tense(sentence)
            if detected_tense:
                tense_counts[detected_tense.value] += 1
        
        total_sentences = len(sentences)
        tense_percentages = {tense: (count / total_sentences * 100) if total_sentences > 0 else 0
                           for tense, count in tense_counts.items()}
        
        return {
            'total_sentences': total_sentences,
            'tense_counts': tense_counts,
            'tense_percentages': tense_percentages,
            'dominant_tense': max(tense_counts, key=tense_counts.get) if any(tense_counts.values()) else None
        }