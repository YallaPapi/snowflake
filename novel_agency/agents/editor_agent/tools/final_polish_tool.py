"""
Final Polish Tool - Manuscript Refinement and Enhancement

Provides final polish and refinement for publication-ready manuscripts.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class FinalPolishTool(BaseTool):
    """
    Tool for final manuscript polish and refinement before publication.
    """
    
    action: str = Field(..., description="Action to perform: 'polish_prose', 'enhance_transitions', 'refine_dialogue', 'optimize_pacing'")
    manuscript: str = Field(default="", description="Manuscript text for polishing")
    focus_areas: list = Field(default=[], description="Specific areas to focus polishing on")
    target_improvements: dict = Field(default={}, description="Specific improvement targets")
    polish_level: str = Field(default="comprehensive", description="Polish level: 'light', 'moderate', 'comprehensive'")
    
    def run(self) -> str:
        """Execute final polish tool action"""
        
        if self.action == "polish_prose":
            return self._polish_prose()
        elif self.action == "enhance_transitions":
            return self._enhance_transitions()
        elif self.action == "refine_dialogue":
            return self._refine_dialogue()
        elif self.action == "optimize_pacing":
            return self._optimize_pacing()
        else:
            return "Error: Invalid action. Use 'polish_prose', 'enhance_transitions', 'refine_dialogue', or 'optimize_pacing'"
    
    def _polish_prose(self) -> str:
        """Polish prose for publication quality"""
        if not self.manuscript:
            return "Error: Manuscript required for prose polishing"
        
        polish = f"✨ PROSE POLISHING RECOMMENDATIONS\n\n"
        
        # Analyze prose for polishing opportunities
        prose_improvements = []
        
        # Word choice improvements
        word_improvements = self._identify_word_improvements()
        prose_improvements.extend(word_improvements)
        
        # Sentence flow improvements
        flow_improvements = self._identify_flow_improvements()
        prose_improvements.extend(flow_improvements)
        
        # Clarity improvements
        clarity_improvements = self._identify_clarity_improvements()
        prose_improvements.extend(clarity_improvements)
        
        # Style consistency improvements
        style_improvements = self._identify_style_improvements()
        prose_improvements.extend(style_improvements)
        
        # Organize by priority
        high_priority = [imp for imp in prose_improvements if imp.get('priority') == 'high']
        medium_priority = [imp for imp in prose_improvements if imp.get('priority') == 'medium']
        low_priority = [imp for imp in prose_improvements if imp.get('priority') == 'low']
        
        polish += f"**Prose Polishing Analysis:**\n"
        polish += f"Total improvements identified: {len(prose_improvements)}\n"
        polish += f"Polish level: {self.polish_level}\n\n"
        
        if high_priority:
            polish += f"**🔴 High Priority (Impact: Significant):**\n"
            for i, improvement in enumerate(high_priority[:5], 1):
                polish += f"{i}. {improvement['description']}\n"
                if improvement.get('example'):
                    polish += f"   Example: {improvement['example']}\n"
            polish += "\n"
        
        if medium_priority and self.polish_level in ['moderate', 'comprehensive']:
            polish += f"**🟡 Medium Priority (Impact: Moderate):**\n"
            for i, improvement in enumerate(medium_priority[:3], 1):
                polish += f"{i}. {improvement['description']}\n"
            polish += "\n"
        
        if low_priority and self.polish_level == 'comprehensive':
            polish += f"**🟢 Low Priority (Impact: Minor):**\n"
            for i, improvement in enumerate(low_priority[:3], 1):
                polish += f"{i}. {improvement['description']}\n"
            polish += "\n"
        
        # Overall polish assessment
        total_issues = len(prose_improvements)
        if total_issues == 0:
            polish += f"✅ Prose quality is excellent - minimal polishing needed\n"
        elif total_issues <= 5:
            polish += f"✅ Prose quality is strong - minor polishing will enhance readability\n"
        elif total_issues <= 15:
            polish += f"⚡ Prose quality is good - moderate polishing will significantly improve impact\n"
        else:
            polish += f"🔧 Prose has potential - comprehensive polishing will transform readability\n"
        
        return polish
    
    def _enhance_transitions(self) -> str:
        """Enhance scene and chapter transitions"""
        if not self.manuscript:
            return "Error: Manuscript required for transition enhancement"
        
        transitions = f"🔗 TRANSITION ENHANCEMENT\n\n"
        
        # Analyze transition quality
        transition_improvements = []
        
        # Scene transitions
        scene_transitions = self._analyze_scene_transitions()
        transition_improvements.extend(scene_transitions)
        
        # Chapter transitions
        chapter_transitions = self._analyze_chapter_transitions()
        transition_improvements.extend(chapter_transitions)
        
        # Time transitions
        time_transitions = self._analyze_time_transitions()
        transition_improvements.extend(time_transitions)
        
        # Location transitions
        location_transitions = self._analyze_location_transitions()
        transition_improvements.extend(location_transitions)
        
        transitions += f"**Transition Analysis:**\n"
        transitions += f"Transition points analyzed: {len(transition_improvements)}\n\n"
        
        if transition_improvements:
            transitions += f"**Enhancement Recommendations:**\n"
            for i, improvement in enumerate(transition_improvements[:8], 1):
                transitions += f"{i}. {improvement['type'].title()}: {improvement['description']}\n"
                if improvement.get('suggestion'):
                    transitions += f"   Suggestion: {improvement['suggestion']}\n"
                transitions += "\n"
        else:
            transitions += f"✅ Transitions are smooth and well-crafted\n"
        
        return transitions
    
    def _refine_dialogue(self) -> str:
        """Refine dialogue for authenticity and impact"""
        if not self.manuscript:
            return "Error: Manuscript required for dialogue refinement"
        
        dialogue = f"💬 DIALOGUE REFINEMENT\n\n"
        
        # Extract dialogue for analysis
        dialogue_lines = [line.strip() for line in self.manuscript.split('\n') if '"' in line]
        
        dialogue += f"**Dialogue Analysis:**\n"
        dialogue += f"Dialogue lines found: {len(dialogue_lines)}\n\n"
        
        if not dialogue_lines:
            dialogue += f"⚠️ No dialogue detected in manuscript\n"
            dialogue += f"Consider adding character interactions through dialogue\n"
            return dialogue
        
        # Analyze dialogue quality
        dialogue_improvements = []
        
        # Voice consistency
        voice_issues = self._analyze_dialogue_voices()
        dialogue_improvements.extend(voice_issues)
        
        # Dialogue tags
        tag_issues = self._analyze_dialogue_tags()
        dialogue_improvements.extend(tag_issues)
        
        # Naturalness
        naturalness_issues = self._analyze_dialogue_naturalness()
        dialogue_improvements.extend(naturalness_issues)
        
        # Purpose and function
        function_issues = self._analyze_dialogue_function()
        dialogue_improvements.extend(function_issues)
        
        if dialogue_improvements:
            dialogue += f"**Refinement Recommendations:**\n"
            for i, improvement in enumerate(dialogue_improvements[:6], 1):
                dialogue += f"{i}. {improvement['category']}: {improvement['description']}\n"
                if improvement.get('example'):
                    dialogue += f"   Example: {improvement['example']}\n"
                dialogue += "\n"
        else:
            dialogue += f"✅ Dialogue is authentic and well-crafted\n"
        
        # Dialogue statistics
        total_words = len(self.manuscript.split())
        dialogue_words = sum(len(line.split()) for line in dialogue_lines)
        dialogue_percentage = (dialogue_words / total_words * 100) if total_words > 0 else 0
        
        dialogue += f"**Dialogue Statistics:**\n"
        dialogue += f"Dialogue ratio: {dialogue_percentage:.1f}% of manuscript\n"
        
        if dialogue_percentage < 10:
            dialogue += f"📈 Consider increasing dialogue for character development\n"
        elif dialogue_percentage > 60:
            dialogue += f"📉 Consider balancing dialogue with narrative description\n"
        else:
            dialogue += f"✅ Good dialogue-to-narrative balance\n"
        
        return dialogue
    
    def _optimize_pacing(self) -> str:
        """Optimize story pacing and rhythm"""
        if not self.manuscript:
            return "Error: Manuscript required for pacing optimization"
        
        pacing = f"⚡ PACING OPTIMIZATION\n\n"
        
        # Analyze pacing elements
        pacing_analysis = []
        
        # Sentence rhythm
        rhythm_analysis = self._analyze_sentence_rhythm()
        pacing_analysis.extend(rhythm_analysis)
        
        # Action/reflection balance
        balance_analysis = self._analyze_action_reflection_balance()
        pacing_analysis.extend(balance_analysis)
        
        # Tension progression
        tension_analysis = self._analyze_tension_progression()
        pacing_analysis.extend(tension_analysis)
        
        # Chapter pacing
        chapter_analysis = self._analyze_chapter_pacing()
        pacing_analysis.extend(chapter_analysis)
        
        pacing += f"**Pacing Analysis:**\n"
        pacing += f"Pacing elements analyzed: {len(pacing_analysis)}\n\n"
        
        if pacing_analysis:
            pacing += f"**Optimization Recommendations:**\n"
            for i, analysis in enumerate(pacing_analysis[:6], 1):
                pacing += f"{i}. {analysis['aspect']}: {analysis['recommendation']}\n"
                if analysis.get('impact'):
                    pacing += f"   Impact: {analysis['impact']}\n"
                pacing += "\n"
        else:
            pacing += f"✅ Pacing is well-optimized for reader engagement\n"
        
        # Overall pacing assessment
        word_count = len(self.manuscript.split())
        estimated_reading_time = word_count / 250  # Average reading speed
        
        pacing += f"**Pacing Overview:**\n"
        pacing += f"Estimated reading time: {estimated_reading_time:.1f} minutes\n"
        pacing += f"Word density: {word_count / 1000:.1f}k words\n"
        
        return pacing
    
    def _identify_word_improvements(self) -> list:
        """Identify word choice improvements"""
        improvements = []
        
        # Check for weak verbs
        weak_verbs = ['was', 'were', 'is', 'are', 'had', 'have', 'got', 'get']
        weak_verb_count = sum(self.manuscript.lower().count(f' {verb} ') for verb in weak_verbs)
        
        if weak_verb_count > len(self.manuscript.split()) * 0.05:
            improvements.append({
                'priority': 'medium',
                'description': 'Replace weak verbs with stronger, more specific action verbs',
                'example': 'Change "was running" to "sprinted" or "raced"'
            })
        
        # Check for redundant adverbs
        adverb_count = sum(1 for word in self.manuscript.split() if word.endswith('ly'))
        if adverb_count > len(self.manuscript.split()) * 0.02:
            improvements.append({
                'priority': 'medium',
                'description': 'Reduce adverb usage by choosing stronger verbs',
                'example': 'Change "ran quickly" to "sprinted"'
            })
        
        # Check for overused words
        words = self.manuscript.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        overused = [word for word, freq in word_freq.items() if freq > len(words) * 0.003]
        if overused:
            improvements.append({
                'priority': 'low',
                'description': f'Vary frequently used words: {", ".join(overused[:3])}',
                'example': 'Use synonyms or rephrase to avoid repetition'
            })
        
        return improvements
    
    def _identify_flow_improvements(self) -> list:
        """Identify sentence flow improvements"""
        improvements = []
        
        sentences = [s.strip() for s in self.manuscript.split('.') if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        if sentence_lengths:
            # Check for monotonous sentence length
            length_variance = max(sentence_lengths) - min(sentence_lengths)
            if length_variance < 8:
                improvements.append({
                    'priority': 'medium',
                    'description': 'Vary sentence lengths for better rhythm and flow',
                    'example': 'Mix short, punchy sentences with longer, complex ones'
                })
            
            # Check for overly long sentences
            long_sentences = [length for length in sentence_lengths if length > 30]
            if long_sentences:
                improvements.append({
                    'priority': 'high',
                    'description': f'Break up {len(long_sentences)} overly long sentences',
                    'example': 'Split complex sentences into clearer, shorter ones'
                })
        
        return improvements
    
    def _identify_clarity_improvements(self) -> list:
        """Identify clarity improvements"""
        improvements = []
        
        # Check for passive voice
        passive_indicators = [' was ', ' were ', ' been ', ' being ']
        passive_count = sum(self.manuscript.lower().count(indicator) for indicator in passive_indicators)
        
        if passive_count > len(self.manuscript.split()) * 0.03:
            improvements.append({
                'priority': 'high',
                'description': 'Convert passive voice to active voice for clarity',
                'example': 'Change "The door was opened by John" to "John opened the door"'
            })
        
        # Check for unclear pronouns
        pronouns = [' it ', ' this ', ' that ', ' they ']
        pronoun_density = sum(self.manuscript.lower().count(pronoun) for pronoun in pronouns)
        
        if pronoun_density > len(self.manuscript.split()) * 0.04:
            improvements.append({
                'priority': 'medium',
                'description': 'Clarify pronoun references for better understanding',
                'example': 'Replace unclear "it" with specific noun'
            })
        
        return improvements
    
    def _identify_style_improvements(self) -> list:
        """Identify style consistency improvements"""
        improvements = []
        
        # Check for consistent tense
        past_tense_words = [' was ', ' were ', ' had ', ' did ']
        present_tense_words = [' is ', ' are ', ' has ', ' does ']
        
        past_count = sum(self.manuscript.lower().count(word) for word in past_tense_words)
        present_count = sum(self.manuscript.lower().count(word) for word in present_tense_words)
        
        if past_count > 0 and present_count > 0 and abs(past_count - present_count) < min(past_count, present_count):
            improvements.append({
                'priority': 'high',
                'description': 'Maintain consistent narrative tense throughout',
                'example': 'Choose either past or present tense and use consistently'
            })
        
        return improvements
    
    def _analyze_scene_transitions(self) -> list:
        """Analyze scene transitions"""
        transitions = []
        
        # Look for abrupt scene changes
        paragraphs = [p.strip() for p in self.manuscript.split('\n\n') if p.strip()]
        
        for i in range(len(paragraphs) - 1):
            current = paragraphs[i]
            next_para = paragraphs[i + 1]
            
            # Simple heuristic for scene changes
            if (len(current.split()) < 20 and len(next_para.split()) > 50) or \
               ('***' in current or '---' in current):
                transitions.append({
                    'type': 'scene',
                    'description': f'Scene transition at paragraph {i+1}',
                    'suggestion': 'Ensure smooth transition with bridging elements'
                })
        
        return transitions[:5]  # Limit results
    
    def _analyze_chapter_transitions(self) -> list:
        """Analyze chapter transitions"""
        transitions = []
        
        # Look for chapter markers
        chapter_markers = ['chapter', 'part', 'section']
        lines = self.manuscript.split('\n')
        
        chapter_positions = []
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in chapter_markers):
                chapter_positions.append(i)
        
        for pos in chapter_positions:
            transitions.append({
                'type': 'chapter',
                'description': f'Chapter transition at line {pos}',
                'suggestion': 'Ensure chapter ends with compelling hook'
            })
        
        return transitions[:3]  # Limit results
    
    def _analyze_time_transitions(self) -> list:
        """Analyze time transitions"""
        transitions = []
        
        # Look for time indicators
        time_words = ['later', 'earlier', 'yesterday', 'tomorrow', 'meanwhile', 'suddenly']
        
        for word in time_words:
            if word in self.manuscript.lower():
                transitions.append({
                    'type': 'time',
                    'description': f'Time transition using "{word}"',
                    'suggestion': 'Ensure clear temporal relationship'
                })
        
        return transitions[:4]  # Limit results
    
    def _analyze_location_transitions(self) -> list:
        """Analyze location transitions"""
        transitions = []
        
        # Look for location change indicators
        location_words = ['arrived', 'entered', 'left', 'traveled', 'went to']
        
        for word in location_words:
            if word in self.manuscript.lower():
                transitions.append({
                    'type': 'location',
                    'description': f'Location transition using "{word}"',
                    'suggestion': 'Provide sufficient spatial orientation'
                })
        
        return transitions[:3]  # Limit results
    
    def _analyze_dialogue_voices(self) -> list:
        """Analyze dialogue voice consistency"""
        issues = []
        
        dialogue_lines = [line for line in self.manuscript.split('\n') if '"' in line]
        
        if len(set(dialogue_lines)) < len(dialogue_lines) * 0.8:
            issues.append({
                'category': 'Voice Consistency',
                'description': 'Ensure each character has distinct speech patterns',
                'example': 'Vary vocabulary, sentence structure, and tone by character'
            })
        
        return issues
    
    def _analyze_dialogue_tags(self) -> list:
        """Analyze dialogue tag usage"""
        issues = []
        
        dialogue_lines = [line for line in self.manuscript.split('\n') if '"' in line]
        said_count = sum(1 for line in dialogue_lines if 'said' in line.lower())
        
        if said_count > len(dialogue_lines) * 0.8:
            issues.append({
                'category': 'Dialogue Tags',
                'description': 'Vary dialogue tags beyond "said"',
                'example': 'Use action beats or varied tags like "whispered," "declared"'
            })
        
        return issues
    
    def _analyze_dialogue_naturalness(self) -> list:
        """Analyze dialogue naturalness"""
        issues = []
        
        dialogue_lines = [line for line in self.manuscript.split('\n') if '"' in line]
        
        # Check for overly formal dialogue
        formal_count = sum(1 for line in dialogue_lines if any(word in line.lower() for word in ['shall', 'would', 'should', 'might']))
        
        if formal_count > len(dialogue_lines) * 0.3:
            issues.append({
                'category': 'Naturalness',
                'description': 'Ensure dialogue sounds natural and conversational',
                'example': 'Use contractions and informal speech patterns'
            })
        
        return issues
    
    def _analyze_dialogue_function(self) -> list:
        """Analyze dialogue function and purpose"""
        issues = []
        
        dialogue_lines = [line for line in self.manuscript.split('\n') if '"' in line]
        
        if len(dialogue_lines) < len(self.manuscript.split('\n')) * 0.1:
            issues.append({
                'category': 'Function',
                'description': 'Increase dialogue to reveal character and advance plot',
                'example': 'Use dialogue to show character relationships and conflicts'
            })
        
        return issues
    
    def _analyze_sentence_rhythm(self) -> list:
        """Analyze sentence rhythm"""
        analysis = []
        
        sentences = [s.strip() for s in self.manuscript.split('.') if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if avg_length > 20:
                analysis.append({
                    'aspect': 'Sentence Rhythm',
                    'recommendation': 'Add shorter sentences for better rhythm',
                    'impact': 'Improves readability and pacing'
                })
            elif avg_length < 10:
                analysis.append({
                    'aspect': 'Sentence Rhythm',
                    'recommendation': 'Add some longer sentences for variety',
                    'impact': 'Creates more sophisticated flow'
                })
        
        return analysis
    
    def _analyze_action_reflection_balance(self) -> list:
        """Analyze action/reflection balance"""
        analysis = []
        
        action_words = ['ran', 'jumped', 'grabbed', 'shouted', 'fought', 'raced']
        reflection_words = ['thought', 'considered', 'wondered', 'remembered', 'realized']
        
        action_count = sum(self.manuscript.lower().count(word) for word in action_words)
        reflection_count = sum(self.manuscript.lower().count(word) for word in reflection_words)
        
        if action_count == 0:
            analysis.append({
                'aspect': 'Action/Reflection Balance',
                'recommendation': 'Add more dynamic action sequences',
                'impact': 'Increases story momentum and engagement'
            })
        elif reflection_count == 0:
            analysis.append({
                'aspect': 'Action/Reflection Balance',
                'recommendation': 'Add character introspection and reflection',
                'impact': 'Deepens character development and emotional connection'
            })
        
        return analysis
    
    def _analyze_tension_progression(self) -> list:
        """Analyze tension progression"""
        analysis = []
        
        tension_words = ['danger', 'threat', 'fear', 'worry', 'anxiety', 'suspense']
        tension_count = sum(self.manuscript.lower().count(word) for word in tension_words)
        
        if tension_count < len(self.manuscript.split()) * 0.001:
            analysis.append({
                'aspect': 'Tension Progression',
                'recommendation': 'Increase tension and conflict throughout story',
                'impact': 'Maintains reader engagement and page-turning quality'
            })
        
        return analysis
    
    def _analyze_chapter_pacing(self) -> list:
        """Analyze chapter-level pacing"""
        analysis = []
        
        # Look for chapter indicators
        chapter_count = self.manuscript.lower().count('chapter')
        word_count = len(self.manuscript.split())
        
        if chapter_count > 0:
            avg_chapter_length = word_count / chapter_count
            
            if avg_chapter_length > 5000:
                analysis.append({
                    'aspect': 'Chapter Pacing',
                    'recommendation': 'Consider shorter chapters for better pacing',
                    'impact': 'Creates more frequent satisfaction points for readers'
                })
            elif avg_chapter_length < 2000:
                analysis.append({
                    'aspect': 'Chapter Pacing',
                    'recommendation': 'Consider longer chapters for better development',
                    'impact': 'Allows for deeper scene and character development'
                })
        
        return analysis