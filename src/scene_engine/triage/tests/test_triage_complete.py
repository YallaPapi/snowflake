"""
Comprehensive Tests for Scene Triage Service

TaskMaster Task 45 Testing: Tests triage classification accuracy, redesign pipeline,
scene type correction, part rewriting, compression, emotion targeting, and re-validation.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from ..service import SceneTriageService, TriageRequest, TriageResponse, TriageDecision
from ..classifier import TriageClassifier, ClassificationCriteria
from ..redesign import RedesignPipeline, RedesignRequest
from ..corrections import SceneTypeCorrector, PartRewriter, CompressionDecider
from ..emotion_targeting import EmotionTargeter, EmotionTarget
from ...models import SceneCard, SceneType


class TestSceneTriageService(unittest.TestCase):
    """
    Test core triage service functionality
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.triage_service = SceneTriageService()
        
        # Create sample high-quality scene
        self.high_quality_scene = self._create_high_quality_scene()
        
        # Create sample low-quality scene
        self.low_quality_scene = self._create_low_quality_scene()
        
        # Create sample medium-quality scene
        self.medium_quality_scene = self._create_medium_quality_scene()
    
    def _create_high_quality_scene(self) -> SceneCard:
        """Create high-quality scene that should get YES decision"""
        
        proactive_mock = Mock()
        proactive_mock.goal = "retrieve the critical research data from the secure server before the deadline"
        proactive_mock.conflict = "the advanced security system detects the intrusion and locks down all access"
        proactive_mock.setback = "the backup power fails, corrupting half the data during transfer"
        
        scene_card = Mock(spec=SceneCard)
        scene_card.scene_id = "high_quality_001"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = "Dr. Sarah Chen"
        scene_card.pov = "third_limited"
        scene_card.tense = "past"
        scene_card.scene_crucible = "the desperate race to save the research project before funding is cut"
        scene_card.setting = "university research laboratory"
        scene_card.proactive = proactive_mock
        
        return scene_card
    
    def _create_low_quality_scene(self) -> SceneCard:
        """Create low-quality scene that should get NO decision"""
        
        scene_card = Mock(spec=SceneCard)
        scene_card.scene_id = "low_quality_001"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = None  # Missing
        scene_card.pov = None            # Missing
        scene_card.tense = None          # Missing
        scene_card.scene_crucible = None # Missing
        scene_card.proactive = None     # Missing structure
        
        return scene_card
    
    def _create_medium_quality_scene(self) -> SceneCard:
        """Create medium-quality scene that should get MAYBE decision"""
        
        proactive_mock = Mock()
        proactive_mock.goal = "find something"  # Too vague
        proactive_mock.conflict = "problem"     # Too brief
        proactive_mock.setback = "fails"        # Too brief
        
        scene_card = Mock(spec=SceneCard)
        scene_card.scene_id = "medium_quality_001"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = "Character"
        scene_card.pov = "third_limited"
        scene_card.tense = "past"
        scene_card.scene_crucible = "some problem"  # Too brief
        scene_card.proactive = proactive_mock
        
        return scene_card
    
    def test_high_quality_scene_gets_yes_decision(self):
        """Test that high-quality scenes receive YES decision"""
        
        request = TriageRequest(
            scene_card=self.high_quality_scene,
            run_full_validation=True,
            auto_redesign_maybe=False  # Don't auto-redesign for this test
        )
        
        response = self.triage_service.evaluate_scene(request)
        
        self.assertTrue(response.success)
        self.assertEqual(response.decision, TriageDecision.YES)
        self.assertGreater(response.classification_score, 0.8)
        self.assertIn("validation", response.components_evaluated)
        self.assertIn("classification", response.components_evaluated)
    
    def test_low_quality_scene_gets_no_decision(self):
        """Test that low-quality scenes receive NO decision"""
        
        request = TriageRequest(
            scene_card=self.low_quality_scene,
            run_full_validation=True,
            auto_redesign_maybe=False
        )
        
        response = self.triage_service.evaluate_scene(request)
        
        self.assertTrue(response.success)
        self.assertEqual(response.decision, TriageDecision.NO)
        self.assertLess(response.classification_score, 0.5)
        self.assertGreater(len(response.identified_issues), 0)
        self.assertGreater(len(response.recommendations), 0)
    
    def test_medium_quality_scene_gets_maybe_decision(self):
        """Test that medium-quality scenes receive MAYBE decision"""
        
        request = TriageRequest(
            scene_card=self.medium_quality_scene,
            auto_redesign_maybe=False  # Test classification only
        )
        
        response = self.triage_service.evaluate_scene(request)
        
        self.assertTrue(response.success)
        self.assertEqual(response.decision, TriageDecision.MAYBE)
        self.assertGreater(response.classification_score, 0.4)
        self.assertLess(response.classification_score, 0.8)
    
    def test_maybe_scene_with_auto_redesign(self):
        """Test MAYBE scene with automatic redesign pipeline"""
        
        request = TriageRequest(
            scene_card=self.medium_quality_scene,
            auto_redesign_maybe=True,
            max_redesign_attempts=2
        )
        
        response = self.triage_service.evaluate_scene(request)
        
        self.assertTrue(response.success)
        self.assertTrue(response.redesign_applied)
        self.assertGreater(response.redesign_attempts, 0)
        self.assertIn("redesign", response.components_evaluated)
        self.assertIn("re_triage", response.components_evaluated)
        
        # Should have improved from original
        self.assertIsNotNone(response.final_scene_card)
    
    def test_prose_content_analysis(self):
        """Test triage with prose content analysis"""
        
        sample_prose = """
        Sarah rushed into the laboratory, her heart pounding. She needed to find the research data 
        before the funding committee arrived in an hour. The computer screens flickered ominously 
        as she began her desperate search through the encrypted files.
        
        "Where is it?" she whispered, fingers flying over the keyboard. The security system beeped 
        a warning - she was running out of authorized access time. With growing panic, she realized 
        the data might be corrupted beyond recovery.
        """
        
        request = TriageRequest(
            scene_card=self.medium_quality_scene,
            prose_content=sample_prose,
            include_prose_analysis=True
        )
        
        response = self.triage_service.evaluate_scene(request)
        
        self.assertTrue(response.success)
        self.assertIn("prose_generation", response.components_evaluated)
        self.assertIsNotNone(response.quality_metrics)
    
    def test_custom_classification_criteria(self):
        """Test triage with custom classification criteria"""
        
        strict_criteria = ClassificationCriteria(
            yes_quality_threshold=0.9,    # Very strict
            no_quality_threshold=0.6,     # Higher threshold
            yes_structure_adherence=0.95,
            require_complete_structure=True
        )
        
        request = TriageRequest(
            scene_card=self.high_quality_scene,
            custom_criteria=strict_criteria
        )
        
        response = self.triage_service.evaluate_scene(request)
        
        self.assertTrue(response.success)
        # With stricter criteria, high-quality scene might become MAYBE
        self.assertIn(response.decision, [TriageDecision.YES, TriageDecision.MAYBE])
    
    def test_bulk_triage_functionality(self):
        """Test bulk triage of multiple scenes"""
        
        scenes = [
            self.high_quality_scene,
            self.medium_quality_scene,
            self.low_quality_scene
        ]
        
        responses = self.triage_service.bulk_triage(scenes)
        
        self.assertEqual(len(responses), 3)
        self.assertTrue(all(response.success for response in responses))
        
        # Get summary
        summary = self.triage_service.get_triage_summary(responses)
        
        self.assertEqual(summary['total_scenes'], 3)
        self.assertIn('decisions', summary)
        self.assertIn('decision_percentages', summary)
        self.assertGreater(summary['average_quality_score'], 0)


class TestTriageClassifier(unittest.TestCase):
    """Test the core classification logic"""
    
    def setUp(self):
        self.classifier = TriageClassifier()
        
        # Create test scenes
        self.complete_proactive = self._create_complete_proactive_scene()
        self.incomplete_reactive = self._create_incomplete_reactive_scene()
        
    def _create_complete_proactive_scene(self):
        """Create complete proactive scene for testing"""
        proactive_mock = Mock()
        proactive_mock.goal = "infiltrate the enemy base and retrieve the stolen intelligence"
        proactive_mock.conflict = "advanced security systems and armed guards patrol the facility"
        proactive_mock.setback = "the alarm is triggered during extraction, forcing an emergency escape"
        
        scene_card = Mock()
        scene_card.scene_id = "complete_proactive"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = "Agent Miller"
        scene_card.pov = "third_limited"
        scene_card.tense = "past"
        scene_card.scene_crucible = "the high-stakes mission to prevent war"
        scene_card.proactive = proactive_mock
        return scene_card
    
    def _create_incomplete_reactive_scene(self):
        """Create incomplete reactive scene for testing"""
        reactive_mock = Mock()
        reactive_mock.reaction = "sad"  # Too brief
        reactive_mock.dilemma = None    # Missing
        reactive_mock.decision = "decides something"  # Vague
        
        scene_card = Mock()
        scene_card.scene_id = "incomplete_reactive"
        scene_card.scene_type = SceneType.REACTIVE
        scene_card.pov_character = "Character"
        scene_card.pov = "first"
        scene_card.tense = "present"
        scene_card.scene_crucible = None  # Missing
        scene_card.reactive = reactive_mock
        return scene_card
    
    def test_complete_scene_classification(self):
        """Test classification of complete scene"""
        
        result = self.classifier.classify_scene(
            scene_card=self.complete_proactive,
            prose_content=None
        )
        
        self.assertIn('decision', result)
        self.assertIn('score', result)
        self.assertIn('metrics', result)
        self.assertGreater(result['score'], 0.6)
        self.assertEqual(result['decision'], TriageDecision.YES)
    
    def test_incomplete_scene_classification(self):
        """Test classification of incomplete scene"""
        
        result = self.classifier.classify_scene(
            scene_card=self.incomplete_reactive,
            prose_content=None
        )
        
        self.assertEqual(result['decision'], TriageDecision.NO)
        self.assertLess(result['score'], 0.6)
        self.assertGreater(len(result['issues']), 0)
        self.assertGreater(len(result['recommendations']), 0)
    
    def test_prose_content_classification(self):
        """Test classification with prose content"""
        
        high_quality_prose = """
        Agent Miller crouched in the shadows outside the enemy compound, his heart hammering 
        against his ribs. The mission was simple in concept but deadly in execution: infiltrate 
        the heavily guarded facility and retrieve the stolen intelligence before it could be 
        transmitted to hostile forces.
        
        He studied the patrol patterns through his night-vision scope. Two guards, rotating 
        every fifteen minutes. Security cameras swept the perimeter in predictable arcs. 
        The advanced alarm system would detect even the slightest irregularity.
        
        As Miller slipped through the outer defenses, every shadow seemed to whisper danger. 
        He had nearly reached the data vault when his foot caught a nearly invisible wire. 
        The facility exploded into blazing light as sirens wailed their terrible warning.
        """
        
        result = self.classifier.classify_scene(
            scene_card=self.complete_proactive,
            prose_content=high_quality_prose
        )
        
        self.assertEqual(result['decision'], TriageDecision.YES)
        self.assertGreater(result['score'], 0.7)
        
        # Check prose quality metrics
        metrics = result['metrics']
        self.assertIn('prose_quality_score', metrics)
        self.assertIn('word_count', metrics)
        self.assertGreater(metrics['prose_quality_score'], 0.6)


class TestRedesignPipeline(unittest.TestCase):
    """Test the redesign pipeline for MAYBE scenes"""
    
    def setUp(self):
        self.redesign_pipeline = RedesignPipeline()
        self.medium_scene = self._create_medium_quality_scene()
    
    def _create_medium_quality_scene(self):
        """Create scene needing redesign"""
        proactive_mock = Mock()
        proactive_mock.goal = "do something important"  # Vague
        proactive_mock.conflict = "obstacle"            # Too brief
        proactive_mock.setback = "problem occurs"       # Vague
        
        scene_card = Mock()
        scene_card.scene_id = "redesign_test"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.pov_character = "Hero"
        scene_card.pov = "third_limited"
        scene_card.tense = "past"
        scene_card.scene_crucible = "tension"  # Too brief
        scene_card.proactive = proactive_mock
        return scene_card
    
    def test_redesign_pipeline_execution(self):
        """Test full redesign pipeline execution"""
        
        request = RedesignRequest(
            scene_card=self.medium_scene,
            target_quality_score=0.8,
            max_attempts=2
        )
        
        response = self.redesign_pipeline.redesign_scene(request)
        
        self.assertTrue(response.success)
        self.assertGreater(response.redesign_attempts, 0)
        self.assertGreater(len(response.steps_executed), 0)
        self.assertIsNotNone(response.final_scene_card)
        
        # Should show improvement
        self.assertGreater(response.final_quality_score, response.initial_quality_score)
    
    def test_scene_type_correction_step(self):
        """Test scene type correction step"""
        
        # Create scene with type mismatch
        reactive_mock = Mock()
        reactive_mock.reaction = "felt determined to succeed"  # Sounds proactive
        reactive_mock.dilemma = "which path to take"
        reactive_mock.decision = "take the direct approach"
        
        mismatched_scene = Mock()
        mismatched_scene.scene_id = "type_mismatch"
        mismatched_scene.scene_type = SceneType.REACTIVE  # But content suggests proactive
        mismatched_scene.scene_crucible = "achieving the goal"
        mismatched_scene.reactive = reactive_mock
        
        request = RedesignRequest(
            scene_card=mismatched_scene,
            enable_scene_type_correction=True,
            enable_part_rewriting=False,
            enable_compression=False,
            enable_emotion_targeting=False
        )
        
        response = self.redesign_pipeline.redesign_scene(request)
        
        self.assertTrue(response.success)
        self.assertGreater(len(response.corrections_applied), 0)


class TestSceneTypeCorrector(unittest.TestCase):
    """Test scene type correction functionality"""
    
    def setUp(self):
        self.corrector = SceneTypeCorrector()
    
    def test_proactive_scene_correction(self):
        """Test correction of proactive scene structure"""
        
        # Scene missing proactive structure
        incomplete_scene = Mock()
        incomplete_scene.scene_id = "incomplete_proactive"
        incomplete_scene.scene_type = SceneType.PROACTIVE
        incomplete_scene.scene_crucible = "test crucible"
        incomplete_scene.proactive = None  # Missing structure
        
        result = self.corrector.correct_scene_type(incomplete_scene)
        
        self.assertGreater(len(result['corrections_applied']), 0)
        self.assertIsNotNone(result['scene_card'].proactive)
        self.assertTrue(hasattr(result['scene_card'].proactive, 'goal'))
        self.assertTrue(hasattr(result['scene_card'].proactive, 'conflict'))
        self.assertTrue(hasattr(result['scene_card'].proactive, 'setback'))
    
    def test_reactive_scene_correction(self):
        """Test correction of reactive scene structure"""
        
        incomplete_scene = Mock()
        incomplete_scene.scene_id = "incomplete_reactive"
        incomplete_scene.scene_type = SceneType.REACTIVE
        incomplete_scene.scene_crucible = "test crucible"
        incomplete_scene.reactive = None  # Missing structure
        
        result = self.corrector.correct_scene_type(incomplete_scene)
        
        self.assertGreater(len(result['corrections_applied']), 0)
        self.assertIsNotNone(result['scene_card'].reactive)
        self.assertTrue(hasattr(result['scene_card'].reactive, 'reaction'))
        self.assertTrue(hasattr(result['scene_card'].reactive, 'dilemma'))
        self.assertTrue(hasattr(result['scene_card'].reactive, 'decision'))


class TestPartRewriter(unittest.TestCase):
    """Test part rewriting functionality"""
    
    def setUp(self):
        self.rewriter = PartRewriter()
    
    def test_scene_card_part_rewriting(self):
        """Test rewriting of scene card parts"""
        
        # Scene with weak parts
        weak_scene = self._create_weak_scene()
        
        result = self.rewriter.rewrite_problematic_parts(
            scene_card=weak_scene,
            target_quality=0.8
        )
        
        self.assertGreater(len(result['parts_rewritten']), 0)
        # Scene card should be improved
        self.assertIsNotNone(result['scene_card'])
    
    def _create_weak_scene(self):
        """Create scene with weak parts for testing"""
        proactive_mock = Mock()
        proactive_mock.goal = "thing"      # Too vague
        proactive_mock.conflict = "bad"    # Too brief
        proactive_mock.setback = "fails"   # Too brief
        
        scene_card = Mock()
        scene_card.scene_id = "weak_scene"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.scene_crucible = "test"  # Too brief
        scene_card.proactive = proactive_mock
        return scene_card
    
    def test_prose_part_rewriting(self):
        """Test rewriting of prose parts"""
        
        weak_prose = "He did something. It was bad. He failed."  # Too simple
        
        result = self.rewriter.rewrite_problematic_parts(
            scene_card=self._create_weak_scene(),
            prose_content=weak_prose,
            target_quality=0.8
        )
        
        if result['parts_rewritten']:
            self.assertIsNotNone(result['prose_content'])
            # Should be enhanced
            self.assertNotEqual(result['prose_content'], weak_prose)


class TestCompressionDecider(unittest.TestCase):
    """Test compression decision functionality"""
    
    def setUp(self):
        self.compression_decider = CompressionDecider()
    
    def test_verbose_scene_compression(self):
        """Test compression of verbose scene"""
        
        # Create verbose scene
        verbose_scene = self._create_verbose_scene()
        verbose_prose = self._create_verbose_prose()
        
        result = self.compression_decider.decide_and_compress(
            scene_card=verbose_scene,
            prose_content=verbose_prose,
            compression_threshold=0.5  # Lower threshold to trigger compression
        )
        
        if result['compression_analysis']['needs_compression']:
            self.assertTrue(result['compression_applied'])
            self.assertIsNotNone(result['scene_card'])
            
            if verbose_prose:
                # Compressed prose should be shorter
                compressed_prose = result['prose_content']
                self.assertLessEqual(len(compressed_prose), len(verbose_prose))
    
    def _create_verbose_scene(self):
        """Create overly verbose scene"""
        proactive_mock = Mock()
        proactive_mock.goal = "achieve the very important and critically essential objective that must be completed within the specified timeframe"
        proactive_mock.conflict = "encounter significant and substantial obstacles that create major impediments to success"
        proactive_mock.setback = "experience complete and total failure resulting in devastating consequences"
        
        scene_card = Mock()
        scene_card.scene_id = "verbose_scene"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.scene_crucible = "the extremely critical and vitally important situation that demands immediate attention"
        scene_card.proactive = proactive_mock
        return scene_card
    
    def _create_verbose_prose(self):
        """Create verbose prose for testing"""
        return """
        The character walked very slowly and quite deliberately across the extremely large 
        and incredibly spacious room that was really very big indeed. He was thinking very 
        deeply and quite intensely about the situation that was really quite serious and 
        extremely important in every possible way. The problem was really very difficult 
        and incredibly challenging in ways that were quite remarkable and truly extraordinary.
        """


class TestEmotionTargeter(unittest.TestCase):
    """Test emotion targeting functionality"""
    
    def setUp(self):
        self.emotion_targeter = EmotionTargeter()
    
    def test_emotion_analysis(self):
        """Test emotion analysis of scene content"""
        
        # Create scene with clear emotional content
        emotional_scene = self._create_emotional_scene()
        emotional_prose = "She felt overwhelming fear as the darkness closed in around her."
        
        analysis = self.emotion_targeter._analyze_current_emotions(
            emotional_scene, emotional_prose
        )
        
        self.assertIsInstance(analysis.current_emotions, dict)
        self.assertGreaterEqual(analysis.emotional_intensity, 0.0)
        self.assertLessEqual(analysis.emotional_intensity, 1.0)
        
        # Should detect fear
        fear_level = analysis.current_emotions.get(EmotionTarget.FEAR, 0.0)
        self.assertGreater(fear_level, 0.1)
    
    def test_emotion_targeting_application(self):
        """Test application of emotion targeting"""
        
        neutral_scene = self._create_neutral_scene()
        
        result = self.emotion_targeter.apply_emotion_targeting(
            scene_card=neutral_scene,
            prose_content=None,
            target_emotion=EmotionTarget.TENSION
        )
        
        self.assertIn('targeting_applied', result)
        self.assertIn('emotion_analysis', result)
        self.assertEqual(result['target_emotion'], EmotionTarget.TENSION)
        
        if result['targeting_applied']:
            # Should show improvement in target emotion
            analysis = result['emotion_analysis']
            self.assertGreater(analysis['improvement'], 0)
    
    def _create_emotional_scene(self):
        """Create scene with emotional content"""
        reactive_mock = Mock()
        reactive_mock.reaction = "overwhelming terror and paralyzing fear"
        reactive_mock.dilemma = "run and abandon everyone or stay and face certain death"
        reactive_mock.decision = "despite the fear, stays to protect the others"
        
        scene_card = Mock()
        scene_card.scene_id = "emotional_scene"
        scene_card.scene_type = SceneType.REACTIVE
        scene_card.scene_crucible = "the moment of ultimate terror"
        scene_card.reactive = reactive_mock
        return scene_card
    
    def _create_neutral_scene(self):
        """Create emotionally neutral scene"""
        proactive_mock = Mock()
        proactive_mock.goal = "complete the task"
        proactive_mock.conflict = "obstacle appears"
        proactive_mock.setback = "task is not completed"
        
        scene_card = Mock()
        scene_card.scene_id = "neutral_scene"
        scene_card.scene_type = SceneType.PROACTIVE
        scene_card.scene_crucible = "the situation"
        scene_card.proactive = proactive_mock
        return scene_card
    
    def test_emotion_target_recommendation(self):
        """Test emotion target recommendation"""
        
        proactive_scene = Mock()
        proactive_scene.scene_type = SceneType.PROACTIVE
        
        reactive_scene = Mock()
        reactive_scene.scene_type = SceneType.REACTIVE
        
        proactive_recommendation = self.emotion_targeter.recommend_emotion_target(proactive_scene)
        reactive_recommendation = self.emotion_targeter.recommend_emotion_target(reactive_scene)
        
        self.assertEqual(proactive_recommendation, EmotionTarget.TENSION)
        self.assertEqual(reactive_recommendation, EmotionTarget.EMPATHY)


class TestTriageStatistics(unittest.TestCase):
    """Test triage service statistics and reporting"""
    
    def setUp(self):
        self.triage_service = SceneTriageService()
    
    def test_statistics_tracking(self):
        """Test that triage statistics are properly tracked"""
        
        # Create and evaluate several scenes
        scenes = [
            self._create_sample_scene("scene_1", quality="high"),
            self._create_sample_scene("scene_2", quality="medium"),
            self._create_sample_scene("scene_3", quality="low")
        ]
        
        for scene in scenes:
            request = TriageRequest(scene_card=scene, auto_redesign_maybe=False)
            self.triage_service.evaluate_scene(request)
        
        stats = self.triage_service.get_triage_statistics()
        
        self.assertEqual(stats['total_evaluations'], 3)
        self.assertIn('decision_counts', stats)
        self.assertIn('decision_percentages', stats)
        self.assertIn('average_processing_time', stats)
        self.assertIn('average_classification_score', stats)
    
    def _create_sample_scene(self, scene_id: str, quality: str):
        """Create sample scene with specified quality level"""
        
        if quality == "high":
            proactive_mock = Mock()
            proactive_mock.goal = "detailed and specific goal with clear stakes"
            proactive_mock.conflict = "significant obstacle with clear opposition"
            proactive_mock.setback = "meaningful failure that changes everything"
            
            scene_card = Mock()
            scene_card.scene_id = scene_id
            scene_card.scene_type = SceneType.PROACTIVE
            scene_card.pov_character = "Character Name"
            scene_card.pov = "third_limited"
            scene_card.tense = "past"
            scene_card.scene_crucible = "detailed description of the critical situation"
            scene_card.proactive = proactive_mock
            
        elif quality == "medium":
            proactive_mock = Mock()
            proactive_mock.goal = "achieve something important"  # Adequate but not great
            proactive_mock.conflict = "problem occurs"
            proactive_mock.setback = "doesn't work out"
            
            scene_card = Mock()
            scene_card.scene_id = scene_id
            scene_card.scene_type = SceneType.PROACTIVE
            scene_card.pov_character = "Character"
            scene_card.pov = "third_limited"
            scene_card.tense = "past"
            scene_card.scene_crucible = "the situation"  # Too brief
            scene_card.proactive = proactive_mock
            
        else:  # low quality
            scene_card = Mock()
            scene_card.scene_id = scene_id
            scene_card.scene_type = SceneType.PROACTIVE
            scene_card.pov_character = None     # Missing
            scene_card.pov = None               # Missing
            scene_card.tense = None             # Missing
            scene_card.scene_crucible = None   # Missing
            scene_card.proactive = None         # Missing
        
        return scene_card


if __name__ == '__main__':
    unittest.main()