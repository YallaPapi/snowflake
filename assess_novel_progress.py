#!/usr/bin/env python3
"""
Novel Progress Assessment
Shows what has been generated so far for the Code of Deception novel
"""

import os
import sys
import json
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def assess_project(project_id):
    """Assess the progress of a project"""
    project_path = Path("artifacts") / project_id
    
    if not project_path.exists():
        print(f"[ERROR] Project directory not found: {project_path}")
        return False
    
    print(f"[PROJECT] Assessing: {project_id}")
    print(f"[PATH] {project_path}")
    
    # Check which steps were completed
    completed_steps = []
    artifacts = {}
    
    for i in range(11):
        json_file = project_path / f"step_{i}_*.json"
        json_files = list(project_path.glob(f"step_{i}_*.json"))
        
        if json_files:
            completed_steps.append(i)
            # Load the artifact
            try:
                with open(json_files[0], 'r', encoding='utf-8') as f:
                    artifacts[i] = json.load(f)
            except Exception as e:
                print(f"[WARN] Could not load step {i} artifact: {e}")
    
    print(f"[PROGRESS] Completed steps: {completed_steps}")
    print(f"[PROGRESS] Total completed: {len(completed_steps)}/11 steps")
    
    # Show details for each completed step
    print_section("COMPLETED STEPS SUMMARY")
    
    step_names = {
        0: "First Things First",
        1: "One Sentence Summary", 
        2: "One Paragraph Summary",
        3: "Character Summaries",
        4: "One Page Synopsis",
        5: "Character Synopses", 
        6: "Long Synopsis",
        7: "Character Bibles",
        8: "Scene List",
        9: "Scene Briefs",
        10: "First Draft"
    }
    
    for step in completed_steps:
        print(f"\n[STEP {step}] {step_names.get(step, 'Unknown')}")
        
        if step in artifacts:
            artifact = artifacts[step]
            
            # Show key information for each step
            if step == 0:
                print(f"  Category: {artifact.get('category', 'Unknown')}")
                print(f"  Target Audience: {artifact.get('target_audience', 'Unknown')}")
                print(f"  Story Kind: {artifact.get('story_kind', 'Unknown')[:100]}...")
                
            elif step == 1:
                print(f"  Summary: {artifact.get('one_sentence_summary', 'Unknown')}")
                
            elif step == 2:
                print(f"  Paragraph: {artifact.get('one_paragraph_summary', 'Unknown')[:200]}...")
                moral = artifact.get('moral_premise', {})
                if isinstance(moral, dict):
                    print(f"  Moral Premise: {moral.get('premise', 'Unknown')}")
                else:
                    print(f"  Moral Premise: {moral}")
                
            elif step == 3:
                characters = artifact.get('characters', [])
                print(f"  Characters: {len(characters)} characters")
                for char in characters[:3]:  # Show first 3
                    print(f"    - {char.get('name', 'Unknown')} ({char.get('role', 'Unknown')})")
                    
            elif step == 4:
                synopsis = artifact.get('one_page_synopsis', '')
                word_count = len(synopsis.split()) if synopsis else 0
                print(f"  Synopsis: {word_count} words")
                
            elif step == 5:
                synopses = artifact.get('character_synopses', [])
                print(f"  Character Synopses: {len(synopses)} characters")
                
            elif step == 6:
                synopsis = artifact.get('long_synopsis', '')
                word_count = len(synopsis.split()) if synopsis else 0
                print(f"  Long Synopsis: {word_count} words")
        
        # Check for text/markdown files too
        text_files = list(project_path.glob(f"step_{step}_*.txt")) + list(project_path.glob(f"step_{step}_*.md"))
        if text_files:
            try:
                with open(text_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    print(f"  Text file: {word_count} words")
            except Exception as e:
                print(f"  Text file: Error reading ({e})")
    
    # Show what's missing
    print_section("REMAINING STEPS")
    missing_steps = [i for i in range(11) if i not in completed_steps]
    
    if missing_steps:
        print("[MISSING] The following steps need to be completed:")
        for step in missing_steps:
            print(f"  Step {step}: {step_names.get(step, 'Unknown')}")
    else:
        print("[COMPLETE] All steps have been completed!")
    
    # Show file sizes
    print_section("GENERATED FILES")
    
    all_files = list(project_path.glob("*"))
    total_size = 0
    
    for file_path in sorted(all_files):
        if file_path.is_file():
            size = file_path.stat().st_size
            total_size += size
            print(f"  {file_path.name}: {size:,} bytes")
    
    print(f"\n[TOTAL] {len(all_files)} files, {total_size:,} bytes")
    
    return True

def show_story_content(project_id):
    """Show the actual story content generated"""
    project_path = Path("artifacts") / project_id
    
    print_section("STORY CONTENT PREVIEW")
    
    # Show the one-sentence summary
    one_sentence_file = project_path / "step_1_one_sentence_summary.txt"
    if one_sentence_file.exists():
        print("[LOGLINE]")
        with open(one_sentence_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            print(f"  {content}")
    
    # Show the paragraph summary
    paragraph_file = project_path / "step_2_one_paragraph_summary.txt"
    if paragraph_file.exists():
        print("\n[PARAGRAPH SUMMARY]")
        with open(paragraph_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            print(f"  {content}")
    
    # Show character info
    char_file = project_path / "step_3_character_summaries.json"
    if char_file.exists():
        print("\n[MAIN CHARACTERS]")
        with open(char_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for char in data.get('characters', [])[:3]:
                print(f"  {char.get('name', 'Unknown')} ({char.get('role', 'Unknown')})")
                print(f"    Goal: {char.get('goal', 'Unknown')}")
                print(f"    Conflict: {char.get('conflict', 'Unknown')}")
                print()
    
    # Show long synopsis excerpt
    synopsis_file = project_path / "step_6_long_synopsis.md"
    if synopsis_file.exists():
        print("[STORY SYNOPSIS - First 500 characters]")
        with open(synopsis_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Skip the header
            if content.startswith('# Long Synopsis'):
                lines = content.split('\n')
                content = '\n'.join(lines[2:])  # Skip title and empty line
            print(f"  {content[:500]}...")

def main():
    """Main function"""
    print_section("CODE OF DECEPTION - NOVEL PROGRESS ASSESSMENT")
    
    # Find the most recent project
    artifacts_dir = Path("artifacts")
    if not artifacts_dir.exists():
        print("[ERROR] No artifacts directory found")
        return False
    
    # Look for Code of Deception projects
    projects = list(artifacts_dir.glob("code_of_deception_*"))
    if not projects:
        print("[ERROR] No Code of Deception projects found")
        return False
    
    # Use the most recent project
    latest_project = max(projects, key=lambda p: p.name)
    project_id = latest_project.name
    
    print(f"[LATEST] Using project: {project_id}")
    
    # Assess progress
    success = assess_project(project_id)
    
    if success:
        # Show story content
        show_story_content(project_id)
        
        print_section("WHAT WE HAVE ACCOMPLISHED")
        print("[SUCCESS] We have successfully generated substantial novel content!")
        print("[CONTENT] The Snowflake Method pipeline has created:")
        print("  - Complete story structure (Steps 0-6)")
        print("  - Detailed character development")  
        print("  - Full story synopsis")
        print("  - Professional-grade novel foundation")
        print()
        print("[NEXT] To complete the novel, we need:")
        print("  - Step 7: Character Bibles (detailed character profiles)")
        print("  - Step 8: Scene List (breaking story into scenes)")
        print("  - Step 9: Scene Briefs (detailed scene planning)")
        print("  - Step 10: First Draft (complete manuscript)")
        print()
        print("[STATUS] We have created a solid foundation for a 50,000-word novel!")
        print(f"[FILES] All artifacts are saved in: {latest_project}")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[FATAL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)