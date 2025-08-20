"""
Example Scene Implementations

TaskMaster Task 49: Example Scene Implementation
Creates example scenes that demonstrate the complete Scene Engine workflow
using original content that follows Snowflake Method principles.

These scenes serve as reference implementations for validation and testing
without reproducing copyrighted material.
"""

from datetime import datetime
from typing import Dict, Any
import uuid

from ..models import SceneCard, SceneType


def create_example_proactive_scene() -> Dict[str, Any]:
    """
    Create an example proactive scene following G-C-S structure.
    
    Demonstrates:
    - Goal-Conflict-Setback pattern
    - 5-point goal validation
    - Escalating obstacles
    - Scene crucible focus
    
    Returns:
        Complete scene card as dictionary
    """
    
    scene_card_data = {
        "scene_id": "example_proactive_escape",
        "scene_type": "proactive",
        "pov_character": "Maya Chen",
        "pov": "third_limited",
        "tense": "past", 
        "scene_crucible": "Trapped in the flooding underground tunnel, Maya must reach the exit before the water blocks all escape routes",
        "setting": "Underground maintenance tunnel, industrial district",
        "time_context": "Late night during heavy storm",
        
        "proactive": {
            "goal": "Reach the tunnel exit before rising floodwater blocks the way",
            "goal_validation": {
                "fits_time": True,  # Minutes available before flooding
                "possible": True,   # Exit is reachable
                "difficult": True,  # Rising water and obstacles
                "fits_pov": True,   # Maya's survival instinct
                "concrete_objective": True  # Physical location to reach
            },
            "conflict": "Rising floodwater fills the tunnel while debris blocks the path forward",
            "setback": "Slips on wet concrete and sprains ankle just as water reaches waist-deep",
            "obstacles": [
                {"attempt": 1, "obstacle": "Knee-deep water slows progress"},
                {"attempt": 2, "obstacle": "Fallen pipe blocks the narrow passage"}, 
                {"attempt": 3, "obstacle": "Electrical sparks from damaged junction box"},
                {"attempt": 4, "obstacle": "Water reaches chest level, current increases"}
            ]
        },
        
        "exposition_used": [
            "Tunnel layout - needed to understand escape route",
            "Storm context - explains flooding urgency", 
            "Maya's location knowledge - justifies route choice"
        ],
        
        "chain_link": {
            "type": "proactive_setback",
            "seeds_reactive": "Maya must deal with injury while water continues rising",
            "next_scene_type": "reactive"
        },
        
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "example_type": "canonical_proactive",
            "demonstrates": ["G-C-S structure", "5-point goal", "escalating obstacles", "setback outcome"]
        }
    }
    
    return scene_card_data


def create_example_reactive_scene() -> Dict[str, Any]:
    """
    Create an example reactive scene following R-D-D structure.
    
    Demonstrates:
    - Reaction-Dilemma-Decision pattern
    - Emotional processing
    - Only-bad options dilemma
    - Firm decision that chains forward
    
    Returns:
        Complete scene card as dictionary
    """
    
    scene_card_data = {
        "scene_id": "example_reactive_betrayal", 
        "scene_type": "reactive",
        "pov_character": "Detective Sarah Kim",
        "pov": "first_person",
        "tense": "present",
        "scene_crucible": "Learning her trusted partner sold evidence to the defense, Sarah faces career destruction unless she acts immediately",
        "setting": "Police station parking garage", 
        "time_context": "Late evening after confrontation",
        
        "reactive": {
            "reaction": "Overwhelming anger mixed with disbelief - the person she trusted most has destroyed years of work and may have let killers walk free",
            "dilemma": "Choose between loyalty and justice with no good options available",
            "dilemma_options": [
                {
                    "option": "Report partner to Internal Affairs immediately",
                    "why_bad": "Destroys partner's family and may not prevent evidence contamination"
                },
                {
                    "option": "Confront partner privately and demand explanation", 
                    "why_bad": "Gives him time to cover tracks and destroy more evidence"
                },
                {
                    "option": "Try to gather more proof before acting",
                    "why_bad": "Delays justice and risks more cases being compromised"
                },
                {
                    "option": "Transfer to different precinct and stay quiet",
                    "why_bad": "Abandons victims and allows corruption to continue"
                }
            ],
            "decision": "Report partner to IA tonight despite personal cost - victims deserve justice more than misguided loyalty deserves protection",
            "next_goal_stub": "Present evidence to Internal Affairs before partner can interfere",
            "compression": "full"
        },
        
        "exposition_used": [
            "Partner relationship history - explains depth of betrayal",
            "Case significance - justifies emotional intensity",
            "IA procedures - needed for decision consequences"
        ],
        
        "chain_link": {
            "type": "reactive_decision", 
            "feeds_proactive": "Present evidence to Internal Affairs before partner can interfere",
            "next_scene_type": "proactive"
        },
        
        "metadata": {
            "created_at": datetime.utcnow().isoformat(),
            "example_type": "canonical_reactive",
            "demonstrates": ["R-D-D structure", "emotional reaction", "no-good-options dilemma", "firm decision"]
        }
    }
    
    return scene_card_data


def create_example_scene_pair() -> Dict[str, Any]:
    """
    Create a pair of chained scenes (Proactive -> Reactive) that demonstrate
    how scenes connect through the Decision->Goal and Setback->Reactive patterns.
    
    Returns:
        Dictionary containing both scenes and chain validation
    """
    
    # Scene 1: Proactive scene with setback
    proactive_scene = {
        "scene_id": "chained_proactive_heist",
        "scene_type": "proactive", 
        "pov_character": "Alex Rivera",
        "pov": "third_limited",
        "tense": "past",
        "scene_crucible": "Security system activates during the art theft - Alex must escape with the painting before guards arrive",
        "setting": "Private art gallery, upper floor",
        "time_context": "2 AM during planned heist",
        
        "proactive": {
            "goal": "Escape the gallery with the stolen painting before security responds",
            "goal_validation": {
                "fits_time": True,
                "possible": True, 
                "difficult": True,
                "fits_pov": True,
                "concrete_objective": True
            },
            "conflict": "Motion sensors trigger lockdown while guards race to location",
            "setback": "Painting falls and tears during desperate escape - now worthless but evidence of crime remains",
            "obstacles": [
                {"attempt": 1, "obstacle": "Motion detector activates unexpectedly"},
                {"attempt": 2, "obstacle": "Security shutters begin closing"},
                {"attempt": 3, "obstacle": "Guards enter building below"},
                {"attempt": 4, "obstacle": "Fire escape ladder jams halfway down"}
            ]
        },
        
        "chain_link": {
            "type": "proactive_setback",
            "outcome_detail": "Escaped but painting damaged and crime still traceable",
            "seeds_reactive": "Must deal with failed heist and exposure risk"
        }
    }
    
    # Scene 2: Reactive scene processing the setback
    reactive_scene = {
        "scene_id": "chained_reactive_aftermath",
        "scene_type": "reactive",
        "pov_character": "Alex Rivera", 
        "pov": "third_limited",
        "tense": "past",
        "scene_crucible": "With the heist failed and evidence pointing to them, Alex must decide how to avoid capture",
        "setting": "Alex's apartment, same night",
        "time_context": "3 AM after failed heist",
        
        "reactive": {
            "reaction": "Frustration at the careful planning gone wrong mixed with growing panic about police investigation",
            "dilemma": "All escape options carry severe risks with no guarantee of safety",
            "dilemma_options": [
                {
                    "option": "Flee the city immediately with fake ID",
                    "why_bad": "Abandons entire life and may not have enough resources"
                },
                {
                    "option": "Stay and try to establish alibi", 
                    "why_bad": "Security footage may already identify them"
                },
                {
                    "option": "Turn themselves in and cooperate",
                    "why_bad": "Guarantees prison time and betrays criminal contacts"
                },
                {
                    "option": "Destroy evidence and lay low",
                    "why_bad": "Police investigation will intensify if they disappear"
                }
            ],
            "decision": "Flee the city tonight using emergency escape plan - better to run than guarantee capture",
            "next_goal_stub": "Reach safe house in border town before police track the trail",
            "compression": "full"
        },
        
        "chain_link": {
            "type": "reactive_decision",
            "feeds_proactive": "Reach safe house in border town before police track the trail",
            "validates_chain": True
        }
    }
    
    return {
        "scene_pair": [proactive_scene, reactive_scene],
        "chain_validation": {
            "proactive_setback_seeds_reactive": True,
            "reactive_decision_creates_next_goal": True, 
            "pov_consistency": True,
            "emotional_progression": "setback_frustration -> decision_resolve"
        },
        "metadata": {
            "demonstrates": ["Scene chaining", "Setback->Reactive", "Decision->Goal", "POV consistency"],
            "created_at": datetime.utcnow().isoformat()
        }
    }


def validate_example_scenes() -> Dict[str, bool]:
    """
    Validate that example scenes follow all Snowflake Method requirements.
    
    Returns:
        Validation results for each scene
    """
    
    proactive = create_example_proactive_scene()
    reactive = create_example_reactive_scene() 
    scene_pair = create_example_scene_pair()
    
    validation_results = {
        "proactive_scene_valid": True,
        "reactive_scene_valid": True, 
        "scene_pair_chains_valid": True,
        "validation_details": {}
    }
    
    # Validate proactive scene structure
    proactive_checks = {
        "has_goal": "goal" in proactive.get("proactive", {}),
        "has_conflict": "conflict" in proactive.get("proactive", {}),
        "has_setback": "setback" in proactive.get("proactive", {}),
        "goal_5_point_valid": all(proactive["proactive"]["goal_validation"].values()),
        "has_scene_crucible": bool(proactive.get("scene_crucible")),
        "pov_specified": bool(proactive.get("pov_character"))
    }
    
    validation_results["validation_details"]["proactive"] = proactive_checks
    validation_results["proactive_scene_valid"] = all(proactive_checks.values())
    
    # Validate reactive scene structure  
    reactive_checks = {
        "has_reaction": "reaction" in reactive.get("reactive", {}),
        "has_dilemma": "dilemma_options" in reactive.get("reactive", {}),
        "has_decision": "decision" in reactive.get("reactive", {}),
        "has_next_goal": "next_goal_stub" in reactive.get("reactive", {}),
        "dilemma_has_bad_options": len(reactive["reactive"]["dilemma_options"]) >= 3,
        "has_scene_crucible": bool(reactive.get("scene_crucible")),
        "pov_specified": bool(reactive.get("pov_character"))
    }
    
    validation_results["validation_details"]["reactive"] = reactive_checks
    validation_results["reactive_scene_valid"] = all(reactive_checks.values())
    
    # Validate scene chaining
    chain_checks = {
        "scenes_connect": scene_pair["chain_validation"]["proactive_setback_seeds_reactive"],
        "decision_creates_goal": scene_pair["chain_validation"]["reactive_decision_creates_next_goal"],
        "pov_consistency": scene_pair["chain_validation"]["pov_consistency"]
    }
    
    validation_results["validation_details"]["chaining"] = chain_checks
    validation_results["scene_pair_chains_valid"] = all(chain_checks.values())
    
    return validation_results


# Export the example scenes for use by other modules
EXAMPLE_SCENES = {
    "proactive": create_example_proactive_scene(),
    "reactive": create_example_reactive_scene(),
    "scene_pair": create_example_scene_pair()
}