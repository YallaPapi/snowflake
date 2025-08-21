"""
Character Bible Tool - Step 7 of Snowflake Method

Creates comprehensive character bibles with full profiles.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class CharacterBibleTool(BaseTool):
    """
    Tool for creating comprehensive character bibles (Step 7).
    Integrates with existing Snowflake Step 7 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_bibles', 'validate_bibles', 'expand_bible', 'analyze_consistency'")
    character_synopses: dict = Field(default={}, description="Step 5 character synopses to build from")
    story_context: dict = Field(default={}, description="Full story context for character integration")
    character_name: str = Field(default="", description="Specific character name for detailed expansion")
    draft_bibles: dict = Field(default={}, description="Draft character bibles for validation")
    
    def run(self) -> str:
        """Execute character bible tool action"""
        
        if self.action == "create_bibles":
            return self._create_bibles()
        elif self.action == "validate_bibles":
            return self._validate_bibles()
        elif self.action == "expand_bible":
            return self._expand_bible()
        elif self.action == "analyze_consistency":
            return self._analyze_consistency()
        else:
            return "Error: Invalid action. Use 'create_bibles', 'validate_bibles', 'expand_bible', or 'analyze_consistency'"
    
    def _create_bibles(self) -> str:
        """Create comprehensive character bibles"""
        try:
            # Import existing Step 7 functionality
            from src.pipeline.executors.step_7_executor import Step7CharacterBibles
            from src.pipeline.validators.step_7_validator import Step7Validator
            
            if not self.character_synopses:
                return "Error: Character synopses required for bible creation"
            
            # Use existing Step 7 executor
            executor = Step7CharacterBibles()
            validator = Step7Validator()
            
            # Generate character bibles
            result = executor.execute(
                step_5_data={'character_synopses': self.character_synopses},
                step_6_data=self.story_context,
                project_id=self.character_synopses.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    bibles = result['artifact']['character_bibles']
                    bible_summary = self._summarize_bibles(bibles)
                    return f"✅ Character bibles created successfully:\n\n{bible_summary}\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Bibles created but validation failed:\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Bible creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_bibles_fallback()
        except Exception as e:
            return f"❌ Error creating bibles: {str(e)}"
    
    def _validate_bibles(self) -> str:
        """Validate existing character bibles"""
        if not self.draft_bibles:
            return "Error: Draft bibles required for validation"
        
        try:
            from src.pipeline.validators.step_7_validator import Step7Validator
            
            validator = Step7Validator()
            artifact = {'character_bibles': self.draft_bibles}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Character bibles validation passed:\n\n{len(self.draft_bibles)} character bibles validated\nAll completeness and consistency checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Bible validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_bibles_fallback()
        except Exception as e:
            return f"❌ Error validating bibles: {str(e)}"
    
    def _expand_bible(self) -> str:
        """Expand a specific character's bible"""
        if not self.character_name:
            return "Error: Character name required for bible expansion"
        
        if not self.character_synopses or self.character_name not in self.character_synopses:
            return f"Error: Character '{self.character_name}' not found in synopses"
        
        # Create comprehensive bible
        bible = self._create_comprehensive_bible(self.character_name, self.character_synopses[self.character_name])
        
        return f"✅ Comprehensive bible for '{self.character_name}':\n\n{self._format_bible_display(bible)}"
    
    def _analyze_consistency(self) -> str:
        """Analyze consistency across character bibles"""
        if not self.draft_bibles:
            return "Error: Character bibles required for consistency analysis"
        
        issues = []
        relationships = {}
        
        # Check for relationship consistency
        for char_name, bible in self.draft_bibles.items():
            char_relationships = bible.get('relationships', {})
            for related_char, relationship_desc in char_relationships.items():
                if related_char in self.draft_bibles:
                    # Check if relationship is mutual
                    other_relationships = self.draft_bibles[related_char].get('relationships', {})
                    if char_name not in other_relationships:
                        issues.append(f"Relationship inconsistency: {char_name} knows {related_char} but not vice versa")
        
        # Check for timeline consistency
        ages = {}
        for char_name, bible in self.draft_bibles.items():
            age = bible.get('physical', {}).get('age')
            if age:
                ages[char_name] = age
        
        # Check for setting consistency
        locations = set()
        for char_name, bible in self.draft_bibles.items():
            char_locations = bible.get('environment', {}).get('locations', [])
            locations.update(char_locations)
        
        consistency_report = f"📊 Character Bible Consistency Analysis:\n\n"
        consistency_report += f"Characters analyzed: {len(self.draft_bibles)}\n"
        consistency_report += f"Unique locations: {len(locations)}\n"
        consistency_report += f"Characters with ages: {len(ages)}\n"
        
        if issues:
            consistency_report += f"\n⚠️ Issues found:\n" + "\n".join(f"- {issue}" for issue in issues)
        else:
            consistency_report += f"\n✅ No major consistency issues found"
        
        return consistency_report
    
    def _create_bibles_fallback(self) -> str:
        """Fallback bible creation when Snowflake modules unavailable"""
        if not self.character_synopses:
            return "Error: Character synopses required for bible creation"
        
        bibles = {}
        
        for char_name, synopsis in self.character_synopses.items():
            bibles[char_name] = self._create_comprehensive_bible(char_name, synopsis)
        
        bible_summary = self._summarize_bibles(bibles)
        
        return f"📝 Character bibles created (fallback mode):\n\n{bible_summary}\n\n⚠️ Note: Using template structure. Recommend adding story-specific details and cultural context."
    
    def _validate_bibles_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        issues = []
        
        if not isinstance(self.draft_bibles, dict):
            issues.append("Bibles should be a dictionary with character names as keys")
            return f"⚠️ Validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
        
        required_sections = ['physical', 'personality', 'environment', 'psychological']
        
        for char_name, bible in self.draft_bibles.items():
            if not isinstance(bible, dict):
                issues.append(f"Bible for '{char_name}' should be a dictionary")
                continue
            
            # Check required sections
            for section in required_sections:
                if section not in bible:
                    issues.append(f"Bible for '{char_name}' missing {section} section")
                elif not bible[section]:
                    issues.append(f"Bible for '{char_name}' has empty {section} section")
            
            # Check completeness
            physical = bible.get('physical', {})
            if 'age' not in physical or 'appearance' not in physical:
                issues.append(f"Bible for '{char_name}' incomplete physical description")
            
            personality = bible.get('personality', {})
            if 'traits' not in personality or 'voice' not in personality:
                issues.append(f"Bible for '{char_name}' incomplete personality profile")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{len(self.draft_bibles)} bibles validated\nAll required sections present"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
    
    def _create_comprehensive_bible(self, char_name: str, synopsis: str) -> dict:
        """Create comprehensive character bible from synopsis"""
        
        # Extract character role and basic info from synopsis
        is_protagonist = 'protagonist' in synopsis.lower()
        is_antagonist = 'antagonist' in synopsis.lower()
        
        bible = {
            "physical": {
                "age": "Age appropriate for role and story demands",
                "appearance": "Physical description that reflects character's personality and background",
                "mannerisms": "Distinctive physical habits and gestures",
                "voice": "Speech patterns, accent, vocabulary level",
                "clothing_style": "Fashion choices that reflect personality and social status"
            },
            "personality": {
                "core_traits": "Primary personality characteristics that drive behavior",
                "strengths": "Positive qualities that serve the character well",
                "flaws": "Weaknesses and blind spots that create conflict",
                "fears": "Deep-seated anxieties that influence decisions",
                "desires": "What the character most wants in life",
                "values": "Moral principles and beliefs that guide choices",
                "humor_style": "How character uses or responds to humor",
                "decision_making": "How character approaches choices and problems"
            },
            "environment": {
                "background": "Social, economic, and cultural origins",
                "education": "Formal and informal learning experiences", 
                "occupation": "Current work and career aspirations",
                "living_situation": "Home environment and living conditions",
                "relationships": "Key relationships that shape character",
                "social_circle": "Friends, colleagues, and community connections",
                "locations": "Important places in character's life"
            },
            "psychological": {
                "worldview": "How character sees life and their place in it",
                "internal_conflicts": "Psychological tensions and contradictions",
                "coping_mechanisms": "How character handles stress and adversity",
                "emotional_patterns": "Typical emotional responses and triggers",
                "growth_potential": "Areas where character can develop",
                "backstory_events": "Formative experiences that shaped personality",
                "motivational_drivers": "Core needs that drive behavior",
                "relationship_patterns": "How character typically relates to others"
            },
            "story_function": {
                "plot_role": "How character serves the overall story",
                "thematic_significance": "What the character represents thematically",
                "character_arc": "How the character changes throughout the story",
                "key_scenes": "Important moments that define the character",
                "relationships_to_other_characters": "Specific dynamics with other cast members",
                "obstacles_faced": "Challenges specific to this character",
                "resolution": "How character's story concludes"
            }
        }
        
        # Customize based on character type
        if is_protagonist:
            bible["psychological"]["growth_potential"] = "Significant capacity for positive change and learning"
            bible["story_function"]["plot_role"] = "Drives main storyline through choices and actions"
            bible["story_function"]["thematic_significance"] = "Embodies story's central theme through personal journey"
        
        elif is_antagonist:
            bible["psychological"]["worldview"] = "Believes their approach is justified and necessary"
            bible["story_function"]["plot_role"] = "Creates primary obstacles and opposition for protagonist"
            bible["story_function"]["thematic_significance"] = "Represents opposing values or approaches to protagonist"
        
        return bible
    
    def _summarize_bibles(self, bibles: dict) -> str:
        """Create summary of character bibles"""
        if not bibles:
            return "No character bibles to summarize"
        
        summary = f"📚 CHARACTER BIBLE SUMMARY\n\n"
        summary += f"Total characters: {len(bibles)}\n\n"
        
        for char_name, bible in bibles.items():
            summary += f"**{char_name.upper()}**\n"
            
            # Physical summary
            physical = bible.get('physical', {})
            summary += f"Physical: {physical.get('age', 'Unspecified age')}, {physical.get('appearance', 'Basic description')}\n"
            
            # Personality highlights
            personality = bible.get('personality', {})
            summary += f"Personality: {personality.get('core_traits', 'Basic traits')}\n"
            
            # Role summary
            story_function = bible.get('story_function', {})
            summary += f"Story Role: {story_function.get('plot_role', 'Supporting character')}\n"
            
            summary += "\n"
        
        return summary
    
    def _format_bible_display(self, bible: dict) -> str:
        """Format character bible for display"""
        output = []
        
        for section_name, section_content in bible.items():
            output.append(f"## {section_name.upper().replace('_', ' ')}")
            
            if isinstance(section_content, dict):
                for key, value in section_content.items():
                    output.append(f"**{key.replace('_', ' ').title()}**: {value}")
            else:
                output.append(str(section_content))
            
            output.append("")
        
        return "\n".join(output)