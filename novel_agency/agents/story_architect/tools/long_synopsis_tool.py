"""
Long Synopsis Tool - Step 6 of Snowflake Method

Creates comprehensive 4-5 page story synopsis.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class LongSynopsisTool(BaseTool):
    """
    Tool for creating long synopsis (Step 6).
    Integrates with existing Snowflake Step 6 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_synopsis', 'validate_synopsis', 'refine_synopsis'")
    one_page_data: dict = Field(default={}, description="Step 4 one-page synopsis data to expand from")
    character_data: dict = Field(default={}, description="Step 5 character synopsis data for context")
    draft_synopsis: str = Field(default="", description="Draft long synopsis for validation/refinement")
    
    def run(self) -> str:
        """Execute long synopsis tool action"""
        
        if self.action == "create_synopsis":
            return self._create_synopsis()
        elif self.action == "validate_synopsis":
            return self._validate_synopsis()
        elif self.action == "refine_synopsis":
            return self._refine_synopsis()
        else:
            return "Error: Invalid action. Use 'create_synopsis', 'validate_synopsis', or 'refine_synopsis'"
    
    def _create_synopsis(self) -> str:
        """Create a new long synopsis"""
        try:
            # Import existing Step 6 functionality
            from src.pipeline.executors.step_6_executor import Step6LongSynopsis
            from src.pipeline.validators.step_6_validator import Step6Validator
            
            if not self.one_page_data:
                return "Error: One-page synopsis data required for long synopsis creation"
            
            # Use existing Step 6 executor
            executor = Step6LongSynopsis()
            validator = Step6Validator()
            
            # Generate long synopsis
            result = executor.execute(
                step_4_data=self.one_page_data,
                step_5_data=self.character_data,
                project_id=self.one_page_data.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    synopsis = result['artifact']['long_synopsis']
                    return f"✅ Long synopsis created successfully:\n\n{synopsis[:500]}...\n\n[Full synopsis: {len(synopsis)} characters]\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Synopsis created but validation failed:\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Synopsis creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_synopsis_fallback()
        except Exception as e:
            return f"❌ Error creating synopsis: {str(e)}"
    
    def _validate_synopsis(self) -> str:
        """Validate an existing long synopsis"""
        if not self.draft_synopsis:
            return "Error: Draft synopsis required for validation"
        
        try:
            from src.pipeline.validators.step_6_validator import Step6Validator
            
            validator = Step6Validator()
            artifact = {'long_synopsis': self.draft_synopsis}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Long synopsis validation passed:\n\nLength: {len(self.draft_synopsis)} characters\nAll structural checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Synopsis validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_synopsis_fallback()
        except Exception as e:
            return f"❌ Error validating synopsis: {str(e)}"
    
    def _refine_synopsis(self) -> str:
        """Refine an existing long synopsis"""
        if not self.draft_synopsis:
            return "Error: Draft synopsis required for refinement"
        
        # Analyze structure and content
        sections = [s.strip() for s in self.draft_synopsis.split('\n\n') if s.strip()]
        word_count = len(self.draft_synopsis.split())
        
        suggestions = []
        
        # Check length (should be 4-5 pages, roughly 1000-2500 words)
        if word_count < 1000:
            suggestions.append(f"Synopsis seems short ({word_count} words) - should be 4-5 pages (1000-2500 words)")
        elif word_count > 3000:
            suggestions.append(f"Synopsis seems very long ({word_count} words) - consider condensing to 2500 words max")
        
        # Check section structure
        if len(sections) < 8:
            suggestions.append("Should have detailed sections expanding each paragraph from one-page synopsis")
        elif len(sections) > 15:
            suggestions.append("Too many sections - consider consolidating for better flow")
        
        # Check for detailed character development
        character_terms = ['motivation', 'backstory', 'psychology', 'internal', 'emotional', 'growth', 'arc']
        character_score = sum(1 for term in character_terms if term in self.draft_synopsis.lower())
        
        if character_score < 3:
            suggestions.append("Should include more detailed character development and psychology")
        
        # Check for scene-level detail
        scene_terms = ['scene', 'setting', 'dialogue', 'action', 'moment', 'beat']
        scene_score = sum(1 for term in scene_terms if term in self.draft_synopsis.lower())
        
        if scene_score < 5:
            suggestions.append("Should include more scene-level details and specific story beats")
        
        # Check for thematic depth
        theme_terms = ['theme', 'meaning', 'symbolism', 'metaphor', 'represents', 'explores']
        theme_score = sum(1 for term in theme_terms if term in self.draft_synopsis.lower())
        
        if theme_score < 2:
            suggestions.append("Should explore thematic elements and deeper story meaning")
        
        if not suggestions:
            return f"✅ Long synopsis structure appears comprehensive:\n\nLength: {word_count} words, {len(sections)} sections\nCharacter depth: {character_score}/7\nScene detail: {scene_score}/6\nThematic depth: {theme_score}/6\n\nNo major structural issues found"
        
        return f"🔧 Long synopsis refinement suggestions:\n\nCurrent: {word_count} words, {len(sections)} sections\n\nSuggestions:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
    def _create_synopsis_fallback(self) -> str:
        """Fallback synopsis creation when Snowflake modules unavailable"""
        if not self.one_page_data:
            return "Error: One-page synopsis data required for long synopsis creation"
        
        one_page = self.one_page_data.get('one_page_synopsis', '')
        
        if not one_page:
            return "Error: One-page synopsis not found in provided data"
        
        # Basic expansion framework
        template = f"""# LONG SYNOPSIS (4-5 Pages)

## ACT I: SETUP AND INCITING INCIDENT

{one_page[:200]}...

[Detailed expansion of opening, introducing protagonist's ordinary world, establishing relationships, and building to the inciting incident. Include character backgrounds, motivations, and the specific circumstances that launch the main story.]

## ACT II-A: RISING ACTION AND FIRST OBSTACLES  

[Expansion of first disaster and initial attempts to resolve conflict. Detail the protagonist's plan, early obstacles, and introduction of key supporting characters and antagonistic forces.]

## ACT II-B: COMPLICATIONS AND MIDPOINT CRISIS

[Expansion of second disaster. Show how initial solutions create new problems, raise stakes, and force character growth. Include subplot development and relationship dynamics.]

## ACT III-A: FINAL OBSTACLES AND DARK MOMENT

[Expansion of third disaster. Everything seems lost, protagonist faces their greatest fear/weakness, all seems hopeless. This is the dark night of the soul.]

## ACT III-B: CLIMAX AND RESOLUTION

[Detailed resolution showing how protagonist overcomes through growth and applies lessons learned. Specific actions, final confrontation, and emotional/thematic resolution.]

## CHARACTER ARCS AND THEMES

[Analysis of how main characters change throughout the story and what deeper meanings the story explores.]

**Length Target**: 1500-2500 words
**Current Draft**: ~400 words"""
        
        return f"📝 Long synopsis framework created (fallback mode):\n\n{template}\n\n⚠️ Note: This is a structural template. Requires substantial development with story-specific details, character depth, and scene-level specificity."
    
    def _validate_synopsis_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        sections = [s.strip() for s in self.draft_synopsis.split('\n\n') if s.strip()]
        word_count = len(self.draft_synopsis.split())
        issues = []
        
        if word_count < 800:
            issues.append(f"Too short: {word_count} words (minimum: 800)")
        elif word_count > 3500:
            issues.append(f"Too long: {word_count} words (maximum: 3500)")
        
        if len(sections) < 6:
            issues.append(f"Too few sections: {len(sections)} (minimum: 6)")
        elif len(sections) > 20:
            issues.append(f"Too many sections: {len(sections)} (maximum: 20)")
        
        # Check for comprehensive coverage
        if 'character' not in self.draft_synopsis.lower():
            issues.append("Should include character development details")
        
        if not any(word in self.draft_synopsis.lower() for word in ['scene', 'moment', 'action']):
            issues.append("Should include scene-level story details")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{word_count} words, {len(sections)} sections\nComprehensive structure appears present"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)