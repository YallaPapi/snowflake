"""
Scene Planners

This implements subtasks 42.2 & 42.3: Proactive and Reactive Scene Planning Logic
Handles the core planning logic for both scene types following the Snowflake Method.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio

from ..models import (
    SceneCard, SceneType, ProactiveScene, ReactiveScene,
    GoalCriteria, ConflictObstacle, Outcome, DilemmaOption,
    OutcomeType, CompressionType, ViewpointType, TenseType
)
from .service import ProactiveScenePlanningRequest, ReactiveScenePlanningRequest


class BaseScenePlanner(ABC):
    """Base class for scene planners"""
    
    def __init__(self, ai_generator=None):
        self.ai_generator = ai_generator
        self.suggestions = []
        self.warnings = []

    def get_suggestions(self) -> List[str]:
        """Get planning suggestions"""
        return self.suggestions.copy()

    def get_warnings(self) -> List[str]:
        """Get planning warnings"""
        return self.warnings.copy()

    def clear_feedback(self):
        """Clear suggestions and warnings"""
        self.suggestions.clear()
        self.warnings.clear()

    @abstractmethod
    async def plan_scene(self, request) -> SceneCard:
        """Plan a scene based on the request"""
        pass


class ProactiveScenePlanner(BaseScenePlanner):
    """Planner for Proactive scenes: Goal → Conflict → Setback/Victory"""

    async def plan_scene(self, request: ProactiveScenePlanningRequest) -> SceneCard:
        """Plan a proactive scene following G-C-S structure"""
        
        self.clear_feedback()
        
        # Step 1: Generate the Scene Crucible
        scene_crucible = await self._generate_scene_crucible(request)
        
        # Step 2: Create the Goal (must pass 5-point validation)
        goal = await self._generate_goal(request)
        
        # Step 3: Generate escalating obstacles
        obstacles = await self._generate_obstacles(request, goal)
        
        # Step 4: Determine outcome (default to Setback per PRD)
        outcome = await self._determine_outcome(request, goal, obstacles)
        
        # Step 5: Generate chain link
        chain_link = self._generate_chain_link(outcome)
        
        # Build the proactive scene
        proactive_scene = ProactiveScene(
            goal=goal,
            conflict_obstacles=obstacles,
            outcome=outcome
        )
        
        # Build the complete scene card
        scene_card = SceneCard(
            scene_type=SceneType.PROACTIVE,
            pov=request.pov,
            viewpoint=request.viewpoint,
            tense=request.tense,
            scene_crucible=scene_crucible,
            place=request.place,
            time=request.time,
            proactive=proactive_scene,
            exposition_used=self._determine_exposition_budget(request),
            chain_link=chain_link
        )
        
        return scene_card

    async def _generate_scene_crucible(self, request: ProactiveScenePlanningRequest) -> str:
        """Generate Scene Crucible focusing on immediate danger 'now'"""
        
        # If we have AI generator, use it; otherwise create a template
        if self.ai_generator:
            # This would call the AI service
            crucible_prompt = f"""
            Create a Scene Crucible for a proactive scene:
            - POV: {request.pov}
            - Place: {request.place}
            - Time: {request.time}
            - Context: {request.story_context}
            
            The Scene Crucible must:
            1. Focus on immediate danger/pressure RIGHT NOW
            2. Be 1-2 sentences maximum
            3. No backstory or world-building
            4. Make the reader feel the urgency
            """
            # result = await self.ai_generator.generate(crucible_prompt)
            # return result.text
        
        # Template fallback
        context_hint = ""
        if request.story_context.get('danger_type'):
            context_hint = f" from {request.story_context['danger_type']}"
        
        return f"At {request.place} now, {request.pov} faces immediate danger{context_hint}; failure means disaster."

    async def _generate_goal(self, request: ProactiveScenePlanningRequest) -> GoalCriteria:
        """Generate goal that passes all 5 criteria"""
        
        # Use suggested goal if provided
        goal_text = request.desired_goal
        
        if not goal_text:
            # Generate goal based on context
            if request.story_context.get('mission'):
                goal_text = f"Complete {request.story_context['mission']} before {request.time_available or 'time runs out'}"
            else:
                goal_text = f"Reach safety at {request.place} within available time"
        
        # Validate the 5 criteria
        goal = GoalCriteria(
            text=goal_text,
            fits_time=self._validate_goal_fits_time(goal_text, request.time_available),
            possible=self._validate_goal_possible(goal_text, request),
            difficult=self._validate_goal_difficult(goal_text, request),
            fits_pov=self._validate_goal_fits_pov(goal_text, request.pov, request.character_goals),
            concrete_objective=self._validate_goal_concrete(goal_text)
        )
        
        # Add suggestions if criteria fail
        if not goal.fits_time:
            self.suggestions.append("Consider reducing goal scope to fit available time")
        if not goal.possible:
            self.warnings.append("Goal may be impossible - consider character capabilities")
        if not goal.difficult:
            self.suggestions.append("Goal should be more challenging to create meaningful conflict")
        if not goal.fits_pov:
            self.warnings.append("Goal doesn't align with character motivations")
        if not goal.concrete_objective:
            self.suggestions.append("Make goal more specific and measurable")
        
        return goal

    def _validate_goal_fits_time(self, goal_text: str, time_available: Optional[str]) -> bool:
        """Check if goal fits available time"""
        if not time_available:
            return True  # Assume reasonable if no time constraint given
        
        # Simple heuristic - could be more sophisticated
        urgent_indicators = ['immediately', 'now', 'quickly', 'before', 'within']
        return any(indicator in goal_text.lower() for indicator in urgent_indicators)

    def _validate_goal_possible(self, goal_text: str, request: ProactiveScenePlanningRequest) -> bool:
        """Check if goal is achievable"""
        # Basic validation - in real implementation would be more sophisticated
        impossible_indicators = ['impossible', 'cannot', 'unable', 'never']
        return not any(indicator in goal_text.lower() for indicator in impossible_indicators)

    def _validate_goal_difficult(self, goal_text: str, request: ProactiveScenePlanningRequest) -> bool:
        """Check if goal is challenging"""
        easy_indicators = ['easy', 'simple', 'trivial', 'effortless']
        difficulty_indicators = ['difficult', 'challenging', 'against odds', 'despite', 'overcome']
        
        if any(easy in goal_text.lower() for easy in easy_indicators):
            return False
        
        # If obstacles are suggested, goal is probably difficult
        if request.obstacles_suggested:
            return True
            
        return any(diff in goal_text.lower() for diff in difficulty_indicators)

    def _validate_goal_fits_pov(self, goal_text: str, pov: str, character_goals: List[str]) -> bool:
        """Check if goal fits POV character"""
        if not character_goals:
            return True  # Assume fits if no character goals specified
        
        # Check if goal aligns with any character goals
        goal_lower = goal_text.lower()
        return any(char_goal.lower() in goal_lower for char_goal in character_goals)

    def _validate_goal_concrete(self, goal_text: str) -> bool:
        """Check if goal is concrete and measurable"""
        abstract_indicators = ['somehow', 'maybe', 'possibly', 'generally', 'feel better']
        concrete_indicators = ['reach', 'get to', 'complete', 'find', 'escape', 'deliver', 'obtain']
        
        if any(abstract in goal_text.lower() for abstract in abstract_indicators):
            return False
            
        return any(concrete in goal_text.lower() for concrete in concrete_indicators)

    async def _generate_obstacles(self, request: ProactiveScenePlanningRequest, goal: GoalCriteria) -> List[ConflictObstacle]:
        """Generate escalating obstacles"""
        
        obstacles = []
        
        # Use suggested obstacles if provided
        if request.obstacles_suggested:
            for i, obstacle_text in enumerate(request.obstacles_suggested[:5]):  # Max 5 obstacles
                obstacles.append(ConflictObstacle(
                    try_number=i + 1,
                    obstacle=obstacle_text
                ))
        else:
            # Generate default obstacles based on context
            base_obstacles = [
                "Initial attempt blocked by unexpected barrier",
                "Security/opposition notices the attempt",
                "Time pressure increases with new complication",
                "Allies are compromised or unavailable",
                "Final desperate attempt as situation deteriorates"
            ]
            
            for i, obstacle_text in enumerate(base_obstacles[:3]):  # Start with 3
                obstacles.append(ConflictObstacle(
                    try_number=i + 1,
                    obstacle=obstacle_text
                ))
        
        # Ensure escalation (try numbers increase)
        obstacles.sort(key=lambda x: x.try_number)
        
        return obstacles

    async def _determine_outcome(self, request: ProactiveScenePlanningRequest, 
                                goal: GoalCriteria, obstacles: List[ConflictObstacle]) -> Outcome:
        """Determine scene outcome - default to Setback per PRD"""
        
        # Default to Setback as per PRD policy
        outcome_type = OutcomeType.SETBACK
        rationale = "Character fails to achieve goal due to escalating obstacles"
        
        # Check if Victory makes sense (rare, prefer mixed)
        if request.story_context.get('allow_victory'):
            if request.difficulty_level == "low":
                outcome_type = OutcomeType.MIXED
                rationale = "Character achieves goal but at significant cost"
            else:
                # Keep as Setback - Victory should be rare
                self.suggestions.append("Consider mixed victory instead of pure victory")
        
        # Specific rationale based on obstacles
        if obstacles:
            final_obstacle = obstacles[-1].obstacle
            rationale = f"Character overwhelmed by final obstacle: {final_obstacle}"
        
        return Outcome(
            type=outcome_type,
            rationale=rationale
        )

    def _generate_chain_link(self, outcome: Outcome) -> str:
        """Generate chain link based on outcome"""
        if outcome.type == OutcomeType.SETBACK:
            return "setback→triggers reactive scene (emotional processing needed)"
        elif outcome.type == OutcomeType.VICTORY:
            return "victory→enables next proactive goal"
        else:  # MIXED
            return "mixed outcome→reactive scene (process costs) or new proactive goal"

    def _determine_exposition_budget(self, request: ProactiveScenePlanningRequest) -> List[str]:
        """Determine what exposition is needed 'right here, right now'"""
        exposition = []
        
        # Only include exposition that's immediately necessary
        if request.place and "unknown" not in request.place.lower():
            exposition.append(f"Location ({request.place}) needed for spatial understanding of obstacles")
        
        if request.time and any(urgent in request.time.lower() for urgent in ['deadline', 'before', 'limited']):
            exposition.append(f"Time constraint ({request.time}) needed for goal urgency")
        
        # Character capabilities if relevant to goal
        if request.character_goals:
            exposition.append("Character motivation needed to understand goal relevance")
        
        return exposition


class ReactiveScenePlanner(BaseScenePlanner):
    """Planner for Reactive scenes: Reaction → Dilemma → Decision"""

    async def plan_scene(self, request: ReactiveScenePlanningRequest) -> SceneCard:
        """Plan a reactive scene following R-D-D structure"""
        
        self.clear_feedback()
        
        # Step 1: Generate Scene Crucible  
        scene_crucible = await self._generate_scene_crucible(request)
        
        # Step 2: Generate emotional Reaction
        reaction = await self._generate_reaction(request)
        
        # Step 3: Create Dilemma (all options bad)
        dilemma_options = await self._generate_dilemma(request)
        
        # Step 4: Make Decision (least-bad, forcing, firm)
        decision = await self._make_decision(request, dilemma_options)
        
        # Step 5: Generate next goal stub
        next_goal_stub = self._generate_next_goal_stub(decision)
        
        # Step 6: Determine compression
        compression = self._determine_compression(request)
        
        # Step 7: Generate chain link
        chain_link = self._generate_chain_link(decision)
        
        # Build the reactive scene
        reactive_scene = ReactiveScene(
            reaction=reaction,
            dilemma_options=dilemma_options,
            decision=decision,
            next_goal_stub=next_goal_stub,
            compression=compression
        )
        
        # Build complete scene card
        scene_card = SceneCard(
            scene_type=SceneType.REACTIVE,
            pov=request.pov,
            viewpoint=request.viewpoint,
            tense=request.tense,
            scene_crucible=scene_crucible,
            place=request.place,
            time=request.time,
            reactive=reactive_scene,
            exposition_used=self._determine_exposition_budget(request),
            chain_link=chain_link
        )
        
        return scene_card

    async def _generate_scene_crucible(self, request: ReactiveScenePlanningRequest) -> str:
        """Generate Scene Crucible for reactive scene"""
        
        if self.ai_generator:
            # Would use AI generator
            pass
        
        # Template fallback
        return f"Reeling from {request.triggering_setback} now at {request.place}; must decide quickly or face worse consequences."

    async def _generate_reaction(self, request: ReactiveScenePlanningRequest) -> str:
        """Generate emotional reaction to setback"""
        
        # Use provided emotional state or infer from setback
        if request.character_emotional_state:
            base_emotion = request.character_emotional_state
        else:
            # Infer from setback type
            if any(word in request.triggering_setback.lower() for word in ['fail', 'defeat', 'loss']):
                base_emotion = "frustrated and angry"
            elif any(word in request.triggering_setback.lower() for word in ['danger', 'threat', 'attack']):
                base_emotion = "fearful but determined"
            else:
                base_emotion = "shocked and uncertain"
        
        return f"{request.pov} feels {base_emotion} after {request.triggering_setback.lower()}. The immediate reality hits hard, but there's no time for wallowing - action is needed."

    async def _generate_dilemma(self, request: ReactiveScenePlanningRequest) -> List[DilemmaOption]:
        """Generate dilemma with all bad options"""
        
        options = []
        
        # Use suggested options if provided
        if request.available_options:
            for option_text in request.available_options:
                # Need to determine why each is bad
                why_bad = self._determine_why_option_bad(option_text, request)
                options.append(DilemmaOption(
                    option=option_text,
                    why_bad=why_bad
                ))
        else:
            # Generate default bad options
            default_options = [
                ("Retreat/give up", "Abandons mission and lets others down"),
                ("Fight back aggressively", "Likely to escalate and make things worse"),
                ("Try to negotiate", "Shows weakness and may not work"),
                ("Wait for help", "Help may not come and situation could deteriorate"),
                ("Take desperate action", "High risk of backfiring spectacularly")
            ]
            
            for option_text, why_bad in default_options[:4]:  # Take first 4
                options.append(DilemmaOption(
                    option=option_text,
                    why_bad=why_bad
                ))
        
        # Ensure all options are genuinely bad
        if len(options) < 2:
            self.warnings.append("Dilemma needs at least 2 bad options")
        
        return options

    def _determine_why_option_bad(self, option: str, request: ReactiveScenePlanningRequest) -> str:
        """Determine why an option is bad"""
        
        # Simple heuristic based on option type
        option_lower = option.lower()
        
        if any(word in option_lower for word in ['run', 'flee', 'escape', 'retreat']):
            return "Abandons responsibility and may lead to worse consequences for others"
        elif any(word in option_lower for word in ['fight', 'attack', 'confront']):
            return "Likely to escalate violence and create more problems"
        elif any(word in option_lower for word in ['wait', 'delay', 'hope']):
            return "Passive approach may allow situation to deteriorate further"
        elif any(word in option_lower for word in ['lie', 'deceive', 'trick']):
            return "Dishonesty could backfire and destroy trust permanently"
        else:
            return "Significant risks and potential for unintended consequences"

    async def _make_decision(self, request: ReactiveScenePlanningRequest, 
                           dilemma_options: List[DilemmaOption]) -> str:
        """Make decision - least bad, forcing, firm, risk-aware"""
        
        if not dilemma_options:
            return "Choose the least risky path forward despite uncertainty"
        
        # Select the "least bad" option (typically the first one in our context)
        chosen_option = dilemma_options[0].option
        chosen_risk = dilemma_options[0].why_bad
        
        # Make it a forcing move and acknowledge risk
        decision = f"Choose to {chosen_option.lower()} despite the risk that {chosen_risk.lower()}. This forces the situation to change rather than letting it stagnate."
        
        return decision

    def _generate_next_goal_stub(self, decision: str) -> str:
        """Generate next goal stub from decision"""
        
        # Extract action from decision
        if "choose to" in decision.lower():
            action = decision.lower().split("choose to")[1].split("despite")[0].strip()
        else:
            action = "follow through on decision"
        
        return f"Successfully {action} while minimizing negative consequences"

    def _determine_compression(self, request: ReactiveScenePlanningRequest) -> CompressionType:
        """Determine compression level - modern trend is fewer full reactive scenes"""
        
        # Default to FULL but could be configured
        if request.story_context.get('pacing') == 'fast':
            return CompressionType.SUMMARIZED
        elif request.story_context.get('skip_reactive'):
            return CompressionType.SKIP
        else:
            return CompressionType.FULL

    def _generate_chain_link(self, decision: str) -> str:
        """Generate chain link from decision to next proactive goal"""
        return f"decision→next proactive goal (implement decision)"

    def _determine_exposition_budget(self, request: ReactiveScenePlanningRequest) -> List[str]:
        """Determine needed exposition for reactive scene"""
        exposition = []
        
        # Minimal exposition for reactive scenes
        if request.triggering_setback:
            exposition.append(f"Setback context needed to understand emotional reaction")
        
        if request.character_emotional_state:
            exposition.append(f"Character emotional state needed for proportional reaction")
        
        return exposition


# Factory function for creating planners
def create_planner(scene_type: SceneType, ai_generator=None) -> BaseScenePlanner:
    """Factory function to create appropriate planner"""
    if scene_type == SceneType.PROACTIVE:
        return ProactiveScenePlanner(ai_generator)
    elif scene_type == SceneType.REACTIVE:
        return ReactiveScenePlanner(ai_generator)
    else:
        raise ValueError(f"Unknown scene type: {scene_type}")