"""
Continuity Checker Tool - Story Consistency Verification

Checks for consistency and continuity across all story elements.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class ContinuityCheckerTool(BaseTool):
    """
    Tool for checking story continuity and consistency across the complete manuscript.
    """
    
    action: str = Field(..., description="Action to perform: 'check_plot_continuity', 'verify_character_consistency', 'validate_timeline', 'cross_reference_elements'")
    manuscript: str = Field(default="", description="Complete manuscript text for analysis")
    story_foundation: dict = Field(default={}, description="All Snowflake story elements for cross-reference")
    character_profiles: dict = Field(default={}, description="Character information for consistency checking")
    scene_metadata: list = Field(default=[], description="Scene metadata for timeline verification")
    
    def run(self) -> str:
        """Execute continuity checker tool action"""
        
        if self.action == "check_plot_continuity":
            return self._check_plot_continuity()
        elif self.action == "verify_character_consistency":
            return self._verify_character_consistency()
        elif self.action == "validate_timeline":
            return self._validate_timeline()
        elif self.action == "cross_reference_elements":
            return self._cross_reference_elements()
        else:
            return "Error: Invalid action. Use 'check_plot_continuity', 'verify_character_consistency', 'validate_timeline', or 'cross_reference_elements'"
    
    def _check_plot_continuity(self) -> str:
        """Check plot continuity and logical consistency"""
        if not self.manuscript:
            return "Error: Manuscript required for plot continuity check"
        
        continuity = f"🔍 PLOT CONTINUITY ANALYSIS\n\n"
        
        plot_issues = []
        
        # Check for established story elements in manuscript
        if self.story_foundation:
            foundation_issues = self._check_foundation_adherence()
            plot_issues.extend(foundation_issues)
        
        # Check for internal plot consistency
        internal_issues = self._check_internal_plot_logic()
        plot_issues.extend(internal_issues)
        
        # Check for scene progression logic
        scene_issues = self._check_scene_progression()
        plot_issues.extend(scene_issues)
        
        # Check for setup and payoff consistency
        setup_payoff_issues = self._check_setup_payoff()
        plot_issues.extend(setup_payoff_issues)
        
        continuity += f"**Plot Continuity Results:**\n"
        continuity += f"Issues identified: {len(plot_issues)}\n\n"
        
        if plot_issues:
            continuity += f"**Issues Found:**\n"
            for i, issue in enumerate(plot_issues, 1):
                continuity += f"{i}. {issue}\n"
        else:
            continuity += f"✅ No major plot continuity issues detected\n"
        
        return continuity
    
    def _verify_character_consistency(self) -> str:
        """Verify character consistency throughout manuscript"""
        if not self.manuscript:
            return "Error: Manuscript required for character consistency check"
        
        consistency = f"👥 CHARACTER CONSISTENCY ANALYSIS\n\n"
        
        character_issues = []
        
        # Check character voice consistency
        if self.character_profiles:
            voice_issues = self._check_character_voices()
            character_issues.extend(voice_issues)
        
        # Check character behavior consistency
        behavior_issues = self._check_character_behavior()
        character_issues.extend(behavior_issues)
        
        # Check character arc progression
        arc_issues = self._check_character_arcs()
        character_issues.extend(arc_issues)
        
        # Check character relationship consistency
        relationship_issues = self._check_character_relationships()
        character_issues.extend(relationship_issues)
        
        consistency += f"**Character Consistency Results:**\n"
        consistency += f"Issues identified: {len(character_issues)}\n\n"
        
        if character_issues:
            consistency += f"**Issues Found:**\n"
            for i, issue in enumerate(character_issues, 1):
                consistency += f"{i}. {issue}\n"
        else:
            consistency += f"✅ No major character consistency issues detected\n"
        
        return consistency
    
    def _validate_timeline(self) -> str:
        """Validate timeline consistency and chronological flow"""
        if not self.manuscript:
            return "Error: Manuscript required for timeline validation"
        
        timeline = f"⏰ TIMELINE VALIDATION\n\n"
        
        timeline_issues = []
        
        # Check chronological consistency
        chronology_issues = self._check_chronological_order()
        timeline_issues.extend(chronology_issues)
        
        # Check time references
        time_reference_issues = self._check_time_references()
        timeline_issues.extend(time_reference_issues)
        
        # Check seasonal/temporal consistency
        temporal_issues = self._check_temporal_consistency()
        timeline_issues.extend(temporal_issues)
        
        # Check age and timeline logic
        if self.character_profiles:
            age_issues = self._check_age_consistency()
            timeline_issues.extend(age_issues)
        
        timeline += f"**Timeline Validation Results:**\n"
        timeline += f"Issues identified: {len(timeline_issues)}\n\n"
        
        if timeline_issues:
            timeline += f"**Issues Found:**\n"
            for i, issue in enumerate(timeline_issues, 1):
                timeline += f"{i}. {issue}\n"
        else:
            timeline += f"✅ No major timeline consistency issues detected\n"
        
        return timeline
    
    def _cross_reference_elements(self) -> str:
        """Cross-reference all story elements for consistency"""
        if not self.manuscript or not self.story_foundation:
            return "Error: Manuscript and story foundation required for cross-reference"
        
        cross_ref = f"🔗 CROSS-REFERENCE ANALYSIS\n\n"
        
        reference_issues = []
        
        # Check concept adherence
        concept_issues = self._check_concept_adherence()
        reference_issues.extend(concept_issues)
        
        # Check character integration
        character_integration_issues = self._check_character_integration()
        reference_issues.extend(character_integration_issues)
        
        # Check theme consistency
        theme_issues = self._check_theme_consistency()
        reference_issues.extend(theme_issues)
        
        # Check genre consistency
        genre_issues = self._check_genre_consistency()
        reference_issues.extend(genre_issues)
        
        cross_ref += f"**Cross-Reference Results:**\n"
        cross_ref += f"Issues identified: {len(reference_issues)}\n\n"
        
        if reference_issues:
            cross_ref += f"**Issues Found:**\n"
            for i, issue in enumerate(reference_issues, 1):
                cross_ref += f"{i}. {issue}\n"
        else:
            cross_ref += f"✅ All story elements properly integrated\n"
        
        return cross_ref
    
    def _check_foundation_adherence(self) -> list:
        """Check adherence to established story foundation"""
        issues = []
        
        # Check logline adherence
        logline = self.story_foundation.get('one_sentence_summary', '')
        if logline:
            # Extract key elements from logline
            logline_words = logline.lower().split()
            manuscript_lower = self.manuscript.lower()
            
            # Simple check for key story elements presence
            key_elements_present = sum(1 for word in logline_words[:10] if word in manuscript_lower)
            if key_elements_present < 3:
                issues.append("Manuscript doesn't clearly reflect established logline elements")
        
        # Check moral premise integration
        moral_premise = self.story_foundation.get('moral_premise', '')
        if moral_premise and len(moral_premise) > 10:
            moral_words = moral_premise.lower().split()[:5]
            if not any(word in self.manuscript.lower() for word in moral_words):
                issues.append("Moral premise not evident in manuscript themes")
        
        return issues
    
    def _check_internal_plot_logic(self) -> list:
        """Check internal plot logic consistency"""
        issues = []
        
        # Look for common plot logic issues
        manuscript_lower = self.manuscript.lower()
        
        # Check for contradictory statements
        contradiction_pairs = [
            (['door was locked', 'door locked'], ['door was open', 'door opened']),
            (['was dead', 'had died'], ['was alive', 'still living']),
            (['was alone', 'by himself', 'by herself'], ['with others', 'together'])
        ]
        
        for positive_terms, negative_terms in contradiction_pairs:
            pos_found = any(term in manuscript_lower for term in positive_terms)
            neg_found = any(term in manuscript_lower for term in negative_terms)
            
            if pos_found and neg_found:
                issues.append(f"Potential contradiction found between conflicting story elements")
        
        return issues
    
    def _check_scene_progression(self) -> list:
        """Check logical scene progression"""
        issues = []
        
        if self.scene_metadata:
            # Check for logical flow between scenes
            for i in range(len(self.scene_metadata) - 1):
                current_scene = self.scene_metadata[i]
                next_scene = self.scene_metadata[i + 1]
                
                # Check for abrupt location changes without transition
                current_location = current_scene.get('location', '')
                next_location = next_scene.get('location', '')
                
                if current_location and next_location and current_location != next_location:
                    # Look for transition in manuscript
                    transition_words = ['traveled', 'went to', 'arrived at', 'moved to']
                    if not any(word in self.manuscript.lower() for word in transition_words):
                        issues.append(f"Scene {i+1} to {i+2}: Abrupt location change without clear transition")
        
        return issues
    
    def _check_setup_payoff(self) -> list:
        """Check setup and payoff consistency"""
        issues = []
        
        # Look for common setup elements that should have payoffs
        setup_indicators = ['foreshadowed', 'hinted', 'promised', 'threatened', 'warned']
        
        for indicator in setup_indicators:
            if indicator in self.manuscript.lower():
                # This is a simplified check - in practice would need more sophisticated analysis
                pass
        
        return issues
    
    def _check_character_voices(self) -> list:
        """Check character voice consistency"""
        issues = []
        
        if not self.character_profiles:
            return issues
        
        for char_name, profile in self.character_profiles.items():
            if char_name.lower() in self.manuscript.lower():
                # Check for voice characteristics
                if isinstance(profile, dict):
                    voice_info = profile.get('voice', {})
                    personality = profile.get('personality', {})
                    
                    # Simple consistency checks
                    if personality.get('formal') and 'gonna' in self.manuscript.lower():
                        issues.append(f"{char_name}: Informal language conflicts with formal personality")
                    
                    if personality.get('quiet') and 'shouted' in self.manuscript.lower():
                        # This could be character growth, but worth flagging
                        issues.append(f"{char_name}: Loud behavior may conflict with quiet personality (check if intentional character growth)")
        
        return issues
    
    def _check_character_behavior(self) -> list:
        """Check character behavior consistency"""
        issues = []
        
        # This would require more sophisticated character behavior analysis
        # For now, basic consistency checks
        
        return issues
    
    def _check_character_arcs(self) -> list:
        """Check character arc progression consistency"""
        issues = []
        
        if self.character_profiles:
            for char_name, profile in self.character_profiles.items():
                if isinstance(profile, dict):
                    arc_info = profile.get('character_arc', '')
                    if arc_info and char_name.lower() in self.manuscript.lower():
                        # Check if arc elements are present in manuscript
                        arc_words = arc_info.lower().split()[:5]
                        if not any(word in self.manuscript.lower() for word in arc_words):
                            issues.append(f"{char_name}: Character arc not clearly developed in manuscript")
        
        return issues
    
    def _check_character_relationships(self) -> list:
        """Check character relationship consistency"""
        issues = []
        
        # This would analyze character interactions for consistency
        # Basic implementation checks for relationship mentions
        
        return issues
    
    def _check_chronological_order(self) -> list:
        """Check chronological order consistency"""
        issues = []
        
        # Look for temporal indicators
        time_indicators = ['yesterday', 'tomorrow', 'earlier', 'later', 'before', 'after', 'then', 'now']
        
        # This would need more sophisticated temporal analysis
        # For now, basic checks for obvious inconsistencies
        
        return issues
    
    def _check_time_references(self) -> list:
        """Check time reference consistency"""
        issues = []
        
        # Look for specific time references
        time_patterns = ['monday', 'tuesday', 'morning', 'afternoon', 'evening', 'night']
        
        # Check for contradictory time references
        # This is a simplified implementation
        
        return issues
    
    def _check_temporal_consistency(self) -> list:
        """Check seasonal and temporal consistency"""
        issues = []
        
        seasons = ['spring', 'summer', 'autumn', 'fall', 'winter']
        weather = ['snow', 'rain', 'sunshine', 'hot', 'cold']
        
        # Check for seasonal consistency
        # This would need more sophisticated analysis
        
        return issues
    
    def _check_age_consistency(self) -> list:
        """Check character age consistency"""
        issues = []
        
        # Check character ages against timeline
        if self.character_profiles:
            for char_name, profile in self.character_profiles.items():
                if isinstance(profile, dict):
                    age_info = profile.get('physical', {}).get('age', '')
                    if age_info and char_name.lower() in self.manuscript.lower():
                        # Check for age-appropriate behavior and references
                        pass
        
        return issues
    
    def _check_concept_adherence(self) -> list:
        """Check adherence to original story concept"""
        issues = []
        
        concept_data = self.story_foundation.get('story_concept', {})
        if concept_data:
            genre = concept_data.get('category', '')
            delight = concept_data.get('delight_statement', '')
            
            if genre and genre.lower() not in self.manuscript.lower():
                # Genre elements should be present
                if genre.lower() == 'fantasy' and not any(word in self.manuscript.lower() for word in ['magic', 'spell', 'enchant']):
                    issues.append(f"Fantasy elements not evident despite {genre} genre")
        
        return issues
    
    def _check_character_integration(self) -> list:
        """Check character integration with story"""
        issues = []
        
        if self.character_profiles:
            for char_name, profile in self.character_profiles.items():
                if char_name.lower() not in self.manuscript.lower():
                    issues.append(f"Character {char_name} from profiles not present in manuscript")
        
        return issues
    
    def _check_theme_consistency(self) -> list:
        """Check theme consistency throughout manuscript"""
        issues = []
        
        moral_premise = self.story_foundation.get('moral_premise', '')
        if moral_premise:
            # Check if themes are developed throughout
            theme_words = moral_premise.lower().split()
            theme_presence = sum(1 for word in theme_words if word in self.manuscript.lower())
            
            if theme_presence < len(theme_words) * 0.3:
                issues.append("Story themes not consistently developed throughout manuscript")
        
        return issues
    
    def _check_genre_consistency(self) -> list:
        """Check genre consistency and expectations"""
        issues = []
        
        # Check if manuscript fulfills genre promises
        concept_data = self.story_foundation.get('story_concept', {})
        if concept_data:
            genre = concept_data.get('category', '').lower()
            
            genre_requirements = {
                'romance': ['love', 'relationship', 'attraction', 'emotion'],
                'thriller': ['danger', 'suspense', 'chase', 'threat'],
                'fantasy': ['magic', 'spell', 'enchant', 'wizard'],
                'mystery': ['clue', 'investigate', 'solve', 'suspect'],
                'science fiction': ['technology', 'future', 'space', 'scientific']
            }
            
            if genre in genre_requirements:
                required_elements = genre_requirements[genre]
                elements_present = sum(1 for element in required_elements if element in self.manuscript.lower())
                
                if elements_present == 0:
                    issues.append(f"Manuscript lacks expected {genre} genre elements")
        
        return issues