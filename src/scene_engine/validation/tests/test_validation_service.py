"""
Validation Service Tests

This implements testing for subtask 43.7: Build Validation Pipeline and Reporting System
Tests the validation service, pipeline, and reporting functionality.
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Dict

from ..service import (
    SceneValidationService, ValidationRequest, ValidationResponse,
    ValidationReport, ValidationMetrics, ValidationRuleCitation,
    validate_scene_card_async, validate_scene_card_sync
)
from ..pipeline import ValidationPipeline, ValidationStage, PipelineResult, validate_scene_with_pipeline
from ...models import (
    SceneCard, SceneType, ProactiveScene, ReactiveScene,
    GoalCriteria, ConflictObstacle, Outcome, DilemmaOption,
    OutcomeType, CompressionType, ViewpointType, TenseType
)
from ...validators import SceneValidator


class TestValidationService:
    """Test the scene validation service"""
    
    @pytest.fixture
    def validation_service(self):
        return SceneValidationService()
    
    @pytest.fixture
    def valid_proactive_scene(self):
        """Create a valid proactive scene card for testing"""
        goal = GoalCriteria(
            text="Reach the safe house before midnight",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        
        obstacles = [
            ConflictObstacle(try_number=1, obstacle="First security checkpoint"),
            ConflictObstacle(try_number=2, obstacle="Patrol guards spot movement"),
            ConflictObstacle(try_number=3, obstacle="Final desperate climb over razor wire")
        ]
        
        outcome = Outcome(
            type=OutcomeType.SETBACK,
            rationale="Captured at final checkpoint due to injury from razor wire"
        )
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=obstacles,
            outcome=outcome
        )
        
        return SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Agent Smith",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Agent Smith faces immediate capture at the checkpoint now; one wrong move means mission failure.",
            place="Enemy compound entrance",
            time="11:30 PM, 30 minutes before deadline",
            proactive=proactive,
            exposition_used=["Checkpoint layout needed for navigation", "Time pressure drives urgency"],
            chain_link="setback→captured, needs reactive scene for escape planning"
        )
    
    @pytest.fixture  
    def valid_reactive_scene(self):
        """Create a valid reactive scene card for testing"""
        dilemma_options = [
            DilemmaOption(option="Try to fight the guards", why_bad="Outnumbered and will escalate violence"),
            DilemmaOption(option="Attempt to negotiate", why_bad="Shows weakness and may not work"), 
            DilemmaOption(option="Wait for rescue", why_bad="Rescue may not come and situation deteriorates")
        ]
        
        reactive = ReactiveScene(
            reaction="Agent Smith feels rage and desperation after being captured. The mission failure hits hard but there's no time for self-pity.",
            dilemma_options=dilemma_options,
            decision="Choose to try negotiation despite the risk of showing weakness. This forces guards to respond and may create an opening.",
            next_goal_stub="Successfully negotiate release or escape during transfer",
            compression=CompressionType.FULL
        )
        
        return SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Agent Smith", 
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Captured and handcuffed now in the guardhouse; must decide quickly before interrogation begins.",
            place="Enemy compound guardhouse",
            time="Just after capture",
            reactive=reactive,
            exposition_used=["Capture context needed for emotional reaction"],
            chain_link="negotiation decision→next proactive goal (escape attempt)"
        )
    
    @pytest.fixture
    def invalid_scene(self):
        """Create an invalid scene card for testing"""
        return SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="",  # Invalid - empty POV
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="",  # Invalid - empty crucible
            place="",  # Invalid - empty place
            time="",   # Invalid - empty time
            proactive=None  # Invalid - missing proactive data
        )
    
    def test_service_initialization(self, validation_service):
        """Test validation service initializes correctly"""
        assert validation_service is not None
        assert validation_service.validator is not None
        assert isinstance(validation_service.rule_citations, dict)
        assert len(validation_service.rule_citations) == 6
        
        # Check statistics initialization
        stats = validation_service.get_validation_statistics()
        assert stats["total_validations"] == 0
        assert stats["success_rate"] == 0.0
    
    @pytest.mark.asyncio
    async def test_valid_proactive_scene_validation(self, validation_service, valid_proactive_scene):
        """Test validation of a valid proactive scene"""
        request = ValidationRequest(scene_card=valid_proactive_scene)
        response = await validation_service.validate_scene(request)
        
        # Check response structure
        assert isinstance(response, ValidationResponse)
        assert response.request_id.startswith("val_")
        assert response.processing_time_ms > 0
        
        # Check validation report
        report = response.validation_report
        assert isinstance(report, ValidationReport)
        assert report.scene_type == SceneType.PROACTIVE
        assert report.is_valid == True  # Should be valid
        assert len(report.validation_errors) == 0
        
        # Check rule citations
        assert isinstance(report.rule_citations, list)
        
        # Check metrics
        assert isinstance(report.validation_metrics, ValidationMetrics)
        assert report.validation_metrics.total_checks_run == 6
        
        # Check recommendations
        assert isinstance(report.recommendations, list)
    
    @pytest.mark.asyncio
    async def test_valid_reactive_scene_validation(self, validation_service, valid_reactive_scene):
        """Test validation of a valid reactive scene"""
        request = ValidationRequest(scene_card=valid_reactive_scene)
        response = await validation_service.validate_scene(request)
        
        report = response.validation_report
        assert report.scene_type == SceneType.REACTIVE
        assert report.is_valid == True
        assert len(report.validation_errors) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_scene_validation(self, validation_service, invalid_scene):
        """Test validation of an invalid scene"""
        request = ValidationRequest(scene_card=invalid_scene)
        response = await validation_service.validate_scene(request)
        
        report = response.validation_report
        assert report.is_valid == False
        assert len(report.validation_errors) > 0
        
        # Should have rule citations for failed checks
        assert len(report.rule_citations) > 0
        
        # Should have recommendations
        assert len(report.recommendations) > 0
    
    def test_rule_citation_extraction(self, validation_service):
        """Test rule citation extraction logic"""
        # Test crucible error
        from ...models import ValidationError
        
        errors = [
            ValidationError(field="scene_crucible", message="test", code="crucible_missing"),
            ValidationError(field="goal", message="test", code="goal_criterion_fits_time_failed")
        ]
        
        citations = validation_service._extract_rule_citations(errors)
        
        assert len(citations) == 2
        citation_names = [c.rule_name for c in citations]
        assert "CrucibleNowCheck" in citation_names
        assert "GoalFiveCheck" in citation_names
    
    def test_recommendation_generation(self, validation_service, invalid_scene):
        """Test recommendation generation"""
        from ...models import ValidationError
        
        errors = [
            ValidationError(field="scene_crucible", message="test", code="crucible_missing"),
            ValidationError(field="goal", message="test", code="goal_criterion_difficult_failed")
        ]
        
        recommendations = validation_service._generate_recommendations(invalid_scene, errors)
        
        assert len(recommendations) > 0
        # Should include crucible and goal recommendations
        crucible_recs = [r for r in recommendations if "Crucible" in r]
        goal_recs = [r for r in recommendations if "goal" in r.lower()]
        assert len(crucible_recs) > 0
        assert len(goal_recs) > 0
    
    @pytest.mark.asyncio 
    async def test_batch_validation(self, validation_service, valid_proactive_scene, valid_reactive_scene):
        """Test batch validation of multiple scenes"""
        requests = [
            ValidationRequest(scene_card=valid_proactive_scene),
            ValidationRequest(scene_card=valid_reactive_scene)
        ]
        
        responses = await validation_service.validate_scene_batch(requests)
        
        assert len(responses) == 2
        assert all(isinstance(r, ValidationResponse) for r in responses)
        assert responses[0].validation_report.scene_type == SceneType.PROACTIVE
        assert responses[1].validation_report.scene_type == SceneType.REACTIVE
    
    def test_synchronous_validation(self, validation_service, valid_proactive_scene):
        """Test synchronous validation wrapper"""
        response = validation_service.validate_scene_sync(valid_proactive_scene)
        
        assert isinstance(response, ValidationResponse)
        assert response.validation_report.is_valid == True
    
    def test_statistics_tracking(self, validation_service, valid_proactive_scene, invalid_scene):
        """Test validation statistics tracking"""
        # Initial stats
        stats = validation_service.get_validation_statistics()
        assert stats["total_validations"] == 0
        
        # Valid validation
        validation_service.validate_scene_sync(valid_proactive_scene)
        stats = validation_service.get_validation_statistics()
        assert stats["total_validations"] == 1
        assert stats["successful_validations"] == 1
        
        # Invalid validation
        validation_service.validate_scene_sync(invalid_scene)
        stats = validation_service.get_validation_statistics()
        assert stats["total_validations"] == 2
        assert stats["successful_validations"] == 1
        assert stats["failed_validations"] == 1
        assert stats["success_rate"] == 50.0
        
        # Reset stats
        validation_service.reset_statistics()
        stats = validation_service.get_validation_statistics()
        assert stats["total_validations"] == 0
    
    def test_validation_report_summary(self, valid_proactive_scene):
        """Test validation report summary generation"""
        service = SceneValidationService()
        response = service.validate_scene_sync(valid_proactive_scene)
        
        summary = response.validation_report.to_summary()
        assert "✅ VALID" in summary
        assert "proactive" in summary.lower()


class TestValidationPipeline:
    """Test the validation pipeline"""
    
    @pytest.fixture
    def pipeline(self):
        return ValidationPipeline()
    
    @pytest.fixture
    def valid_proactive_scene(self):
        """Same as above"""
        goal = GoalCriteria(
            text="Reach the safe house before midnight",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        
        obstacles = [
            ConflictObstacle(try_number=1, obstacle="First security checkpoint"),
            ConflictObstacle(try_number=2, obstacle="Patrol guards spot movement") 
        ]
        
        outcome = Outcome(
            type=OutcomeType.SETBACK,
            rationale="Captured due to guard patrol"
        )
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=obstacles,
            outcome=outcome
        )
        
        return SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Agent",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Agent faces immediate capture now; one wrong move means mission failure.",
            place="Compound",
            time="Night",
            proactive=proactive,
            exposition_used=["Location context needed"],
            chain_link="setback→reactive scene needed"
        )
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes correctly"""
        assert pipeline is not None
        assert len(pipeline.stages) > 0
        
        # Check stage types exist
        stage_names = [stage.name for stage in pipeline.stages]
        expected_stages = [
            "structural_validation", "crucible_validation", 
            "goal_validation", "reactive_triad_validation"
        ]
        for expected in expected_stages:
            assert expected in stage_names
    
    def test_stage_applicability(self, pipeline, valid_proactive_scene):
        """Test stage applicability logic"""
        applicable_stages = pipeline._get_applicable_stages(valid_proactive_scene)
        
        stage_names = [stage.name for stage in applicable_stages]
        
        # Should include proactive-specific stages
        assert "goal_validation" in stage_names
        assert "conflict_validation" in stage_names
        assert "outcome_validation" in stage_names
        
        # Should not include reactive-specific stages
        assert "reactive_triad_validation" not in stage_names
        assert "compression_validation" not in stage_names
    
    @pytest.mark.asyncio
    async def test_pipeline_execution(self, pipeline, valid_proactive_scene):
        """Test complete pipeline execution"""
        result = await pipeline.validate_scene(valid_proactive_scene)
        
        assert isinstance(result, PipelineResult)
        assert result.scene_id is not None
        assert result.total_duration_ms > 0
        assert len(result.stage_results) > 0
        
        # Should be successful for valid scene
        assert result.overall_success == True
        
        # Check stage results
        for stage_result in result.stage_results:
            assert stage_result.stage_name is not None
            assert stage_result.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_pipeline_fail_fast(self, pipeline):
        """Test fail-fast pipeline execution"""
        # Create scene that will fail early
        invalid_scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Test",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="",  # This will fail crucible validation
            place="Place",
            time="Time"
        )
        
        result = await pipeline.validate_scene(invalid_scene, fail_fast=True)
        
        assert result.overall_success == False
        # Should stop after first failure
        failed_stages = [r for r in result.stage_results if not r.success]
        assert len(failed_stages) > 0
    
    def test_dependency_satisfaction(self, pipeline):
        """Test stage dependency logic"""
        stage_with_deps = None
        for stage in pipeline.stages:
            if len(stage.depends_on) > 0:
                stage_with_deps = stage
                break
        
        assert stage_with_deps is not None
        
        # Empty completed set - dependencies not satisfied
        assert not pipeline._dependencies_satisfied(stage_with_deps, set())
        
        # With dependencies - should be satisfied
        completed = set(stage_with_deps.depends_on)
        assert pipeline._dependencies_satisfied(stage_with_deps, completed)
    
    def test_pipeline_statistics(self, pipeline, valid_proactive_scene):
        """Test pipeline statistics tracking"""
        # Initial stats
        stats = pipeline.get_pipeline_statistics()
        assert stats["total_runs"] == 0
        
        # Run pipeline
        asyncio.run(pipeline.validate_scene(valid_proactive_scene))
        
        stats = pipeline.get_pipeline_statistics()
        assert stats["total_runs"] == 1
        assert stats["successful_runs"] == 1
        assert stats["avg_duration_ms"] > 0
    
    def test_stage_info(self, pipeline):
        """Test stage information retrieval"""
        stage_info = pipeline.get_stage_info()
        
        assert len(stage_info) > 0
        assert all("name" in info for info in stage_info)
        assert all("description" in info for info in stage_info)
        assert all("required" in info for info in stage_info)


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @pytest.fixture
    def valid_scene(self):
        """Simple valid scene for testing"""
        goal = GoalCriteria(
            text="Test goal",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=[ConflictObstacle(try_number=1, obstacle="Test obstacle")],
            outcome=Outcome(type=OutcomeType.SETBACK, rationale="Test rationale")
        )
        
        return SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Test",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Test scene faces immediate danger now.",
            place="Test place",
            time="Test time",
            proactive=proactive,
            exposition_used=["Test exposition"],
            chain_link="Test chain link"
        )
    
    @pytest.mark.asyncio
    async def test_async_convenience_function(self, valid_scene):
        """Test async convenience function"""
        response = await validate_scene_card_async(valid_scene)
        
        assert isinstance(response, ValidationResponse)
        assert response.validation_report.is_valid == True
    
    def test_sync_convenience_function(self, valid_scene):
        """Test sync convenience function"""  
        response = validate_scene_card_sync(valid_scene)
        
        assert isinstance(response, ValidationResponse)
        assert response.validation_report.is_valid == True
    
    @pytest.mark.asyncio
    async def test_pipeline_convenience_function(self, valid_scene):
        """Test pipeline convenience function"""
        result = await validate_scene_with_pipeline(valid_scene)
        
        assert isinstance(result, PipelineResult)
        assert result.overall_success == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])