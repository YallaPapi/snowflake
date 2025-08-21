"""
Scene Sequence Tool - Scene Flow and Pacing Analysis

Analyzes and optimizes scene sequences for better narrative flow.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class SceneSequenceTool(BaseTool):
    """
    Tool for analyzing and optimizing scene sequences and pacing.
    """
    
    action: str = Field(..., description="Action to perform: 'analyze_flow', 'optimize_pacing', 'check_continuity', 'suggest_reorder'")
    scene_list: list = Field(default=[], description="Scene list for sequence analysis")
    scene_briefs: list = Field(default=[], description="Scene briefs for detailed flow analysis")
    target_acts: int = Field(default=3, description="Number of acts for pacing analysis")
    
    def run(self) -> str:
        """Execute scene sequence tool action"""
        
        if self.action == "analyze_flow":
            return self._analyze_flow()
        elif self.action == "optimize_pacing":
            return self._optimize_pacing()
        elif self.action == "check_continuity":
            return self._check_continuity()
        elif self.action == "suggest_reorder":
            return self._suggest_reorder()
        else:
            return "Error: Invalid action. Use 'analyze_flow', 'optimize_pacing', 'check_continuity', or 'suggest_reorder'"
    
    def _analyze_flow(self) -> str:
        """Analyze overall narrative flow of scene sequence"""
        if not self.scene_list:
            return "Error: Scene list required for flow analysis"
        
        total_scenes = len(self.scene_list)
        
        analysis = f"🌊 NARRATIVE FLOW ANALYSIS\n\n"
        analysis += f"Total scenes: {total_scenes}\n\n"
        
        # Analyze scene type distribution
        proactive_scenes = []
        reactive_scenes = []
        
        for i, scene in enumerate(self.scene_list):
            scene_type = scene.get('type', 'unknown')
            if scene_type == 'proactive':
                proactive_scenes.append(i + 1)
            elif scene_type == 'reactive':
                reactive_scenes.append(i + 1)
        
        analysis += f"**Scene Type Distribution:**\n"
        analysis += f"Proactive: {len(proactive_scenes)} ({len(proactive_scenes)/total_scenes*100:.1f}%)\n"
        analysis += f"Reactive: {len(reactive_scenes)} ({len(reactive_scenes)/total_scenes*100:.1f}%)\n\n"
        
        # Analyze POV distribution
        pov_counts = {}
        pov_sequence = []
        
        for scene in self.scene_list:
            pov = scene.get('pov', 'unknown')
            pov_counts[pov] = pov_counts.get(pov, 0) + 1
            pov_sequence.append(pov)
        
        analysis += f"**POV Distribution:**\n"
        for pov, count in pov_counts.items():
            analysis += f"{pov}: {count} scenes ({count/total_scenes*100:.1f}%)\n"
        
        # Check for POV balance issues
        max_pov_count = max(pov_counts.values()) if pov_counts else 0
        if max_pov_count > total_scenes * 0.8:
            analysis += f"\n⚠️ POV imbalance: One character dominates ({max_pov_count} scenes)\n"
        
        # Analyze alternating pattern
        pattern_quality = self._analyze_alternating_pattern()
        analysis += f"\n**Pattern Analysis:**\n{pattern_quality}\n"
        
        # Analyze conflict escalation
        conflict_analysis = self._analyze_conflict_escalation()
        analysis += f"**Conflict Progression:**\n{conflict_analysis}\n"
        
        return analysis
    
    def _optimize_pacing(self) -> str:
        """Optimize scene pacing for better story rhythm"""
        if not self.scene_list:
            return "Error: Scene list required for pacing optimization"
        
        total_scenes = len(self.scene_list)
        
        optimization = f"⚡ PACING OPTIMIZATION ANALYSIS\n\n"
        
        # Calculate act breaks
        if self.target_acts == 3:
            act1_end = int(total_scenes * 0.25)
            act2_end = int(total_scenes * 0.75)
            act_breaks = [act1_end, act2_end, total_scenes]
        else:
            # Distribute evenly for other act structures
            act_length = total_scenes // self.target_acts
            act_breaks = [act_length * i for i in range(1, self.target_acts + 1)]
            act_breaks[-1] = total_scenes
        
        optimization += f"**Act Structure ({self.target_acts} acts):**\n"
        for i, break_point in enumerate(act_breaks):
            start = act_breaks[i-1] if i > 0 else 1
            optimization += f"Act {i+1}: Scenes {start}-{break_point}\n"
        
        optimization += "\n"
        
        # Analyze pacing within each act
        suggestions = []
        
        for act_num in range(self.target_acts):
            act_start = act_breaks[act_num - 1] if act_num > 0 else 0
            act_end = act_breaks[act_num]
            act_scenes = self.scene_list[act_start:act_end]
            
            # Count scene types in this act
            act_proactive = sum(1 for s in act_scenes if s.get('type') == 'proactive')
            act_reactive = sum(1 for s in act_scenes if s.get('type') == 'reactive')
            
            optimization += f"**Act {act_num + 1} Pacing:**\n"
            optimization += f"Scenes: {len(act_scenes)}, Proactive: {act_proactive}, Reactive: {act_reactive}\n"
            
            # Act-specific recommendations
            if act_num == 0:  # Act 1
                if act_proactive < act_reactive:
                    suggestions.append(f"Act 1: Consider more proactive scenes to establish momentum")
            elif act_num == 1:  # Act 2
                if len(act_scenes) < total_scenes * 0.4:
                    suggestions.append(f"Act 2: Seems short - consider adding complication scenes")
            else:  # Final act
                if act_reactive > act_proactive:
                    suggestions.append(f"Act {act_num + 1}: Consider more proactive scenes for strong resolution")
            
            optimization += "\n"
        
        # Check for pacing dead zones
        consecutive_reactive = self._find_consecutive_reactive_scenes()
        if consecutive_reactive:
            suggestions.append(f"Break up consecutive reactive scenes at positions: {consecutive_reactive}")
        
        if suggestions:
            optimization += f"**Optimization Suggestions:**\n"
            for suggestion in suggestions:
                optimization += f"- {suggestion}\n"
        else:
            optimization += f"✅ Pacing appears well-optimized\n"
        
        return optimization
    
    def _check_continuity(self) -> str:
        """Check scene continuity and logical flow"""
        if not self.scene_list:
            return "Error: Scene list required for continuity check"
        
        continuity = f"🔗 SCENE CONTINUITY ANALYSIS\n\n"
        
        issues = []
        
        # Check time flow
        time_issues = []
        prev_time = None
        
        for i, scene in enumerate(self.scene_list):
            scene_time = scene.get('time', '')
            if prev_time and scene_time:
                # Simple check for obvious time inconsistencies
                if 'earlier' in scene_time.lower() and i > 0:
                    time_issues.append(f"Scene {i+1}: Time goes backward ({scene_time})")
            prev_time = scene_time
        
        if time_issues:
            issues.extend(time_issues)
        
        # Check location flow
        location_jumps = []
        prev_location = None
        
        for i, scene in enumerate(self.scene_list):
            location = scene.get('location', '')
            if prev_location and location and location != prev_location:
                # Check for jarring location changes
                if i > 0 and not any(word in scene.get('summary', '').lower() for word in ['travels', 'goes', 'moves', 'arrives']):
                    location_jumps.append(f"Scene {i+1}: Abrupt location change to {location}")
            prev_location = location
        
        if location_jumps:
            issues.extend(location_jumps)
        
        # Check hook continuity
        hook_issues = []
        for i in range(len(self.scene_list) - 1):
            current_scene = self.scene_list[i]
            next_scene = self.scene_list[i + 1]
            
            outbound_hook = current_scene.get('outbound_hook', '')
            inbound_hook = next_scene.get('inbound_hook', '')
            
            # Simple check for hook connection
            if outbound_hook and inbound_hook:
                if len(outbound_hook) < 10 or len(inbound_hook) < 10:
                    hook_issues.append(f"Scenes {i+1}-{i+2}: Weak hook connection")
        
        if hook_issues:
            issues.extend(hook_issues)
        
        # Check character arc continuity
        character_arcs = {}
        for i, scene in enumerate(self.scene_list):
            pov = scene.get('pov', 'unknown')
            if pov not in character_arcs:
                character_arcs[pov] = []
            character_arcs[pov].append(i + 1)
        
        arc_issues = []
        for character, scene_numbers in character_arcs.items():
            if len(scene_numbers) > 1:
                # Check for large gaps in character appearances
                gaps = []
                for i in range(len(scene_numbers) - 1):
                    gap = scene_numbers[i + 1] - scene_numbers[i]
                    if gap > 5:  # More than 5 scenes between appearances
                        gaps.append(gap)
                
                if gaps:
                    max_gap = max(gaps)
                    arc_issues.append(f"{character}: {max_gap} scene gap between appearances")
        
        if arc_issues:
            issues.extend(arc_issues)
        
        continuity += f"**Continuity Check Results:**\n"
        if issues:
            continuity += f"Issues found: {len(issues)}\n\n"
            for issue in issues:
                continuity += f"⚠️ {issue}\n"
        else:
            continuity += f"✅ No major continuity issues detected\n"
        
        continuity += f"\n**Character Arc Distribution:**\n"
        for character, scenes in character_arcs.items():
            continuity += f"{character}: {len(scenes)} scenes ({scenes[0]}-{scenes[-1]})\n"
        
        return continuity
    
    def _suggest_reorder(self) -> str:
        """Suggest scene reordering for better flow"""
        if not self.scene_list:
            return "Error: Scene list required for reordering suggestions"
        
        suggestions = f"🔄 SCENE REORDERING SUGGESTIONS\n\n"
        
        reorder_suggestions = []
        
        # Check for scenes that might work better in different positions
        for i, scene in enumerate(self.scene_list):
            scene_type = scene.get('type', 'unknown')
            scene_pov = scene.get('pov', 'unknown')
            
            # Look for reactive scenes at story beginning
            if i < 2 and scene_type == 'reactive':
                reorder_suggestions.append(f"Scene {i+1}: Consider moving reactive scene later or changing to proactive")
            
            # Look for proactive scenes that might create better hooks
            if scene_type == 'proactive':
                summary = scene.get('summary', '').lower()
                if any(word in summary for word in ['reveals', 'discovers', 'learns']):
                    # This might be a good cliffhanger scene
                    chapter_hint = scene.get('chapter_hint', 1)
                    if i < len(self.scene_list) - 1:
                        next_scene = self.scene_list[i + 1]
                        next_chapter = next_scene.get('chapter_hint', 1)
                        if chapter_hint != next_chapter:
                            reorder_suggestions.append(f"Scene {i+1}: Good chapter ending - consider if placement maximizes suspense")
        
        # Check for better POV distribution
        pov_suggestions = self._analyze_pov_distribution()
        if pov_suggestions:
            reorder_suggestions.extend(pov_suggestions)
        
        # Check for conflict pacing
        conflict_suggestions = self._analyze_conflict_pacing()
        if conflict_suggestions:
            reorder_suggestions.extend(conflict_suggestions)
        
        if reorder_suggestions:
            suggestions += f"**Reordering Suggestions:**\n"
            for suggestion in reorder_suggestions:
                suggestions += f"- {suggestion}\n"
        else:
            suggestions += f"✅ Current scene order appears optimal\n"
        
        return suggestions
    
    def _analyze_alternating_pattern(self) -> str:
        """Analyze the proactive/reactive alternating pattern"""
        if not self.scene_list:
            return "No scenes to analyze"
        
        pattern_breaks = 0
        consecutive_count = 1
        prev_type = None
        
        for i, scene in enumerate(self.scene_list):
            current_type = scene.get('type', 'unknown')
            
            if current_type == prev_type:
                consecutive_count += 1
                if consecutive_count >= 3:
                    pattern_breaks += 1
            else:
                consecutive_count = 1
            
            prev_type = current_type
        
        if pattern_breaks == 0:
            return "Good alternating pattern maintained"
        else:
            return f"{pattern_breaks} pattern breaks found - consider alternating proactive/reactive scenes"
    
    def _analyze_conflict_escalation(self) -> str:
        """Analyze conflict escalation through scenes"""
        if not self.scene_list:
            return "No scenes to analyze"
        
        # Simple heuristic for conflict intensity
        conflict_levels = []
        
        for scene in self.scene_list:
            conflict_desc = scene.get('conflict', '').lower()
            
            # Assign intensity levels based on keywords
            if any(word in conflict_desc for word in ['climax', 'final', 'decisive', 'ultimate']):
                intensity = 5
            elif any(word in conflict_desc for word in ['crisis', 'disaster', 'catastrophe']):
                intensity = 4
            elif any(word in conflict_desc for word in ['danger', 'threat', 'confrontation']):
                intensity = 3
            elif any(word in conflict_desc for word in ['tension', 'conflict', 'obstacle']):
                intensity = 2
            else:
                intensity = 1
            
            conflict_levels.append(intensity)
        
        if len(conflict_levels) > 5:
            # Check if generally escalating
            first_third = conflict_levels[:len(conflict_levels)//3]
            last_third = conflict_levels[-len(conflict_levels)//3:]
            
            avg_early = sum(first_third) / len(first_third) if first_third else 1
            avg_late = sum(last_third) / len(last_third) if last_third else 1
            
            if avg_late > avg_early:
                return f"Good escalation (early: {avg_early:.1f}, late: {avg_late:.1f})"
            else:
                return f"Consider stronger escalation (early: {avg_early:.1f}, late: {avg_late:.1f})"
        
        return "Conflict progression analysis inconclusive (too few scenes)"
    
    def _find_consecutive_reactive_scenes(self) -> list:
        """Find positions of consecutive reactive scenes"""
        consecutive_positions = []
        consecutive_count = 0
        
        for i, scene in enumerate(self.scene_list):
            if scene.get('type') == 'reactive':
                consecutive_count += 1
                if consecutive_count >= 3:
                    consecutive_positions.append(i + 1 - consecutive_count + 1)
            else:
                consecutive_count = 0
        
        return consecutive_positions
    
    def _analyze_pov_distribution(self) -> list:
        """Analyze POV distribution for reordering suggestions"""
        suggestions = []
        
        pov_positions = {}
        for i, scene in enumerate(self.scene_list):
            pov = scene.get('pov', 'unknown')
            if pov not in pov_positions:
                pov_positions[pov] = []
            pov_positions[pov].append(i + 1)
        
        # Check for uneven distribution
        for character, positions in pov_positions.items():
            if len(positions) > 2:
                gaps = []
                for i in range(len(positions) - 1):
                    gap = positions[i + 1] - positions[i]
                    gaps.append(gap)
                
                if gaps and max(gaps) > 6:
                    suggestions.append(f"Consider redistributing {character} POV scenes more evenly")
        
        return suggestions
    
    def _analyze_conflict_pacing(self) -> list:
        """Analyze conflict pacing for reordering suggestions"""
        suggestions = []
        
        # Look for low-conflict scenes clustered together
        low_conflict_runs = []
        current_run = 0
        
        for scene in self.scene_list:
            conflict_desc = scene.get('conflict', '').lower()
            
            # Simple check for low conflict
            is_low_conflict = not any(word in conflict_desc for word in 
                                    ['crisis', 'danger', 'threat', 'confrontation', 'disaster'])
            
            if is_low_conflict:
                current_run += 1
            else:
                if current_run >= 3:
                    low_conflict_runs.append(current_run)
                current_run = 0
        
        if low_conflict_runs:
            suggestions.append("Consider interspersing high-conflict scenes to maintain tension")
        
        return suggestions