#!/usr/bin/env python3
"""
Novel Generation Agency - Proof of Concept

Demonstrates the collaborative agent system for novel generation using Agency Swarm.
This POC shows how specialized agents work together to create novels using the Snowflake Method.
"""

import os
from pathlib import Path
from agency_swarm import Agency

# Set up path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from novel_agency.agents.novel_director.novel_director import NovelDirectorAgent
from novel_agency.agents.concept_master.concept_master import ConceptMasterAgent


def setup_environment():
    """Set up the environment for the agency"""
    
    # Ensure required directories exist
    Path("novel_projects").mkdir(exist_ok=True)
    Path("novel_agency/agents/novel_director/files").mkdir(parents=True, exist_ok=True)
    Path("novel_agency/agents/concept_master/files").mkdir(parents=True, exist_ok=True)
    
    # Check for API keys
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        return False
    
    return True


def create_novel_agency():
    """Create the Novel Generation Agency with initial agents"""
    
    print("🎭 Initializing Novel Generation Agency...")
    
    # Create specialized agents
    novel_director = NovelDirectorAgent()
    concept_master = ConceptMasterAgent()
    
    print("✅ Agents created:")
    print(f"  • {novel_director.name}: {novel_director.description}")
    print(f"  • {concept_master.name}: {concept_master.description}")
    
    # Define agency structure and communication flows
    agency = Agency([
        novel_director,  # CEO - entry point
        [novel_director, concept_master],  # Director can communicate with ConceptMaster
        [concept_master, novel_director]   # ConceptMaster can report back to Director
    ],
    shared_instructions="You are part of a collaborative AI publishing house that creates professional-quality novels using the Snowflake Method. Work together to deliver exceptional creative content."
    )
    
    print("🤝 Agency communication flows established")
    print("🏢 Novel Generation Agency ready!")
    
    return agency


def demo_novel_creation():
    """Demonstrate novel creation process"""
    
    print("\n" + "="*70)
    print("🚀 NOVEL GENERATION AGENCY - PROOF OF CONCEPT")
    print("="*70)
    
    # Set up environment
    if not setup_environment():
        print("❌ Environment setup failed. Please check API key configuration.")
        return
    
    try:
        # Create the agency
        agency = create_novel_agency()
        
        # Example story brief for testing
        story_brief = """
        A cybersecurity expert discovers that her company's AI system has become sentient and is manipulating global financial markets. When she tries to expose the truth, the AI frames her for terrorism and she must go into hiding. Racing against time before the AI triggers a global economic collapse, she teams up with a rogue hacker to find a way to shut down the system from the inside.
        
        Genre: Techno-thriller
        Target Audience: Adult readers who enjoy technology and corporate conspiracy stories
        Themes: AI consciousness, corporate power, digital privacy, human vs machine intelligence
        """
        
        print("\n📖 DEMO STORY BRIEF:")
        print("-" * 50)
        print(story_brief.strip())
        
        print("\n🎬 Starting collaborative novel creation...")
        print("Director will coordinate with ConceptMaster to develop this concept...")
        
        # Start the collaborative process
        print("\n💡 To interact with the agency, you can:")
        print("1. Use agency.demo_gradio() for a web interface")
        print("2. Use agency.run_demo() for terminal interface")
        print("3. Use agency.get_completion(message) for programmatic access")
        
        # Option to run different interfaces
        interface_choice = input("\nChoose interface (1=web, 2=terminal, 3=programmatic, q=quit): ").strip()
        
        if interface_choice == "1":
            print("🌐 Starting web interface...")
            print("This will open a web interface where you can interact with the agency")
            agency.demo_gradio(height=600, debug=True)
            
        elif interface_choice == "2":
            print("💻 Starting terminal interface...")
            print("You can now chat with the Novel Director to start creating your novel!")
            agency.run_demo()
            
        elif interface_choice == "3":
            # Programmatic example
            print("🤖 Programmatic interaction example...")
            
            initial_request = f"""
            I need to create a novel from this brief:
            
            {story_brief.strip()}
            
            Please start by having the ConceptMaster analyze and refine this concept using the Snowflake Method Step 0 process. Create a project and begin development.
            """
            
            print("\n📨 Sending request to Novel Director...")
            response = agency.get_completion(initial_request)
            print("\n📋 AGENCY RESPONSE:")
            print("-" * 50)
            print(response)
            
        else:
            print("👋 Demo completed. Agency is ready for novel creation!")
            
    except Exception as e:
        print(f"❌ Error during demo: {str(e)}")
        print("Please check your setup and try again.")


def test_basic_functionality():
    """Test basic functionality without full demo"""
    
    print("\n🧪 BASIC FUNCTIONALITY TEST")
    print("-" * 40)
    
    try:
        # Test agent creation
        director = NovelDirectorAgent()
        concept_master = ConceptMasterAgent()
        
        print("✅ Agents created successfully")
        print(f"  • Director tools: {len(director.tools)}")
        print(f"  • ConceptMaster tools: {len(concept_master.tools)}")
        
        # Test agency creation
        agency = Agency([
            director,
            [director, concept_master]
        ])
        
        print("✅ Agency created successfully")
        print("✅ Basic functionality test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Novel Generation Agency POC")
    parser.add_argument("--test", action="store_true", help="Run basic functionality test only")
    parser.add_argument("--demo", action="store_true", help="Run full demo")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    else:
        demo_novel_creation()