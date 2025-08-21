"""
Scene Writer Tool - Step 10 of Snowflake Method

Transforms scene briefs into compelling novel prose.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class SceneWriterTool(BaseTool):
    """
    Tool for writing individual scenes from scene briefs (Step 10).
    Integrates with existing Snowflake Step 10 functionality.
    """
    
    action: str = Field(..., description="Action to perform: 'write_scene', 'revise_scene', 'analyze_prose', 'check_consistency'")
    scene_brief: dict = Field(default={}, description="Scene brief to write from")
    character_voices: dict = Field(default={}, description="Character voice guidelines and speech patterns")
    story_context: dict = Field(default={}, description="Full story context for consistency")
    target_words: int = Field(default=3000, description="Target word count for the scene")
    draft_prose: str = Field(default="", description="Draft prose for revision or analysis")
    
    def run(self) -> str:
        """Execute scene writer tool action"""
        
        if self.action == "write_scene":
            return self._write_scene()
        elif self.action == "revise_scene":
            return self._revise_scene()
        elif self.action == "analyze_prose":
            return self._analyze_prose()
        elif self.action == "check_consistency":
            return self._check_consistency()
        else:
            return "Error: Invalid action. Use 'write_scene', 'revise_scene', 'analyze_prose', or 'check_consistency'"
    
    def _write_scene(self) -> str:
        """Write scene prose from scene brief"""
        try:
            # Import existing Step 10 functionality
            from src.pipeline.executors.step_10_executor import Step10FirstDraft
            from src.pipeline.validators.step_10_validator import Step10Validator
            
            if not self.scene_brief:
                return "Error: Scene brief required for prose writing"
            
            # Use existing Step 10 executor for individual scene
            executor = Step10FirstDraft()
            validator = Step10Validator()
            
            # Prepare scene data
            scene_data = {
                'scene_briefs': [self.scene_brief],
                'character_bibles': self.character_voices,
                'story_context': self.story_context
            }
            
            # Generate scene prose
            result = executor.execute(
                step_9_data=scene_data,
                step_7_data={'character_bibles': self.character_voices},
                project_id='agent_generated'
            )
            
            if result.get('success'):
                prose = result['artifact'].get('manuscript', '')
                word_count = len(prose.split())
                
                return f"✅ Scene written successfully:\n\n{prose[:500]}...\n\n[Full scene: {word_count} words]\nTarget: {self.target_words} words"
            else:
                return f"❌ Scene writing failed: {result.get('error', 'Unknown error')}"
                
        except ImportError:
            # Fallback if Snowflake modules not available
            return self._write_scene_fallback()
        except Exception as e:
            return f"❌ Error writing scene: {str(e)}"
    
    def _revise_scene(self) -> str:
        """Revise existing scene prose"""
        if not self.draft_prose:
            return "Error: Draft prose required for revision"
        
        # Analyze current prose for improvement opportunities
        word_count = len(self.draft_prose.split())
        
        revision_notes = []
        
        # Check length vs target
        if word_count < self.target_words * 0.7:
            revision_notes.append(f"Scene is short ({word_count} words) - consider adding sensory details, internal thoughts, or dialogue")
        elif word_count > self.target_words * 1.3:
            revision_notes.append(f"Scene is long ({word_count} words) - consider tightening description and dialogue")
        
        # Check dialogue ratio
        dialogue_count = self.draft_prose.count('"')
        if dialogue_count < 4:
            revision_notes.append("Consider adding dialogue to bring characters to life")
        elif dialogue_count > word_count * 0.3:
            revision_notes.append("Heavy dialogue - ensure balance with action and description")
        
        # Check scene structure based on brief type
        if self.scene_brief:
            scene_type = self.scene_brief.get('type', 'unknown')
            
            if scene_type == 'proactive':
                goal = self.scene_brief.get('goal', '')
                if goal and not any(word in self.draft_prose.lower() for word in goal.lower().split()[:3]):
                    revision_notes.append("Ensure character's goal is clear in the prose")
            
            elif scene_type == 'reactive':
                reaction = self.scene_brief.get('reaction', '')
                if reaction and not any(word in self.draft_prose.lower() for word in ['felt', 'thought', 'realized', 'emotion']):
                    revision_notes.append("Strengthen emotional reaction and internal processing")
        
        # Check POV consistency
        pov_char = self.scene_brief.get('pov', 'protagonist') if self.scene_brief else 'protagonist'
        if pov_char.lower() not in self.draft_prose.lower():
            revision_notes.append(f"Ensure {pov_char} perspective is clear throughout")
        
        revision_summary = f"🔧 SCENE REVISION ANALYSIS\n\n"
        revision_summary += f"Current length: {word_count} words (Target: {self.target_words})\n"
        revision_summary += f"Dialogue markers: {dialogue_count//2} exchanges\n\n"
        
        if revision_notes:
            revision_summary += f"**Revision Suggestions:**\n"
            for note in revision_notes:
                revision_summary += f"- {note}\n"
        else:
            revision_summary += f"✅ Scene appears well-structured for its brief\n"
        
        return revision_summary
    
    def _analyze_prose(self) -> str:
        """Analyze prose quality and craft elements"""
        if not self.draft_prose:
            return "Error: Draft prose required for analysis"
        
        analysis = f"📊 PROSE CRAFT ANALYSIS\n\n"
        
        # Basic metrics
        word_count = len(self.draft_prose.split())
        sentence_count = len([s for s in self.draft_prose.split('.') if s.strip()])
        paragraph_count = len([p for p in self.draft_prose.split('\n\n') if p.strip()])
        
        analysis += f"**Structure:**\n"
        analysis += f"Words: {word_count}\n"
        analysis += f"Sentences: {sentence_count}\n"
        analysis += f"Paragraphs: {paragraph_count}\n"
        analysis += f"Avg words/sentence: {word_count/sentence_count:.1f}\n\n"
        
        # Dialogue analysis
        dialogue_lines = [line.strip() for line in self.draft_prose.split('\n') if '"' in line]
        analysis += f"**Dialogue:**\n"
        analysis += f"Lines with dialogue: {len(dialogue_lines)}\n"
        
        # Character voice consistency
        if self.character_voices:
            voice_analysis = self._analyze_character_voices()
            analysis += f"**Voice Consistency:**\n{voice_analysis}\n"
        
        # Pacing analysis
        action_words = ['ran', 'jumped', 'grabbed', 'shouted', 'slammed', 'rushed']
        description_words = ['beautiful', 'dark', 'large', 'small', 'ancient', 'modern']
        emotion_words = ['felt', 'thought', 'realized', 'wondered', 'hoped', 'feared']
        
        action_count = sum(1 for word in action_words if word in self.draft_prose.lower())
        description_count = sum(1 for word in description_words if word in self.draft_prose.lower())
        emotion_count = sum(1 for word in emotion_words if word in self.draft_prose.lower())
        
        analysis += f"**Content Balance:**\n"
        analysis += f"Action elements: {action_count}\n"
        analysis += f"Description elements: {description_count}\n"
        analysis += f"Emotional elements: {emotion_count}\n\n"
        
        # Readability assessment
        readability_notes = []
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        if avg_sentence_length > 25:
            readability_notes.append("Consider shorter sentences for better flow")
        elif avg_sentence_length < 8:
            readability_notes.append("Consider varying sentence length for rhythm")
        
        if paragraph_count < 3:
            readability_notes.append("Consider breaking into more paragraphs for readability")
        
        if readability_notes:
            analysis += f"**Readability Suggestions:**\n"
            for note in readability_notes:
                analysis += f"- {note}\n"
        else:
            analysis += f"✅ Good readability and flow\n"
        
        return analysis
    
    def _check_consistency(self) -> str:
        """Check consistency with story context and character information"""
        if not self.draft_prose:
            return "Error: Draft prose required for consistency check"
        
        consistency = f"🎯 CONSISTENCY CHECK\n\n"
        
        issues = []
        
        # Check POV consistency
        if self.scene_brief:
            expected_pov = self.scene_brief.get('pov', 'unknown')
            
            # Simple check for POV shifts
            other_pov_indicators = ['he thought', 'she felt', 'they realized']
            pov_shifts = sum(1 for indicator in other_pov_indicators if indicator in self.draft_prose.lower())
            
            if pov_shifts > 0 and expected_pov != 'omniscient':
                issues.append(f"Possible POV shifts detected ({pov_shifts} instances)")
        
        # Check character voice consistency
        if self.character_voices:
            voice_issues = self._check_voice_consistency()
            issues.extend(voice_issues)
        
        # Check scene brief adherence
        if self.scene_brief:
            brief_issues = self._check_brief_adherence()
            issues.extend(brief_issues)
        
        # Check story context consistency
        if self.story_context:
            context_issues = self._check_story_context()
            issues.extend(context_issues)
        
        consistency += f"**Consistency Results:**\n"
        if issues:
            consistency += f"Issues found: {len(issues)}\n\n"
            for issue in issues:
                consistency += f"⚠️ {issue}\n"
        else:
            consistency += f"✅ No major consistency issues detected\n"
        
        return consistency
    
    def _write_scene_fallback(self) -> str:
        """Fallback scene writing when Snowflake modules unavailable"""
        if not self.scene_brief:
            return "Error: Scene brief required for prose writing"
        
        scene_type = self.scene_brief.get('type', 'proactive')
        pov_char = self.scene_brief.get('pov', 'protagonist')
        scene_index = self.scene_brief.get('scene_index', 1)
        
        # Create basic scene structure based on type
        if scene_type == 'proactive':
            goal = self.scene_brief.get('goal', 'Character pursues their objective')
            conflict = self.scene_brief.get('conflict', 'Opposition emerges')
            setback = self.scene_brief.get('setback', 'Plans go awry')
            
            prose_template = f"""[Scene {scene_index} - {pov_char} POV]

{pov_char} focused on the task ahead. {goal.replace(pov_char, 'They' if pov_char != 'I' else 'I')}

The plan seemed straightforward enough, but as {pov_char} began to act, complications arose. {conflict}

Despite their best efforts, things didn't go as expected. {setback} 

{pov_char} realized this was only the beginning of a much larger challenge.

[Word count: ~{len(prose_template.split())} words - Target: {self.target_words}]

⚠️ This is a basic template. Recommend expanding with:
- Detailed sensory description
- Character-specific dialogue and thoughts  
- Scene-specific action and setting details
- Emotional depth and internal conflict"""
        
        else:  # reactive scene
            reaction = self.scene_brief.get('reaction', 'Character processes what happened')
            dilemma = self.scene_brief.get('dilemma', 'Character faces difficult choice')
            decision = self.scene_brief.get('decision', 'Character chooses path forward')
            
            prose_template = f"""[Scene {scene_index} - {pov_char} POV]

The events still echoed in {pov_char}'s mind. {reaction}

As the initial shock faded, the real problem became clear. {dilemma}

{pov_char} weighed the options carefully. Each choice carried its own risks, its own potential consequences.

Finally, a decision crystallized. {decision}

Whatever came next, there was no turning back now.

[Word count: ~{len(prose_template.split())} words - Target: {self.target_words}]

⚠️ This is a basic template. Recommend expanding with:
- Rich emotional interiority
- Detailed thought processes
- Character-specific voice and reactions
- Environmental details that reflect mood"""
        
        return f"📝 Scene draft created (fallback mode):\n\n{prose_template}"
    
    def _analyze_character_voices(self) -> str:
        """Analyze character voice consistency"""
        if not self.character_voices or not self.draft_prose:
            return "No character voice data available for analysis"
        
        voice_notes = []
        
        # Check if characters appear in the prose
        for char_name, voice_info in self.character_voices.items():
            if char_name.lower() in self.draft_prose.lower():
                # Check for voice characteristics
                if isinstance(voice_info, dict):
                    voice_traits = voice_info.get('voice', {})
                    speech_patterns = voice_info.get('speech_patterns', '')
                    
                    if speech_patterns and speech_patterns not in self.draft_prose:
                        voice_notes.append(f"{char_name}: Consider incorporating established speech patterns")
        
        if not voice_notes:
            return "Character voices appear consistent"
        
        return "\n".join(f"- {note}" for note in voice_notes)
    
    def _check_voice_consistency(self) -> list:
        """Check for character voice consistency issues"""
        issues = []
        
        for char_name, voice_info in self.character_voices.items():
            if char_name.lower() in self.draft_prose.lower():
                # Basic voice consistency checks
                if isinstance(voice_info, dict):
                    personality = voice_info.get('personality', {})
                    if personality.get('formal') and 'gonna' in self.draft_prose.lower():
                        issues.append(f"{char_name}: Informal language conflicts with formal personality")
        
        return issues
    
    def _check_brief_adherence(self) -> list:
        """Check adherence to scene brief requirements"""
        issues = []
        
        scene_type = self.scene_brief.get('type', 'unknown')
        
        if scene_type == 'proactive':
            goal = self.scene_brief.get('goal', '')
            if goal and len(goal) > 20:
                # Check if goal elements appear in prose
                goal_words = goal.lower().split()[:5]  # First 5 words of goal
                if not any(word in self.draft_prose.lower() for word in goal_words):
                    issues.append("Scene goal not clearly reflected in prose")
        
        elif scene_type == 'reactive':
            reaction = self.scene_brief.get('reaction', '')
            if reaction and not any(word in self.draft_prose.lower() for word in ['felt', 'thought', 'emotion', 'realized']):
                issues.append("Emotional reaction not evident in prose")
        
        return issues
    
    def _check_story_context(self) -> list:
        """Check consistency with broader story context"""
        issues = []
        
        # Basic context consistency checks
        if isinstance(self.story_context, dict):
            setting = self.story_context.get('setting', '')
            if setting and setting.lower() not in self.draft_prose.lower():
                # This might be okay if scene is in different location
                pass
            
            genre = self.story_context.get('genre', '')
            if genre == 'fantasy' and 'magic' not in self.draft_prose.lower() and len(self.draft_prose) > 1000:
                # This is just a gentle suggestion, not necessarily an error
                pass
        
        return issues