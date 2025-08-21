"""
Character Synopsis Tool - Step 5 of Snowflake Method

Develops detailed character synopses with backstory and psychology.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class CharacterSynopsisTool(BaseTool):
    """
    Tool for creating detailed character synopses (Step 5).
    Integrates with existing Snowflake Step 5 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_synopses', 'validate_synopses', 'expand_character'")
    character_summaries: dict = Field(default={}, description="Step 3 character summaries to expand from")
    story_structure: dict = Field(default={}, description="Step 4 story structure for context")
    character_name: str = Field(default="", description="Specific character name for expansion")
    draft_synopses: dict = Field(default={}, description="Draft character synopses for validation")
    
    def run(self) -> str:
        """Execute character synopsis tool action"""
        
        if self.action == "create_synopses":
            return self._create_synopses()
        elif self.action == "validate_synopses":
            return self._validate_synopses()
        elif self.action == "expand_character":
            return self._expand_character()
        else:
            return "Error: Invalid action. Use 'create_synopses', 'validate_synopses', or 'expand_character'"
    
    def _create_synopses(self) -> str:
        """Create detailed character synopses"""
        try:
            # Import existing Step 5 functionality
            from src.pipeline.executors.step_5_executor import Step5CharacterSynopses
            from src.pipeline.validators.step_5_validator import Step5Validator
            
            if not self.character_summaries:
                return "Error: Character summaries required for synopsis creation"
            
            # Use existing Step 5 executor
            executor = Step5CharacterSynopses()
            validator = Step5Validator()
            
            # Generate character synopses
            result = executor.execute(
                step_3_data={'character_summaries': self.character_summaries},
                step_4_data=self.story_structure,
                project_id=self.character_summaries.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    synopses = result['artifact']['character_synopses']
                    synopsis_text = self._format_synopses_output(synopses)
                    return f"✅ Character synopses created successfully:\n\n{synopsis_text[:800]}...\n\n[{len(synopses)} characters developed]\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Synopses created but validation failed:\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Synopsis creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_synopses_fallback()
        except Exception as e:
            return f"❌ Error creating synopses: {str(e)}"
    
    def _validate_synopses(self) -> str:
        """Validate existing character synopses"""
        if not self.draft_synopses:
            return "Error: Draft synopses required for validation"
        
        try:
            from src.pipeline.validators.step_5_validator import Step5Validator
            
            validator = Step5Validator()
            artifact = {'character_synopses': self.draft_synopses}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Character synopses validation passed:\n\n{len(self.draft_synopses)} character synopses validated\nAll depth and structure checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Synopsis validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_synopses_fallback()
        except Exception as e:
            return f"❌ Error validating synopses: {str(e)}"
    
    def _expand_character(self) -> str:
        """Expand a specific character synopsis"""
        if not self.character_name:
            return "Error: Character name required for expansion"
        
        if not self.character_summaries or self.character_name not in self.character_summaries:
            return f"Error: Character '{self.character_name}' not found in summaries"
        
        character_summary = self.character_summaries[self.character_name]
        
        # Create expanded synopsis
        expanded_synopsis = self._create_detailed_synopsis(self.character_name, character_summary)
        
        return f"✅ Expanded synopsis for '{self.character_name}':\n\n{expanded_synopsis}"
    
    def _create_synopses_fallback(self) -> str:
        """Fallback synopsis creation when Snowflake modules unavailable"""
        if not self.character_summaries:
            return "Error: Character summaries required for synopsis creation"
        
        synopses = {}
        
        for char_name, char_summary in self.character_summaries.items():
            synopses[char_name] = self._create_detailed_synopsis(char_name, char_summary)
        
        synopsis_text = self._format_synopses_output(synopses)
        
        return f"📝 Character synopses created (fallback mode):\n\n{synopsis_text[:800]}...\n\n[{len(synopses)} characters developed]\n\n⚠️ Note: Using template expansion. Recommend adding story-specific psychological depth and backstory details."
    
    def _validate_synopses_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        issues = []
        
        if not isinstance(self.draft_synopses, dict):
            issues.append("Synopses should be a dictionary with character names as keys")
            return f"⚠️ Validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
        
        for char_name, synopsis in self.draft_synopses.items():
            if not isinstance(synopsis, str):
                issues.append(f"Synopsis for '{char_name}' should be text")
                continue
            
            word_count = len(synopsis.split())
            if word_count < 100:
                issues.append(f"Synopsis for '{char_name}' too short ({word_count} words, minimum 100)")
            elif word_count > 800:
                issues.append(f"Synopsis for '{char_name}' too long ({word_count} words, maximum 800)")
            
            # Check for key elements
            required_elements = ['backstory', 'psychology', 'motivation', 'relationship']
            missing_elements = [elem for elem in required_elements if elem not in synopsis.lower()]
            if missing_elements:
                issues.append(f"Synopsis for '{char_name}' missing: {', '.join(missing_elements)}")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{len(self.draft_synopses)} synopses validated\nAll required elements present"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
    
    def _create_detailed_synopsis(self, char_name: str, char_summary: dict) -> str:
        """Create detailed character synopsis from summary"""
        role = char_summary.get('role', 'character')
        name = char_summary.get('name', char_name)
        goal = char_summary.get('goal', 'Undefined goal')
        conflict = char_summary.get('conflict', 'Undefined conflict')
        epiphany = char_summary.get('epiphany', 'Undefined epiphany')
        arc = char_summary.get('one_paragraph_arc', 'Undefined arc')
        
        # Build comprehensive synopsis
        synopsis_parts = []
        
        # Introduction and role
        synopsis_parts.append(f"**{name}** serves as the {role} in this story, driving key narrative elements through their personal journey and relationships with other characters.")
        
        # Backstory and psychology
        if role == 'protagonist':
            synopsis_parts.append(f"**Backstory & Psychology**: {name} begins the story with a complex psychological landscape shaped by past experiences. Their motivation stems from {goal.lower()}, but they are hindered by deep-seated fears and limiting beliefs. The character's internal world is rich with contradictions - they possess both strengths that will serve them well and blind spots that create vulnerability.")
        
        elif role == 'antagonist':
            synopsis_parts.append(f"**Backstory & Psychology**: {name} represents the primary opposition force, but their antagonism springs from believable motivations. They are not evil for evil's sake; rather, their psychology is shaped by experiences that have led them to believe their approach is justified. Their goal of {goal.lower()} puts them in direct conflict with the protagonist, but their methods and worldview stem from a coherent internal logic.")
        
        else:
            synopsis_parts.append(f"**Backstory & Psychology**: {name} brings their own rich history and psychological complexity to the story. Their personal motivation of {goal.lower()} interweaves with the main plot while maintaining their distinct identity. They are neither purely functional nor purely decorative - they have agency and desires that create authentic relationships with other characters.")
        
        # Conflict and obstacles
        synopsis_parts.append(f"**Central Conflict**: The character's primary struggle revolves around {conflict.lower()}. This conflict operates on multiple levels - external obstacles that prevent goal achievement, and internal barriers that must be overcome for true growth. The tension between what they want and what they need creates compelling character moments throughout the story.")
        
        # Character relationships and role in plot
        synopsis_parts.append(f"**Relationships & Plot Function**: {name} doesn't exist in isolation but forms dynamic relationships that drive story forward. Their interactions with other characters reveal different facets of their personality while serving specific plot functions. They both influence and are influenced by the central storyline, creating authentic cause-and-effect relationships.")
        
        # Growth and transformation
        synopsis_parts.append(f"**Character Arc & Transformation**: {arc} This growth isn't arbitrary but emerges organically from the character's struggles and choices. Their epiphany - {epiphany.lower()} - represents a fundamental shift in understanding that enables new actions and relationships. The transformation feels earned because it grows from authentic character struggle.")
        
        # Resolution and thematic significance
        if role == 'protagonist':
            synopsis_parts.append(f"**Resolution & Theme**: By story's end, {name} has achieved not just their external goal but more importantly, their internal transformation. They embody the story's thematic message through their journey, demonstrating how human beings can grow, change, and overcome both external obstacles and internal limitations.")
        else:
            synopsis_parts.append(f"**Resolution & Theme**: {name}'s fate in the story serves both plot and thematic functions. Whether they achieve their goals or face consequences, their journey illuminates important aspects of the story's deeper meaning about human nature, choice, and consequence.")
        
        return "\n\n".join(synopsis_parts)
    
    def _format_synopses_output(self, synopses: dict) -> str:
        """Format character synopses for display"""
        if not synopses:
            return "No character synopses to display"
        
        output = []
        for char_name, synopsis in synopses.items():
            output.append(f"## {char_name.upper()}")
            output.append(synopsis[:300] + "..." if len(synopsis) > 300 else synopsis)
            output.append("")
        
        return "\n".join(output)