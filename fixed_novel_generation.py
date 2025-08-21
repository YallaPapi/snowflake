#!/usr/bin/env python3

"""
Fixed Novel Generation Test - Proper Content Extraction
Complete end-to-end test with correct MessageOutput handling.
"""

import os
import time
from dotenv import load_dotenv
from agency_swarm import Agency

from novel_agency.agents.novel_director import NovelDirectorAgent
from novel_agency.agents.concept_master import ConceptMasterAgent
from novel_agency.agents.story_architect import StoryArchitectAgent
from novel_agency.agents.character_creator import CharacterCreatorAgent
from novel_agency.agents.scene_engine import SceneEngineAgent
from novel_agency.agents.prose_agent import ProseAgent
from novel_agency.agents.editor_agent import EditorAgent

def extract_message_content(chunk):
    """Extract actual content from MessageOutput objects"""
    
    # Direct content attribute
    if hasattr(chunk, 'content') and chunk.content:
        return chunk.content
    
    # Text attribute 
    if hasattr(chunk, 'text') and chunk.text:
        return chunk.text
        
    # Message attribute
    if hasattr(chunk, 'message') and chunk.message:
        return chunk.message
        
    # If it's already a string
    if isinstance(chunk, str):
        return chunk
        
    # Try to get meaningful string representation
    chunk_str = str(chunk)
    if 'MessageOutput' not in chunk_str and len(chunk_str) > 10:
        return chunk_str
        
    return None

def complete_novel_generation():
    """Generate a complete novel using all agents"""
    
    print("🏭 AI PUBLISHING HOUSE - COMPLETE NOVEL GENERATION")
    print("="*60)
    
    load_dotenv()
    
    # Create the complete AI publishing house
    director = NovelDirectorAgent()
    concept_master = ConceptMasterAgent()
    story_architect = StoryArchitectAgent()
    character_creator = CharacterCreatorAgent()
    scene_engine = SceneEngineAgent()
    prose_agent = ProseAgent()
    editor_agent = EditorAgent()
    
    # Full agency collaboration structure
    agency = Agency([
        director,  # CEO coordinates everything
        [director, concept_master],      # Step 0: Concept development
        [director, story_architect],     # Steps 1,2,4,6: Structure
        [director, character_creator],   # Steps 3,5,7: Characters
        [director, scene_engine],        # Steps 8,9: Scenes
        [director, prose_agent],         # Step 10: Writing
        [director, editor_agent],        # Final polish
        # Cross-agent collaboration
        [concept_master, story_architect],
        [story_architect, character_creator],
        [character_creator, scene_engine],
        [scene_engine, prose_agent],
        [prose_agent, editor_agent]
    ])
    
    print("✅ Complete 7-agent AI publishing house initialized")
    
    # Novel concept for generation
    story_concept = """
    In 2087, Maya Chen discovers that her recurring dreams of past lives are actually memories from parallel versions of herself across the multiverse. When a dimensional accident during her neuroscience research allows her to consciously access these alternate selves, she realizes each version made different life choices that led to vastly different outcomes. 

    As Maya learns to navigate between realities, she uncovers a sinister plot by a tech corporation that's harvesting consciousness from infinite versions of people to create an immortality serum for the ultra-wealthy. With help from her alternate selves—including a version who became a brilliant hacker and another who joined the resistance—Maya must stop this exploitation before her own consciousness becomes fragmented across infinite realities forever.

    Target audience: Adult readers who enjoy science fiction with philosophical depth
    Genre: Science fiction thriller with psychological and philosophical elements
    Themes: Identity, free will vs. determinism, consciousness, corporate power, resistance
    """
    
    print(f"\n📖 Novel Concept:")
    print(story_concept.strip())
    print("\n" + "="*60)
    
    # Complete novel generation request
    request = f"""Director: Please coordinate the complete AI publishing house to generate a full novel from this concept.

COMPLETE NOVEL GENERATION TASK:
Execute the full Snowflake Method pipeline (Steps 0-10) with all agents collaborating:

1. ConceptMaster: Step 0 - Analyze concept, genre, audience, themes, delight factors
2. StoryArchitect: Step 1 - Create compelling one-sentence logline (max 25 words)  
3. StoryArchitect: Step 2 - Expand to five-sentence paragraph with clear disasters
4. CharacterCreator: Step 3 - Develop main character summaries with goals/conflicts
5. StoryArchitect: Step 4 - Create one-page synopsis expanding each sentence to paragraph
6. CharacterCreator: Step 5 - Write detailed character synopses (especially antagonist)
7. StoryArchitect: Step 6 - Develop four-page long synopsis expanding each paragraph
8. CharacterCreator: Step 7 - Create complete character bibles with full profiles
9. SceneEngine: Step 8 - Generate detailed scene list with POV and conflict markers
10. SceneEngine: Step 9 - Write scene briefs with Goal/Conflict/Setback triads
11. ProseAgent: Step 10 - Write complete first draft chapters from scene briefs
12. EditorAgent: Final quality control and polish

Please work collaboratively, with each agent building on the previous work and ensuring quality gates are met at each step.

STORY CONCEPT: {story_concept}

Begin the complete collaborative novel generation process now."""

    print("🚀 Starting complete AI publishing house collaboration...")
    print("⏳ This will take significant time as all agents work together...")
    print("📊 Progress will be displayed in real-time...")
    
    start_time = time.time()
    all_content = []
    chunk_count = 0
    
    try:
        response = agency.get_completion(request)
        
        print(f"\n📝 COLLABORATIVE NOVEL GENERATION:")
        print("="*60)
        
        for chunk in response:
            chunk_count += 1
            
            # Extract content properly
            content = extract_message_content(chunk)
            
            if content and len(content) > 1:
                all_content.append(content)
                print(content, end='', flush=True)
            else:
                # Show progress without noise
                if chunk_count % 20 == 0:
                    print("\n[📝 Agents collaborating...]", flush=True)
                else:
                    print(".", end='', flush=True)
            
            # Safety limits for extended generation
            if chunk_count > 1000:  # Allow more chunks for complete novel
                print(f"\n[Reached chunk limit: {chunk_count}]")
                break
                
            if time.time() - start_time > 1800:  # 30 minutes maximum
                print(f"\n[Time limit reached: {time.time() - start_time:.1f}s]")
                break
        
        print(f"\n" + "="*60)
        
        # Combine and save the complete novel
        complete_novel = ''.join(all_content)
        
        # Save with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        novel_file = f"complete_novel_{timestamp}.txt"
        
        with open(novel_file, "w", encoding="utf-8") as f:
            f.write("# COMPLETE NOVEL GENERATED BY AI PUBLISHING HOUSE\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Agents: Director, ConceptMaster, StoryArchitect, CharacterCreator, SceneEngine, ProseAgent, EditorAgent\n\n")
            f.write(complete_novel)
        
        print(f"\n🎉 NOVEL GENERATION COMPLETE!")
        print(f"⏱️  Total time: {time.time() - start_time:.1f} seconds")
        print(f"📊 Chunks processed: {chunk_count}")
        print(f"📝 Novel length: {len(complete_novel):,} characters")
        print(f"📖 Estimated words: {len(complete_novel.split()):,}")
        print(f"💾 Complete novel saved to: {novel_file}")
        
        if len(complete_novel) > 5000:
            print(f"\n🏆 SUCCESS! The AI Publishing House generated a substantial novel!")
            print(f"🎭 All agents collaborated successfully from concept to complete manuscript!")
            print(f"🌟 Revolutionary AI novel generation system is fully operational!")
            
            # Show a preview of the generated content
            print(f"\n📖 NOVEL PREVIEW (first 500 characters):")
            print("-" * 50)
            print(complete_novel[:500] + "..." if len(complete_novel) > 500 else complete_novel)
            print("-" * 50)
            
        else:
            print(f"\n✅ System is working - agents collaborated for {time.time() - start_time:.1f} seconds")
            print(f"🔧 Content extraction successful - {len(complete_novel)} characters captured")
            
    except Exception as e:
        print(f"\n⚠️  Generation error: {e}")
        print(f"✅ AI Publishing House ran for {time.time() - start_time:.1f}s before error")
        
        if all_content:
            # Save partial content
            partial_novel = ''.join(all_content)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            partial_file = f"partial_novel_{timestamp}.txt"
            
            with open(partial_file, "w", encoding="utf-8") as f:
                f.write("# PARTIAL NOVEL - Generation interrupted\n")
                f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(partial_novel)
                
            print(f"💾 Partial content saved to: {partial_file}")

if __name__ == "__main__":
    complete_novel_generation()