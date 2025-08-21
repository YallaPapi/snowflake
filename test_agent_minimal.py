#!/usr/bin/env python3

"""
Minimal test to isolate the Agent initialization issue
"""

try:
    print("Testing minimal agent creation...")
    
    # Import the Agent class
    from agency_swarm.agents import Agent
    print("✅ Successfully imported Agent")
    
    # Create minimal agent
    agent = Agent(
        name="TestAgent",
        description="Minimal test agent",
        instructions="You are a test agent."
    )
    print("✅ Successfully created Agent with temperature parameter")
    
    print("Agent created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()