"""
Test Suite for Step 1: One Sentence Summary (Logline)
Tests validator, prompt generation, and execution according to Snowflake Method
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
from src.pipeline.validators.step_1_validator import Step1Validator
from src.pipeline.prompts.step_1_prompt import Step1Prompt

class TestStep1Validator(unittest.TestCase):
    """Test Step 1 validation rules"""
    
    def setUp(self):
        self.validator = Step1Validator()
    
    def test_valid_logline_passes(self):
        """Test that a properly formatted logline passes validation"""
        artifact = {
            "logline": "Sarah, a detective, must prove her suspect's innocence before the mob silences him."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        self.assertLessEqual(artifact['word_count'], 25)
        self.assertLessEqual(artifact['lead_count'], 2)
    
    def test_word_count_limit(self):
        """Test that loglines over 25 words fail"""
        # 30 words - too long
        artifact = {
            "logline": "Sarah, a very experienced detective with a troubled past and drinking problem, must somehow find a way to prove her primary suspect's complete innocence before the dangerous mob silences him forever."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO LONG" in e for e in errors))
    
    def test_maximum_two_named_leads(self):
        """Test that more than 2 named characters fails"""
        artifact = {
            "logline": "Sarah, Marcus, Elena, and David must work together to stop the heist."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO MANY NAMES" in e for e in errors))
        
        # Two names should be OK
        artifact = {
            "logline": "Sarah and Marcus, rival detectives, must work together to stop the heist."
        }
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("TOO MANY NAMES" in e for e in errors))
    
    def test_requires_protagonist_name(self):
        """Test that logline needs at least one named character"""
        artifact = {
            "logline": "A detective must prove the suspect's innocence before time runs out."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("NO PROTAGONIST" in e for e in errors))
    
    def test_external_goal_required(self):
        """Test that concrete external goal is required"""
        # Mood goal - should fail
        artifact = {
            "logline": "Sarah, a detective, must find herself while investigating the case."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MOOD GOAL" in e for e in errors))
        
        # Concrete goal - should pass goal check
        artifact = {
            "logline": "Sarah, a detective, must expose the mole before the operation fails."
        }
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("MOOD GOAL" in e for e in errors))
        self.assertFalse(any("NO CONCRETE GOAL" in e for e in errors))
    
    def test_must_obligation_word(self):
        """Test that 'must' or similar obligation word is required"""
        artifact = {
            "logline": "Sarah, a detective, wants to solve the case quickly."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("NO OBLIGATION" in e for e in errors))
        
        # With "must" should pass obligation check
        artifact = {
            "logline": "Sarah, a detective, must solve the case before midnight."
        }
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("NO OBLIGATION" in e for e in errors))
    
    def test_opposition_required(self):
        """Test that opposition/conflict is required"""
        artifact = {
            "logline": "Sarah, a detective, must solve the mysterious case."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("NO OPPOSITION" in e for e in errors))
        
        # With opposition should pass
        artifact = {
            "logline": "Sarah, a detective, must solve the case despite the corrupt police chief."
        }
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("NO OPPOSITION" in e for e in errors))
    
    def test_ending_not_revealed(self):
        """Test that ending must not be revealed"""
        artifact = {
            "logline": "Sarah, a detective, successfully proves her suspect's innocence and saves him."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("ENDING REVEALED" in e for e in errors))
        
        # Without ending reveal
        artifact = {
            "logline": "Sarah, a detective, must prove her suspect's innocence before it's too late."
        }
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("ENDING REVEALED" in e for e in errors))
    
    def test_proper_structure_parsing(self):
        """Test that properly structured logline gets parsed"""
        artifact = {
            "logline": "Marcus, a disgraced surgeon, must perform the impossible operation despite his trembling hands."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        
        # Check components were parsed
        self.assertIn('components', artifact)
        self.assertEqual(artifact['components']['lead_name'], 'Marcus')
        self.assertEqual(artifact['components']['lead_role'], 'disgraced surgeon')
        self.assertIn('perform', artifact['components']['external_goal'])
    
    def test_compression_helper(self):
        """Test the compression helper method"""
        verbose = "Sarah, a very experienced detective, must find a way to prove the suspect's complete innocence."
        compressed = self.validator.compress_logline(verbose)
        
        # Should be shorter
        self.assertLess(len(compressed.split()), len(verbose.split()))
        # Should remove "very", "find a way to", etc.
        self.assertNotIn("very", compressed)
        self.assertNotIn("find a way to", compressed)

class TestStep1Prompt(unittest.TestCase):
    """Test Step 1 prompt generation"""
    
    def setUp(self):
        self.prompt_gen = Step1Prompt()
        self.step_0_artifact = {
            "category": "Romantic Suspense",
            "story_kind": "Enemies-to-lovers with espionage backdrop.",
            "audience_delight": "Undercover reveals, forced proximity, betrayal twist."
        }
    
    def test_prompt_generation(self):
        """Test that prompts are generated correctly"""
        story_brief = "A detective falls in love with her suspect during investigation"
        
        prompt_data = self.prompt_gen.generate_prompt(self.step_0_artifact, story_brief)
        
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        
        # Check system prompt content
        self.assertIn("maximum 25 words", prompt_data["system"])
        self.assertIn("EXTERNAL, TESTABLE", prompt_data["system"])
        
        # Check user prompt includes context
        self.assertIn("Romantic Suspense", prompt_data["user"])
        self.assertIn("Enemies-to-lovers", prompt_data["user"])
        self.assertIn(story_brief, prompt_data["user"])
    
    def test_compression_prompt(self):
        """Test compression prompt generation"""
        long_logline = "Sarah, a very experienced detective with years of training, must find a way to prove her suspect's innocence."
        
        prompt_data = self.prompt_gen.generate_compression_prompt(long_logline, 18)
        
        self.assertIn("COMPRESS", prompt_data["user"])
        self.assertIn("18-word", prompt_data["user"])
        self.assertIn("≤25 words", prompt_data["user"])
    
    def test_revision_prompt(self):
        """Test revision prompt for fixing errors"""
        current = "Sarah wants to find herself during the investigation."
        errors = ["MOOD GOAL: Convert internal goal to external proxy", 
                 "NO OBLIGATION: Missing 'must'"]
        
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current, errors, self.step_0_artifact
        )
        
        self.assertIn("FIX this logline", prompt_data["user"])
        self.assertIn("MOOD GOAL", prompt_data["user"])
        self.assertIn("REPLACE internal goal", prompt_data["user"])

class TestStep1Execution(unittest.TestCase):
    """Test Step 1 execution and file operations"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.step1 = Step1OneSentenceSummary(self.test_dir)
        self.step_0_artifact = {
            "category": "Psychological Thriller",
            "story_kind": "Unreliable narrator with conspiracy backdrop.",
            "audience_delight": "Plot twists, psychological games, shocking reveal.",
            "metadata": {
                "project_id": "test-123",
                "step": 0,
                "version": "1.0.0"
            }
        }
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_metadata_generation(self):
        """Test that metadata is properly generated"""
        content = {"logline": "Test logline."}
        model_config = {"model_name": "test-model", "temperature": 0.2}
        
        artifact = self.step1.add_metadata(
            content, "test-123", "hash123", model_config, "upstream123"
        )
        
        self.assertEqual(artifact["metadata"]["step"], 1)
        self.assertEqual(artifact["metadata"]["project_id"], "test-123")
        self.assertEqual(artifact["metadata"]["hash_upstream"], "upstream123")
        self.assertIn("created_at", artifact["metadata"])
    
    def test_artifact_saving(self):
        """Test that artifacts are saved correctly"""
        artifact = {
            "logline": "Marcus, a surgeon, must save the patient despite sabotage.",
            "word_count": 9,
            "lead_count": 1,
            "metadata": {
                "project_id": "test-123",
                "step": 1,
                "version": "1.0.0",
                "created_at": "2024-01-01T00:00:00",
                "hash_upstream": "abc123"
            }
        }
        
        save_path = self.step1.save_artifact(artifact, "test-123")
        
        # Check JSON file
        self.assertTrue(save_path.exists())
        with open(save_path, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["logline"], artifact["logline"])
        
        # Check human-readable file
        txt_path = save_path.parent / "step_1_one_sentence_summary.txt"
        self.assertTrue(txt_path.exists())
        with open(txt_path, 'r') as f:
            content = f.read()
        self.assertIn("LOGLINE:", content)
        self.assertIn("Word Count: 9/25", content)
    
    def test_validation_only(self):
        """Test validation without execution"""
        # Valid logline
        valid = {
            "logline": "Elena, a spy, must steal the codes before dawn."
        }
        
        is_valid, message = self.step1.validate_only(valid)
        self.assertTrue(is_valid)
        self.assertIn("passes all checks", message)
        
        # Invalid logline
        invalid = {
            "logline": "Someone needs to find themselves."
        }
        
        is_valid, message = self.step1.validate_only(invalid)
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", message)

if __name__ == "__main__":
    unittest.main()