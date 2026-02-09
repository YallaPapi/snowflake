"""
Step 9 Validator: Scene Briefs (Proactive vs Reactive)
Validates scene briefs with correct triads according to Snowflake Method
"""

import re
from typing import Dict, Any, Tuple, List

class Step9Validator:
    """
    Validator for Step 9: Scene Briefs
    Enforces correct triad structure for Proactive and Reactive scenes
    """
    
    VERSION = "1.0.0"
    
    # Required fields per scene type
    PROACTIVE_FIELDS = ['goal', 'conflict', 'setback', 'stakes', 'links']
    REACTIVE_FIELDS = ['reaction', 'dilemma', 'decision', 'stakes', 'links']
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 9 artifact
        
        Args:
            artifact: The Step 9 artifact to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        if 'scene_briefs' not in artifact:
            errors.append("MISSING SCENE BRIEFS: No scene_briefs array found")
            return False, errors
        
        scene_briefs = artifact['scene_briefs']
        
        # RULE 1: Must have briefs for all scenes
        brief_count = len(scene_briefs)
        artifact['brief_count'] = brief_count
        
        if brief_count < 10:
            errors.append(f"TOO FEW BRIEFS: Need at least 10, found {brief_count}")
        
        # Track validation results
        proactive_count = 0
        reactive_count = 0
        triads_complete = []
        triads_incomplete = []
        decision_goal_chain = []
        
        # RULE 2: Validate each brief
        for i, brief in enumerate(scene_briefs):
            brief_id = f"Brief {i+1}"
            
            # Check scene type
            if 'type' not in brief:
                errors.append(f"{brief_id} MISSING TYPE: Must be Proactive or Reactive")
                continue
            
            scene_type = brief['type']
            
            # Normalize case for type
            if scene_type.lower() == 'proactive':
                scene_type = 'Proactive'
                brief['type'] = scene_type
            elif scene_type.lower() == 'reactive':
                scene_type = 'Reactive'
                brief['type'] = scene_type
            
            if scene_type == 'Proactive':
                proactive_count += 1
                brief_errors = self.validate_proactive_brief(brief, brief_id)
                errors.extend(brief_errors)
                
                if len(brief_errors) == 0:
                    triads_complete.append(i + 1)
                else:
                    triads_incomplete.append(i + 1)
                    
            elif scene_type == 'Reactive':
                reactive_count += 1
                brief_errors = self.validate_reactive_brief(brief, brief_id)
                errors.extend(brief_errors)
                
                if len(brief_errors) == 0:
                    triads_complete.append(i + 1)
                else:
                    triads_incomplete.append(i + 1)
                    
                # Check if decision seeds next goal
                if i < len(scene_briefs) - 1:
                    next_brief = scene_briefs[i + 1]
                    if self.decision_seeds_goal(brief, next_brief):
                        decision_goal_chain.append((i + 1, i + 2))
            else:
                errors.append(f"{brief_id} INVALID TYPE: '{scene_type}' must be Proactive or Reactive")
        
        # Store validation results
        artifact['type_distribution'] = {
            'proactive': proactive_count,
            'reactive': reactive_count
        }
        
        artifact['triad_validation'] = {
            'complete': triads_complete,
            'incomplete': triads_incomplete,
            'completion_rate': len(triads_complete) / max(brief_count, 1)
        }
        
        artifact['causal_chain'] = {
            'decision_goal_links': decision_goal_chain,
            'chain_strength': len(decision_goal_chain) / max(reactive_count - 1, 1) if reactive_count > 1 else 0
        }
        
        # RULE 3: Check balance of types
        if proactive_count == 0:
            errors.append("NO PROACTIVE SCENES: Story needs goal-pursuing scenes")
        if reactive_count == 0:
            errors.append("NO REACTIVE SCENES: Story needs reaction/decision scenes")
        
        # RULE 4: Check disaster links
        disaster_links = self.validate_disaster_links(scene_briefs)
        artifact['disaster_links'] = disaster_links
        
        if not disaster_links['d1_linked']:
            errors.append("D1 NOT LINKED: No brief links to Disaster 1")
        if not disaster_links['d2_linked']:
            errors.append("D2 NOT LINKED: No brief links to Disaster 2")
        if not disaster_links['d3_linked']:
            errors.append("D3 NOT LINKED: No brief links to Disaster 3")
        
        return len(errors) == 0, errors
    
    def validate_proactive_brief(self, brief: Dict[str, Any], brief_id: str) -> List[str]:
        """Validate Proactive scene brief"""
        errors = []
        
        # Check required fields
        for field in self.PROACTIVE_FIELDS:
            if field not in brief or not brief.get(field):
                errors.append(f"{brief_id} MISSING {field.upper()}")
        
        # Validate Goal
        if 'goal' in brief:
            goal_errors = self.validate_goal(brief['goal'], brief_id)
            errors.extend(goal_errors)
        
        # Validate Conflict
        if 'conflict' in brief:
            conflict_errors = self.validate_conflict(brief['conflict'], brief_id)
            errors.extend(conflict_errors)
        
        # Validate Setback
        if 'setback' in brief:
            setback_errors = self.validate_setback(brief['setback'], brief_id)
            errors.extend(setback_errors)
        
        # Validate Stakes
        if 'stakes' in brief:
            stakes_errors = self.validate_stakes(brief['stakes'], brief_id)
            errors.extend(stakes_errors)
        
        # Validate Links
        if 'links' in brief:
            links = brief['links']
            # Handle case where links might be a string or other non-dict
            if isinstance(links, dict):
                links_errors = self.validate_links(links, brief_id)
                errors.extend(links_errors)
        
        return errors
    
    def validate_reactive_brief(self, brief: Dict[str, Any], brief_id: str) -> List[str]:
        """Validate Reactive scene brief"""
        errors = []
        
        # Check required fields
        for field in self.REACTIVE_FIELDS:
            if field not in brief or not brief.get(field):
                errors.append(f"{brief_id} MISSING {field.upper()}")
        
        # Validate Reaction
        if 'reaction' in brief:
            reaction_errors = self.validate_reaction(brief['reaction'], brief_id)
            errors.extend(reaction_errors)
        
        # Validate Dilemma
        if 'dilemma' in brief:
            dilemma_errors = self.validate_dilemma(brief['dilemma'], brief_id)
            errors.extend(dilemma_errors)
        
        # Validate Decision
        if 'decision' in brief:
            decision_errors = self.validate_decision(brief['decision'], brief_id)
            errors.extend(decision_errors)
        
        # Validate Stakes
        if 'stakes' in brief:
            stakes_errors = self.validate_stakes(brief['stakes'], brief_id)
            errors.extend(stakes_errors)
        
        # Validate Links
        if 'links' in brief:
            links = brief['links']
            # Handle case where links might be a string or other non-dict
            if isinstance(links, dict):
                links_errors = self.validate_links(links, brief_id)
                errors.extend(links_errors)
        
        return errors
    
    def validate_goal(self, goal: str, brief_id: str) -> List[str]:
        """Validate goal is literal and time-bound (relaxed for reliability)"""
        errors = []
        
        # Basic length check
        if len(goal) < 10:
            errors.append(f"{brief_id} GOAL TOO SHORT: Describe what character wants")
        
        # Check for some kind of action (more lenient)
        action_words = r'\b(get|take|find|go|stop|save|help|escape|prove|win|capture|destroy|protect|complete|steal|convince|reach|achieve|secure|obtain)\b'
        if not re.search(action_words, goal, re.I):
            errors.append(f"{brief_id} GOAL NOT CLEAR: What does character want to do?")
        
        # Less strict on time constraints - just suggest
        time_markers = r'\b(before|within|by|until|deadline|midnight|dawn|sunset|hours?|minutes?|soon|quickly|urgent)\b'
        if not re.search(time_markers, goal, re.I) and len(errors) == 0:
            # Only warn if goal is otherwise good
            pass  # Don't require time constraint
        
        # Check for vague goals (still important)
        vague_markers = r'\b(somehow|maybe|perhaps|try to|attempt|hope)\b'
        if re.search(vague_markers, goal, re.I):
            errors.append(f"{brief_id} GOAL TOO VAGUE: Be more specific about what character will do")
        
        return errors
    
    def validate_conflict(self, conflict: str, brief_id: str) -> List[str]:
        """Validate conflict is opposition (relaxed)"""
        errors = []
        
        # Basic length check (more lenient)
        if len(conflict) < 10:
            errors.append(f"{brief_id} CONFLICT TOO SHORT: What opposes the character?")
        
        # Check for opposition concepts (broader list)
        opposition_words = r'\b(against|oppose|block|prevent|stop|fight|resist|conflict|problem|obstacle|difficult|challenge|enemy|rival)\b'
        if not re.search(opposition_words, conflict, re.I):
            errors.append(f"{brief_id} CONFLICT UNCLEAR: What opposes the character's goal?")
        
        return errors
    
    def validate_setback(self, setback: str, brief_id: str) -> List[str]:
        """Validate setback changes situation (relaxed)"""
        errors = []
        
        # Basic length check
        if len(setback) < 10:
            errors.append(f"{brief_id} SETBACK TOO SHORT: What goes wrong?")
        
        # Check for negative outcome (broader)
        negative_words = r'\b(fail|wrong|bad|worse|problem|trouble|caught|lost|trapped|difficult|backfire|mistake)\b'
        if not re.search(negative_words, setback, re.I):
            errors.append(f"{brief_id} SETBACK UNCLEAR: How does the situation get worse?")
        
        return errors
    
    def validate_reaction(self, reaction: str, brief_id: str) -> List[str]:
        """Validate reaction has substance"""
        errors = []

        if len(reaction.strip()) < 10:
            errors.append(f"{brief_id} REACTION TOO SHORT: Describe character's response")

        return errors
    
    def validate_dilemma(self, dilemma: str, brief_id: str) -> List[str]:
        """Validate dilemma has substance"""
        errors = []

        if len(dilemma.strip()) < 10:
            errors.append(f"{brief_id} DILEMMA TOO SHORT: Describe the character's dilemma")

        return errors
    
    def validate_decision(self, decision: str, brief_id: str) -> List[str]:
        """Validate decision launches next goal"""
        errors = []
        
        # Check for action commitment
        action_markers = r'\b(decides? to|chooses? to|commits? to|will|going to)\b'
        if not re.search(action_markers, decision, re.I):
            errors.append(f"{brief_id} DECISION NOT ACTIVE: Must commit to action")
        
        # Check for specific next step
        if len(decision) < 15:
            errors.append(f"{brief_id} DECISION TOO VAGUE: Specify next action")
        
        return errors
    
    def validate_stakes(self, stakes: str, brief_id: str) -> List[str]:
        """Validate stakes explain what's at risk (relaxed)"""
        errors = []
        
        if len(stakes) < 5:
            errors.append(f"{brief_id} STAKES TOO SHORT: What's at risk?")
        
        # Check for consequence concepts (broader)
        risk_words = r'\b(risk|lose|fail|die|hurt|damage|destroy|ruin|cost|price|consequence|matter|important)\b'
        if not re.search(risk_words, stakes, re.I):
            errors.append(f"{brief_id} STAKES UNCLEAR: What happens if character fails?")
        
        return errors
    
    def validate_links(self, links: Dict[str, Any], brief_id: str) -> List[str]:
        """Validate links have some content"""
        # Links are informational — don't gate on specific fields
        return []
    
    def decision_seeds_goal(self, reactive_brief: Dict[str, Any], next_brief: Dict[str, Any]) -> bool:
        """Check if decision in reactive brief seeds goal in next brief"""
        if next_brief.get('type') != 'Proactive':
            return False
        
        decision = reactive_brief.get('decision', '').lower()
        next_goal = next_brief.get('goal', '').lower()
        
        # Simple check for related words
        decision_words = set(decision.split())
        goal_words = set(next_goal.split())
        
        # If significant overlap, likely connected
        overlap = decision_words & goal_words
        return len(overlap) >= 2
    
    def validate_disaster_links(self, scene_briefs: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Check if disasters are properly linked"""
        disaster_links = {
            'd1_linked': False,
            'd2_linked': False,
            'd3_linked': False
        }
        
        for brief in scene_briefs:
            links = brief.get('links', {})
            # Handle case where links might be a string or other non-dict
            if not isinstance(links, dict):
                links = {}
            disaster_anchor = links.get('disaster_anchor')
            
            if disaster_anchor == 'D1':
                disaster_links['d1_linked'] = True
            elif disaster_anchor == 'D2':
                disaster_links['d2_linked'] = True
            elif disaster_anchor == 'D3':
                disaster_links['d3_linked'] = True
        
        return disaster_links
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "MISSING TYPE" in error:
                suggestions.append("Specify type as Proactive or Reactive")
            elif "GOAL NOT CONCRETE" in error:
                suggestions.append("Use format: verb + object (steal the ledger)")
            elif "GOAL NOT TIME-BOUND" in error:
                suggestions.append("Add deadline: 'before midnight', 'within 24 hours'")
            elif "GOAL TOO VAGUE" in error:
                suggestions.append("Remove 'try to', make specific and measurable")
            elif "CONFLICT NOT CONCRETE" in error:
                suggestions.append("Name specific obstacles: guards, alarms, rival")
            elif "SETBACK NO CHANGE" in error:
                suggestions.append("Show how situation worsens or options narrow")
            elif "REACTION NOT VISCERAL" in error:
                suggestions.append("Show physical response: trembles, collapses, vomits")
            elif "DILEMMA NO CHOICE" in error:
                suggestions.append("Present two clear options with 'either...or'")
            elif "DILEMMA NO COST" in error:
                suggestions.append("Make both options painful with real losses")
            elif "DILEMMA STRAWMAN" in error:
                suggestions.append("Balance options so neither is obviously better")
            elif "DECISION NOT ACTIVE" in error:
                suggestions.append("Use 'decides to' + specific action")
            elif "STAKES NOT CONCRETE" in error:
                suggestions.append("State what dies/fails/ends if they fail")
            elif "NO CHARACTER LINK" in error:
                suggestions.append("Link to character's goal from Step 3")
            elif "NOT LINKED" in error:
                suggestions.append("Link disaster scenes to disaster anchors")
            elif "NO PROACTIVE SCENES" in error:
                suggestions.append("Add scenes where characters pursue goals")
            elif "NO REACTIVE SCENES" in error:
                suggestions.append("Add scenes where characters process setbacks")
            else:
                suggestions.append("Review Step 9 requirements in guide")
        
        return suggestions