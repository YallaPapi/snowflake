"""
Test Suite for Step 2: One Paragraph Summary (Five Sentences)
Tests validator, prompt generation, and execution according to Snowflake Method
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from src.pipeline.steps.step_2_one_paragraph_summary import Step2OneParagraphSummary
from src.pipeline.validators.step_2_validator import Step2Validator
from src.pipeline.prompts.step_2_prompt import Step2Prompt

class TestStep2Validator(unittest.TestCase):
    """Test Step 2 validation rules"""
    
    def setUp(self):
        self.validator = Step2Validator()
    
    def test_valid_paragraph_passes(self):
        """Test that a properly formatted paragraph passes validation"""
        artifact = {
            "paragraph": (
                "In modern Seattle, Detective Sarah Chen must expose a trafficking ring before the FBI raid tomorrow. "
                "When her partner is murdered at their safehouse, she is forced to go undercover alone or let the ring escape. "
                "After discovering her captain leads the ring, she realizes following protocol will fail and must become a vigilante to gather evidence. "
                "When the traffickers kidnap her sister as leverage, both Sarah and the crime boss must commit to a final deadly confrontation. "
                "In the warehouse showdown, Sarah sacrifices her badge but saves her sister and dozens of victims."
            ),
            "moral_premise": "People succeed when they sacrifice status for justice, and they fail when they protect their position over truth."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        self.assertEqual(artifact['sentence_count'], 5)
        self.assertTrue(artifact['disasters']['d1_present'])
        self.assertTrue(artifact['disasters']['d2_present'])
        self.assertTrue(artifact['disasters']['d3_present'])
    
    def test_wrong_sentence_count_fails(self):
        """Test that paragraphs with wrong sentence count fail"""
        # Only 4 sentences
        artifact = {
            "paragraph": (
                "Sarah must stop the conspiracy. "
                "Her partner betrays her. "
                "She learns the truth. "
                "She wins in the end."
            ),
            "moral_premise": "People succeed when they persist."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG SENTENCE COUNT" in e for e in errors))
        self.assertEqual(artifact['sentence_count'], 4)
    
    def test_missing_disasters_fail(self):
        """Test that missing disaster markers fail"""
        artifact = {
            "paragraph": (
                "Sarah is a detective in Seattle who wants to solve a case. "
                "Something bad happens to her partner. "
                "She discovers new information about the case. "
                "Things get worse for everyone involved. "
                "Eventually she solves the case somehow."
            ),
            "moral_premise": "People succeed when they try hard."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        # Should fail multiple disaster checks
        self.assertTrue(any("D1 WEAK" in e or "D1 NOT FORCING" in e for e in errors))
        self.assertTrue(any("D2 WEAK" in e or "D2 NO REALIZATION" in e for e in errors))
        self.assertTrue(any("D3 WEAK" in e or "D3 NOT FINAL" in e for e in errors))
    
    def test_setup_requirements(self):
        """Test that setup sentence needs time/place/urgency"""
        artifact = {
            "paragraph": (
                "Sarah wants to solve a case. "  # Missing time/place/urgency
                "When her partner dies, she is forced to work alone. "
                "After learning the truth, she realizes she must change tactics. "
                "When the final confrontation arrives, she must face the villain. "
                "In the end, she wins."
            ),
            "moral_premise": "People succeed when they persist."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("SETUP MISSING TIME" in e for e in errors))
        self.assertTrue(any("SETUP MISSING PLACE" in e for e in errors))
        self.assertTrue(any("SETUP NO URGENCY" in e for e in errors))
    
    def test_moral_premise_format(self):
        """Test that moral premise must follow specific format"""
        # Wrong format
        artifact = {
            "paragraph": "S1. S2. S3. S4. S5.",
            "moral_premise": "Good beats evil."  # Wrong format
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID MORAL PREMISE" in e for e in errors))
        
        # Correct format
        artifact = {
            "paragraph": "S1. S2. S3. S4. S5.",
            "moral_premise": "People succeed when they choose courage, and they fail when they choose fear."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        # May have other errors but moral premise should be OK
        self.assertFalse(any("INVALID MORAL PREMISE" in e for e in errors))
    
    def test_moral_pivot_in_disaster_2(self):
        """Test that Disaster 2 must show the moral pivot"""
        artifact = {
            "paragraph": (
                "In Seattle, Sarah must solve the case before midnight. "
                "When her partner dies, she is forced to continue alone. "
                "Something bad happens to Sarah but she keeps going. "  # No pivot shown
                "When the deadline arrives, she must confront the villain. "
                "She wins the fight."
            ),
            "moral_premise": "People succeed when they trust others, and they fail when they work alone."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("NO MORAL PIVOT" in e for e in errors))
        self.assertTrue(any("D2 NO REALIZATION" in e for e in errors))
    
    def test_resolution_requirements(self):
        """Test that resolution needs concrete outcome"""
        artifact = {
            "paragraph": (
                "Setup sentence with urgency in Seattle now. "
                "D1 forces commitment. "
                "D2 drives realization and new approach. "
                "D3 forces final confrontation. "
                "Something happens at the end."  # Vague ending
            ),
            "moral_premise": "People succeed when they persist, and fail when they quit."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("VAGUE ENDING" in e for e in errors))
        self.assertTrue(any("NO SHOWDOWN" in e for e in errors))
    
    def test_causality_check(self):
        """Test that coincidences are flagged"""
        artifact = {
            "paragraph": (
                "In Seattle, Sarah must solve the case today. "
                "Suddenly her partner is killed. "  # Coincidence marker
                "Out of nowhere she discovers the truth. "  # Coincidence marker
                "By chance the villain appears. "  # Coincidence marker
                "She wins."
            ),
            "moral_premise": "People succeed when they persist, and fail when they quit."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("COINCIDENCE" in e for e in errors))
        self.assertTrue(artifact['causality_check']['has_coincidence'])
        self.assertFalse(artifact['causality_check']['causal_chain'])
    
    def test_disaster_classification(self):
        """Test that disasters are properly classified"""
        artifact = {
            "paragraph": (
                "Setup. "
                "When Sarah discovers the betrayal, she is forced to act. "  # revelation
                "After her partner dies, she realizes she must work alone. "  # loss
                "When the deadline expires, she must face the final battle. "  # deadline
                "She wins."
            ),
            "moral_premise": "People succeed when they persist, and fail when they quit."
        }
        
        is_valid, errors = self.validator.validate(artifact)
        
        self.assertEqual(artifact['disasters']['d1_type'], 'revelation')
        self.assertEqual(artifact['disasters']['d2_type'], 'loss')
        self.assertEqual(artifact['disasters']['d3_type'], 'deadline')
    
    def test_sentence_parsing(self):
        """Test that sentences are correctly parsed"""
        paragraph = "First sentence. Second one! Third one? Fourth. Fifth."
        sentences = self.validator.parse_sentences(paragraph)
        
        self.assertEqual(len(sentences['all']), 5)
        self.assertEqual(sentences['setup'], "First sentence.")
        self.assertEqual(sentences['disaster_1'], "Second one!")
        self.assertEqual(sentences['disaster_2'], "Third one?")
        self.assertEqual(sentences['disaster_3'], "Fourth.")
        self.assertEqual(sentences['resolution'], "Fifth.")

class TestStep2Prompt(unittest.TestCase):
    """Test Step 2 prompt generation"""
    
    def setUp(self):
        self.prompt_gen = Step2Prompt()
        self.step_0_artifact = {
            "category": "Psychological Thriller",
            "story_kind": "Cat and mouse with unreliable narrator.",
            "audience_delight": "Mind games, plot twists, shocking reveals."
        }
        self.step_1_artifact = {
            "logline": "Sarah, a therapist, must prove her patient innocent before he's executed."
        }
    
    def test_main_prompt_generation(self):
        """Test that main prompts are generated correctly"""
        prompt_data = self.prompt_gen.generate_prompt(
            self.step_0_artifact,
            self.step_1_artifact
        )
        
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        
        # Check system prompt
        self.assertIn("EXACTLY FIVE SENTENCES", prompt_data["system"])
        self.assertIn("DISASTER", prompt_data["system"])
        
        # Check user prompt includes context
        self.assertIn("Psychological Thriller", prompt_data["user"])
        self.assertIn("Sarah, a therapist", prompt_data["user"])
        self.assertIn("SENTENCE 1 - SETUP", prompt_data["user"])
        self.assertIn("SENTENCE 2 - DISASTER #1", prompt_data["user"])
        self.assertIn("MORAL PREMISE", prompt_data["user"])
    
    def test_disaster_brainstorm_prompt(self):
        """Test disaster brainstorming prompt"""
        prompt_data = self.prompt_gen.generate_disaster_brainstorm(
            self.step_0_artifact,
            self.step_1_artifact
        )
        
        self.assertIn("8-10 possible story disasters", prompt_data["user"])
        self.assertIn("TYPE:", prompt_data["user"])
        self.assertIn("FORCING MECHANISM", prompt_data["user"])
    
    def test_revision_prompt(self):
        """Test revision prompt generation"""
        current_paragraph = "Bad paragraph with only 3 sentences. Missing disasters. No moral pivot shown."
        current_moral = "Wrong format moral."
        errors = [
            "WRONG SENTENCE COUNT: Must be exactly 5 sentences, found 3",
            "D1 NOT FORCING: Disaster 1 must use forcing language",
            "NO MORAL PIVOT: Sentence 3 must explicitly show the FALSE→TRUE shift"
        ]
        
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current_paragraph,
            current_moral,
            errors,
            self.step_0_artifact,
            self.step_1_artifact
        )
        
        self.assertIn("FIX this paragraph", prompt_data["user"])
        self.assertIn("WRONG SENTENCE COUNT", prompt_data["user"])
        self.assertIn("Split or combine to EXACTLY 5 sentences", prompt_data["user"])
        self.assertIn("EXPLICITLY show shift from false to true belief", prompt_data["user"])
    
    def test_moral_premise_prompt(self):
        """Test moral premise generation prompt"""
        paragraph = "Five sentences about a story."
        
        prompt_data = self.prompt_gen.generate_moral_premise_prompt(
            paragraph,
            self.step_0_artifact
        )
        
        self.assertIn("People succeed when they", prompt_data["user"])
        self.assertIn("TRUE BELIEF", prompt_data["user"])
        self.assertIn("FALSE BELIEF", prompt_data["user"])
        self.assertIn("Psychological Thriller", prompt_data["user"])

class TestStep2Execution(unittest.TestCase):
    """Test Step 2 execution and file operations"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.step2 = Step2OneParagraphSummary(self.test_dir)
        self.step_0_artifact = {
            "category": "Romantic Suspense",
            "story_kind": "Enemies to lovers with conspiracy.",
            "audience_delight": "Sexual tension, plot twists, HEA.",
            "metadata": {
                "project_id": "test-123",
                "step": 0,
                "version": "1.0.0"
            }
        }
        self.step_1_artifact = {
            "logline": "Agent Maya must capture rogue spy Alex before he sells state secrets.",
            "word_count": 11,
            "lead_count": 2,
            "metadata": {
                "project_id": "test-123",
                "step": 1,
                "version": "1.0.0"
            }
        }
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_metadata_generation(self):
        """Test that metadata is properly generated"""
        content = {
            "paragraph": "Five sentences.",
            "moral_premise": "A moral premise."
        }
        model_config = {"model_name": "test-model", "temperature": 0.3}
        
        artifact = self.step2.add_metadata(
            content, "test-123", "hash123", model_config, "upstream123"
        )
        
        self.assertEqual(artifact["metadata"]["step"], 2)
        self.assertEqual(artifact["metadata"]["project_id"], "test-123")
        self.assertEqual(artifact["metadata"]["hash_upstream"], "upstream123")
        self.assertIn("created_at", artifact["metadata"])
    
    def test_artifact_saving(self):
        """Test that artifacts are saved correctly"""
        artifact = {
            "paragraph": "S1. S2. S3. S4. S5.",
            "moral_premise": "People succeed when they trust, and fail when they doubt.",
            "sentence_count": 5,
            "sentences": {
                "setup": "S1.",
                "disaster_1": "S2.",
                "disaster_2": "S3.",
                "disaster_3": "S4.",
                "resolution": "S5."
            },
            "disasters": {
                "d1_present": True,
                "d2_present": True,
                "d3_present": True,
                "d1_type": "betrayal",
                "d2_type": "revelation",
                "d3_type": "deadline"
            },
            "metadata": {
                "project_id": "test-123",
                "step": 2,
                "version": "1.0.0",
                "created_at": "2024-01-01T00:00:00",
                "hash_upstream": "abc123"
            }
        }
        
        save_path = self.step2.save_artifact(artifact, "test-123")
        
        # Check main JSON file
        self.assertTrue(save_path.exists())
        with open(save_path, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["paragraph"], artifact["paragraph"])
        self.assertEqual(loaded["moral_premise"], artifact["moral_premise"])
        
        # Check moral premise separate file
        moral_path = save_path.parent / "moral_premise.json"
        self.assertTrue(moral_path.exists())
        with open(moral_path, 'r') as f:
            moral_data = json.load(f)
        self.assertEqual(moral_data["moral_premise"], artifact["moral_premise"])
        
        # Check human-readable file
        txt_path = save_path.parent / "step_2_one_paragraph_summary.txt"
        self.assertTrue(txt_path.exists())
        with open(txt_path, 'r') as f:
            content = f.read()
        self.assertIn("COMPLETE PARAGRAPH:", content)
        self.assertIn("MORAL PREMISE:", content)
        self.assertIn("SENTENCE BREAKDOWN:", content)
        self.assertIn("DISASTER VALIDATION:", content)
    
    def test_validation_only(self):
        """Test validation without execution"""
        # Valid paragraph
        valid = {
            "paragraph": (
                "In NYC today, Maya must capture Alex before midnight. "
                "When her handler betrays her location, she is forced to go dark. "
                "After discovering Alex was framed, she realizes the agency is corrupt and must work with him. "
                "When the real mole activates a kill order on both, they must fight together or die. "
                "In the final confrontation, Maya exposes the mole but loses her career."
            ),
            "moral_premise": "People succeed when they question authority, and fail when they blindly follow orders."
        }
        
        is_valid, message = self.step2.validate_only(valid)
        self.assertTrue(is_valid)
        self.assertIn("passes all checks", message)
        
        # Invalid paragraph
        invalid = {
            "paragraph": "Too few sentences. Only three. Not enough.",
            "moral_premise": "Bad format."
        }
        
        is_valid, message = self.step2.validate_only(invalid)
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", message)

if __name__ == "__main__":
    unittest.main()