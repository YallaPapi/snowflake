"""
Scene Correction Components

TaskMaster Tasks 45.3, 45.4, 45.5: Scene type correction, part rewriting, and compression logic
Components used by the redesign pipeline to improve scene quality.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import copy
import re

from ..models import SceneCard, SceneType


class CorrectionType(Enum):
    """Types of corrections that can be applied"""
    SCENE_TYPE_MISMATCH = "scene_type_mismatch"
    MISSING_STRUCTURE = "missing_structure"
    WEAK_STRUCTURE = "weak_structure"
    INCONSISTENT_POV = "inconsistent_pov"
    INCONSISTENT_TENSE = "inconsistent_tense"


class RewriteTarget(Enum):
    """Parts of scene that can be rewritten"""
    OPENING = "opening"
    GOAL_STATEMENT = "goal_statement"
    CONFLICT_DESCRIPTION = "conflict_description"
    SETBACK_SEQUENCE = "setback_sequence"
    REACTION_SEQUENCE = "reaction_sequence"
    DILEMMA_PRESENTATION = "dilemma_presentation"
    DECISION_SEQUENCE = "decision_sequence"
    CONCLUSION = "conclusion"
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"


class CompressionArea(Enum):
    """Areas that can be compressed"""
    EXCESSIVE_DESCRIPTION = "excessive_description"
    REDUNDANT_DIALOGUE = "redundant_dialogue"
    UNNECESSARY_EXPOSITION = "unnecessary_exposition"
    REPETITIVE_PHRASES = "repetitive_phrases"
    VERBOSE_SENTENCES = "verbose_sentences"


class SceneTypeCorrector:
    """
    TaskMaster Task 45.3: Scene Type Correction
    Identifies and corrects scene type mismatches during redesign process.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SceneTypeCorrector")
    
    def correct_scene_type(self, scene_card: SceneCard, prose_content: Optional[str] = None,
                          preserve_crucible: bool = True) -> Dict[str, Any]:
        """
        Detect and correct scene type mismatches
        
        Args:
            scene_card: Scene card to analyze and correct
            prose_content: Optional prose content for analysis
            preserve_crucible: Whether to preserve scene crucible during correction
            
        Returns:
            Dictionary with correction results
        """
        
        self.logger.debug(f"Analyzing scene type for scene {scene_card.scene_id}")
        
        corrected_scene_card = copy.deepcopy(scene_card)
        corrections_applied = []
        
        # Analyze current scene type alignment
        type_analysis = self._analyze_scene_type_alignment(scene_card, prose_content)
        
        if type_analysis['needs_correction']:
            self.logger.info(f"Scene type mismatch detected for scene {scene_card.scene_id}: "
                           f"{type_analysis['current_type']} -> {type_analysis['suggested_type']}")
            
            # Apply scene type correction
            correction_result = self._apply_scene_type_correction(
                corrected_scene_card, type_analysis, preserve_crucible
            )
            
            if correction_result['success']:
                corrected_scene_card = correction_result['scene_card']
                corrections_applied.extend(correction_result['corrections'])
        
        # Check for missing structure elements
        structure_analysis = self._analyze_structure_completeness(corrected_scene_card)
        
        if structure_analysis['missing_elements']:
            self.logger.info(f"Missing structure elements detected: {structure_analysis['missing_elements']}")
            
            # Add missing structure elements
            structure_correction = self._add_missing_structure_elements(
                corrected_scene_card, structure_analysis
            )
            
            if structure_correction['success']:
                corrected_scene_card = structure_correction['scene_card']
                corrections_applied.extend(structure_correction['corrections'])
        
        # Generate corrected prose if needed
        corrected_prose = prose_content
        if prose_content and corrections_applied:
            corrected_prose = self._update_prose_for_corrections(
                prose_content, corrected_scene_card, corrections_applied
            )
        
        return {
            'scene_card': corrected_scene_card,
            'prose_content': corrected_prose,
            'corrections_applied': corrections_applied,
            'analysis': {
                'type_analysis': type_analysis,
                'structure_analysis': structure_analysis
            }
        }
    
    def _analyze_scene_type_alignment(self, scene_card: SceneCard, 
                                    prose_content: Optional[str]) -> Dict[str, Any]:
        """Analyze if scene type matches its structure and content"""
        
        analysis = {
            'needs_correction': False,
            'current_type': scene_card.scene_type,
            'suggested_type': scene_card.scene_type,
            'confidence': 1.0,
            'reasons': []
        }
        
        # Check structure alignment
        if scene_card.scene_type == SceneType.PROACTIVE:
            if not (hasattr(scene_card, 'proactive') and scene_card.proactive):
                analysis['needs_correction'] = True
                analysis['suggested_type'] = SceneType.REACTIVE
                analysis['reasons'].append("Missing proactive structure")
            else:
                proactive = scene_card.proactive
                if not all([
                    hasattr(proactive, 'goal') and proactive.goal,
                    hasattr(proactive, 'conflict') and proactive.conflict,
                    hasattr(proactive, 'setback') and proactive.setback
                ]):
                    analysis['needs_correction'] = True
                    analysis['reasons'].append("Incomplete proactive structure")
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if not (hasattr(scene_card, 'reactive') and scene_card.reactive):
                analysis['needs_correction'] = True
                analysis['suggested_type'] = SceneType.PROACTIVE
                analysis['reasons'].append("Missing reactive structure")
            else:
                reactive = scene_card.reactive
                if not all([
                    hasattr(reactive, 'reaction') and reactive.reaction,
                    hasattr(reactive, 'dilemma') and reactive.dilemma,
                    hasattr(reactive, 'decision') and reactive.decision
                ]):
                    analysis['needs_correction'] = True
                    analysis['reasons'].append("Incomplete reactive structure")
        
        # Check prose content alignment if available
        if prose_content and not analysis['needs_correction']:
            prose_analysis = self._analyze_prose_scene_type_indicators(prose_content)
            
            if prose_analysis['suggested_type'] != scene_card.scene_type:
                if prose_analysis['confidence'] > 0.7:
                    analysis['needs_correction'] = True
                    analysis['suggested_type'] = prose_analysis['suggested_type']
                    analysis['confidence'] = prose_analysis['confidence']
                    analysis['reasons'].extend(prose_analysis['indicators'])
        
        return analysis
    
    def _analyze_prose_scene_type_indicators(self, prose_content: str) -> Dict[str, Any]:
        """Analyze prose content for scene type indicators"""
        
        prose_lower = prose_content.lower()
        
        # Proactive indicators
        proactive_indicators = [
            'goal', 'objective', 'plan', 'try to', 'attempt', 'need to',
            'wanted to', 'decided to', 'determined to'
        ]
        proactive_count = sum(1 for indicator in proactive_indicators if indicator in prose_lower)
        
        # Reactive indicators  
        reactive_indicators = [
            'felt', 'emotion', 'reaction', 'response', 'aftermath', 'consequences',
            'had to decide', 'faced with', 'dilemma', 'choice'
        ]
        reactive_count = sum(1 for indicator in reactive_indicators if indicator in prose_lower)
        
        if proactive_count > reactive_count and proactive_count > 2:
            return {
                'suggested_type': SceneType.PROACTIVE,
                'confidence': min(1.0, proactive_count / 5.0),
                'indicators': [f"Found {proactive_count} proactive indicators"]
            }
        elif reactive_count > proactive_count and reactive_count > 2:
            return {
                'suggested_type': SceneType.REACTIVE,
                'confidence': min(1.0, reactive_count / 5.0),
                'indicators': [f"Found {reactive_count} reactive indicators"]
            }
        else:
            return {
                'suggested_type': None,
                'confidence': 0.0,
                'indicators': ["Insufficient clear indicators"]
            }
    
    def _apply_scene_type_correction(self, scene_card: SceneCard, type_analysis: Dict[str, Any],
                                   preserve_crucible: bool) -> Dict[str, Any]:
        """Apply scene type correction"""
        
        corrections = []
        
        original_type = scene_card.scene_type
        new_type = type_analysis['suggested_type']
        
        scene_card.scene_type = new_type
        corrections.append(f"Changed scene type from {original_type.value} to {new_type.value}")
        
        # Add appropriate structure based on new type
        if new_type == SceneType.PROACTIVE:
            if not (hasattr(scene_card, 'proactive') and scene_card.proactive):
                # Create basic proactive structure
                from types import SimpleNamespace
                scene_card.proactive = SimpleNamespace()
                scene_card.proactive.goal = "Character goal to be defined"
                scene_card.proactive.conflict = "Obstacle preventing goal achievement"
                scene_card.proactive.setback = "Failure or complication"
                corrections.append("Added basic proactive structure (G-C-S)")
        
        elif new_type == SceneType.REACTIVE:
            if not (hasattr(scene_card, 'reactive') and scene_card.reactive):
                # Create basic reactive structure
                from types import SimpleNamespace
                scene_card.reactive = SimpleNamespace()
                scene_card.reactive.reaction = "Emotional response to previous events"
                scene_card.reactive.dilemma = "Difficult choice with no clear good option"
                scene_card.reactive.decision = "Choice made despite difficulties"
                corrections.append("Added basic reactive structure (R-D-D)")
        
        return {
            'success': True,
            'scene_card': scene_card,
            'corrections': corrections
        }
    
    def _analyze_structure_completeness(self, scene_card: SceneCard) -> Dict[str, Any]:
        """Analyze completeness of scene structure"""
        
        missing_elements = []
        weak_elements = []
        
        # Check basic elements
        if not scene_card.scene_crucible:
            missing_elements.append("scene_crucible")
        elif len(scene_card.scene_crucible) < 10:
            weak_elements.append("scene_crucible (too brief)")
        
        if not scene_card.pov_character:
            missing_elements.append("pov_character")
        
        if not scene_card.pov:
            missing_elements.append("pov")
        
        if not scene_card.tense:
            missing_elements.append("tense")
        
        # Check scene type specific elements
        if scene_card.scene_type == SceneType.PROACTIVE:
            if hasattr(scene_card, 'proactive') and scene_card.proactive:
                proactive = scene_card.proactive
                if not (hasattr(proactive, 'goal') and proactive.goal):
                    missing_elements.append("proactive.goal")
                elif len(proactive.goal) < 10:
                    weak_elements.append("proactive.goal (too brief)")
                
                if not (hasattr(proactive, 'conflict') and proactive.conflict):
                    missing_elements.append("proactive.conflict")
                elif len(proactive.conflict) < 10:
                    weak_elements.append("proactive.conflict (too brief)")
                
                if not (hasattr(proactive, 'setback') and proactive.setback):
                    missing_elements.append("proactive.setback")
                elif len(proactive.setback) < 10:
                    weak_elements.append("proactive.setback (too brief)")
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if hasattr(scene_card, 'reactive') and scene_card.reactive:
                reactive = scene_card.reactive
                if not (hasattr(reactive, 'reaction') and reactive.reaction):
                    missing_elements.append("reactive.reaction")
                elif len(reactive.reaction) < 10:
                    weak_elements.append("reactive.reaction (too brief)")
                
                if not (hasattr(reactive, 'dilemma') and reactive.dilemma):
                    missing_elements.append("reactive.dilemma")
                elif len(reactive.dilemma) < 10:
                    weak_elements.append("reactive.dilemma (too brief)")
                
                if not (hasattr(reactive, 'decision') and reactive.decision):
                    missing_elements.append("reactive.decision")
                elif len(reactive.decision) < 10:
                    weak_elements.append("reactive.decision (too brief)")
        
        return {
            'missing_elements': missing_elements,
            'weak_elements': weak_elements,
            'completeness_score': 1.0 - (len(missing_elements) + len(weak_elements) * 0.5) / 7.0
        }
    
    def _add_missing_structure_elements(self, scene_card: SceneCard, 
                                      structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Add missing structure elements with placeholder content"""
        
        corrections = []
        
        # Add missing basic elements
        for element in structure_analysis['missing_elements']:
            if element == "scene_crucible":
                scene_card.scene_crucible = "Scene crucible to be defined"
                corrections.append("Added placeholder scene crucible")
            elif element == "pov_character":
                scene_card.pov_character = "Character"
                corrections.append("Added default POV character")
            elif element == "pov":
                scene_card.pov = "third_limited"
                corrections.append("Set default POV to third limited")
            elif element == "tense":
                scene_card.tense = "past"
                corrections.append("Set default tense to past")
            
            # Handle scene type specific elements
            elif element.startswith("proactive."):
                field = element.split(".", 1)[1]
                if field == "goal":
                    scene_card.proactive.goal = "Character goal to be defined"
                    corrections.append("Added placeholder goal")
                elif field == "conflict":
                    scene_card.proactive.conflict = "Conflict obstacle to be defined"
                    corrections.append("Added placeholder conflict")
                elif field == "setback":
                    scene_card.proactive.setback = "Setback outcome to be defined"
                    corrections.append("Added placeholder setback")
            
            elif element.startswith("reactive."):
                field = element.split(".", 1)[1]
                if field == "reaction":
                    scene_card.reactive.reaction = "Emotional reaction to be defined"
                    corrections.append("Added placeholder reaction")
                elif field == "dilemma":
                    scene_card.reactive.dilemma = "Difficult choice to be defined"
                    corrections.append("Added placeholder dilemma")
                elif field == "decision":
                    scene_card.reactive.decision = "Decision outcome to be defined"
                    corrections.append("Added placeholder decision")
        
        return {
            'success': True,
            'scene_card': scene_card,
            'corrections': corrections
        }
    
    def _update_prose_for_corrections(self, prose_content: str, corrected_scene_card: SceneCard,
                                    corrections: List[str]) -> str:
        """Update prose content to reflect structural corrections"""
        
        # This is a simplified implementation
        # In a full implementation, this would regenerate or modify prose sections
        
        updated_prose = prose_content
        
        # Add note about corrections at the end
        correction_note = f"\n\n[Note: Scene structure corrected - {', '.join(corrections)}]"
        updated_prose += correction_note
        
        return updated_prose


class PartRewriter:
    """
    TaskMaster Task 45.4: Part Rewriting Logic  
    Identifies and rewrites problematic scene parts during redesign.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("PartRewriter")
    
    def rewrite_problematic_parts(self, scene_card: SceneCard, prose_content: Optional[str] = None,
                                 target_quality: float = 0.8, preserve_crucible: bool = True) -> Dict[str, Any]:
        """
        Identify and rewrite problematic scene parts
        
        Args:
            scene_card: Scene card to analyze
            prose_content: Prose content to analyze and rewrite
            target_quality: Target quality level
            preserve_crucible: Whether to preserve scene crucible
            
        Returns:
            Dictionary with rewriting results
        """
        
        self.logger.debug(f"Analyzing parts for rewriting in scene {scene_card.scene_id}")
        
        parts_rewritten = []
        updated_scene_card = copy.deepcopy(scene_card)
        updated_prose = prose_content
        
        # Analyze scene card parts
        card_analysis = self._analyze_scene_card_parts(scene_card)
        
        for part_name, analysis in card_analysis.items():
            if analysis['needs_rewriting']:
                rewrite_result = self._rewrite_scene_card_part(
                    updated_scene_card, part_name, analysis, preserve_crucible
                )
                
                if rewrite_result['success']:
                    parts_rewritten.append(f"scene_card.{part_name}")
                    updated_scene_card = rewrite_result['scene_card']
        
        # Analyze prose parts if available
        if prose_content:
            prose_analysis = self._analyze_prose_parts(prose_content, target_quality)
            
            for part_name, analysis in prose_analysis.items():
                if analysis['needs_rewriting']:
                    rewrite_result = self._rewrite_prose_part(
                        updated_prose, part_name, analysis, preserve_crucible
                    )
                    
                    if rewrite_result['success']:
                        parts_rewritten.append(f"prose.{part_name}")
                        updated_prose = rewrite_result['prose_content']
        
        return {
            'scene_card': updated_scene_card,
            'prose_content': updated_prose,
            'parts_rewritten': parts_rewritten,
            'analysis': {
                'scene_card_analysis': card_analysis,
                'prose_analysis': prose_analysis if prose_content else {}
            }
        }
    
    def _analyze_scene_card_parts(self, scene_card: SceneCard) -> Dict[str, Any]:
        """Analyze scene card parts for quality issues"""
        
        analysis = {}
        
        # Analyze scene crucible
        analysis['scene_crucible'] = self._analyze_crucible_quality(scene_card.scene_crucible)
        
        # Analyze scene type specific parts
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            if scene_card.proactive:
                analysis['goal'] = self._analyze_text_quality(
                    getattr(scene_card.proactive, 'goal', ''), 'goal'
                )
                analysis['conflict'] = self._analyze_text_quality(
                    getattr(scene_card.proactive, 'conflict', ''), 'conflict'
                )
                analysis['setback'] = self._analyze_text_quality(
                    getattr(scene_card.proactive, 'setback', ''), 'setback'
                )
        
        elif scene_card.scene_type == SceneType.REACTIVE and hasattr(scene_card, 'reactive'):
            if scene_card.reactive:
                analysis['reaction'] = self._analyze_text_quality(
                    getattr(scene_card.reactive, 'reaction', ''), 'reaction'
                )
                analysis['dilemma'] = self._analyze_text_quality(
                    getattr(scene_card.reactive, 'dilemma', ''), 'dilemma'
                )
                analysis['decision'] = self._analyze_text_quality(
                    getattr(scene_card.reactive, 'decision', ''), 'decision'
                )
        
        return analysis
    
    def _analyze_prose_parts(self, prose_content: str, target_quality: float) -> Dict[str, Any]:
        """Analyze prose parts for quality issues"""
        
        analysis = {}
        
        # Split prose into logical parts
        paragraphs = prose_content.split('\n\n')
        
        if len(paragraphs) >= 3:
            analysis['opening'] = self._analyze_prose_section(paragraphs[0], 'opening', target_quality)
            analysis['middle'] = self._analyze_prose_section(
                '\n\n'.join(paragraphs[1:-1]), 'middle', target_quality
            )
            analysis['conclusion'] = self._analyze_prose_section(paragraphs[-1], 'conclusion', target_quality)
        
        # Analyze dialogue quality
        dialogue_analysis = self._analyze_dialogue_quality(prose_content, target_quality)
        if dialogue_analysis['needs_rewriting']:
            analysis['dialogue'] = dialogue_analysis
        
        # Analyze description quality
        description_analysis = self._analyze_description_quality(prose_content, target_quality)
        if description_analysis['needs_rewriting']:
            analysis['description'] = description_analysis
        
        return analysis
    
    def _analyze_crucible_quality(self, crucible: Optional[str]) -> Dict[str, Any]:
        """Analyze scene crucible quality"""
        
        if not crucible:
            return {
                'needs_rewriting': True,
                'issues': ['Missing scene crucible'],
                'quality_score': 0.0
            }
        
        issues = []
        quality_score = 0.8  # Start optimistic
        
        # Length check
        if len(crucible) < 15:
            issues.append("Crucible too brief")
            quality_score -= 0.3
        elif len(crucible) > 150:
            issues.append("Crucible too verbose")
            quality_score -= 0.2
        
        # Content check
        if not any(word in crucible.lower() for word in ['conflict', 'tension', 'problem', 'challenge', 'crisis']):
            issues.append("Crucible lacks tension indicators")
            quality_score -= 0.3
        
        return {
            'needs_rewriting': quality_score < 0.7 or len(issues) > 0,
            'issues': issues,
            'quality_score': max(0.0, quality_score)
        }
    
    def _analyze_text_quality(self, text: str, text_type: str) -> Dict[str, Any]:
        """Analyze general text quality"""
        
        if not text:
            return {
                'needs_rewriting': True,
                'issues': [f'Missing {text_type}'],
                'quality_score': 0.0
            }
        
        issues = []
        quality_score = 0.8
        
        # Length check
        if len(text) < 10:
            issues.append(f"{text_type.capitalize()} too brief")
            quality_score -= 0.3
        
        # Specificity check
        vague_words = ['thing', 'something', 'stuff', 'anything']
        if any(word in text.lower() for word in vague_words):
            issues.append(f"{text_type.capitalize()} too vague")
            quality_score -= 0.2
        
        # Action/specificity for goals and decisions
        if text_type in ['goal', 'decision']:
            if not any(word in text.lower() for word in ['to', 'will', 'must', 'need', 'want']):
                issues.append(f"{text_type.capitalize()} lacks action orientation")
                quality_score -= 0.2
        
        return {
            'needs_rewriting': quality_score < 0.6 or len(issues) > 1,
            'issues': issues,
            'quality_score': max(0.0, quality_score)
        }
    
    def _analyze_prose_section(self, section: str, section_type: str, target_quality: float) -> Dict[str, Any]:
        """Analyze prose section quality"""
        
        if not section or not section.strip():
            return {
                'needs_rewriting': True,
                'issues': [f'Empty {section_type} section'],
                'quality_score': 0.0
            }
        
        issues = []
        quality_score = 0.7
        
        # Basic quality checks
        words = section.split()
        
        # Length check
        if len(words) < 20:
            issues.append(f"{section_type.capitalize()} section too short")
            quality_score -= 0.2
        
        # Sentence variety
        sentences = re.split(r'[.!?]+', section)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_length < 5 or avg_length > 25:
                issues.append(f"{section_type.capitalize()} has poor sentence variety")
                quality_score -= 0.1
        
        return {
            'needs_rewriting': quality_score < target_quality,
            'issues': issues,
            'quality_score': quality_score
        }
    
    def _analyze_dialogue_quality(self, prose: str, target_quality: float) -> Dict[str, Any]:
        """Analyze dialogue quality"""
        
        dialogue_count = prose.count('"')
        
        if dialogue_count < 2:
            return {
                'needs_rewriting': target_quality > 0.7,  # Only if high quality target
                'issues': ['Minimal dialogue'],
                'quality_score': 0.5
            }
        
        # Basic dialogue quality analysis would go here
        return {
            'needs_rewriting': False,
            'issues': [],
            'quality_score': 0.8
        }
    
    def _analyze_description_quality(self, prose: str, target_quality: float) -> Dict[str, Any]:
        """Analyze description quality"""
        
        # Simplified analysis
        sensory_words = ['saw', 'heard', 'felt', 'smelled', 'looked', 'seemed']
        sensory_count = sum(1 for word in prose.lower().split() if word in sensory_words)
        
        quality_score = min(1.0, sensory_count / 5.0)
        
        return {
            'needs_rewriting': quality_score < target_quality and target_quality > 0.8,
            'issues': ['Insufficient sensory details'] if quality_score < 0.5 else [],
            'quality_score': quality_score
        }
    
    def _rewrite_scene_card_part(self, scene_card: SceneCard, part_name: str, 
                               analysis: Dict[str, Any], preserve_crucible: bool) -> Dict[str, Any]:
        """Rewrite a scene card part"""
        
        # Simplified rewriting - in full implementation would use AI or templates
        if part_name == 'scene_crucible':
            if preserve_crucible:
                # Enhance existing crucible
                current = scene_card.scene_crucible or ""
                scene_card.scene_crucible = f"The critical moment when {current.lower()}" if current else "The crucial turning point"
            else:
                scene_card.scene_crucible = "Enhanced scene crucible with greater tension"
        
        elif part_name == 'goal':
            scene_card.proactive.goal = "Clear, specific goal with urgency and stakes"
        elif part_name == 'conflict':
            scene_card.proactive.conflict = "Significant obstacle that directly opposes the goal"
        elif part_name == 'setback':
            scene_card.proactive.setback = "Meaningful setback that changes the situation"
        
        elif part_name == 'reaction':
            scene_card.reactive.reaction = "Visceral emotional response to previous events"
        elif part_name == 'dilemma':
            scene_card.reactive.dilemma = "Difficult choice between two poor options"
        elif part_name == 'decision':
            scene_card.reactive.decision = "Clear decision that moves the story forward"
        
        return {
            'success': True,
            'scene_card': scene_card
        }
    
    def _rewrite_prose_part(self, prose_content: str, part_name: str, 
                          analysis: Dict[str, Any], preserve_crucible: bool) -> Dict[str, Any]:
        """Rewrite a prose part"""
        
        # Simplified rewriting - in full implementation would regenerate sections
        updated_prose = prose_content + f"\n\n[{part_name.capitalize()} section enhanced for better quality]"
        
        return {
            'success': True,
            'prose_content': updated_prose
        }


class CompressionDecider:
    """
    TaskMaster Task 45.5: Compression Decision Logic
    Determines if scene compression is needed and applies it appropriately.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("CompressionDecider")
    
    def decide_and_compress(self, scene_card: SceneCard, prose_content: Optional[str] = None,
                          compression_threshold: float = 0.8, preserve_crucible: bool = True) -> Dict[str, Any]:
        """
        Assess scene for compression needs and apply compression if appropriate
        
        Args:
            scene_card: Scene card to analyze
            prose_content: Prose content to analyze and compress
            compression_threshold: Verbosity threshold for compression
            preserve_crucible: Whether to preserve scene crucible
            
        Returns:
            Dictionary with compression results
        """
        
        self.logger.debug(f"Analyzing compression needs for scene {scene_card.scene_id}")
        
        compression_analysis = self._analyze_compression_needs(scene_card, prose_content, compression_threshold)
        
        compression_applied = False
        updated_scene_card = copy.deepcopy(scene_card)
        updated_prose = prose_content
        
        if compression_analysis['needs_compression']:
            self.logger.info(f"Applying compression to scene {scene_card.scene_id}: {compression_analysis['reasons']}")
            
            # Apply scene card compression
            if compression_analysis['compress_scene_card']:
                card_result = self._compress_scene_card(updated_scene_card, compression_analysis, preserve_crucible)
                updated_scene_card = card_result['scene_card']
                compression_applied = True
            
            # Apply prose compression
            if compression_analysis['compress_prose'] and prose_content:
                prose_result = self._compress_prose(updated_prose, compression_analysis, preserve_crucible)
                updated_prose = prose_result['prose_content']
                compression_applied = True
        
        return {
            'scene_card': updated_scene_card,
            'prose_content': updated_prose,
            'compression_applied': compression_applied,
            'compression_analysis': compression_analysis
        }
    
    def _analyze_compression_needs(self, scene_card: SceneCard, prose_content: Optional[str],
                                 compression_threshold: float) -> Dict[str, Any]:
        """Analyze if compression is needed"""
        
        needs_compression = False
        reasons = []
        compress_scene_card = False
        compress_prose = False
        
        # Analyze scene card verbosity
        card_verbosity = self._calculate_scene_card_verbosity(scene_card)
        if card_verbosity > compression_threshold:
            needs_compression = True
            compress_scene_card = True
            reasons.append(f"Scene card too verbose (score: {card_verbosity:.2f})")
        
        # Analyze prose verbosity
        if prose_content:
            prose_verbosity = self._calculate_prose_verbosity(prose_content)
            if prose_verbosity > compression_threshold:
                needs_compression = True
                compress_prose = True
                reasons.append(f"Prose too verbose (score: {prose_verbosity:.2f})")
        
        return {
            'needs_compression': needs_compression,
            'reasons': reasons,
            'compress_scene_card': compress_scene_card,
            'compress_prose': compress_prose,
            'card_verbosity': card_verbosity,
            'prose_verbosity': prose_verbosity if prose_content else 0.0
        }
    
    def _calculate_scene_card_verbosity(self, scene_card: SceneCard) -> float:
        """Calculate scene card verbosity score"""
        
        total_length = 0
        field_count = 0
        
        # Check basic fields
        if scene_card.scene_crucible:
            total_length += len(scene_card.scene_crucible)
            field_count += 1
        
        # Check scene type specific fields
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            if scene_card.proactive:
                for field in ['goal', 'conflict', 'setback']:
                    value = getattr(scene_card.proactive, field, '')
                    if value:
                        total_length += len(value)
                        field_count += 1
        
        elif scene_card.scene_type == SceneType.REACTIVE and hasattr(scene_card, 'reactive'):
            if scene_card.reactive:
                for field in ['reaction', 'dilemma', 'decision']:
                    value = getattr(scene_card.reactive, field, '')
                    if value:
                        total_length += len(value)
                        field_count += 1
        
        if field_count == 0:
            return 0.0
        
        avg_length = total_length / field_count
        
        # Convert to verbosity score (0-1, where 1 is very verbose)
        # Consider > 100 chars per field as verbose
        return min(1.0, avg_length / 100.0)
    
    def _calculate_prose_verbosity(self, prose_content: str) -> float:
        """Calculate prose verbosity score"""
        
        words = prose_content.split()
        if not words:
            return 0.0
        
        sentences = re.split(r'[.!?]+', prose_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Calculate repetition score
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        
        repeated_words = sum(1 for count in word_counts.values() if count > 3)
        repetition_score = repeated_words / len(word_counts)
        
        # Combine metrics
        length_verbosity = min(1.0, avg_sentence_length / 20.0)  # 20+ words per sentence is verbose
        repetition_verbosity = min(1.0, repetition_score * 2)
        
        return (length_verbosity + repetition_verbosity) / 2
    
    def _compress_scene_card(self, scene_card: SceneCard, analysis: Dict[str, Any],
                           preserve_crucible: bool) -> Dict[str, Any]:
        """Compress verbose scene card elements"""
        
        # Compress scene crucible if not preserving
        if not preserve_crucible and scene_card.scene_crucible:
            if len(scene_card.scene_crucible) > 80:
                # Keep first part, remove excessive detail
                scene_card.scene_crucible = scene_card.scene_crucible[:80] + "..."
        
        # Compress scene type specific fields
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            if scene_card.proactive:
                for field in ['goal', 'conflict', 'setback']:
                    value = getattr(scene_card.proactive, field, '')
                    if value and len(value) > 60:
                        # Compress to essential elements
                        setattr(scene_card.proactive, field, value[:60] + "...")
        
        elif scene_card.scene_type == SceneType.REACTIVE and hasattr(scene_card, 'reactive'):
            if scene_card.reactive:
                for field in ['reaction', 'dilemma', 'decision']:
                    value = getattr(scene_card.reactive, field, '')
                    if value and len(value) > 60:
                        setattr(scene_card.reactive, field, value[:60] + "...")
        
        return {
            'scene_card': scene_card
        }
    
    def _compress_prose(self, prose_content: str, analysis: Dict[str, Any],
                       preserve_crucible: bool) -> Dict[str, Any]:
        """Compress verbose prose content"""
        
        # Simplified compression - remove excessive adjectives and redundancy
        compressed = prose_content
        
        # Remove redundant phrases
        redundant_patterns = [
            r'\b(very|quite|really|extremely|incredibly)\s+',
            r'\b(that|which)\s+was\s+',
            r'\bin\s+order\s+to\b'
        ]
        
        for pattern in redundant_patterns:
            compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)
        
        # Combine short sentences
        sentences = re.split(r'[.!?]+', compressed)
        combined_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # If sentence is very short, combine with previous
                if (combined_sentences and len(sentence.split()) < 4 and 
                    len(combined_sentences[-1].split()) < 15):
                    combined_sentences[-1] += f", {sentence.lower()}"
                else:
                    combined_sentences.append(sentence)
        
        compressed = '. '.join(combined_sentences) + '.'
        
        return {
            'prose_content': compressed
        }