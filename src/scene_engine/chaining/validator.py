"""
Chain Link Validator

This implements subtask 46.3: Implement Chain Link Validation
Validates the integrity and correctness of chain links between scenes.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from ..models import SceneCard, SceneType, OutcomeType
from .models import (
    ChainLink, ChainLinkType, ChainValidationResult, ChainSequence, 
    ChainStrength, SceneReference
)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"    # Breaks story flow
    ERROR = "error"         # Violates Snowflake rules  
    WARNING = "warning"     # Sub-optimal but workable
    INFO = "info"          # Informational suggestions


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    severity: ValidationSeverity
    code: str
    message: str
    field: str
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.message}"


class ChainLinkValidator:
    """
    Validates individual chain links for correctness and quality
    
    Validation categories:
    1. Structural - Basic data integrity
    2. Logical - Narrative logic and consistency
    3. Snowflake Compliance - Adherence to method rules
    4. Content Quality - Quality of trigger/seed content
    5. Transition Appropriateness - Suitability of transition type
    """
    
    def __init__(self):
        self.validation_stats = {
            "total_validated": 0,
            "valid_links": 0,
            "critical_errors": 0,
            "errors": 0,
            "warnings": 0
        }
    
    def validate_chain_link(self, chain_link: ChainLink,
                          source_scene: Optional[SceneCard] = None,
                          target_scene: Optional[SceneCard] = None) -> ChainValidationResult:
        """
        Comprehensive validation of a chain link
        
        Args:
            chain_link: Chain link to validate
            source_scene: Optional source scene for deep validation
            target_scene: Optional target scene for compatibility checking
            
        Returns:
            ChainValidationResult with detailed validation information
        """
        issues = []
        
        # Run all validation checks
        issues.extend(self._validate_structural_integrity(chain_link))
        issues.extend(self._validate_snowflake_compliance(chain_link, source_scene))
        issues.extend(self._validate_logical_consistency(chain_link, source_scene))
        issues.extend(self._validate_content_quality(chain_link))
        issues.extend(self._validate_transition_appropriateness(chain_link, source_scene))
        
        if target_scene:
            issues.extend(self._validate_target_compatibility(chain_link, target_scene))
        
        # Categorize issues
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]  
        warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(chain_link, issues)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(issues)
        
        # Update statistics
        self._update_validation_stats(len(critical_issues), len(errors), len(warnings))
        
        # Create result
        return ChainValidationResult(
            is_valid=len(critical_issues) == 0 and len(errors) == 0,
            chain_quality_score=quality_score,
            validation_errors=[i.message for i in critical_issues + errors],
            validation_warnings=[i.message for i in warnings],
            improvement_suggestions=suggestions
        )
    
    def _validate_structural_integrity(self, chain_link: ChainLink) -> List[ValidationIssue]:
        """Validate basic structural integrity"""
        issues = []
        
        # Check required fields
        if not chain_link.chain_id:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="missing_chain_id",
                message="Chain link must have a unique chain_id",
                field="chain_id"
            ))
        
        if not chain_link.trigger_content:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="missing_trigger_content", 
                message="Chain link must specify trigger content",
                field="trigger_content"
            ))
        
        if not chain_link.target_seed:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="missing_target_seed",
                message="Chain link must provide target seed for next scene",
                field="target_seed"
            ))
        
        # Validate source scene reference
        if not chain_link.source_scene:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="missing_source_scene",
                message="Chain link must reference a source scene",
                field="source_scene"
            ))
        elif not chain_link.source_scene.scene_id:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="invalid_source_scene_id",
                message="Source scene must have valid scene_id",
                field="source_scene.scene_id"
            ))
        
        return issues
    
    def _validate_snowflake_compliance(self, chain_link: ChainLink,
                                     source_scene: Optional[SceneCard] = None) -> List[ValidationIssue]:
        """Validate compliance with Snowflake Method rules"""
        issues = []
        
        if not source_scene:
            return issues  # Can't validate without source scene
        
        # Check transition pattern compliance
        source_type = source_scene.scene_type
        chain_type = chain_link.chain_type
        
        # Proactive scene transition rules
        if source_type == SceneType.PROACTIVE:
            valid_proactive_transitions = [
                ChainLinkType.SETBACK_TO_REACTIVE,
                ChainLinkType.VICTORY_TO_PROACTIVE,
                ChainLinkType.MIXED_TO_REACTIVE,
                ChainLinkType.MIXED_TO_PROACTIVE
            ]
            
            if chain_type not in valid_proactive_transitions:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="invalid_proactive_transition",
                    message=f"Proactive scenes cannot transition to {chain_type.value}",
                    field="chain_type",
                    suggestion="Use setback→reactive, victory→proactive, or mixed outcome transitions"
                ))
            
            # Check outcome alignment
            if source_scene.proactive:
                outcome_type = source_scene.proactive.outcome.type
                
                if outcome_type == OutcomeType.SETBACK and chain_type != ChainLinkType.SETBACK_TO_REACTIVE:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="setback_must_go_reactive",
                        message="Setback outcomes must transition to reactive scenes",
                        field="chain_type",
                        suggestion="Change chain type to SETBACK_TO_REACTIVE"
                    ))
                
                elif outcome_type == OutcomeType.VICTORY and chain_type != ChainLinkType.VICTORY_TO_PROACTIVE:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="victory_should_continue_proactive",
                        message="Victory outcomes typically continue to proactive scenes",
                        field="chain_type",
                        suggestion="Consider VICTORY_TO_PROACTIVE unless processing is needed"
                    ))
        
        # Reactive scene transition rules
        elif source_type == SceneType.REACTIVE:
            if chain_type != ChainLinkType.DECISION_TO_PROACTIVE:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="reactive_must_go_proactive",
                    message="Reactive scenes must transition to proactive scenes via decisions",
                    field="chain_type",
                    suggestion="Change chain type to DECISION_TO_PROACTIVE"
                ))
            
            # Check for next goal stub
            if source_scene.reactive and not source_scene.reactive.next_goal_stub:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="missing_next_goal_stub",
                    message="Reactive scenes must provide next_goal_stub for transition",
                    field="source_scene.reactive.next_goal_stub",
                    suggestion="Add next_goal_stub to reactive scene"
                ))
        
        return issues
    
    def _validate_logical_consistency(self, chain_link: ChainLink,
                                    source_scene: Optional[SceneCard] = None) -> List[ValidationIssue]:
        """Validate logical consistency of the transition"""
        issues = []
        
        if not source_scene:
            return issues
        
        # Check POV consistency
        source_pov = source_scene.pov
        link_pov = chain_link.source_scene.pov_character
        
        if source_pov != link_pov:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="pov_inconsistency",
                message=f"POV mismatch: scene has '{source_pov}', link has '{link_pov}'",
                field="source_scene.pov_character",
                suggestion="Ensure POV consistency or mark as POV shift"
            ))
        
        # Check trigger content alignment
        trigger_content = chain_link.trigger_content.lower()
        
        if source_scene.scene_type == SceneType.PROACTIVE:
            if source_scene.proactive:
                outcome_rationale = source_scene.proactive.outcome.rationale.lower()
                
                # Check if trigger content relates to outcome
                if not self._content_similarity(trigger_content, outcome_rationale):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="trigger_outcome_mismatch",
                        message="Trigger content doesn't align well with scene outcome",
                        field="trigger_content",
                        suggestion="Ensure trigger content reflects the actual scene outcome"
                    ))
        
        elif source_scene.scene_type == SceneType.REACTIVE:
            if source_scene.reactive:
                decision = source_scene.reactive.decision.lower()
                
                if not self._content_similarity(trigger_content, decision):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="trigger_decision_mismatch",
                        message="Trigger content doesn't align with reactive decision",
                        field="trigger_content",
                        suggestion="Ensure trigger content reflects the actual decision made"
                    ))
        
        return issues
    
    def _validate_content_quality(self, chain_link: ChainLink) -> List[ValidationIssue]:
        """Validate quality of trigger and seed content"""
        issues = []
        
        # Check trigger content quality
        trigger_content = chain_link.trigger_content
        if len(trigger_content.strip()) < 10:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="trigger_content_too_short",
                message="Trigger content is very brief - consider adding more detail",
                field="trigger_content",
                suggestion="Expand trigger content to better explain the transition"
            ))
        
        if len(trigger_content) > 500:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="trigger_content_too_long",
                message="Trigger content is quite long - consider condensing",
                field="trigger_content",
                suggestion="Condense trigger content to essential information"
            ))
        
        # Check target seed quality
        target_seed = chain_link.target_seed
        if len(target_seed.strip()) < 5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="target_seed_too_short", 
                message="Target seed is too brief to be useful",
                field="target_seed",
                suggestion="Provide more substantial target seed for next scene"
            ))
        
        # Check for actionable content in target seed
        if chain_link.chain_type == ChainLinkType.DECISION_TO_PROACTIVE:
            if not self._contains_actionable_content(target_seed):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="target_seed_not_actionable",
                    message="Target seed for proactive scene should contain actionable goal",
                    field="target_seed",
                    suggestion="Make target seed more specific and actionable"
                ))
        
        # Check for emotional content in reactive seeds
        elif chain_link.chain_type == ChainLinkType.SETBACK_TO_REACTIVE:
            if not self._contains_emotional_content(target_seed):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="target_seed_lacks_emotion",
                    message="Target seed for reactive scene should contain emotional content",
                    field="target_seed",
                    suggestion="Add emotional context to target seed"
                ))
        
        return issues
    
    def _validate_transition_appropriateness(self, chain_link: ChainLink,
                                           source_scene: Optional[SceneCard] = None) -> List[ValidationIssue]:
        """Validate appropriateness of transition type"""
        issues = []
        
        transition_type = chain_link.transition_type
        chain_type = chain_link.chain_type
        
        # Check transition type compatibility with chain type
        if chain_type == ChainLinkType.SETBACK_TO_REACTIVE:
            # Setback reactions typically need immediate processing
            if transition_type.value not in ["immediate", "compressed"]:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="setback_should_be_immediate",
                    message="Setback reactions typically need immediate processing",
                    field="transition_type",
                    suggestion="Consider using immediate or compressed transition"
                ))
        
        elif chain_type == ChainLinkType.VICTORY_TO_PROACTIVE:
            # Victories often need bridging content
            if transition_type.value == "immediate":
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    code="victory_may_need_bridging",
                    message="Victory transitions often benefit from bridging content",
                    field="transition_type",
                    suggestion="Consider sequel or time_cut transition for victory processing"
                ))
        
        # Check bridging content requirements
        if transition_type.value in ["sequel", "time_cut"] and not chain_link.bridging_content:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="missing_bridging_content",
                message=f"{transition_type.value} transitions should include bridging content",
                field="bridging_content",
                suggestion="Add bridging content to explain the transition"
            ))
        
        return issues
    
    def _validate_target_compatibility(self, chain_link: ChainLink,
                                     target_scene: SceneCard) -> List[ValidationIssue]:
        """Validate compatibility with target scene"""
        issues = []
        
        # Check scene type alignment
        expected_target_type = None
        
        if chain_link.chain_type in [ChainLinkType.SETBACK_TO_REACTIVE, ChainLinkType.MIXED_TO_REACTIVE]:
            expected_target_type = SceneType.REACTIVE
        elif chain_link.chain_type in [
            ChainLinkType.DECISION_TO_PROACTIVE, 
            ChainLinkType.VICTORY_TO_PROACTIVE,
            ChainLinkType.MIXED_TO_PROACTIVE
        ]:
            expected_target_type = SceneType.PROACTIVE
        
        if expected_target_type and target_scene.scene_type != expected_target_type:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="target_scene_type_mismatch",
                message=f"Expected {expected_target_type.value} target scene, got {target_scene.scene_type.value}",
                field="target_scene",
                suggestion=f"Change target scene type to {expected_target_type.value}"
            ))
        
        # Check POV consistency
        if chain_link.target_scene:
            expected_pov = chain_link.target_scene.pov_character
            actual_pov = target_scene.pov
            
            if expected_pov != actual_pov and chain_link.transition_type.value != "pov_shift":
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="target_pov_mismatch",
                    message=f"POV changes from '{expected_pov}' to '{actual_pov}' without POV shift marker",
                    field="transition_type",
                    suggestion="Mark as pov_shift transition or ensure POV consistency"
                ))
        
        return issues
    
    # Helper methods for content analysis
    
    def _content_similarity(self, content1: str, content2: str) -> bool:
        """Check if two pieces of content are similar (basic implementation)"""
        # Simple word overlap check - could be enhanced with semantic analysis
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity > 0.3  # 30% word overlap threshold
    
    def _contains_actionable_content(self, content: str) -> bool:
        """Check if content contains actionable elements"""
        action_words = [
            'reach', 'get', 'find', 'complete', 'accomplish', 'achieve',
            'defeat', 'overcome', 'stop', 'prevent', 'rescue', 'save',
            'deliver', 'obtain', 'secure', 'capture', 'investigate'
        ]
        
        content_lower = content.lower()
        return any(word in content_lower for word in action_words)
    
    def _contains_emotional_content(self, content: str) -> bool:
        """Check if content contains emotional elements"""
        emotion_words = [
            'feel', 'felt', 'emotion', 'angry', 'sad', 'happy', 'fear', 'afraid',
            'frustrated', 'devastated', 'elated', 'disappointed', 'rage', 'grief',
            'guilt', 'shame', 'pride', 'desperate', 'hopeful', 'worried'
        ]
        
        content_lower = content.lower()
        return any(word in content_lower for word in emotion_words)
    
    def _calculate_quality_score(self, chain_link: ChainLink, 
                               issues: List[ValidationIssue]) -> float:
        """Calculate overall quality score for chain link"""
        base_score = 1.0
        
        # Deduct for issues by severity
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.4
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.2
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
        
        # Bonus for good practices
        if len(chain_link.trigger_content) > 50:  # Detailed trigger
            base_score += 0.05
        
        if len(chain_link.target_seed) > 30:  # Detailed seed
            base_score += 0.05
        
        if chain_link.metadata and chain_link.metadata.chain_strength == ChainStrength.STRONG:
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_improvement_suggestions(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate improvement suggestions based on issues"""
        suggestions = []
        
        # Collect unique suggestions
        for issue in issues:
            if issue.suggestion and issue.suggestion not in suggestions:
                suggestions.append(issue.suggestion)
        
        # Add general suggestions based on issue patterns
        error_codes = [i.code for i in issues if i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]
        
        if "setback_must_go_reactive" in error_codes:
            suggestions.append("Review Snowflake Method rules for proper scene transitions")
        
        if any("content" in code for code in error_codes):
            suggestions.append("Enhance content quality with more specific and detailed descriptions")
        
        if any("pov" in code for code in error_codes):
            suggestions.append("Maintain POV consistency or explicitly mark POV changes")
        
        return suggestions
    
    def _update_validation_stats(self, critical_count: int, error_count: int, warning_count: int):
        """Update validation statistics"""
        self.validation_stats["total_validated"] += 1
        
        if critical_count == 0 and error_count == 0:
            self.validation_stats["valid_links"] += 1
        
        self.validation_stats["critical_errors"] += critical_count
        self.validation_stats["errors"] += error_count
        self.validation_stats["warnings"] += warning_count
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        stats = self.validation_stats.copy()
        if stats["total_validated"] > 0:
            stats["success_rate"] = (stats["valid_links"] / stats["total_validated"]) * 100
            stats["avg_issues_per_link"] = ((stats["critical_errors"] + stats["errors"] + stats["warnings"]) / 
                                          stats["total_validated"])
        else:
            stats["success_rate"] = 0.0
            stats["avg_issues_per_link"] = 0.0
        return stats


class ChainSequenceValidator:
    """
    Validates sequences of connected scenes for overall coherence
    
    Validates:
    1. Scene alternation patterns (Proactive/Reactive)
    2. Chain link consistency across sequence
    3. POV and character continuity
    4. Narrative flow and pacing
    5. Overall sequence structure
    """
    
    def __init__(self):
        self.sequence_validator = ChainLinkValidator()
    
    def validate_chain_sequence(self, sequence: ChainSequence,
                              scenes: Optional[List[SceneCard]] = None) -> ChainValidationResult:
        """
        Validate a complete chain sequence
        
        Args:
            sequence: Chain sequence to validate
            scenes: Optional list of actual scene cards for deep validation
            
        Returns:
            ChainValidationResult for the entire sequence
        """
        issues = []
        
        # Validate sequence structure
        issues.extend(self._validate_sequence_structure(sequence))
        
        # Validate individual chain links
        link_results = []
        for i, chain_link in enumerate(sequence.chain_links):
            source_scene = scenes[i] if scenes and i < len(scenes) else None
            target_scene = scenes[i + 1] if scenes and i + 1 < len(scenes) else None
            
            link_result = self.sequence_validator.validate_chain_link(
                chain_link, source_scene, target_scene
            )
            link_results.append(link_result)
            
            # Add link-specific issues to sequence issues
            for error in link_result.validation_errors:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="chain_link_error",
                    message=f"Link {i}: {error}",
                    field=f"chain_links[{i}]"
                ))
        
        # Validate sequence-level patterns
        if scenes:
            issues.extend(self._validate_scene_alternation(scenes))
            issues.extend(self._validate_pov_consistency(scenes, sequence))
            issues.extend(self._validate_narrative_flow(scenes, sequence))
        
        # Calculate overall quality
        individual_scores = [r.chain_quality_score for r in link_results if r.chain_quality_score > 0]
        avg_link_quality = sum(individual_scores) / len(individual_scores) if individual_scores else 0.5
        
        sequence_structure_score = 1.0 - (len([i for i in issues if i.severity != ValidationSeverity.INFO]) * 0.1)
        overall_quality = (avg_link_quality + max(0, sequence_structure_score)) / 2
        
        return ChainValidationResult(
            is_valid=not any(i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR] for i in issues),
            chain_quality_score=min(1.0, max(0.0, overall_quality)),
            validation_errors=[i.message for i in issues if i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]],
            validation_warnings=[i.message for i in issues if i.severity == ValidationSeverity.WARNING],
            improvement_suggestions=self._generate_sequence_suggestions(issues, sequence)
        )
    
    def _validate_sequence_structure(self, sequence: ChainSequence) -> List[ValidationIssue]:
        """Validate basic sequence structure"""
        issues = []
        
        # Check scene/link count alignment
        expected_links = len(sequence.scenes) - 1
        actual_links = len(sequence.chain_links)
        
        if actual_links != expected_links:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="scene_link_count_mismatch",
                message=f"Expected {expected_links} chain links for {len(sequence.scenes)} scenes, found {actual_links}",
                field="chain_links"
            ))
        
        # Check sequence length
        if len(sequence.scenes) < 2:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="sequence_too_short",
                message="Sequence must contain at least 2 scenes",
                field="scenes"
            ))
        
        if len(sequence.scenes) > 20:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="sequence_very_long",
                message="Very long sequence may benefit from chapter breaks",
                field="scenes",
                suggestion="Consider breaking into multiple chapters"
            ))
        
        return issues
    
    def _validate_scene_alternation(self, scenes: List[SceneCard]) -> List[ValidationIssue]:
        """Validate Proactive/Reactive alternation pattern"""
        issues = []
        
        if len(scenes) < 2:
            return issues
        
        # Count alternation violations
        violations = 0
        consecutive_same = 0
        
        for i in range(len(scenes) - 1):
            current_type = scenes[i].scene_type
            next_type = scenes[i + 1].scene_type
            
            if current_type == next_type:
                violations += 1
                consecutive_same += 1
            else:
                consecutive_same = 0
            
            # Flag excessive consecutive scenes of same type
            if consecutive_same >= 3:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="excessive_consecutive_same_type",
                    message=f"Found {consecutive_same + 1} consecutive {current_type.value} scenes",
                    field=f"scenes[{i-consecutive_same}:{i+1}]",
                    suggestion="Consider alternating between Proactive and Reactive scenes"
                ))
        
        # Overall alternation assessment
        alternation_rate = 1.0 - (violations / (len(scenes) - 1))
        
        if alternation_rate < 0.5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="poor_scene_alternation",
                message=f"Low alternation rate ({alternation_rate:.1%}) between scene types",
                field="scenes",
                suggestion="Improve alternation between Proactive and Reactive scenes"
            ))
        
        return issues
    
    def _validate_pov_consistency(self, scenes: List[SceneCard], 
                                sequence: ChainSequence) -> List[ValidationIssue]:
        """Validate POV consistency across sequence"""
        issues = []
        
        pov_characters = [scene.pov for scene in scenes]
        unique_povs = set(pov_characters)
        
        # Check for excessive POV changes
        pov_changes = sum(1 for i in range(len(pov_characters) - 1) 
                         if pov_characters[i] != pov_characters[i + 1])
        
        change_rate = pov_changes / (len(scenes) - 1) if len(scenes) > 1 else 0
        
        if change_rate > 0.5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="frequent_pov_changes",
                message=f"High POV change rate ({change_rate:.1%}) may disrupt narrative flow",
                field="scenes",
                suggestion="Consider maintaining POV consistency within chapters"
            ))
        
        # Update sequence dominant POV if not set
        if not sequence.dominant_pov and pov_characters:
            pov_counts = {}
            for pov in pov_characters:
                pov_counts[pov] = pov_counts.get(pov, 0) + 1
            sequence.dominant_pov = max(pov_counts, key=pov_counts.get)
        
        return issues
    
    def _validate_narrative_flow(self, scenes: List[SceneCard],
                               sequence: ChainSequence) -> List[ValidationIssue]:
        """Validate narrative flow across sequence"""
        issues = []
        
        # Check for narrative momentum
        proactive_scenes = [s for s in scenes if s.scene_type == SceneType.PROACTIVE]
        reactive_scenes = [s for s in scenes if s.scene_type == SceneType.REACTIVE]
        
        proactive_ratio = len(proactive_scenes) / len(scenes)
        
        if proactive_ratio < 0.3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="low_proactive_ratio",
                message=f"Low proactive scene ratio ({proactive_ratio:.1%}) may reduce narrative momentum",
                field="scenes",
                suggestion="Consider adding more action-oriented proactive scenes"
            ))
        elif proactive_ratio > 0.8:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="high_proactive_ratio", 
                message=f"High proactive scene ratio ({proactive_ratio:.1%}) may lack emotional processing",
                field="scenes",
                suggestion="Consider adding reactive scenes for character development"
            ))
        
        # Check sequence tone consistency
        if not sequence.sequence_tone:
            # Could infer tone from scene content
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="missing_sequence_tone",
                message="Consider setting sequence tone for better coherence tracking",
                field="sequence_tone"
            ))
        
        return issues
    
    def _generate_sequence_suggestions(self, issues: List[ValidationIssue],
                                     sequence: ChainSequence) -> List[str]:
        """Generate sequence-specific improvement suggestions"""
        suggestions = []
        
        # Extract issue codes
        issue_codes = [i.code for i in issues]
        
        if "scene_link_count_mismatch" in issue_codes:
            suggestions.append("Ensure each scene has a corresponding chain link to the next scene")
        
        if "poor_scene_alternation" in issue_codes:
            suggestions.append("Improve story rhythm by alternating Proactive and Reactive scenes")
        
        if "frequent_pov_changes" in issue_codes:
            suggestions.append("Maintain POV consistency within chapters for better reader immersion")
        
        if "sequence_very_long" in issue_codes:
            suggestions.append("Consider natural chapter breaks at major story beats")
        
        # Add general suggestions based on sequence characteristics
        if len(sequence.scenes) > 10 and not any("chapter" in s for s in suggestions):
            suggestions.append("Long sequences benefit from clear chapter structure")
        
        return suggestions


# Convenience functions
def validate_chain_link(chain_link: ChainLink, 
                       source_scene: Optional[SceneCard] = None,
                       target_scene: Optional[SceneCard] = None) -> ChainValidationResult:
    """Convenience function to validate a chain link"""
    validator = ChainLinkValidator()
    return validator.validate_chain_link(chain_link, source_scene, target_scene)


def validate_chain_sequence(sequence: ChainSequence,
                          scenes: Optional[List[SceneCard]] = None) -> ChainValidationResult:
    """Convenience function to validate a chain sequence"""
    validator = ChainSequenceValidator()
    return validator.validate_chain_sequence(sequence, scenes)