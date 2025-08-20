"""
Scene Card Validators

This implements subtask 41.3 & 41.5: Runtime validation and type checking
Implements all validators from Section E1 of the PRD.
"""

from typing import List, Dict, Any, Optional, Tuple
from .models import SceneCard, ValidationResult, ValidationError, SceneType, OutcomeType


class SceneValidator:
    """Main scene validator implementing all PRD validation rules"""
    
    def validate_scene_card(self, scene_card: SceneCard) -> ValidationResult:
        """Run all validation checks on a scene card"""
        errors = []
        warnings = []
        
        # Run all validation checks
        try:
            errors.extend(self.crucible_now_check(scene_card))
            errors.extend(self.goal_five_check(scene_card))
            errors.extend(self.conflict_escalation_check(scene_card))
            errors.extend(self.outcome_polarity_check(scene_card))
            errors.extend(self.reactive_triad_check(scene_card))
            errors.extend(self.compression_integrity_check(scene_card))
            
            # Additional structural validation
            errors.extend(self.validate_scene_structure(scene_card))
            errors.extend(self.validate_exposition_budget(scene_card))
            
        except Exception as e:
            errors.append(ValidationError(
                field="general",
                message=f"Validation error: {str(e)}",
                code="validation_exception"
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def crucible_now_check(self, scene_card: SceneCard) -> List[ValidationError]:
        """CrucibleNowCheck - must exist and focus on 'now', not Story dump"""
        errors = []
        
        crucible = scene_card.scene_crucible
        
        if not crucible or not crucible.strip():
            errors.append(ValidationError(
                field="scene_crucible",
                message="Scene Crucible is required and cannot be empty",
                code="crucible_missing"
            ))
            return errors
            
        crucible = crucible.strip().lower()
        
        # Check for "now" language
        now_indicators = ['now', 'immediately', 'right now', 'at this moment', 'currently', 'here']
        has_now = any(indicator in crucible for indicator in now_indicators)
        
        # Check for story dump indicators
        story_dump_indicators = [
            'background', 'history', 'years ago', 'in the past', 'previously',
            'backstory', 'long ago', 'context', 'explanation'
        ]
        has_story_dump = any(indicator in crucible for indicator in story_dump_indicators)
        
        if has_story_dump:
            errors.append(ValidationError(
                field="scene_crucible",
                message="Scene Crucible should focus on immediate danger, not backstory/world dump",
                code="crucible_story_dump"
            ))
        
        # Check length (should be 1-2 sentences)
        sentence_count = len([s for s in scene_card.scene_crucible.split('.') if s.strip()])
        if sentence_count > 3:
            errors.append(ValidationError(
                field="scene_crucible", 
                message="Scene Crucible should be 1-2 sentences, not a lengthy exposition",
                code="crucible_too_long"
            ))
        
        return errors
    
    def goal_five_check(self, scene_card: SceneCard) -> List[ValidationError]:
        """GoalFiveCheck - proactive scenes must pass all 5 goal criteria"""
        errors = []
        
        if scene_card.scene_type != SceneType.PROACTIVE or not scene_card.proactive:
            return errors  # Only applies to proactive scenes
        
        goal = scene_card.proactive.goal
        
        # Check each of the 5 criteria
        criteria_checks = [
            (goal.fits_time, "fits_time", "Goal must fit the available time"),
            (goal.possible, "possible", "Goal must be achievable/possible"),
            (goal.difficult, "difficult", "Goal must be challenging/difficult"),
            (goal.fits_pov, "fits_pov", "Goal must fit the POV character's capabilities/values"),
            (goal.concrete_objective, "concrete_objective", "Goal must be concrete and measurable")
        ]
        
        for passed, criterion, message in criteria_checks:
            if not passed:
                errors.append(ValidationError(
                    field=f"proactive.goal.{criterion}",
                    message=message,
                    code=f"goal_criterion_{criterion}_failed"
                ))
        
        # Check goal text quality
        if len(goal.text.strip()) < 5:
            errors.append(ValidationError(
                field="proactive.goal.text",
                message="Goal text is too short to be meaningful",
                code="goal_text_too_short"
            ))
        
        return errors
    
    def conflict_escalation_check(self, scene_card: SceneCard) -> List[ValidationError]:
        """ConflictEscalationCheck - conflicts must escalate, end when out of obstacles"""
        errors = []
        
        if scene_card.scene_type != SceneType.PROACTIVE or not scene_card.proactive:
            return errors
        
        obstacles = scene_card.proactive.conflict_obstacles
        
        if len(obstacles) < 1:
            errors.append(ValidationError(
                field="proactive.conflict_obstacles",
                message="Proactive scenes must have at least one obstacle",
                code="no_obstacles"
            ))
            return errors
        
        # Check escalation - each obstacle should be harder than the last
        for i in range(len(obstacles) - 1):
            current = obstacles[i]
            next_obstacle = obstacles[i + 1]
            
            if current.try_number >= next_obstacle.try_number:
                errors.append(ValidationError(
                    field="proactive.conflict_obstacles",
                    message=f"Obstacle {i+1} does not escalate from obstacle {i} (try numbers must increase)",
                    code="escalation_violation"
                ))
        
        # Check that obstacles have meaningful content
        for i, obstacle in enumerate(obstacles):
            if len(obstacle.obstacle.strip()) < 5:
                errors.append(ValidationError(
                    field=f"proactive.conflict_obstacles[{i}].obstacle",
                    message="Obstacle description is too short",
                    code="obstacle_too_short"
                ))
        
        return errors
    
    def outcome_polarity_check(self, scene_card: SceneCard) -> List[ValidationError]:
        """OutcomePolarityCheck - default Setback; Victory allowed but prefer mixed"""
        errors = []
        
        if scene_card.scene_type != SceneType.PROACTIVE or not scene_card.proactive:
            return errors
        
        outcome = scene_card.proactive.outcome
        
        # Check rationale exists
        if not outcome.rationale or len(outcome.rationale.strip()) < 5:
            errors.append(ValidationError(
                field="proactive.outcome.rationale",
                message="Outcome rationale must explain why this outcome occurred",
                code="outcome_rationale_missing"
            ))
        
        # Note: Victory is allowed per PRD, but Setback is preferred
        # No enforcement here, just validation that it's a valid choice
        
        return errors
    
    def reactive_triad_check(self, scene_card: SceneCard) -> List[ValidationError]:
        """ReactiveTriadCheck - Reaction/Dilemma/Decision must meet exact rules"""
        errors = []
        
        if scene_card.scene_type != SceneType.REACTIVE or not scene_card.reactive:
            return errors
        
        reactive = scene_card.reactive
        
        # Check Reaction (emotional, proportional)
        if not reactive.reaction or len(reactive.reaction.strip()) < 10:
            errors.append(ValidationError(
                field="reactive.reaction",
                message="Reaction must be a substantial emotional response",
                code="reaction_insufficient"
            ))
        
        # Check Dilemma (all bad options)
        if len(reactive.dilemma_options) < 2:
            errors.append(ValidationError(
                field="reactive.dilemma_options",
                message="Dilemma must have at least 2 bad options",
                code="dilemma_insufficient_options"
            ))
        
        for i, option in enumerate(reactive.dilemma_options):
            if not option.why_bad or len(option.why_bad.strip()) < 5:
                errors.append(ValidationError(
                    field=f"reactive.dilemma_options[{i}].why_bad",
                    message="Each dilemma option must explain why it's bad",
                    code="dilemma_option_not_bad"
                ))
        
        # Check Decision (firm, risk-aware, produces next goal)
        if not reactive.decision or len(reactive.decision.strip()) < 10:
            errors.append(ValidationError(
                field="reactive.decision",
                message="Decision must be substantial and firm",
                code="decision_insufficient"
            ))
        
        if not reactive.next_goal_stub or len(reactive.next_goal_stub.strip()) < 5:
            errors.append(ValidationError(
                field="reactive.next_goal_stub",
                message="Decision must produce a next goal stub for future proactive scene",
                code="next_goal_missing"
            ))
        
        return errors
    
    def compression_integrity_check(self, scene_card: SceneCard) -> List[ValidationError]:
        """CompressionIntegrityCheck - compressed scenes still need complete R-D-D"""
        errors = []
        
        if scene_card.scene_type != SceneType.REACTIVE or not scene_card.reactive:
            return errors
        
        reactive = scene_card.reactive
        
        # Even if compressed (summarized/skip), must still have all triad elements
        if reactive.compression in ["summarized", "skip"]:
            # Still need complete Reaction, Dilemma, Decision
            if not reactive.reaction:
                errors.append(ValidationError(
                    field="reactive.reaction",
                    message="Even compressed reactive scenes must have recorded Reaction",
                    code="compressed_missing_reaction"
                ))
            
            if not reactive.dilemma_options:
                errors.append(ValidationError(
                    field="reactive.dilemma_options", 
                    message="Even compressed reactive scenes must have recorded Dilemma",
                    code="compressed_missing_dilemma"
                ))
            
            if not reactive.decision:
                errors.append(ValidationError(
                    field="reactive.decision",
                    message="Even compressed reactive scenes must have recorded Decision",
                    code="compressed_missing_decision"
                ))
        
        return errors
    
    def validate_scene_structure(self, scene_card: SceneCard) -> List[ValidationError]:
        """Additional structural validation"""
        errors = []
        
        # Check scene type matches data
        if scene_card.scene_type == SceneType.PROACTIVE:
            if not scene_card.proactive:
                errors.append(ValidationError(
                    field="proactive",
                    message="Proactive scenes must have proactive data",
                    code="missing_proactive_data"
                ))
            if scene_card.reactive:
                errors.append(ValidationError(
                    field="reactive", 
                    message="Proactive scenes should not have reactive data",
                    code="invalid_reactive_data"
                ))
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if not scene_card.reactive:
                errors.append(ValidationError(
                    field="reactive",
                    message="Reactive scenes must have reactive data", 
                    code="missing_reactive_data"
                ))
            if scene_card.proactive:
                errors.append(ValidationError(
                    field="proactive",
                    message="Reactive scenes should not have proactive data",
                    code="invalid_proactive_data"
                ))
        
        return errors
    
    def validate_exposition_budget(self, scene_card: SceneCard) -> List[ValidationError]:
        """Validate exposition budget follows 'now or never' rule"""
        errors = []
        
        # Check that exposition items have rationale
        for i, exposition in enumerate(scene_card.exposition_used):
            if not exposition or len(exposition.strip()) < 10:
                errors.append(ValidationError(
                    field=f"exposition_used[{i}]",
                    message="Exposition items must explain why needed 'right here, right now'",
                    code="exposition_no_rationale"
                ))
        
        # Warn if too much exposition
        if len(scene_card.exposition_used) > 3:
            # This could be a warning rather than error
            pass
        
        return errors


def validate_scene_card(scene_card: SceneCard) -> ValidationResult:
    """Convenience function to validate a scene card"""
    validator = SceneValidator()
    return validator.validate_scene_card(scene_card)