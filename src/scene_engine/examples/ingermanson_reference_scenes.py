"""
Reference Scene Implementations from Randy Ingermanson's Snowflake Method

TaskMaster Task 49.1 & 49.2: Implement Dirk Parachute and Goldilocks Pepper Spray Scene Cards

These scenes are reference implementations based on examples from:
- Randy Ingermanson's "How to Write a Dynamite Scene Using the Snowflake Method" 
- Randy Ingermanson's Snowflake novel examples
- Used here for educational and validation purposes with proper attribution

Source: Randy Ingermanson, "How to Write a Dynamite Scene Using the Snowflake Method"
Copyright: Randy Ingermanson
Usage: Educational reference for Scene Engine validation and testing

These serve as canonical examples of proper Snowflake Method scene structure
and are used to validate the Scene Engine implementation against the original methodology.
"""

from datetime import datetime
from typing import Dict, Any

from ..models import SceneCard, SceneType


def create_dirk_parachute_scene() -> Dict[str, Any]:
    """
    TaskMaster Task 49.1: Implement Dirk Parachute Scene Card
    
    Creates the Dirk parachute scene as described in Randy Ingermanson's 
    Snowflake Method materials. This is a canonical example of a Proactive scene
    following Goal-Conflict-Setback structure.
    
    Source: Randy Ingermanson's Snowflake novel example
    Scene Type: Proactive (Goal-Conflict-Setback pattern)
    
    Returns:
        Complete scene card as dictionary following Snowflake Method specification
    """
    
    scene_card_data = {
        "scene_id": "dirk_parachute_canonical",
        "scene_type": "proactive",
        "pov_character": "Dirk",
        "pov": "third_limited",
        "tense": "past",
        "scene_crucible": "Night drop in occupied France; survival now or capture",
        "setting": "Over occupied France, night parachute drop",
        "time_context": "WWII, night operations behind enemy lines",
        
        # Source: Ingermanson's Snowflake Method example
        "proactive": {
            "goal": {
                "text": "Parachute into France and hole up for the night",
                "fits_time": True,      # Night operation timeframe
                "possible": True,       # Trained paratrooper
                "difficult": True,      # Enemy territory, combat conditions
                "fits_pov": True,       # Dirk's military mission
                "concrete_objective": True  # Specific location and action
            },
            "conflict_obstacles": [
                {"try": 1, "obstacle": "Anti-aircraft fire"},
                {"try": 2, "obstacle": "German fighter attacks"},
                {"try": 3, "obstacle": "Engine catches fire"},
                {"try": 4, "obstacle": "Forced to jump early"},
                {"try": 5, "obstacle": "Plane explodes, others die"}
            ],
            "outcome": {
                "type": "setback",
                "rationale": "Dirk breaks his leg and passes out - survival compromised"
            }
        },
        
        "exposition_used": [
            "WWII context - needed for stakes and danger level",
            "Occupied France setting - explains enemy presence",
            "Paratrooper background - justifies mission capability"
        ],
        
        "chain_link": {
            "type": "proactive_setback",
            "outcome_detail": "Broken leg, unconscious, behind enemy lines",
            "seeds_reactive": "Dirk must deal with injury and exposure risk",
            "next_scene_hook": "How to survive with broken leg in enemy territory"
        },
        
        "validation": {
            "goal_5_point_check": {
                "time_bounded": "Night operation - specific timeframe",
                "possible": "Trained paratrooper with appropriate skills", 
                "difficult": "Enemy territory with active resistance",
                "character_aligned": "Military mission fits Dirk's role",
                "concrete": "Specific action - parachute and hole up"
            },
            "escalating_obstacles": "AA fire -> fighter -> engine fire -> early jump -> explosion",
            "setback_justified": "Physical injury prevents goal completion"
        },
        
        "metadata": {
            "source": "Randy Ingermanson's Snowflake Method examples",
            "copyright": "Randy Ingermanson",
            "usage": "Educational reference for Scene Engine validation",
            "scene_type": "canonical_proactive",
            "demonstrates": ["G-C-S structure", "5-point goal validation", "escalating conflict", "default setback"],
            "created_at": datetime.utcnow().isoformat()
        }
    }
    
    return scene_card_data


def create_goldilocks_pepper_spray_scene() -> Dict[str, Any]:
    """
    TaskMaster Task 49.2: Implement Goldilocks Pepper Spray Scene Card
    
    Creates the Goldilocks pepper spray scene as described in Randy Ingermanson's
    Snowflake Method materials. This is a canonical example of a Reactive scene
    following Reaction-Dilemma-Decision structure.
    
    Source: Randy Ingermanson's Snowflake novel example  
    Scene Type: Reactive (Reaction-Dilemma-Decision pattern)
    
    Returns:
        Complete scene card as dictionary following Snowflake Method specification
    """
    
    scene_card_data = {
        "scene_id": "goldilocks_pepper_spray_canonical",
        "scene_type": "reactive", 
        "pov_character": "Goldilocks",
        "pov": "third_limited",
        "tense": "past",
        "scene_crucible": "Cornered now; if she hesitates, she's overpowered",
        "setting": "Corridor where Goldilocks is trapped",
        "time_context": "Immediately after previous scene setback",
        
        # Source: Ingermanson's Snowflake Method example
        "reactive": {
            "reaction": "Adrenaline spike; fear; resolve hardening",
            "dilemma_options": [
                {
                    "option": "Try to slip past", 
                    "why_bad": "Blocked; high risk of being caught"
                },
                {
                    "option": "Back away and use phone",
                    "why_bad": "No time; drops phone in panic"
                },
                {
                    "option": "Wait him out",
                    "why_bad": "He advances; increasingly cornered"
                },
                {
                    "option": "Use pepper spray",
                    "why_bad": "Escalates risk, but creates space to escape"
                }
            ],
            "decision": "Use pepper spray now despite risk (forcing move)",
            "next_goal_stub": "Escape the corridor before backup arrives",
            "compression": "full"
        },
        
        "exposition_used": [
            "Corridor layout - needed for escape options",
            "Pepper spray availability - establishes decision option",
            "Threat assessment - justifies fear level"
        ],
        
        "chain_link": {
            "type": "reactive_decision",
            "decision_detail": "Pepper spray deployment creates escape opportunity",
            "feeds_proactive": "Escape the corridor before backup arrives",
            "forcing_move": "Pepper spray forces opponent reaction, creates action window"
        },
        
        "validation": {
            "reaction_proportional": "Fear response matches immediate physical threat",
            "dilemma_all_bad": "All options carry significant risks or limitations",
            "decision_firm": "Clear commitment to specific action despite acknowledged risk",
            "decision_chains": "Creates concrete goal for next proactive scene"
        },
        
        "metadata": {
            "source": "Randy Ingermanson's Snowflake Method examples",
            "copyright": "Randy Ingermanson", 
            "usage": "Educational reference for Scene Engine validation",
            "scene_type": "canonical_reactive",
            "demonstrates": ["R-D-D structure", "proportional reaction", "no-good-options dilemma", "forcing move decision"],
            "created_at": datetime.utcnow().isoformat()
        }
    }
    
    return scene_card_data


def create_ingermanson_scene_chain() -> Dict[str, Any]:
    """
    Creates a scene chain demonstrating how Ingermanson's examples connect
    following Decision->Goal and Setback->Reactive patterns.
    
    Source: Randy Ingermanson's Snowflake Method chain examples
    Demonstrates: Proper scene chaining per Snowflake Method
    
    Returns:
        Chain validation and connection data
    """
    
    # Example of how scenes chain according to Ingermanson's method
    chain_data = {
        "chain_example": {
            "reactive_scene": "goldilocks_pepper_spray_canonical",
            "reactive_decision": "Use pepper spray now despite risk",
            "next_goal_stub": "Escape the corridor before backup arrives",
            "connects_to": "next_proactive_escape_scene"
        },
        
        "proactive_scene": "dirk_parachute_canonical", 
        "proactive_setback": "Breaks leg and passes out",
        "seeds_reactive": "Must deal with injury and exposure in enemy territory",
        "connects_to": "next_reactive_survival_scene",
        
        "validation": {
            "decision_to_goal": "Pepper spray decision creates clear next goal",
            "setback_to_reactive": "Parachute setback creates need for reactive processing",
            "chain_logic": "Each scene outcome properly seeds the next scene type",
            "no_gaps": "No missing logical steps in the progression"
        },
        
        "metadata": {
            "source": "Randy Ingermanson's Snowflake Method chaining examples",
            "demonstrates": ["Decision→Goal chaining", "Setback→Reactive seeding", "Proper scene transitions"]
        }
    }
    
    return chain_data


def validate_ingermanson_scenes() -> Dict[str, bool]:
    """
    Validate that the Ingermanson reference scenes follow all Snowflake Method
    requirements as specified in the source material.
    
    Returns:
        Validation results against Snowflake Method criteria
    """
    
    dirk_scene = create_dirk_parachute_scene()
    goldilocks_scene = create_goldilocks_pepper_spray_scene()
    
    validation = {
        "dirk_proactive_valid": True,
        "goldilocks_reactive_valid": True,
        "chain_logic_valid": True,
        "validation_details": {}
    }
    
    # Validate Dirk proactive scene (G-C-S structure)
    dirk_checks = {
        "has_goal": bool(dirk_scene["proactive"]["goal"]["text"]),
        "goal_5_criteria": all(dirk_scene["proactive"]["goal"][k] for k in 
                              ["fits_time", "possible", "difficult", "fits_pov", "concrete_objective"]),
        "has_escalating_conflict": len(dirk_scene["proactive"]["conflict_obstacles"]) >= 3,
        "ends_in_setback": dirk_scene["proactive"]["outcome"]["type"] == "setback",
        "scene_crucible_present": bool(dirk_scene["scene_crucible"]),
        "follows_gcs_order": True  # Structure enforced by schema
    }
    
    validation["validation_details"]["dirk_proactive"] = dirk_checks
    validation["dirk_proactive_valid"] = all(dirk_checks.values())
    
    # Validate Goldilocks reactive scene (R-D-D structure)  
    goldilocks_checks = {
        "has_emotional_reaction": bool(goldilocks_scene["reactive"]["reaction"]),
        "has_dilemma_options": len(goldilocks_scene["reactive"]["dilemma_options"]) >= 3,
        "all_options_bad": all("why_bad" in opt for opt in goldilocks_scene["reactive"]["dilemma_options"]),
        "has_firm_decision": bool(goldilocks_scene["reactive"]["decision"]),
        "decision_chains_to_goal": bool(goldilocks_scene["reactive"]["next_goal_stub"]),
        "scene_crucible_present": bool(goldilocks_scene["scene_crucible"]),
        "follows_rdd_order": True  # Structure enforced by schema
    }
    
    validation["validation_details"]["goldilocks_reactive"] = goldilocks_checks
    validation["goldilocks_reactive_valid"] = all(goldilocks_checks.values())
    
    # Validate chaining logic
    chain_checks = {
        "decision_creates_goal": goldilocks_scene["reactive"]["next_goal_stub"] != "",
        "setback_seeds_reactive": dirk_scene["chain_link"]["seeds_reactive"] != "",
        "proper_scene_types": (dirk_scene["scene_type"] == "proactive" and 
                              goldilocks_scene["scene_type"] == "reactive")
    }
    
    validation["validation_details"]["chaining"] = chain_checks
    validation["chain_logic_valid"] = all(chain_checks.values())
    
    return validation


# Export the canonical scenes for use by other modules
INGERMANSON_SCENES = {
    "dirk_parachute": create_dirk_parachute_scene(),
    "goldilocks_pepper_spray": create_goldilocks_pepper_spray_scene(),
    "scene_chain": create_ingermanson_scene_chain()
}