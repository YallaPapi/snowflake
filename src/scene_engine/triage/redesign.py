"""
Scene Redesign Pipeline

TaskMaster Task 45.2-45.7: Redesign pipeline for MAYBE scenes following Step 14 protocol
Includes scene type correction, part rewriting, compression decisions, emotion targeting,
and re-validation with re-triage steps.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import copy

from ..models import SceneCard, SceneType
from ..validation.service import SceneValidationService
from ..drafting.service import SceneDraftingService, DraftingRequest
from .corrections import SceneTypeCorrector, PartRewriter, CompressionDecider
from .emotion_targeting import EmotionTargeter, EmotionTarget


class RedesignStep(Enum):
    """Steps in the redesign pipeline following Step 14 protocol"""
    SCENE_TYPE_CORRECTION = "scene_type_correction"
    PART_REWRITING = "part_rewriting"  
    COMPRESSION_DECISION = "compression_decision"
    EMOTION_TARGETING = "emotion_targeting"
    RE_VALIDATION = "re_validation"
    RE_TRIAGE = "re_triage"


@dataclass
class RedesignRequest:
    """Request for scene redesign pipeline"""
    scene_card: SceneCard
    prose_content: Optional[str] = None
    
    # Redesign targets
    target_quality_score: float = 0.8
    target_structure_adherence: float = 0.9
    target_validation_pass_rate: float = 0.95
    
    # Redesign settings
    max_attempts: int = 3
    enable_scene_type_correction: bool = True
    enable_part_rewriting: bool = True
    enable_compression: bool = True
    enable_emotion_targeting: bool = True
    
    # Step-specific settings
    compression_threshold: float = 0.8  # Compress if scene is too verbose
    emotion_target: Optional[EmotionTarget] = None
    preserve_scene_crucible: bool = True
    
    # Quality thresholds for each step
    quality_improvement_threshold: float = 0.1  # Minimum improvement to continue


@dataclass
class RedesignResponse:
    """Response from redesign pipeline"""
    success: bool
    redesign_attempts: int = 0
    
    # Results by step
    corrections_applied: List[str] = field(default_factory=list)
    parts_rewritten: List[str] = field(default_factory=list)
    compression_applied: bool = False
    emotion_targeting_applied: bool = False
    
    # Quality progression
    initial_quality_score: float = 0.0
    final_quality_score: float = 0.0
    quality_improvement: float = 0.0
    
    # Final outputs
    final_scene_card: Optional[SceneCard] = None
    final_prose_content: Optional[str] = None
    
    # Processing information
    steps_executed: List[RedesignStep] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    
    # Error and warning information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    step_results: Dict[str, Any] = field(default_factory=dict)


class RedesignPipeline:
    """
    TaskMaster Task 45.2: Redesign Pipeline for MAYBE Scenes
    
    Implements Step 14 protocol for redesigning scenes that received MAYBE classification.
    Coordinates scene type correction, part rewriting, compression, emotion targeting,
    and re-validation steps to improve scene quality.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("RedesignPipeline")
        
        # Initialize correction components
        self.scene_type_corrector = SceneTypeCorrector()
        self.part_rewriter = PartRewriter()
        self.compression_decider = CompressionDecider()
        self.emotion_targeter = EmotionTargeter()
        
        # Initialize services
        self.validation_service = SceneValidationService()
        self.drafting_service = SceneDraftingService()
        
        # Pipeline statistics
        self.redesign_history = []
    
    def redesign_scene(self, request: RedesignRequest) -> RedesignResponse:
        """
        Execute redesign pipeline following Step 14 protocol
        
        Step 14 Protocol:
        1. Scene type correction
        2. Part rewriting for problematic sections
        3. Compression decision and application
        4. Emotion targeting alignment
        5. Re-validation
        6. Re-triage (handled by calling service)
        """
        
        start_time = datetime.now()
        
        response = RedesignResponse(
            success=False,
            initial_quality_score=self._calculate_initial_quality_score(request)
        )
        
        try:
            self.logger.info(f"Starting redesign pipeline for scene {request.scene_card.scene_id}")
            
            # Initialize working copies
            current_scene_card = copy.deepcopy(request.scene_card)
            current_prose = request.prose_content
            
            # Execute redesign pipeline
            for attempt in range(request.max_attempts):
                response.redesign_attempts = attempt + 1
                
                self.logger.debug(f"Redesign attempt {attempt + 1}/{request.max_attempts}")
                
                # Step 1: Scene Type Correction (Task 45.3)
                if request.enable_scene_type_correction:
                    correction_result = self._apply_scene_type_correction(
                        current_scene_card, current_prose, request
                    )
                    
                    if correction_result['corrections_applied']:
                        current_scene_card = correction_result['scene_card']
                        current_prose = correction_result['prose_content']
                        response.corrections_applied.extend(correction_result['corrections_applied'])
                        response.steps_executed.append(RedesignStep.SCENE_TYPE_CORRECTION)
                        response.step_results['scene_type_correction'] = correction_result
                
                # Step 2: Part Rewriting (Task 45.4)
                if request.enable_part_rewriting:
                    rewriting_result = self._apply_part_rewriting(
                        current_scene_card, current_prose, request
                    )
                    
                    if rewriting_result['parts_rewritten']:
                        current_scene_card = rewriting_result['scene_card']
                        current_prose = rewriting_result['prose_content']
                        response.parts_rewritten.extend(rewriting_result['parts_rewritten'])
                        response.steps_executed.append(RedesignStep.PART_REWRITING)
                        response.step_results['part_rewriting'] = rewriting_result
                
                # Step 3: Compression Decision (Task 45.5)
                if request.enable_compression:
                    compression_result = self._apply_compression_decision(
                        current_scene_card, current_prose, request
                    )
                    
                    if compression_result['compression_applied']:
                        current_scene_card = compression_result['scene_card']
                        current_prose = compression_result['prose_content']
                        response.compression_applied = True
                        response.steps_executed.append(RedesignStep.COMPRESSION_DECISION)
                        response.step_results['compression'] = compression_result
                
                # Step 4: Emotion Targeting (Task 45.6)
                if request.enable_emotion_targeting:
                    emotion_result = self._apply_emotion_targeting(
                        current_scene_card, current_prose, request
                    )
                    
                    if emotion_result['targeting_applied']:
                        current_scene_card = emotion_result['scene_card']
                        current_prose = emotion_result['prose_content']
                        response.emotion_targeting_applied = True
                        response.steps_executed.append(RedesignStep.EMOTION_TARGETING)
                        response.step_results['emotion_targeting'] = emotion_result
                
                # Step 5: Re-validation (Task 45.7)
                validation_result = self._apply_re_validation(current_scene_card, current_prose)
                response.steps_executed.append(RedesignStep.RE_VALIDATION)
                response.step_results['validation'] = validation_result
                
                # Calculate quality after this attempt
                current_quality = self._calculate_quality_score(current_scene_card, current_prose, validation_result)
                
                # Check if target quality reached
                if (current_quality >= request.target_quality_score and
                    validation_result.get('pass_rate', 0) >= request.target_validation_pass_rate):
                    
                    response.final_quality_score = current_quality
                    response.final_scene_card = current_scene_card
                    response.final_prose_content = current_prose
                    response.success = True
                    break
                
                # Check if sufficient improvement made
                improvement = current_quality - response.initial_quality_score
                if improvement < request.quality_improvement_threshold and attempt > 0:
                    response.warnings.append(f"Insufficient quality improvement ({improvement:.2f}) after attempt {attempt + 1}")
                    break
            
            # Final quality calculation
            response.final_quality_score = self._calculate_quality_score(
                current_scene_card, current_prose, response.step_results.get('validation', {})
            )
            response.quality_improvement = response.final_quality_score - response.initial_quality_score
            
            # Set final outputs even if not fully successful
            response.final_scene_card = current_scene_card
            response.final_prose_content = current_prose
            
            if not response.success and response.quality_improvement > 0:
                response.success = True  # Partial success
                response.warnings.append("Did not reach target quality but achieved improvement")
        
        except Exception as e:
            self.logger.error(f"Redesign pipeline error: {e}")
            response.error_message = str(e)
        
        finally:
            response.processing_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # Add to history
            self.redesign_history.append({
                'request': request,
                'response': response,
                'timestamp': start_time
            })
        
        return response
    
    def _apply_scene_type_correction(self, scene_card: SceneCard, prose_content: Optional[str],
                                   request: RedesignRequest) -> Dict[str, Any]:
        """
        TaskMaster Task 45.3: Scene Type Correction
        Identify and correct scene type mismatches during redesign.
        """
        
        self.logger.debug(f"Applying scene type correction for scene {scene_card.scene_id}")
        
        return self.scene_type_corrector.correct_scene_type(
            scene_card=scene_card,
            prose_content=prose_content,
            preserve_crucible=request.preserve_scene_crucible
        )
    
    def _apply_part_rewriting(self, scene_card: SceneCard, prose_content: Optional[str],
                            request: RedesignRequest) -> Dict[str, Any]:
        """
        TaskMaster Task 45.4: Part Rewriting Logic
        Identify and rewrite problematic scene parts.
        """
        
        self.logger.debug(f"Applying part rewriting for scene {scene_card.scene_id}")
        
        return self.part_rewriter.rewrite_problematic_parts(
            scene_card=scene_card,
            prose_content=prose_content,
            target_quality=request.target_quality_score,
            preserve_crucible=request.preserve_scene_crucible
        )
    
    def _apply_compression_decision(self, scene_card: SceneCard, prose_content: Optional[str],
                                  request: RedesignRequest) -> Dict[str, Any]:
        """
        TaskMaster Task 45.5: Compression Decision Logic
        Determine if compression is needed and apply it.
        """
        
        self.logger.debug(f"Applying compression decision for scene {scene_card.scene_id}")
        
        return self.compression_decider.decide_and_compress(
            scene_card=scene_card,
            prose_content=prose_content,
            compression_threshold=request.compression_threshold,
            preserve_crucible=request.preserve_scene_crucible
        )
    
    def _apply_emotion_targeting(self, scene_card: SceneCard, prose_content: Optional[str],
                               request: RedesignRequest) -> Dict[str, Any]:
        """
        TaskMaster Task 45.6: Emotion Targeting
        Apply emotion targeting to align with intended emotional response.
        """
        
        self.logger.debug(f"Applying emotion targeting for scene {scene_card.scene_id}")
        
        emotion_target = request.emotion_target or self._determine_emotion_target(scene_card)
        
        return self.emotion_targeter.apply_emotion_targeting(
            scene_card=scene_card,
            prose_content=prose_content,
            target_emotion=emotion_target,
            preserve_crucible=request.preserve_scene_crucible
        )
    
    def _apply_re_validation(self, scene_card: SceneCard, prose_content: Optional[str]) -> Dict[str, Any]:
        """
        TaskMaster Task 45.7: Re-validation
        Run full validation checks after redesign steps.
        """
        
        self.logger.debug(f"Applying re-validation for scene {scene_card.scene_id}")
        
        # Run validation using validation service
        validation_request = {
            'scene_card': scene_card,
            'prose_content': prose_content,
            'run_all_validators': True
        }
        
        validation_report = self.validation_service.validate_scene_complete(validation_request)
        
        # Calculate pass rate
        passed_validations = sum(1 for result in validation_report.validation_results 
                               if result.get('passed', False))
        total_validations = len(validation_report.validation_results)
        pass_rate = passed_validations / total_validations if total_validations > 0 else 0.0
        
        return {
            'validation_report': validation_report,
            'pass_rate': pass_rate,
            'passed_validations': passed_validations,
            'total_validations': total_validations
        }
    
    def _calculate_initial_quality_score(self, request: RedesignRequest) -> float:
        """Calculate initial quality score for baseline"""
        
        # Use simplified quality calculation
        structure_score = self._calculate_structure_completeness(request.scene_card)
        
        prose_score = 0.5  # Default if no prose
        if request.prose_content:
            prose_score = self._calculate_prose_quality(request.prose_content)
        
        return (structure_score + prose_score) / 2
    
    def _calculate_quality_score(self, scene_card: SceneCard, prose_content: Optional[str],
                               validation_result: Dict[str, Any]) -> float:
        """Calculate current quality score"""
        
        structure_score = self._calculate_structure_completeness(scene_card)
        
        prose_score = 0.5
        if prose_content:
            prose_score = self._calculate_prose_quality(prose_content)
        
        validation_score = validation_result.get('pass_rate', 0.5)
        
        # Weighted average
        return (structure_score * 0.4 + prose_score * 0.4 + validation_score * 0.2)
    
    def _calculate_structure_completeness(self, scene_card: SceneCard) -> float:
        """Calculate scene structure completeness score"""
        
        score = 0.0
        
        # Basic fields
        if scene_card.scene_crucible:
            score += 0.2
        if scene_card.pov_character:
            score += 0.1
        if scene_card.pov:
            score += 0.1
        if scene_card.tense:
            score += 0.1
        
        # Scene type specific structure
        if scene_card.scene_type == SceneType.PROACTIVE:
            if hasattr(scene_card, 'proactive') and scene_card.proactive:
                proactive = scene_card.proactive
                if hasattr(proactive, 'goal') and proactive.goal:
                    score += 0.15
                if hasattr(proactive, 'conflict') and proactive.conflict:
                    score += 0.15
                if hasattr(proactive, 'setback') and proactive.setback:
                    score += 0.15
        elif scene_card.scene_type == SceneType.REACTIVE:
            if hasattr(scene_card, 'reactive') and scene_card.reactive:
                reactive = scene_card.reactive
                if hasattr(reactive, 'reaction') and reactive.reaction:
                    score += 0.15
                if hasattr(reactive, 'dilemma') and reactive.dilemma:
                    score += 0.15
                if hasattr(reactive, 'decision') and reactive.decision:
                    score += 0.15
        
        return min(1.0, score)
    
    def _calculate_prose_quality(self, prose_content: str) -> float:
        """Calculate prose quality score (simplified)"""
        
        words = prose_content.split()
        if not words:
            return 0.0
        
        score = 0.0
        
        # Word count in reasonable range
        word_count = len(words)
        if 200 <= word_count <= 1000:
            score += 0.3
        elif word_count < 200:
            score += 0.3 * (word_count / 200)
        else:
            score += 0.3 * (1000 / word_count)
        
        # Sentence variety
        sentences = prose_content.split('.')
        if len(sentences) > 1:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 8 <= avg_sentence_length <= 20:
                score += 0.25
        
        # Dialogue presence
        dialogue_count = prose_content.count('"')
        if dialogue_count >= 2:  # At least one dialogue exchange
            score += 0.2
        
        # Basic flow indicators
        transition_words = ['however', 'then', 'but', 'meanwhile', 'suddenly']
        if any(word in prose_content.lower() for word in transition_words):
            score += 0.15
        
        # Vocabulary variety (simplified)
        unique_words = len(set(word.lower() for word in words))
        vocab_ratio = unique_words / len(words)
        if vocab_ratio > 0.6:
            score += 0.1
        
        return min(1.0, score)
    
    def _determine_emotion_target(self, scene_card: SceneCard) -> EmotionTarget:
        """Determine appropriate emotion target based on scene card"""
        
        # Default emotion targets based on scene type
        if scene_card.scene_type == SceneType.PROACTIVE:
            return EmotionTarget.TENSION  # Goal pursuit creates tension
        else:  # REACTIVE
            return EmotionTarget.EMPATHY  # Reaction scenes create empathy
    
    def get_redesign_statistics(self) -> Dict[str, Any]:
        """Get redesign pipeline statistics"""
        
        if not self.redesign_history:
            return {'total_redesigns': 0}
        
        total_redesigns = len(self.redesign_history)
        successful_redesigns = sum(1 for entry in self.redesign_history if entry['response'].success)
        
        # Step usage statistics
        step_usage = {step.value: 0 for step in RedesignStep}
        for entry in self.redesign_history:
            for step in entry['response'].steps_executed:
                step_usage[step.value] += 1
        
        # Quality improvement statistics
        quality_improvements = [entry['response'].quality_improvement for entry in self.redesign_history]
        avg_quality_improvement = sum(quality_improvements) / len(quality_improvements)
        
        # Attempt statistics
        attempt_counts = [entry['response'].redesign_attempts for entry in self.redesign_history]
        avg_attempts = sum(attempt_counts) / len(attempt_counts)
        
        return {
            'total_redesigns': total_redesigns,
            'successful_redesigns': successful_redesigns,
            'success_rate': successful_redesigns / total_redesigns,
            'average_quality_improvement': avg_quality_improvement,
            'average_attempts': avg_attempts,
            'step_usage_counts': step_usage,
            'step_usage_percentages': {
                step: (count / total_redesigns * 100) if total_redesigns > 0 else 0
                for step, count in step_usage.items()
            }
        }