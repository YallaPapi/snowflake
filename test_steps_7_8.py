#!/usr/bin/env python3
"""
Test Steps 7 and 8 with comprehensive generation
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.steps.step_7_character_bibles import Step7CharacterBibles
from src.pipeline.steps.step_8_scene_list import Step8SceneList
from src.ai.model_selector import ModelSelector

def load_artifact(project_id: str, step: int) -> dict:
    """Load an artifact from a previous step"""
    artifact_dir = Path("artifacts") / project_id
    
    if step == 5:
        path = artifact_dir / "step_5_character_synopses.json"
    elif step == 6:
        path = artifact_dir / "step_6_long_synopsis.json"
    elif step == 7:
        path = artifact_dir / "step_7_character_bibles.json"
    else:
        raise ValueError(f"Unknown step: {step}")
    
    if not path.exists():
        print(f"ERROR: {path} not found")
        return None
    
    with open(path, "r") as f:
        return json.load(f)

def create_test_step5_artifact():
    """Create a test Step 5 artifact if needed"""
    return {
        "characters": [
            {
                "name": "Sarah Chen",
                "role": "Protagonist",
                "synopsis": "Sarah Chen is a 32-year-old investigative journalist haunted by her failure to expose a corruption scandal that led to her mentor's death. She masks her guilt with relentless ambition and a sharp wit, but underneath lies deep vulnerability. Her journey involves learning to trust again while uncovering a conspiracy that threatens everything she believes in. She must overcome her fear of failure and accept that perfection isn't possible - sometimes doing the right thing means taking imperfect action."
            },
            {
                "name": "Marcus Vale",
                "role": "Antagonist",
                "synopsis": "Marcus Vale is a 45-year-old tech billionaire who believes humanity's survival depends on controlled evolution through his AI systems. Orphaned at age seven, he learned that power is the only real security. He genuinely believes his authoritarian vision will save humanity from itself. His fatal flaw is his inability to see that his need for control stems from childhood trauma, not logic. He represents the danger of unchecked power wielded by those who confuse their wounds with wisdom."
            },
            {
                "name": "Dr. Amelia Ross",
                "role": "Major Supporting",
                "synopsis": "Dr. Amelia Ross is a 38-year-old AI researcher caught between her loyalty to Marcus (her former mentor) and her growing horror at his methods. She struggles with the weight of her contributions to potentially harmful technology. Her arc involves finding the courage to stand against someone she once admired, learning that true loyalty sometimes means opposition."
            }
        ]
    }

def create_test_step6_artifact():
    """Create a test Step 6 artifact if needed"""
    return {
        "long_synopsis": """ACT ONE - THE SETUP
Sarah Chen, an investigative journalist in San Francisco, receives an anonymous tip about strange deaths linked to NeuralLink, a revolutionary AI therapy system created by tech billionaire Marcus Vale. Still haunted by her failure to prevent her mentor's death two years ago, Sarah initially dismisses the tip. But when her source turns up dead in an apparent suicide, she realizes she can't make the same mistake twice.

Sarah begins investigating NeuralLink, discovering it's more than therapeutic software - it's actively rewriting users' neural pathways. She infiltrates Vale's company, posing as a tech journalist writing a puff piece. There she meets Dr. Amelia Ross, the brilliant but troubled lead researcher who seems uncomfortable with her own creation.

As Sarah digs deeper, she uncovers a pattern: NeuralLink users are becoming mysteriously compliant, losing their ability to resist Vale's vision of a 'optimized society.' Her investigation attracts Vale's attention, who initially tries to recruit her, seeing her skills as valuable. When she refuses, the first disaster strikes - Vale uses NeuralLink to manipulate her editor, who fires her and discredits her publicly. Sarah loses her platform and credibility overnight.

ACT TWO - THE CONFRONTATION
Stripped of her official resources, Sarah goes underground, aided by a group of NeuralLink victims' families. She discovers Vale's true plan: to make NeuralLink mandatory through government contracts, creating a society where dissent is neurologically impossible. Dr. Ross, wrestling with guilt, secretly provides Sarah with evidence, but maintains her position to avoid suspicion.

Sarah attempts to expose Vale through alternative media, but he's always one step ahead, using NeuralLink's predictive algorithms to anticipate her moves. The second disaster occurs at the midpoint when Vale discovers Ross is helping Sarah. He doesn't fire Ross - instead, he forces her to undergo an experimental NeuralLink treatment, turning her into his most devoted supporter. Sarah watches her only ally inside become her enemy, realizing the true horror of Vale's technology.

Desperate, Sarah infiltrates a NeuralLink treatment center to gather irrefutable evidence. She discovers the system's weakness: it requires voluntary initial consent to work. But Vale is working on an airborne version that would eliminate even this protection. Time is running out.

Sarah orchestrates a live broadcast from inside Vale's headquarters, planning to expose everything. But the third disaster strikes when Vale reveals he's already released the airborne version in the building. Sarah and everyone present have been infected. In 48 hours, they'll all be compliant. Vale offers Sarah a choice: submit now and become his partner in shaping the new world, or resist and lose herself completely.

ACT THREE - THE RESOLUTION
Sarah realizes the only way to stop Vale is to use his own system against him. She pretends to accept his offer, gaining access to NeuralLink's core. With her remaining free will, she introduces a hidden protocol that Dr. Ross had built as a safeguard before her conversion - a kill switch that will destroy NeuralLink completely, but will also cause temporary neural damage to all current users, including herself.

As the compliance begins taking hold, Sarah struggles to maintain enough independence to activate the protocol. In a climactic confrontation, she must overcome not just Vale, but her own growing urge to submit. She succeeds in triggering the kill switch moments before losing herself completely.

The aftermath is chaotic. Thousands of NeuralLink users experience temporary disorientation, but recover their free will. Vale's empire crumbles as evidence of his manipulation floods out. Dr. Ross, freed from the system's influence, faces the weight of her actions. Sarah, neurologically damaged but free, must rebuild her life and career from scratch.

In the denouement, we see Sarah six months later, her cognitive functions slowly recovering. She's returned to journalism, no longer seeking perfection but focusing on truth. She's learned that redemption isn't about never failing, but about continuing to fight despite past failures. Vale is imprisoned, but unrepentant, still believing his vision would have saved humanity. Dr. Ross leads the effort to help NeuralLink victims recover, seeking her own redemption. The story ends with Sarah receiving another anonymous tip - suggesting Vale's technology has been acquired by another corporation. She smiles grimly and begins investigating, knowing the fight for human autonomy never truly ends.""",
        "target_word_count": 90000
    }

def test_step_7():
    """Test Step 7 Character Bibles generation"""
    print("\n" + "="*60)
    print("TESTING STEP 7: CHARACTER BIBLES")
    print("="*60)
    
    # Try to load existing Step 5 artifact
    project_id = "test_steps_7_8"
    step5_artifact = load_artifact(project_id, 5)
    
    if not step5_artifact:
        print("Creating test Step 5 artifact...")
        step5_artifact = create_test_step5_artifact()
    
    # Initialize Step 7
    step7 = Step7CharacterBibles()
    
    # Get optimal model config
    model_config = ModelSelector.get_model_config(step=7)
    print(f"Using model: {model_config.get('model_name', 'default')}")
    
    # Execute Step 7
    print("\nGenerating character bibles...")
    success, artifact, message = step7.execute(
        step5_artifact=step5_artifact,
        project_id=project_id,
        model_config=model_config
    )
    
    if success:
        print(f"SUCCESS: {message}")
        print(f"\nGenerated {len(artifact.get('bibles', []))} character bibles")
        
        # Show summary of each bible
        for bible in artifact.get('bibles', []):
            name = bible.get('name', 'Unknown')
            print(f"\n{name}:")
            
            # Count filled fields
            total_fields = 0
            filled_fields = 0
            
            for section in ['physical', 'personality', 'environment', 'psychology']:
                section_data = bible.get(section, {})
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        total_fields += 1
                        if value and str(value).strip():
                            filled_fields += 1
                elif section_data:
                    total_fields += 1
                    filled_fields += 1
            
            completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            print(f"  - Completeness: {completeness:.0f}%")
            print(f"  - Voice notes: {len(bible.get('voice_notes', []))}")
            
            if bible.get('psychology'):
                psych = bible['psychology']
                if isinstance(psych, dict):
                    wound = psych.get('wound') or psych.get('backstory_wound', '')
                    if wound:
                        print(f"  - Core wound: {wound[:50]}...")
        
        return artifact
    else:
        print(f"FAILED: {message}")
        return None

def test_step_8(step6_artifact=None, step7_artifact=None):
    """Test Step 8 Scene List generation"""
    print("\n" + "="*60)
    print("TESTING STEP 8: SCENE LIST")
    print("="*60)
    
    project_id = "test_steps_7_8"
    
    # Load or create test artifacts
    if not step6_artifact:
        step6_artifact = load_artifact(project_id, 6)
        if not step6_artifact:
            print("Creating test Step 6 artifact...")
            step6_artifact = create_test_step6_artifact()
    
    if not step7_artifact:
        step7_artifact = load_artifact(project_id, 7)
        if not step7_artifact:
            print("Creating test Step 7 artifact...")
            step7_artifact = test_step_7()
            if not step7_artifact:
                print("ERROR: Could not create Step 7 artifact")
                return None
    
    # Initialize Step 8
    step8 = Step8SceneList()
    
    # Get optimal model config
    model_config = ModelSelector.get_model_config(step=8)
    print(f"Using model: {model_config.get('model_name', 'default')}")
    
    # Execute Step 8
    print("\nGenerating scene list...")
    success, artifact, message = step8.execute(
        step6_artifact=step6_artifact,
        step7_artifact=step7_artifact,
        project_id=project_id,
        model_config=model_config
    )
    
    if success:
        print(f"SUCCESS: {message}")
        
        scenes = artifact.get('scenes', [])
        print(f"\nGenerated {len(scenes)} scenes")
        print(f"Total word target: {artifact.get('total_word_target', 0):,} words")
        
        # Check disaster anchors
        disasters = artifact.get('disaster_anchors', {})
        print(f"\nDisaster anchors:")
        print(f"  - D1: Scene {disasters.get('d1_scene', 'Not set')}")
        print(f"  - D2: Scene {disasters.get('d2_scene', 'Not set')}")
        print(f"  - D3: Scene {disasters.get('d3_scene', 'Not set')}")
        
        # Check POV distribution
        pov_dist = artifact.get('pov_distribution', {})
        print(f"\nPOV Distribution:")
        for pov, count in pov_dist.items():
            print(f"  - {pov}: {count} scenes")
        
        # Check scene types
        proactive = sum(1 for s in scenes if s.get('type') == 'Proactive')
        reactive = sum(1 for s in scenes if s.get('type') == 'Reactive')
        print(f"\nScene Types:")
        print(f"  - Proactive: {proactive}")
        print(f"  - Reactive: {reactive}")
        
        # Check conflict presence
        conflict_check = artifact.get('conflict_validation', {})
        if conflict_check.get('all_have_conflict'):
            print(f"\nOK: All scenes have conflict")
        else:
            without = conflict_check.get('scenes_without_conflict', [])
            print(f"\nERROR: Scenes without conflict: {without}")
        
        # Check CSV export
        csv_path = Path("artifacts") / project_id / "step_8_scenes.csv"
        if csv_path.exists():
            print(f"\nOK: CSV exported to: {csv_path}")
        
        return artifact
    else:
        print(f"FAILED: {message}")
        return None

def main():
    """Run tests for Steps 7 and 8"""
    print("TESTING STEPS 7 AND 8 - CHARACTER BIBLES AND SCENE LIST")
    print("="*60)
    
    # Test Step 7
    step7_artifact = test_step_7()
    
    if step7_artifact:
        # Test Step 8
        step8_artifact = test_step_8(step7_artifact=step7_artifact)
        
        if step8_artifact:
            print("\n" + "="*60)
            print("ALL TESTS COMPLETED SUCCESSFULLY")
            print("="*60)
            return True
    
    print("\n" + "="*60)
    print("TESTS FAILED - SEE ERRORS ABOVE")
    print("="*60)
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)