"""
Scene Drafting Service

This implements TaskMaster Task 44: Scene Drafting Service
Converts validated Scene Cards into prose following Snowflake Method structures.
"""

from .service import SceneDraftingService, DraftingRequest, DraftingResponse
from .prose_generators import ProactiveProseGenerator, ReactiveProseGenerator
from .pov_handler import POVHandler, POVType, TenseType
from .exposition_tracker import ExpositionTracker, ExpositionBudget

__all__ = [
    # Core drafting service
    "SceneDraftingService", "DraftingRequest", "DraftingResponse",
    # Prose generators
    "ProactiveProseGenerator", "ReactiveProseGenerator", 
    # POV and tense handling
    "POVHandler", "POVType", "TenseType",
    # Exposition tracking
    "ExpositionTracker", "ExpositionBudget"
]