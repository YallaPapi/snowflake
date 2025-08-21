"""
Logline Tool - Step 1 of Snowflake Method

Creates compelling one-sentence story summaries.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class LoglineTool(BaseTool):
    """
    Tool for creating compelling one-sentence story loglines (Step 1).
    Integrates with existing Snowflake Step 1 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_logline', 'validate_logline', 'refine_logline'")
    concept_data: dict = Field(default={}, description="Step 0 concept data to build from")
    draft_logline: str = Field(default="", description="Draft logline text for validation/refinement")
    
    def run(self) -> str:
        """Execute logline tool action"""
        
        if self.action == "create_logline":
            return self._create_logline()
        elif self.action == "validate_logline":
            return self._validate_logline()
        elif self.action == "refine_logline":
            return self._refine_logline()
        else:
            return "Error: Invalid action. Use 'create_logline', 'validate_logline', or 'refine_logline'"
    
    def _create_logline(self) -> str:
        """Create a new logline from concept data"""
        try:
            # Import existing Step 1 functionality
            from src.pipeline.executors.step_1_executor import Step1OnesentenceSummary
            from src.pipeline.validators.step_1_validator import Step1Validator
            
            if not self.concept_data:
                return "Error: Concept data required for logline creation"
            
            # Use existing Step 1 executor
            executor = Step1OnesentenceSummary()
            validator = Step1Validator()
            
            # Generate logline
            result = executor.execute(
                step_0_data=self.concept_data,
                project_id=self.concept_data.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    return f"✅ Logline created successfully:\n\n{result['artifact']['one_sentence_summary']}\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Logline created but validation failed:\n\n{result['artifact']['one_sentence_summary']}\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Logline creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_logline_fallback()
        except Exception as e:
            return f"❌ Error creating logline: {str(e)}"
    
    def _validate_logline(self) -> str:
        """Validate an existing logline"""
        if not self.draft_logline:
            return "Error: Draft logline required for validation"
        
        try:
            from src.pipeline.validators.step_1_validator import Step1Validator
            
            validator = Step1Validator()
            artifact = {'one_sentence_summary': self.draft_logline}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Logline validation passed:\n\n{self.draft_logline}\n\nAll checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Logline validation failed:\n\n{self.draft_logline}\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_logline_fallback()
        except Exception as e:
            return f"❌ Error validating logline: {str(e)}"
    
    def _refine_logline(self) -> str:
        """Refine an existing logline"""
        if not self.draft_logline:
            return "Error: Draft logline required for refinement"
        
        # Analyze current logline for improvement opportunities
        word_count = len(self.draft_logline.split())
        
        suggestions = []
        if word_count > 25:
            suggestions.append(f"Reduce word count from {word_count} to 25 or fewer")
        if self.draft_logline.count(',') > 2:
            suggestions.append("Simplify sentence structure - avoid too many clauses")
        if any(word in self.draft_logline.lower() for word in ['ends', 'finally', 'discovers', 'realizes']):
            suggestions.append("Avoid revealing the ending in the logline")
        
        if not suggestions:
            return f"✅ Logline appears well-crafted:\n\n{self.draft_logline}\n\nNo major refinements needed"
        
        return f"🔧 Logline refinement suggestions:\n\n{self.draft_logline}\n\nSuggestions:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
    def _create_logline_fallback(self) -> str:
        """Fallback logline creation when Snowflake modules unavailable"""
        if not self.concept_data:
            return "Error: Concept data required for logline creation"
        
        category = self.concept_data.get('category', 'Unknown')
        story_kind = self.concept_data.get('story_kind', 'Unknown')
        delight = self.concept_data.get('delight_statement', 'An engaging story')
        
        template = f"A {category} {story_kind} about {delight}"
        
        return f"📝 Draft logline created (fallback mode):\n\n{template}\n\n⚠️ Note: Using basic template. Recommend manual refinement for optimal results."
    
    def _validate_logline_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        word_count = len(self.draft_logline.split())
        issues = []
        
        if word_count > 25:
            issues.append(f"Too long: {word_count} words (limit: 25)")
        if word_count < 8:
            issues.append(f"Too short: {word_count} words (minimum: 8)")
        if not any(c.isupper() for c in self.draft_logline):
            issues.append("Should start with capital letter")
        if not self.draft_logline.endswith('.'):
            issues.append("Should end with period")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{self.draft_logline}\n\nWord count: {word_count}/25"
        else:
            return f"⚠️ Validation issues found:\n\n{self.draft_logline}\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)