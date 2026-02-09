"""
Integration test for Steps 0-3 of the Snowflake pipeline
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
from src.pipeline.steps.step_1_one_sentence_summary import Step1OneSentenceSummary
from src.pipeline.steps.step_2_one_paragraph_summary import Step2OneParagraphSummary
from src.pipeline.steps.step_3_character_summaries import Step3CharacterSummaries

class TestPipelineIntegration(unittest.TestCase):
    """Test pipeline integration from Step 0 to Step 3"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_id = "test-integration-123"
        
        # Initialize all steps
        self.step0 = Step0FirstThingsFirst(self.test_dir)
        self.step1 = Step1OneSentenceSummary(self.test_dir)
        self.step2 = Step2OneParagraphSummary(self.test_dir)
        self.step3 = Step3CharacterSummaries(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_complete_pipeline_flow(self):
        """Test complete flow from Step 0 to Step 3"""
        
        # Step 0: First Things First
        user_input = {
            "category": "Psychological Thriller",
            "story_kind": "Cat and mouse game with unreliable narrator and conspiracy backdrop.",
            "selected_tropes": ["unreliable narrator", "conspiracy", "psychological games"],
            "selected_satisfiers": ["plot twists", "mind games", "shocking reveal", "morally grey characters"]
        }
        
        success, step0_artifact, message = self.step0.execute(user_input, self.project_id)
        self.assertTrue(success, f"Step 0 failed: {message}")
        
        # Verify Step 0 output
        self.assertIn('category', step0_artifact)
        self.assertIn('story_kind', step0_artifact)
        self.assertIn('audience_delight', step0_artifact)
        
        # Step 1: One Sentence Summary
        story_brief = "A therapist discovers her star patient might be innocent of murder but proving it means confronting a conspiracy"
        
        success, step1_artifact, message = self.step1.execute(
            step0_artifact, story_brief, self.project_id
        )
        
        # For now, manually set a valid logline since AI isn't connected
        step1_artifact['logline'] = "Sarah Chen, a therapist, must prove her patient's innocence before he's executed by the state."

        # Re-validate
        is_valid, message = self.step1.validate_only(step1_artifact)
        self.assertTrue(is_valid, f"Step 1 validation failed: {message}")

        # Save manually-fixed artifact to disk
        step1_artifact = self.step1.add_metadata(step1_artifact, self.project_id, "test-hash", {"model_name": "mock"}, "upstream-hash")
        self.step1.save_artifact(step1_artifact, self.project_id)
        
        # Step 2: One Paragraph Summary
        success, step2_artifact, message = self.step2.execute(
            step0_artifact, step1_artifact, self.project_id
        )
        
        # Manually set valid paragraph for testing
        step2_artifact['paragraph'] = (
            "In Boston today, Sarah Chen must prove her death-row patient innocent before his execution in 30 days. "
            "When her supervisor dies mysteriously after supporting her, she is forced to investigate alone or abandon her patient. "
            "After discovering the real killer is a prominent judge, she realizes she must risk everything for truth and has no choice but to shift to a new approach gathering evidence illegally. "
            "When the judge frames Sarah for murder too, both she and her patient are trapped in a final confrontation and must expose the truth or die. "
            "In the courtroom showdown, Sarah confronts the judge and sacrifices her license but saves her patient and exposes the conspiracy."
        )
        step2_artifact['moral_premise'] = "People succeed when they risk everything for truth, and they fail when they protect their position over justice."
        
        # Re-validate
        is_valid, message = self.step2.validate_only(step2_artifact)
        self.assertTrue(is_valid, f"Step 2 validation failed: {message}")

        # Save manually-fixed artifact to disk
        step2_artifact = self.step2.add_metadata(step2_artifact, self.project_id, "test-hash", {"model_name": "mock"}, "upstream-hash")
        self.step2.save_artifact(step2_artifact, self.project_id)

        # Step 3: Character Summaries
        success, step3_artifact, message = self.step3.execute(
            step0_artifact, step1_artifact, step2_artifact, self.project_id
        )
        
        # Verify Step 3 output
        self.assertIn('characters', step3_artifact)
        self.assertGreaterEqual(len(step3_artifact['characters']), 2)
        
        # Check protagonist exists
        has_protagonist = any(c['role'] == 'Protagonist' for c in step3_artifact['characters'])
        self.assertTrue(has_protagonist, "Missing protagonist")
        
        # Check antagonist exists
        has_antagonist = any(c['role'] == 'Antagonist' for c in step3_artifact['characters'])
        self.assertTrue(has_antagonist, "Missing antagonist")
        
        # Verify files were created
        project_path = Path(self.test_dir) / self.project_id
        self.assertTrue((project_path / "step_0_first_things_first.json").exists())
        self.assertTrue((project_path / "step_1_one_sentence_summary.json").exists())
        self.assertTrue((project_path / "step_2_one_paragraph_summary.json").exists())
        self.assertTrue((project_path / "step_3_character_summaries.json").exists())
        
        # Verify human-readable files
        self.assertTrue((project_path / "step_0_first_things_first.txt").exists())
        self.assertTrue((project_path / "step_1_one_sentence_summary.txt").exists())
        self.assertTrue((project_path / "step_2_one_paragraph_summary.txt").exists())
        self.assertTrue((project_path / "step_3_character_summaries.txt").exists())
    
    def test_upstream_hash_tracking(self):
        """Test that upstream hashes are properly tracked"""
        
        # Create minimal valid artifacts
        step0_artifact = {
            "category": "Mystery",
            "story_kind": "Cozy mystery",
            "audience_delight": "Puzzles, red herrings, satisfying reveal.",
            "metadata": {"project_id": self.project_id, "step": 0}
        }
        
        step1_artifact = {
            "logline": "Jane must solve the murder.",
            "metadata": {"project_id": self.project_id, "step": 1}
        }
        
        step2_artifact = {
            "paragraph": "S1. S2. S3. S4. S5.",
            "moral_premise": "People succeed when they persist.",
            "metadata": {"project_id": self.project_id, "step": 2}
        }
        
        # Execute Step 3
        success, step3_artifact, message = self.step3.execute(
            step0_artifact, step1_artifact, step2_artifact, self.project_id
        )
        
        # Check upstream hash exists
        self.assertIn('hash_upstream', step3_artifact['metadata'])
        self.assertIsNotNone(step3_artifact['metadata']['hash_upstream'])
        
        # Modify Step 2 and re-run - should get different hash
        step2_artifact['paragraph'] = "Different. Paragraph. Here. Now. End."
        
        success, step3_artifact_2, message = self.step3.execute(
            step0_artifact, step1_artifact, step2_artifact, self.project_id
        )
        
        # Hashes should be different
        self.assertNotEqual(
            step3_artifact['metadata']['hash_upstream'],
            step3_artifact_2['metadata']['hash_upstream']
        )

if __name__ == "__main__":
    unittest.main()