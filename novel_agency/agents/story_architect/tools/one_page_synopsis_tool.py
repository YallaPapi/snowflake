"""
One Page Synopsis Tool - Step 4 of Snowflake Method

Expands paragraph summary into detailed one-page synopsis.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class OnePageSynopsisTool(BaseTool):
    """
    Tool for creating one-page synopsis (Step 4).
    Integrates with existing Snowflake Step 4 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_synopsis', 'validate_synopsis', 'refine_synopsis'")
    paragraph_data: dict = Field(default={}, description="Step 2 paragraph data to expand from")
    character_data: dict = Field(default={}, description="Step 3 character data for context")
    draft_synopsis: str = Field(default="", description="Draft synopsis for validation/refinement")
    
    def run(self) -> str:
        """Execute one-page synopsis tool action"""
        
        if self.action == "create_synopsis":
            return self._create_synopsis()
        elif self.action == "validate_synopsis":
            return self._validate_synopsis()
        elif self.action == "refine_synopsis":
            return self._refine_synopsis()
        else:
            return "Error: Invalid action. Use 'create_synopsis', 'validate_synopsis', or 'refine_synopsis'"
    
    def _create_synopsis(self) -> str:
        """Create a new one-page synopsis"""
        try:
            # Import existing Step 4 functionality
            from src.pipeline.executors.step_4_executor import Step4OnePageSynopsis
            from src.pipeline.validators.step_4_validator import Step4Validator
            
            if not self.paragraph_data:
                return "Error: Paragraph summary data required for synopsis creation"
            
            # Use existing Step 4 executor
            executor = Step4OnePageSynopsis()
            validator = Step4Validator()
            
            # Generate synopsis
            result = executor.execute(
                step_2_data=self.paragraph_data,
                step_3_data=self.character_data,
                project_id=self.paragraph_data.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    synopsis = result['artifact']['one_page_synopsis']
                    return f"✅ One-page synopsis created successfully:\n\n{synopsis}\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Synopsis created but validation failed:\n\n{result['artifact']}\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Synopsis creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_synopsis_fallback()
        except Exception as e:
            return f"❌ Error creating synopsis: {str(e)}"
    
    def _validate_synopsis(self) -> str:
        """Validate an existing synopsis"""
        if not self.draft_synopsis:
            return "Error: Draft synopsis required for validation"
        
        try:
            from src.pipeline.validators.step_4_validator import Step4Validator
            
            validator = Step4Validator()
            artifact = {'one_page_synopsis': self.draft_synopsis}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Synopsis validation passed:\n\nLength: {len(self.draft_synopsis)} characters\nAll structural checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Synopsis validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_synopsis_fallback()
        except Exception as e:
            return f"❌ Error validating synopsis: {str(e)}"
    
    def _refine_synopsis(self) -> str:
        """Refine an existing synopsis"""
        if not self.draft_synopsis:
            return "Error: Draft synopsis required for refinement"
        
        # Analyze structure and content
        paragraphs = [p.strip() for p in self.draft_synopsis.split('\n\n') if p.strip()]
        word_count = len(self.draft_synopsis.split())
        
        suggestions = []
        
        # Check length (should be roughly one page)
        if word_count < 300:
            suggestions.append(f"Synopsis seems short ({word_count} words) - consider expanding details")
        elif word_count > 800:
            suggestions.append(f"Synopsis seems long ({word_count} words) - consider condensing")
        
        # Check paragraph structure (should expand each sentence from Step 2)
        if len(paragraphs) < 4:
            suggestions.append("Should have 4-5 paragraphs expanding each sentence from paragraph summary")
        elif len(paragraphs) > 6:
            suggestions.append("Too many paragraphs - should focus on core story beats")
        
        # Check for character development
        if not any(word in self.draft_synopsis.lower() for word in ['growth', 'learns', 'realizes', 'transforms', 'changes']):
            suggestions.append("Should show clear character development and transformation")
        
        # Check for escalating conflict
        conflict_words = ['conflict', 'tension', 'crisis', 'danger', 'threat', 'challenge']
        if sum(1 for word in conflict_words if word in self.draft_synopsis.lower()) < 3:
            suggestions.append("Should emphasize escalating conflict and rising stakes")
        
        if not suggestions:
            return f"✅ Synopsis structure appears solid:\n\nLength: {word_count} words, {len(paragraphs)} paragraphs\nNo major structural issues found"
        
        return f"🔧 Synopsis refinement suggestions:\n\nCurrent: {word_count} words, {len(paragraphs)} paragraphs\n\nSuggestions:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
    def _create_synopsis_fallback(self) -> str:
        """Fallback synopsis creation when Snowflake modules unavailable"""
        if not self.paragraph_data:
            return "Error: Paragraph summary data required for synopsis creation"
        
        paragraph_summary = self.paragraph_data.get('one_paragraph_summary', '')
        moral_premise = self.paragraph_data.get('moral_premise', '')
        
        if not paragraph_summary:
            return "Error: Paragraph summary not found in provided data"
        
        # Basic expansion template
        sentences = [s.strip() for s in paragraph_summary.split('.') if s.strip()]
        
        template_paragraphs = []
        for i, sentence in enumerate(sentences[:5]):
            if i == 0:
                template_paragraphs.append(f"**Setup**: {sentence}. The story begins by establishing the protagonist's ordinary world and the circumstances that will lead to the central conflict.")
            elif i == 1:
                template_paragraphs.append(f"**First Act Crisis**: {sentence}. This initial disaster forces the protagonist into the story and sets up the central conflict.")
            elif i == 2:
                template_paragraphs.append(f"**Second Act Complications**: {sentence}. The situation becomes more complex as the protagonist's initial attempts to resolve the conflict create new problems.")
            elif i == 3:
                template_paragraphs.append(f"**Third Act Crisis**: {sentence}. Everything reaches a breaking point as the protagonist faces their greatest challenge.")
            elif i == 4:
                template_paragraphs.append(f"**Resolution**: {sentence}. The protagonist must draw on everything they've learned to achieve resolution and transformation.")
        
        synopsis = '\n\n'.join(template_paragraphs)
        
        if moral_premise:
            synopsis += f"\n\n**Thematic Foundation**: {moral_premise}"
        
        return f"📝 Draft synopsis created (fallback mode):\n\n{synopsis}\n\n⚠️ Note: Using expansion template. Recommend adding story-specific details and character development."
    
    def _validate_synopsis_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        paragraphs = [p.strip() for p in self.draft_synopsis.split('\n\n') if p.strip()]
        word_count = len(self.draft_synopsis.split())
        issues = []
        
        if word_count < 200:
            issues.append(f"Too short: {word_count} words (minimum: 200)")
        elif word_count > 1000:
            issues.append(f"Too long: {word_count} words (maximum: 1000)")
        
        if len(paragraphs) < 3:
            issues.append(f"Too few paragraphs: {len(paragraphs)} (minimum: 3)")
        elif len(paragraphs) > 7:
            issues.append(f"Too many paragraphs: {len(paragraphs)} (maximum: 7)")
        
        if not any(c.isupper() for c in self.draft_synopsis):
            issues.append("Should have proper capitalization")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{word_count} words, {len(paragraphs)} paragraphs\nBasic structure appears sound"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)