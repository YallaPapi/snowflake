"""
Scene Triage Service Implementation

TaskMaster Task 45: Scene Triage Service
Implements YES/NO/MAYBE classification and redesign pipeline following Step 14 protocol.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from ..models import SceneCard, SceneType
from ..validation.service import SceneValidationService, ValidationReport
from ..drafting.service import SceneDraftingService, DraftingRequest
from .classifier import TriageClassifier, ClassificationCriteria
from .redesign import RedesignPipeline, RedesignRequest


class TriageDecision(Enum):
    """Triage classification decisions"""
    YES = "yes"      # Scene is ready for production
    NO = "no"        # Scene should be rejected/replaced
    MAYBE = "maybe"  # Scene needs redesign before acceptance


@dataclass
class TriageRequest:
    """Request for scene triage evaluation"""
    scene_card: SceneCard
    
    # Optional prose content for evaluation
    prose_content: Optional[str] = None
    
    # Classification criteria overrides
    custom_criteria: Optional[ClassificationCriteria] = None
    
    # Validation settings
    run_full_validation: bool = True
    include_prose_analysis: bool = True
    
    # Redesign settings for MAYBE scenes
    auto_redesign_maybe: bool = True
    max_redesign_attempts: int = 3
    
    # Quality thresholds
    minimum_quality_score: float = 0.7
    minimum_structure_adherence: float = 0.8


@dataclass
class TriageResponse:
    """Response from scene triage evaluation"""
    success: bool
    decision: TriageDecision
    
    # Evaluation details
    classification_score: float = 0.0
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    validation_report: Optional[ValidationReport] = None
    
    # Issues and recommendations  
    identified_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Redesign information (for MAYBE scenes)
    redesign_applied: bool = False
    redesign_attempts: int = 0
    redesign_results: Dict[str, Any] = field(default_factory=dict)
    
    # Processing information
    processing_time_seconds: float = 0.0
    components_evaluated: List[str] = field(default_factory=list)
    
    # Final outputs
    final_scene_card: Optional[SceneCard] = None
    final_prose_content: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class SceneTriageService:
    """
    TaskMaster Task 45: Scene Triage Service
    
    Implements YES/NO/MAYBE classification system for scene evaluation.
    Provides redesign pipeline for MAYBE scenes following Step 14 protocol.
    Includes scene type correction, part rewriting, compression decisions,
    and emotion targeting with re-validation and re-triage steps.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SceneTriageService")
        
        # Initialize components
        self.classifier = TriageClassifier()
        self.validation_service = SceneValidationService()
        self.drafting_service = SceneDraftingService()
        self.redesign_pipeline = RedesignPipeline()
        
        # Statistics
        self.triage_history = []
        self.decision_counts = {decision.value: 0 for decision in TriageDecision}
        
    def evaluate_scene(self, request: TriageRequest) -> TriageResponse:
        """
        TaskMaster Task 45 - Core functionality:
        Evaluate scene and classify as YES/NO/MAYBE.
        Apply redesign pipeline for MAYBE scenes.
        Return final triage decision with supporting data.
        """
        
        start_time = datetime.now()
        
        response = TriageResponse(
            success=False,
            decision=TriageDecision.NO
        )
        
        try:
            self.logger.info(f"Starting triage evaluation for scene: {request.scene_card.scene_id}")
            
            # Step 1: Initial validation if requested
            if request.run_full_validation:
                response.validation_report = self._run_full_validation(request.scene_card)
                response.components_evaluated.append("validation")
            
            # Step 2: Generate or analyze prose content
            prose_content = request.prose_content
            if not prose_content and request.include_prose_analysis:
                prose_content = self._generate_prose_for_analysis(request.scene_card)
                response.components_evaluated.append("prose_generation")
            
            # Step 3: Run triage classification
            classification_result = self._classify_scene(request, prose_content)
            response.decision = classification_result['decision']
            response.classification_score = classification_result['score']
            response.quality_metrics = classification_result['metrics']
            response.identified_issues = classification_result['issues']
            response.recommendations = classification_result['recommendations']
            response.components_evaluated.append("classification")
            
            # Step 4: Handle MAYBE scenes with redesign pipeline
            if response.decision == TriageDecision.MAYBE and request.auto_redesign_maybe:
                redesign_result = self._apply_redesign_pipeline(request, prose_content)
                
                response.redesign_applied = redesign_result['applied']
                response.redesign_attempts = redesign_result['attempts']
                response.redesign_results = redesign_result['results']
                response.components_evaluated.append("redesign")
                
                # Re-triage after redesign
                if redesign_result['success']:
                    response.final_scene_card = redesign_result['scene_card']
                    response.final_prose_content = redesign_result['prose_content']
                    
                    # Re-run classification
                    re_triage_request = TriageRequest(
                        scene_card=response.final_scene_card,
                        prose_content=response.final_prose_content,
                        custom_criteria=request.custom_criteria,
                        auto_redesign_maybe=False  # Prevent infinite recursion
                    )
                    
                    re_classification = self._classify_scene(re_triage_request, response.final_prose_content)
                    response.decision = re_classification['decision']
                    response.classification_score = re_classification['score']
                    response.components_evaluated.append("re_triage")
            
            # Step 5: Final decision validation
            if response.decision == TriageDecision.YES:
                # Ensure minimum quality thresholds are met
                if response.classification_score < request.minimum_quality_score:
                    response.decision = TriageDecision.MAYBE
                    response.warnings.append(f"Quality score {response.classification_score:.2f} below threshold {request.minimum_quality_score}")
            
            # Update statistics
            self.decision_counts[response.decision.value] += 1
            response.success = True
            
        except Exception as e:
            self.logger.error(f"Triage evaluation error: {e}")
            response.error_message = str(e)
        
        finally:
            response.processing_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # Add to history
            self.triage_history.append({
                'request': request,
                'response': response,
                'timestamp': start_time
            })
        
        return response
    
    def _run_full_validation(self, scene_card: SceneCard) -> ValidationReport:
        """Run full validation on scene card"""
        
        self.logger.debug(f"Running full validation for scene {scene_card.scene_id}")
        
        # Use existing validation service
        validation_request = {
            'scene_card': scene_card,
            'run_all_validators': True
        }
        
        return self.validation_service.validate_scene_complete(validation_request)
    
    def _generate_prose_for_analysis(self, scene_card: SceneCard) -> str:
        """Generate prose content for analysis if not provided"""
        
        self.logger.debug(f"Generating prose for analysis: {scene_card.scene_id}")
        
        # Use drafting service to generate prose
        drafting_request = DraftingRequest(
            scene_card=scene_card,
            target_word_count=600,
            validate_structure_adherence=True,
            validate_pov_consistency=True
        )
        
        drafting_response = self.drafting_service.draft_scene_prose(drafting_request)
        
        if drafting_response.success:
            return drafting_response.prose_content
        else:
            self.logger.warning(f"Failed to generate prose for analysis: {drafting_response.error_message}")
            return ""
    
    def _classify_scene(self, request: TriageRequest, prose_content: Optional[str]) -> Dict[str, Any]:
        """
        TaskMaster Task 45.1: YES/NO/MAYBE Classification Logic
        Core triage classification based on evaluation criteria.
        """
        
        criteria = request.custom_criteria or self._get_default_classification_criteria()
        
        return self.classifier.classify_scene(
            scene_card=request.scene_card,
            prose_content=prose_content,
            validation_report=getattr(request, 'validation_report', None),
            criteria=criteria
        )
    
    def _apply_redesign_pipeline(self, request: TriageRequest, prose_content: Optional[str]) -> Dict[str, Any]:
        """
        TaskMaster Task 45.2-45.7: Apply redesign pipeline for MAYBE scenes
        Implements Step 14 protocol with scene type correction, part rewriting,
        compression decisions, emotion targeting, and re-validation.
        """
        
        self.logger.info(f"Applying redesign pipeline to scene {request.scene_card.scene_id}")
        
        redesign_request = RedesignRequest(
            scene_card=request.scene_card,
            prose_content=prose_content,
            max_attempts=request.max_redesign_attempts,
            target_quality_score=request.minimum_quality_score,
            target_structure_adherence=request.minimum_structure_adherence
        )
        
        redesign_response = self.redesign_pipeline.redesign_scene(redesign_request)
        
        return {
            'applied': True,
            'success': redesign_response.success,
            'attempts': redesign_response.redesign_attempts,
            'results': {
                'corrections_applied': redesign_response.corrections_applied,
                'parts_rewritten': redesign_response.parts_rewritten,
                'compression_applied': redesign_response.compression_applied,
                'emotion_targeting_applied': redesign_response.emotion_targeting_applied,
                'final_quality_score': redesign_response.final_quality_score
            },
            'scene_card': redesign_response.final_scene_card,
            'prose_content': redesign_response.final_prose_content,
            'error': redesign_response.error_message
        }
    
    def _get_default_classification_criteria(self) -> ClassificationCriteria:
        """Get default classification criteria for triage"""
        
        return ClassificationCriteria(
            # YES thresholds (scene ready for production)
            yes_quality_threshold=0.8,
            yes_structure_adherence=0.9,
            yes_validation_pass_rate=0.95,
            
            # NO thresholds (scene should be rejected)
            no_quality_threshold=0.4,
            no_structure_adherence=0.5,
            no_validation_pass_rate=0.6,
            
            # Quality weights
            structure_weight=0.3,
            prose_quality_weight=0.25,
            validation_weight=0.25,
            snowflake_adherence_weight=0.2,
            
            # Scene-specific criteria
            require_scene_crucible=True,
            require_complete_structure=True,
            allow_minor_pov_inconsistencies=True
        )
    
    def get_triage_statistics(self) -> Dict[str, Any]:
        """Get triage service statistics"""
        
        if not self.triage_history:
            return {'total_evaluations': 0}
        
        total_evaluations = len(self.triage_history)
        
        # Calculate averages
        avg_processing_time = sum(entry['response'].processing_time_seconds for entry in self.triage_history) / total_evaluations
        avg_classification_score = sum(entry['response'].classification_score for entry in self.triage_history) / total_evaluations
        
        # Redesign statistics
        redesign_applied_count = sum(1 for entry in self.triage_history if entry['response'].redesign_applied)
        successful_redesigns = sum(1 for entry in self.triage_history 
                                 if entry['response'].redesign_applied and 
                                    entry['response'].redesign_results.get('success', False))
        
        return {
            'total_evaluations': total_evaluations,
            'decision_counts': self.decision_counts.copy(),
            'decision_percentages': {
                decision: (count / total_evaluations * 100) if total_evaluations > 0 else 0
                for decision, count in self.decision_counts.items()
            },
            'average_processing_time': avg_processing_time,
            'average_classification_score': avg_classification_score,
            'redesign_statistics': {
                'total_redesigns_applied': redesign_applied_count,
                'successful_redesigns': successful_redesigns,
                'redesign_success_rate': (successful_redesigns / redesign_applied_count * 100) if redesign_applied_count > 0 else 0
            },
            'component_usage': self._calculate_component_usage_stats()
        }
    
    def _calculate_component_usage_stats(self) -> Dict[str, Any]:
        """Calculate component usage statistics"""
        
        component_counts = {}
        total_evaluations = len(self.triage_history)
        
        for entry in self.triage_history:
            for component in entry['response'].components_evaluated:
                component_counts[component] = component_counts.get(component, 0) + 1
        
        component_percentages = {
            component: (count / total_evaluations * 100) if total_evaluations > 0 else 0
            for component, count in component_counts.items()
        }
        
        return {
            'component_counts': component_counts,
            'component_usage_percentages': component_percentages
        }
    
    def bulk_triage(self, scene_cards: List[SceneCard], 
                   common_criteria: Optional[ClassificationCriteria] = None) -> List[TriageResponse]:
        """Perform bulk triage evaluation on multiple scenes"""
        
        self.logger.info(f"Starting bulk triage for {len(scene_cards)} scenes")
        
        responses = []
        
        for scene_card in scene_cards:
            request = TriageRequest(
                scene_card=scene_card,
                custom_criteria=common_criteria,
                auto_redesign_maybe=True
            )
            
            response = self.evaluate_scene(request)
            responses.append(response)
        
        return responses
    
    def get_triage_summary(self, responses: List[TriageResponse]) -> Dict[str, Any]:
        """Get summary statistics for a batch of triage responses"""
        
        if not responses:
            return {'total_scenes': 0}
        
        decision_counts = {decision.value: 0 for decision in TriageDecision}
        quality_scores = []
        redesign_count = 0
        
        for response in responses:
            decision_counts[response.decision.value] += 1
            quality_scores.append(response.classification_score)
            if response.redesign_applied:
                redesign_count += 1
        
        avg_quality_score = sum(quality_scores) / len(quality_scores)
        
        return {
            'total_scenes': len(responses),
            'decisions': decision_counts,
            'decision_percentages': {
                decision: (count / len(responses) * 100)
                for decision, count in decision_counts.items()
            },
            'average_quality_score': avg_quality_score,
            'scenes_requiring_redesign': redesign_count,
            'redesign_rate': redesign_count / len(responses) * 100,
            'quality_distribution': {
                'high_quality': sum(1 for score in quality_scores if score >= 0.8),
                'medium_quality': sum(1 for score in quality_scores if 0.6 <= score < 0.8),
                'low_quality': sum(1 for score in quality_scores if score < 0.6)
            }
        }