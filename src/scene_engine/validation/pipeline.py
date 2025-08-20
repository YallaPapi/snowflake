"""
Validation Pipeline

This implements subtask 43.7: Build Validation Pipeline and Reporting System
Provides structured pipeline for running validation checks in sequence.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio

from ..models import SceneCard, ValidationResult, ValidationError, SceneType
from ..validators import SceneValidator


class ValidationStageType(Enum):
    """Types of validation stages"""
    STRUCTURAL = "structural"  # Basic structure validation
    SEMANTIC = "semantic"     # Content and meaning validation  
    BUSINESS_RULE = "business_rule"  # PRD business rules
    QUALITY = "quality"       # Quality and best practices


@dataclass 
class ValidationStage:
    """Individual validation stage in the pipeline"""
    name: str
    stage_type: ValidationStageType
    validator_method: str  # Method name on SceneValidator
    description: str
    required: bool = True
    depends_on: List[str] = None  # Stage names this depends on
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class StageResult:
    """Result of a single validation stage"""
    stage_name: str
    success: bool
    errors: List[ValidationError]
    warnings: List[ValidationError] = None
    duration_ms: float = 0.0
    stage_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.stage_metadata is None:
            self.stage_metadata = {}


@dataclass
class PipelineResult:
    """Result of complete validation pipeline execution"""
    scene_id: str
    overall_success: bool
    stage_results: List[StageResult]
    total_duration_ms: float
    pipeline_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.pipeline_metadata is None:
            self.pipeline_metadata = {}
    
    @property
    def all_errors(self) -> List[ValidationError]:
        """Get all errors from all stages"""
        errors = []
        for result in self.stage_results:
            errors.extend(result.errors)
        return errors
    
    @property 
    def all_warnings(self) -> List[ValidationError]:
        """Get all warnings from all stages"""
        warnings = []
        for result in self.stage_results:
            warnings.extend(result.warnings)
        return warnings
    
    def get_stage_result(self, stage_name: str) -> Optional[StageResult]:
        """Get result for specific stage"""
        for result in self.stage_results:
            if result.stage_name == stage_name:
                return result
        return None


class ValidationPipeline:
    """
    Structured validation pipeline that runs checks in defined stages
    
    The pipeline organizes validation into logical stages:
    1. Structural - Basic data structure validation
    2. Semantic - Content validation per scene type
    3. Business Rule - PRD-specific validation rules
    4. Quality - Best practice and quality checks
    """
    
    def __init__(self, validator: SceneValidator = None):
        self.validator = validator or SceneValidator()
        self.stages = self._initialize_stages()
        self.pipeline_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "avg_duration_ms": 0.0
        }
    
    def _initialize_stages(self) -> List[ValidationStage]:
        """Initialize the validation pipeline stages"""
        return [
            # Stage 1: Structural validation
            ValidationStage(
                name="structural_validation",
                stage_type=ValidationStageType.STRUCTURAL,
                validator_method="validate_scene_structure",
                description="Validate basic scene structure and required fields",
                required=True
            ),
            
            # Stage 2: Scene Crucible validation
            ValidationStage(
                name="crucible_validation", 
                stage_type=ValidationStageType.SEMANTIC,
                validator_method="crucible_now_check",
                description="Validate Scene Crucible focuses on 'now' and avoids story dumps",
                required=True,
                depends_on=["structural_validation"]
            ),
            
            # Stage 3: Scene type specific validation
            ValidationStage(
                name="scene_type_validation",
                stage_type=ValidationStageType.BUSINESS_RULE,
                validator_method="validate_scene_type_specific",
                description="Validate scene follows correct type-specific patterns",
                required=True,
                depends_on=["structural_validation", "crucible_validation"]
            ),
            
            # Stage 4: Goal validation (proactive only)
            ValidationStage(
                name="goal_validation",
                stage_type=ValidationStageType.BUSINESS_RULE, 
                validator_method="goal_five_check",
                description="Validate 5-point goal criteria for proactive scenes",
                required=True,
                depends_on=["scene_type_validation"]
            ),
            
            # Stage 5: Conflict escalation (proactive only)
            ValidationStage(
                name="conflict_validation",
                stage_type=ValidationStageType.BUSINESS_RULE,
                validator_method="conflict_escalation_check", 
                description="Validate conflict escalation and obstacle progression",
                required=True,
                depends_on=["goal_validation"]
            ),
            
            # Stage 6: Outcome validation (proactive only)
            ValidationStage(
                name="outcome_validation",
                stage_type=ValidationStageType.BUSINESS_RULE,
                validator_method="outcome_polarity_check",
                description="Validate outcome polarity and rationale",
                required=True,
                depends_on=["conflict_validation"]
            ),
            
            # Stage 7: Reactive triad validation (reactive only)
            ValidationStage(
                name="reactive_triad_validation",
                stage_type=ValidationStageType.BUSINESS_RULE,
                validator_method="reactive_triad_check",
                description="Validate Reaction-Dilemma-Decision triad completeness",
                required=True,
                depends_on=["scene_type_validation"]
            ),
            
            # Stage 8: Compression integrity (reactive only)
            ValidationStage(
                name="compression_validation",
                stage_type=ValidationStageType.BUSINESS_RULE,
                validator_method="compression_integrity_check",
                description="Validate compressed scenes maintain integrity",
                required=True,
                depends_on=["reactive_triad_validation"]
            ),
            
            # Stage 9: Exposition budget validation
            ValidationStage(
                name="exposition_validation",
                stage_type=ValidationStageType.QUALITY,
                validator_method="validate_exposition_budget", 
                description="Validate exposition follows 'now or never' rule",
                required=False,
                depends_on=["scene_type_validation"]
            )
        ]
    
    async def validate_scene(self, scene_card: SceneCard, 
                           fail_fast: bool = False,
                           skip_optional: bool = False) -> PipelineResult:
        """
        Run the complete validation pipeline on a scene card
        
        Args:
            scene_card: Scene to validate
            fail_fast: Stop pipeline on first stage failure
            skip_optional: Skip non-required validation stages
            
        Returns:
            PipelineResult with detailed stage-by-stage results
        """
        start_time = datetime.now()
        scene_id = f"{scene_card.scene_type.value}_{scene_card.pov}_{int(start_time.timestamp())}"
        
        stage_results = []
        overall_success = True
        completed_stages = set()
        
        try:
            # Run stages in dependency order
            for stage in self._get_applicable_stages(scene_card, skip_optional):
                # Check dependencies
                if not self._dependencies_satisfied(stage, completed_stages):
                    continue
                
                # Run stage
                stage_result = await self._run_stage(stage, scene_card)
                stage_results.append(stage_result)
                completed_stages.add(stage.name)
                
                # Check for failure
                if not stage_result.success:
                    overall_success = False
                    if fail_fast and stage.required:
                        break
            
            # Calculate total duration
            total_duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update statistics
            self._update_pipeline_stats(overall_success, total_duration)
            
            return PipelineResult(
                scene_id=scene_id,
                overall_success=overall_success,
                stage_results=stage_results,
                total_duration_ms=total_duration,
                pipeline_metadata={
                    "stages_run": len(stage_results),
                    "stages_skipped": len(self.stages) - len(stage_results),
                    "fail_fast": fail_fast,
                    "skip_optional": skip_optional
                }
            )
            
        except Exception as e:
            # Handle pipeline errors
            error_result = StageResult(
                stage_name="pipeline_error",
                success=False,
                errors=[ValidationError(
                    field="pipeline",
                    message=f"Pipeline execution error: {str(e)}",
                    code="pipeline_error"
                )]
            )
            
            total_duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return PipelineResult(
                scene_id=scene_id,
                overall_success=False,
                stage_results=[error_result],
                total_duration_ms=total_duration
            )
    
    def _get_applicable_stages(self, scene_card: SceneCard, 
                              skip_optional: bool = False) -> List[ValidationStage]:
        """Get stages applicable to this scene type"""
        applicable_stages = []
        
        for stage in self.stages:
            # Skip optional stages if requested
            if skip_optional and not stage.required:
                continue
            
            # Include stage based on scene type and stage applicability
            if self._is_stage_applicable(stage, scene_card):
                applicable_stages.append(stage)
        
        return applicable_stages
    
    def _is_stage_applicable(self, stage: ValidationStage, scene_card: SceneCard) -> bool:
        """Check if stage applies to this scene type"""
        
        # Universal stages
        universal_stages = [
            "structural_validation", "crucible_validation", 
            "scene_type_validation", "exposition_validation"
        ]
        if stage.name in universal_stages:
            return True
        
        # Proactive-only stages
        proactive_stages = [
            "goal_validation", "conflict_validation", "outcome_validation"
        ]
        if stage.name in proactive_stages:
            return scene_card.scene_type == SceneType.PROACTIVE
        
        # Reactive-only stages  
        reactive_stages = [
            "reactive_triad_validation", "compression_validation"
        ]
        if stage.name in reactive_stages:
            return scene_card.scene_type == SceneType.REACTIVE
        
        return True
    
    def _dependencies_satisfied(self, stage: ValidationStage, 
                               completed_stages: set) -> bool:
        """Check if stage dependencies are satisfied"""
        for dependency in stage.depends_on:
            if dependency not in completed_stages:
                return False
        return True
    
    async def _run_stage(self, stage: ValidationStage, scene_card: SceneCard) -> StageResult:
        """Run a single validation stage"""
        start_time = datetime.now()
        
        try:
            # Get the validator method
            if stage.validator_method == "validate_scene_type_specific":
                # Special handling for scene type specific validation
                errors = await self._validate_scene_type_specific(scene_card)
            else:
                validator_method = getattr(self.validator, stage.validator_method)
                errors = validator_method(scene_card)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return StageResult(
                stage_name=stage.name,
                success=len(errors) == 0,
                errors=errors,
                duration_ms=duration,
                stage_metadata={
                    "stage_type": stage.stage_type.value,
                    "description": stage.description,
                    "required": stage.required
                }
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return StageResult(
                stage_name=stage.name,
                success=False,
                errors=[ValidationError(
                    field=stage.name,
                    message=f"Stage execution error: {str(e)}",
                    code="stage_error"
                )],
                duration_ms=duration
            )
    
    async def _validate_scene_type_specific(self, scene_card: SceneCard) -> List[ValidationError]:
        """Validate scene follows correct type-specific patterns"""
        errors = []
        
        if scene_card.scene_type == SceneType.PROACTIVE:
            if not scene_card.proactive:
                errors.append(ValidationError(
                    field="proactive",
                    message="Proactive scenes must have proactive data structure",
                    code="missing_proactive_structure"
                ))
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if not scene_card.reactive:
                errors.append(ValidationError(
                    field="reactive", 
                    message="Reactive scenes must have reactive data structure",
                    code="missing_reactive_structure"
                ))
        
        return errors
    
    def _update_pipeline_stats(self, success: bool, duration_ms: float):
        """Update pipeline statistics"""
        self.pipeline_stats["total_runs"] += 1
        
        if success:
            self.pipeline_stats["successful_runs"] += 1
        
        # Update rolling average duration
        total = self.pipeline_stats["total_runs"]
        current_avg = self.pipeline_stats["avg_duration_ms"]
        new_avg = ((current_avg * (total - 1)) + duration_ms) / total
        self.pipeline_stats["avg_duration_ms"] = new_avg
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        stats = self.pipeline_stats.copy()
        if stats["total_runs"] > 0:
            stats["success_rate"] = (stats["successful_runs"] / stats["total_runs"]) * 100
        else:
            stats["success_rate"] = 0.0
        return stats
    
    def reset_statistics(self):
        """Reset pipeline statistics"""
        self.pipeline_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "avg_duration_ms": 0.0
        }
    
    def get_stage_info(self) -> List[Dict[str, Any]]:
        """Get information about all pipeline stages"""
        return [
            {
                "name": stage.name,
                "type": stage.stage_type.value,
                "description": stage.description,
                "required": stage.required,
                "depends_on": stage.depends_on,
                "validator_method": stage.validator_method
            }
            for stage in self.stages
        ]


# Convenience functions
async def validate_scene_with_pipeline(scene_card: SceneCard, **kwargs) -> PipelineResult:
    """Convenience function for pipeline validation"""
    pipeline = ValidationPipeline()
    return await pipeline.validate_scene(scene_card, **kwargs)