"""
Prose Generators for Scene Drafting

TaskMaster Task 44.2 & 44.3: Implement prose generation for proactive and reactive scenes
Converts Scene Card structures into prose following Snowflake Method patterns.
"""

from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging

from ..models import SceneCard, SceneType
from .pov_handler import POVType, TenseType
from .exposition_tracker import ExpositionTracker


class ProseGenerator(ABC):
    """Base class for prose generators"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def generate_prose(self, scene_card: SceneCard, pov_type: POVType, 
                      tense_type: TenseType, exposition_tracker: ExpositionTracker,
                      **kwargs) -> str:
        """Generate prose from Scene Card"""
        pass


class ProactiveProseGenerator(ProseGenerator):
    """
    TaskMaster Task 44.2: Implement Prose Generation for Proactive Scenes
    
    Converts proactive Scene Cards to prose following Goal-Conflict-Setback/Value (G-C-S/V) structure.
    Maps Scene Card fields to narrative elements while maintaining scene crucible focus.
    """
    
    def generate_prose(self, scene_card: SceneCard, pov_type: POVType, 
                      tense_type: TenseType, exposition_tracker: ExpositionTracker,
                      target_word_count: Optional[int] = None,
                      dialogue_target: float = 0.3,
                      maintain_crucible_focus: bool = True,
                      include_sensory_details: bool = True) -> str:
        """
        Generate prose for proactive scene following G-C-S/V structure
        
        Structure:
        1. Scene setup with crucible context
        2. Goal establishment and character motivation  
        3. Conflict introduction and escalation
        4. Setback/failure and emotional impact
        5. Value change and scene conclusion
        """
        
        self.logger.debug(f"Generating proactive prose for scene {scene_card.scene_id}")
        
        if not scene_card.proactive:
            raise ValueError("Scene Card missing proactive structure")
        
        proactive = scene_card.proactive
        prose_sections = []
        
        # Calculate target word distribution
        target_words = target_word_count or 800
        words_per_section = target_words // 5
        
        # 1. Scene Setup and Crucible Context
        setup_section = self._generate_setup_section(
            scene_card, exposition_tracker, words_per_section, 
            pov_type, tense_type, include_sensory_details
        )
        prose_sections.append(setup_section)
        
        # 2. Goal Establishment  
        goal_section = self._generate_goal_section(
            proactive.goal, scene_card.pov_character, words_per_section,
            pov_type, tense_type, maintain_crucible_focus
        )
        prose_sections.append(goal_section)
        
        # 3. Conflict Introduction and Escalation
        conflict_section = self._generate_conflict_section(
            proactive.conflict, proactive.goal, words_per_section,
            pov_type, tense_type, dialogue_target, include_sensory_details
        )
        prose_sections.append(conflict_section)
        
        # 4. Setback and Emotional Impact
        setback_section = self._generate_setback_section(
            proactive.setback, proactive.conflict, scene_card.pov_character,
            words_per_section, pov_type, tense_type
        )
        prose_sections.append(setback_section)
        
        # 5. Value Change and Conclusion
        conclusion_section = self._generate_value_change_section(
            proactive.setback, scene_card.scene_crucible, words_per_section,
            pov_type, tense_type, maintain_crucible_focus
        )
        prose_sections.append(conclusion_section)
        
        return "\n\n".join(prose_sections)
    
    def _generate_setup_section(self, scene_card: SceneCard, exposition_tracker: ExpositionTracker,
                               target_words: int, pov_type: POVType, tense_type: TenseType,
                               include_sensory_details: bool) -> str:
        """Generate scene setup with crucible context"""
        
        # Start with scene crucible as foundation
        crucible = scene_card.scene_crucible
        setting = getattr(scene_card, 'setting', 'an unspecified location')
        pov_character = scene_card.pov_character
        
        setup_elements = []
        
        # Establish setting with sensory details if requested
        if include_sensory_details:
            if tense_type == TenseType.PAST:
                setup_elements.append(f"The {setting.lower()} seemed different that morning.")
            else:
                setup_elements.append(f"The {setting.lower()} seems different this morning.")
        else:
            setup_elements.append(f"In the {setting.lower()},")
        
        # Introduce POV character in context of crucible
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                setup_elements.append(f"I found myself facing {crucible.lower()}.")
            else:
                setup_elements.append(f"I find myself facing {crucible.lower()}.")
        else:
            if tense_type == TenseType.PAST:
                setup_elements.append(f"{pov_character} found themselves facing {crucible.lower()}.")
            else:
                setup_elements.append(f"{pov_character} finds themselves facing {crucible.lower()}.")
        
        # Track exposition usage
        exposition_tracker.add_exposition("scene_setup", " ".join(setup_elements))
        
        return " ".join(setup_elements)
    
    def _generate_goal_section(self, goal: str, pov_character: str, target_words: int,
                              pov_type: POVType, tense_type: TenseType, 
                              maintain_crucible_focus: bool) -> str:
        """Generate goal establishment section"""
        
        goal_elements = []
        
        # Character motivation and goal clarity
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                goal_elements.append(f"I knew what I had to do: {goal.lower()}.")
                goal_elements.append("The path forward seemed clear enough.")
            else:
                goal_elements.append(f"I know what I have to do: {goal.lower()}.")
                goal_elements.append("The path forward seems clear enough.")
        else:
            if tense_type == TenseType.PAST:
                goal_elements.append(f"{pov_character} knew what they had to do: {goal.lower()}.")
                goal_elements.append("The path forward seemed clear enough.")
            else:
                goal_elements.append(f"{pov_character} knows what they have to do: {goal.lower()}.")
                goal_elements.append("The path forward seems clear enough.")
        
        # Add determination and commitment
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                goal_elements.append("I steeled myself for what lay ahead.")
            else:
                goal_elements.append("I steel myself for what lies ahead.")
        else:
            if tense_type == TenseType.PAST:
                goal_elements.append(f"{pov_character} steeled themselves for what lay ahead.")
            else:
                goal_elements.append(f"{pov_character} steels themselves for what lies ahead.")
        
        return " ".join(goal_elements)
    
    def _generate_conflict_section(self, conflict: str, goal: str, target_words: int,
                                  pov_type: POVType, tense_type: TenseType, 
                                  dialogue_target: float, include_sensory_details: bool) -> str:
        """Generate conflict introduction and escalation"""
        
        conflict_elements = []
        
        # Conflict emergence
        if tense_type == TenseType.PAST:
            conflict_elements.append(f"But then {conflict.lower()} emerged.")
        else:
            conflict_elements.append(f"But then {conflict.lower()} emerges.")
        
        # Character realization of opposition
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                conflict_elements.append("I realized this would be harder than I thought.")
            else:
                conflict_elements.append("I realize this will be harder than I thought.")
        else:
            if tense_type == TenseType.PAST:
                conflict_elements.append("They realized this would be harder than expected.")
            else:
                conflict_elements.append("They realize this will be harder than expected.")
        
        # Add dialogue if target requires it (simplified)
        if dialogue_target > 0.2:
            if pov_type == POVType.FIRST_PERSON:
                conflict_elements.append('"This changes everything," I said aloud.')
            else:
                conflict_elements.append('"This changes everything," they said.')
        
        # Escalation and resistance
        if include_sensory_details:
            if tense_type == TenseType.PAST:
                conflict_elements.append("The tension could be felt in the air.")
            else:
                conflict_elements.append("The tension can be felt in the air.")
        
        return " ".join(conflict_elements)
    
    def _generate_setback_section(self, setback: str, conflict: str, pov_character: str,
                                 target_words: int, pov_type: POVType, tense_type: TenseType) -> str:
        """Generate setback and emotional impact"""
        
        setback_elements = []
        
        # Setback occurs
        if tense_type == TenseType.PAST:
            setback_elements.append(f"Then {setback.lower()} happened.")
        else:
            setback_elements.append(f"Then {setback.lower()} happens.")
        
        # Emotional impact
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                setback_elements.append("I felt the weight of failure settling in.")
                setback_elements.append("Everything I had worked for seemed to slip away.")
            else:
                setback_elements.append("I feel the weight of failure settling in.")
                setback_elements.append("Everything I have worked for seems to slip away.")
        else:
            if tense_type == TenseType.PAST:
                setback_elements.append(f"{pov_character} felt the weight of failure settling in.")
                setback_elements.append("Everything they had worked for seemed to slip away.")
            else:
                setback_elements.append(f"{pov_character} feels the weight of failure settling in.")
                setback_elements.append("Everything they have worked for seems to slip away.")
        
        return " ".join(setback_elements)
    
    def _generate_value_change_section(self, setback: str, scene_crucible: str, target_words: int,
                                     pov_type: POVType, tense_type: TenseType, 
                                     maintain_crucible_focus: bool) -> str:
        """Generate value change and scene conclusion"""
        
        value_elements = []
        
        # Value change realization
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                value_elements.append("I understood now that things had changed fundamentally.")
            else:
                value_elements.append("I understand now that things have changed fundamentally.")
        else:
            if tense_type == TenseType.PAST:
                value_elements.append("They understood now that things had changed fundamentally.")
            else:
                value_elements.append("They understand now that things have changed fundamentally.")
        
        # Return to crucible if maintaining focus
        if maintain_crucible_focus:
            if tense_type == TenseType.PAST:
                value_elements.append(f"The {scene_crucible.lower()} remained, but everything else was different.")
            else:
                value_elements.append(f"The {scene_crucible.lower()} remains, but everything else is different.")
        
        # Scene conclusion
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                value_elements.append("I had to find another way forward.")
            else:
                value_elements.append("I have to find another way forward.")
        else:
            if tense_type == TenseType.PAST:
                value_elements.append("They had to find another way forward.")
            else:
                value_elements.append("They have to find another way forward.")
        
        return " ".join(value_elements)


class ReactiveProseGenerator(ProseGenerator):
    """
    TaskMaster Task 44.3: Implement Prose Generation for Reactive Scenes
    
    Converts reactive Scene Cards to prose following Reaction-Dilemma-Decision (R-D-D) structure.
    Maps reactive scene schema fields to narrative elements while maintaining scene crucible focus.
    """
    
    def generate_prose(self, scene_card: SceneCard, pov_type: POVType, 
                      tense_type: TenseType, exposition_tracker: ExpositionTracker,
                      target_word_count: Optional[int] = None,
                      dialogue_target: float = 0.3,
                      maintain_crucible_focus: bool = True,
                      include_sensory_details: bool = True) -> str:
        """
        Generate prose for reactive scene following R-D-D structure
        
        Structure:
        1. Scene setup with aftermath context
        2. Emotional reaction to previous events
        3. Dilemma presentation with no good options
        4. Decision making process
        5. Decision execution and consequences
        """
        
        self.logger.debug(f"Generating reactive prose for scene {scene_card.scene_id}")
        
        if not scene_card.reactive:
            raise ValueError("Scene Card missing reactive structure")
        
        reactive = scene_card.reactive
        prose_sections = []
        
        # Calculate target word distribution
        target_words = target_word_count or 800
        words_per_section = target_words // 5
        
        # 1. Scene Setup with Aftermath Context
        setup_section = self._generate_aftermath_setup(
            scene_card, exposition_tracker, words_per_section,
            pov_type, tense_type, include_sensory_details
        )
        prose_sections.append(setup_section)
        
        # 2. Emotional Reaction
        reaction_section = self._generate_reaction_section(
            reactive.reaction, scene_card.pov_character, words_per_section,
            pov_type, tense_type, include_sensory_details
        )
        prose_sections.append(reaction_section)
        
        # 3. Dilemma Presentation
        dilemma_section = self._generate_dilemma_section(
            reactive.dilemma, reactive.reaction, words_per_section,
            pov_type, tense_type, maintain_crucible_focus
        )
        prose_sections.append(dilemma_section)
        
        # 4. Decision Making Process
        decision_process_section = self._generate_decision_process(
            reactive.decision, reactive.dilemma, words_per_section,
            pov_type, tense_type, dialogue_target
        )
        prose_sections.append(decision_process_section)
        
        # 5. Decision Execution and Consequences
        execution_section = self._generate_decision_execution(
            reactive.decision, scene_card.scene_crucible, words_per_section,
            pov_type, tense_type, maintain_crucible_focus
        )
        prose_sections.append(execution_section)
        
        return "\n\n".join(prose_sections)
    
    def _generate_aftermath_setup(self, scene_card: SceneCard, exposition_tracker: ExpositionTracker,
                                 target_words: int, pov_type: POVType, tense_type: TenseType,
                                 include_sensory_details: bool) -> str:
        """Generate scene setup showing aftermath of previous events"""
        
        crucible = scene_card.scene_crucible
        pov_character = scene_card.pov_character
        setting = getattr(scene_card, 'setting', 'the same location')
        
        setup_elements = []
        
        # Aftermath context
        if include_sensory_details:
            if tense_type == TenseType.PAST:
                setup_elements.append(f"The silence in {setting.lower()} felt deafening.")
            else:
                setup_elements.append(f"The silence in {setting.lower()} feels deafening.")
        
        # Character in aftermath
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                setup_elements.append("I sat there, trying to process what had just happened.")
            else:
                setup_elements.append("I sit here, trying to process what just happened.")
        else:
            if tense_type == TenseType.PAST:
                setup_elements.append(f"{pov_character} sat there, trying to process what had just happened.")
            else:
                setup_elements.append(f"{pov_character} sits there, trying to process what just happened.")
        
        # Reference to crucible context
        if tense_type == TenseType.PAST:
            setup_elements.append(f"The {crucible.lower()} remained, but everything else had changed.")
        else:
            setup_elements.append(f"The {crucible.lower()} remains, but everything else has changed.")
        
        exposition_tracker.add_exposition("aftermath_setup", " ".join(setup_elements))
        
        return " ".join(setup_elements)
    
    def _generate_reaction_section(self, reaction: str, pov_character: str, target_words: int,
                                  pov_type: POVType, tense_type: TenseType, 
                                  include_sensory_details: bool) -> str:
        """Generate emotional reaction section"""
        
        reaction_elements = []
        
        # Initial emotional response
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                reaction_elements.append(f"I felt {reaction.lower()} wash over me.")
            else:
                reaction_elements.append(f"I feel {reaction.lower()} wash over me.")
        else:
            if tense_type == TenseType.PAST:
                reaction_elements.append(f"{pov_character} felt {reaction.lower()} wash over them.")
            else:
                reaction_elements.append(f"{pov_character} feels {reaction.lower()} wash over them.")
        
        # Physical manifestation if sensory details included
        if include_sensory_details:
            if pov_type == POVType.FIRST_PERSON:
                if tense_type == TenseType.PAST:
                    reaction_elements.append("My hands trembled as the full weight of it hit me.")
                else:
                    reaction_elements.append("My hands tremble as the full weight of it hits me.")
            else:
                if tense_type == TenseType.PAST:
                    reaction_elements.append("Their hands trembled as the full weight of it hit them.")
                else:
                    reaction_elements.append("Their hands tremble as the full weight of it hits them.")
        
        # Intensification of emotion
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                reaction_elements.append("I couldn't escape the feeling that everything was wrong.")
            else:
                reaction_elements.append("I can't escape the feeling that everything is wrong.")
        else:
            if tense_type == TenseType.PAST:
                reaction_elements.append("They couldn't escape the feeling that everything was wrong.")
            else:
                reaction_elements.append("They can't escape the feeling that everything is wrong.")
        
        return " ".join(reaction_elements)
    
    def _generate_dilemma_section(self, dilemma: str, reaction: str, target_words: int,
                                 pov_type: POVType, tense_type: TenseType, 
                                 maintain_crucible_focus: bool) -> str:
        """Generate dilemma presentation with no good options"""
        
        dilemma_elements = []
        
        # Dilemma recognition
        if tense_type == TenseType.PAST:
            dilemma_elements.append(f"The dilemma became clear: {dilemma.lower()}.")
        else:
            dilemma_elements.append(f"The dilemma becomes clear: {dilemma.lower()}.")
        
        # No good options
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                dilemma_elements.append("I saw no good options ahead of me.")
                dilemma_elements.append("Every path seemed to lead to more problems.")
            else:
                dilemma_elements.append("I see no good options ahead of me.")
                dilemma_elements.append("Every path seems to lead to more problems.")
        else:
            if tense_type == TenseType.PAST:
                dilemma_elements.append("They saw no good options ahead.")
                dilemma_elements.append("Every path seemed to lead to more problems.")
            else:
                dilemma_elements.append("They see no good options ahead.")
                dilemma_elements.append("Every path seems to lead to more problems.")
        
        # Pressure mounting
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                dilemma_elements.append("I had to choose, but how could I?")
            else:
                dilemma_elements.append("I have to choose, but how can I?")
        else:
            if tense_type == TenseType.PAST:
                dilemma_elements.append("They had to choose, but how could they?")
            else:
                dilemma_elements.append("They have to choose, but how can they?")
        
        return " ".join(dilemma_elements)
    
    def _generate_decision_process(self, decision: str, dilemma: str, target_words: int,
                                  pov_type: POVType, tense_type: TenseType, 
                                  dialogue_target: float) -> str:
        """Generate decision making process"""
        
        decision_elements = []
        
        # Internal deliberation
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                decision_elements.append("I weighed my options, such as they were.")
            else:
                decision_elements.append("I weigh my options, such as they are.")
        else:
            if tense_type == TenseType.PAST:
                decision_elements.append("They weighed their options, such as they were.")
            else:
                decision_elements.append("They weigh their options, such as they are.")
        
        # Add internal dialogue if target requires it
        if dialogue_target > 0.2:
            if pov_type == POVType.FIRST_PERSON:
                decision_elements.append('"There has to be another way," I thought.')
            else:
                decision_elements.append('"There has to be another way," they thought.')
        
        # Decision crystallization
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                decision_elements.append(f"Finally, I decided: {decision.lower()}.")
            else:
                decision_elements.append(f"Finally, I decide: {decision.lower()}.")
        else:
            if tense_type == TenseType.PAST:
                decision_elements.append(f"Finally, they decided: {decision.lower()}.")
            else:
                decision_elements.append(f"Finally, they decide: {decision.lower()}.")
        
        return " ".join(decision_elements)
    
    def _generate_decision_execution(self, decision: str, scene_crucible: str, target_words: int,
                                   pov_type: POVType, tense_type: TenseType, 
                                   maintain_crucible_focus: bool) -> str:
        """Generate decision execution and consequences"""
        
        execution_elements = []
        
        # Action taken
        if pov_type == POVType.FIRST_PERSON:
            if tense_type == TenseType.PAST:
                execution_elements.append("I acted on my decision immediately.")
            else:
                execution_elements.append("I act on my decision immediately.")
        else:
            if tense_type == TenseType.PAST:
                execution_elements.append("They acted on their decision immediately.")
            else:
                execution_elements.append("They act on their decision immediately.")
        
        # Immediate consequences
        if tense_type == TenseType.PAST:
            execution_elements.append("The consequences were immediate and irreversible.")
        else:
            execution_elements.append("The consequences are immediate and irreversible.")
        
        # Return to crucible if maintaining focus
        if maintain_crucible_focus:
            if pov_type == POVType.FIRST_PERSON:
                if tense_type == TenseType.PAST:
                    execution_elements.append(f"I had changed the nature of {scene_crucible.lower()} forever.")
                else:
                    execution_elements.append(f"I have changed the nature of {scene_crucible.lower()} forever.")
            else:
                if tense_type == TenseType.PAST:
                    execution_elements.append(f"They had changed the nature of {scene_crucible.lower()} forever.")
                else:
                    execution_elements.append(f"They have changed the nature of {scene_crucible.lower()} forever.")
        
        return " ".join(execution_elements)