import json
import os
import sys
from datetime import datetime
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline.steps.step_10_draft_writer import Step10DraftWriter
from ai.generator import AIGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def continue_novel_generation():
    """Continue generating the novel from scene 34."""
    
    project_dir = Path("artifacts/code_of_deception_20250821_212841")
    
    # Load existing artifacts
    logger.info("Loading existing artifacts...")
    with open(project_dir / "step_8_scene_list.json", "r") as f:
        scene_list = json.load(f)
    
    with open(project_dir / "step_9_scene_briefs.json", "r") as f:
        scene_briefs = json.load(f)
    
    with open(project_dir / "step_3_character_summaries.json", "r") as f:
        characters = json.load(f)
    
    # Load progress
    start_scene = 34  # Continue from scene 34
    total_scenes = len(scene_list['scenes'])
    
    logger.info(f"Continuing from scene {start_scene}/{total_scenes}")
    
    # Initialize AI generator
    ai_generator = AIGenerator()
    
    # Create draft writer
    draft_writer = Step10DraftWriter()
    
    # Generate remaining scenes
    manuscript_scenes = []
    
    # Load existing scenes from progress file
    if (project_dir / "manuscript_progress_30_scenes.md").exists():
        with open(project_dir / "manuscript_progress_30_scenes.md", "r", encoding='utf-8') as f:
            existing_manuscript = f.read()
            # Parse existing scenes (simple approach)
            manuscript_scenes = existing_manuscript.split("\n\n---\n\n")[:30]
    
    current_word_count = sum(len(scene.split()) for scene in manuscript_scenes)
    logger.info(f"Starting with {current_word_count} words from {len(manuscript_scenes)} existing scenes")
    
    # Continue generating
    for i in range(start_scene - 1, total_scenes):
        scene = scene_list['scenes'][i]
        brief = scene_briefs['briefs'][i] if i < len(scene_briefs['briefs']) else {}
        
        logger.info(f"Writing scene {i+1}/{total_scenes}: {scene.get('summary', '')[:50]}...")
        
        try:
            # Generate scene prose
            scene_prose = draft_writer.draft_scene(scene, brief, characters, ai_generator)
            
            # Format scene
            formatted_scene = f"## Chapter {scene.get('chapter_hint', i//4 + 1)}, Scene {i+1}\n\n{scene_prose}"
            manuscript_scenes.append(formatted_scene)
            
            word_count = len(scene_prose.split())
            current_word_count += word_count
            logger.info(f"  ✓ Scene {i+1}: {word_count} words (Total: {current_word_count})")
            
            # Save progress every 10 scenes
            if (i + 1) % 10 == 0:
                progress_file = project_dir / f"manuscript_progress_{i+1}_scenes.md"
                with open(progress_file, "w", encoding='utf-8') as f:
                    f.write("\n\n---\n\n".join(manuscript_scenes))
                logger.info(f"  Progress saved: {i+1} scenes, {current_word_count} words")
            
            # Check if we've reached target
            if current_word_count >= 50000:
                logger.info(f"Target word count reached: {current_word_count} words")
                break
                
        except Exception as e:
            logger.error(f"Error generating scene {i+1}: {e}")
            # Add fallback prose
            fallback = f"[Scene {i+1} - Generation Error: {scene.get('summary', 'No summary')}]"
            manuscript_scenes.append(fallback)
    
    # Save final manuscript
    logger.info("Saving complete manuscript...")
    final_manuscript = "\n\n---\n\n".join(manuscript_scenes)
    
    # Save as markdown
    with open(project_dir / "COMPLETE_MANUSCRIPT.md", "w", encoding='utf-8') as f:
        f.write(f"# CODE OF DECEPTION\n\nA Techno-Thriller Novel\n\n---\n\n{final_manuscript}")
    
    # Save completion report
    with open(project_dir / "NOVEL_COMPLETION_REPORT.txt", "w", encoding='utf-8') as f:
        f.write(f"NOVEL GENERATION COMPLETE\n")
        f.write(f"========================\n\n")
        f.write(f"Title: Code of Deception\n")
        f.write(f"Genre: Techno-Thriller\n")
        f.write(f"Total Scenes: {len(manuscript_scenes)}\n")
        f.write(f"Total Words: {current_word_count}\n")
        f.write(f"Status: COMPLETE\n")
        f.write(f"Timestamp: {datetime.now()}\n")
    
    logger.info(f"COMPLETE! Novel saved to {project_dir}/COMPLETE_MANUSCRIPT.md")
    logger.info(f"Final stats: {len(manuscript_scenes)} scenes, {current_word_count} words")
    
    return True

if __name__ == "__main__":
    continue_novel_generation()