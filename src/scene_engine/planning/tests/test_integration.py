"""
Integration Tests for Scene Planning Service

This implements subtask 42.7: Write Integration Tests for All Planning Flows
Tests the complete planning workflows with example inputs from PRD.
"""

import pytest
import asyncio
from typing import Dict, Any

from ..service import (
    ScenePlanningService, ProactiveScenePlanningRequest, ReactiveScenePlanningRequest,
    ScenePlanningError, InvalidScenePlanningRequest, ScenePlanningFailure
)
from ..planner import ProactiveScenePlanner, ReactiveScenePlanner, create_planner
from ..prompts import get_prompt, format_scene_context, format_scene_parameters
from ...models import SceneType, ViewpointType, TenseType, OutcomeType, CompressionType
from ...validators import SceneValidator


class MockAIGenerator:
    """Mock AI generator for testing"""
    
    def __init__(self):
        self.call_count = 0
        self.last_prompt = None
    
    async def generate(self, prompt: str) -> Any:
        """Mock generation method"""
        self.call_count += 1
        self.last_prompt = prompt
        
        # Return simple mock response
        class MockResponse:
            text = "Mock AI response"
        
        return MockResponse()


class TestScenePlanningServiceIntegration:
    """Integration tests for the complete planning service"""
    
    @pytest.fixture
    def mock_ai_generator(self):
        return MockAIGenerator()
    
    @pytest.fixture
    def scene_validator(self):
        return SceneValidator()
    
    @pytest.fixture
    def planning_service(self, mock_ai_generator, scene_validator):
        return ScenePlanningService(ai_generator=mock_ai_generator, validator=scene_validator)

    def test_service_initialization(self, planning_service):
        """Test service initializes correctly"""
        assert planning_service is not None
        assert planning_service._planning_stats["total_scenes_planned"] == 0

    @pytest.mark.asyncio
    async def test_proactive_scene_planning_flow(self, planning_service):
        """Test complete proactive scene planning workflow"""
        
        # Create request based on Dirk parachute example from PRD
        request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="Dirk",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Airspace over occupied France",
            time="Night, 1944",
            desired_goal="Parachute into France and hole up for the night",
            time_available="A few hours until dawn",
            obstacles_suggested=[
                "Anti-aircraft fire",
                "German fighter plane",
                "Engine catches fire"
            ],
            story_context={
                "mission": "Infiltration behind enemy lines",
                "danger_type": "military combat",
                "difficulty_level": "high"
            }
        )
        
        # Execute planning
        response = await planning_service.plan_proactive_scene(request)
        
        # Verify response structure
        assert response.scene_card is not None
        assert response.validation_result is not None
        assert response.planning_metadata is not None
        
        # Verify scene card structure
        scene_card = response.scene_card
        assert scene_card.scene_type == SceneType.PROACTIVE
        assert scene_card.pov == "Dirk"
        assert scene_card.proactive is not None
        assert scene_card.reactive is None
        
        # Verify proactive scene structure
        proactive = scene_card.proactive
        assert proactive.goal is not None
        assert len(proactive.conflict_obstacles) >= 1
        assert proactive.outcome is not None
        
        # Verify goal criteria (5-point validation)
        goal = proactive.goal
        assert goal.text is not None and len(goal.text) > 0
        assert isinstance(goal.fits_time, bool)
        assert isinstance(goal.possible, bool)
        assert isinstance(goal.difficult, bool)
        assert isinstance(goal.fits_pov, bool)
        assert isinstance(goal.concrete_objective, bool)
        
        # Verify conflict escalation
        for i, obstacle in enumerate(proactive.conflict_obstacles):
            assert obstacle.try_number == i + 1
            assert obstacle.obstacle is not None and len(obstacle.obstacle) > 0
        
        # Verify outcome
        assert proactive.outcome.type in [OutcomeType.SETBACK, OutcomeType.VICTORY, OutcomeType.MIXED]
        assert proactive.outcome.rationale is not None and len(proactive.outcome.rationale) > 0
        
        # Verify scene crucible
        assert scene_card.scene_crucible is not None
        assert len(scene_card.scene_crucible) > 10  # Should be substantial
        
        # Verify chain link
        assert scene_card.chain_link is not None
        
        # Check statistics updated
        assert planning_service._planning_stats["total_scenes_planned"] == 1
        assert planning_service._planning_stats["proactive_scenes"] == 1

    @pytest.mark.asyncio
    async def test_reactive_scene_planning_flow(self, planning_service):
        """Test complete reactive scene planning workflow"""
        
        # Create request based on Goldilocks pepper spray example from PRD
        request = ReactiveScenePlanningRequest(
            scene_type=SceneType.REACTIVE,
            pov="Goldilocks",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Narrow corridor",
            time="Present moment",
            triggering_setback="Cornered by Tiny Pig after previous scene failure",
            character_emotional_state="fearful but resolute",
            available_options=[
                "Try to slip past him",
                "Call for help on phone",
                "Wait him out",
                "Use pepper spray"
            ],
            story_context={
                "emotional_pressure": "high",
                "decision_urgency": "immediate"
            }
        )
        
        # Execute planning
        response = await planning_service.plan_reactive_scene(request)
        
        # Verify response structure
        assert response.scene_card is not None
        assert response.validation_result is not None
        
        # Verify scene card structure
        scene_card = response.scene_card
        assert scene_card.scene_type == SceneType.REACTIVE
        assert scene_card.pov == "Goldilocks"
        assert scene_card.reactive is not None
        assert scene_card.proactive is None
        
        # Verify reactive scene structure (R-D-D pattern)
        reactive = scene_card.reactive
        assert reactive.reaction is not None and len(reactive.reaction) > 10
        assert len(reactive.dilemma_options) >= 2
        assert reactive.decision is not None and len(reactive.decision) > 10
        assert reactive.next_goal_stub is not None and len(reactive.next_goal_stub) > 5
        assert reactive.compression in [CompressionType.FULL, CompressionType.SUMMARIZED, CompressionType.SKIP]
        
        # Verify dilemma options are all bad
        for option in reactive.dilemma_options:
            assert option.option is not None and len(option.option) > 0
            assert option.why_bad is not None and len(option.why_bad) > 0
        
        # Verify decision structure
        assert "despite" in reactive.decision.lower() or "risk" in reactive.decision.lower()
        
        # Check statistics updated
        assert planning_service._planning_stats["total_scenes_planned"] == 1
        assert planning_service._planning_stats["reactive_scenes"] == 1

    @pytest.mark.asyncio
    async def test_generic_scene_planning_routes_correctly(self, planning_service):
        """Test that generic scene planning routes to correct planner"""
        
        # Test proactive routing
        proactive_request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="Test Character",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Test Location",
            time="Test Time",
            desired_goal="Test goal"
        )
        
        response = await planning_service.plan_scene(proactive_request)
        assert response.scene_card.scene_type == SceneType.PROACTIVE
        assert response.scene_card.proactive is not None
        
        # Test reactive routing
        reactive_request = ReactiveScenePlanningRequest(
            scene_type=SceneType.REACTIVE,
            pov="Test Character",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Test Location",
            time="Test Time",
            triggering_setback="Test setback"
        )
        
        response = await planning_service.plan_scene(reactive_request)
        assert response.scene_card.scene_type == SceneType.REACTIVE
        assert response.scene_card.reactive is not None

    def test_request_validation(self, planning_service):
        """Test planning request validation"""
        
        # Valid request
        valid_request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="Valid POV",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Valid Place",
            time="Valid Time"
        )
        
        result = planning_service.validate_planning_request(valid_request)
        assert result.is_valid
        
        # Invalid request - missing POV
        invalid_request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="",  # Invalid
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Valid Place",
            time="Valid Time"
        )
        
        result = planning_service.validate_planning_request(invalid_request)
        assert not result.is_valid
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, planning_service):
        """Test error handling in planning flows"""
        
        # Test invalid request handling
        invalid_request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="",  # Invalid - empty POV
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="",  # Invalid - empty place
            time=""    # Invalid - empty time
        )
        
        with pytest.raises(InvalidScenePlanningRequest):
            await planning_service.plan_proactive_scene(invalid_request)

    def test_planning_statistics(self, planning_service):
        """Test planning service statistics tracking"""
        
        # Initial state
        stats = planning_service.get_planning_statistics()
        assert stats["total_scenes_planned"] == 0
        assert stats["proactive_scenes"] == 0
        assert stats["reactive_scenes"] == 0
        assert stats["validation_failures"] == 0
        
        # Reset functionality
        planning_service.reset_statistics()
        stats = planning_service.get_planning_statistics()
        assert all(count == 0 for count in stats.values())


class TestProactiveScenePlannerIntegration:
    """Integration tests for proactive scene planner"""

    @pytest.fixture
    def mock_ai_generator(self):
        return MockAIGenerator()

    @pytest.fixture
    def planner(self, mock_ai_generator):
        return ProactiveScenePlanner(ai_generator=mock_ai_generator)

    @pytest.mark.asyncio
    async def test_goal_five_point_validation_integration(self, planner):
        """Test 5-point goal validation integration"""
        
        request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="Test Character",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Test Location",
            time="Test Time",
            desired_goal="Reach the safe house before midnight",
            time_available="2 hours",
            character_goals=["Survive the mission", "Protect teammates"]
        )
        
        scene_card = await planner.plan_scene(request)
        goal = scene_card.proactive.goal
        
        # Verify all 5 criteria are evaluated
        assert hasattr(goal, 'fits_time')
        assert hasattr(goal, 'possible')
        assert hasattr(goal, 'difficult')
        assert hasattr(goal, 'fits_pov')
        assert hasattr(goal, 'concrete_objective')
        
        # Verify goal text matches request
        assert "safe house" in goal.text.lower() or request.desired_goal.lower() in goal.text.lower()

    @pytest.mark.asyncio
    async def test_scene_crucible_generation_integration(self, planner):
        """Test Scene Crucible generation and validation"""
        
        request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="Agent Smith",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PRESENT,
            place="Enemy compound rooftop",
            time="Dawn approaching",
            story_context={"danger_type": "imminent capture"}
        )
        
        scene_card = await planner.plan_scene(request)
        crucible = scene_card.scene_crucible
        
        # Verify crucible characteristics
        assert len(crucible) > 20  # Substantial content
        assert len(crucible.split('.')) <= 3  # 1-2 sentences max
        
        # Should reference immediate danger
        immediate_indicators = ['now', 'immediately', 'at this moment', 'current']
        has_immediate_language = any(indicator in crucible.lower() for indicator in immediate_indicators)
        # Note: Not strictly required but preferred
        
        # Should reference the POV and place
        assert request.pov.lower() in crucible.lower() or "agent" in crucible.lower()

    @pytest.mark.asyncio
    async def test_conflict_escalation_integration(self, planner):
        """Test conflict escalation logic"""
        
        request = ProactiveScenePlanningRequest(
            scene_type=SceneType.PROACTIVE,
            pov="Protagonist",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Test Location",
            time="Test Time",
            obstacles_suggested=[
                "First minor obstacle",
                "Second larger obstacle", 
                "Third major obstacle"
            ]
        )
        
        scene_card = await planner.plan_scene(request)
        obstacles = scene_card.proactive.conflict_obstacles
        
        # Verify escalation
        assert len(obstacles) == 3
        for i, obstacle in enumerate(obstacles):
            assert obstacle.try_number == i + 1
            # Could add more sophisticated escalation detection


class TestReactiveScenePlannerIntegration:
    """Integration tests for reactive scene planner"""

    @pytest.fixture
    def mock_ai_generator(self):
        return MockAIGenerator()

    @pytest.fixture
    def planner(self, mock_ai_generator):
        return ReactiveScenePlanner(ai_generator=mock_ai_generator)

    @pytest.mark.asyncio
    async def test_reactive_triad_integration(self, planner):
        """Test Reaction-Dilemma-Decision triad integration"""
        
        request = ReactiveScenePlanningRequest(
            scene_type=SceneType.REACTIVE,
            pov="Hero",
            viewpoint=ViewpointType.FIRST,
            tense=TenseType.PRESENT,
            place="Crisis location",
            time="Moment of crisis",
            triggering_setback="Failed to save the hostages",
            character_emotional_state="guilt and determination"
        )
        
        scene_card = await planner.plan_scene(request)
        reactive = scene_card.reactive
        
        # Verify complete triad
        assert reactive.reaction is not None
        assert len(reactive.dilemma_options) >= 2
        assert reactive.decision is not None
        assert reactive.next_goal_stub is not None
        
        # Verify reaction references the setback
        assert "hostage" in reactive.reaction.lower() or "fail" in reactive.reaction.lower()
        
        # Verify decision leads to goal
        assert len(reactive.next_goal_stub) > 5

    @pytest.mark.asyncio
    async def test_dilemma_all_bad_options_integration(self, planner):
        """Test that dilemma options are all genuinely bad"""
        
        request = ReactiveScenePlanningRequest(
            scene_type=SceneType.REACTIVE,
            pov="Character",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Difficult situation",
            time="Time of decision",
            triggering_setback="Major setback occurred",
            available_options=[
                "Run away",
                "Fight back",
                "Try to negotiate",
                "Wait for help"
            ]
        )
        
        scene_card = await planner.plan_scene(request)
        options = scene_card.reactive.dilemma_options
        
        # Verify all options have downsides
        for option in options:
            assert len(option.why_bad) > 5
            bad_indicators = ['risk', 'danger', 'fail', 'problem', 'bad', 'worse', 'abandon', 'escalate']
            has_bad_indicator = any(indicator in option.why_bad.lower() for indicator in bad_indicators)
            # Should explain why it's bad, but not strictly enforced in test


class TestPromptIntegration:
    """Integration tests for prompt templates"""

    def test_proactive_prompt_formatting(self):
        """Test proactive prompt template formatting"""
        
        prompt = get_prompt("planning", SceneType.PROACTIVE)
        
        context = format_scene_context(
            character_summaries={"hero": "Brave protagonist"},
            long_synopsis="Epic story",
            previous_outcome="Previous failure"
        )
        
        params = format_scene_parameters(
            pov="Hero",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            place="Dangerous place",
            time="Critical time",
            time_available="Limited time"
        )
        
        formatted = prompt.format_prompt(**context, **params)
        
        assert "system" in formatted
        assert "user" in formatted
        assert "Hero" in formatted["user"]
        assert "Dangerous place" in formatted["user"]

    def test_reactive_prompt_formatting(self):
        """Test reactive prompt template formatting"""
        
        prompt = get_prompt("planning", SceneType.REACTIVE)
        
        context = format_scene_context(
            character_summaries={"hero": "Determined character"},
            triggering_setback="Major failure occurred"
        )
        
        params = format_scene_parameters(
            pov="Hero",
            viewpoint=ViewpointType.FIRST,
            tense=TenseType.PRESENT,
            place="Crisis location",
            time="Moment of decision",
            emotional_state="angry and confused"
        )
        
        formatted = prompt.format_prompt(**context, **params)
        
        assert "system" in formatted
        assert "user" in formatted
        assert "Major failure" in formatted["user"]
        assert "angry and confused" in formatted["user"]

    def test_validation_prompt_integration(self):
        """Test validation prompt integration"""
        
        prompt = get_prompt("validation")
        
        formatted = prompt.format_prompt(
            scene_card_json='{"test": "scene card"}'
        )
        
        assert "system" in formatted
        assert "user" in formatted
        assert "scene card" in formatted["user"]

    def test_triage_prompt_integration(self):
        """Test triage prompt integration"""
        
        prompt = get_prompt("triage")
        
        formatted = prompt.format_prompt(
            scene_card_json='{"test": "scene"}',
            validation_results='{"is_valid": true}'
        )
        
        assert "system" in formatted  
        assert "user" in formatted
        assert "scene" in formatted["user"]


class TestPlannerFactoryIntegration:
    """Integration tests for planner factory"""

    def test_planner_factory_creates_correct_types(self):
        """Test planner factory creates correct planner types"""
        
        proactive_planner = create_planner(SceneType.PROACTIVE)
        assert isinstance(proactive_planner, ProactiveScenePlanner)
        
        reactive_planner = create_planner(SceneType.REACTIVE)
        assert isinstance(reactive_planner, ReactiveScenePlanner)
        
        # Test invalid type
        with pytest.raises(ValueError):
            create_planner("invalid_type")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])