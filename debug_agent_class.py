#!/usr/bin/env python3

"""
Debug the Agent class to see its actual signature
"""

import inspect

try:
    # Import the Agent class
    from agency_swarm.agents import Agent
    print("✅ Successfully imported Agent")
    print(f"Agent class: {Agent}")
    print(f"Agent module: {Agent.__module__}")
    print(f"Agent file: {inspect.getfile(Agent)}")
    
    # Get the init signature
    sig = inspect.signature(Agent.__init__)
    print(f"\nAgent.__init__ signature:")
    print(f"{sig}")
    
    # Check if temperature parameter exists
    params = sig.parameters
    print(f"\nParameters:")
    for name, param in params.items():
        print(f"  {name}: {param}")
    
    if 'temperature' in params:
        print("\n✅ temperature parameter IS present")
    else:
        print("\n❌ temperature parameter is NOT present")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()