"""
Comprehensive Tests for Scene Drafting Service

TaskMaster Task 44.6: Write Tests for Structure Adherence and Output Quality
Tests prose generation with example Scene Cards, verifies structure adherence,
checks POV/tense consistency, and validates exposition limits.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from ..service import SceneDraftingService, DraftingRequest, DraftingResponse, DraftingStatus
from ..prose_generators import ProactiveProseGenerator, ReactiveProseGenerator
from ..pov_handler import POVHandler, POVType, TenseType
from ..exposition_tracker import ExpositionTracker, ExpositionBudget, ExpositionType
from ...models import SceneCard, SceneType


class TestSceneDraftingService(unittest.TestCase):
    """
    TaskMaster Task 44.6: Tests for Structure Adherence and Output Quality
    
    Test prose generation with example Scene Cards from PRD.
    Verify structure adherence for G-C-S/V and R-D-D patterns.
    Check POV/tense consistency throughout generated prose.
    Validate exposition limits and budget enforcement.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.drafting_service = SceneDraftingService()
        
        # Create sample proactive scene card
        self.proactive_scene = self._create_sample_proactive_scene()
        
        # Create sample reactive scene card  
        self.reactive_scene = self._create_sample_reactive_scene()
        
    def _create_sample_proactive_scene(self) -> SceneCard:
        """Create sample proactive scene card for testing"""
        
        # Mock proactive structure
        proactive_mock = Mock()
        proactive_mock.goal = "find the missing research data before the deadline"
        proactive_mock.conflict = "the security system locks down the building"
        proactive_mock.setback = "the data has been corrupted and is unreadable"
        
        scene_card = Mock(spec=SceneCard)
        scene_card.scene_id = "test_proactive_001"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = "Dr. Sarah Chen"
        scene_card.pov = "third_limited"
        scene_card.tense = "past"
        scene_card.scene_crucible = "the race to save the research project"
        scene_card.setting = "the university research lab"
        scene_card.proactive = proactive_mock
        
        return scene_card
    
    def _create_sample_reactive_scene(self) -> SceneCard:
        """Create sample reactive scene card for testing"""
        
        # Mock reactive structure
        reactive_mock = Mock()
        reactive_mock.reaction = "overwhelming guilt and shame at the failure"
        reactive_mock.dilemma = "confess the mistake and lose everything or cover it up and live with the lie"
        reactive_mock.decision = "confess to the department head despite the consequences"
        
        scene_card = Mock(spec=SceneCard)
        scene_card.scene_id = "test_reactive_001"
        scene_card.scene_type = SceneType.REACTIVE
        scene_card.pov_character = "Dr. Sarah Chen"
        scene_card.pov = "first"
        scene_card.tense = "present"
        scene_card.scene_crucible = "facing the aftermath of professional failure"
        scene_card.setting = "the empty research lab"
        scene_card.reactive = reactive_mock
        
        return scene_card
    
    def test_proactive_scene_drafting_basic(self):
        """Test basic proactive scene prose generation"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,
            target_word_count=400,
            maintain_scene_crucible_focus=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        # Basic success checks
        self.assertTrue(response.success)
        self.assertEqual(response.status, DraftingStatus.SUCCESS)
        self.assertIsNotNone(response.prose_content)
        self.assertGreater(response.word_count, 0)
        self.assertEqual(response.generator_used, "ProactiveProseGenerator")
        
        # Word count should be reasonable
        self.assertGreater(response.word_count, 200)  # Minimum substantial content
        self.assertLess(response.word_count, 1000)    # Not excessively long
    
    def test_reactive_scene_drafting_basic(self):
        """Test basic reactive scene prose generation"""
        
        request = DraftingRequest(
            scene_card=self.reactive_scene,
            target_word_count=400,
            maintain_scene_crucible_focus=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        # Basic success checks
        self.assertTrue(response.success)
        self.assertEqual(response.status, DraftingStatus.SUCCESS)
        self.assertIsNotNone(response.prose_content)
        self.assertGreater(response.word_count, 0)
        self.assertEqual(response.generator_used, "ReactiveProseGenerator")
        
        # Word count should be reasonable
        self.assertGreater(response.word_count, 200)
        self.assertLess(response.word_count, 1000)
    
    def test_proactive_structure_adherence(self):
        """Test that proactive scenes follow G-C-S/V structure"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,
            validate_structure_adherence=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        
        # Check structure adherence results
        self.assertIn('goal_present', response.structure_adherence)
        self.assertIn('conflict_present', response.structure_adherence)
        self.assertIn('setback_present', response.structure_adherence)
        
        # Goal should be present in prose
        goal_keywords = ["find", "research", "data", "deadline"]
        prose_lower = response.prose_content.lower()
        goal_found = any(keyword in prose_lower for keyword in goal_keywords)
        self.assertTrue(goal_found, "Goal keywords not found in prose")
        
        # Conflict should be present
        conflict_keywords = ["security", "system", "locks", "building"]
        conflict_found = any(keyword in prose_lower for keyword in conflict_keywords)
        self.assertTrue(conflict_found, "Conflict keywords not found in prose")
        
        # Setback should be present
        setback_keywords = ["data", "corrupted", "unreadable"]
        setback_found = any(keyword in prose_lower for keyword in setback_keywords)
        self.assertTrue(setback_found, "Setback keywords not found in prose")
    
    def test_reactive_structure_adherence(self):
        """Test that reactive scenes follow R-D-D structure"""
        
        request = DraftingRequest(
            scene_card=self.reactive_scene,
            validate_structure_adherence=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        
        # Check structure adherence results
        self.assertIn('reaction_present', response.structure_adherence)
        self.assertIn('dilemma_present', response.structure_adherence)
        self.assertIn('decision_present', response.structure_adherence)
        
        prose_lower = response.prose_content.lower()
        
        # Reaction should be present
        reaction_keywords = ["guilt", "shame", "failure"]
        reaction_found = any(keyword in prose_lower for keyword in reaction_keywords)
        self.assertTrue(reaction_found, "Reaction keywords not found in prose")
        
        # Dilemma should be present
        dilemma_keywords = ["confess", "cover", "lie"]
        dilemma_found = any(keyword in prose_lower for keyword in dilemma_keywords)
        self.assertTrue(dilemma_found, "Dilemma keywords not found in prose")
        
        # Decision should be present
        decision_keywords = ["confess", "department", "consequences"]
        decision_found = any(keyword in prose_lower for keyword in decision_keywords)
        self.assertTrue(decision_found, "Decision keywords not found in prose")
    
    def test_pov_consistency_third_person(self):
        """Test POV consistency for third person scenes"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,  # Third limited POV
            validate_pov_consistency=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        self.assertTrue(response.pov_consistency, "POV consistency check failed")
        
        # Check for proper third person usage
        prose_lower = response.prose_content.lower()
        self.assertIn("she ", prose_lower)  # Third person pronouns should be present
        self.assertNotIn(" i ", prose_lower)  # First person should not be present
        self.assertNotIn(" my ", prose_lower)
    
    def test_pov_consistency_first_person(self):
        """Test POV consistency for first person scenes"""
        
        request = DraftingRequest(
            scene_card=self.reactive_scene,  # First person POV
            validate_pov_consistency=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        self.assertTrue(response.pov_consistency, "POV consistency check failed")
        
        # Check for proper first person usage
        prose_lower = response.prose_content.lower()
        self.assertIn(" i ", prose_lower)  # First person pronouns should be present
        self.assertIn(" my ", prose_lower)
    
    def test_tense_consistency_past(self):
        """Test tense consistency for past tense scenes"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,  # Past tense
            validate_pov_consistency=True  # This also validates tense
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        self.assertTrue(response.tense_consistency, "Tense consistency check failed")
        
        # Check for past tense verbs
        prose_lower = response.prose_content.lower()
        past_tense_indicators = ["was", "were", "had", "found"]
        past_found = any(indicator in prose_lower for indicator in past_tense_indicators)
        self.assertTrue(past_found, "Past tense indicators not found")
    
    def test_tense_consistency_present(self):
        """Test tense consistency for present tense scenes"""
        
        request = DraftingRequest(
            scene_card=self.reactive_scene,  # Present tense
            validate_pov_consistency=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        self.assertTrue(response.tense_consistency, "Tense consistency check failed")
        
        # Check for present tense verbs
        prose_lower = response.prose_content.lower()
        present_tense_indicators = ["am", "is", "are", "feel", "see"]
        present_found = any(indicator in prose_lower for indicator in present_tense_indicators)
        self.assertTrue(present_found, "Present tense indicators not found")
    
    def test_exposition_budget_tracking(self):
        """Test exposition budget tracking and limits"""
        
        budget = ExpositionBudget(
            max_exposition_percentage=0.1,  # Very strict 10% limit
            max_backstory_sentences=1,
            max_world_building_sentences=1,
            strict_enforcement=True
        )
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,
            exposition_budget=budget,
            strict_exposition_enforcement=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        # Should still succeed but may have warnings
        self.assertTrue(response.success)
        
        # Check exposition tracking
        self.assertIsNotNone(response.exposition_usage)
        self.assertIn('total_exposition_words', response.exposition_usage)
        self.assertIn('exposition_percentage', response.exposition_usage)
        self.assertIn('usage_by_type', response.exposition_usage)
        
        # Exposition percentage should be calculated
        exp_percentage = response.exposition_usage.get('exposition_percentage', 0)
        self.assertGreaterEqual(exp_percentage, 0)
        self.assertLessEqual(exp_percentage, 100)
    
    def test_scene_crucible_maintenance(self):
        """Test that scene crucible focus is maintained"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,
            maintain_scene_crucible_focus=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        
        # Scene crucible maintenance score should be calculated
        self.assertGreaterEqual(response.scene_crucible_maintenance, 0.0)
        self.assertLessEqual(response.scene_crucible_maintenance, 1.0)
        
        # Crucible keywords should appear in prose
        crucible = self.proactive_scene.scene_crucible.lower()
        prose_lower = response.prose_content.lower()
        
        # At least some crucible keywords should be present
        crucible_keywords = crucible.split()[:3]  # Take first 3 words
        crucible_found = any(keyword in prose_lower for keyword in crucible_keywords)
        self.assertTrue(crucible_found, f"Scene crucible keywords {crucible_keywords} not found in prose")
    
    def test_dialogue_percentage_target(self):
        """Test dialogue percentage targeting"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,
            dialogue_percentage_target=0.4  # 40% dialogue target
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        
        # Dialogue percentage should be calculated
        self.assertGreaterEqual(response.dialogue_percentage, 0.0)
        self.assertLessEqual(response.dialogue_percentage, 1.0)
        
        # With a high dialogue target, should contain some dialogue
        if response.dialogue_percentage > 0.1:  # If any significant dialogue
            self.assertIn('"', response.prose_content, "Dialogue markers not found despite dialogue target")
    
    def test_sensory_details_inclusion(self):
        """Test sensory details inclusion"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,
            include_sensory_details=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        
        # Sensory detail score should be calculated
        self.assertGreaterEqual(response.sensory_detail_score, 0.0)
        self.assertLessEqual(response.sensory_detail_score, 1.0)
        
        # Should contain some sensory words
        prose_lower = response.prose_content.lower()
        sensory_words = ['saw', 'heard', 'felt', 'seemed', 'looked', 'sounded']
        sensory_found = any(word in prose_lower for word in sensory_words)
        self.assertTrue(sensory_found, "No sensory details found despite inclusion request")
    
    def test_invalid_scene_card_handling(self):
        """Test handling of invalid Scene Cards"""
        
        # Scene card missing proactive structure
        invalid_scene = Mock(spec=SceneCard)
        invalid_scene.scene_id = "invalid_001"
        invalid_scene.scene_type = SceneType.PROACTIVE
        invalid_scene.scene_crucible = "test crucible"
        invalid_scene.proactive = None  # Missing proactive structure
        
        request = DraftingRequest(scene_card=invalid_scene)
        
        response = self.drafting_service.draft_scene_prose(request)
        
        # Should fail gracefully
        self.assertFalse(response.success)
        self.assertEqual(response.status, DraftingStatus.FAILED)
        self.assertIsNotNone(response.error_message)
        self.assertIn("proactive structure", response.error_message.lower())
    
    def test_missing_scene_crucible(self):
        """Test handling of Scene Card missing scene crucible"""
        
        invalid_scene = Mock(spec=SceneCard)
        invalid_scene.scene_id = "invalid_002"
        invalid_scene.scene_type = SceneType.PROACTIVE
        invalid_scene.scene_crucible = None  # Missing crucible
        
        request = DraftingRequest(scene_card=invalid_scene)
        
        response = self.drafting_service.draft_scene_prose(request)
        
        # Should fail gracefully
        self.assertFalse(response.success)
        self.assertIn("scene_crucible", response.error_message.lower())
    
    def test_statistics_tracking(self):
        """Test drafting statistics tracking"""
        
        # Generate a few scenes
        for i in range(3):
            request = DraftingRequest(scene_card=self.proactive_scene)
            self.drafting_service.draft_scene_prose(request)
        
        stats = self.drafting_service.get_drafting_statistics()
        
        # Should have statistics
        self.assertIn('total_drafts', stats)
        self.assertIn('successful_drafts', stats)
        self.assertIn('success_rate', stats)
        self.assertIn('average_word_count', stats)
        self.assertIn('average_processing_time', stats)
        self.assertIn('generators_used', stats)
        
        # Should show 3 drafts
        self.assertEqual(stats['total_drafts'], 3)
        self.assertEqual(stats['successful_drafts'], 3)
        self.assertEqual(stats['success_rate'], 1.0)
        self.assertGreater(stats['average_word_count'], 0)
    
    def test_pov_tense_overrides(self):
        """Test POV and tense override functionality"""
        
        request = DraftingRequest(
            scene_card=self.proactive_scene,  # Default: third_limited, past
            pov_override=POVType.FIRST_PERSON,
            tense_override=TenseType.PRESENT,
            validate_pov_consistency=True
        )
        
        response = self.drafting_service.draft_scene_prose(request)
        
        self.assertTrue(response.success)
        
        # Should use overridden POV/tense
        prose_lower = response.prose_content.lower()
        self.assertIn(" i ", prose_lower)  # First person from override
        
        # Should have good consistency with overrides
        self.assertTrue(response.pov_consistency)
        self.assertTrue(response.tense_consistency)


class TestProseGenerators(unittest.TestCase):
    """Test prose generators individually"""
    
    def setUp(self):
        self.proactive_generator = ProactiveProseGenerator()
        self.reactive_generator = ReactiveProseGenerator()
        self.exposition_tracker = ExpositionTracker()
        
        # Sample scene cards
        self.proactive_scene = self._create_sample_proactive_scene()
        self.reactive_scene = self._create_sample_reactive_scene()
    
    def _create_sample_proactive_scene(self):
        """Create sample proactive scene for testing"""
        proactive_mock = Mock()
        proactive_mock.goal = "escape from the locked building"
        proactive_mock.conflict = "the security system is armed"
        proactive_mock.setback = "the backup power fails"
        
        scene_card = Mock()
        scene_card.scene_id = "gen_test_001"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = "Alex"
        scene_card.scene_crucible = "trapped in the office building"
        scene_card.proactive = proactive_mock
        return scene_card
    
    def _create_sample_reactive_scene(self):
        """Create sample reactive scene for testing"""
        reactive_mock = Mock()
        reactive_mock.reaction = "panic and fear"
        reactive_mock.dilemma = "call for help or try to escape alone"
        reactive_mock.decision = "call the emergency number despite the risk"
        
        scene_card = Mock()
        scene_card.scene_id = "gen_test_002"
        scene_card.scene_type = SceneType.REACTIVE
        scene_card.pov_character = "Alex"
        scene_card.scene_crucible = "dealing with the aftermath of being trapped"
        scene_card.reactive = reactive_mock
        return scene_card
    
    def test_proactive_prose_generation(self):
        """Test proactive prose generator"""
        
        prose = self.proactive_generator.generate_prose(
            scene_card=self.proactive_scene,
            pov_type=POVType.THIRD_LIMITED,
            tense_type=TenseType.PAST,
            exposition_tracker=self.exposition_tracker,
            target_word_count=300
        )
        
        self.assertIsNotNone(prose)
        self.assertGreater(len(prose), 100)  # Substantial content
        
        # Should contain G-C-S elements
        prose_lower = prose.lower()
        self.assertTrue(any(word in prose_lower for word in ["escape", "building"]))  # Goal
        self.assertTrue(any(word in prose_lower for word in ["security", "system"]))  # Conflict
        self.assertTrue(any(word in prose_lower for word in ["power", "fails"]))     # Setback
    
    def test_reactive_prose_generation(self):
        """Test reactive prose generator"""
        
        prose = self.reactive_generator.generate_prose(
            scene_card=self.reactive_scene,
            pov_type=POVType.FIRST_PERSON,
            tense_type=TenseType.PRESENT,
            exposition_tracker=self.exposition_tracker,
            target_word_count=300
        )
        
        self.assertIsNotNone(prose)
        self.assertGreater(len(prose), 100)
        
        # Should contain R-D-D elements
        prose_lower = prose.lower()
        self.assertTrue(any(word in prose_lower for word in ["panic", "fear"]))      # Reaction
        self.assertTrue(any(word in prose_lower for word in ["call", "help", "escape"]))  # Dilemma
        self.assertTrue(any(word in prose_lower for word in ["call", "emergency"]))  # Decision


class TestPOVHandler(unittest.TestCase):
    """Test POV and tense handler"""
    
    def setUp(self):
        self.pov_handler = POVHandler()
    
    def test_pov_detection(self):
        """Test POV detection in prose"""
        
        first_person_text = "I walked to the store and bought some milk."
        third_person_text = "She walked to the store and bought some milk."
        
        first_detected = self.pov_handler._detect_pov(first_person_text)
        third_detected = self.pov_handler._detect_pov(third_person_text)
        
        self.assertEqual(first_detected, POVType.FIRST_PERSON)
        self.assertEqual(third_detected, POVType.THIRD_LIMITED)
    
    def test_tense_detection(self):
        """Test tense detection in prose"""
        
        past_text = "I walked to the store and bought some milk."
        present_text = "I walk to the store and buy some milk."
        
        past_detected = self.pov_handler._detect_tense(past_text)
        present_detected = self.pov_handler._detect_tense(present_text)
        
        self.assertEqual(past_detected, TenseType.PAST)
        self.assertEqual(present_detected, TenseType.PRESENT)
    
    def test_pov_consistency_validation(self):
        """Test POV consistency validation"""
        
        consistent_text = "I walked to the store. I bought some milk. I went home."
        inconsistent_text = "I walked to the store. She bought some milk. I went home."
        
        consistent_result = self.pov_handler.validate_consistency(consistent_text, POVType.FIRST_PERSON)
        inconsistent_result = self.pov_handler.validate_consistency(inconsistent_text, POVType.FIRST_PERSON)
        
        self.assertTrue(consistent_result)
        self.assertFalse(inconsistent_result)


class TestExpositionTracker(unittest.TestCase):
    """Test exposition tracking and budget enforcement"""
    
    def setUp(self):
        self.tracker = ExpositionTracker()
        self.budget = ExpositionBudget(
            max_exposition_percentage=0.2,
            max_backstory_sentences=2,
            max_world_building_sentences=1
        )
    
    def test_exposition_tracking(self):
        """Test basic exposition tracking"""
        
        self.tracker.initialize_budget(self.budget)
        
        # Add some exposition
        self.tracker.add_exposition("backstory", "Years ago, he had worked in this building.", "setup")
        self.tracker.add_exposition("world_building", "In this world, security systems were omnipresent.", "context")
        
        # Add regular prose
        self.tracker.add_prose_content("He walked quickly down the hallway, his heart pounding.")
        
        report = self.tracker.get_usage_report()
        
        self.assertIn('total_exposition_words', report)
        self.assertIn('exposition_percentage', report)
        self.assertIn('usage_by_type', report)
        self.assertGreater(report['total_exposition_words'], 0)
    
    def test_budget_violation_detection(self):
        """Test budget violation detection"""
        
        strict_budget = ExpositionBudget(
            max_exposition_percentage=0.1,  # Very strict
            max_backstory_sentences=1,
            strict_enforcement=True
        )
        
        self.tracker.initialize_budget(strict_budget)
        
        # Add minimal regular content
        self.tracker.add_prose_content("He ran.")
        
        # Add excessive exposition
        self.tracker.add_exposition("backstory", "Long exposition sentence one.")
        self.tracker.add_exposition("backstory", "Long exposition sentence two.")  # Should exceed limit
        
        self.assertTrue(self.tracker.is_budget_exceeded())
        
        recommendations = self.tracker.get_recommendations()
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)


if __name__ == '__main__':
    unittest.main()