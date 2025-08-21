"""
Direct Novel Completion - Steps 7-10
Directly calls the step modules to complete the novel
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def complete_novel_direct():
    """Complete the novel using direct step execution"""
    
    # Use the existing project
    project_dir = Path("artifacts/code_of_deception_20250821_212841")
    
    if not project_dir.exists():
        logger.error(f"Project directory not found: {project_dir}")
        return None
    
    logger.info(f"Loading existing artifacts from {project_dir}")
    
    # Load existing artifacts
    artifacts = {}
    for file in project_dir.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            artifacts[file.stem] = json.load(f)
    
    # Also load markdown files
    for file in project_dir.glob("*.md"):
        with open(file, 'r', encoding='utf-8') as f:
            artifacts[file.stem + "_text"] = f.read()
    
    # Import step modules
    from src.pipeline.steps.step_7_character_bibles import Step7CharacterBibles
    from src.pipeline.steps.step_8_scene_list import Step8SceneList
    from src.pipeline.steps.step_9_scene_briefs_v2 import Step9SceneBriefsV2
    from src.pipeline.steps.step_10_first_draft import Step10FirstDraft
    
    # ========================================
    # STEP 7: CHARACTER BIBLES
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("STEP 7: GENERATING CHARACTER BIBLES")
    logger.info("="*80)
    
    try:
        step7 = Step7CharacterBibles(str(project_dir))
        
        # Load required artifacts
        character_summaries = artifacts.get("step_3_character_summaries", {})
        character_synopses = artifacts.get("step_5_character_synopses", {})
        
        # Execute Step 7
        logger.info("Generating character bibles...")
        character_bibles = step7.execute(
            character_summaries=character_summaries,
            character_synopses=character_synopses
        )
        
        logger.info(f"✓ Step 7 complete: {len(character_bibles.get('characters', []))} character bibles")
        artifacts["step_7_character_bibles"] = character_bibles
        
    except Exception as e:
        logger.error(f"Step 7 error: {e}")
        # Use minimal character bibles
        character_bibles = artifacts.get("step_7_character_bibles", {
            "characters": [
                {"name": "Sarah Chen", "role": "protagonist"},
                {"name": "Marcus Vale", "role": "antagonist"}
            ]
        })
    
    # ========================================
    # STEP 8: SCENE LIST
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("STEP 8: GENERATING SCENE LIST")
    logger.info("="*80)
    
    try:
        step8 = Step8SceneList(str(project_dir))
        
        # Execute Step 8
        logger.info("Generating scene list...")
        scene_list = step8.execute(
            long_synopsis=artifacts.get("step_6_long_synopsis_text", ""),
            character_bibles=character_bibles,
            one_paragraph_summary=artifacts.get("step_2_one_paragraph_summary", {})
        )
        
        logger.info(f"✓ Step 8 complete: {len(scene_list.get('scenes', []))} scenes")
        artifacts["step_8_scene_list"] = scene_list
        
    except Exception as e:
        logger.error(f"Step 8 error: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 9: SCENE BRIEFS
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("STEP 9: GENERATING SCENE BRIEFS")
    logger.info("="*80)
    
    try:
        step9 = Step9SceneBriefsV2(str(project_dir))
        
        # Execute Step 9
        logger.info("Generating scene briefs...")
        scene_briefs = step9.execute(
            scene_list=scene_list,
            character_bibles=character_bibles,
            long_synopsis=artifacts.get("step_6_long_synopsis_text", "")
        )
        
        logger.info(f"✓ Step 9 complete: {len(scene_briefs.get('briefs', []))} briefs")
        artifacts["step_9_scene_briefs"] = scene_briefs
        
    except Exception as e:
        logger.error(f"Step 9 error: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 10: WRITE THE NOVEL
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("STEP 10: WRITING THE COMPLETE NOVEL")
    logger.info("="*80)
    
    try:
        step10 = Step10FirstDraft(str(project_dir))
        
        logger.info("Writing complete manuscript...")
        manuscript = step10.execute(
            scene_list=scene_list,
            scene_briefs=scene_briefs,
            character_bibles=character_bibles,
            long_synopsis=artifacts.get("step_6_long_synopsis_text", ""),
            one_sentence_summary=artifacts.get("step_1_one_sentence_summary", {}),
            target_words=50000
        )
        
        # Save the manuscript
        output_file = project_dir / "step_10_manuscript.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(manuscript)
        
        word_count = len(manuscript.split())
        
        logger.info("\n" + "="*80)
        logger.info("🎉 NOVEL GENERATION COMPLETE! 🎉")
        logger.info(f"📖 Title: Code of Deception")
        logger.info(f"📝 Word Count: {word_count}")
        logger.info(f"📁 Location: {output_file}")
        logger.info("="*80)
        
        return output_file
        
    except Exception as e:
        logger.error(f"Step 10 error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        logger.error("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        sys.exit(1)
    
    logger.info("Starting direct novel completion...")
    result = complete_novel_direct()
    
    if result:
        logger.info(f"\n✅ SUCCESS! Novel at: {result}")
    else:
        logger.error("\n❌ Failed to complete novel")