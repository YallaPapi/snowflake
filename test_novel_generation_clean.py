#!/usr/bin/env python3
"""
Clean Novel Generation Test - No Unicode Issues
Tests the complete agency system for novel generation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_api_keys():
    """Load API keys from environment"""
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if openai_key:
        print("OpenAI API key loaded successfully")
        return True
    elif anthropic_key:
        print("Anthropic API key loaded successfully") 
        return True
    else:
        print("WARNING: No API keys found in environment")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return False

def test_agency_novel_generation():
    """Test the complete agency system for novel generation"""
    
    print("=" * 80)
    print("SNOWFLAKE AGENCY SYSTEM - COMPLETE NOVEL GENERATION TEST")
    print("=" * 80)
    
    # Load API keys
    if not setup_api_keys():
        print("Cannot proceed without API keys")
        return False
    
    try:
        # Import agency components
        print("\nImporting agency components...")
        from novel_agency.agents.novel_director import NovelDirectorAgent
        from novel_agency.agents.concept_master import ConceptMasterAgent
        from novel_agency.agents.story_architect import StoryArchitectAgent
        from novel_agency.agents.character_creator import CharacterCreatorAgent
        from novel_agency.agents.scene_engine import SceneEngineAgent
        from novel_agency.agents.prose_agent import ProseAgent
        from novel_agency.agents.editor_agent import EditorAgent
        from agency_swarm import Agency
        
        print("All agency components imported successfully!")
        
        # Create all agents
        print("\nCreating specialized AI agents...")
        novel_director = NovelDirectorAgent()
        concept_master = ConceptMasterAgent()
        story_architect = StoryArchitectAgent()
        character_creator = CharacterCreatorAgent()
        scene_engine = SceneEngineAgent()
        prose_agent = ProseAgent()
        editor_agent = EditorAgent()
        
        print("All 7 agents created successfully!")
        
        # Create agency with full collaboration network
        print("\nEstablishing agency collaboration network...")
        agency = Agency([
            novel_director,  # CEO - main entry point
            
            # Director coordination with all agents
            [novel_director, concept_master],
            [novel_director, story_architect],
            [novel_director, character_creator],
            [novel_director, scene_engine],
            [novel_director, prose_agent],
            [novel_director, editor_agent],
            
            # Snowflake Method workflow chains
            [concept_master, story_architect],     
            [story_architect, character_creator],  
            [character_creator, scene_engine],     
            [scene_engine, prose_agent],           
            [prose_agent, editor_agent],           
            
            # Bidirectional feedback loops
            [editor_agent, prose_agent],           
            [editor_agent, scene_engine],          
            [editor_agent, character_creator],     
            [editor_agent, story_architect],       
            [editor_agent, concept_master],        
        ],
        shared_instructions="""You are part of the world's most advanced AI publishing house, creating professional-quality novels through collaborative intelligence.

WORKFLOW: Follow the Snowflake Method exactly
- ConceptMaster: Develop story foundations (Step 0)
- StoryArchitect: Build narrative structure (Steps 1,2,4,6) 
- CharacterCreator: Create compelling characters (Steps 3,5,7)
- SceneEngine: Design scene sequences (Steps 8,9)
- ProseAgent: Write the novel (Step 10)
- EditorAgent: Polish and refine (Quality Control)

COLLABORATION PRINCIPLES:
- Build on each other's work systematically
- Provide constructive feedback and iterate
- Maintain consistency with established story elements
- Aim for professional publishing standards
- Support the creative vision while enhancing quality

QUALITY STANDARDS:
- Every output must be publication-ready
- Characters must be compelling and consistent  
- Plot must be engaging with proper pacing
- Prose must be polished and readable
- Final novel must be market-ready

Work together to create extraordinary novels that readers will love."""
        )
        
        print("Agency collaboration network established successfully!")
        print("AI Publishing House is ready for novel generation!")
        
        # Define compelling story concept
        story_brief = """
        In 2045, memories can be extracted, stored, and traded like cryptocurrency. Maya Chen, a memory archaeologist, discovers that her own childhood memories have been systematically stolen and sold on the black market. As she investigates, she uncovers a vast conspiracy where politicians maintain power by erasing citizens' memories of their failures, and corporations harvest emotional memories from the poor to sell to the wealthy.

        When Maya gets close to the truth, the memory cartel frames her for terrorism and attempts to erase her entirely. Racing against time before they can complete the memory wipe, she must team up with a rogue hacker and a group of memory rebels to expose the conspiracy. But to succeed, she'll have to sacrifice her most precious memories - the only proof of who she really is.

        Genre: Cyberpunk Thriller
        Target Audience: Adult readers who enjoy complex sci-fi, corporate conspiracy stories, and dystopian futures
        Themes: Identity, memory, power, truth vs. manufactured reality, human consciousness
        Setting: Near-future Los Angeles where memories are the ultimate currency
        """
        
        print("\nSTORY CONCEPT:")
        print("-" * 60)
        print(story_brief.strip())
        
        print("\nInitiating collaborative novel creation process...")
        print("This will involve all 7 agents working together through the complete Snowflake Method...")
        print("Progress can be monitored at: http://127.0.0.1:5000")
        
        # Create the collaborative request
        collaborative_request = f"""
        Director: Please orchestrate the complete novel development process for this story concept.
        
        MISSION: Create a professional-quality novel using collaborative intelligence
        
        WORKFLOW COORDINATION:
        1. ConceptMaster: Develop Step 0 story concept foundations
        2. StoryArchitect: Create Steps 1,2,4,6 narrative structure  
        3. CharacterCreator: Build Steps 3,5,7 character development
        4. SceneEngine: Design Steps 8,9 scene architecture
        5. ProseAgent: Write Step 10 novel prose (target 50,000-80,000 words)
        6. EditorAgent: Provide final quality control and polish
        
        COLLABORATION INSTRUCTIONS:
        - Each agent should build systematically on previous agents' work
        - Provide feedback and suggestions to improve overall quality
        - Ensure consistency with established story elements
        - Create multiple revision cycles if needed for quality
        - Aim for professional publication standards
        
        STORY CONCEPT: {story_brief.strip()}
        
        Begin the collaborative novel creation process now. Work together to create an exceptional novel that readers will love.
        """
        
        print("\nStarting collaborative AI novel generation...")
        print("This may take 30-60 minutes for a complete novel...")
        
        # Start the collaborative process
        print("\nAgency response:")
        print("=" * 60)
        
        response = agency.get_completion(collaborative_request)
        print(response)
        
        print("\n" + "=" * 60)
        print("NOVEL GENERATION PROCESS INITIATED!")
        print("Monitor progress at: http://127.0.0.1:5000")
        
        return True
        
    except Exception as e:
        print(f"Error during agency novel generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting AI Publishing House Novel Generation Test...")
    success = test_agency_novel_generation()
    
    if success:
        print("\nAI Publishing House is operational!")
        print("Check the observability dashboard for real-time progress")
    else:
        print("\nTest encountered issues")
    
    # Keep running so user can monitor
    print("\nPress Ctrl+C to stop monitoring...")
    try:
        input()  # Wait for user input
    except KeyboardInterrupt:
        print("\nStopping test...")