"""
Test Suite for Step 0: First Things First
Tests validator, prompt generation, and execution according to Snowflake Method
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
from src.pipeline.validators.step_0_validator import Step0Validator
from src.pipeline.prompts.step_0_prompt import Step0Prompt

class TestStep0Validator(unittest.TestCase):
    """Test Step 0 validation rules"""
    
    def setUp(self):
        self.validator = Step0Validator()
    
    def test_valid_artifact_passes(self):
        """Test that a properly formatted artifact passes validation"""
        artifact = {
            "category": "Romantic Suspense",
            "story_kind": "Enemies-to-lovers with espionage backdrop.",
            "audience_delight": "Undercover reveals, forced proximity, betrayal twist, heroic sacrifice ending."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_missing_fields_fail(self):
        """Test that missing required fields are caught"""
        artifact = {
            "category": "Romantic Suspense"
            # Missing story_kind and audience_delight
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertIn("MISSING: Story Kind field is required", errors)
        self.assertIn("MISSING: Audience Delight field is required", errors)
    
    def test_invalid_category_fails(self):
        """Test that invalid categories are rejected"""
        # Test vague "Literary"
        artifact = {
            "category": "Literary",
            "story_kind": "A perfectionist must finish the book that terrifies her.",
            "audience_delight": "Creative struggle, complicated friendships, career win, personal growth, redemption."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("VAGUE CATEGORY" in e for e in errors))
        
        # Test completely invalid category
        artifact["category"] = "My Cool Book Type"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID CATEGORY" in e for e in errors))
    
    def test_story_kind_requires_trope(self):
        """Test that story_kind must include a trope noun"""
        artifact = {
            "category": "Contemporary Romance",
            "story_kind": "A woman discovers herself through travel.",  # No trope noun
            "audience_delight": "Self-discovery, travel adventures, new relationships, personal growth, happy ending."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING TROPE" in e for e in errors))
        
        # Now with trope
        artifact["story_kind"] = "A woman discovers herself through travel in this fish-out-of-water romance."
        is_valid, errors = self.validator.validate(artifact)
        # Should pass trope check now (might fail other checks)
        self.assertFalse(any("MISSING TROPE" in e for e in errors))
    
    def test_story_kind_single_sentence(self):
        """Test that story_kind must be ONE sentence"""
        artifact = {
            "category": "Psychological Thriller",
            "story_kind": "An unreliable-narrator tells her story. But nothing is as it seems. Trust no one.",
            "audience_delight": "Plot twists, unreliable narrator, psychological manipulation, shocking reveal, ambiguous ending."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MULTIPLE SENTENCES" in e for e in errors))
    
    def test_audience_delight_concrete_satisfiers(self):
        """Test that audience_delight requires concrete satisfiers, not mood words"""
        # Test with mood words
        artifact = {
            "category": "Epic Fantasy",
            "story_kind": "Chosen-one must save the realm from ancient evil.",
            "audience_delight": "Exciting battles, emotional journey, thrilling adventure, compelling characters."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MOOD WORDS" in e for e in errors))
        
        # Test with concrete satisfiers
        artifact["audience_delight"] = "Magic system reveals, mentor betrayal, found family, heroic sacrifice, bittersweet victory."
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
    
    def test_audience_delight_count(self):
        """Test that audience_delight needs 3-5 concrete satisfiers"""
        # Too few
        artifact = {
            "category": "Cozy Mystery",
            "story_kind": "Amateur sleuth solves whodunit in small town.",
            "audience_delight": "Red herrings, puzzle solving."  # Only 2
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INSUFFICIENT SATISFIERS" in e for e in errors))
        
        # Just right
        artifact["audience_delight"] = "Red herrings, puzzle solving, quirky townspeople, no gore, justice prevails."
        is_valid, errors = self.validator.validate(artifact)
        # Should pass satisfier count (might have other issues)
        self.assertFalse(any("INSUFFICIENT SATISFIERS" in e for e in errors))
    
    def test_todo_markers_noted(self):
        """Test that TODO and BEST-GUESS markers are noted in metadata"""
        artifact = {
            "category": "Romantic Suspense",
            "story_kind": "TODO: Enemies-to-lovers with heist backdrop.",
            "audience_delight": "BEST-GUESS: Betrayal twist, forced proximity, ticking clock, happy ending.",
            "metadata": {}
        }
        
        is_valid, errors = self.validator.validate(artifact)
        # Should note TODO markers in metadata
        self.assertIn("todo_markers", artifact["metadata"])
        self.assertTrue(any("TODO" in marker for marker in artifact["metadata"]["todo_markers"]))

class TestStep0Prompt(unittest.TestCase):
    """Test Step 0 prompt generation"""
    
    def setUp(self):
        self.prompt_gen = Step0Prompt()
    
    def test_prompt_generation(self):
        """Test that prompts are generated correctly"""
        brief = "A story about a detective who falls in love with the suspect"
        
        prompt_data = self.prompt_gen.generate_prompt(brief)
        
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        self.assertIn("version", prompt_data)
        
        # Check system prompt content
        self.assertIn("Snowflake Method Step 0 Planner", prompt_data["system"])
        self.assertIn("NO flowery prose", prompt_data["system"])
        
        # Check user prompt content
        self.assertIn(brief, prompt_data["user"])
        self.assertIn("CATEGORY", prompt_data["user"])
        self.assertIn("STORY KIND", prompt_data["user"])
        self.assertIn("AUDIENCE DELIGHT", prompt_data["user"])
        
        # Check hash is valid SHA256
        self.assertEqual(len(prompt_data["prompt_hash"]), 64)
    
    def test_revision_prompt(self):
        """Test revision prompt generation"""
        original = {
            "category": "Mystery",
            "story_kind": "Detective solves case.",
            "audience_delight": "Clues, investigation, reveal."
        }
        
        reason = "Category too vague, needs more specific subgenre"
        
        prompt_data = self.prompt_gen.generate_revision_prompt(original, reason)
        
        self.assertIn("REVISION REQUIRED", prompt_data["user"])
        self.assertIn(reason, prompt_data["user"])
        self.assertIn("Mystery", prompt_data["user"])
        self.assertTrue(prompt_data.get("revision", False))

class TestStep0Execution(unittest.TestCase):
    """Test Step 0 execution and file operations"""
    
    def setUp(self):
        # Create temporary directory for test artifacts
        self.test_dir = tempfile.mkdtemp()
        self.step0 = Step0FirstThingsFirst(self.test_dir)
    
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_dir)
    
    def test_artifact_saving(self):
        """Test that artifacts are saved correctly"""
        artifact = {
            "category": "Romantic Suspense",
            "story_kind": "Enemies-to-lovers with espionage backdrop.",
            "audience_delight": "Undercover reveals, forced proximity, betrayal twist, heroic sacrifice ending.",
            "metadata": {
                "project_id": "test-project-123",
                "step": 0,
                "version": "1.0.0",
                "created_at": "2024-01-01T00:00:00",
                "model_name": "test-model",
                "prompt_hash": "a" * 64,
                "validator_version": "1.0.0"
            }
        }
        
        save_path = self.step0.save_artifact(artifact, "test-project-123")
        
        # Check JSON file exists and is correct
        self.assertTrue(save_path.exists())
        with open(save_path, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["category"], "Romantic Suspense")
        
        # Check human-readable file exists
        txt_path = save_path.parent / "step_0_first_things_first.txt"
        self.assertTrue(txt_path.exists())
        with open(txt_path, 'r') as f:
            content = f.read()
        self.assertIn("Category: Romantic Suspense", content)
        self.assertIn("Story Kind: Enemies-to-lovers", content)
    
    def test_artifact_loading(self):
        """Test loading saved artifacts"""
        # First save an artifact
        artifact = {
            "category": "Epic Fantasy",
            "story_kind": "Chosen-one quest to save the realm.",
            "audience_delight": "Magic system, world-building, epic battles, mentor figure, heroic journey.",
            "metadata": {"project_id": "test-123", "step": 0, "version": "1.0.0"}
        }
        
        self.step0.save_artifact(artifact, "test-123")
        
        # Now load it
        loaded = self.step0.load_artifact("test-123")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["category"], "Epic Fantasy")
        self.assertEqual(loaded["metadata"]["project_id"], "test-123")
    
    def test_snapshot_creation(self):
        """Test that snapshots are created during revision"""
        artifact = {
            "category": "Thriller",
            "story_kind": "Cat-and-mouse game with serial killer.",
            "audience_delight": "Psychological tension, plot twists, unreliable narrator, shocking reveal.",
            "metadata": {"version": "1.0.0"}
        }
        
        self.step0.snapshot_artifact(artifact, "test-project")
        
        # Check snapshot exists
        snapshot_dir = Path(self.test_dir) / "test-project" / "snapshots"
        self.assertTrue(snapshot_dir.exists())
        
        snapshots = list(snapshot_dir.glob("step_0_v1.0.0_*.json"))
        self.assertEqual(len(snapshots), 1)
        
        # Verify snapshot content
        with open(snapshots[0], 'r') as f:
            snapshot_data = json.load(f)
        self.assertEqual(snapshot_data["category"], "Thriller")
    
    def test_validation_only(self):
        """Test validation without execution"""
        # Valid artifact
        valid_artifact = {
            "category": "Contemporary Romance",
            "story_kind": "Friends-to-lovers in small town setting.",
            "audience_delight": "Slow burn, forced proximity, small town charm, happy ending, found family."
        }
        
        is_valid, message = self.step0.validate_only(valid_artifact)
        self.assertTrue(is_valid)
        self.assertIn("passes all validation", message)
        
        # Invalid artifact
        invalid_artifact = {
            "category": "Some Random Genre",
            "story_kind": "A story happens.",  # No trope
            "audience_delight": "It's exciting and emotional."  # Mood words
        }
        
        is_valid, message = self.step0.validate_only(invalid_artifact)
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", message)
        self.assertIn("FIX:", message)

if __name__ == "__main__":
    unittest.main()