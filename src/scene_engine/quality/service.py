"""
Content Quality Assessment Service

This implements Task 45: Content Quality Assessment
Comprehensive quality metrics and assessment system combining all analysis components
for complete prose quality evaluation with Snowflake Method compliance.
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..models import SceneCard, SceneType


class QualityDimension(Enum):
    """Quality assessment dimensions"""
    READABILITY = "readability"
    COHERENCE = "coherence"
    STRUCTURE = "structure"
    ENGAGEMENT = "engagement"
    TECHNICAL = "technical"
    SNOWFLAKE_COMPLIANCE = "snowflake_compliance"


@dataclass
class QualityScore:
    """Individual quality score with details"""
    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    max_possible: float = 1.0
    confidence: float = 1.0
    explanation: str = ""
    contributing_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    content_id: str
    assessment_timestamp: datetime
    
    # Individual scores
    readability_score: QualityScore = None
    coherence_score: QualityScore = None
    structure_score: QualityScore = None
    engagement_score: QualityScore = None
    technical_score: QualityScore = None
    snowflake_compliance_score: QualityScore = None
    
    # Overall metrics
    overall_quality: float = 0.0
    weighted_score: float = 0.0
    
    # Content statistics
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    
    # Processing info
    processing_time_seconds: float = 0.0
    analysis_completeness: float = 1.0  # 0-1, how complete the analysis was
    
    def get_all_scores(self) -> List[QualityScore]:
        """Get all quality scores"""
        scores = []
        for attr in [self.readability_score, self.coherence_score, self.structure_score,
                    self.engagement_score, self.technical_score, self.snowflake_compliance_score]:
            if attr:
                scores.append(attr)
        return scores
    
    def get_score_summary(self) -> Dict[str, float]:
        """Get summary of all scores"""
        return {
            "overall_quality": self.overall_quality,
            "readability": self.readability_score.score if self.readability_score else 0.0,
            "coherence": self.coherence_score.score if self.coherence_score else 0.0,
            "structure": self.structure_score.score if self.structure_score else 0.0,
            "engagement": self.engagement_score.score if self.engagement_score else 0.0,
            "technical": self.technical_score.score if self.technical_score else 0.0,
            "snowflake_compliance": self.snowflake_compliance_score.score if self.snowflake_compliance_score else 0.0
        }


class ReadabilityAnalyzer:
    """Advanced readability scoring and linguistic analysis"""
    
    @staticmethod
    def analyze_readability(content: str) -> QualityScore:
        """Comprehensive readability analysis"""
        
        if not content.strip():
            return QualityScore(
                dimension=QualityDimension.READABILITY,
                score=0.0,
                explanation="No content to analyze"
            )
        
        # Basic text metrics
        words = content.split()
        word_count = len(words)
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        sentence_count = len(sentences)
        
        if word_count == 0 or sentence_count == 0:
            return QualityScore(
                dimension=QualityDimension.READABILITY,
                score=0.0,
                explanation="Insufficient content for analysis"
            )
        
        # Calculate syllable count (approximation)
        syllable_count = ReadabilityAnalyzer._estimate_syllables(content)
        
        # Flesch Reading Ease
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        # Convert to 0-1 scale (scores above 60 are considered good)
        readability_score = min(1.0, flesch_score / 70.0)
        
        # Additional factors
        factors = []
        recommendations = []
        
        # Sentence length variety
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = ReadabilityAnalyzer._calculate_variance(sentence_lengths)
        
        if length_variance < 5:
            factors.append("Low sentence length variety")
            recommendations.append("Vary sentence lengths for better rhythm")
        else:
            factors.append("Good sentence length variety")
        
        # Complex word analysis
        complex_words = [word for word in words if ReadabilityAnalyzer._is_complex_word(word)]
        complex_ratio = len(complex_words) / word_count
        
        if complex_ratio > 0.15:  # More than 15% complex words
            factors.append("High proportion of complex words")
            recommendations.append("Consider simplifying some vocabulary")
        elif complex_ratio < 0.05:
            factors.append("Low vocabulary complexity")
            recommendations.append("Consider adding more sophisticated vocabulary")
        else:
            factors.append("Balanced vocabulary complexity")
        
        # Passive voice detection
        passive_patterns = [r'\bwas\s+\w+ed\b', r'\bwere\s+\w+ed\b', r'\bbeing\s+\w+ed\b']
        passive_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in passive_patterns)
        passive_ratio = passive_count / sentence_count
        
        if passive_ratio > 0.3:
            factors.append("Frequent passive voice usage")
            recommendations.append("Convert some passive constructions to active voice")
        else:
            factors.append("Appropriate active voice usage")
        
        explanation = f"Flesch Reading Ease: {flesch_score:.1f}, Average sentence length: {avg_sentence_length:.1f} words"
        
        return QualityScore(
            dimension=QualityDimension.READABILITY,
            score=readability_score,
            explanation=explanation,
            contributing_factors=factors,
            recommendations=recommendations
        )
    
    @staticmethod
    def _estimate_syllables(text: str) -> int:
        """Estimate syllable count"""
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = text.split()
        
        total_syllables = 0
        for word in words:
            syllables = len(re.findall(r'[aeiouy]+', word))
            if word.endswith('e'):
                syllables -= 1
            total_syllables += max(1, syllables)
        
        return total_syllables
    
    @staticmethod
    def _calculate_variance(numbers: List[float]) -> float:
        """Calculate variance of a list of numbers"""
        if len(numbers) <= 1:
            return 0.0
        
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
        return variance
    
    @staticmethod
    def _is_complex_word(word: str) -> bool:
        """Determine if a word is complex (3+ syllables)"""
        clean_word = re.sub(r'[^a-zA-Z]', '', word.lower())
        if len(clean_word) < 3:
            return False
        
        syllables = len(re.findall(r'[aeiouy]+', clean_word))
        if clean_word.endswith('e'):
            syllables -= 1
        
        return max(1, syllables) >= 3


class CoherenceAnalyzer:
    """Narrative coherence and flow analysis"""
    
    @staticmethod
    def analyze_coherence(content: str, scene_card: Optional[SceneCard] = None) -> QualityScore:
        """Analyze narrative coherence and flow"""
        
        if not content.strip():
            return QualityScore(
                dimension=QualityDimension.COHERENCE,
                score=0.0,
                explanation="No content to analyze"
            )
        
        factors = []
        recommendations = []
        coherence_score = 0.5  # Start with neutral
        
        # Transition analysis
        transition_words = [
            'then', 'next', 'after', 'before', 'when', 'while', 'during', 'suddenly',
            'meanwhile', 'however', 'therefore', 'consequently', 'furthermore', 'moreover'
        ]
        
        transition_count = sum(1 for word in transition_words 
                              if re.search(r'\b' + word + r'\b', content, re.IGNORECASE))
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        sentence_count = len(sentences)
        
        if sentence_count > 0:
            transition_ratio = transition_count / sentence_count
            
            if transition_ratio > 0.2:
                factors.append("Good use of transitional elements")
                coherence_score += 0.15
            elif transition_ratio < 0.1:
                factors.append("Limited transitional elements")
                recommendations.append("Add more transitional words and phrases")
                coherence_score -= 0.1
        
        # Pronoun reference analysis
        pronouns = ['he', 'she', 'it', 'they', 'him', 'her', 'them']
        pronoun_count = sum(len(re.findall(r'\b' + pronoun + r'\b', content, re.IGNORECASE)) 
                          for pronoun in pronouns)
        
        if pronoun_count > 0:
            words = content.split()
            pronoun_ratio = pronoun_count / len(words)
            
            if 0.02 <= pronoun_ratio <= 0.08:  # Appropriate range
                factors.append("Balanced pronoun usage")
                coherence_score += 0.1
            elif pronoun_ratio > 0.12:
                factors.append("Heavy pronoun usage may cause confusion")
                recommendations.append("Clarify some pronoun references with specific nouns")
                coherence_score -= 0.15
        
        # Temporal consistency
        past_tense_indicators = ['was', 'were', 'had', 'did', 'went', 'came', 'said']
        present_tense_indicators = ['is', 'are', 'has', 'does', 'goes', 'comes', 'says']
        
        past_count = sum(len(re.findall(r'\b' + word + r'\b', content, re.IGNORECASE)) 
                        for word in past_tense_indicators)
        present_count = sum(len(re.findall(r'\b' + word + r'\b', content, re.IGNORECASE)) 
                           for word in present_tense_indicators)
        
        if past_count > 0 or present_count > 0:
            total_tense = past_count + present_count
            tense_consistency = max(past_count, present_count) / total_tense
            
            if tense_consistency > 0.8:
                factors.append("Consistent verb tense usage")
                coherence_score += 0.15
            else:
                factors.append("Inconsistent verb tense usage")
                recommendations.append("Maintain consistent tense throughout the scene")
                coherence_score -= 0.2
        
        # Dialogue integration
        dialogue_matches = re.findall(r'"[^"]*"', content)
        if dialogue_matches:
            # Check for dialogue tags and attribution
            dialogue_with_tags = 0
            for match in dialogue_matches:
                context = content[content.find(match):content.find(match) + len(match) + 50]
                if re.search(r'(said|asked|replied|whispered|shouted)', context, re.IGNORECASE):
                    dialogue_with_tags += 1
            
            if len(dialogue_matches) > 0:
                tag_ratio = dialogue_with_tags / len(dialogue_matches)
                if tag_ratio > 0.7:
                    factors.append("Well-integrated dialogue")
                    coherence_score += 0.1
                else:
                    factors.append("Some dialogue lacks clear attribution")
                    recommendations.append("Ensure all dialogue has clear speaker attribution")
        
        # Scene-specific coherence (if scene card provided)
        if scene_card:
            coherence_score += CoherenceAnalyzer._analyze_scene_coherence(content, scene_card, factors, recommendations)
        
        # Clamp final score
        coherence_score = max(0.0, min(1.0, coherence_score))
        
        explanation = f"Coherence analysis based on transitions, pronouns, tense consistency, and dialogue integration"
        
        return QualityScore(
            dimension=QualityDimension.COHERENCE,
            score=coherence_score,
            explanation=explanation,
            contributing_factors=factors,
            recommendations=recommendations
        )
    
    @staticmethod
    def _analyze_scene_coherence(content: str, scene_card: SceneCard, 
                                factors: List[str], recommendations: List[str]) -> float:
        """Analyze scene-specific coherence"""
        
        coherence_bonus = 0.0
        
        # Check POV consistency
        pov_character = scene_card.pov.lower()
        if pov_character in content.lower():
            factors.append("POV character appears in content")
            coherence_bonus += 0.05
        else:
            factors.append("POV character not clearly present")
            recommendations.append("Ensure POV character is clearly present in the scene")
        
        # Check setting consistency
        if scene_card.place and scene_card.place.lower() in content.lower():
            factors.append("Setting consistent with scene metadata")
            coherence_bonus += 0.05
        
        # Check scene type coherence
        if scene_card.scene_type == SceneType.PROACTIVE:
            # Look for action and goal-oriented language
            action_words = ['tried', 'attempted', 'sought', 'searched', 'fought', 'ran', 'climbed']
            if any(word in content.lower() for word in action_words):
                factors.append("Content matches proactive scene type")
                coherence_bonus += 0.1
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            # Look for emotional and reflective language
            emotion_words = ['felt', 'thought', 'realized', 'wondered', 'considered', 'reflected']
            if any(word in content.lower() for word in emotion_words):
                factors.append("Content matches reactive scene type")
                coherence_bonus += 0.1
        
        return coherence_bonus


class QualityMetricsEngine:
    """Core quality assessment engine"""
    
    def __init__(self):
        self.readability_analyzer = ReadabilityAnalyzer()
        self.coherence_analyzer = CoherenceAnalyzer()
        
        # Quality dimension weights
        self.dimension_weights = {
            QualityDimension.READABILITY: 0.20,
            QualityDimension.COHERENCE: 0.25,
            QualityDimension.STRUCTURE: 0.20,
            QualityDimension.ENGAGEMENT: 0.15,
            QualityDimension.TECHNICAL: 0.10,
            QualityDimension.SNOWFLAKE_COMPLIANCE: 0.10
        }
    
    def assess_structure(self, content: str, scene_card: Optional[SceneCard] = None) -> QualityScore:
        """Assess structural quality"""
        
        factors = []
        recommendations = []
        structure_score = 0.5  # Start neutral
        
        if not content.strip():
            return QualityScore(
                dimension=QualityDimension.STRUCTURE,
                score=0.0,
                explanation="No content to analyze"
            )
        
        # Paragraph analysis
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        if paragraph_count >= 3:
            factors.append("Appropriate paragraph structure")
            structure_score += 0.1
        elif paragraph_count == 1:
            factors.append("Single paragraph - may lack structure")
            recommendations.append("Consider breaking into multiple paragraphs")
            structure_score -= 0.15
        
        # Opening strength
        if paragraphs:
            first_paragraph = paragraphs[0]
            first_words = first_paragraph.split()[:3]
            
            weak_openings = ['the', 'it', 'there', 'when', 'as']
            if first_words and first_words[0].lower() in weak_openings:
                factors.append("Weak opening construction")
                recommendations.append("Start with stronger, more active language")
                structure_score -= 0.1
            else:
                factors.append("Strong opening")
                structure_score += 0.1
        
        # Ending analysis
        if paragraphs:
            last_paragraph = paragraphs[-1]
            if len(last_paragraph.split()) < 10:
                factors.append("Abrupt or weak ending")
                recommendations.append("Expand the conclusion")
                structure_score -= 0.1
            else:
                factors.append("Substantive conclusion")
                structure_score += 0.1
        
        # Scene card alignment
        if scene_card:
            structure_score += self._assess_scene_structure_alignment(
                content, scene_card, factors, recommendations
            )
        
        structure_score = max(0.0, min(1.0, structure_score))
        
        return QualityScore(
            dimension=QualityDimension.STRUCTURE,
            score=structure_score,
            explanation="Structural analysis of paragraphs, opening, ending, and scene alignment",
            contributing_factors=factors,
            recommendations=recommendations
        )
    
    def _assess_scene_structure_alignment(self, content: str, scene_card: SceneCard,
                                        factors: List[str], recommendations: List[str]) -> float:
        """Assess alignment with scene structure requirements"""
        
        alignment_score = 0.0
        
        if scene_card.scene_type == SceneType.PROACTIVE and scene_card.proactive:
            # Check for goal, conflict, setback indicators
            goal_indicators = ['wanted', 'needed', 'tried', 'attempted', 'sought']
            conflict_indicators = ['but', 'however', 'unfortunately', 'blocked', 'stopped']
            setback_indicators = ['failed', 'couldn\'t', 'impossible', 'too late']
            
            has_goal = any(indicator in content.lower() for indicator in goal_indicators)
            has_conflict = any(indicator in content.lower() for indicator in conflict_indicators)
            has_setback = any(indicator in content.lower() for indicator in setback_indicators)
            
            if has_goal and has_conflict and has_setback:
                factors.append("Clear Goal-Conflict-Setback structure")
                alignment_score += 0.2
            else:
                missing = []
                if not has_goal: missing.append("goal")
                if not has_conflict: missing.append("conflict")
                if not has_setback: missing.append("setback")
                
                factors.append(f"Missing G-C-S elements: {', '.join(missing)}")
                recommendations.append("Ensure clear Goal-Conflict-Setback structure")
        
        elif scene_card.scene_type == SceneType.REACTIVE and scene_card.reactive:
            # Check for reaction, dilemma, decision indicators
            reaction_indicators = ['felt', 'realized', 'shocked', 'angry', 'disappointed']
            dilemma_indicators = ['choice', 'decision', 'options', 'what if', 'should']
            decision_indicators = ['decided', 'chose', 'would', 'must', 'going to']
            
            has_reaction = any(indicator in content.lower() for indicator in reaction_indicators)
            has_dilemma = any(indicator in content.lower() for indicator in dilemma_indicators)
            has_decision = any(indicator in content.lower() for indicator in decision_indicators)
            
            if has_reaction and has_dilemma and has_decision:
                factors.append("Clear Reaction-Dilemma-Decision structure")
                alignment_score += 0.2
            else:
                missing = []
                if not has_reaction: missing.append("reaction")
                if not has_dilemma: missing.append("dilemma")
                if not has_decision: missing.append("decision")
                
                factors.append(f"Missing R-D-D elements: {', '.join(missing)}")
                recommendations.append("Ensure clear Reaction-Dilemma-Decision structure")
        
        return alignment_score
    
    def assess_engagement(self, content: str) -> QualityScore:
        """Assess reader engagement factors"""
        
        factors = []
        recommendations = []
        engagement_score = 0.5  # Start neutral
        
        if not content.strip():
            return QualityScore(
                dimension=QualityDimension.ENGAGEMENT,
                score=0.0,
                explanation="No content to analyze"
            )
        
        # Dialogue presence and quality
        dialogue_matches = re.findall(r'"[^"]*"', content)
        words = content.split()
        
        if dialogue_matches and words:
            dialogue_words = sum(len(match.split()) for match in dialogue_matches)
            dialogue_ratio = dialogue_words / len(words)
            
            if 0.2 <= dialogue_ratio <= 0.6:  # Good balance
                factors.append("Good dialogue-to-narrative balance")
                engagement_score += 0.15
            elif dialogue_ratio > 0.8:
                factors.append("Dialogue-heavy content")
                recommendations.append("Balance dialogue with narrative description")
            elif dialogue_ratio < 0.1:
                factors.append("Limited dialogue")
                recommendations.append("Consider adding dialogue for character interaction")
        
        # Sensory details
        sensory_words = [
            'saw', 'looked', 'watched', 'glimpsed',  # Visual
            'heard', 'listened', 'whispered', 'shouted',  # Auditory
            'felt', 'touched', 'rough', 'smooth',  # Tactile
            'smelled', 'scent', 'aroma', 'stench',  # Olfactory
            'tasted', 'bitter', 'sweet', 'salty'  # Gustatory
        ]
        
        sensory_count = sum(1 for word in sensory_words 
                          if re.search(r'\b' + word + r'\b', content, re.IGNORECASE))
        
        if sensory_count >= 3:
            factors.append("Rich sensory details")
            engagement_score += 0.15
        elif sensory_count < 1:
            factors.append("Limited sensory engagement")
            recommendations.append("Add more sensory details to immerse readers")
        
        # Emotional language
        emotion_words = [
            'angry', 'sad', 'happy', 'excited', 'nervous', 'afraid', 'relieved',
            'frustrated', 'delighted', 'worried', 'confident', 'surprised'
        ]
        
        emotion_count = sum(1 for word in emotion_words 
                          if re.search(r'\b' + word + r'\b', content, re.IGNORECASE))
        
        if emotion_count >= 2:
            factors.append("Strong emotional content")
            engagement_score += 0.1
        elif emotion_count == 0:
            factors.append("Limited emotional language")
            recommendations.append("Include more emotional depth")
        
        # Action and movement
        action_words = [
            'ran', 'jumped', 'climbed', 'fought', 'grabbed', 'threw', 'pushed',
            'pulled', 'rushed', 'dashed', 'leaped', 'struck'
        ]
        
        action_count = sum(1 for word in action_words 
                         if re.search(r'\b' + word + r'\b', content, re.IGNORECASE))
        
        if action_count >= 2:
            factors.append("Dynamic action elements")
            engagement_score += 0.1
        
        engagement_score = max(0.0, min(1.0, engagement_score))
        
        return QualityScore(
            dimension=QualityDimension.ENGAGEMENT,
            score=engagement_score,
            explanation="Engagement based on dialogue, sensory details, emotion, and action",
            contributing_factors=factors,
            recommendations=recommendations
        )
    
    def assess_technical_quality(self, content: str) -> QualityScore:
        """Assess technical writing quality"""
        
        factors = []
        recommendations = []
        technical_score = 0.8  # Start high, deduct for problems
        
        if not content.strip():
            return QualityScore(
                dimension=QualityDimension.TECHNICAL,
                score=0.0,
                explanation="No content to analyze"
            )
        
        # Basic grammar and punctuation checks
        # Check for double spaces
        if '  ' in content:
            factors.append("Multiple spaces found")
            recommendations.append("Remove extra spaces")
            technical_score -= 0.05
        
        # Check for missing spaces after punctuation
        missing_spaces = len(re.findall(r'[.!?][a-zA-Z]', content))
        if missing_spaces > 0:
            factors.append("Missing spaces after punctuation")
            recommendations.append("Add spaces after sentence endings")
            technical_score -= 0.1
        
        # Check for inconsistent quotation marks
        single_quotes = content.count("'")
        double_quotes = content.count('"')
        
        if single_quotes > 0 and double_quotes > 0:
            factors.append("Mixed quotation mark styles")
            recommendations.append("Use consistent quotation marks")
            technical_score -= 0.05
        
        # Check for paragraph formatting
        if '\n\n\n' in content:  # Triple line breaks
            factors.append("Inconsistent paragraph spacing")
            recommendations.append("Use consistent paragraph breaks")
            technical_score -= 0.05
        
        # Check for capitalization after periods
        sentences = re.split(r'[.!?]+\s+', content)
        lowercase_starts = sum(1 for sentence in sentences[1:] 
                             if sentence and sentence[0].islower())
        
        if lowercase_starts > 0:
            factors.append("Capitalization issues")
            recommendations.append("Capitalize first word of sentences")
            technical_score -= 0.1
        
        # Positive indicators
        if technical_score > 0.7:
            factors.append("Good technical quality")
        
        technical_score = max(0.0, min(1.0, technical_score))
        
        return QualityScore(
            dimension=QualityDimension.TECHNICAL,
            score=technical_score,
            explanation="Technical quality based on grammar, punctuation, and formatting",
            contributing_factors=factors,
            recommendations=recommendations
        )
    
    def assess_snowflake_compliance(self, content: str, scene_card: SceneCard) -> QualityScore:
        """Assess compliance with Snowflake Method principles"""
        
        factors = []
        recommendations = []
        compliance_score = 0.5  # Start neutral
        
        # Scene crucible alignment
        if scene_card.scene_crucible:
            crucible_words = scene_card.scene_crucible.lower().split()
            content_lower = content.lower()
            
            matching_words = sum(1 for word in crucible_words 
                               if len(word) > 3 and word in content_lower)
            
            if len(crucible_words) > 0:
                alignment_ratio = matching_words / len(crucible_words)
                
                if alignment_ratio > 0.3:
                    factors.append("Content aligns with scene crucible")
                    compliance_score += 0.2
                else:
                    factors.append("Limited alignment with scene crucible")
                    recommendations.append("Ensure content reflects the scene crucible")
        
        # POV consistency
        pov_character = scene_card.pov
        if pov_character in content:
            factors.append("POV character present in content")
            compliance_score += 0.1
        else:
            factors.append("POV character not clearly present")
            recommendations.append("Feature the POV character more prominently")
        
        # Scene type compliance
        if scene_card.scene_type == SceneType.PROACTIVE:
            if scene_card.proactive:
                # Check for clear goal, conflict, setback progression
                goal_present = any(word in content.lower() 
                                 for word in ['wanted', 'needed', 'goal', 'objective'])
                conflict_present = any(word in content.lower() 
                                     for word in ['but', 'however', 'obstacle', 'problem'])
                setback_present = any(word in content.lower() 
                                    for word in ['failed', 'couldn\'t', 'worse'])
                
                structure_elements = sum([goal_present, conflict_present, setback_present])
                compliance_score += (structure_elements / 3) * 0.3
                
                if structure_elements == 3:
                    factors.append("Complete G-C-S structure evident")
                else:
                    factors.append(f"Partial G-C-S structure ({structure_elements}/3 elements)")
                    recommendations.append("Strengthen Goal-Conflict-Setback structure")
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if scene_card.reactive:
                # Check for reaction, dilemma, decision progression
                reaction_present = any(word in content.lower() 
                                     for word in ['felt', 'realized', 'emotion'])
                dilemma_present = any(word in content.lower() 
                                    for word in ['choice', 'decision', 'what if'])
                decision_present = any(word in content.lower() 
                                     for word in ['decided', 'chose', 'would'])
                
                structure_elements = sum([reaction_present, dilemma_present, decision_present])
                compliance_score += (structure_elements / 3) * 0.3
                
                if structure_elements == 3:
                    factors.append("Complete R-D-D structure evident")
                else:
                    factors.append(f"Partial R-D-D structure ({structure_elements}/3 elements)")
                    recommendations.append("Strengthen Reaction-Dilemma-Decision structure")
        
        # Viewpoint discipline
        viewpoint_consistency = self._check_viewpoint_consistency(content, scene_card.viewpoint.value)
        compliance_score += viewpoint_consistency * 0.2
        
        if viewpoint_consistency > 0.8:
            factors.append("Consistent viewpoint discipline")
        else:
            factors.append("Viewpoint consistency issues")
            recommendations.append("Maintain consistent viewpoint throughout")
        
        compliance_score = max(0.0, min(1.0, compliance_score))
        
        return QualityScore(
            dimension=QualityDimension.SNOWFLAKE_COMPLIANCE,
            score=compliance_score,
            explanation="Compliance with Snowflake Method scene structure and principles",
            contributing_factors=factors,
            recommendations=recommendations
        )
    
    def _check_viewpoint_consistency(self, content: str, viewpoint: str) -> float:
        """Check viewpoint consistency throughout content"""
        
        if viewpoint == "third":
            # Should predominantly use third person pronouns
            third_person = len(re.findall(r'\b(he|she|him|her|his|hers|they|them|their)\b', 
                                        content, re.IGNORECASE))
            first_person = len(re.findall(r'\b(I|me|my|mine)\b', content, re.IGNORECASE))
            
            if third_person + first_person == 0:
                return 0.5  # No clear pronouns
            
            return third_person / (third_person + first_person)
        
        elif viewpoint == "first":
            # Should predominantly use first person pronouns
            first_person = len(re.findall(r'\b(I|me|my|mine)\b', content, re.IGNORECASE))
            third_person = len(re.findall(r'\b(he|she|him|her|his|hers)\b', 
                                        content, re.IGNORECASE))
            
            if third_person + first_person == 0:
                return 0.5
            
            return first_person / (third_person + first_person)
        
        return 0.5  # Default for other viewpoints


class QualityAssessmentService:
    """Complete quality assessment service integrating all analyzers"""
    
    def __init__(self):
        self.metrics_engine = QualityMetricsEngine()
        self.assessment_history = []
    
    def assess_content_quality(self, content: str, scene_card: Optional[SceneCard] = None,
                             custom_weights: Optional[Dict[QualityDimension, float]] = None) -> QualityReport:
        """Comprehensive content quality assessment"""
        
        start_time = datetime.utcnow()
        content_id = f"quality_{int(start_time.timestamp())}"
        
        # Basic content statistics
        words = content.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Perform all assessments
        readability_score = ReadabilityAnalyzer.analyze_readability(content)
        coherence_score = CoherenceAnalyzer.analyze_coherence(content, scene_card)
        structure_score = self.metrics_engine.assess_structure(content, scene_card)
        engagement_score = self.metrics_engine.assess_engagement(content)
        technical_score = self.metrics_engine.assess_technical_quality(content)
        
        snowflake_score = None
        if scene_card:
            snowflake_score = self.metrics_engine.assess_snowflake_compliance(content, scene_card)
        
        # Calculate overall quality using weights
        weights = custom_weights or self.metrics_engine.dimension_weights
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        scores = [readability_score, coherence_score, structure_score, engagement_score, technical_score]
        if snowflake_score:
            scores.append(snowflake_score)
        
        for score in scores:
            weight = weights.get(score.dimension, 0.0)
            weighted_sum += score.score * weight
            total_weight += weight
        
        overall_quality = weighted_sum / total_weight if total_weight > 0 else 0.0
        weighted_score = weighted_sum
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create comprehensive report
        report = QualityReport(
            content_id=content_id,
            assessment_timestamp=start_time,
            readability_score=readability_score,
            coherence_score=coherence_score,
            structure_score=structure_score,
            engagement_score=engagement_score,
            technical_score=technical_score,
            snowflake_compliance_score=snowflake_score,
            overall_quality=overall_quality,
            weighted_score=weighted_score,
            word_count=len(words),
            sentence_count=len(sentences),
            paragraph_count=len(paragraphs),
            processing_time_seconds=processing_time,
            analysis_completeness=1.0
        )
        
        # Add to assessment history
        self.assessment_history.append({
            'report': report,
            'scene_card': scene_card,
            'content_length': len(content)
        })
        
        return report
    
    def compare_quality_reports(self, report_a: QualityReport, report_b: QualityReport) -> Dict[str, Any]:
        """Compare two quality reports and provide insights"""
        
        comparison = {
            'overall_improvement': report_b.overall_quality - report_a.overall_quality,
            'dimension_changes': {},
            'recommendations': []
        }
        
        # Compare each dimension
        dimensions = ['readability', 'coherence', 'structure', 'engagement', 'technical', 'snowflake_compliance']
        
        for dim in dimensions:
            score_a = getattr(report_a, f"{dim}_score")
            score_b = getattr(report_b, f"{dim}_score")
            
            if score_a and score_b:
                change = score_b.score - score_a.score
                comparison['dimension_changes'][dim] = {
                    'change': change,
                    'direction': 'improved' if change > 0 else 'declined' if change < 0 else 'unchanged'
                }
                
                if change > 0.1:
                    comparison['recommendations'].append(f"Significant improvement in {dim}")
                elif change < -0.1:
                    comparison['recommendations'].append(f"Consider addressing decline in {dim}")
        
        return comparison
    
    def get_quality_trends(self, limit: int = 10) -> Dict[str, Any]:
        """Analyze quality trends from assessment history"""
        
        if len(self.assessment_history) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        recent_assessments = self.assessment_history[-limit:]
        
        # Calculate trend for overall quality
        overall_scores = [assessment['report'].overall_quality for assessment in recent_assessments]
        
        if len(overall_scores) >= 2:
            trend_slope = (overall_scores[-1] - overall_scores[0]) / (len(overall_scores) - 1)
            trend_direction = 'improving' if trend_slope > 0.01 else 'declining' if trend_slope < -0.01 else 'stable'
        else:
            trend_slope = 0.0
            trend_direction = 'stable'
        
        # Average scores by dimension
        dimension_averages = {}
        for dim in ['readability', 'coherence', 'structure', 'engagement', 'technical']:
            scores = []
            for assessment in recent_assessments:
                score_obj = getattr(assessment['report'], f"{dim}_score")
                if score_obj:
                    scores.append(score_obj.score)
            
            if scores:
                dimension_averages[dim] = sum(scores) / len(scores)
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': trend_slope,
            'average_quality': sum(overall_scores) / len(overall_scores),
            'dimension_averages': dimension_averages,
            'total_assessments': len(recent_assessments)
        }
    
    def export_quality_report(self, report: QualityReport, format: str = "json") -> str:
        """Export quality report in specified format"""
        
        if format == "json":
            import json
            
            export_data = {
                'content_id': report.content_id,
                'timestamp': report.assessment_timestamp.isoformat(),
                'overall_quality': report.overall_quality,
                'scores': report.get_score_summary(),
                'content_stats': {
                    'word_count': report.word_count,
                    'sentence_count': report.sentence_count,
                    'paragraph_count': report.paragraph_count
                },
                'detailed_scores': []
            }
            
            for score in report.get_all_scores():
                score_data = {
                    'dimension': score.dimension.value,
                    'score': score.score,
                    'explanation': score.explanation,
                    'factors': score.contributing_factors,
                    'recommendations': score.recommendations
                }
                export_data['detailed_scores'].append(score_data)
            
            return json.dumps(export_data, indent=2, default=str)
        
        elif format == "text":
            lines = [
                f"Quality Assessment Report - {report.content_id}",
                f"Generated: {report.assessment_timestamp}",
                f"Overall Quality: {report.overall_quality:.2f}/1.0",
                "",
                "Score Breakdown:"
            ]
            
            for score in report.get_all_scores():
                lines.extend([
                    f"  {score.dimension.value.title()}: {score.score:.2f}/1.0",
                    f"    {score.explanation}",
                    ""
                ])
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """Get comprehensive assessment statistics"""
        
        if not self.assessment_history:
            return {'total_assessments': 0}
        
        total_assessments = len(self.assessment_history)
        
        # Average quality scores
        overall_qualities = [assessment['report'].overall_quality for assessment in self.assessment_history]
        avg_overall_quality = sum(overall_qualities) / len(overall_qualities)
        
        # Content length statistics
        content_lengths = [assessment['content_length'] for assessment in self.assessment_history]
        avg_content_length = sum(content_lengths) / len(content_lengths)
        
        # Processing time statistics
        processing_times = [assessment['report'].processing_time_seconds for assessment in self.assessment_history]
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        return {
            'total_assessments': total_assessments,
            'average_overall_quality': avg_overall_quality,
            'average_content_length': avg_content_length,
            'average_processing_time': avg_processing_time,
            'quality_distribution': {
                'excellent': sum(1 for q in overall_qualities if q >= 0.9),
                'good': sum(1 for q in overall_qualities if 0.7 <= q < 0.9),
                'fair': sum(1 for q in overall_qualities if 0.5 <= q < 0.7),
                'poor': sum(1 for q in overall_qualities if q < 0.5)
            }
        }