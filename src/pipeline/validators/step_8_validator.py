"""
Step 8 Validator: Scene List
Validates the scene list with mandatory conflict according to Snowflake Method
"""

import re
from typing import Dict, Any, Tuple, List, Set

class Step8Validator:
    """
    Validator for Step 8: Scene List
    Enforces mandatory conflict in every scene
    """
    
    VERSION = "1.0.0"
    
    # Conflict markers for validation
    CONFLICT_MARKERS = {
        'opposition': r'\b(opposes?|blocks?|prevents?|stops?|fights?|resists?|against|versus)\b',
        'dilemma': r'\b(choose|choice|dilemma|torn|between|either|decision)\b',
        'stakes': r'\b(risk|lose|stakes|consequence|cost|price|sacrifice)\b',
        'tension': r'\b(tension|conflict|struggle|battle|confrontation|clash)\b'
    }
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 8 artifact
        
        Args:
            artifact: The Step 8 artifact to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        if 'scenes' not in artifact:
            errors.append("MISSING SCENES: No scenes array found")
            return False, errors
        
        scenes = artifact['scenes']
        
        # RULE 1: Minimum scene count
        scene_count = len(scenes)
        artifact['scene_count'] = scene_count
        
        if scene_count < 10:
            errors.append(f"TOO FEW SCENES: Need at least 10, found {scene_count}")
        
        # RULE 2: Validate each scene
        scenes_without_conflict = []
        pov_distribution = {}
        total_word_target = 0
        disaster_scenes = {'D1': None, 'D2': None, 'D3': None}
        
        for i, scene in enumerate(scenes):
            scene_errors = self.validate_scene(scene, i + 1)
            errors.extend(scene_errors)
            
            # Check for conflict
            if not self.has_conflict(scene):
                scenes_without_conflict.append(i + 1)
            
            # Track POV distribution
            pov = scene.get('pov', 'Unknown')
            pov_distribution[pov] = pov_distribution.get(pov, 0) + 1
            
            # Sum word targets
            total_word_target += scene.get('word_target', 0)
            
            # Track disaster anchors
            disaster = scene.get('disaster_anchor')
            if disaster in ['D1', 'D2', 'D3']:
                disaster_scenes[disaster] = i + 1
        
        artifact['pov_distribution'] = pov_distribution
        artifact['total_word_target'] = total_word_target
        
        # RULE 3: Mandatory conflict in every scene
        if scenes_without_conflict:
            errors.append(f"SCENES WITHOUT CONFLICT: {scenes_without_conflict}")
        
        artifact['conflict_validation'] = {
            'all_have_conflict': len(scenes_without_conflict) == 0,
            'scenes_without_conflict': scenes_without_conflict
        }
        
        # RULE 4: Disaster anchors must be present
        artifact['disaster_anchors'] = {
            'd1_scene': disaster_scenes['D1'],
            'd2_scene': disaster_scenes['D2'],
            'd3_scene': disaster_scenes['D3']
        }
        
        if not disaster_scenes['D1']:
            errors.append("MISSING D1 ANCHOR: No scene marked as Disaster 1")
        if not disaster_scenes['D2']:
            errors.append("MISSING D2 ANCHOR: No scene marked as Disaster 2")
        if not disaster_scenes['D3']:
            errors.append("MISSING D3 ANCHOR: No scene marked as Disaster 3")
        
        # RULE 5: Disaster placement validation
        if all(disaster_scenes.values()):
            d1, d2, d3 = disaster_scenes['D1'], disaster_scenes['D2'], disaster_scenes['D3']
            
            # D1 should be around 25% mark
            expected_d1 = scene_count * 0.25
            if abs(d1 - expected_d1) > scene_count * 0.2:
                errors.append(f"D1 PLACEMENT: Scene {d1} too far from 25% mark")

            # D2 should be around 50% mark
            expected_d2 = scene_count * 0.5
            if abs(d2 - expected_d2) > scene_count * 0.2:
                errors.append(f"D2 PLACEMENT: Scene {d2} too far from 50% mark")

            # D3 should be around 75% mark
            expected_d3 = scene_count * 0.75
            if abs(d3 - expected_d3) > scene_count * 0.2:
                errors.append(f"D3 PLACEMENT: Scene {d3} too far from 75% mark")
            
            # Must be in order
            if not (d1 < d2 < d3):
                errors.append("DISASTER ORDER: D1, D2, D3 must occur in sequence")
        
        # RULE 6: POV variety check (informational only)
        # Single POV is valid for many stories
        
        # RULE 7: Word target validation
        if total_word_target < 20000:
            errors.append(f"TOO SHORT: Total word target {total_word_target} below minimum 20,000")
        
        # RULE 8: No duplicate scenes
        duplicates = self.find_duplicate_scenes(scenes)
        if duplicates:
            errors.append(f"DUPLICATE SCENES: {duplicates}")
        
        return len(errors) == 0, errors
    
    def validate_scene(self, scene: Dict[str, Any], index: int) -> List[str]:
        """Validate individual scene"""
        errors = []
        scene_id = f"Scene {index}"
        
        # Required fields
        required = ['index', 'pov', 'type', 'summary', 'time', 'location', 
                   'word_target', 'inbound_hook', 'outbound_hook']
        
        for field in required:
            if field not in scene or not scene.get(field):
                errors.append(f"{scene_id} MISSING {field.upper()}")
        
        # Validate scene type
        if 'type' in scene:
            if scene['type'] not in ['Proactive', 'Reactive']:
                errors.append(f"{scene_id} INVALID TYPE: Must be Proactive or Reactive")
        
        # Validate summary length and content
        if 'summary' in scene:
            summary = scene['summary']
            if len(summary) < 50:
                errors.append(f"{scene_id} SUMMARY TOO SHORT: Must be 2-3 sentences")
            if len(summary) > 800:
                errors.append(f"{scene_id} SUMMARY TOO LONG: Keep to 2-4 sentences")
        
        # Validate word target
        if 'word_target' in scene:
            target = scene['word_target']
            if target < 600:
                errors.append(f"{scene_id} TARGET TOO LOW: Minimum 600 words")
            if target > 3000:
                errors.append(f"{scene_id} TARGET TOO HIGH: Maximum 3000 words")
        
        # Validate hooks
        if 'inbound_hook' in scene:
            if len(scene['inbound_hook']) < 10:
                errors.append(f"{scene_id} WEAK INBOUND HOOK: Must pull reader in")
        
        if 'outbound_hook' in scene:
            if len(scene['outbound_hook']) < 10:
                errors.append(f"{scene_id} WEAK OUTBOUND HOOK: Must pull reader forward")
        
        return errors
    
    def has_conflict(self, scene: Dict[str, Any]) -> bool:
        """Check if scene has conflict"""
        summary = scene.get('summary', '').lower()
        
        # Check for explicit conflict markers
        for marker_type, pattern in self.CONFLICT_MARKERS.items():
            if re.search(pattern, summary, re.I):
                return True
        
        # Check scene type specific requirements
        scene_type = scene.get('type', '')
        
        if scene_type == 'Proactive':
            # Must have opposition
            if re.search(r'\b(but|however|unfortunately|blocks?|prevents?)\b', summary, re.I):
                return True
        elif scene_type == 'Reactive':
            # Must have dilemma
            if re.search(r'\b(must choose|torn between|dilemma|decision)\b', summary, re.I):
                return True
        
        # Check for explicit conflict field
        if 'conflict' in scene and scene['conflict']:
            if 'description' in scene['conflict'] and len(scene['conflict']['description']) > 10:
                return True
        
        return False
    
    def find_duplicate_scenes(self, scenes: List[Dict[str, Any]]) -> List[str]:
        """Find duplicate scenes"""
        duplicates = []
        seen_summaries = set()
        
        for i, scene in enumerate(scenes):
            summary = scene.get('summary', '').lower().strip()
            
            # Check for exact duplicates
            if summary in seen_summaries:
                duplicates.append(f"Scene {i+1}")
            else:
                seen_summaries.add(summary)
        
        return duplicates
    
    def validate_scene_flow(self, scenes: List[Dict[str, Any]]) -> List[str]:
        """Validate causal flow between scenes"""
        errors = []
        
        for i in range(len(scenes) - 1):
            current = scenes[i]
            next_scene = scenes[i + 1]
            
            # Check if outbound hook connects to next inbound
            outbound = current.get('outbound_hook', '').lower()
            inbound = next_scene.get('inbound_hook', '').lower()
            
            # Check for Reactive following Proactive setback
            if current.get('type') == 'Proactive':
                # Next scene should often be Reactive
                if next_scene.get('type') != 'Reactive' and i % 3 == 0:
                    # Allow some flexibility but flag patterns
                    pass  # Could add warning
            
            # Check for Decision leading to next Goal
            if current.get('type') == 'Reactive':
                # Decision should seed next Proactive goal
                if next_scene.get('type') == 'Proactive':
                    # This is good pattern
                    pass
        
        return errors
    
    def calculate_pacing(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate pacing metrics"""
        short_scenes = sum(1 for s in scenes if s.get('word_target', 0) < 1000)
        medium_scenes = sum(1 for s in scenes if 1000 <= s.get('word_target', 0) < 2000)
        long_scenes = sum(1 for s in scenes if s.get('word_target', 0) >= 2000)
        
        return {
            'short': short_scenes,
            'medium': medium_scenes,
            'long': long_scenes,
            'variety': min(short_scenes, medium_scenes, long_scenes) > 0
        }
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "TOO FEW SCENES" in error:
                suggestions.append("Break long synopsis into more discrete scenes")
            elif "SCENES WITHOUT CONFLICT" in error:
                suggestions.append("Add opposition (Proactive) or dilemma (Reactive) to every scene")
            elif "MISSING" in error and "ANCHOR" in error:
                suggestions.append("Mark scenes where disasters occur with disaster_anchor field")
            elif "PLACEMENT" in error:
                suggestions.append("Adjust disaster placement to standard three-act structure")
            elif "DISASTER ORDER" in error:
                suggestions.append("Ensure D1 < D2 < D3 in scene sequence")
            elif "SINGLE POV" in error:
                suggestions.append("Consider scenes from other character perspectives")
            elif "TOO SHORT" in error:
                suggestions.append("Add scenes or increase word targets")
            elif "DUPLICATE SCENES" in error:
                suggestions.append("Merge duplicate scenes or differentiate them")
            elif "SUMMARY TOO SHORT" in error:
                suggestions.append("Expand summary to 2-3 sentences showing conflict")
            elif "WEAK" in error and "HOOK" in error:
                suggestions.append("Strengthen hooks with questions, reversals, or revelations")
            elif "INVALID TYPE" in error:
                suggestions.append("Mark as Proactive (pursuing goal) or Reactive (processing blow)")
            else:
                suggestions.append("Review Step 8 requirements in guide")
        
        return suggestions