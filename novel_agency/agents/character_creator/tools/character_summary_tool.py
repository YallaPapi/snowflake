"""
Character Summary Tool - Step 3 of Snowflake Method

Creates character summaries with goals, conflicts, and epiphanies.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class CharacterSummaryTool(BaseTool):
    """
    Tool for creating character summaries (Step 3).
    Integrates with existing Snowflake Step 3 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_summaries', 'validate_summaries', 'refine_character'")
    story_data: dict = Field(default={}, description="Story data from Steps 0-2 for character context")
    character_name: str = Field(default="", description="Specific character name for refinement")
    draft_summaries: dict = Field(default={}, description="Draft character summaries for validation")
    
    def run(self) -> str:
        """Execute character summary tool action"""
        
        if self.action == "create_summaries":
            return self._create_summaries()
        elif self.action == "validate_summaries":
            return self._validate_summaries()
        elif self.action == "refine_character":
            return self._refine_character()
        else:
            return "Error: Invalid action. Use 'create_summaries', 'validate_summaries', or 'refine_character'"
    
    def _create_summaries(self) -> str:
        """Create character summaries from story data"""
        try:
            # Import existing Step 3 functionality
            from src.pipeline.executors.step_3_executor import Step3CharacterSummaries
            from src.pipeline.validators.step_3_validator import Step3Validator
            
            if not self.story_data:
                return "Error: Story data required for character summary creation"
            
            # Use existing Step 3 executor
            executor = Step3CharacterSummaries()
            validator = Step3Validator()
            
            # Generate character summaries
            result = executor.execute(
                step_2_data=self.story_data,
                project_id=self.story_data.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    summaries = result['artifact']['character_summaries']
                    summary_text = self._format_summaries_output(summaries)
                    return f"✅ Character summaries created successfully:\n\n{summary_text}\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Summaries created but validation failed:\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Summary creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_summaries_fallback()
        except Exception as e:
            return f"❌ Error creating summaries: {str(e)}"
    
    def _validate_summaries(self) -> str:
        """Validate existing character summaries"""
        if not self.draft_summaries:
            return "Error: Draft summaries required for validation"
        
        try:
            from src.pipeline.validators.step_3_validator import Step3Validator
            
            validator = Step3Validator()
            artifact = {'character_summaries': self.draft_summaries}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Character summaries validation passed:\n\n{len(self.draft_summaries)} characters validated\nAll checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Summary validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_summaries_fallback()
        except Exception as e:
            return f"❌ Error validating summaries: {str(e)}"
    
    def _refine_character(self) -> str:
        """Refine a specific character"""
        if not self.character_name:
            return "Error: Character name required for refinement"
        
        if not self.draft_summaries or self.character_name not in self.draft_summaries:
            return f"Error: Character '{self.character_name}' not found in draft summaries"
        
        character = self.draft_summaries[self.character_name]
        suggestions = []
        
        # Check required fields
        required_fields = ['role', 'name', 'goal', 'conflict', 'epiphany', 'one_line_arc', 'one_paragraph_arc']
        for field in required_fields:
            if field not in character or not character[field]:
                suggestions.append(f"Missing or empty {field}")
        
        # Check goal clarity
        goal = character.get('goal', '')
        if goal and len(goal.split()) < 5:
            suggestions.append("Goal should be more detailed and specific")
        
        # Check conflict depth
        conflict = character.get('conflict', '')
        if conflict and 'internal' not in conflict.lower() and 'external' not in conflict.lower():
            suggestions.append("Consider adding both internal and external conflict elements")
        
        # Check epiphany connection to arc
        epiphany = character.get('epiphany', '')
        one_line_arc = character.get('one_line_arc', '')
        if epiphany and one_line_arc and not any(word in one_line_arc.lower() for word in epiphany.lower().split()[:3]):
            suggestions.append("Epiphany should connect more clearly to character arc")
        
        if not suggestions:
            return f"✅ Character '{self.character_name}' appears well-developed:\n\n{self._format_single_character(character)}\n\nNo major issues found"
        
        return f"🔧 Refinement suggestions for '{self.character_name}':\n\n{self._format_single_character(character)}\n\nSuggestions:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
    def _create_summaries_fallback(self) -> str:
        """Fallback summary creation when Snowflake modules unavailable"""
        if not self.story_data:
            return "Error: Story data required for character summary creation"
        
        # Extract story elements for character creation
        logline = self.story_data.get('one_sentence_summary', '')
        paragraph = self.story_data.get('one_paragraph_summary', '')
        moral_premise = self.story_data.get('moral_premise', '')
        
        # Create basic character templates
        characters = {
            "protagonist": {
                "role": "protagonist", 
                "name": "Main Character",
                "goal": "To overcome the central conflict and achieve their desire",
                "conflict": "Internal doubt and external obstacles preventing goal achievement",
                "epiphany": "Realizes what truly matters and finds inner strength",
                "one_line_arc": "Grows from uncertainty to confident action",
                "one_paragraph_arc": "Begins uncertain and reactive, faces escalating challenges that force growth, ultimately discovers inner resources to overcome both external obstacles and internal limitations."
            },
            "antagonist": {
                "role": "antagonist",
                "name": "Primary Opponent", 
                "goal": "To prevent protagonist from succeeding",
                "conflict": "Believes their approach is justified and necessary",
                "epiphany": "May realize the cost of their actions or double down on their path",
                "one_line_arc": "Escalates opposition until final confrontation",
                "one_paragraph_arc": "Starts as obstacle, becomes increasingly threatening as stakes rise, ultimately forces protagonist to their greatest growth through final confrontation."
            }
        }
        
        # Add additional characters based on story complexity
        if len(paragraph.split()) > 100:  # More complex story
            characters["ally"] = {
                "role": "ally",
                "name": "Supporting Character",
                "goal": "To help protagonist achieve their goal",
                "conflict": "Has own limitations and obstacles",
                "epiphany": "Learns to trust protagonist or finds own strength",
                "one_line_arc": "Grows from helper to true partner",
                "one_paragraph_arc": "Begins as support, faces own challenges, grows alongside protagonist to become essential to final resolution."
            }
        
        summary_text = self._format_summaries_output(characters)
        
        return f"📝 Character summaries created (fallback mode):\n\n{summary_text}\n\n⚠️ Note: Using basic templates based on story structure. Recommend customization with story-specific details."
    
    def _validate_summaries_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        issues = []
        
        if not isinstance(self.draft_summaries, dict):
            issues.append("Summaries should be a dictionary with character names as keys")
            return f"⚠️ Validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
        
        required_fields = ['role', 'name', 'goal', 'conflict', 'epiphany', 'one_line_arc', 'one_paragraph_arc']
        
        for char_name, character in self.draft_summaries.items():
            if not isinstance(character, dict):
                issues.append(f"Character '{char_name}' should be a dictionary")
                continue
                
            for field in required_fields:
                if field not in character or not character[field]:
                    issues.append(f"Character '{char_name}' missing {field}")
            
            # Check minimum content length
            if character.get('one_paragraph_arc', '') and len(character['one_paragraph_arc'].split()) < 20:
                issues.append(f"Character '{char_name}' paragraph arc too short")
        
        # Check for required roles
        roles = [char.get('role', '') for char in self.draft_summaries.values()]
        if 'protagonist' not in roles:
            issues.append("Must include protagonist character")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{len(self.draft_summaries)} characters validated\nAll required fields present"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
    
    def _format_summaries_output(self, summaries: dict) -> str:
        """Format character summaries for display"""
        if not summaries:
            return "No character summaries to display"
        
        output = []
        for char_name, character in summaries.items():
            output.append(f"**{char_name.upper()}** ({character.get('role', 'Unknown Role')})")
            output.append(f"Name: {character.get('name', 'Unnamed')}")
            output.append(f"Goal: {character.get('goal', 'Not defined')}")
            output.append(f"Conflict: {character.get('conflict', 'Not defined')}")
            output.append(f"Epiphany: {character.get('epiphany', 'Not defined')}")
            output.append(f"Arc: {character.get('one_line_arc', 'Not defined')}")
            output.append("")
        
        return "\n".join(output)
    
    def _format_single_character(self, character: dict) -> str:
        """Format single character for display"""
        return f"""Name: {character.get('name', 'Unnamed')}
Role: {character.get('role', 'Unknown')}
Goal: {character.get('goal', 'Not defined')}
Conflict: {character.get('conflict', 'Not defined')}
Epiphany: {character.get('epiphany', 'Not defined')}
One-line Arc: {character.get('one_line_arc', 'Not defined')}
Paragraph Arc: {character.get('one_paragraph_arc', 'Not defined')}"""