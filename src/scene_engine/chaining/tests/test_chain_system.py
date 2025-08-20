"""
Chain System Comprehensive Tests

This implements subtask 46.6: Write Tests for Chain Validation and Consistency
Tests chain link generation, validation, transitions, sequences, and consistency.
"""

import pytest
import tempfile
import json
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from ..models import (
    ChainLink, ChainSequence, SceneReference, ChainMetadata,
    ChainLinkType, TransitionType, ChainStrength, ChainValidationResult
)
from ..generator import (
    ChainLinkGenerator, ChainGenerationContext, TransitionRule,
    generate_chain_from_scene, generate_chain_sequence
)
from ..validator import (
    ChainLinkValidator, ChainSequenceValidator, ValidationSeverity,
    validate_chain_link, validate_chain_sequence
)
from ..transitions import (
    DecisionToGoalTransitionHandler, SetbackToReactiveTransitionHandler,
    TransitionOrchestrator, process_any_transition
)
from ..serialization import (
    ChainLinkImportExportManager, JSONChainLinkSerializer, YAMLChainLinkSerializer,
    CSVChainLinkSerializer, ChainSequenceSerializer, SerializationError
)
from ...models import (
    SceneCard, SceneType, ProactiveScene, ReactiveScene,
    GoalCriteria, ConflictObstacle, Outcome, DilemmaOption,
    OutcomeType, CompressionType, ViewpointType, TenseType
)


class TestChainLinkModels:
    """Test chain link data models"""
    
    def test_chain_link_creation(self):
        """Test basic chain link creation"""
        source_scene = SceneReference(
            scene_id="test_scene_1",
            scene_type=SceneType.PROACTIVE,
            pov_character="Hero"
        )
        
        chain_link = ChainLink(
            chain_id="test_chain_1",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            source_scene=source_scene,
            trigger_content="Character fails to achieve goal",
            target_seed="Character processes emotional impact of failure"
        )
        
        assert chain_link.chain_id == "test_chain_1"
        assert chain_link.chain_type == ChainLinkType.SETBACK_TO_REACTIVE
        assert chain_link.source_scene.pov_character == "Hero"
        assert chain_link.is_valid == True
    
    def test_chain_metadata_quality_calculation(self):
        """Test chain metadata quality score calculation"""
        metadata = ChainMetadata(
            validation_score=0.8,
            chain_strength=ChainStrength.STRONG,
            pov_consistency=True,
            time_consistency=True,
            emotional_continuity=0.9,
            narrative_necessity=0.8
        )
        
        quality = metadata.calculate_overall_quality()
        assert 0.7 <= quality <= 1.0  # Should be high quality
    
    def test_scene_reference_identifier(self):
        """Test scene reference identifier generation"""
        scene_ref = SceneReference(
            scene_id="scene_123",
            scene_type=SceneType.REACTIVE,
            pov_character="Protagonist"
        )
        
        identifier = scene_ref.to_identifier()
        assert "reactive" in identifier.lower()
        assert "protagonist" in identifier.lower()
        assert "scene_123" in identifier
    
    def test_chain_link_validation_logic(self):
        """Test chain link transition validation"""
        # Valid proactive → reactive transition
        proactive_source = SceneReference(
            scene_id="proactive_1",
            scene_type=SceneType.PROACTIVE,
            pov_character="Hero"
        )
        
        valid_chain = ChainLink(
            chain_id="valid_chain",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            source_scene=proactive_source,
            trigger_content="Setback occurs",
            target_seed="Emotional processing needed"
        )
        
        assert valid_chain.validate_transition_logic() == True
        
        # Invalid transition (proactive → decision-based)
        invalid_chain = ChainLink(
            chain_id="invalid_chain", 
            chain_type=ChainLinkType.DECISION_TO_PROACTIVE,  # Wrong for proactive source
            source_scene=proactive_source,
            trigger_content="Setback occurs",
            target_seed="Should be invalid"
        )
        
        assert invalid_chain.validate_transition_logic() == False


class TestChainLinkGenerator:
    """Test chain link generation logic"""
    
    @pytest.fixture
    def generator(self):
        return ChainLinkGenerator()
    
    @pytest.fixture
    def proactive_setback_scene(self):
        """Create proactive scene with setback outcome"""
        goal = GoalCriteria(
            text="Reach the safe house before midnight",
            fits_time=True,
            possible=True,
            difficult=True,
            fits_pov=True,
            concrete_objective=True
        )
        
        obstacles = [
            ConflictObstacle(try_number=1, obstacle="Security checkpoint"),
            ConflictObstacle(try_number=2, obstacle="Guard patrol appears")
        ]
        
        outcome = Outcome(
            type=OutcomeType.SETBACK,
            rationale="Captured by guards due to unexpected patrol timing"
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
            scene_crucible="Agent Smith faces capture at checkpoint now; mission hangs in balance.",
            place="Enemy compound gate",
            time="11:45 PM",
            proactive=proactive,
            exposition_used=["Checkpoint layout", "Time pressure context"],
            chain_link="setback→reactive processing needed"
        )
    
    @pytest.fixture
    def reactive_decision_scene(self):
        """Create reactive scene with decision"""
        dilemma_options = [
            DilemmaOption(option="Try to fight guards", why_bad="Outnumbered, will escalate"),
            DilemmaOption(option="Attempt negotiation", why_bad="Shows weakness, may fail"),
            DilemmaOption(option="Wait for rescue", why_bad="Rescue uncertain, time limited")
        ]
        
        reactive = ReactiveScene(
            reaction="Agent Smith feels trapped and desperate after capture, mind racing for solutions.",
            dilemma_options=dilemma_options,
            decision="Choose to attempt negotiation despite showing weakness, as it's the least risky option",
            next_goal_stub="Successfully negotiate release or create escape opportunity",
            compression=CompressionType.FULL
        )
        
        return SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Agent Smith",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Captured and handcuffed now, Agent Smith must choose quickly before interrogation begins.",
            place="Guard station",
            time="Just after capture",
            reactive=reactive,
            exposition_used=["Capture context for emotional state"],
            chain_link="negotiation decision→next proactive goal"
        )
    
    def test_proactive_setback_generation(self, generator, proactive_setback_scene):
        """Test generation of setback→reactive chain link"""
        context = ChainGenerationContext(
            emotional_intensity=0.8,
            narrative_tension=0.7,
            target_pacing="moderate"
        )
        
        chain_link = generator.generate_chain_link(proactive_setback_scene, context)
        
        assert chain_link is not None
        assert chain_link.chain_type == ChainLinkType.SETBACK_TO_REACTIVE
        assert chain_link.source_scene.scene_type == SceneType.PROACTIVE
        assert "capture" in chain_link.trigger_content.lower() or "guard" in chain_link.trigger_content.lower()
        assert len(chain_link.target_seed) > 10  # Substantial emotional trigger
        
        # Check metadata quality
        assert chain_link.metadata is not None
        assert chain_link.metadata.emotional_continuity > 0.5
    
    def test_reactive_decision_generation(self, generator, reactive_decision_scene):
        """Test generation of decision→proactive chain link"""
        context = ChainGenerationContext(
            narrative_tension=0.6,
            target_pacing="moderate"
        )
        
        chain_link = generator.generate_chain_link(reactive_decision_scene, context)
        
        assert chain_link is not None
        assert chain_link.chain_type == ChainLinkType.DECISION_TO_PROACTIVE
        assert chain_link.source_scene.scene_type == SceneType.REACTIVE
        assert "negotiat" in chain_link.trigger_content.lower()
        assert "negotiat" in chain_link.target_seed.lower() or "release" in chain_link.target_seed.lower()
        
        # Check metadata
        assert chain_link.metadata.narrative_necessity > 0.8  # Should be high for decision chains
    
    def test_generation_statistics(self, generator, proactive_setback_scene, reactive_decision_scene):
        """Test generation statistics tracking"""
        initial_stats = generator.get_generation_statistics()
        assert initial_stats["total_generated"] == 0
        
        # Generate some chain links
        generator.generate_chain_link(proactive_setback_scene)
        generator.generate_chain_link(reactive_decision_scene)
        
        stats = generator.get_generation_statistics()
        assert stats["total_generated"] == 2
        assert stats["setback_to_reactive"] == 1
        assert stats["decision_to_proactive"] == 1
    
    def test_context_awareness(self, generator, proactive_setback_scene):
        """Test that generator responds to context parameters"""
        # High intensity context
        high_intensity_context = ChainGenerationContext(
            emotional_intensity=0.9,
            target_pacing="fast"
        )
        
        chain_high = generator.generate_chain_link(proactive_setback_scene, high_intensity_context)
        
        # Low intensity context
        low_intensity_context = ChainGenerationContext(
            emotional_intensity=0.2,
            target_pacing="slow"
        )
        
        chain_low = generator.generate_chain_link(proactive_setback_scene, low_intensity_context)
        
        # Both should generate, but may have different transition types
        assert chain_high is not None
        assert chain_low is not None
        
        # High intensity might prefer immediate transitions
        # Low intensity might allow time cuts or sequel processing


class TestChainLinkValidator:
    """Test chain link validation"""
    
    @pytest.fixture
    def validator(self):
        return ChainLinkValidator()
    
    @pytest.fixture
    def valid_setback_chain(self):
        """Create valid setback chain link"""
        source = SceneReference(
            scene_id="proactive_1",
            scene_type=SceneType.PROACTIVE,
            pov_character="Hero"
        )
        
        return ChainLink(
            chain_id="valid_setback_chain",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            source_scene=source,
            trigger_content="Hero fails to complete mission due to unexpected enemy reinforcements",
            target_seed="Hero experiences crushing disappointment and must process the failure emotionally"
        )
    
    @pytest.fixture
    def invalid_chain_missing_fields(self):
        """Create invalid chain link missing required fields"""
        source = SceneReference(
            scene_id="scene_1",
            scene_type=SceneType.PROACTIVE, 
            pov_character="Hero"
        )
        
        return ChainLink(
            chain_id="",  # Invalid - missing chain ID
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            source_scene=source,
            trigger_content="",  # Invalid - missing trigger
            target_seed=""  # Invalid - missing seed
        )
    
    def test_valid_chain_validation(self, validator, valid_setback_chain):
        """Test validation of valid chain link"""
        result = validator.validate_chain_link(valid_setback_chain)
        
        assert result.is_valid == True
        assert result.chain_quality_score > 0.5
        assert len(result.validation_errors) == 0
    
    def test_invalid_chain_validation(self, validator, invalid_chain_missing_fields):
        """Test validation of invalid chain link"""
        result = validator.validate_chain_link(invalid_chain_missing_fields)
        
        assert result.is_valid == False
        assert result.chain_quality_score < 0.5
        assert len(result.validation_errors) > 0
        
        # Check for specific errors
        error_messages = [error for error in result.validation_errors]
        assert any("chain_id" in error.lower() for error in error_messages)
        assert any("trigger" in error.lower() for error in error_messages)
    
    def test_snowflake_compliance_validation(self, validator):
        """Test Snowflake Method compliance checking"""
        # Create proactive scene with wrong transition type
        proactive_source = SceneReference(
            scene_id="proactive_1",
            scene_type=SceneType.PROACTIVE,
            pov_character="Hero"
        )
        
        # Proactive scenes shouldn't use decision-to-proactive transitions
        invalid_transition = ChainLink(
            chain_id="invalid_transition",
            chain_type=ChainLinkType.DECISION_TO_PROACTIVE,  # Wrong for proactive source
            source_scene=proactive_source,
            trigger_content="Some trigger",
            target_seed="Some seed"
        )
        
        result = validator.validate_chain_link(invalid_transition)
        
        assert result.is_valid == False
        assert any("proactive" in error.lower() and "transition" in error.lower() 
                  for error in result.validation_errors)
    
    def test_content_quality_validation(self, validator):
        """Test content quality validation"""
        source = SceneReference(
            scene_id="scene_1",
            scene_type=SceneType.PROACTIVE,
            pov_character="Hero"
        )
        
        # Create chain with poor content quality
        poor_content_chain = ChainLink(
            chain_id="poor_content",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            source_scene=source,
            trigger_content="Bad",  # Too short
            target_seed="Sad"  # Too short
        )
        
        result = validator.validate_chain_link(poor_content_chain)
        
        # Should have warnings about content quality
        assert len(result.validation_warnings) > 0 or len(result.validation_errors) > 0
    
    def test_validator_statistics(self, validator, valid_setback_chain, invalid_chain_missing_fields):
        """Test validator statistics tracking"""
        initial_stats = validator.get_validation_statistics()
        assert initial_stats["total_validated"] == 0
        
        # Validate some chains
        validator.validate_chain_link(valid_setback_chain)
        validator.validate_chain_link(invalid_chain_missing_fields)
        
        stats = validator.get_validation_statistics()
        assert stats["total_validated"] == 2
        assert stats["valid_links"] == 1  # Only one was valid
        assert stats["success_rate"] == 50.0


class TestSpecializedTransitions:
    """Test specialized transition handlers"""
    
    @pytest.fixture
    def decision_handler(self):
        return DecisionToGoalTransitionHandler()
    
    @pytest.fixture
    def setback_handler(self):
        return SetbackToReactiveTransitionHandler()
    
    @pytest.fixture
    def orchestrator(self):
        return TransitionOrchestrator()
    
    @pytest.fixture
    def reactive_scene_with_decision(self):
        """Create reactive scene for decision→goal testing"""
        dilemma = [
            DilemmaOption(option="Fight", why_bad="Dangerous"),
            DilemmaOption(option="Run", why_bad="Abandons mission")
        ]
        
        reactive = ReactiveScene(
            reaction="Character feels angry and frustrated",
            dilemma_options=dilemma,
            decision="Choose to fight despite the danger because mission is critical",
            next_goal_stub="Defeat the enemy and complete the mission",
            compression=CompressionType.FULL
        )
        
        return SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Hero",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Hero must decide now",
            place="Battlefield",
            time="Critical moment",
            reactive=reactive
        )
    
    def test_decision_to_goal_handler(self, decision_handler, reactive_scene_with_decision):
        """Test decision→goal transition handler"""
        assert decision_handler.can_handle(reactive_scene_with_decision) == True
        
        analysis = decision_handler.analyze_transition(reactive_scene_with_decision)
        assert analysis.transition_type == ChainLinkType.DECISION_TO_PROACTIVE
        assert analysis.source_scene_type == SceneType.REACTIVE
        
        content = decision_handler.generate_target_content(reactive_scene_with_decision, analysis)
        assert "goal_text" in content
        assert "goal_criteria" in content
        assert "potential_obstacles" in content
        
        # Goal should be actionable
        goal_text = content["goal_text"]
        assert len(goal_text) > 10
        assert "fight" in goal_text.lower() or "defeat" in goal_text.lower()
    
    def test_setback_to_reactive_handler(self, setback_handler):
        """Test setback→reactive transition handler"""
        # Create proactive scene with setback
        goal = GoalCriteria(
            text="Complete the mission",
            fits_time=True, possible=True, difficult=True,
            fits_pov=True, concrete_objective=True
        )
        
        outcome = Outcome(
            type=OutcomeType.SETBACK,
            rationale="Mission failed due to betrayal by trusted ally"
        )
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=[ConflictObstacle(try_number=1, obstacle="Enemy resistance")],
            outcome=outcome
        )
        
        setback_scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Hero",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Hero faces betrayal now",
            place="Mission site",
            time="Critical moment",
            proactive=proactive
        )
        
        assert setback_handler.can_handle(setback_scene) == True
        
        analysis = setback_handler.analyze_transition(setback_scene)
        assert analysis.transition_type == ChainLinkType.SETBACK_TO_REACTIVE
        assert analysis.extracted_elements["setback_type"] == "betrayal"
        
        content = setback_handler.generate_target_content(setback_scene, analysis)
        assert "reaction_content" in content
        assert "dilemma_options" in content
        assert "next_goal_seed" in content
        
        # Reaction should be emotional
        reaction = content["reaction_content"]
        assert len(reaction) > 20
        assert "betray" in reaction.lower() or "anger" in reaction.lower()
    
    def test_transition_orchestrator(self, orchestrator, reactive_scene_with_decision):
        """Test transition orchestrator"""
        result = orchestrator.process_transition(reactive_scene_with_decision)
        
        assert result is not None
        assert "handler_type" in result
        assert "analysis" in result
        assert "generated_content" in result
        assert "DecisionToGoalTransitionHandler" in result["handler_type"]
        
        stats = orchestrator.get_transition_statistics()
        assert stats["total_transitions"] == 1
        assert stats["decision_to_goal"] == 1


class TestChainSequences:
    """Test chain sequence validation and operations"""
    
    @pytest.fixture
    def sequence_validator(self):
        return ChainSequenceValidator()
    
    @pytest.fixture
    def valid_chain_sequence(self):
        """Create valid chain sequence"""
        # Create scenes
        scenes = [
            SceneReference(
                scene_id="scene_1",
                scene_type=SceneType.PROACTIVE,
                pov_character="Hero",
                word_count=800
            ),
            SceneReference(
                scene_id="scene_2", 
                scene_type=SceneType.REACTIVE,
                pov_character="Hero",
                word_count=600
            ),
            SceneReference(
                scene_id="scene_3",
                scene_type=SceneType.PROACTIVE,
                pov_character="Hero", 
                word_count=900
            )
        ]
        
        # Create chain links
        chain_links = [
            ChainLink(
                chain_id="link_1_2",
                chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
                source_scene=scenes[0],
                trigger_content="Hero fails in first attempt",
                target_seed="Hero processes the failure emotionally"
            ),
            ChainLink(
                chain_id="link_2_3",
                chain_type=ChainLinkType.DECISION_TO_PROACTIVE,
                source_scene=scenes[1],
                trigger_content="Hero decides to try different approach",
                target_seed="Hero attempts new strategy to achieve goal"
            )
        ]
        
        return ChainSequence(
            sequence_id="test_sequence",
            title="Test Scene Sequence",
            scenes=scenes,
            chain_links=chain_links,
            dominant_pov="Hero"
        )
    
    def test_valid_sequence_validation(self, sequence_validator, valid_chain_sequence):
        """Test validation of valid chain sequence"""
        result = sequence_validator.validate_chain_sequence(valid_chain_sequence)
        
        assert result.is_valid == True
        assert result.chain_quality_score > 0.5
        assert len(result.validation_errors) == 0
    
    def test_sequence_structure_validation(self, sequence_validator):
        """Test sequence structure validation"""
        # Create sequence with mismatched scenes/links
        scenes = [
            SceneReference(scene_id="scene_1", scene_type=SceneType.PROACTIVE, pov_character="Hero"),
            SceneReference(scene_id="scene_2", scene_type=SceneType.REACTIVE, pov_character="Hero"),
            SceneReference(scene_id="scene_3", scene_type=SceneType.PROACTIVE, pov_character="Hero")
        ]
        
        # Only one chain link for 3 scenes (should have 2)
        chain_links = [
            ChainLink(
                chain_id="link_1",
                chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
                source_scene=scenes[0],
                trigger_content="Test trigger",
                target_seed="Test seed"
            )
        ]
        
        invalid_sequence = ChainSequence(
            sequence_id="invalid_seq",
            scenes=scenes,
            chain_links=chain_links
        )
        
        result = sequence_validator.validate_chain_sequence(invalid_sequence)
        
        assert result.is_valid == False
        assert any("mismatch" in error.lower() for error in result.validation_errors)
    
    def test_sequence_alternation_validation(self, sequence_validator):
        """Test scene alternation validation"""
        # Create sequence with poor alternation (all proactive)
        scenes = [
            SceneReference(scene_id=f"scene_{i}", scene_type=SceneType.PROACTIVE, pov_character="Hero")
            for i in range(5)
        ]
        
        chain_links = [
            ChainLink(
                chain_id=f"link_{i}",
                chain_type=ChainLinkType.VICTORY_TO_PROACTIVE,
                source_scene=scenes[i],
                trigger_content="Victory leads to next challenge",
                target_seed="New proactive goal"
            )
            for i in range(4)
        ]
        
        poor_alternation_sequence = ChainSequence(
            sequence_id="poor_alternation",
            scenes=scenes,
            chain_links=chain_links
        )
        
        result = sequence_validator.validate_chain_sequence(poor_alternation_sequence)
        
        # Should have warnings about poor alternation
        assert len(result.validation_warnings) > 0
        assert any("alternation" in warning.lower() for warning in result.validation_warnings)
    
    def test_sequence_word_count_calculation(self, valid_chain_sequence):
        """Test sequence word count calculation"""
        total = valid_chain_sequence.calculate_total_word_count()
        
        # Should include scene word counts plus bridging estimates
        expected_scene_words = 800 + 600 + 900  # From fixture
        assert total >= expected_scene_words
        assert total <= expected_scene_words + 500  # Plus reasonable bridging
    
    def test_sequence_integrity_validation(self, valid_chain_sequence):
        """Test sequence integrity validation"""
        result = valid_chain_sequence.validate_sequence_integrity()
        
        assert isinstance(result, ChainValidationResult)
        assert result.is_valid == True
        assert result.chain_quality_score > 0.0


class TestSerialization:
    """Test import/export functionality"""
    
    @pytest.fixture
    def sample_chain_link(self):
        """Create sample chain link for testing"""
        source = SceneReference(
            scene_id="test_scene",
            scene_type=SceneType.PROACTIVE,
            pov_character="TestHero"
        )
        
        return ChainLink(
            chain_id="test_chain_123",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            source_scene=source,
            trigger_content="Test setback triggers emotional processing",
            target_seed="Character must process this setback emotionally",
            bridging_content="Brief transition between scenes"
        )
    
    @pytest.fixture
    def import_export_manager(self):
        return ChainLinkImportExportManager()
    
    def test_json_serialization(self, sample_chain_link):
        """Test JSON serialization/deserialization"""
        serializer = JSONChainLinkSerializer()
        
        # Serialize
        json_data = serializer.serialize(sample_chain_link)
        assert isinstance(json_data, str)
        assert "test_chain_123" in json_data
        
        # Deserialize
        restored_link = serializer.deserialize(json_data)
        assert restored_link.chain_id == sample_chain_link.chain_id
        assert restored_link.chain_type == sample_chain_link.chain_type
        assert restored_link.source_scene.pov_character == sample_chain_link.source_scene.pov_character
    
    def test_csv_serialization(self, sample_chain_link):
        """Test CSV serialization/deserialization"""
        serializer = CSVChainLinkSerializer()
        
        # Serialize
        csv_data = serializer.serialize(sample_chain_link)
        assert isinstance(csv_data, str)
        assert "test_chain_123" in csv_data
        
        # Deserialize
        restored_link = serializer.deserialize(csv_data)
        assert restored_link.chain_id == sample_chain_link.chain_id
        assert restored_link.chain_type == sample_chain_link.chain_type
    
    def test_file_import_export(self, import_export_manager, sample_chain_link):
        """Test file import/export operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export to JSON file
            json_path = Path(temp_dir) / "test_chain.json"
            success = import_export_manager.export_chain_link(sample_chain_link, json_path)
            assert success == True
            assert json_path.exists()
            
            # Import from JSON file
            imported_link = import_export_manager.import_chain_link(json_path)
            assert imported_link.chain_id == sample_chain_link.chain_id
    
    def test_batch_operations(self, import_export_manager):
        """Test batch import/export operations"""
        # Create multiple chain links
        chain_links = []
        for i in range(3):
            source = SceneReference(
                scene_id=f"scene_{i}",
                scene_type=SceneType.PROACTIVE,
                pov_character="Hero"
            )
            
            link = ChainLink(
                chain_id=f"chain_{i}",
                chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
                source_scene=source,
                trigger_content=f"Trigger {i}",
                target_seed=f"Seed {i}"
            )
            chain_links.append(link)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Batch export
            exported_files = import_export_manager.export_chain_links_batch(
                chain_links, temp_dir, 'json'
            )
            assert len(exported_files) == 3
            
            # Batch import
            imported_links = import_export_manager.import_chain_links_batch(temp_dir, 'json')
            assert len(imported_links) == 3
            
            # Check IDs match
            imported_ids = {link.chain_id for link in imported_links}
            original_ids = {link.chain_id for link in chain_links}
            assert imported_ids == original_ids
    
    def test_csv_table_operations(self, import_export_manager):
        """Test CSV table import/export"""
        # Create chain links
        chain_links = []
        for i in range(2):
            source = SceneReference(
                scene_id=f"scene_{i}",
                scene_type=SceneType.PROACTIVE,
                pov_character="Hero"
            )
            
            link = ChainLink(
                chain_id=f"csv_chain_{i}",
                chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
                source_scene=source,
                trigger_content=f"CSV Trigger {i}",
                target_seed=f"CSV Seed {i}"
            )
            chain_links.append(link)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "chains.csv"
            
            # Export to CSV table
            success = import_export_manager.export_to_csv_table(chain_links, csv_path)
            assert success == True
            assert csv_path.exists()
            
            # Import from CSV table
            imported_links = import_export_manager.import_from_csv_table(csv_path)
            assert len(imported_links) == 2
    
    def test_import_export_statistics(self, import_export_manager, sample_chain_link):
        """Test statistics tracking for import/export operations"""
        initial_stats = import_export_manager.get_export_statistics()
        assert initial_stats["total_exports"] == 0
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Perform some operations
            json_path = Path(temp_dir) / "stats_test.json"
            import_export_manager.export_chain_link(sample_chain_link, json_path)
            import_export_manager.import_chain_link(json_path)
            
            export_stats = import_export_manager.get_export_statistics()
            import_stats = import_export_manager.get_import_statistics()
            
            assert export_stats["total_exports"] == 1
            assert export_stats["successful_exports"] == 1
            assert import_stats["total_imports"] == 1
            assert import_stats["successful_imports"] == 1


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows"""
    
    def test_complete_chain_generation_workflow(self):
        """Test complete workflow from scene to validated chain"""
        # Create source scene
        goal = GoalCriteria(
            text="Infiltrate enemy base and retrieve intel",
            fits_time=True, possible=True, difficult=True,
            fits_pov=True, concrete_objective=True
        )
        
        outcome = Outcome(
            type=OutcomeType.SETBACK,
            rationale="Discovered by security cameras, must escape quickly"
        )
        
        proactive = ProactiveScene(
            goal=goal,
            conflict_obstacles=[
                ConflictObstacle(try_number=1, obstacle="Laser security grid"),
                ConflictObstacle(try_number=2, obstacle="Motion sensors activate")
            ],
            outcome=outcome
        )
        
        source_scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Agent Alpha",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Agent Alpha faces immediate discovery now; one wrong move means mission failure.",
            place="Enemy command center",
            time="2:30 AM",
            proactive=proactive
        )
        
        # Generate chain link
        generator = ChainLinkGenerator()
        chain_link = generator.generate_chain_link(source_scene)
        
        assert chain_link is not None
        assert chain_link.chain_type == ChainLinkType.SETBACK_TO_REACTIVE
        
        # Validate chain link
        validator = ChainLinkValidator()
        result = validator.validate_chain_link(chain_link, source_scene)
        
        assert result.is_valid == True
        assert result.chain_quality_score > 0.5
        
        # Export and import
        manager = ChainLinkImportExportManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "integration_test.json"
            
            # Export
            export_success = manager.export_chain_link(chain_link, file_path)
            assert export_success == True
            
            # Import
            imported_link = manager.import_chain_link(file_path)
            assert imported_link.chain_id == chain_link.chain_id
    
    def test_sequence_creation_and_validation_workflow(self):
        """Test creating and validating complete sequences"""
        # Create multiple scenes
        scenes = []
        scene_cards = []
        
        # Scene 1: Proactive
        proactive_scene = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov="Hero",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Hero attempts dangerous mission now",
            place="Enemy territory",
            time="Dawn",
            proactive=ProactiveScene(
                goal=GoalCriteria(
                    text="Complete mission", fits_time=True, possible=True,
                    difficult=True, fits_pov=True, concrete_objective=True
                ),
                conflict_obstacles=[ConflictObstacle(try_number=1, obstacle="Enemy patrol")],
                outcome=Outcome(type=OutcomeType.SETBACK, rationale="Mission fails due to betrayal")
            )
        )
        
        # Scene 2: Reactive  
        reactive_scene = SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Hero",
            viewpoint=ViewpointType.THIRD,
            tense=TenseType.PAST,
            scene_crucible="Hero processes betrayal now",
            place="Safe house",
            time="After escape",
            reactive=ReactiveScene(
                reaction="Hero feels betrayed and angry",
                dilemma_options=[
                    DilemmaOption(option="Seek revenge", why_bad="Dangerous escalation"),
                    DilemmaOption(option="Report betrayal", why_bad="May not be believed")
                ],
                decision="Choose to gather evidence before acting",
                next_goal_stub="Gather proof of betrayal",
                compression=CompressionType.FULL
            )
        )
        
        scene_cards = [proactive_scene, reactive_scene]
        
        # Generate chain links
        chain_links = generate_chain_sequence(scene_cards)
        
        assert len(chain_links) == 1  # One link between two scenes
        assert chain_links[0].chain_type == ChainLinkType.SETBACK_TO_REACTIVE
        
        # Create scene references
        scenes = [
            SceneReference(
                scene_id=f"workflow_scene_{i}",
                scene_type=scene.scene_type,
                pov_character=scene.pov,
                word_count=800
            )
            for i, scene in enumerate(scene_cards)
        ]
        
        # Create sequence
        sequence = ChainSequence(
            sequence_id="workflow_test_sequence",
            title="Integration Test Sequence",
            scenes=scenes,
            chain_links=chain_links
        )
        
        # Validate sequence
        validator = ChainSequenceValidator()
        result = validator.validate_chain_sequence(sequence, scene_cards)
        
        assert result.is_valid == True
        assert result.chain_quality_score > 0.4  # Should be decent quality
    
    def test_specialized_transition_integration(self):
        """Test specialized transitions with orchestrator"""
        # Create reactive scene with complex decision
        reactive_scene = SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Detective",
            viewpoint=ViewpointType.FIRST,
            tense=TenseType.PRESENT,
            scene_crucible="I must decide now how to handle this evidence",
            place="Police station",
            time="Late night",
            reactive=ReactiveScene(
                reaction="I feel torn between duty and personal loyalty after discovering my partner's involvement",
                dilemma_options=[
                    DilemmaOption(
                        option="Report partner immediately", 
                        why_bad="Destroys friendship and may ruin innocent person"
                    ),
                    DilemmaOption(
                        option="Confront partner privately",
                        why_bad="Gives them chance to destroy evidence or flee"
                    ),
                    DilemmaOption(
                        option="Investigate further alone",
                        why_bad="Delays justice and risks tampering with case"
                    )
                ],
                decision="Choose to confront partner privately despite the risk because friendship demands giving them a chance to explain",
                next_goal_stub="Confront partner and demand truth about their involvement",
                compression=CompressionType.FULL
            )
        )
        
        # Use orchestrator to process transition
        orchestrator = TransitionOrchestrator()
        result = orchestrator.process_transition(reactive_scene)
        
        assert result is not None
        assert "DecisionToGoalTransitionHandler" in result["handler_type"]
        
        # Check generated content
        content = result["generated_content"]
        assert "goal_text" in content
        assert "confront" in content["goal_text"].lower()
        assert "partner" in content["goal_text"].lower()
        
        # Check analysis
        analysis = result["analysis"]
        assert analysis.emotional_intensity in ["low", "medium", "high"]
        assert analysis.content_complexity in ["simple", "moderate", "complex"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])