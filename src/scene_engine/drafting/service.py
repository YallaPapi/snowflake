"""
Scene Drafting Service Implementation

TaskMaster Task 44: Scene Drafting Service
Converts validated Scene Cards into structured prose following Snowflake Method principles.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from ..models import SceneCard, SceneType
from .prose_generators import ProactiveProseGenerator, ReactiveProseGenerator
from .pov_handler import POVHandler, POVType, TenseType
from .exposition_tracker import ExpositionTracker, ExpositionBudget


class DraftingStatus(Enum):
    """Status of drafting operation"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class DraftingRequest:
    """Request for Scene Card to prose conversion"""
    scene_card: SceneCard
    
    # POV and tense overrides (optional - will use Scene Card defaults)
    pov_override: Optional[POVType] = None
    tense_override: Optional[TenseType] = None
    
    # Exposition budget settings
    exposition_budget: Optional[ExpositionBudget] = None
    strict_exposition_enforcement: bool = True
    
    # Prose generation settings
    target_word_count: Optional[int] = None
    maintain_scene_crucible_focus: bool = True
    include_sensory_details: bool = True
    dialogue_percentage_target: float = 0.3  # 30% dialogue target
    
    # Validation settings
    validate_structure_adherence: bool = True
    validate_pov_consistency: bool = True


@dataclass
class DraftingResponse:
    """Response from Scene Card drafting operation"""
    success: bool
    status: DraftingStatus
    
    # Generated content
    prose_content: str = ""
    word_count: int = 0
    
    # Structure analysis
    structure_adherence: Dict[str, bool] = field(default_factory=dict)
    pov_consistency: bool = True
    tense_consistency: bool = True
    
    # Exposition analysis
    exposition_usage: Dict[str, Any] = field(default_factory=dict)
    exposition_budget_exceeded: bool = False
    
    # Quality metrics
    dialogue_percentage: float = 0.0
    scene_crucible_maintenance: float = 1.0
    sensory_detail_score: float = 0.0
    
    # Processing info
    processing_time_seconds: float = 0.0
    generator_used: str = ""
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class SceneDraftingService:
    """
    TaskMaster Task 44: Scene Drafting Service
    
    Converts validated Scene Cards into prose following strict adherence to:
    - Proactive scenes: Goal-Conflict-Setback/Value (G-C-S/V) structure
    - Reactive scenes: Reaction-Dilemma-Decision (R-D-D) structure
    - POV and tense consistency
    - Exposition budget tracking
    - Scene crucible focus maintenance
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SceneDraftingService")
        
        # Initialize prose generators
        self.proactive_generator = ProactiveProseGenerator()
        self.reactive_generator = ReactiveProseGenerator()
        
        # Initialize handlers
        self.pov_handler = POVHandler()
        self.exposition_tracker = ExpositionTracker()
        
        # Statistics
        self.drafting_history = []
        
    def draft_scene_prose(self, request: DraftingRequest) -> DraftingResponse:
        """
        Convert Scene Card to prose
        
        TaskMaster Task 44 - Core functionality:
        - Takes validated Scene Card as input
        - Generates prose following strict structure adherence
        - Handles POV and tense consistently
        - Tracks exposition budget
        - Maintains scene crucible focus
        """
        start_time = datetime.now()
        
        response = DraftingResponse(
            success=False,
            status=DraftingStatus.FAILED
        )
        
        try:
            self.logger.info(f"Starting prose drafting for scene: {request.scene_card.scene_id}")
            
            # Validate Scene Card
            if not self._validate_scene_card(request.scene_card, response):
                return response
            
            # Determine POV and tense
            pov_type, tense_type = self._determine_pov_and_tense(request)
            
            # Initialize exposition tracking
            exposition_budget = request.exposition_budget or self._create_default_exposition_budget()
            self.exposition_tracker.initialize_budget(exposition_budget)
            
            # Generate prose based on scene type
            if request.scene_card.scene_type == SceneType.PROACTIVE:
                prose_content = self._generate_proactive_prose(request, pov_type, tense_type)
                response.generator_used = "ProactiveProseGenerator"
            else:  # REACTIVE
                prose_content = self._generate_reactive_prose(request, pov_type, tense_type)
                response.generator_used = "ReactiveProseGenerator"
            
            if not prose_content:
                response.error_message = "Failed to generate prose content"
                return response
            
            # Apply POV and tense handling
            processed_prose = self.pov_handler.process_prose(
                prose_content, pov_type, tense_type
            )
            
            response.prose_content = processed_prose
            response.word_count = len(processed_prose.split())
            
            # Analyze generated prose
            self._analyze_prose_quality(request, response)
            
            # Validate structure adherence if requested
            if request.validate_structure_adherence:
                response.structure_adherence = self._validate_structure_adherence(
                    request.scene_card, response.prose_content
                )
            
            # Validate POV consistency if requested
            if request.validate_pov_consistency:
                response.pov_consistency = self.pov_handler.validate_consistency(
                    response.prose_content, pov_type
                )
                response.tense_consistency = self.pov_handler.validate_tense_consistency(
                    response.prose_content, tense_type
                )
            
            # Check exposition budget
            response.exposition_usage = self.exposition_tracker.get_usage_report()
            response.exposition_budget_exceeded = self.exposition_tracker.is_budget_exceeded()
            
            if response.exposition_budget_exceeded and request.strict_exposition_enforcement:
                response.warnings.append("Exposition budget exceeded")
                response.status = DraftingStatus.PARTIAL
            else:
                response.status = DraftingStatus.SUCCESS
            
            response.success = True
            
        except Exception as e:
            self.logger.error(f"Drafting error: {e}")
            response.error_message = str(e)
            response.status = DraftingStatus.FAILED
        
        finally:
            response.processing_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # Add to history
            self.drafting_history.append({
                'request': request,
                'response': response,
                'timestamp': start_time
            })
        
        return response
    
    def _validate_scene_card(self, scene_card: SceneCard, response: DraftingResponse) -> bool:
        """Validate Scene Card has required fields for prose generation"""
        
        if not scene_card.scene_crucible:
            response.error_message = "Scene Card missing scene_crucible - required for prose generation"
            return False
        
        if scene_card.scene_type == SceneType.PROACTIVE:
            if not hasattr(scene_card, 'proactive') or not scene_card.proactive:
                response.error_message = "Proactive Scene Card missing proactive structure"
                return False
            
            proactive = scene_card.proactive
            if not all([proactive.goal, proactive.conflict, proactive.setback]):
                response.error_message = "Proactive scene missing required G-C-S elements"
                return False
        
        else:  # REACTIVE
            if not hasattr(scene_card, 'reactive') or not scene_card.reactive:
                response.error_message = "Reactive Scene Card missing reactive structure"
                return False
            
            reactive = scene_card.reactive
            if not all([reactive.reaction, reactive.dilemma, reactive.decision]):
                response.error_message = "Reactive scene missing required R-D-D elements"
                return False
        
        return True
    
    def _determine_pov_and_tense(self, request: DraftingRequest) -> tuple[POVType, TenseType]:
        """Determine POV and tense for prose generation"""
        
        # Use overrides if provided
        pov_type = request.pov_override
        tense_type = request.tense_override
        
        # Otherwise use Scene Card values
        if not pov_type:
            pov_map = {
                'first': POVType.FIRST_PERSON,
                'third_limited': POVType.THIRD_LIMITED,
                'third_omniscient': POVType.THIRD_OMNISCIENT
            }
            pov_type = pov_map.get(request.scene_card.pov, POVType.THIRD_LIMITED)
        
        if not tense_type:
            tense_map = {
                'past': TenseType.PAST,
                'present': TenseType.PRESENT,
                'future': TenseType.FUTURE
            }
            tense_type = tense_map.get(request.scene_card.tense, TenseType.PAST)
        
        return pov_type, tense_type
    
    def _create_default_exposition_budget(self) -> ExpositionBudget:
        """Create default exposition budget"""
        return ExpositionBudget(
            max_exposition_percentage=0.15,  # 15% max exposition
            max_backstory_sentences=2,
            max_world_building_sentences=1,
            allow_character_thoughts=True
        )
    
    def _generate_proactive_prose(self, request: DraftingRequest, 
                                 pov_type: POVType, tense_type: TenseType) -> str:
        """Generate prose for proactive scene following G-C-S/V structure"""
        
        return self.proactive_generator.generate_prose(
            scene_card=request.scene_card,
            pov_type=pov_type,
            tense_type=tense_type,
            exposition_tracker=self.exposition_tracker,
            target_word_count=request.target_word_count,
            dialogue_target=request.dialogue_percentage_target,
            maintain_crucible_focus=request.maintain_scene_crucible_focus,
            include_sensory_details=request.include_sensory_details
        )
    
    def _generate_reactive_prose(self, request: DraftingRequest,
                                pov_type: POVType, tense_type: TenseType) -> str:
        """Generate prose for reactive scene following R-D-D structure"""
        
        return self.reactive_generator.generate_prose(
            scene_card=request.scene_card,
            pov_type=pov_type,
            tense_type=tense_type,
            exposition_tracker=self.exposition_tracker,
            target_word_count=request.target_word_count,
            dialogue_target=request.dialogue_percentage_target,
            maintain_crucible_focus=request.maintain_scene_crucible_focus,
            include_sensory_details=request.include_sensory_details
        )
    
    def _analyze_prose_quality(self, request: DraftingRequest, response: DraftingResponse):
        """Analyze quality metrics of generated prose"""
        
        prose = response.prose_content
        words = prose.split()
        
        # Calculate dialogue percentage
        dialogue_words = 0
        in_dialogue = False
        for word in words:
            if '"' in word:
                in_dialogue = not in_dialogue
            if in_dialogue:
                dialogue_words += 1
        
        response.dialogue_percentage = dialogue_words / len(words) if words else 0.0
        
        # Calculate scene crucible maintenance (simplified metric)
        crucible_keywords = request.scene_card.scene_crucible.lower().split()
        crucible_mentions = sum(1 for word in prose.lower().split() if word in crucible_keywords)
        response.scene_crucible_maintenance = min(1.0, crucible_mentions / len(crucible_keywords))
        
        # Calculate sensory detail score (simplified)
        sensory_words = ['saw', 'heard', 'felt', 'smelled', 'tasted', 'touched', 'looked', 'sounded']
        sensory_count = sum(1 for word in prose.lower().split() if word in sensory_words)
        response.sensory_detail_score = min(1.0, sensory_count / max(len(words) // 50, 1))
    
    def _validate_structure_adherence(self, scene_card: SceneCard, prose: str) -> Dict[str, bool]:
        """Validate prose follows required scene structure"""
        
        adherence = {}
        
        if scene_card.scene_type == SceneType.PROACTIVE:
            # Check for G-C-S/V structure markers in prose
            goal_keywords = scene_card.proactive.goal.lower().split()[:3]  # First 3 words
            conflict_keywords = scene_card.proactive.conflict.lower().split()[:3]
            setback_keywords = scene_card.proactive.setback.lower().split()[:3]
            
            prose_lower = prose.lower()
            adherence['goal_present'] = any(keyword in prose_lower for keyword in goal_keywords)
            adherence['conflict_present'] = any(keyword in prose_lower for keyword in conflict_keywords)
            adherence['setback_present'] = any(keyword in prose_lower for keyword in setback_keywords)
            
        else:  # REACTIVE
            # Check for R-D-D structure markers in prose
            reaction_keywords = scene_card.reactive.reaction.lower().split()[:3]
            dilemma_keywords = scene_card.reactive.dilemma.lower().split()[:3]  
            decision_keywords = scene_card.reactive.decision.lower().split()[:3]
            
            prose_lower = prose.lower()
            adherence['reaction_present'] = any(keyword in prose_lower for keyword in reaction_keywords)
            adherence['dilemma_present'] = any(keyword in prose_lower for keyword in dilemma_keywords)
            adherence['decision_present'] = any(keyword in prose_lower for keyword in decision_keywords)
        
        return adherence
    
    def get_drafting_statistics(self) -> Dict[str, Any]:
        """Get drafting service statistics"""
        
        if not self.drafting_history:
            return {'total_drafts': 0}
        
        total_drafts = len(self.drafting_history)
        successful_drafts = sum(1 for entry in self.drafting_history if entry['response'].success)
        
        avg_word_count = sum(entry['response'].word_count for entry in self.drafting_history) / total_drafts
        avg_processing_time = sum(entry['response'].processing_time_seconds for entry in self.drafting_history) / total_drafts
        
        return {
            'total_drafts': total_drafts,
            'successful_drafts': successful_drafts,
            'success_rate': successful_drafts / total_drafts,
            'average_word_count': avg_word_count,
            'average_processing_time': avg_processing_time,
            'generators_used': {
                'proactive': sum(1 for entry in self.drafting_history 
                               if entry['response'].generator_used == "ProactiveProseGenerator"),
                'reactive': sum(1 for entry in self.drafting_history 
                               if entry['response'].generator_used == "ReactiveProseGenerator")
            }
        }