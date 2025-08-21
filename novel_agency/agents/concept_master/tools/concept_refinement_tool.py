"""
Concept Refinement Tool for Concept Master Agent

Integrates with existing Snowflake Step 0 functionality to refine and develop story concepts.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Dict, Any, List, Optional
import json
import sys
from pathlib import Path

# Add the src directory to the path to import existing Snowflake modules
src_path = Path(__file__).resolve().parents[4] / "src"
sys.path.insert(0, str(src_path))

try:
    from pipeline.steps.step_0_first_things_first import Step0FirstThingsFirst
    from pipeline.validators.step_0_validator import Step0Validator
except ImportError as e:
    print(f"Warning: Could not import Snowflake modules: {e}")
    Step0FirstThingsFirst = None
    Step0Validator = None


class ConceptRefinementTool(BaseTool):
    """
    Refine and develop story concepts using the Snowflake Method Step 0 process
    """
    
    story_brief: str = Field(
        ..., 
        description="Raw story brief or concept to be refined and developed"
    )
    project_id: str = Field(
        ..., 
        description="Project ID for saving the refined concept"
    )
    enhancement_focus: Optional[str] = Field(
        None, 
        description="Specific area to focus enhancement: 'genre', 'audience', 'themes', 'delight_factors'"
    )
    iterative_refinement: Optional[bool] = Field(
        False, 
        description="Whether to perform multiple refinement passes"
    )

    def run(self) -> str:
        """Refine the story concept using Snowflake Method Step 0"""
        
        try:
            # Initialize the Step 0 processor if available
            if Step0FirstThingsFirst is not None:
                step0_processor = Step0FirstThingsFirst(project_dir="novel_projects")
                success, artifact, message = step0_processor.execute(self.story_brief, self.project_id)
                
                if success:
                    # Enhance the artifact based on focus area
                    enhanced_artifact = self._enhance_concept(artifact)
                    
                    # Save enhanced version
                    self._save_enhanced_concept(enhanced_artifact)
                    
                    return self._format_success_response(enhanced_artifact, message)
                else:
                    return f"❌ Concept refinement failed: {message}"
            else:
                # Fallback to basic concept analysis if Snowflake modules unavailable
                return self._basic_concept_refinement()
                
        except Exception as e:
            return f"❌ Error during concept refinement: {str(e)}"

    def _enhance_concept(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the concept artifact based on the enhancement focus"""
        
        enhanced_artifact = artifact.copy()
        
        if self.enhancement_focus == "genre":
            enhanced_artifact = self._enhance_genre_elements(enhanced_artifact)
        elif self.enhancement_focus == "audience":
            enhanced_artifact = self._enhance_audience_definition(enhanced_artifact)
        elif self.enhancement_focus == "themes":
            enhanced_artifact = self._enhance_thematic_elements(enhanced_artifact)
        elif self.enhancement_focus == "delight_factors":
            enhanced_artifact = self._enhance_delight_factors(enhanced_artifact)
        else:
            # General enhancement
            enhanced_artifact = self._general_enhancement(enhanced_artifact)
        
        # Add concept master metadata
        enhanced_artifact["concept_master_enhancements"] = {
            "enhancement_focus": self.enhancement_focus or "general",
            "iterative_passes": 2 if self.iterative_refinement else 1,
            "creative_confidence": self._assess_creative_confidence(enhanced_artifact)
        }
        
        return enhanced_artifact

    def _enhance_genre_elements(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance genre-specific elements"""
        category = artifact.get("category", "").lower()
        
        genre_enhancements = {
            "thriller": {
                "pacing_notes": "Fast-paced with escalating tension and time pressure",
                "reader_expectations": "High stakes, constant danger, plot twists",
                "key_elements": ["ticking clock", "life-or-death stakes", "cat-and-mouse dynamics"]
            },
            "romance": {
                "pacing_notes": "Emotional beats and relationship development",
                "reader_expectations": "Character chemistry, emotional satisfaction, HEA/HFN",
                "key_elements": ["emotional conflict", "character growth", "satisfying resolution"]
            },
            "mystery": {
                "pacing_notes": "Steady revelation of clues and red herrings",
                "reader_expectations": "Fair play mystery, satisfying resolution, clever detection",
                "key_elements": ["central puzzle", "clues and misdirection", "logical resolution"]
            }
        }
        
        if category in genre_enhancements:
            artifact["genre_enhancement"] = genre_enhancements[category]
        
        return artifact

    def _enhance_audience_definition(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance target audience definition"""
        audience = artifact.get("target_audience", "")
        
        # Add detailed audience analysis
        artifact["audience_analysis"] = {
            "primary_audience": audience,
            "secondary_markets": self._identify_secondary_markets(audience, artifact.get("category", "")),
            "reader_motivations": self._identify_reader_motivations(audience),
            "market_positioning": self._suggest_market_positioning(audience, artifact.get("story_kind", ""))
        }
        
        return artifact

    def _enhance_thematic_elements(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance thematic depth and meaning"""
        story_kind = artifact.get("story_kind", "")
        
        # Extract potential themes from the story
        themes = self._extract_themes_from_story(self.story_brief)
        
        artifact["thematic_enhancement"] = {
            "core_themes": themes,
            "thematic_questions": self._generate_thematic_questions(themes),
            "moral_complexity": self._assess_moral_complexity(self.story_brief),
            "universal_appeal": self._identify_universal_elements(themes)
        }
        
        return artifact

    def _enhance_delight_factors(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance and expand delight factors"""
        existing_delights = artifact.get("delight_factors", [])
        
        # Analyze and expand delight factors
        enhanced_delights = []
        for delight in existing_delights:
            enhanced_delights.append({
                "factor": delight,
                "reader_appeal": self._analyze_reader_appeal(delight),
                "uniqueness_score": self._assess_uniqueness(delight),
                "market_differentiation": self._identify_differentiation(delight)
            })
        
        # Suggest additional delight factors
        additional_delights = self._suggest_additional_delights(artifact)
        
        artifact["enhanced_delight_factors"] = {
            "core_delights": enhanced_delights,
            "additional_suggestions": additional_delights,
            "competitive_advantages": self._identify_competitive_advantages(enhanced_delights)
        }
        
        return artifact

    def _general_enhancement(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Apply general enhancements across all areas"""
        # Apply moderate enhancements to all areas
        artifact = self._enhance_genre_elements(artifact)
        artifact = self._enhance_audience_definition(artifact)
        
        # Add overall creative assessment
        artifact["creative_assessment"] = {
            "concept_strength": self._assess_concept_strength(artifact),
            "market_potential": self._assess_market_potential(artifact),
            "creative_risks": self._identify_creative_risks(artifact),
            "enhancement_opportunities": self._identify_enhancement_opportunities(artifact)
        }
        
        return artifact

    def _basic_concept_refinement(self) -> str:
        """Basic concept refinement when Snowflake modules are unavailable"""
        
        # Basic analysis of the story brief
        analysis = {
            "word_count": len(self.story_brief.split()),
            "key_elements_identified": self._identify_basic_story_elements(),
            "genre_indicators": self._identify_genre_indicators(),
            "audience_clues": self._identify_audience_clues(),
            "concept_strength": "analyzed_manually"
        }
        
        # Save basic analysis
        self._save_basic_analysis(analysis)
        
        return f"""
📝 BASIC CONCEPT ANALYSIS COMPLETE
=================================
Story Brief Analysis:
- Word Count: {analysis['word_count']} words
- Key Elements: {', '.join(analysis['key_elements_identified'])}
- Genre Indicators: {', '.join(analysis['genre_indicators'])}

Status: Ready for director review
Note: Full Snowflake Method processing will be available once integration is complete.
"""

    def _save_enhanced_concept(self, enhanced_artifact: Dict[str, Any]) -> None:
        """Save the enhanced concept to the project directory"""
        project_dir = Path("novel_projects") / self.project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Save enhanced concept
        concept_file = project_dir / "step_0_enhanced_concept.json"
        with open(concept_file, 'w') as f:
            json.dump(enhanced_artifact, f, indent=2)

    def _save_basic_analysis(self, analysis: Dict[str, Any]) -> None:
        """Save basic analysis when full processing unavailable"""
        project_dir = Path("novel_projects") / self.project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_file = project_dir / "concept_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

    def _format_success_response(self, artifact: Dict[str, Any], original_message: str) -> str:
        """Format the success response with enhancement details"""
        
        enhancements = artifact.get("concept_master_enhancements", {})
        confidence = enhancements.get("creative_confidence", "medium")
        
        response = f"""
🎭 CONCEPT REFINEMENT COMPLETE
=============================
Project: {self.project_id}
Enhancement Focus: {enhancements.get('enhancement_focus', 'general').title()}
Creative Confidence: {confidence.title()}

CORE ELEMENTS IDENTIFIED:
Category: {artifact.get('category', 'Not specified')}
Target Audience: {artifact.get('target_audience', 'Not specified')}
Story Kind: {artifact.get('story_kind', 'Not specified')}

DELIGHT FACTORS:
{self._format_delight_factors(artifact.get('delight_factors', []))}

CREATIVE ASSESSMENT:
{self._format_creative_assessment(artifact)}

STATUS: ✅ Ready for Novel Director review and approval
NEXT STEP: Concept approval and advancement to logline development
"""
        
        return response

    def _format_delight_factors(self, delight_factors: List[str]) -> str:
        """Format delight factors for display"""
        if not delight_factors:
            return "• No delight factors identified"
        
        return "\n".join([f"• {factor}" for factor in delight_factors])

    def _format_creative_assessment(self, artifact: Dict[str, Any]) -> str:
        """Format creative assessment for display"""
        assessment = artifact.get("creative_assessment", {})
        
        if not assessment:
            return "Assessment pending full analysis"
        
        return f"""
• Concept Strength: {assessment.get('concept_strength', 'Not assessed')}
• Market Potential: {assessment.get('market_potential', 'Not assessed')}
• Key Opportunities: {len(assessment.get('enhancement_opportunities', []))} identified
"""

    # Helper methods for analysis (simplified implementations)
    def _assess_creative_confidence(self, artifact: Dict[str, Any]) -> str:
        """Assess confidence level in the concept"""
        required_elements = ["category", "target_audience", "story_kind", "delight_factors"]
        present_elements = sum(1 for elem in required_elements if artifact.get(elem))
        
        confidence_ratio = present_elements / len(required_elements)
        
        if confidence_ratio >= 0.9:
            return "high"
        elif confidence_ratio >= 0.7:
            return "medium"
        else:
            return "low"

    def _identify_basic_story_elements(self) -> List[str]:
        """Identify basic story elements from the brief"""
        elements = []
        brief_lower = self.story_brief.lower()
        
        if "detective" in brief_lower or "investigate" in brief_lower:
            elements.append("investigation")
        if "love" in brief_lower or "romance" in brief_lower:
            elements.append("romance")
        if "murder" in brief_lower or "death" in brief_lower:
            elements.append("murder/death")
        if "secret" in brief_lower or "hidden" in brief_lower:
            elements.append("secrets")
        
        return elements or ["general story elements"]

    def _identify_genre_indicators(self) -> List[str]:
        """Identify genre indicators from the brief"""
        indicators = []
        brief_lower = self.story_brief.lower()
        
        genre_keywords = {
            "thriller": ["thriller", "danger", "chase", "escape", "threat"],
            "mystery": ["mystery", "detective", "clue", "solve", "investigate"],
            "romance": ["love", "romance", "relationship", "heart", "attraction"],
            "fantasy": ["magic", "fantasy", "dragon", "wizard", "quest"],
            "sci-fi": ["space", "future", "technology", "alien", "robot"]
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in brief_lower for keyword in keywords):
                indicators.append(genre)
        
        return indicators or ["general fiction"]

    def _identify_audience_clues(self) -> List[str]:
        """Identify target audience clues from the brief"""
        clues = []
        brief_lower = self.story_brief.lower()
        
        if "adult" in brief_lower or "mature" in brief_lower:
            clues.append("adult")
        if "young" in brief_lower or "teen" in brief_lower:
            clues.append("young adult")
        if "children" in brief_lower or "kid" in brief_lower:
            clues.append("children")
        
        return clues or ["general audience"]

    # Placeholder methods for full enhancement features
    def _identify_secondary_markets(self, audience: str, category: str) -> List[str]:
        return ["secondary market analysis pending"]

    def _identify_reader_motivations(self, audience: str) -> List[str]:
        return ["reader motivation analysis pending"]

    def _suggest_market_positioning(self, audience: str, story_kind: str) -> str:
        return "Market positioning analysis pending"

    def _extract_themes_from_story(self, brief: str) -> List[str]:
        return ["theme extraction pending"]

    def _generate_thematic_questions(self, themes: List[str]) -> List[str]:
        return ["thematic questions pending"]

    def _assess_moral_complexity(self, brief: str) -> str:
        return "moral complexity assessment pending"

    def _identify_universal_elements(self, themes: List[str]) -> List[str]:
        return ["universal elements pending"]

    def _analyze_reader_appeal(self, delight: str) -> str:
        return "reader appeal analysis pending"

    def _assess_uniqueness(self, delight: str) -> str:
        return "uniqueness assessment pending"

    def _identify_differentiation(self, delight: str) -> str:
        return "differentiation analysis pending"

    def _suggest_additional_delights(self, artifact: Dict[str, Any]) -> List[str]:
        return ["additional delights pending"]

    def _identify_competitive_advantages(self, delights: List[Dict]) -> List[str]:
        return ["competitive advantages pending"]

    def _assess_concept_strength(self, artifact: Dict[str, Any]) -> str:
        return "concept strength assessment pending"

    def _assess_market_potential(self, artifact: Dict[str, Any]) -> str:
        return "market potential assessment pending"

    def _identify_creative_risks(self, artifact: Dict[str, Any]) -> List[str]:
        return ["creative risks pending"]

    def _identify_enhancement_opportunities(self, artifact: Dict[str, Any]) -> List[str]:
        return ["enhancement opportunities pending"]