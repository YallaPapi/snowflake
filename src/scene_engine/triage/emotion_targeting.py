"""
Emotion Targeting for Scene Redesign

TaskMaster Task 45.6: Emotion Targeting
Analyzes scenes for emotional impact and adjusts content to align with desired emotional targets.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import copy
import re

from ..models import SceneCard, SceneType


class EmotionTarget(Enum):
    """Target emotions for scene optimization"""
    TENSION = "tension"           # Suspense, anticipation, worry
    EMPATHY = "empathy"           # Understanding, connection, sympathy  
    EXCITEMENT = "excitement"     # Energy, enthusiasm, anticipation
    FEAR = "fear"                 # Anxiety, dread, concern
    HOPE = "hope"                 # Optimism, anticipation, desire
    SADNESS = "sadness"           # Melancholy, loss, disappointment
    ANGER = "anger"               # Frustration, rage, indignation
    JOY = "joy"                   # Happiness, delight, satisfaction
    SURPRISE = "surprise"         # Shock, amazement, unexpected
    CURIOSITY = "curiosity"       # Interest, intrigue, wonder


@dataclass
class EmotionAnalysis:
    """Analysis of emotional content in scene"""
    current_emotions: Dict[EmotionTarget, float]  # Detected emotion levels (0-1)
    emotional_intensity: float                    # Overall emotional intensity
    emotional_clarity: float                      # How clear the emotions are
    emotional_progression: List[EmotionTarget]    # Emotion sequence through scene
    missing_emotions: List[EmotionTarget]         # Emotions that should be present
    excessive_emotions: List[EmotionTarget]       # Emotions that are too strong


@dataclass
class EmotionTargetingRequest:
    """Request for emotion targeting"""
    scene_card: SceneCard
    target_emotion: EmotionTarget
    prose_content: Optional[str] = None
    target_intensity: float = 0.7              # Desired emotion intensity (0-1)
    allow_secondary_emotions: bool = True       # Allow other emotions alongside target
    preserve_scene_structure: bool = True      # Maintain G-C-S or R-D-D structure


class EmotionTargeter:
    """
    TaskMaster Task 45.6: Emotion Targeting
    
    Analyzes scenes for emotional impact and adjusts content to align with
    desired emotional targets while maintaining scene structure and crucible focus.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("EmotionTargeter")
        
        # Emotion word mapping for detection and enhancement
        self.emotion_words = {
            EmotionTarget.TENSION: {
                'detect': ['tense', 'nervous', 'worried', 'anxious', 'suspense', 'edge', 'waiting', 'uncertain'],
                'enhance': ['heart pounded', 'breath caught', 'muscles tensed', 'waited anxiously', 'gripped with worry']
            },
            EmotionTarget.EMPATHY: {
                'detect': ['understood', 'felt for', 'sympathized', 'connected', 'related', 'compassion'],
                'enhance': ['heart went out', 'deeply understood', 'felt their pain', 'shared the burden']
            },
            EmotionTarget.EXCITEMENT: {
                'detect': ['excited', 'thrilled', 'energized', 'eager', 'anticipation', 'pumped'],
                'enhance': ['pulse quickened', 'energy surged', 'could hardly contain', 'bubbling with excitement']
            },
            EmotionTarget.FEAR: {
                'detect': ['afraid', 'scared', 'terrified', 'frightened', 'dread', 'panic', 'horror'],
                'enhance': ['blood ran cold', 'terror gripped', 'paralyzed with fear', 'nightmare unfolding']
            },
            EmotionTarget.HOPE: {
                'detect': ['hope', 'optimistic', 'possibility', 'chance', 'maybe', 'potential', 'dream'],
                'enhance': ['dared to hope', 'glimmer of possibility', 'heart lifted', 'saw a way forward']
            },
            EmotionTarget.SADNESS: {
                'detect': ['sad', 'melancholy', 'grief', 'sorrow', 'loss', 'disappointed', 'heavy heart'],
                'enhance': ['weight of sorrow', 'tears threatened', 'heavy with loss', 'ache of disappointment']
            },
            EmotionTarget.ANGER: {
                'detect': ['angry', 'furious', 'rage', 'mad', 'frustrated', 'irritated', 'livid'],
                'enhance': ['anger flared', 'fury burned', 'blood boiled', 'jaw clenched in rage']
            },
            EmotionTarget.JOY: {
                'detect': ['happy', 'joyful', 'delighted', 'pleased', 'cheerful', 'elated', 'wonderful'],
                'enhance': ['heart soared', 'burst with joy', 'radiant with happiness', 'couldn\'t stop smiling']
            },
            EmotionTarget.SURPRISE: {
                'detect': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected', 'sudden'],
                'enhance': ['jaw dropped', 'eyes widened', 'caught completely off guard', 'couldn\'t believe']
            },
            EmotionTarget.CURIOSITY: {
                'detect': ['curious', 'wondered', 'intrigued', 'fascinated', 'mystery', 'question'],
                'enhance': ['burning curiosity', 'had to know', 'mystery beckoned', 'fascinated by the puzzle']
            }
        }
        
        # Scene type to emotion mapping
        self.scene_emotion_mapping = {
            SceneType.PROACTIVE: [EmotionTarget.TENSION, EmotionTarget.EXCITEMENT, EmotionTarget.HOPE],
            SceneType.REACTIVE: [EmotionTarget.EMPATHY, EmotionTarget.SADNESS, EmotionTarget.FEAR]
        }
    
    def apply_emotion_targeting(self, scene_card: SceneCard, prose_content: Optional[str],
                              target_emotion: EmotionTarget, preserve_crucible: bool = True) -> Dict[str, Any]:
        """
        Apply emotion targeting to scene
        
        Args:
            scene_card: Scene card to analyze and enhance
            prose_content: Prose content to analyze and enhance
            target_emotion: Target emotion to optimize for
            preserve_crucible: Whether to preserve scene crucible
            
        Returns:
            Dictionary with targeting results
        """
        
        self.logger.debug(f"Applying emotion targeting ({target_emotion.value}) to scene {scene_card.scene_id}")
        
        # Analyze current emotional content
        emotion_analysis = self._analyze_current_emotions(scene_card, prose_content)
        
        # Determine if targeting is needed
        current_level = emotion_analysis.current_emotions.get(target_emotion, 0.0)
        targeting_needed = current_level < 0.6  # Below satisfactory threshold
        
        updated_scene_card = copy.deepcopy(scene_card)
        updated_prose = prose_content
        targeting_applied = False
        
        if targeting_needed:
            self.logger.info(f"Enhancing {target_emotion.value} emotion (current level: {current_level:.2f})")
            
            # Apply scene card emotion targeting
            card_result = self._enhance_scene_card_emotion(
                updated_scene_card, target_emotion, emotion_analysis, preserve_crucible
            )
            
            if card_result['enhanced']:
                updated_scene_card = card_result['scene_card']
                targeting_applied = True
            
            # Apply prose emotion targeting
            if prose_content:
                prose_result = self._enhance_prose_emotion(
                    updated_prose, target_emotion, emotion_analysis, preserve_crucible
                )
                
                if prose_result['enhanced']:
                    updated_prose = prose_result['prose_content']
                    targeting_applied = True
        
        # Re-analyze after enhancement
        final_analysis = self._analyze_current_emotions(updated_scene_card, updated_prose)
        final_level = final_analysis.current_emotions.get(target_emotion, 0.0)
        
        return {
            'scene_card': updated_scene_card,
            'prose_content': updated_prose,
            'targeting_applied': targeting_applied,
            'emotion_analysis': {
                'initial': emotion_analysis,
                'final': final_analysis,
                'improvement': final_level - current_level
            },
            'target_emotion': target_emotion
        }
    
    def _analyze_current_emotions(self, scene_card: SceneCard, 
                                prose_content: Optional[str]) -> EmotionAnalysis:
        """Analyze current emotional content in scene"""
        
        current_emotions = {emotion: 0.0 for emotion in EmotionTarget}
        
        # Analyze scene card emotions
        card_emotions = self._analyze_scene_card_emotions(scene_card)
        for emotion, level in card_emotions.items():
            current_emotions[emotion] = max(current_emotions[emotion], level)
        
        # Analyze prose emotions if available
        if prose_content:
            prose_emotions = self._analyze_prose_emotions(prose_content)
            for emotion, level in prose_emotions.items():
                current_emotions[emotion] = max(current_emotions[emotion], level)
        
        # Calculate overall metrics
        emotional_intensity = sum(current_emotions.values()) / len(current_emotions)
        emotional_clarity = max(current_emotions.values()) - (sum(current_emotions.values()) - max(current_emotions.values())) / (len(current_emotions) - 1)
        
        # Determine emotion progression (simplified)
        emotion_progression = [emotion for emotion, level in current_emotions.items() if level > 0.3]
        emotion_progression.sort(key=lambda x: current_emotions[x], reverse=True)
        
        # Identify missing emotions based on scene type
        expected_emotions = self.scene_emotion_mapping.get(scene_card.scene_type, [])
        missing_emotions = [emotion for emotion in expected_emotions if current_emotions[emotion] < 0.3]
        
        # Identify excessive emotions
        excessive_emotions = [emotion for emotion, level in current_emotions.items() if level > 0.8]
        
        return EmotionAnalysis(
            current_emotions=current_emotions,
            emotional_intensity=emotional_intensity,
            emotional_clarity=emotional_clarity,
            emotional_progression=emotion_progression,
            missing_emotions=missing_emotions,
            excessive_emotions=excessive_emotions
        )
    
    def _analyze_scene_card_emotions(self, scene_card: SceneCard) -> Dict[EmotionTarget, float]:
        """Analyze emotions present in scene card structure"""
        
        emotions = {emotion: 0.0 for emotion in EmotionTarget}
        
        # Analyze scene crucible
        if scene_card.scene_crucible:
            crucible_emotions = self._detect_emotions_in_text(scene_card.scene_crucible)
            for emotion, level in crucible_emotions.items():
                emotions[emotion] = max(emotions[emotion], level)
        
        # Analyze scene type specific elements
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            if scene_card.proactive:
                # Goals often create tension/excitement
                if hasattr(scene_card.proactive, 'goal') and scene_card.proactive.goal:
                    goal_emotions = self._detect_emotions_in_text(scene_card.proactive.goal)
                    emotions[EmotionTarget.TENSION] = max(emotions[EmotionTarget.TENSION], goal_emotions.get(EmotionTarget.TENSION, 0.3))
                    emotions[EmotionTarget.HOPE] = max(emotions[EmotionTarget.HOPE], goal_emotions.get(EmotionTarget.HOPE, 0.3))
                
                # Conflicts create tension/fear
                if hasattr(scene_card.proactive, 'conflict') and scene_card.proactive.conflict:
                    conflict_emotions = self._detect_emotions_in_text(scene_card.proactive.conflict)
                    emotions[EmotionTarget.TENSION] = max(emotions[EmotionTarget.TENSION], conflict_emotions.get(EmotionTarget.TENSION, 0.4))
                
                # Setbacks create disappointment/sadness
                if hasattr(scene_card.proactive, 'setback') and scene_card.proactive.setback:
                    setback_emotions = self._detect_emotions_in_text(scene_card.proactive.setback)
                    emotions[EmotionTarget.SADNESS] = max(emotions[EmotionTarget.SADNESS], setback_emotions.get(EmotionTarget.SADNESS, 0.4))
        
        elif scene_card.scene_type == SceneType.REACTIVE and hasattr(scene_card, 'reactive'):
            if scene_card.reactive:
                # Reactions are inherently emotional
                if hasattr(scene_card.reactive, 'reaction') and scene_card.reactive.reaction:
                    reaction_emotions = self._detect_emotions_in_text(scene_card.reactive.reaction)
                    for emotion, level in reaction_emotions.items():
                        emotions[emotion] = max(emotions[emotion], level + 0.2)  # Boost detected emotions
                
                # Dilemmas create tension/fear
                if hasattr(scene_card.reactive, 'dilemma') and scene_card.reactive.dilemma:
                    dilemma_emotions = self._detect_emotions_in_text(scene_card.reactive.dilemma)
                    emotions[EmotionTarget.TENSION] = max(emotions[EmotionTarget.TENSION], 0.5)
                
                # Decisions can create various emotions
                if hasattr(scene_card.reactive, 'decision') and scene_card.reactive.decision:
                    decision_emotions = self._detect_emotions_in_text(scene_card.reactive.decision)
                    for emotion, level in decision_emotions.items():
                        emotions[emotion] = max(emotions[emotion], level)
        
        return emotions
    
    def _analyze_prose_emotions(self, prose_content: str) -> Dict[EmotionTarget, float]:
        """Analyze emotions present in prose content"""
        
        return self._detect_emotions_in_text(prose_content)
    
    def _detect_emotions_in_text(self, text: str) -> Dict[EmotionTarget, float]:
        """Detect emotion levels in text using word matching"""
        
        if not text:
            return {emotion: 0.0 for emotion in EmotionTarget}
        
        text_lower = text.lower()
        emotions = {emotion: 0.0 for emotion in EmotionTarget}
        
        for emotion, word_lists in self.emotion_words.items():
            detect_words = word_lists['detect']
            
            # Count emotion word occurrences
            emotion_count = 0
            for word in detect_words:
                emotion_count += text_lower.count(word)
            
            # Convert to emotion level (0-1)
            # Normalize by text length and cap at 1.0
            text_words = len(text.split())
            if text_words > 0:
                emotions[emotion] = min(1.0, emotion_count / max(1, text_words // 10))
        
        return emotions
    
    def _enhance_scene_card_emotion(self, scene_card: SceneCard, target_emotion: EmotionTarget,
                                   emotion_analysis: EmotionAnalysis, preserve_crucible: bool) -> Dict[str, Any]:
        """Enhance emotion in scene card elements"""
        
        enhanced = False
        
        # Enhance scene crucible if not preserving exactly
        if not preserve_crucible and scene_card.scene_crucible:
            enhanced_crucible = self._add_emotional_language(
                scene_card.scene_crucible, target_emotion, intensity=0.3
            )
            if enhanced_crucible != scene_card.scene_crucible:
                scene_card.scene_crucible = enhanced_crucible
                enhanced = True
        
        # Enhance scene type specific elements
        if scene_card.scene_type == SceneType.PROACTIVE and hasattr(scene_card, 'proactive'):
            if scene_card.proactive:
                # Enhance goal with target emotion
                if hasattr(scene_card.proactive, 'goal') and scene_card.proactive.goal:
                    enhanced_goal = self._add_emotional_language(
                        scene_card.proactive.goal, target_emotion, intensity=0.2
                    )
                    if enhanced_goal != scene_card.proactive.goal:
                        scene_card.proactive.goal = enhanced_goal
                        enhanced = True
                
                # Enhance conflict for tension/fear
                if hasattr(scene_card.proactive, 'conflict') and scene_card.proactive.conflict:
                    conflict_emotion = target_emotion if target_emotion in [EmotionTarget.TENSION, EmotionTarget.FEAR] else EmotionTarget.TENSION
                    enhanced_conflict = self._add_emotional_language(
                        scene_card.proactive.conflict, conflict_emotion, intensity=0.3
                    )
                    if enhanced_conflict != scene_card.proactive.conflict:
                        scene_card.proactive.conflict = enhanced_conflict
                        enhanced = True
                
                # Enhance setback for appropriate emotion
                if hasattr(scene_card.proactive, 'setback') and scene_card.proactive.setback:
                    setback_emotion = target_emotion if target_emotion in [EmotionTarget.SADNESS, EmotionTarget.FEAR, EmotionTarget.ANGER] else EmotionTarget.SADNESS
                    enhanced_setback = self._add_emotional_language(
                        scene_card.proactive.setback, setback_emotion, intensity=0.4
                    )
                    if enhanced_setback != scene_card.proactive.setback:
                        scene_card.proactive.setback = enhanced_setback
                        enhanced = True
        
        elif scene_card.scene_type == SceneType.REACTIVE and hasattr(scene_card, 'reactive'):
            if scene_card.reactive:
                # Enhance reaction with target emotion
                if hasattr(scene_card.reactive, 'reaction') and scene_card.reactive.reaction:
                    enhanced_reaction = self._add_emotional_language(
                        scene_card.reactive.reaction, target_emotion, intensity=0.5
                    )
                    if enhanced_reaction != scene_card.reactive.reaction:
                        scene_card.reactive.reaction = enhanced_reaction
                        enhanced = True
                
                # Enhance dilemma for tension
                if hasattr(scene_card.reactive, 'dilemma') and scene_card.reactive.dilemma:
                    dilemma_emotion = EmotionTarget.TENSION
                    enhanced_dilemma = self._add_emotional_language(
                        scene_card.reactive.dilemma, dilemma_emotion, intensity=0.3
                    )
                    if enhanced_dilemma != scene_card.reactive.dilemma:
                        scene_card.reactive.dilemma = enhanced_dilemma
                        enhanced = True
                
                # Enhance decision with appropriate emotion
                if hasattr(scene_card.reactive, 'decision') and scene_card.reactive.decision:
                    enhanced_decision = self._add_emotional_language(
                        scene_card.reactive.decision, target_emotion, intensity=0.3
                    )
                    if enhanced_decision != scene_card.reactive.decision:
                        scene_card.reactive.decision = enhanced_decision
                        enhanced = True
        
        return {
            'enhanced': enhanced,
            'scene_card': scene_card
        }
    
    def _enhance_prose_emotion(self, prose_content: str, target_emotion: EmotionTarget,
                             emotion_analysis: EmotionAnalysis, preserve_crucible: bool) -> Dict[str, Any]:
        """Enhance emotion in prose content"""
        
        if not prose_content:
            return {'enhanced': False, 'prose_content': prose_content}
        
        enhanced_prose = prose_content
        
        # Add emotional enhancement phrases
        enhancement_phrases = self.emotion_words[target_emotion]['enhance']
        
        # Find good insertion points (end of paragraphs, after dialogue)
        paragraphs = enhanced_prose.split('\n\n')
        enhanced_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            enhanced_paragraph = paragraph
            
            # Add emotional enhancement to every other paragraph (not too aggressive)
            if i % 2 == 0 and len(enhancement_phrases) > i // 2:
                enhancement = enhancement_phrases[i // 2]
                
                # Find good insertion point in paragraph
                sentences = paragraph.split('.')
                if len(sentences) > 1:
                    # Insert before last sentence
                    enhanced_paragraph = '. '.join(sentences[:-1]) + f'. {enhancement}.' + sentences[-1]
                else:
                    # Add at end
                    enhanced_paragraph += f' {enhancement}.'
            
            enhanced_paragraphs.append(enhanced_paragraph)
        
        enhanced_prose = '\n\n'.join(enhanced_paragraphs)
        
        # Check if meaningful enhancement was made
        enhanced = enhanced_prose != prose_content and len(enhanced_prose) > len(prose_content) * 1.05
        
        return {
            'enhanced': enhanced,
            'prose_content': enhanced_prose
        }
    
    def _add_emotional_language(self, text: str, emotion: EmotionTarget, intensity: float = 0.3) -> str:
        """Add emotional language to text"""
        
        if not text or emotion not in self.emotion_words:
            return text
        
        # Get enhancement words for this emotion
        enhancement_words = self.emotion_words[emotion]['enhance']
        
        if not enhancement_words:
            return text
        
        # Choose enhancement based on intensity
        enhancement_index = min(len(enhancement_words) - 1, int(intensity * len(enhancement_words)))
        enhancement = enhancement_words[enhancement_index]
        
        # Add enhancement to text (simple approach - append or insert)
        if len(text.split()) < 10:  # Short text - append
            enhanced = f"{text}, {enhancement}"
        else:  # Longer text - insert in middle
            words = text.split()
            middle_point = len(words) // 2
            words.insert(middle_point, f"({enhancement})")
            enhanced = ' '.join(words)
        
        return enhanced
    
    def recommend_emotion_target(self, scene_card: SceneCard) -> EmotionTarget:
        """Recommend appropriate emotion target based on scene"""
        
        # Base recommendation on scene type
        if scene_card.scene_type == SceneType.PROACTIVE:
            # Proactive scenes usually benefit from tension or excitement
            return EmotionTarget.TENSION
        else:  # REACTIVE
            # Reactive scenes usually benefit from empathy or sadness
            return EmotionTarget.EMPATHY
    
    def get_emotion_targeting_statistics(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get emotion targeting usage statistics"""
        
        if not history:
            return {'total_targeting_sessions': 0}
        
        total_sessions = len(history)
        successful_sessions = sum(1 for session in history if session.get('targeting_applied', False))
        
        # Emotion target usage
        emotion_usage = {emotion.value: 0 for emotion in EmotionTarget}
        for session in history:
            target = session.get('target_emotion')
            if target:
                emotion_usage[target.value] += 1
        
        # Improvement statistics
        improvements = []
        for session in history:
            analysis = session.get('emotion_analysis', {})
            improvement = analysis.get('improvement', 0.0)
            improvements.append(improvement)
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
        
        return {
            'total_targeting_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'success_rate': successful_sessions / total_sessions if total_sessions > 0 else 0,
            'emotion_target_usage': emotion_usage,
            'average_emotion_improvement': avg_improvement,
            'most_targeted_emotion': max(emotion_usage, key=emotion_usage.get),
            'improvement_distribution': {
                'significant_improvement': sum(1 for imp in improvements if imp > 0.3),
                'moderate_improvement': sum(1 for imp in improvements if 0.1 <= imp <= 0.3),
                'minimal_improvement': sum(1 for imp in improvements if imp < 0.1)
            }
        }