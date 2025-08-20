"""
Scene Engine for the Snowflake Auto-Novel Generator

This module implements Randy Ingermanson's Scene Engine from 
"How to Write a Dynamite Scene Using the Snowflake Method"

Main components:
- Scene Card data structures (models.py)
- Scene planning service  
- Scene validation service
- Scene drafting service
- Scene triage service
- Scene chaining system
"""

from .models import (
    SceneCard,
    SceneType,
    ViewpointType, 
    TenseType,
    OutcomeType,
    CompressionType,
    ProactiveScene,
    ReactiveScene,
    ValidationResult
)

__all__ = [
    'SceneCard',
    'SceneType',
    'ViewpointType', 
    'TenseType',
    'OutcomeType',
    'CompressionType',
    'ProactiveScene',
    'ReactiveScene',
    'ValidationResult'
]