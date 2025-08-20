"""
Scene Validation Service

This implements subtask 43.7: Build Validation Pipeline and Reporting System
Provides high-level validation services with detailed reporting and source rule citations.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio

from ..models import SceneCard, ValidationResult, ValidationError, SceneType
from ..validators import SceneValidator


class ValidationSeverity(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRuleCitation:
    """Citation to source rule in PRD or documentation"""
    section: str  # e.g., "Section E1"
    rule_name: str  # e.g., "CrucibleNowCheck"
    rule_description: str
    prd_reference: Optional[str] = None  # Page number or section reference


@dataclass
class ValidationRequest:
    """Request for scene validation"""
    scene_card: SceneCard
    validation_options: Dict[str, Any] = None
    include_warnings: bool = True
    include_rule_citations: bool = True
    validation_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.validation_options is None:
            self.validation_options = {}
        if self.validation_context is None:
            self.validation_context = {}


@dataclass
class ValidationMetrics:
    """Validation performance and statistics"""
    total_checks_run: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warned: int = 0
    validation_duration_ms: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """Calculate validation success rate"""
        if self.total_checks_run == 0:
            return 0.0
        return (self.checks_passed / self.total_checks_run) * 100


@dataclass 
class ValidationReport:
    """Detailed validation report with citations and metrics"""
    scene_id: str
    scene_type: SceneType
    is_valid: bool
    validation_errors: List[ValidationError]
    validation_warnings: List[ValidationError] = None
    rule_citations: List[ValidationRuleCitation] = None
    validation_metrics: ValidationMetrics = None
    recommendations: List[str] = None
    report_timestamp: datetime = None
    
    def __post_init__(self):
        if self.validation_warnings is None:
            self.validation_warnings = []
        if self.rule_citations is None:
            self.rule_citations = []
        if self.recommendations is None:
            self.recommendations = []
        if self.report_timestamp is None:
            self.report_timestamp = datetime.now()
    
    def to_summary(self) -> str:
        """Generate human-readable summary"""
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        error_count = len(self.validation_errors)
        warning_count = len(self.validation_warnings)
        
        summary = f"{status} - {self.scene_type.value} scene"
        if error_count > 0:
            summary += f" ({error_count} errors)"
        if warning_count > 0:
            summary += f" ({warning_count} warnings)"
        
        return summary


@dataclass
class ValidationResponse:
    """Response from validation service"""
    request_id: str
    validation_report: ValidationReport
    processing_time_ms: float
    service_version: str = "1.0.0"


class SceneValidationService:
    """
    High-level scene validation service with detailed reporting
    
    This service provides:
    - Comprehensive scene validation using all PRD validators
    - Detailed reports with rule citations and recommendations
    - Performance metrics and validation statistics
    - Async validation pipeline support
    """
    
    def __init__(self, validator: SceneValidator = None):
        self.validator = validator or SceneValidator()
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "avg_validation_time_ms": 0.0
        }
        self.rule_citations = self._initialize_rule_citations()
    
    def _initialize_rule_citations(self) -> Dict[str, ValidationRuleCitation]:
        """Initialize rule citations from PRD Section E1"""
        return {
            "crucible_now_check": ValidationRuleCitation(
                section="Section E1",
                rule_name="CrucibleNowCheck",
                rule_description="Scene Crucible must focus on immediate danger 'now', not backstory/world dump. Must be 1-2 sentences maximum.",
                prd_reference="E1.1"
            ),
            "goal_five_check": ValidationRuleCitation(
                section="Section E1", 
                rule_name="GoalFiveCheck",
                rule_description="Proactive scenes must pass all 5 goal criteria: fits time, possible, difficult, fits POV, concrete objective.",
                prd_reference="E1.2"
            ),
            "conflict_escalation_check": ValidationRuleCitation(
                section="Section E1",
                rule_name="ConflictEscalationCheck", 
                rule_description="Conflicts must escalate with increasing try numbers. End scene when out of obstacles.",
                prd_reference="E1.3"
            ),
            "outcome_polarity_check": ValidationRuleCitation(
                section="Section E1",
                rule_name="OutcomePolarityCheck",
                rule_description="Default to Setback outcome. Victory allowed but prefer mixed outcomes.",
                prd_reference="E1.4"
            ),
            "reactive_triad_check": ValidationRuleCitation(
                section="Section E1",
                rule_name="ReactiveTriadCheck",
                rule_description="Reactive scenes must follow exact Reaction-Dilemma-Decision pattern with all options being bad.",
                prd_reference="E1.5"
            ),
            "compression_integrity_check": ValidationRuleCitation(
                section="Section E1", 
                rule_name="CompressionIntegrityCheck",
                rule_description="Compressed reactive scenes must still maintain complete R-D-D triad structure.",
                prd_reference="E1.6"
            )
        }
    
    async def validate_scene(self, request: ValidationRequest) -> ValidationResponse:
        """
        Perform comprehensive scene validation with detailed reporting
        
        Args:
            request: ValidationRequest containing scene card and options
            
        Returns:
            ValidationResponse with detailed validation report
        """
        start_time = datetime.now()
        request_id = f"val_{int(start_time.timestamp() * 1000)}"
        
        try:
            # Run validation
            validation_result = self.validator.validate_scene_card(request.scene_card)
            
            # Generate detailed report
            report = await self._generate_validation_report(
                scene_card=request.scene_card,
                validation_result=validation_result,
                request=request
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_validation_stats(report.is_valid, processing_time)
            
            return ValidationResponse(
                request_id=request_id,
                validation_report=report,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            # Handle validation errors
            error_report = ValidationReport(
                scene_id=f"scene_{int(start_time.timestamp())}",
                scene_type=request.scene_card.scene_type,
                is_valid=False,
                validation_errors=[ValidationError(
                    field="validation_service",
                    message=f"Validation service error: {str(e)}",
                    code="service_error"
                )]
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ValidationResponse(
                request_id=request_id,
                validation_report=error_report,
                processing_time_ms=processing_time
            )
    
    async def _generate_validation_report(self, scene_card: SceneCard, 
                                        validation_result: ValidationResult,
                                        request: ValidationRequest) -> ValidationReport:
        """Generate detailed validation report"""
        
        # Generate scene ID
        scene_id = f"{scene_card.scene_type.value}_{scene_card.pov}_{int(datetime.now().timestamp())}"
        
        # Extract rule citations for failed checks
        rule_citations = []
        if request.include_rule_citations:
            rule_citations = self._extract_rule_citations(validation_result.errors)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scene_card, validation_result.errors)
        
        # Calculate metrics
        metrics = self._calculate_validation_metrics(validation_result)
        
        return ValidationReport(
            scene_id=scene_id,
            scene_type=scene_card.scene_type,
            is_valid=validation_result.is_valid,
            validation_errors=validation_result.errors,
            validation_warnings=validation_result.warnings,
            rule_citations=rule_citations,
            validation_metrics=metrics,
            recommendations=recommendations
        )
    
    def _extract_rule_citations(self, errors: List[ValidationError]) -> List[ValidationRuleCitation]:
        """Extract relevant rule citations based on validation errors"""
        citations = []
        cited_rules = set()
        
        for error in errors:
            # Map error codes to rule citations
            if error.code.startswith("crucible_") and "crucible_now_check" not in cited_rules:
                citations.append(self.rule_citations["crucible_now_check"])
                cited_rules.add("crucible_now_check")
            elif error.code.startswith("goal_") and "goal_five_check" not in cited_rules:
                citations.append(self.rule_citations["goal_five_check"])
                cited_rules.add("goal_five_check")
            elif error.code.startswith("escalation_") and "conflict_escalation_check" not in cited_rules:
                citations.append(self.rule_citations["conflict_escalation_check"])
                cited_rules.add("conflict_escalation_check")
            elif error.code.startswith("outcome_") and "outcome_polarity_check" not in cited_rules:
                citations.append(self.rule_citations["outcome_polarity_check"])
                cited_rules.add("outcome_polarity_check")
            elif (error.code.startswith("reaction_") or error.code.startswith("dilemma_") or 
                  error.code.startswith("decision_")) and "reactive_triad_check" not in cited_rules:
                citations.append(self.rule_citations["reactive_triad_check"])
                cited_rules.add("reactive_triad_check")
            elif error.code.startswith("compressed_") and "compression_integrity_check" not in cited_rules:
                citations.append(self.rule_citations["compression_integrity_check"])
                cited_rules.add("compression_integrity_check")
        
        return citations
    
    def _generate_recommendations(self, scene_card: SceneCard, 
                                errors: List[ValidationError]) -> List[str]:
        """Generate actionable recommendations based on validation errors"""
        recommendations = []
        
        # Group errors by category
        error_categories = {}
        for error in errors:
            category = error.code.split("_")[0]
            if category not in error_categories:
                error_categories[category] = []
            error_categories[category].append(error)
        
        # Generate category-specific recommendations
        if "crucible" in error_categories:
            recommendations.append("Focus Scene Crucible on immediate danger 'right now' - avoid backstory exposition")
            recommendations.append("Keep Scene Crucible to 1-2 sentences maximum")
        
        if "goal" in error_categories:
            recommendations.append("Ensure goal passes all 5 criteria: fits time, possible, difficult, fits POV, concrete")
            recommendations.append("Make goal more specific and measurable")
        
        if "escalation" in error_categories:
            recommendations.append("Ensure obstacles escalate in difficulty with increasing try numbers")
            recommendations.append("End scene when character runs out of obstacles to try")
        
        if "outcome" in error_categories:
            recommendations.append("Provide clear rationale for why this outcome occurred")
        
        if any(cat in error_categories for cat in ["reaction", "dilemma", "decision"]):
            recommendations.append("Ensure Reaction-Dilemma-Decision triad is complete and substantial")
            recommendations.append("Make sure all dilemma options are genuinely bad choices")
            recommendations.append("Decision must be firm and produce next goal stub")
        
        if "compressed" in error_categories:
            recommendations.append("Even compressed scenes need complete R-D-D triad recorded")
        
        return recommendations
    
    def _calculate_validation_metrics(self, validation_result: ValidationResult) -> ValidationMetrics:
        """Calculate validation metrics"""
        total_checks = 6  # Number of main validation checks
        failed_checks = len(validation_result.errors)
        passed_checks = total_checks - failed_checks
        warned_checks = len(validation_result.warnings)
        
        return ValidationMetrics(
            total_checks_run=total_checks,
            checks_passed=passed_checks, 
            checks_failed=failed_checks,
            checks_warned=warned_checks,
            validation_duration_ms=0.0  # Will be set by caller
        )
    
    def _update_validation_stats(self, is_valid: bool, processing_time_ms: float):
        """Update service validation statistics"""
        self.validation_stats["total_validations"] += 1
        
        if is_valid:
            self.validation_stats["successful_validations"] += 1
        else:
            self.validation_stats["failed_validations"] += 1
        
        # Update rolling average processing time
        total = self.validation_stats["total_validations"]
        current_avg = self.validation_stats["avg_validation_time_ms"]
        new_avg = ((current_avg * (total - 1)) + processing_time_ms) / total
        self.validation_stats["avg_validation_time_ms"] = new_avg
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get current validation service statistics"""
        stats = self.validation_stats.copy()
        if stats["total_validations"] > 0:
            stats["success_rate"] = (stats["successful_validations"] / stats["total_validations"]) * 100
        else:
            stats["success_rate"] = 0.0
        return stats
    
    def reset_statistics(self):
        """Reset validation service statistics"""
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0, 
            "avg_validation_time_ms": 0.0
        }
    
    async def validate_scene_batch(self, requests: List[ValidationRequest]) -> List[ValidationResponse]:
        """Validate multiple scenes in parallel"""
        tasks = [self.validate_scene(request) for request in requests]
        return await asyncio.gather(*tasks)
    
    def validate_scene_sync(self, scene_card: SceneCard, **kwargs) -> ValidationResponse:
        """Synchronous validation for convenience"""
        request = ValidationRequest(scene_card=scene_card, **kwargs)
        return asyncio.run(self.validate_scene(request))


# Convenience functions
async def validate_scene_card_async(scene_card: SceneCard, **kwargs) -> ValidationResponse:
    """Async convenience function for scene validation"""
    service = SceneValidationService()
    request = ValidationRequest(scene_card=scene_card, **kwargs)
    return await service.validate_scene(request)


def validate_scene_card_sync(scene_card: SceneCard, **kwargs) -> ValidationResponse:
    """Sync convenience function for scene validation"""
    service = SceneValidationService()
    return service.validate_scene_sync(scene_card, **kwargs)