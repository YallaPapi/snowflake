"""
Scene Chaining System

This implements Task 46: Scene Chaining System
Provides data models and logic for connecting scenes following Snowflake Method patterns.
"""

from .models import (
    ChainLink, ChainLinkType, TransitionType, ChainMetadata,
    SceneReference, ChainValidationResult, ChainSequence
)
from .generator import ChainLinkGenerator, TransitionRule, ChainGenerationContext
from .validator import ChainLinkValidator, ChainSequenceValidator
from .service import SceneChainingService, ChainRequest, ChainResponse

__all__ = [
    # Data models
    "ChainLink", "ChainLinkType", "TransitionType", "ChainMetadata",
    "SceneReference", "ChainValidationResult", "ChainSequence",
    # Generation
    "ChainLinkGenerator", "TransitionRule", "ChainGenerationContext",
    # Validation
    "ChainLinkValidator", "ChainSequenceValidator", 
    # Service
    "SceneChainingService", "ChainRequest", "ChainResponse"
]