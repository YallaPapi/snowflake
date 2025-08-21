"""
Scene Brief Tool - Step 9 of Snowflake Method

Creates detailed scene briefs with Goal/Conflict/Setback or Reaction/Dilemma/Decision.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class SceneBriefTool(BaseTool):
    """
    Tool for creating detailed scene briefs (Step 9).
    Integrates with existing Snowflake Step 9 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_briefs', 'validate_briefs', 'develop_scene', 'analyze_structure'")
    scene_list: list = Field(default=[], description="Step 8 scene list to develop briefs from")
    character_data: dict = Field(default={}, description="Character information for scene development")
    scene_index: int = Field(default=0, description="Specific scene index for individual development")
    draft_briefs: list = Field(default=[], description="Draft scene briefs for validation")
    
    def run(self) -> str:
        """Execute scene brief tool action"""
        
        if self.action == "create_briefs":
            return self._create_briefs()
        elif self.action == "validate_briefs":
            return self._validate_briefs()
        elif self.action == "develop_scene":
            return self._develop_scene()
        elif self.action == "analyze_structure":
            return self._analyze_structure()
        else:
            return "Error: Invalid action. Use 'create_briefs', 'validate_briefs', 'develop_scene', or 'analyze_structure'"
    
    def _create_briefs(self) -> str:
        """Create scene briefs from scene list"""
        try:
            # Import existing Step 9 functionality
            from src.pipeline.executors.step_9_executor import Step9SceneBriefs
            from src.pipeline.validators.step_9_validator import Step9Validator
            
            if not self.scene_list:
                return "Error: Scene list required for brief creation"
            
            # Use existing Step 9 executor
            executor = Step9SceneBriefs()
            validator = Step9Validator()
            
            # Generate scene briefs
            result = executor.execute(
                step_8_data={'scenes': self.scene_list},
                step_7_data=self.character_data,
                project_id='agent_generated'
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    briefs = result['artifact']['scene_briefs']
                    brief_summary = self._summarize_briefs(briefs)
                    return f"✅ Scene briefs created successfully:\n\n{brief_summary}\n\nValidation: All triadic structures verified"
                else:
                    return f"⚠️ Briefs created but validation failed:\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Brief creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_briefs_fallback()
        except Exception as e:
            return f"❌ Error creating briefs: {str(e)}"
    
    def _validate_briefs(self) -> str:
        """Validate existing scene briefs"""
        if not self.draft_briefs:
            return "Error: Draft briefs required for validation"
        
        try:
            from src.pipeline.validators.step_9_validator import Step9Validator
            
            validator = Step9Validator()
            artifact = {'scene_briefs': self.draft_briefs}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Scene briefs validation passed:\n\n{len(self.draft_briefs)} briefs validated\nAll triadic structures verified"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Brief validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_briefs_fallback()
        except Exception as e:
            return f"❌ Error validating briefs: {str(e)}"
    
    def _develop_scene(self) -> str:
        """Develop a specific scene brief"""
        if not self.scene_list or self.scene_index >= len(self.scene_list):
            return f"Error: Invalid scene index {self.scene_index} for scene list of {len(self.scene_list)} scenes"
        
        scene = self.scene_list[self.scene_index]
        scene_type = scene.get('type', 'proactive')
        
        if scene_type == 'proactive':
            brief = self._create_proactive_brief(scene)
        elif scene_type == 'reactive':
            brief = self._create_reactive_brief(scene)
        else:
            return f"Error: Unknown scene type '{scene_type}' for scene {self.scene_index + 1}"
        
        return f"✅ Scene brief developed for Scene {self.scene_index + 1}:\n\n{self._format_brief(brief, scene_type)}"
    
    def _analyze_structure(self) -> str:
        """Analyze structural integrity of scene briefs"""
        if not self.draft_briefs:
            return "Error: Scene briefs required for structural analysis"
        
        analysis = f"🔍 SCENE BRIEF STRUCTURAL ANALYSIS\n\n"
        analysis += f"Total briefs: {len(self.draft_briefs)}\n\n"
        
        # Analyze brief completeness
        complete_briefs = 0
        proactive_count = 0
        reactive_count = 0
        issues = []
        
        for i, brief in enumerate(self.draft_briefs):
            scene_num = i + 1
            
            if isinstance(brief, dict):
                # Determine scene type based on fields present
                has_goal = 'goal' in brief and brief['goal']
                has_reaction = 'reaction' in brief and brief['reaction']
                
                if has_goal:
                    proactive_count += 1
                    # Check proactive triad
                    if all(field in brief and brief[field] for field in ['goal', 'conflict', 'setback']):
                        complete_briefs += 1
                    else:
                        issues.append(f"Scene {scene_num} incomplete proactive triad")
                
                elif has_reaction:
                    reactive_count += 1
                    # Check reactive triad
                    if all(field in brief and brief[field] for field in ['reaction', 'dilemma', 'decision']):
                        complete_briefs += 1
                    else:
                        issues.append(f"Scene {scene_num} incomplete reactive triad")
                
                else:
                    issues.append(f"Scene {scene_num} unclear type (neither proactive nor reactive)")
            
            else:
                issues.append(f"Scene {scene_num} is not properly structured")
        
        analysis += f"**Brief Types:**\n"
        analysis += f"Proactive: {proactive_count}\n"
        analysis += f"Reactive: {reactive_count}\n"
        analysis += f"Complete: {complete_briefs}/{len(self.draft_briefs)}\n\n"
        
        # Check for alternating pattern
        pattern_issues = self._check_alternating_pattern()
        if pattern_issues:
            issues.extend(pattern_issues)
        
        if issues:
            analysis += f"⚠️ Structural issues found:\n" + "\n".join(f"- {issue}" for issue in issues)
        else:
            analysis += f"✅ All briefs structurally sound"
        
        return analysis
    
    def _create_briefs_fallback(self) -> str:
        """Fallback brief creation when Snowflake modules unavailable"""
        if not self.scene_list:
            return "Error: Scene list required for brief creation"
        
        briefs = []
        
        for i, scene in enumerate(self.scene_list):
            scene_type = scene.get('type', 'proactive')
            
            if scene_type == 'proactive':
                brief = self._create_proactive_brief(scene)
            elif scene_type == 'reactive':
                brief = self._create_reactive_brief(scene)
            else:
                # Default to proactive if unclear
                brief = self._create_proactive_brief(scene)
            
            briefs.append(brief)
        
        brief_summary = self._summarize_briefs(briefs)
        
        return f"📝 Scene briefs created (fallback mode):\n\n{brief_summary}\n\n⚠️ Note: Using template structure. Recommend customizing with character-specific goals and conflicts."
    
    def _validate_briefs_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        issues = []
        
        if not isinstance(self.draft_briefs, list):
            issues.append("Briefs should be a list of brief objects")
            return f"⚠️ Validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
        
        for i, brief in enumerate(self.draft_briefs):
            scene_num = i + 1
            
            if not isinstance(brief, dict):
                issues.append(f"Brief {scene_num} should be a dictionary")
                continue
            
            # Determine expected structure
            has_goal = 'goal' in brief
            has_reaction = 'reaction' in brief
            
            if has_goal:
                # Check proactive structure
                required_fields = ['goal', 'conflict', 'setback']
                for field in required_fields:
                    if field not in brief or not brief[field]:
                        issues.append(f"Proactive brief {scene_num} missing {field}")
            
            elif has_reaction:
                # Check reactive structure  
                required_fields = ['reaction', 'dilemma', 'decision']
                for field in required_fields:
                    if field not in brief or not brief[field]:
                        issues.append(f"Reactive brief {scene_num} missing {field}")
            
            else:
                issues.append(f"Brief {scene_num} unclear structure (needs goal or reaction)")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{len(self.draft_briefs)} briefs validated\nAll required triadic structures present"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
    
    def _create_proactive_brief(self, scene: dict) -> dict:
        """Create proactive scene brief (Goal/Conflict/Setback)"""
        pov_char = scene.get('pov', 'protagonist')
        scene_summary = scene.get('summary', 'Scene action')
        scene_conflict = scene.get('conflict', 'General conflict')
        
        # Get character motivation if available
        char_info = self.character_data.get(pov_char, {})
        char_goal = char_info.get('goal', 'achieve their desire')
        
        brief = {
            'scene_index': scene.get('index', 0),
            'pov': pov_char,
            'type': 'proactive',
            'goal': f"{pov_char} wants to {char_goal} by {scene_summary.lower()}",
            'conflict': f"Opposition arises when {scene_conflict.lower()}, creating obstacles that prevent easy goal achievement",
            'setback': f"Despite their efforts, {pov_char} faces a setback that complicates the situation and raises stakes for future scenes",
            'stakes': f"Failure means {pov_char} will be further from their ultimate goal and face increased opposition",
            'links': {
                'disaster_anchor': self._determine_disaster_anchor(scene.get('index', 0)),
                'character_arc': f"Advances {pov_char}'s journey toward character growth"
            }
        }
        
        return brief
    
    def _create_reactive_brief(self, scene: dict) -> dict:
        """Create reactive scene brief (Reaction/Dilemma/Decision)"""
        pov_char = scene.get('pov', 'protagonist')
        scene_summary = scene.get('summary', 'Character processes events')
        
        brief = {
            'scene_index': scene.get('index', 0),
            'pov': pov_char,
            'type': 'reactive',
            'reaction': f"{pov_char} reacts to the previous setback with shock, anger, fear, or other strong emotion that shows the impact of events",
            'dilemma': f"{pov_char} faces a difficult choice about how to proceed, with no clearly good options available",
            'decision': f"After weighing options, {pov_char} decides on a course of action that will drive the next proactive scene",
            'stakes': f"The decision will determine {pov_char}'s next actions and influence the story's direction",
            'links': {
                'emotional_arc': f"Develops {pov_char}'s emotional journey and internal growth",
                'plot_advancement': "Sets up motivation for next proactive scene"
            }
        }
        
        return brief
    
    def _determine_disaster_anchor(self, scene_index: int) -> int:
        """Determine which disaster this scene connects to"""
        total_scenes = len(self.scene_list) if self.scene_list else 20
        
        if scene_index <= total_scenes * 0.33:
            return 1  # First disaster
        elif scene_index <= total_scenes * 0.67:
            return 2  # Second disaster  
        else:
            return 3  # Third disaster
    
    def _check_alternating_pattern(self) -> list:
        """Check for proper alternating scene pattern"""
        issues = []
        
        if not self.draft_briefs:
            return issues
        
        consecutive_count = 1
        prev_type = None
        
        for i, brief in enumerate(self.draft_briefs):
            # Determine brief type
            if isinstance(brief, dict):
                if 'goal' in brief:
                    current_type = 'proactive'
                elif 'reaction' in brief:
                    current_type = 'reactive'
                else:
                    current_type = 'unknown'
            else:
                current_type = 'unknown'
            
            if current_type == prev_type:
                consecutive_count += 1
                if consecutive_count >= 4:
                    issues.append(f"Too many consecutive {current_type} scenes around scene {i+1}")
            else:
                consecutive_count = 1
            
            prev_type = current_type
        
        return issues
    
    def _summarize_briefs(self, briefs: list) -> str:
        """Summarize scene briefs for display"""
        if not briefs:
            return "No scene briefs to summarize"
        
        summary = f"📋 SCENE BRIEFS SUMMARY\n\n"
        summary += f"Total briefs: {len(briefs)}\n\n"
        
        # Show first few briefs as examples
        summary += "**Sample Briefs:**\n"
        for i, brief in enumerate(briefs[:3]):
            if isinstance(brief, dict):
                scene_num = brief.get('scene_index', i + 1)
                scene_type = brief.get('type', 'unknown').upper()
                pov = brief.get('pov', 'unknown')
                
                summary += f"Scene {scene_num} [{scene_type}] - {pov} POV:\n"
                
                if brief.get('goal'):
                    summary += f"  Goal: {brief['goal'][:100]}...\n"
                elif brief.get('reaction'):
                    summary += f"  Reaction: {brief['reaction'][:100]}...\n"
                
                summary += "\n"
        
        if len(briefs) > 3:
            summary += f"... and {len(briefs) - 3} more scene briefs\n"
        
        return summary
    
    def _format_brief(self, brief: dict, scene_type: str) -> str:
        """Format single scene brief for display"""
        output = f"**SCENE {brief.get('scene_index', 'Unknown')} - {scene_type.upper()} ({brief.get('pov', 'Unknown')} POV)**\n\n"
        
        if scene_type == 'proactive':
            output += f"**Goal**: {brief.get('goal', 'Not defined')}\n\n"
            output += f"**Conflict**: {brief.get('conflict', 'Not defined')}\n\n"
            output += f"**Setback**: {brief.get('setback', 'Not defined')}\n\n"
        elif scene_type == 'reactive':
            output += f"**Reaction**: {brief.get('reaction', 'Not defined')}\n\n"
            output += f"**Dilemma**: {brief.get('dilemma', 'Not defined')}\n\n"
            output += f"**Decision**: {brief.get('decision', 'Not defined')}\n\n"
        
        output += f"**Stakes**: {brief.get('stakes', 'Not defined')}\n"
        
        return output