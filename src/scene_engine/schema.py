"""
JSON Schema Generation for Scene Cards

This implements subtask 41.2: Author JSON Schema for Scene Card
Uses Pydantic's built-in JSON schema generation capabilities.
"""

import json
from typing import Dict, Any
from .models import SceneCard, SceneGenerationRequest, SceneGenerationResponse, ValidationResult


def generate_scene_card_schema() -> Dict[str, Any]:
    """Generate JSON schema for SceneCard model"""
    return SceneCard.schema()


def generate_validation_result_schema() -> Dict[str, Any]:
    """Generate JSON schema for ValidationResult model"""
    return ValidationResult.schema()


def generate_scene_generation_request_schema() -> Dict[str, Any]:
    """Generate JSON schema for SceneGenerationRequest model"""
    return SceneGenerationRequest.schema()


def generate_scene_generation_response_schema() -> Dict[str, Any]:
    """Generate JSON schema for SceneGenerationResponse model"""
    return SceneGenerationResponse.schema()


def export_schemas_to_file(filepath: str) -> None:
    """Export all schemas to a JSON file"""
    schemas = {
        "SceneCard": generate_scene_card_schema(),
        "ValidationResult": generate_validation_result_schema(),
        "SceneGenerationRequest": generate_scene_generation_request_schema(),
        "SceneGenerationResponse": generate_scene_generation_response_schema()
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(schemas, f, indent=2, ensure_ascii=False)


def get_scene_card_example() -> Dict[str, Any]:
    """Get example Scene Card data matching the PRD"""
    
    # Proactive example from PRD (Dirk parachute)
    proactive_example = {
        "scene_type": "proactive",
        "pov": "Dirk", 
        "viewpoint": "third",
        "tense": "past",
        "scene_crucible": "Night drop in occupied France; survival now or capture.",
        "place": "Airspace over occupied France",
        "time": "Night, 1944",
        "proactive": {
            "goal": {
                "text": "Hole up for the night after drop",
                "fits_time": True,
                "possible": True,
                "difficult": True,
                "fits_pov": True,
                "concrete_objective": True
            },
            "conflict_obstacles": [
                {"try_number": 1, "obstacle": "Anti-aircraft fire"},
                {"try_number": 2, "obstacle": "German fighter plane"},
                {"try_number": 3, "obstacle": "Engine catches fire, forced jump"}
            ],
            "outcome": {
                "type": "setback",
                "rationale": "Breaks leg and passes out on landing"
            }
        },
        "exposition_used": [
            "Occupied France location needed for immediate danger context",
            "Parachute operation context for goal understanding"
        ],
        "chain_link": "setback→Elise hears something (seed for Reactive scene)"
    }

    # Reactive example from PRD (Goldilocks pepper spray)  
    reactive_example = {
        "scene_type": "reactive",
        "pov": "Goldilocks",
        "viewpoint": "third", 
        "tense": "past",
        "scene_crucible": "Cornered now by Tiny Pig; if she hesitates, she's overpowered.",
        "place": "Narrow corridor",
        "time": "Present moment",
        "reactive": {
            "reaction": "Adrenaline spike; fear mixed with hardening resolve.",
            "dilemma_options": [
                {
                    "option": "Try to slip past him",
                    "why_bad": "He's blocking the exit; high risk of being grabbed"
                },
                {
                    "option": "Call for help on phone",
                    "why_bad": "No time; already dropped the phone in panic"
                },
                {
                    "option": "Wait him out, hope he backs down",
                    "why_bad": "He's advancing; being cornered makes it worse"
                },
                {
                    "option": "Use pepper spray",
                    "why_bad": "Escalates the confrontation; creates legal risk"
                }
            ],
            "decision": "Use pepper spray now despite risk - it's a forcing move that creates space",
            "next_goal_stub": "Escape the corridor before backup arrives",
            "compression": "full"
        },
        "exposition_used": [
            "Corridor layout needed for spatial understanding",
            "Pepper spray availability for decision option"
        ],
        "chain_link": "decision→next proactive goal (escape corridor)"
    }
    
    return {
        "proactive_example": proactive_example,
        "reactive_example": reactive_example
    }


if __name__ == "__main__":
    # Generate and save schemas
    export_schemas_to_file("scene_card_schemas.json")
    print("Scene Card JSON schemas generated successfully!")
    
    # Print example
    examples = get_scene_card_example()
    print("\nProactive Scene Example:")
    print(json.dumps(examples["proactive_example"], indent=2))
    
    print("\nReactive Scene Example:")  
    print(json.dumps(examples["reactive_example"], indent=2))