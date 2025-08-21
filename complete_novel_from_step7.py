"""
Complete Novel Generation from Step 7
Continues from existing artifacts and generates the complete 50,000 word manuscript
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.orchestration.orchestrator import SnowflakeOrchestrator
from src.orchestration.pipeline import SnowflakePipeline
from src.agents.character_agent import CharacterAgent
from src.agents.outline_agent import OutlineAgent
from src.agents.scene_agent import SceneAgent
from src.agents.draft_agent import DraftAgent
from src.validation.validator import SnowflakeValidator
from src.export.exporter import Exporter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_existing_artifacts(project_dir: Path):
    """Load artifacts from Steps 0-6"""
    artifacts = {}
    
    # Load all existing artifacts
    for file in project_dir.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            artifacts[file.stem] = json.load(f)
    
    # Also load markdown files
    for file in project_dir.glob("*.md"):
        with open(file, 'r', encoding='utf-8') as f:
            artifacts[file.stem] = f.read()
    
    return artifacts

def continue_from_step_7():
    """Continue generation from Step 7 through Step 10"""
    
    # Use the existing project
    project_dir = Path("artifacts/code_of_deception_20250821_212841")
    
    if not project_dir.exists():
        logger.error(f"Project directory not found: {project_dir}")
        return
    
    logger.info(f"Loading existing artifacts from {project_dir}")
    artifacts = load_existing_artifacts(project_dir)
    
    # Load project data
    project_data = artifacts.get("project", {})
    project_id = project_data.get("project_id", "code_of_deception_continued")
    
    # Initialize agents
    logger.info("Initializing agents...")
    character_agent = CharacterAgent()
    outline_agent = OutlineAgent()
    scene_agent = SceneAgent()
    draft_agent = DraftAgent()
    validator = SnowflakeValidator()
    
    # Step 7: Character Bibles
    logger.info("\n" + "="*80)
    logger.info("STEP 7: CHARACTER BIBLES")
    logger.info("="*80)
    
    try:
        # Load character summaries and synopses
        character_summaries = artifacts.get("step_3_character_summaries", {})
        character_synopses = artifacts.get("step_5_character_synopses", {})
        
        # Generate character bibles
        character_bibles = character_agent.generate_character_bibles(
            character_summaries=character_summaries,
            character_synopses=character_synopses,
            long_synopsis=artifacts.get("step_6_long_synopsis", "")
        )
        
        # Save character bibles
        output_file = project_dir / "step_7_character_bibles.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(character_bibles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Step 7 complete: {output_file}")
        artifacts["step_7_character_bibles"] = character_bibles
        
    except Exception as e:
        logger.error(f"Step 7 failed: {e}")
        logger.info("Continuing with minimal character bibles...")
        character_bibles = {"characters": []}
        artifacts["step_7_character_bibles"] = character_bibles
    
    # Step 8: Scene List (Generate 70-80 scenes for 50,000 words)
    logger.info("\n" + "="*80)
    logger.info("STEP 8: SCENE LIST (70-80 scenes)")
    logger.info("="*80)
    
    try:
        # Generate comprehensive scene list
        scene_list = outline_agent.generate_scene_list(
            long_synopsis=artifacts.get("step_6_long_synopsis", ""),
            character_bibles=character_bibles,
            one_paragraph=artifacts.get("step_2_one_paragraph_summary", {}),
            target_scenes=75  # For ~50,000 words
        )
        
        # Save scene list
        output_file = project_dir / "step_8_scene_list.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scene_list, f, indent=2, ensure_ascii=False)
        
        # Also save as CSV
        csv_file = project_dir / "step_8_scene_list.csv"
        import csv
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'index', 'chapter', 'type', 'pov', 'summary', 
                'time', 'location', 'word_target', 'status'
            ])
            writer.writeheader()
            for scene in scene_list.get('scenes', []):
                writer.writerow(scene)
        
        logger.info(f"✓ Step 8 complete: {len(scene_list.get('scenes', []))} scenes generated")
        artifacts["step_8_scene_list"] = scene_list
        
    except Exception as e:
        logger.error(f"Step 8 failed: {e}")
        return
    
    # Step 9: Scene Briefs for ALL scenes
    logger.info("\n" + "="*80)
    logger.info("STEP 9: SCENE BRIEFS (All scenes)")
    logger.info("="*80)
    
    try:
        scene_briefs = []
        scenes = scene_list.get('scenes', [])
        
        for i, scene in enumerate(scenes):
            logger.info(f"Generating brief for scene {i+1}/{len(scenes)}: {scene.get('summary', '')[:50]}...")
            
            brief = scene_agent.generate_scene_brief(
                scene_info=scene,
                character_bibles=character_bibles,
                long_synopsis=artifacts.get("step_6_long_synopsis", ""),
                previous_scenes=scene_briefs  # Pass previously generated briefs for continuity
            )
            
            scene_briefs.append(brief)
            
            # Save progress periodically
            if (i + 1) % 10 == 0:
                temp_file = project_dir / f"step_9_scene_briefs_progress_{i+1}.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump({"briefs": scene_briefs}, f, indent=2, ensure_ascii=False)
                logger.info(f"Progress saved: {i+1}/{len(scenes)} briefs complete")
        
        # Save all scene briefs
        output_file = project_dir / "step_9_scene_briefs.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"briefs": scene_briefs}, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Step 9 complete: {len(scene_briefs)} scene briefs generated")
        artifacts["step_9_scene_briefs"] = {"briefs": scene_briefs}
        
    except Exception as e:
        logger.error(f"Step 9 failed: {e}")
        return
    
    # Step 10: WRITE THE COMPLETE NOVEL (50,000 words)
    logger.info("\n" + "="*80)
    logger.info("STEP 10: WRITING COMPLETE NOVEL MANUSCRIPT (50,000 words)")
    logger.info("="*80)
    
    try:
        # Generate the complete manuscript
        manuscript_parts = []
        current_chapter = 1
        chapter_content = []
        total_words = 0
        
        for i, (scene, brief) in enumerate(zip(scenes, scene_briefs)):
            logger.info(f"\nWriting scene {i+1}/{len(scenes)}: {scene.get('summary', '')[:50]}...")
            
            # Generate prose for this scene
            scene_prose = draft_agent.write_scene(
                scene_brief=brief,
                scene_info=scene,
                character_bibles=character_bibles,
                previous_content="\n\n".join(chapter_content[-2:]) if chapter_content else "",  # Context from recent scenes
                target_words=scene.get('word_target', 700)  # Average 700 words per scene
            )
            
            # Check if we need to start a new chapter
            if scene.get('chapter', current_chapter) != current_chapter:
                # Save current chapter
                if chapter_content:
                    chapter_text = "\n\n".join(chapter_content)
                    manuscript_parts.append(f"# Chapter {current_chapter}\n\n{chapter_text}")
                    chapter_words = len(chapter_text.split())
                    total_words += chapter_words
                    logger.info(f"Chapter {current_chapter} complete: {chapter_words} words")
                
                # Start new chapter
                current_chapter = scene.get('chapter', current_chapter + 1)
                chapter_content = []
            
            chapter_content.append(scene_prose)
            
            # Save progress periodically
            if (i + 1) % 5 == 0:
                progress_file = project_dir / f"manuscript_progress_{i+1}_scenes.md"
                progress_text = "\n\n".join(manuscript_parts)
                if chapter_content:
                    progress_text += f"\n\n# Chapter {current_chapter}\n\n" + "\n\n".join(chapter_content)
                
                with open(progress_file, 'w', encoding='utf-8') as f:
                    f.write(progress_text)
                
                current_total = len(progress_text.split())
                logger.info(f"Progress: {i+1}/{len(scenes)} scenes, {current_total} words written")
        
        # Add final chapter
        if chapter_content:
            chapter_text = "\n\n".join(chapter_content)
            manuscript_parts.append(f"# Chapter {current_chapter}\n\n{chapter_text}")
            total_words += len(chapter_text.split())
        
        # Combine all parts into complete manuscript
        complete_manuscript = "\n\n".join(manuscript_parts)
        
        # Add title and metadata
        final_manuscript = f"""# Code of Deception

**A Techno-Thriller Novel**

By The Snowflake Engine

---

{complete_manuscript}

---

## The End

**Final Word Count: {len(complete_manuscript.split())} words**

*Generated by the Snowflake Novel Engine*
*Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save complete manuscript
        manuscript_file = project_dir / "step_10_manuscript.md"
        with open(manuscript_file, 'w', encoding='utf-8') as f:
            f.write(final_manuscript)
        
        logger.info(f"\n✓ STEP 10 COMPLETE!")
        logger.info(f"✓ NOVEL MANUSCRIPT GENERATED: {len(complete_manuscript.split())} words")
        logger.info(f"✓ Saved to: {manuscript_file}")
        
        # Export to DOCX
        try:
            logger.info("\nExporting to DOCX format...")
            exporter = Exporter(project_dir)
            docx_file = exporter.export_to_docx(final_manuscript, "Code of Deception")
            logger.info(f"✓ DOCX export complete: {docx_file}")
        except Exception as e:
            logger.error(f"DOCX export failed: {e}")
        
        # Update status
        status_file = project_dir / "status.json"
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        status['current_step'] = 10
        status['steps']['step_10'] = {
            'completed': True,
            'word_count': len(complete_manuscript.split()),
            'chapters': current_chapter,
            'scenes': len(scenes)
        }
        status['pipeline_complete'] = True
        status['completed_at'] = datetime.now().isoformat()
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info("\n" + "="*80)
        logger.info("🎉 NOVEL GENERATION COMPLETE! 🎉")
        logger.info(f"📖 Title: Code of Deception")
        logger.info(f"📝 Word Count: {len(complete_manuscript.split())} words")
        logger.info(f"📚 Chapters: {current_chapter}")
        logger.info(f"🎬 Scenes: {len(scenes)}")
        logger.info(f"📁 Location: {manuscript_file}")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"Step 10 failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    return manuscript_file

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        logger.error("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    logger.info("Starting novel completion from Step 7...")
    result = continue_from_step_7()
    
    if result:
        logger.info(f"\n✅ SUCCESS! Novel manuscript saved to: {result}")
    else:
        logger.error("\n❌ Failed to complete novel generation")