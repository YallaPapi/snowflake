"""
Genre Analysis Tool for Concept Master Agent

Analyzes and provides insights about genre conventions, market expectations, and positioning.
"""

from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Dict, Any, List, Optional
import json
from pathlib import Path


class GenreAnalysisTool(BaseTool):
    """
    Analyze genre conventions, market expectations, and positioning for story concepts
    """
    
    genre: str = Field(
        ..., 
        description="Primary genre to analyze (e.g., 'thriller', 'romance', 'mystery', 'fantasy')"
    )
    subgenre: Optional[str] = Field(
        None, 
        description="Subgenre for more specific analysis (e.g., 'police procedural', 'romantic suspense')"
    )
    analysis_focus: str = Field(
        "comprehensive", 
        description="Focus area: 'conventions', 'market', 'audience', 'comprehensive'"
    )
    target_audience: Optional[str] = Field(
        None, 
        description="Specific target audience for tailored analysis"
    )
    competitive_context: Optional[bool] = Field(
        False, 
        description="Include competitive landscape analysis"
    )

    def run(self) -> str:
        """Perform genre analysis and provide insights"""
        
        try:
            # Get genre database
            genre_data = self._get_genre_database()
            
            # Perform requested analysis
            if self.analysis_focus == "conventions":
                return self._analyze_conventions(genre_data)
            elif self.analysis_focus == "market":
                return self._analyze_market(genre_data)
            elif self.analysis_focus == "audience":
                return self._analyze_audience(genre_data)
            else:
                return self._comprehensive_analysis(genre_data)
                
        except Exception as e:
            return f"❌ Genre analysis error: {str(e)}"

    def _get_genre_database(self) -> Dict[str, Any]:
        """Get genre information database"""
        
        # Comprehensive genre database
        genre_db = {
            "thriller": {
                "core_conventions": {
                    "pacing": "Fast-paced with escalating tension",
                    "structure": "Ticking clock, mounting pressure, climactic confrontation",
                    "protagonist": "Ordinary person thrust into extraordinary circumstances",
                    "stakes": "Life and death, often extending to loved ones or society",
                    "tone": "Suspenseful, urgent, high-tension"
                },
                "reader_expectations": {
                    "plot_twists": "Multiple reversals and surprises",
                    "action": "Physical confrontations and chase sequences",
                    "resolution": "Clear victory over antagonist",
                    "emotional_journey": "From vulnerability to empowerment"
                },
                "market_data": {
                    "target_demographics": ["Adults 25-55", "Equal male/female appeal"],
                    "popular_subgenres": ["Political thriller", "Medical thriller", "Techno-thriller"],
                    "average_length": "80,000-100,000 words",
                    "market_size": "Large, established market"
                },
                "success_elements": [
                    "Compelling hook in first chapter",
                    "Escalating stakes throughout",
                    "Strong antagonist with clear motivation",
                    "Satisfying action sequences",
                    "Tight plotting with no wasted scenes"
                ]
            },
            
            "romance": {
                "core_conventions": {
                    "pacing": "Relationship-driven with emotional beats",
                    "structure": "Meet-cute, conflict, separation, reunion, HEA/HFN",
                    "protagonist": "Relatable character seeking love/fulfillment",
                    "stakes": "Emotional fulfillment, personal growth, true love",
                    "tone": "Emotional, hopeful, intimate"
                },
                "reader_expectations": {
                    "chemistry": "Palpable attraction between leads",
                    "conflict": "Believable obstacles to relationship",
                    "resolution": "Happy Ever After or Happy For Now",
                    "emotional_journey": "From loneliness/mistrust to love/commitment"
                },
                "market_data": {
                    "target_demographics": ["Women 18-65", "Growing male readership"],
                    "popular_subgenres": ["Contemporary", "Historical", "Paranormal", "Romantic suspense"],
                    "average_length": "50,000-90,000 words",
                    "market_size": "Largest fiction market segment"
                },
                "success_elements": [
                    "Strong emotional connection between leads",
                    "Believable relationship conflict",
                    "Satisfying romantic resolution",
                    "Compelling individual character arcs",
                    "Appropriate heat level for target market"
                ]
            },
            
            "mystery": {
                "core_conventions": {
                    "pacing": "Steady revelation of clues and information",
                    "structure": "Crime, investigation, red herrings, revelation, resolution",
                    "protagonist": "Detective (professional or amateur) with deductive skills",
                    "stakes": "Justice, truth, solving the puzzle",
                    "tone": "Cerebral, methodical, puzzle-focused"
                },
                "reader_expectations": {
                    "fair_play": "Reader has same clues as detective",
                    "logical_resolution": "Solution must make sense in retrospect",
                    "red_herrings": "False leads that misdirect but don't cheat",
                    "satisfaction": "Clever detection and just resolution"
                },
                "market_data": {
                    "target_demographics": ["Adults 35-70", "Slight female skew"],
                    "popular_subgenres": ["Cozy mystery", "Police procedural", "Historical mystery"],
                    "average_length": "70,000-90,000 words", 
                    "market_size": "Solid, loyal readership"
                },
                "success_elements": [
                    "Compelling central mystery",
                    "Engaging detective character",
                    "Fair clue placement",
                    "Satisfying logical resolution",
                    "Appropriate series potential"
                ]
            },
            
            "fantasy": {
                "core_conventions": {
                    "pacing": "Quest-driven with world-building integration",
                    "structure": "Call to adventure, trials, transformation, return",
                    "protagonist": "Chosen one or reluctant hero with special destiny",
                    "stakes": "Fate of world/realm, magical balance, personal power",
                    "tone": "Epic, magical, wonder-filled"
                },
                "reader_expectations": {
                    "world_building": "Rich, consistent magical world",
                    "magic_system": "Clear rules and limitations",
                    "epic_scope": "Large-scale conflicts and consequences",
                    "character_growth": "Hero's journey transformation"
                },
                "market_data": {
                    "target_demographics": ["Teens and adults 14-45", "Growing cross-demographic appeal"],
                    "popular_subgenres": ["Urban fantasy", "Epic fantasy", "Romantic fantasy"],
                    "average_length": "80,000-120,000+ words",
                    "market_size": "Large and growing"
                },
                "success_elements": [
                    "Immersive world-building",
                    "Compelling magic system",
                    "Epic scope and stakes",
                    "Strong character development",
                    "Series potential"
                ]
            },
            
            "science_fiction": {
                "core_conventions": {
                    "pacing": "Idea-driven with technological integration",
                    "structure": "Problem/discovery, exploration, conflict, resolution",
                    "protagonist": "Scientist, explorer, or ordinary person in extraordinary circumstances",
                    "stakes": "Humanity's future, technological implications, survival",
                    "tone": "Speculative, analytical, wonder-based"
                },
                "reader_expectations": {
                    "scientific_plausibility": "Believable extrapolation from current science",
                    "technological_focus": "Technology as plot driver",
                    "big_ideas": "Exploration of concepts and implications",
                    "future_vision": "Compelling vision of what might be"
                },
                "market_data": {
                    "target_demographics": ["Adults 25-55", "Male skew but diversifying"],
                    "popular_subgenres": ["Space opera", "Cyberpunk", "Hard SF", "Dystopian"],
                    "average_length": "80,000-100,000 words",
                    "market_size": "Dedicated but smaller than other genres"
                },
                "success_elements": [
                    "Strong scientific concept",
                    "Believable future world",
                    "Exploration of big ideas",
                    "Human story within SF elements",
                    "Logical consequence development"
                ]
            }
        }
        
        return genre_db.get(self.genre.lower(), {})

    def _analyze_conventions(self, genre_data: Dict[str, Any]) -> str:
        """Analyze genre conventions and requirements"""
        
        if not genre_data:
            return f"❌ Genre '{self.genre}' not found in database. Available genres: thriller, romance, mystery, fantasy, science_fiction"
        
        conventions = genre_data.get("core_conventions", {})
        expectations = genre_data.get("reader_expectations", {})
        
        return f"""
📚 GENRE CONVENTIONS ANALYSIS: {self.genre.upper()}
{'=' * 50}

CORE CONVENTIONS:
• Pacing: {conventions.get('pacing', 'Not specified')}
• Structure: {conventions.get('structure', 'Not specified')}
• Protagonist Type: {conventions.get('protagonist', 'Not specified')}
• Typical Stakes: {conventions.get('stakes', 'Not specified')}
• Tone: {conventions.get('tone', 'Not specified')}

READER EXPECTATIONS:
{self._format_expectations(expectations)}

COMPLIANCE CHECKLIST:
{self._create_compliance_checklist(conventions, expectations)}

SUBGENRE CONSIDERATIONS:
{self._analyze_subgenre_variations() if self.subgenre else "No subgenre specified"}
"""

    def _analyze_market(self, genre_data: Dict[str, Any]) -> str:
        """Analyze market conditions and opportunities"""
        
        if not genre_data:
            return f"❌ Genre '{self.genre}' not found in database."
        
        market_data = genre_data.get("market_data", {})
        success_elements = genre_data.get("success_elements", [])
        
        return f"""
📊 MARKET ANALYSIS: {self.genre.upper()}
{'=' * 40}

TARGET DEMOGRAPHICS:
{self._format_demographics(market_data.get('target_demographics', []))}

POPULAR SUBGENRES:
{self._format_subgenres(market_data.get('popular_subgenres', []))}

MARKET CHARACTERISTICS:
• Average Length: {market_data.get('average_length', 'Not specified')}
• Market Size: {market_data.get('market_size', 'Not specified')}

SUCCESS ELEMENTS:
{self._format_success_elements(success_elements)}

COMPETITIVE LANDSCAPE:
{self._analyze_competitive_landscape() if self.competitive_context else "Competitive analysis not requested"}

MARKET OPPORTUNITIES:
{self._identify_market_opportunities(market_data)}
"""

    def _analyze_audience(self, genre_data: Dict[str, Any]) -> str:
        """Analyze target audience characteristics and preferences"""
        
        if not genre_data:
            return f"❌ Genre '{self.genre}' not found in database."
        
        market_data = genre_data.get("market_data", {})
        expectations = genre_data.get("reader_expectations", {})
        
        audience_analysis = self._create_audience_profile(market_data, expectations)
        
        return f"""
👥 AUDIENCE ANALYSIS: {self.genre.upper()}
{'=' * 40}

PRIMARY AUDIENCE:
{self._format_primary_audience(audience_analysis)}

READER MOTIVATIONS:
{self._identify_reader_motivations(audience_analysis)}

CONTENT PREFERENCES:
{self._analyze_content_preferences(expectations)}

ACQUISITION PATTERNS:
{self._analyze_acquisition_patterns(audience_analysis)}

AUDIENCE TARGETING RECOMMENDATIONS:
{self._create_targeting_recommendations(audience_analysis)}
"""

    def _comprehensive_analysis(self, genre_data: Dict[str, Any]) -> str:
        """Perform comprehensive genre analysis"""
        
        if not genre_data:
            return f"❌ Genre '{self.genre}' not found in database."
        
        return f"""
🎭 COMPREHENSIVE GENRE ANALYSIS: {self.genre.upper()}
{'=' * 55}

{self._analyze_conventions(genre_data)}

{self._analyze_market(genre_data)}

{self._analyze_audience(genre_data)}

STRATEGIC RECOMMENDATIONS:
{self._create_strategic_recommendations(genre_data)}

RISK ASSESSMENT:
{self._assess_genre_risks(genre_data)}

NEXT STEPS:
{self._recommend_next_steps(genre_data)}
"""

    # Helper formatting methods
    def _format_expectations(self, expectations: Dict[str, Any]) -> str:
        """Format reader expectations for display"""
        if not expectations:
            return "• No specific expectations documented"
        
        return "\n".join([f"• {key.title()}: {value}" for key, value in expectations.items()])

    def _create_compliance_checklist(self, conventions: Dict[str, Any], expectations: Dict[str, Any]) -> str:
        """Create compliance checklist for the genre"""
        checklist_items = []
        
        # Add convention-based checklist items
        if "pacing" in conventions:
            checklist_items.append(f"□ Pacing aligns with {conventions['pacing'].lower()}")
        if "structure" in conventions:
            checklist_items.append(f"□ Story follows {conventions['structure'].lower()}")
        if "stakes" in conventions:
            checklist_items.append(f"□ Stakes are {conventions['stakes'].lower()}")
        
        # Add expectation-based checklist items
        for expectation in expectations.keys():
            checklist_items.append(f"□ Delivers on reader expectation: {expectation}")
        
        return "\n".join(checklist_items) if checklist_items else "□ Basic genre compliance"

    def _format_demographics(self, demographics: List[str]) -> str:
        """Format demographic information"""
        if not demographics:
            return "• Demographics not specified"
        return "\n".join([f"• {demo}" for demo in demographics])

    def _format_subgenres(self, subgenres: List[str]) -> str:
        """Format subgenre information"""
        if not subgenres:
            return "• No popular subgenres documented"
        return "\n".join([f"• {subgenre}" for subgenre in subgenres])

    def _format_success_elements(self, elements: List[str]) -> str:
        """Format success elements"""
        if not elements:
            return "• No success elements documented"
        return "\n".join([f"✓ {element}" for element in elements])

    # Analysis helper methods (simplified implementations)
    def _analyze_subgenre_variations(self) -> str:
        """Analyze subgenre-specific variations"""
        return f"Subgenre '{self.subgenre}' analysis pending detailed implementation"

    def _analyze_competitive_landscape(self) -> str:
        """Analyze competitive landscape"""
        return "Competitive landscape analysis pending market research integration"

    def _identify_market_opportunities(self, market_data: Dict[str, Any]) -> str:
        """Identify market opportunities"""
        return "Market opportunity analysis pending trend research"

    def _create_audience_profile(self, market_data: Dict[str, Any], expectations: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed audience profile"""
        return {
            "demographics": market_data.get("target_demographics", []),
            "expectations": expectations,
            "preferences": "preference analysis pending"
        }

    def _format_primary_audience(self, audience_analysis: Dict[str, Any]) -> str:
        """Format primary audience information"""
        demographics = audience_analysis.get("demographics", [])
        return "\n".join([f"• {demo}" for demo in demographics]) if demographics else "• Primary audience analysis pending"

    def _identify_reader_motivations(self, audience_analysis: Dict[str, Any]) -> str:
        """Identify what motivates readers in this genre"""
        motivations = {
            "thriller": ["Excitement and adrenaline", "Escapism", "Puzzle-solving"],
            "romance": ["Emotional fulfillment", "Fantasy/wish fulfillment", "Happy endings"],
            "mystery": ["Intellectual challenge", "Justice/resolution", "Puzzle-solving"],
            "fantasy": ["Escapism", "Wonder and magic", "Hero's journey"],
            "science_fiction": ["Ideas and concepts", "Future speculation", "Problem-solving"]
        }
        
        genre_motivations = motivations.get(self.genre.lower(), ["Genre-specific motivations pending analysis"])
        return "\n".join([f"• {motivation}" for motivation in genre_motivations])

    def _analyze_content_preferences(self, expectations: Dict[str, Any]) -> str:
        """Analyze content preferences"""
        return "Content preference analysis pending detailed reader research"

    def _analyze_acquisition_patterns(self, audience_analysis: Dict[str, Any]) -> str:
        """Analyze how audiences discover and acquire books"""
        return "Acquisition pattern analysis pending market research"

    def _create_targeting_recommendations(self, audience_analysis: Dict[str, Any]) -> str:
        """Create audience targeting recommendations"""
        return "Targeting recommendations pending marketing integration"

    def _create_strategic_recommendations(self, genre_data: Dict[str, Any]) -> str:
        """Create strategic recommendations based on genre analysis"""
        return "Strategic recommendations pending comprehensive market analysis"

    def _assess_genre_risks(self, genre_data: Dict[str, Any]) -> str:
        """Assess risks associated with the genre choice"""
        common_risks = {
            "thriller": ["Market saturation", "High reader expectations", "Action sequence execution"],
            "romance": ["Formula predictability", "Heat level appropriateness", "Character chemistry"],
            "mystery": ["Plot hole risks", "Red herring balance", "Fair play requirements"],
            "fantasy": ["World-building complexity", "Magic system consistency", "Length expectations"],
            "science_fiction": ["Scientific accuracy", "Idea accessibility", "Niche market appeal"]
        }
        
        genre_risks = common_risks.get(self.genre.lower(), ["General genre risks pending analysis"])
        return "\n".join([f"⚠️ {risk}" for risk in genre_risks])

    def _recommend_next_steps(self, genre_data: Dict[str, Any]) -> str:
        """Recommend next steps based on analysis"""
        return f"""
1. Validate story concept against {self.genre} conventions
2. Develop character archetypes appropriate for {self.genre} readers
3. Structure plot to meet reader expectations
4. Consider subgenre positioning for market differentiation
5. Plan marketing approach for target demographics
"""