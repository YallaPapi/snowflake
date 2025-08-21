"""
Paragraph Summary Tool - Step 2 of Snowflake Method

Creates structured 5-sentence story summaries with moral premise.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class ParagraphSummaryTool(BaseTool):
    """
    Tool for creating 5-sentence paragraph summaries with moral premise (Step 2).
    Integrates with existing Snowflake Step 2 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_summary', 'validate_summary', 'refine_summary'")
    logline_data: dict = Field(default={}, description="Step 1 logline data to expand from")
    draft_summary: str = Field(default="", description="Draft paragraph summary for validation/refinement")
    draft_moral_premise: str = Field(default="", description="Draft moral premise for validation/refinement")
    
    def run(self) -> str:
        """Execute paragraph summary tool action"""
        
        if self.action == "create_summary":
            return self._create_summary()
        elif self.action == "validate_summary":
            return self._validate_summary()
        elif self.action == "refine_summary":
            return self._refine_summary()
        else:
            return "Error: Invalid action. Use 'create_summary', 'validate_summary', or 'refine_summary'"
    
    def _create_summary(self) -> str:
        """Create a new paragraph summary from logline data"""
        try:
            # Import existing Step 2 functionality
            from src.pipeline.executors.step_2_executor import Step2OneParagraphSummary
            from src.pipeline.validators.step_2_validator import Step2Validator
            
            if not self.logline_data:
                return "Error: Logline data required for paragraph summary creation"
            
            # Use existing Step 2 executor
            executor = Step2OneParagraphSummary()
            validator = Step2Validator()
            
            # Generate paragraph summary
            result = executor.execute(
                step_1_data=self.logline_data,
                project_id=self.logline_data.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    summary = result['artifact']['one_paragraph_summary']
                    moral_premise = result['artifact']['moral_premise']
                    return f"✅ Paragraph summary created successfully:\n\n**Summary:**\n{summary}\n\n**Moral Premise:**\n{moral_premise}\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Summary created but validation failed:\n\n{result['artifact']}\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Summary creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_summary_fallback()
        except Exception as e:
            return f"❌ Error creating summary: {str(e)}"
    
    def _validate_summary(self) -> str:
        """Validate an existing paragraph summary"""
        if not self.draft_summary:
            return "Error: Draft summary required for validation"
        
        try:
            from src.pipeline.validators.step_2_validator import Step2Validator
            
            validator = Step2Validator()
            artifact = {
                'one_paragraph_summary': self.draft_summary,
                'moral_premise': self.draft_moral_premise
            }
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Summary validation passed:\n\n**Summary:**\n{self.draft_summary}\n\n**Moral Premise:**\n{self.draft_moral_premise}\n\nAll checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Summary validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_summary_fallback()
        except Exception as e:
            return f"❌ Error validating summary: {str(e)}"
    
    def _refine_summary(self) -> str:
        """Refine an existing paragraph summary"""
        if not self.draft_summary:
            return "Error: Draft summary required for refinement"
        
        # Analyze structure
        sentences = [s.strip() for s in self.draft_summary.split('.') if s.strip()]
        
        suggestions = []
        if len(sentences) != 5:
            suggestions.append(f"Structure should be exactly 5 sentences (found {len(sentences)})")
        
        # Check for disaster progression
        disaster_keywords = ['disaster', 'crisis', 'conflict', 'problem', 'threat', 'challenge']
        disaster_mentions = sum(1 for sentence in sentences for keyword in disaster_keywords if keyword in sentence.lower())
        
        if disaster_mentions < 2:
            suggestions.append("Should include clear progression through multiple disasters/conflicts")
        
        # Check for character focus
        if not any(pronoun in self.draft_summary.lower() for pronoun in ['he', 'she', 'they', 'protagonist']):
            suggestions.append("Should focus on protagonist's journey and character arc")
        
        if not suggestions:
            return f"✅ Summary structure appears solid:\n\n{self.draft_summary}\n\nNo major structural issues found"
        
        return f"🔧 Summary refinement suggestions:\n\n{self.draft_summary}\n\nSuggestions:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
    def _create_summary_fallback(self) -> str:
        """Fallback summary creation when Snowflake modules unavailable"""
        if not self.logline_data:
            return "Error: Logline data required for summary creation"
        
        logline = self.logline_data.get('one_sentence_summary', 'A compelling story unfolds')
        
        template = f"""Sentence 1 (Setup): {logline}
Sentence 2 (First Disaster): The protagonist faces their first major challenge.
Sentence 3 (Second Disaster): The situation becomes more complicated and stakes rise.
Sentence 4 (Third Disaster): Everything seems lost as the final crisis emerges.
Sentence 5 (Resolution): The protagonist overcomes through growth and transformation.

Moral Premise: Through facing adversity, characters discover their true strength."""
        
        return f"📝 Draft summary created (fallback mode):\n\n{template}\n\n⚠️ Note: Using basic template. Recommend manual refinement for story-specific details."
    
    def _validate_summary_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        sentences = [s.strip() for s in self.draft_summary.split('.') if s.strip()]
        issues = []
        
        if len(sentences) != 5:
            issues.append(f"Should be exactly 5 sentences (found {len(sentences)})")
        
        if len(self.draft_summary) < 200:
            issues.append("Summary seems too short - should be a full paragraph")
        elif len(self.draft_summary) > 800:
            issues.append("Summary seems too long - should be concise")
        
        if not self.draft_moral_premise:
            issues.append("Moral premise is required")
        elif len(self.draft_moral_premise.split()) < 5:
            issues.append("Moral premise should be more substantial")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n**Summary:** {len(sentences)} sentences, {len(self.draft_summary)} characters\n**Moral Premise:** {len(self.draft_moral_premise.split())} words"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)