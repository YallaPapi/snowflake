"""
Scene List Tool - Step 8 of Snowflake Method

Creates comprehensive scene list with POV, conflicts, and progression.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class SceneListTool(BaseTool):
    """
    Tool for creating comprehensive scene lists (Step 8).
    Integrates with existing Snowflake Step 8 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'create_scene_list', 'validate_scenes', 'analyze_pacing', 'refine_sequence'")
    story_structure: dict = Field(default={}, description="Long synopsis and story structure for scene breakdown")
    character_data: dict = Field(default={}, description="Character information for POV decisions")
    target_length: int = Field(default=80000, description="Target word count for pacing calculations")
    draft_scenes: list = Field(default=[], description="Draft scene list for validation/refinement")
    
    def run(self) -> str:
        """Execute scene list tool action"""
        
        if self.action == "create_scene_list":
            return self._create_scene_list()
        elif self.action == "validate_scenes":
            return self._validate_scenes()
        elif self.action == "analyze_pacing":
            return self._analyze_pacing()
        elif self.action == "refine_sequence":
            return self._refine_sequence()
        else:
            return "Error: Invalid action. Use 'create_scene_list', 'validate_scenes', 'analyze_pacing', or 'refine_sequence'"
    
    def _create_scene_list(self) -> str:
        """Create scene list from story structure"""
        try:
            # Import existing Step 8 functionality
            from src.pipeline.executors.step_8_executor import Step8SceneList
            from src.pipeline.validators.step_8_validator import Step8Validator
            
            if not self.story_structure:
                return "Error: Story structure required for scene list creation"
            
            # Use existing Step 8 executor
            executor = Step8SceneList()
            validator = Step8Validator()
            
            # Generate scene list
            result = executor.execute(
                step_6_data=self.story_structure,
                step_7_data=self.character_data,
                project_id=self.story_structure.get('project_id', 'agent_generated')
            )
            
            if result.get('success'):
                # Validate the result
                validation = validator.validate(result['artifact'])
                if validation.get('valid'):
                    scenes = result['artifact']['scenes']
                    scene_summary = self._summarize_scene_list(scenes)
                    return f"✅ Scene list created successfully:\n\n{scene_summary}\n\nValidation: All checks passed"
                else:
                    return f"⚠️ Scene list created but validation failed:\n\nIssues: {validation.get('errors', [])}"
            else:
                return f"❌ Scene list creation failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._create_scene_list_fallback()
        except Exception as e:
            return f"❌ Error creating scene list: {str(e)}"
    
    def _validate_scenes(self) -> str:
        """Validate existing scene list"""
        if not self.draft_scenes:
            return "Error: Draft scenes required for validation"
        
        try:
            from src.pipeline.validators.step_8_validator import Step8Validator
            
            validator = Step8Validator()
            artifact = {'scenes': self.draft_scenes}
            validation = validator.validate(artifact)
            
            if validation.get('valid'):
                return f"✅ Scene list validation passed:\n\n{len(self.draft_scenes)} scenes validated\nAll structure and conflict checks successful"
            else:
                issues = validation.get('errors', [])
                return f"⚠️ Scene validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
                
        except ImportError:
            return self._validate_scenes_fallback()
        except Exception as e:
            return f"❌ Error validating scenes: {str(e)}"
    
    def _analyze_pacing(self) -> str:
        """Analyze pacing and flow of scene sequence"""
        if not self.draft_scenes:
            return "Error: Scene list required for pacing analysis"
        
        # Analyze scene types and distribution
        proactive_count = 0
        reactive_count = 0
        pov_distribution = {}
        conflict_types = {}
        
        for i, scene in enumerate(self.draft_scenes):
            scene_type = scene.get('type', 'unknown')
            if scene_type == 'proactive':
                proactive_count += 1
            elif scene_type == 'reactive':
                reactive_count += 1
            
            # Track POV distribution
            pov = scene.get('pov', 'unknown')
            pov_distribution[pov] = pov_distribution.get(pov, 0) + 1
            
            # Track conflict types
            conflict = scene.get('conflict', 'unknown')
            conflict_types[conflict] = conflict_types.get(conflict, 0) + 1
        
        # Calculate pacing metrics
        total_scenes = len(self.draft_scenes)
        avg_words_per_scene = self.target_length // total_scenes if total_scenes > 0 else 0
        
        pacing_report = f"📊 SCENE PACING ANALYSIS\n\n"
        pacing_report += f"Total scenes: {total_scenes}\n"
        pacing_report += f"Target length: {self.target_length:,} words\n"
        pacing_report += f"Average per scene: ~{avg_words_per_scene:,} words\n\n"
        
        pacing_report += f"**Scene Types:**\n"
        pacing_report += f"Proactive: {proactive_count} ({proactive_count/total_scenes*100:.1f}%)\n"
        pacing_report += f"Reactive: {reactive_count} ({reactive_count/total_scenes*100:.1f}%)\n\n"
        
        pacing_report += f"**POV Distribution:**\n"
        for pov, count in pov_distribution.items():
            pacing_report += f"{pov}: {count} scenes ({count/total_scenes*100:.1f}%)\n"
        
        # Identify pacing issues
        issues = []
        if proactive_count == 0:
            issues.append("No proactive scenes - story may lack forward momentum")
        elif reactive_count == 0:
            issues.append("No reactive scenes - characters may not process events")
        elif abs(proactive_count - reactive_count) > total_scenes * 0.3:
            issues.append("Unbalanced proactive/reactive ratio - consider rebalancing")
        
        if len(pov_distribution) == 1:
            issues.append("Single POV throughout - consider multiple perspectives")
        elif max(pov_distribution.values()) > total_scenes * 0.8:
            issues.append("One POV dominates heavily - consider better distribution")
        
        if issues:
            pacing_report += f"\n⚠️ Pacing concerns:\n" + "\n".join(f"- {issue}" for issue in issues)
        else:
            pacing_report += f"\n✅ Pacing appears well-balanced"
        
        return pacing_report
    
    def _refine_sequence(self) -> str:
        """Refine scene sequence for better flow"""
        if not self.draft_scenes:
            return "Error: Scene list required for refinement"
        
        suggestions = []
        
        # Check for alternating pattern
        prev_type = None
        consecutive_same = 0
        
        for i, scene in enumerate(self.draft_scenes):
            scene_type = scene.get('type', 'unknown')
            
            if scene_type == prev_type:
                consecutive_same += 1
                if consecutive_same >= 3:
                    suggestions.append(f"Consider breaking up consecutive {scene_type} scenes around scene {i+1}")
            else:
                consecutive_same = 0
            
            prev_type = scene_type
        
        # Check opening and closing
        if self.draft_scenes:
            first_scene = self.draft_scenes[0]
            last_scene = self.draft_scenes[-1]
            
            if first_scene.get('type') != 'proactive':
                suggestions.append("Consider starting with a proactive scene to hook readers")
            
            if last_scene.get('type') != 'proactive':
                suggestions.append("Consider ending with a proactive scene for strong resolution")
        
        # Check for conflict escalation
        conflict_intensity = []
        for scene in self.draft_scenes:
            # Simple heuristic based on conflict description
            conflict_desc = scene.get('conflict', '').lower()
            intensity = 1
            if any(word in conflict_desc for word in ['crisis', 'disaster', 'death', 'betrayal']):
                intensity = 3
            elif any(word in conflict_desc for word in ['threat', 'danger', 'conflict', 'confrontation']):
                intensity = 2
            conflict_intensity.append(intensity)
        
        # Check if conflicts generally escalate
        if len(conflict_intensity) > 5:
            mid_point = len(conflict_intensity) // 2
            first_half_avg = sum(conflict_intensity[:mid_point]) / mid_point
            second_half_avg = sum(conflict_intensity[mid_point:]) / (len(conflict_intensity) - mid_point)
            
            if second_half_avg <= first_half_avg:
                suggestions.append("Consider escalating conflict intensity in the second half")
        
        if not suggestions:
            return f"✅ Scene sequence appears well-structured:\n\n{len(self.draft_scenes)} scenes with good flow and pacing\nNo major structural issues identified"
        
        return f"🔧 Scene sequence refinement suggestions:\n\nCurrent: {len(self.draft_scenes)} scenes\n\nSuggestions:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
    
    def _create_scene_list_fallback(self) -> str:
        """Fallback scene list creation when Snowflake modules unavailable"""
        if not self.story_structure:
            return "Error: Story structure required for scene list creation"
        
        long_synopsis = self.story_structure.get('long_synopsis', '')
        
        if not long_synopsis:
            return "Error: Long synopsis not found in story structure"
        
        # Create basic scene structure from synopsis
        estimated_scenes = max(12, self.target_length // 3000)  # ~3000 words per scene
        
        scenes = []
        
        # Template scene structure based on three-act structure
        act_breaks = [
            int(estimated_scenes * 0.25),  # End of Act I
            int(estimated_scenes * 0.75),  # End of Act II
            estimated_scenes  # End of Act III
        ]
        
        for i in range(estimated_scenes):
            scene_num = i + 1
            
            # Determine scene type (alternating with some variation)
            scene_type = 'proactive' if i % 2 == 0 else 'reactive'
            
            # Determine POV (distribute among main characters)
            pov_chars = list(self.character_data.keys()) if self.character_data else ['protagonist']
            pov = pov_chars[i % len(pov_chars)]
            
            # Create basic scene structure
            if scene_num <= act_breaks[0]:
                # Act I scenes
                chapter_hint = 1 + (i // 3)
                location = "Opening setting"
                conflict = "Establishing conflict and character introduction"
                if i == 0:
                    summary = "Opening scene - introduce protagonist and story world"
                elif i == act_breaks[0] - 1:
                    summary = "Inciting incident - launch main story conflict"
                else:
                    summary = f"Development scene - build character and world"
            
            elif scene_num <= act_breaks[1]:
                # Act II scenes
                chapter_hint = 1 + act_breaks[0] + ((i - act_breaks[0]) // 3)
                location = "Various story locations"
                conflict = "Escalating obstacles and complications"
                if i == int(estimated_scenes * 0.5):
                    summary = "Midpoint crisis - major plot twist or revelation"
                else:
                    summary = f"Rising action - complications and character growth"
            
            else:
                # Act III scenes
                chapter_hint = 1 + act_breaks[1] + ((i - act_breaks[1]) // 3)
                location = "Final confrontation settings"
                conflict = "Final obstacles and resolution"
                if i == estimated_scenes - 1:
                    summary = "Resolution - story conclusion and character transformation"
                elif i >= estimated_scenes - 3:
                    summary = "Climax - final confrontation and decisive action"
                else:
                    summary = "Final complications - last obstacles before climax"
            
            scene = {
                'index': scene_num,
                'chapter_hint': chapter_hint,
                'type': scene_type,
                'pov': pov,
                'summary': summary,
                'time': f"Story time for scene {scene_num}",
                'location': location,
                'word_target': self.target_length // estimated_scenes,
                'status': 'planned',
                'conflict': conflict,
                'inbound_hook': f"Previous scene leads to {summary.lower()}",
                'outbound_hook': f"Scene ends with tension leading to next development"
            }
            
            scenes.append(scene)
        
        scene_summary = self._summarize_scene_list(scenes)
        
        return f"📝 Scene list created (fallback mode):\n\n{scene_summary}\n\n⚠️ Note: Using structural template. Recommend customizing with story-specific conflicts and developments."
    
    def _validate_scenes_fallback(self) -> str:
        """Fallback validation when Snowflake modules unavailable"""
        issues = []
        
        if not isinstance(self.draft_scenes, list):
            issues.append("Scenes should be a list of scene objects")
            return f"⚠️ Validation failed:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
        
        required_fields = ['index', 'type', 'pov', 'summary', 'conflict']
        
        for i, scene in enumerate(self.draft_scenes):
            if not isinstance(scene, dict):
                issues.append(f"Scene {i+1} should be a dictionary")
                continue
            
            for field in required_fields:
                if field not in scene or not scene[field]:
                    issues.append(f"Scene {i+1} missing {field}")
            
            # Check scene type
            scene_type = scene.get('type', '')
            if scene_type not in ['proactive', 'reactive']:
                issues.append(f"Scene {i+1} invalid type: {scene_type} (should be 'proactive' or 'reactive')")
            
            # Check summary length
            summary = scene.get('summary', '')
            if len(summary.split()) < 5:
                issues.append(f"Scene {i+1} summary too short")
        
        if not issues:
            return f"✅ Basic validation passed:\n\n{len(self.draft_scenes)} scenes validated\nAll required fields present"
        else:
            return f"⚠️ Validation issues found:\n\nIssues:\n" + "\n".join(f"- {issue}" for issue in issues)
    
    def _summarize_scene_list(self, scenes: list) -> str:
        """Summarize scene list for display"""
        if not scenes:
            return "No scenes to summarize"
        
        summary = f"🎬 SCENE LIST SUMMARY\n\n"
        summary += f"Total scenes: {len(scenes)}\n"
        
        # Count scene types
        proactive = sum(1 for s in scenes if s.get('type') == 'proactive')
        reactive = sum(1 for s in scenes if s.get('type') == 'reactive')
        
        summary += f"Proactive scenes: {proactive}\n"
        summary += f"Reactive scenes: {reactive}\n\n"
        
        # Show first few scenes as examples
        summary += "**Sample Scenes:**\n"
        for i, scene in enumerate(scenes[:5]):
            summary += f"{scene.get('index', i+1)}. [{scene.get('type', 'unknown').upper()}] "
            summary += f"{scene.get('pov', 'unknown')} POV - {scene.get('summary', 'No summary')}\n"
        
        if len(scenes) > 5:
            summary += f"... and {len(scenes) - 5} more scenes\n"
        
        return summary