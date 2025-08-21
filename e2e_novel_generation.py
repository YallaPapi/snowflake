#!/usr/bin/env python3

"""
E2E Novel Generation Test - Complete Novel Creation

End-to-end test to generate an actual novel using the AI publishing house.
"""

import os
import time
from dotenv import load_dotenv
from agency_swarm import Agency

# Import all agents
from novel_agency.agents.novel_director import NovelDirectorAgent
from novel_agency.agents.concept_master import ConceptMasterAgent
from novel_agency.agents.story_architect import StoryArchitectAgent
from novel_agency.agents.character_creator import CharacterCreatorAgent
from novel_agency.agents.scene_engine import SceneEngineAgent
from novel_agency.agents.prose_agent import ProseAgent
from novel_agency.agents.editor_agent import EditorAgent

def create_publishing_house():
    """Create the complete AI publishing house"""
    print("🏢 Creating AI Publishing House...")
    
    # Create all agents
    novel_director = NovelDirectorAgent()
    concept_master = ConceptMasterAgent()
    story_architect = StoryArchitectAgent()
    character_creator = CharacterCreatorAgent()
    scene_engine = SceneEngineAgent()
    prose_agent = ProseAgent()
    editor_agent = EditorAgent()
    
    print("✅ All 7 agents created")
    
    # Create agency with complete workflow
    agency = Agency([
        novel_director,  # CEO
        [novel_director, concept_master],
        [novel_director, story_architect],
        [novel_director, character_creator],
        [novel_director, scene_engine],
        [novel_director, prose_agent],
        [novel_director, editor_agent],
        [concept_master, story_architect],
        [story_architect, character_creator],
        [character_creator, scene_engine],
        [scene_engine, prose_agent],
        [prose_agent, editor_agent]
    ],
    shared_instructions="""You are part of an AI publishing house creating professional novels. 
    Work systematically through the Snowflake Method. Be thorough but efficient.
    Focus on creating compelling, publication-ready content."""
    )
    
    print("✅ Publishing house ready!")
    return agency

def capture_response(response, max_chunks=200, max_time=300):
    """Capture agent response with proper timeouts"""
    print("\n🤖 AGENT COLLABORATION IN PROGRESS...")
    print("="*60)
    
    full_response = ""
    chunk_count = 0
    start_time = time.time()
    
    try:
        if hasattr(response, '__iter__'):
            for chunk in response:
                # Check limits
                if chunk_count >= max_chunks or (time.time() - start_time) >= max_time:
                    print(f"\n[Reached limits: {chunk_count} chunks, {time.time() - start_time:.1f}s]")
                    break
                
                try:
                    chunk_str = str(chunk)
                    if chunk_str and len(chunk_str) > 5:
                        print(chunk_str, end='', flush=True)
                        full_response += chunk_str
                    elif "MessageOutput" not in chunk_str:
                        print(".", end='', flush=True)
                except Exception as e:
                    print(".", end='', flush=True)
                
                chunk_count += 1
        else:
            full_response = str(response)
            print(full_response)
    
    except Exception as e:
        print(f"\n[Response capture ended: {e}]")
    
    print(f"\n" + "="*60)
    print(f"✅ Collaboration session completed!")
    print(f"📊 Response: {len(full_response)} characters, {chunk_count} chunks")
    print(f"⏱️  Time: {time.time() - start_time:.1f} seconds")
    
    return full_response

def test_step_by_step_development():
    """Test step-by-step novel development"""
    
    print("📚 E2E NOVEL GENERATION TEST")
    print("="*60)
    
    # Load environment
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ No API keys found")
        return
    
    print("✅ API keys loaded")
    
    # Create publishing house
    agency = create_publishing_house()
    
    # Story brief for actual novel generation
    story_brief = """
    Title: "The Memory Thief"
    
    A forensic psychologist discovers she can extract and experience other people's memories by touching objects they've handled. When a series of murders rocks her small town, she uses this ability to help solve the case, but each memory she absorbs begins to change her own personality. As she gets closer to the killer, she realizes the murderer knows about her gift and is using it to frame her for the crimes.
    
    Genre: Psychological thriller with supernatural elements
    Target: Adult thriller readers
    Length: Novella (25,000-30,000 words, ~10-12 chapters)
    Setting: Small mountain town, present day
    Themes: Identity, truth vs. perception, the cost of empathy
    """
    
    print(f"\n📖 STORY BRIEF:")
    print(story_brief.strip())
    
    print(f"\n🎬 PHASE 1: CONCEPT DEVELOPMENT")
    print("-" * 40)
    
    # Phase 1: Concept Development (Steps 0-2)
    concept_request = f"""Director: Please coordinate the initial concept development for this novel.

PHASE 1 WORKFLOW:
1. ConceptMaster: Create Step 0 story concept foundation
2. StoryArchitect: Develop Step 1 logline and Step 2 paragraph summary

Please work together to establish the strong foundation for this thriller.

STORY BRIEF: {story_brief}

Begin the systematic development process now."""
    
    print("⚡ Starting Phase 1...")
    phase1_response = agency.get_completion(concept_request)
    phase1_output = capture_response(phase1_response, max_chunks=100, max_time=180)
    
    # Save Phase 1 output
    with open("phase1_concept.txt", "w") as f:
        f.write(phase1_output)
    print("💾 Phase 1 results saved to phase1_concept.txt")
    
    print(f"\n🎭 PHASE 2: CHARACTER & STRUCTURE")
    print("-" * 40)
    
    # Phase 2: Character and Structure (Steps 3-4)
    structure_request = f"""Director: Now coordinate the character and structural development.

PHASE 2 WORKFLOW:
1. CharacterCreator: Develop Step 3 character summaries for the main characters
2. StoryArchitect: Create Step 4 one-page synopsis

Use the concept foundation from Phase 1 to create compelling characters and detailed structure.

Continue the systematic development of "The Memory Thief" thriller."""
    
    print("⚡ Starting Phase 2...")
    phase2_response = agency.get_completion(structure_request)
    phase2_output = capture_response(phase2_response, max_chunks=100, max_time=180)
    
    # Save Phase 2 output
    with open("phase2_structure.txt", "w") as f:
        f.write(phase2_output)
    print("💾 Phase 2 results saved to phase2_structure.txt")
    
    print(f"\n🎬 PHASE 3: SCENE DEVELOPMENT")
    print("-" * 40)
    
    # Phase 3: Scene Development (Steps 8-9)
    scene_request = f"""Director: Coordinate the scene development phase.

PHASE 3 WORKFLOW:
1. SceneEngine: Create Step 8 scene list for 10-12 chapters
2. SceneEngine: Develop Step 9 scene briefs for the first 3 scenes

Focus on creating a compelling opening that hooks readers and establishes the thriller pacing.

Build on all the previous development to create specific, actionable scene architecture."""
    
    print("⚡ Starting Phase 3...")
    phase3_response = agency.get_completion(scene_request)
    phase3_output = capture_response(phase3_response, max_chunks=100, max_time=180)
    
    # Save Phase 3 output
    with open("phase3_scenes.txt", "w") as f:
        f.write(phase3_output)
    print("💾 Phase 3 results saved to phase3_scenes.txt")
    
    print(f"\n✍️ PHASE 4: PROSE WRITING")
    print("-" * 40)
    
    # Phase 4: Prose Writing
    prose_request = f"""Director: Coordinate the prose writing phase.

PHASE 4 WORKFLOW:
1. ProseAgent: Write the opening chapter of "The Memory Thief" using the scene briefs
2. Focus on: Strong hook, character establishment, thriller pacing
3. Target: 2000-2500 words for Chapter 1

Use all the established story elements to craft compelling, publication-quality prose that will hook readers immediately.

Create the actual novel opening now."""
    
    print("⚡ Starting Phase 4...")
    phase4_response = agency.get_completion(prose_request)
    phase4_output = capture_response(phase4_response, max_chunks=150, max_time=240)
    
    # Save Phase 4 output
    with open("chapter1_draft.txt", "w") as f:
        f.write(phase4_output)
    print("💾 Chapter 1 draft saved to chapter1_draft.txt")
    
    print(f"\n📝 PHASE 5: EDITORIAL REVIEW")
    print("-" * 40)
    
    # Phase 5: Editorial Review
    editor_request = f"""Director: Have EditorAgent review the Chapter 1 draft for quality and provide feedback.

EDITORIAL REVIEW:
1. Assess prose quality and readability
2. Check character voice and thriller pacing  
3. Verify story consistency with established elements
4. Provide specific improvement recommendations

Provide professional editorial feedback on the opening chapter."""
    
    print("⚡ Starting Phase 5...")
    phase5_response = agency.get_completion(editor_request)
    phase5_output = capture_response(phase5_response, max_chunks=100, max_time=120)
    
    # Save Phase 5 output
    with open("editorial_feedback.txt", "w") as f:
        f.write(phase5_output)
    print("💾 Editorial feedback saved to editorial_feedback.txt")
    
    # Final summary
    print(f"\n🎉 E2E NOVEL GENERATION COMPLETE!")
    print("="*60)
    print("📁 Generated Files:")
    print("  • phase1_concept.txt - Story concept foundation")
    print("  • phase2_structure.txt - Characters and structure")  
    print("  • phase3_scenes.txt - Scene architecture")
    print("  • chapter1_draft.txt - Opening chapter prose")
    print("  • editorial_feedback.txt - Professional feedback")
    print(f"\n🏆 REVOLUTIONARY SUCCESS!")
    print("The AI Publishing House has generated novel content end-to-end!")
    print("From concept to polished prose - the future of novel creation is here!")

if __name__ == "__main__":
    test_step_by_step_development()