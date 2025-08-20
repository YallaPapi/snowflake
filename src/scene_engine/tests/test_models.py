"""
Unit tests for Scene Card models

Tests the Pydantic models, validation logic, and JSON schema generation.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError

from ..models import (
    SceneCard, SceneType, ViewpointType, TenseType, OutcomeType, CompressionType,
    ProactiveScene, ReactiveScene, GoalCriteria, ConflictObstacle, 
    Outcome, DilemmaOption
)
from ..validators import validate_scene_card
from ..schema import get_scene_card_example


class TestSceneCardModels:
    """Test Scene Card Pydantic models"""
    
    def test_proactive_scene_creation(self):
        """Test creating a valid proactive scene"""
        goal = GoalCriteria(
            text="Reach the radio room before patrol returns",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        
        obstacles = [
            ConflictObstacle(try_number=1, obstacle="Locked door"),
            ConflictObstacle(try_number=2, obstacle="Missing keys"),
            ConflictObstacle(try_number=3, obstacle="Guard footsteps approaching")
        ]
        
        outcome = Outcome(
            type=OutcomeType.SETBACK,
            rationale="Guard catches protagonist before reaching radio"
        )
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=obstacles,
            outcome=outcome
        )
        
        scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="John",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Trapped in enemy base now; discovery means capture or death.",
            place="Enemy military base",
            time="2 AM, under cover of darkness",
            proactive=proactive
        )
        
        assert scene.scene_type == SceneType.PROACTIVE
        assert scene.pov == "John"
        assert scene.proactive is not None
        assert scene.reactive is None
        assert len(scene.proactive.conflict_obstacles) == 3

    def test_reactive_scene_creation(self):
        """Test creating a valid reactive scene"""
        dilemma_options = [
            DilemmaOption(
                option="Run away",
                why_bad="Would abandon the mission and teammates"
            ),
            DilemmaOption(
                option="Surrender", 
                why_bad="Would reveal mission details under interrogation"
            ),
            DilemmaOption(
                option="Fight back",
                why_bad="Outnumbered, likely to fail and escalate violence"
            )
        ]
        
        reactive = ReactiveScene(
            reaction="Heart pounding with fear and anger at being caught",
            dilemma_options=dilemma_options,
            decision="Fight back despite the odds - create a distraction for teammates",
            next_goal_stub="Create enough chaos for team to escape",
            compression=CompressionType.FULL
        )
        
        scene = SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Sarah",
            viewpoint=ViewpointType.FIRST,
            tense=TenseType.PRESENT,
            scene_crucible="Surrounded now by armed guards; one wrong move means death for everyone.",
            place="Enemy compound courtyard",
            time="Present moment, after alarm sounds",
            reactive=reactive
        )
        
        assert scene.scene_type == SceneType.REACTIVE
        assert scene.reactive is not None
        assert scene.proactive is None
        assert len(scene.reactive.dilemma_options) == 3

    def test_goal_criteria_validation(self):
        """Test that goal criteria validation works"""
        # Valid goal
        goal = GoalCriteria(
            text="Valid goal text",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        assert goal.text == "Valid goal text"
        
        # Invalid goal - empty text
        with pytest.raises(PydanticValidationError):
            GoalCriteria(
                text="",
                fits_time=True,
                possible=True,
                difficult=True,
                fits_pov=True,
                concrete_objective=True
            )
        
        # Invalid goal - whitespace only
        with pytest.raises(PydanticValidationError):
            GoalCriteria(
                text="   ",
                fits_time=True,
                possible=True,
                difficult=True,
                fits_pov=True,
                concrete_objective=True
            )

    def test_conflict_obstacle_escalation(self):
        """Test that obstacles must escalate"""
        goal = GoalCriteria(
            text="Test goal",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        
        # Valid escalating obstacles
        valid_obstacles = [
            ConflictObstacle(try_number=1, obstacle="First obstacle"),
            ConflictObstacle(try_number=2, obstacle="Second obstacle"),
            ConflictObstacle(try_number=3, obstacle="Third obstacle")
        ]
        
        outcome = Outcome(type=OutcomeType.SETBACK, rationale="Test rationale")
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=valid_obstacles,
            outcome=outcome
        )
        
        assert len(proactive.conflict_obstacles) == 3
        
        # Invalid - non-escalating obstacles
        invalid_obstacles = [
            ConflictObstacle(try_number=1, obstacle="First obstacle"),
            ConflictObstacle(try_number=3, obstacle="Third obstacle"),
            ConflictObstacle(try_number=2, obstacle="Second obstacle")  # Wrong order
        ]
        
        with pytest.raises(PydanticValidationError):
            ProactiveScene(
                goal=goal,
                conflict_obstacles=invalid_obstacles,
                outcome=outcome
            )

    def test_reactive_dilemma_validation(self):
        """Test reactive scene dilemma validation"""
        # Valid dilemma with multiple bad options
        valid_options = [
            DilemmaOption(option="Option 1", why_bad="Reason 1 why bad"),
            DilemmaOption(option="Option 2", why_bad="Reason 2 why bad"),
            DilemmaOption(option="Option 3", why_bad="Reason 3 why bad")
        ]
        
        reactive = ReactiveScene(
            reaction="Valid reaction",
            dilemma_options=valid_options,
            decision="Final decision made",
            next_goal_stub="Next goal stub",
            compression=CompressionType.FULL
        )
        
        assert len(reactive.dilemma_options) == 3
        
        # Invalid - not enough options
        with pytest.raises(PydanticValidationError):
            ReactiveScene(
                reaction="Valid reaction",
                dilemma_options=[DilemmaOption(option="Only option", why_bad="Reason")],
                decision="Final decision made",
                next_goal_stub="Next goal stub",
                compression=CompressionType.FULL
            )

    def test_scene_type_data_validation(self):
        """Test that scenes have appropriate data for their type"""
        proactive_data = ProactiveScene(
            goal=GoalCriteria(
                text="Test goal",
                fits_time=True,
                possible=True,
                difficult=True,
                fits_pov=True,
                concrete_objective=True
            ),
            conflict_obstacles=[ConflictObstacle(try_number=1, obstacle="Test obstacle")],
            outcome=Outcome(type=OutcomeType.SETBACK, rationale="Test rationale")
        )
        
        # Valid - proactive scene with proactive data
        scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Test POV",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Test crucible with immediate danger now.",
            place="Test place",
            time="Test time",
            proactive=proactive_data
        )
        
        assert scene.scene_type == SceneType.PROACTIVE
        assert scene.proactive is not None
        
        # Invalid - proactive scene without proactive data
        with pytest.raises(PydanticValidationError):
            SceneCard(
                scene_type=SceneType.PROACTIVE,
                pov="Test POV",
                viewpoint=ViewpointType.THIRD,
                tense=TenseType.PAST,
                scene_crucible="Test crucible with immediate danger now.",
                place="Test place",
                time="Test time"
                # Missing proactive data
            )

    def test_scene_crucible_validation(self):
        """Test Scene Crucible validation"""
        proactive_data = ProactiveScene(
            goal=GoalCriteria(
                text="Test goal",
                fits_time=True,
                possible=True,
                difficult=True,
                fits_pov=True,
                concrete_objective=True
            ),
            conflict_obstacles=[ConflictObstacle(try_number=1, obstacle="Test obstacle")],
            outcome=Outcome(type=OutcomeType.SETBACK, rationale="Test rationale")
        )
        
        # Valid scene crucible
        scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Test POV",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Immediate danger right now; if action fails, death is certain.",
            place="Test place",
            time="Test time",
            proactive=proactive_data
        )
        
        assert "now" in scene.scene_crucible.lower()
        
        # Invalid - empty crucible
        with pytest.raises(PydanticValidationError):
            SceneCard(
                scene_type=SceneType.PROACTIVE,
                pov="Test POV",
                viewpoint=ViewpointType.THIRD,
                tense=TenseType.PAST,
                scene_crucible="",
                place="Test place",
                time="Test time",
                proactive=proactive_data
            )
        
        # Invalid - too short
        with pytest.raises(PydanticValidationError):
            SceneCard(
                scene_type=SceneType.PROACTIVE,
                pov="Test POV",
                viewpoint=ViewpointType.THIRD,
                tense=TenseType.PAST,
                scene_crucible="Short",
                place="Test place",
                time="Test time",
                proactive=proactive_data
            )


class TestExampleScenes:
    """Test the example scenes from the PRD"""
    
    def test_dirk_parachute_example(self):
        """Test the Dirk parachute proactive scene example"""
        examples = get_scene_card_example()
        dirk_data = examples["proactive_example"]
        
        # Should be able to create SceneCard from example data
        scene = SceneCard(**dirk_data)
        
        assert scene.scene_type == SceneType.PROACTIVE
        assert scene.pov == "Dirk"
        assert scene.proactive is not None
        assert scene.proactive.outcome.type == OutcomeType.SETBACK
        assert len(scene.proactive.conflict_obstacles) == 3

    def test_goldilocks_pepper_spray_example(self):
        """Test the Goldilocks pepper spray reactive scene example"""
        examples = get_scene_card_example()
        goldilocks_data = examples["reactive_example"]
        
        # Should be able to create SceneCard from example data
        scene = SceneCard(**goldilocks_data)
        
        assert scene.scene_type == SceneType.REACTIVE
        assert scene.pov == "Goldilocks"
        assert scene.reactive is not None
        assert scene.reactive.compression == CompressionType.FULL
        assert len(scene.reactive.dilemma_options) == 4


class TestSceneValidation:
    """Test the custom validation logic"""
    
    def test_valid_scene_passes_validation(self):
        """Test that a valid scene passes all validation checks"""
        examples = get_scene_card_example()
        scene = SceneCard(**examples["proactive_example"])
        
        result = validate_scene_card(scene)
        
        # Should pass validation (though may have warnings)
        assert result.is_valid or len(result.errors) == 0

    def test_invalid_scene_fails_validation(self):
        """Test that invalid scenes fail validation appropriately"""
        # Create a scene with validation issues
        scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="",  # Invalid - empty POV
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="No immediate danger mentioned",  # Invalid - no 'now' language
            place="Test place",
            time="Test time"
            # Missing proactive data for proactive scene
        )
        
        result = validate_scene_card(scene)
        
        assert not result.is_valid
        assert len(result.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])