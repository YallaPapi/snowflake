"""
Scene Triage Classifier

TaskMaster Task 45.1: Implement YES/NO/MAYBE Classification Logic
Core classification engine that evaluates scenes against criteria to determine triage decision.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

from ..models import SceneCard, SceneType
from ..validation.service import ValidationReport
from .service import TriageDecision


@dataclass  
class ClassificationCriteria:
    """Criteria for scene classification"""
    
    # YES decision thresholds (scene ready for production)
    yes_quality_threshold: float = 0.8
    yes_structure_adherence: float = 0.9
    yes_validation_pass_rate: float = 0.95
    yes_prose_coherence: float = 0.8
    
    # NO decision thresholds (scene should be rejected)
    no_quality_threshold: float = 0.4
    no_structure_adherence: float = 0.5
    no_validation_pass_rate: float = 0.6
    no_prose_coherence: float = 0.4
    
    # Metric weights for overall score calculation
    structure_weight: float = 0.3
    prose_quality_weight: float = 0.25
    validation_weight: float = 0.25
    snowflake_adherence_weight: float = 0.2
    
    # Scene-specific requirements
    require_scene_crucible: bool = True
    require_complete_structure: bool = True
    min_word_count: int = 200
    max_word_count: int = 2000
    
    # Quality tolerances  
    allow_minor_pov_inconsistencies: bool = True
    allow_minor_tense_inconsistencies: bool = True
    max_exposition_percentage: float = 0.25
    
    # Snowflake Method adherence
    require_goal_conflict_setback: bool = True  # For proactive scenes
    require_reaction_dilemma_decision: bool = True  # For reactive scenes
    
    # Advanced criteria
    min_dialogue_percentage: float = 0.1
    max_dialogue_percentage: float = 0.6
    require_sensory_details: bool = True
    require_emotional_content: bool = True


class ClassificationMetrics:
    """Calculated metrics for scene classification"""
    
    def __init__(self):
        self.structure_score = 0.0
        self.prose_quality_score = 0.0
        self.validation_score = 0.0
        self.snowflake_adherence_score = 0.0
        
        # Detailed breakdowns
        self.word_count = 0
        self.dialogue_percentage = 0.0
        self.exposition_percentage = 0.0
        self.pov_consistency = 0.0
        self.tense_consistency = 0.0
        self.sensory_detail_score = 0.0
        self.emotional_content_score = 0.0
        
        # Issue tracking
        self.structural_issues = []
        self.quality_issues = []
        self.validation_issues = []
        self.snowflake_issues = []


class TriageClassifier:
    """
    TaskMaster Task 45.1: YES/NO/MAYBE Classification Logic
    
    Evaluates scenes against classification criteria to make triage decisions.
    Provides detailed scoring and issue identification to support redesign decisions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("TriageClassifier")
        
        # Classification thresholds (can be overridden by criteria)
        self.default_yes_threshold = 0.8
        self.default_no_threshold = 0.4
        
    def classify_scene(self, scene_card: SceneCard, prose_content: Optional[str] = None,
                      validation_report: Optional[ValidationReport] = None,
                      criteria: Optional[ClassificationCriteria] = None) -> Dict[str, Any]:
        """
        Classify scene as YES/NO/MAYBE based on evaluation criteria
        
        Args:
            scene_card: Scene card to evaluate
            prose_content: Optional prose content for analysis
            validation_report: Optional validation results
            criteria: Classification criteria (uses defaults if not provided)
            
        Returns:
            Dictionary with decision, score, metrics, issues, and recommendations
        """
        
        self.logger.debug(f"Classifying scene {scene_card.scene_id}")
        
        # Use provided criteria or defaults
        criteria = criteria or self._get_default_criteria()
        
        # Calculate metrics
        metrics = self._calculate_metrics(scene_card, prose_content, validation_report, criteria)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics, criteria)
        
        # Make classification decision
        decision = self._make_classification_decision(overall_score, metrics, criteria)
        
        # Generate issues and recommendations
        issues = self._identify_issues(metrics, criteria)
        recommendations = self._generate_recommendations(metrics, issues, criteria)
        
        return {
            'decision': decision,
            'score': overall_score,
            'metrics': self._metrics_to_dict(metrics),
            'issues': issues,
            'recommendations': recommendations,
            'criteria_used': criteria
        }
    
    def _calculate_metrics(self, scene_card: SceneCard, prose_content: Optional[str],
                          validation_report: Optional[ValidationReport], 
                          criteria: ClassificationCriteria) -> ClassificationMetrics:
        """Calculate all classification metrics"""
        
        metrics = ClassificationMetrics()
        
        # Structure score based on Scene Card completeness
        metrics.structure_score = self._calculate_structure_score(scene_card, criteria)
        
        # Prose quality score if prose available
        if prose_content:
            metrics.prose_quality_score = self._calculate_prose_quality_score(prose_content, criteria)
            metrics.word_count = len(prose_content.split())
            metrics.dialogue_percentage = self._calculate_dialogue_percentage(prose_content)
            metrics.exposition_percentage = self._estimate_exposition_percentage(prose_content)
            metrics.pov_consistency = self._analyze_pov_consistency(prose_content)
            metrics.tense_consistency = self._analyze_tense_consistency(prose_content)
            metrics.sensory_detail_score = self._analyze_sensory_details(prose_content)
            metrics.emotional_content_score = self._analyze_emotional_content(prose_content)
        
        # Validation score if validation report available
        if validation_report:
            metrics.validation_score = self._calculate_validation_score(validation_report)
        else:
            metrics.validation_score = 0.5  # Neutral when no validation available
        
        # Snowflake adherence score
        metrics.snowflake_adherence_score = self._calculate_snowflake_adherence(scene_card, prose_content, criteria)
        
        return metrics
    
    def _calculate_structure_score(self, scene_card: SceneCard, criteria: ClassificationCriteria) -> float:
        """Calculate structural completeness score"""
        
        score = 0.0
        components = 0
        
        # Basic required fields
        if scene_card.scene_crucible and criteria.require_scene_crucible:
            score += 0.2
        components += 1
        
        if scene_card.pov_character:
            score += 0.1
        components += 1
        
        if scene_card.pov:
            score += 0.1
        components += 1
        
        if scene_card.tense:
            score += 0.1
        components += 1
        
        # Scene type specific structure
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            proactive = scene_card.proactive
            if proactive and criteria.require_complete_structure:
                if hasattr(proactive, 'goal') and proactive.goal:
                    score += 0.15
                if hasattr(proactive, 'conflict') and proactive.conflict:
                    score += 0.15
                if hasattr(proactive, 'setback') and proactive.setback:
                    score += 0.15
            components += 3
        
        elif scene_card.scene_type == SceneType.REACTIVE and hasattr(scene_card, 'reactive'):
            reactive = scene_card.reactive
            if reactive and criteria.require_complete_structure:
                if hasattr(reactive, 'reaction') and reactive.reaction:
                    score += 0.15
                if hasattr(reactive, 'dilemma') and reactive.dilemma:
                    score += 0.15
                if hasattr(reactive, 'decision') and reactive.decision:
                    score += 0.15
            components += 3
        
        return min(1.0, score)
    
    def _calculate_prose_quality_score(self, prose_content: str, criteria: ClassificationCriteria) -> float:
        """Calculate prose quality score"""
        
        score = 0.0
        
        # Word count within acceptable range
        word_count = len(prose_content.split())
        if criteria.min_word_count <= word_count <= criteria.max_word_count:
            score += 0.2
        elif word_count < criteria.min_word_count:
            score += max(0, 0.2 * (word_count / criteria.min_word_count))
        else:  # Too long
            score += max(0, 0.2 * (criteria.max_word_count / word_count))
        
        # Sentence variety and structure
        sentences = re.split(r'[.!?]+', prose_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 8 <= avg_sentence_length <= 20:  # Good range
                score += 0.15
        
        # Paragraph structure
        paragraphs = prose_content.split('\n\n')
        if len(paragraphs) >= 2:  # Multiple paragraphs
            score += 0.1
        
        # Basic readability (simplified)
        if self._has_good_flow(prose_content):
            score += 0.2
        
        # Vocabulary variety (simplified check)
        words = prose_content.lower().split()
        unique_words = len(set(words))
        vocabulary_ratio = unique_words / len(words) if words else 0
        if vocabulary_ratio > 0.6:  # Good vocabulary variety
            score += 0.15
        
        # Grammar and mechanics (simplified)
        if self._basic_grammar_check(prose_content):
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_validation_score(self, validation_report: ValidationReport) -> float:
        """Calculate score based on validation results"""
        
        if not validation_report or not validation_report.validation_results:
            return 0.5  # Neutral when no validation
        
        passed_validations = sum(1 for result in validation_report.validation_results 
                               if result.get('passed', False))
        total_validations = len(validation_report.validation_results)
        
        return passed_validations / total_validations if total_validations > 0 else 0.0
    
    def _calculate_snowflake_adherence(self, scene_card: SceneCard, prose_content: Optional[str], 
                                     criteria: ClassificationCriteria) -> float:
        """Calculate Snowflake Method adherence score"""
        
        score = 0.0
        
        # Scene type adherence
        if scene_card.scene_type == SceneType.PROACTIVE:
            if hasattr(scene_card, 'proactive') and scene_card.proactive:
                proactive = scene_card.proactive
                if hasattr(proactive, 'goal') and proactive.goal:
                    score += 0.35  # Goal present
                if hasattr(proactive, 'conflict') and proactive.conflict:
                    score += 0.35  # Conflict present
                if hasattr(proactive, 'setback') and proactive.setback:
                    score += 0.30  # Setback present
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if hasattr(scene_card, 'reactive') and scene_card.reactive:
                reactive = scene_card.reactive
                if hasattr(reactive, 'reaction') and reactive.reaction:
                    score += 0.35  # Reaction present
                if hasattr(reactive, 'dilemma') and reactive.dilemma:
                    score += 0.35  # Dilemma present
                if hasattr(reactive, 'decision') and reactive.decision:
                    score += 0.30  # Decision present
        
        # Check prose alignment with structure if available
        if prose_content and score > 0:
            structure_alignment = self._check_prose_structure_alignment(scene_card, prose_content)
            score = score * structure_alignment  # Modulate by alignment
        
        return min(1.0, score)
    
    def _calculate_overall_score(self, metrics: ClassificationMetrics, 
                               criteria: ClassificationCriteria) -> float:
        """Calculate weighted overall score"""
        
        overall_score = (
            metrics.structure_score * criteria.structure_weight +
            metrics.prose_quality_score * criteria.prose_quality_weight +
            metrics.validation_score * criteria.validation_weight +
            metrics.snowflake_adherence_score * criteria.snowflake_adherence_weight
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _make_classification_decision(self, overall_score: float, metrics: ClassificationMetrics,
                                    criteria: ClassificationCriteria) -> TriageDecision:
        """Make final classification decision based on score and criteria"""
        
        # Check for hard NO conditions
        if (overall_score < criteria.no_quality_threshold or
            metrics.structure_score < criteria.no_structure_adherence or
            metrics.validation_score < criteria.no_validation_pass_rate):
            return TriageDecision.NO
        
        # Check for YES conditions
        if (overall_score >= criteria.yes_quality_threshold and
            metrics.structure_score >= criteria.yes_structure_adherence and
            metrics.validation_score >= criteria.yes_validation_pass_rate):
            return TriageDecision.YES
        
        # Everything else is MAYBE
        return TriageDecision.MAYBE
    
    def _identify_issues(self, metrics: ClassificationMetrics, 
                        criteria: ClassificationCriteria) -> List[str]:
        """Identify specific issues with the scene"""
        
        issues = []
        
        # Structure issues
        if metrics.structure_score < criteria.yes_structure_adherence:
            issues.append("Incomplete scene structure - missing required elements")
        
        # Prose quality issues
        if metrics.word_count > 0:  # Only if prose available
            if metrics.word_count < criteria.min_word_count:
                issues.append(f"Scene too short: {metrics.word_count} words (minimum {criteria.min_word_count})")
            elif metrics.word_count > criteria.max_word_count:
                issues.append(f"Scene too long: {metrics.word_count} words (maximum {criteria.max_word_count})")
            
            if metrics.dialogue_percentage < criteria.min_dialogue_percentage:
                issues.append(f"Insufficient dialogue: {metrics.dialogue_percentage:.1%} (minimum {criteria.min_dialogue_percentage:.1%})")
            elif metrics.dialogue_percentage > criteria.max_dialogue_percentage:
                issues.append(f"Excessive dialogue: {metrics.dialogue_percentage:.1%} (maximum {criteria.max_dialogue_percentage:.1%})")
            
            if metrics.exposition_percentage > criteria.max_exposition_percentage:
                issues.append(f"Too much exposition: {metrics.exposition_percentage:.1%} (maximum {criteria.max_exposition_percentage:.1%})")
        
        # Validation issues
        if metrics.validation_score < criteria.yes_validation_pass_rate:
            issues.append("Failed validation checks - see validation report for details")
        
        # Snowflake adherence issues
        if metrics.snowflake_adherence_score < 0.7:
            issues.append("Poor Snowflake Method adherence - structure doesn't follow required patterns")
        
        return issues
    
    def _generate_recommendations(self, metrics: ClassificationMetrics, issues: List[str],
                                criteria: ClassificationCriteria) -> List[str]:
        """Generate recommendations for improvement"""
        
        recommendations = []
        
        # Structure recommendations
        if metrics.structure_score < 0.8:
            recommendations.append("Complete all required scene structure elements (goal/conflict/setback or reaction/dilemma/decision)")
        
        # Prose recommendations
        if metrics.word_count > 0:
            if metrics.prose_quality_score < 0.7:
                recommendations.append("Improve prose quality: vary sentence length, enhance vocabulary, check grammar")
            
            if metrics.sensory_detail_score < 0.5:
                recommendations.append("Add more sensory details to make the scene more vivid")
            
            if metrics.emotional_content_score < 0.5:
                recommendations.append("Strengthen emotional content to better engage readers")
        
        # Validation recommendations
        if metrics.validation_score < 0.8:
            recommendations.append("Address validation failures to meet quality standards")
        
        # Snowflake recommendations
        if metrics.snowflake_adherence_score < 0.8:
            recommendations.append("Ensure scene follows Snowflake Method patterns more closely")
        
        return recommendations
    
    def _get_default_criteria(self) -> ClassificationCriteria:
        """Get default classification criteria"""
        return ClassificationCriteria()
    
    def _metrics_to_dict(self, metrics: ClassificationMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary for response"""
        
        return {
            'structure_score': metrics.structure_score,
            'prose_quality_score': metrics.prose_quality_score,
            'validation_score': metrics.validation_score,
            'snowflake_adherence_score': metrics.snowflake_adherence_score,
            'word_count': metrics.word_count,
            'dialogue_percentage': metrics.dialogue_percentage,
            'exposition_percentage': metrics.exposition_percentage,
            'pov_consistency': metrics.pov_consistency,
            'tense_consistency': metrics.tense_consistency,
            'sensory_detail_score': metrics.sensory_detail_score,
            'emotional_content_score': metrics.emotional_content_score
        }
    
    # Helper methods for prose analysis (simplified implementations)
    
    def _calculate_dialogue_percentage(self, prose: str) -> float:
        """Calculate percentage of content that is dialogue"""
        words = prose.split()
        dialogue_words = 0
        in_dialogue = False
        
        for word in words:
            if '"' in word:
                in_dialogue = not in_dialogue
            if in_dialogue:
                dialogue_words += 1
        
        return dialogue_words / len(words) if words else 0.0
    
    def _estimate_exposition_percentage(self, prose: str) -> float:
        """Estimate exposition percentage (simplified)"""
        exposition_indicators = ['had been', 'years ago', 'in the past', 'used to', 'was known for']
        words = prose.lower().split()
        exposition_words = sum(1 for word in words if any(indicator in prose.lower() for indicator in exposition_indicators))
        
        return min(0.5, exposition_words / len(words)) if words else 0.0
    
    def _analyze_pov_consistency(self, prose: str) -> float:
        """Analyze POV consistency (simplified)"""
        first_person_count = prose.lower().count(' i ') + prose.lower().count(' my ')
        third_person_count = prose.lower().count(' he ') + prose.lower().count(' she ') + prose.lower().count(' they ')
        
        if first_person_count + third_person_count == 0:
            return 0.5  # Neutral
        
        dominant_pov = max(first_person_count, third_person_count)
        total_pov = first_person_count + third_person_count
        
        return dominant_pov / total_pov if total_pov > 0 else 0.5
    
    def _analyze_tense_consistency(self, prose: str) -> float:
        """Analyze tense consistency (simplified)"""
        past_indicators = prose.lower().count('was') + prose.lower().count('were') + prose.lower().count('had')
        present_indicators = prose.lower().count('is') + prose.lower().count('are') + prose.lower().count('am')
        
        if past_indicators + present_indicators == 0:
            return 0.5
        
        dominant_tense = max(past_indicators, present_indicators)
        total_tense = past_indicators + present_indicators
        
        return dominant_tense / total_tense if total_tense > 0 else 0.5
    
    def _analyze_sensory_details(self, prose: str) -> float:
        """Analyze sensory detail content (simplified)"""
        sensory_words = ['saw', 'heard', 'felt', 'smelled', 'tasted', 'looked', 'sounded', 'seemed']
        words = prose.lower().split()
        sensory_count = sum(1 for word in words if word in sensory_words)
        
        return min(1.0, sensory_count / max(len(words) // 25, 1))  # Normalized score
    
    def _analyze_emotional_content(self, prose: str) -> float:
        """Analyze emotional content (simplified)"""
        emotion_words = ['felt', 'angry', 'sad', 'happy', 'fear', 'joy', 'love', 'hate', 'worried', 'excited']
        words = prose.lower().split()
        emotion_count = sum(1 for word in words if word in emotion_words)
        
        return min(1.0, emotion_count / max(len(words) // 30, 1))
    
    def _has_good_flow(self, prose: str) -> bool:
        """Check for good prose flow (simplified)"""
        # Look for transition words and varied sentence starts
        transition_words = ['however', 'meanwhile', 'then', 'but', 'and', 'yet', 'so']
        return any(word in prose.lower() for word in transition_words)
    
    def _basic_grammar_check(self, prose: str) -> bool:
        """Basic grammar check (simplified)"""
        # Check for capitalization and punctuation
        sentences = re.split(r'[.!?]+', prose)
        properly_capitalized = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        
        return properly_capitalized / len(sentences) > 0.8 if sentences else False
    
    def _check_prose_structure_alignment(self, scene_card: SceneCard, prose: str) -> float:
        """Check if prose aligns with scene card structure (simplified)"""
        
        prose_lower = prose.lower()
        alignment_score = 0.5  # Base score
        
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            proactive = scene_card.proactive
            if proactive:
                # Check if goal/conflict/setback elements appear in prose
                if hasattr(proactive, 'goal') and proactive.goal:
                    goal_words = proactive.goal.lower().split()[:3]
                    if any(word in prose_lower for word in goal_words):
                        alignment_score += 0.2
                
                if hasattr(proactive, 'conflict') and proactive.conflict:
                    conflict_words = proactive.conflict.lower().split()[:3]
                    if any(word in prose_lower for word in conflict_words):
                        alignment_score += 0.2
                
                if hasattr(proactive, 'setback') and proactive.setback:
                    setback_words = proactive.setback.lower().split()[:3]
                    if any(word in prose_lower for word in setback_words):
                        alignment_score += 0.1
        
        return min(1.0, alignment_score)