"""
Prose Style Tool - Writing Style and Voice Management

Manages writing style, consistency, and voice throughout the manuscript.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class ProseStyleTool(BaseTool):
    """
    Tool for managing writing style, voice consistency, and prose quality.
    """
    
    action: str = Field(..., description="Action to perform: 'analyze_style', 'check_voice_consistency', 'suggest_improvements', 'adapt_genre_style'")
    prose_samples: list = Field(default=[], description="List of prose samples to analyze")
    target_genre: str = Field(default="", description="Target genre for style adaptation")
    target_audience: str = Field(default="adult", description="Target audience: 'adult', 'young_adult', 'middle_grade'")
    character_voices: dict = Field(default={}, description="Character voice guidelines")
    style_guidelines: dict = Field(default={}, description="Specific style preferences")
    
    def run(self) -> str:
        """Execute prose style tool action"""
        
        if self.action == "analyze_style":
            return self._analyze_style()
        elif self.action == "check_voice_consistency":
            return self._check_voice_consistency()
        elif self.action == "suggest_improvements":
            return self._suggest_improvements()
        elif self.action == "adapt_genre_style":
            return self._adapt_genre_style()
        else:
            return "Error: Invalid action. Use 'analyze_style', 'check_voice_consistency', 'suggest_improvements', or 'adapt_genre_style'"
    
    def _analyze_style(self) -> str:
        """Analyze prose style across samples"""
        if not self.prose_samples:
            return "Error: Prose samples required for style analysis"
        
        analysis = f"✍️ PROSE STYLE ANALYSIS\n\n"
        
        # Combine all samples for analysis
        combined_prose = ' '.join(self.prose_samples)
        
        # Basic style metrics
        word_count = len(combined_prose.split())
        sentence_count = len([s for s in combined_prose.split('.') if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        analysis += f"**Overall Metrics:**\n"
        analysis += f"Total words analyzed: {word_count:,}\n"
        analysis += f"Average sentence length: {avg_sentence_length:.1f} words\n\n"
        
        # Vocabulary analysis
        vocabulary_analysis = self._analyze_vocabulary(combined_prose)
        analysis += f"**Vocabulary Analysis:**\n{vocabulary_analysis}\n\n"
        
        # Sentence structure analysis
        sentence_analysis = self._analyze_sentence_structure(combined_prose)
        analysis += f"**Sentence Structure:**\n{sentence_analysis}\n\n"
        
        # Dialogue analysis
        dialogue_analysis = self._analyze_dialogue(combined_prose)
        analysis += f"**Dialogue Analysis:**\n{dialogue_analysis}\n\n"
        
        # Style consistency across samples
        if len(self.prose_samples) > 1:
            consistency_analysis = self._analyze_consistency()
            analysis += f"**Consistency Analysis:**\n{consistency_analysis}\n\n"
        
        # Genre appropriateness
        if self.target_genre:
            genre_analysis = self._analyze_genre_fit(combined_prose)
            analysis += f"**Genre Appropriateness ({self.target_genre}):**\n{genre_analysis}\n"
        
        return analysis
    
    def _check_voice_consistency(self) -> str:
        """Check character voice consistency across samples"""
        if not self.prose_samples:
            return "Error: Prose samples required for voice consistency check"
        
        consistency = f"🎭 VOICE CONSISTENCY CHECK\n\n"
        
        voice_issues = []
        
        # Check each character's voice consistency
        if self.character_voices:
            for char_name, voice_info in self.character_voices.items():
                char_issues = self._check_character_voice(char_name, voice_info)
                voice_issues.extend(char_issues)
        
        # Check narrative voice consistency
        narrative_issues = self._check_narrative_voice()
        voice_issues.extend(narrative_issues)
        
        consistency += f"**Voice Consistency Results:**\n"
        if voice_issues:
            consistency += f"Issues found: {len(voice_issues)}\n\n"
            for issue in voice_issues:
                consistency += f"⚠️ {issue}\n"
        else:
            consistency += f"✅ No major voice consistency issues detected\n"
        
        # Voice strength assessment
        voice_strength = self._assess_voice_strength()
        consistency += f"\n**Voice Strength Assessment:**\n{voice_strength}\n"
        
        return consistency
    
    def _suggest_improvements(self) -> str:
        """Suggest prose improvements based on analysis"""
        if not self.prose_samples:
            return "Error: Prose samples required for improvement suggestions"
        
        suggestions = f"🔧 PROSE IMPROVEMENT SUGGESTIONS\n\n"
        
        improvement_suggestions = []
        
        # Analyze current prose for improvement opportunities
        combined_prose = ' '.join(self.prose_samples)
        
        # Sentence variety suggestions
        sentence_suggestions = self._suggest_sentence_improvements(combined_prose)
        improvement_suggestions.extend(sentence_suggestions)
        
        # Vocabulary suggestions
        vocab_suggestions = self._suggest_vocabulary_improvements(combined_prose)
        improvement_suggestions.extend(vocab_suggestions)
        
        # Pacing suggestions
        pacing_suggestions = self._suggest_pacing_improvements(combined_prose)
        improvement_suggestions.extend(pacing_suggestions)
        
        # Show vs tell suggestions
        show_tell_suggestions = self._suggest_show_vs_tell_improvements(combined_prose)
        improvement_suggestions.extend(show_tell_suggestions)
        
        # Dialogue improvements
        dialogue_suggestions = self._suggest_dialogue_improvements(combined_prose)
        improvement_suggestions.extend(dialogue_suggestions)
        
        suggestions += f"**Improvement Recommendations:**\n"
        if improvement_suggestions:
            for i, suggestion in enumerate(improvement_suggestions, 1):
                suggestions += f"{i}. {suggestion}\n"
        else:
            suggestions += f"✅ Prose quality appears strong - no major improvements needed\n"
        
        return suggestions
    
    def _adapt_genre_style(self) -> str:
        """Provide genre-specific style adaptation advice"""
        if not self.target_genre:
            return "Error: Target genre required for style adaptation"
        
        adaptation = f"🎨 GENRE STYLE ADAPTATION\n\n"
        adaptation += f"Target Genre: {self.target_genre}\n"
        adaptation += f"Target Audience: {self.target_audience}\n\n"
        
        # Genre-specific style guidelines
        genre_guidelines = self._get_genre_guidelines(self.target_genre)
        adaptation += f"**Genre Style Guidelines:**\n{genre_guidelines}\n\n"
        
        # Analyze current prose against genre expectations
        if self.prose_samples:
            genre_analysis = self._analyze_genre_alignment()
            adaptation += f"**Current Alignment Analysis:**\n{genre_analysis}\n\n"
        
        # Specific adaptation recommendations
        adaptation_recommendations = self._get_adaptation_recommendations(self.target_genre)
        adaptation += f"**Adaptation Recommendations:**\n{adaptation_recommendations}\n"
        
        return adaptation
    
    def _analyze_vocabulary(self, prose: str) -> str:
        """Analyze vocabulary complexity and variety"""
        words = prose.lower().split()
        unique_words = set(words)
        
        vocabulary_ratio = len(unique_words) / len(words) if words else 0
        
        # Check for complex words (simple heuristic: longer than 7 characters)
        complex_words = [w for w in unique_words if len(w) > 7]
        complex_ratio = len(complex_words) / len(unique_words) if unique_words else 0
        
        analysis = f"Vocabulary diversity: {vocabulary_ratio:.2f}\n"
        analysis += f"Complex words ratio: {complex_ratio:.2f}\n"
        
        if vocabulary_ratio < 0.3:
            analysis += "⚠️ Consider varying vocabulary for richer prose\n"
        elif vocabulary_ratio > 0.7:
            analysis += "✅ Good vocabulary variety\n"
        
        if complex_ratio > 0.3:
            analysis += "⚠️ May be too complex for target audience\n"
        
        return analysis
    
    def _analyze_sentence_structure(self, prose: str) -> str:
        """Analyze sentence structure variety"""
        sentences = [s.strip() for s in prose.split('.') if s.strip()]
        
        if not sentences:
            return "No sentences to analyze"
        
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Check for variety
        short_sentences = sum(1 for length in sentence_lengths if length < 10)
        medium_sentences = sum(1 for length in sentence_lengths if 10 <= length <= 20)
        long_sentences = sum(1 for length in sentence_lengths if length > 20)
        
        analysis = f"Average sentence length: {avg_length:.1f} words\n"
        analysis += f"Short sentences: {short_sentences} ({short_sentences/len(sentences)*100:.1f}%)\n"
        analysis += f"Medium sentences: {medium_sentences} ({medium_sentences/len(sentences)*100:.1f}%)\n"
        analysis += f"Long sentences: {long_sentences} ({long_sentences/len(sentences)*100:.1f}%)\n"
        
        if avg_length < 8:
            analysis += "⚠️ Consider longer sentences for better flow\n"
        elif avg_length > 25:
            analysis += "⚠️ Consider shorter sentences for readability\n"
        else:
            analysis += "✅ Good sentence length balance\n"
        
        return analysis
    
    def _analyze_dialogue(self, prose: str) -> str:
        """Analyze dialogue usage and quality"""
        dialogue_lines = [line for line in prose.split('\n') if '"' in line]
        total_lines = len(prose.split('\n'))
        
        dialogue_ratio = len(dialogue_lines) / total_lines if total_lines > 0 else 0
        
        analysis = f"Dialogue ratio: {dialogue_ratio:.2f}\n"
        analysis += f"Dialogue lines: {len(dialogue_lines)}\n"
        
        if dialogue_ratio < 0.1:
            analysis += "⚠️ Consider adding more dialogue for character interaction\n"
        elif dialogue_ratio > 0.6:
            analysis += "⚠️ Very dialogue-heavy - ensure balance with narrative\n"
        else:
            analysis += "✅ Good dialogue balance\n"
        
        # Check for dialogue tags variety
        if dialogue_lines:
            said_count = sum(1 for line in dialogue_lines if 'said' in line.lower())
            tag_ratio = said_count / len(dialogue_lines) if dialogue_lines else 0
            
            if tag_ratio > 0.8:
                analysis += "⚠️ Consider varying dialogue tags\n"
        
        return analysis
    
    def _analyze_consistency(self) -> str:
        """Analyze style consistency across prose samples"""
        if len(self.prose_samples) < 2:
            return "Need multiple samples for consistency analysis"
        
        # Simple consistency checks
        sentence_lengths = []
        vocabulary_ratios = []
        
        for sample in self.prose_samples:
            words = sample.split()
            sentences = [s for s in sample.split('.') if s.strip()]
            
            if words and sentences:
                avg_sentence_length = len(words) / len(sentences)
                sentence_lengths.append(avg_sentence_length)
                
                unique_words = set(w.lower() for w in words)
                vocab_ratio = len(unique_words) / len(words) if words else 0
                vocabulary_ratios.append(vocab_ratio)
        
        consistency_report = ""
        
        if sentence_lengths:
            sentence_variance = max(sentence_lengths) - min(sentence_lengths)
            if sentence_variance > 10:
                consistency_report += f"⚠️ Sentence length varies significantly ({min(sentence_lengths):.1f} to {max(sentence_lengths):.1f})\n"
            else:
                consistency_report += f"✅ Consistent sentence length patterns\n"
        
        if vocabulary_ratios:
            vocab_variance = max(vocabulary_ratios) - min(vocabulary_ratios)
            if vocab_variance > 0.2:
                consistency_report += f"⚠️ Vocabulary density varies significantly\n"
            else:
                consistency_report += f"✅ Consistent vocabulary usage\n"
        
        return consistency_report
    
    def _analyze_genre_fit(self, prose: str) -> str:
        """Analyze how well prose fits target genre"""
        genre_fit = ""
        
        if self.target_genre.lower() == "fantasy":
            # Look for fantasy elements
            fantasy_words = ['magic', 'spell', 'wizard', 'dragon', 'kingdom', 'sword', 'enchant']
            fantasy_count = sum(1 for word in fantasy_words if word in prose.lower())
            genre_fit += f"Fantasy elements: {fantasy_count} instances\n"
            
            if fantasy_count == 0:
                genre_fit += "⚠️ Consider adding more fantasy elements\n"
        
        elif self.target_genre.lower() == "thriller":
            # Look for thriller elements
            thriller_words = ['danger', 'threat', 'suspense', 'chase', 'escape', 'fear', 'urgent']
            thriller_count = sum(1 for word in thriller_words if word in prose.lower())
            genre_fit += f"Thriller elements: {thriller_count} instances\n"
            
            if thriller_count == 0:
                genre_fit += "⚠️ Consider increasing tension and suspense\n"
        
        elif self.target_genre.lower() == "romance":
            # Look for romance elements
            romance_words = ['love', 'heart', 'kiss', 'passion', 'attraction', 'desire', 'emotion']
            romance_count = sum(1 for word in romance_words if word in prose.lower())
            genre_fit += f"Romance elements: {romance_count} instances\n"
            
            if romance_count == 0:
                genre_fit += "⚠️ Consider adding more emotional and romantic elements\n"
        
        return genre_fit
    
    def _check_character_voice(self, char_name: str, voice_info: dict) -> list:
        """Check consistency of a specific character's voice"""
        issues = []
        
        # This is a simplified check - in practice, would analyze character-specific dialogue
        combined_prose = ' '.join(self.prose_samples)
        
        if char_name.lower() in combined_prose.lower():
            # Check for voice characteristics if specified
            if isinstance(voice_info, dict):
                formal_level = voice_info.get('formal', False)
                if formal_level and 'gonna' in combined_prose.lower():
                    issues.append(f"{char_name}: Informal language conflicts with formal voice")
        
        return issues
    
    def _check_narrative_voice(self) -> list:
        """Check narrative voice consistency"""
        issues = []
        
        # Check for POV consistency across samples
        first_person_count = 0
        third_person_count = 0
        
        for sample in self.prose_samples:
            if ' I ' in sample or sample.startswith('I '):
                first_person_count += 1
            if ' he ' in sample or ' she ' in sample:
                third_person_count += 1
        
        if first_person_count > 0 and third_person_count > 0:
            issues.append("Mixed POV detected - ensure consistent narrative perspective")
        
        return issues
    
    def _assess_voice_strength(self) -> str:
        """Assess overall voice strength and distinctiveness"""
        combined_prose = ' '.join(self.prose_samples)
        
        # Simple voice strength indicators
        distinctive_elements = 0
        
        # Check for unique word choices
        unique_descriptors = ['crimson', 'azure', 'whispered', 'thundered', 'shimmered']
        distinctive_elements += sum(1 for word in unique_descriptors if word in combined_prose.lower())
        
        # Check for varied sentence beginnings
        sentences = [s.strip() for s in combined_prose.split('.') if s.strip()]
        if sentences:
            first_words = [s.split()[0].lower() for s in sentences if s.split()]
            unique_starts = len(set(first_words)) / len(first_words) if first_words else 0
            
            if unique_starts > 0.7:
                distinctive_elements += 2
        
        if distinctive_elements >= 3:
            return "✅ Strong, distinctive narrative voice"
        elif distinctive_elements >= 1:
            return "⚠️ Moderate voice strength - consider more distinctive elements"
        else:
            return "⚠️ Voice could be more distinctive and memorable"
    
    def _suggest_sentence_improvements(self, prose: str) -> list:
        """Suggest sentence structure improvements"""
        suggestions = []
        
        sentences = [s.strip() for s in prose.split('.') if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if avg_length > 20:
                suggestions.append("Consider breaking up long sentences for better readability")
            elif avg_length < 8:
                suggestions.append("Consider combining short sentences for better flow")
        
        return suggestions
    
    def _suggest_vocabulary_improvements(self, prose: str) -> list:
        """Suggest vocabulary improvements"""
        suggestions = []
        
        words = prose.lower().split()
        
        # Check for overused words
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        overused_words = [word for word, count in word_counts.items() if count > len(words) * 0.02]
        
        if overused_words:
            suggestions.append(f"Consider varying these frequently used words: {', '.join(overused_words[:5])}")
        
        return suggestions
    
    def _suggest_pacing_improvements(self, prose: str) -> list:
        """Suggest pacing improvements"""
        suggestions = []
        
        # Check for pacing variety
        action_words = ['ran', 'jumped', 'grabbed', 'shouted', 'rushed']
        contemplation_words = ['thought', 'wondered', 'considered', 'reflected']
        
        action_count = sum(1 for word in action_words if word in prose.lower())
        contemplation_count = sum(1 for word in contemplation_words if word in prose.lower())
        
        if action_count == 0:
            suggestions.append("Consider adding more action for dynamic pacing")
        elif contemplation_count == 0:
            suggestions.append("Consider adding reflective moments for pacing variety")
        
        return suggestions
    
    def _suggest_show_vs_tell_improvements(self, prose: str) -> list:
        """Suggest show vs tell improvements"""
        suggestions = []
        
        # Look for telling indicators
        telling_phrases = ['he was angry', 'she was sad', 'he felt', 'she was beautiful']
        telling_count = sum(1 for phrase in telling_phrases if phrase in prose.lower())
        
        if telling_count > 0:
            suggestions.append("Consider showing emotions through actions and dialogue instead of stating them")
        
        return suggestions
    
    def _suggest_dialogue_improvements(self, prose: str) -> list:
        """Suggest dialogue improvements"""
        suggestions = []
        
        dialogue_lines = [line for line in prose.split('\n') if '"' in line]
        
        if dialogue_lines:
            # Check for adverb overuse in dialogue tags
            adverb_tags = sum(1 for line in dialogue_lines if any(word.endswith('ly') for word in line.split()))
            
            if adverb_tags > len(dialogue_lines) * 0.3:
                suggestions.append("Consider reducing adverbs in dialogue tags - use stronger verbs instead")
        
        return suggestions
    
    def _get_genre_guidelines(self, genre: str) -> str:
        """Get style guidelines for specific genre"""
        guidelines = {
            "fantasy": "Use rich, descriptive language. Include sensory details for magical elements. Vary sentence structure for epic feel.",
            "thriller": "Use short, punchy sentences for tension. Include sensory details that heighten suspense. Maintain urgent pacing.",
            "romance": "Focus on emotional language and internal thoughts. Use sensory details for intimate moments. Vary pacing between action and reflection.",
            "science fiction": "Balance technical concepts with accessible language. Use precise terminology. Maintain logical flow for complex ideas.",
            "mystery": "Use precise, observational language. Include details that serve as clues. Maintain tension through pacing.",
            "literary fiction": "Emphasize character voice and internal depth. Use sophisticated vocabulary and varied sentence structure."
        }
        
        return guidelines.get(genre.lower(), "Focus on clear, engaging prose appropriate for your story and audience.")
    
    def _analyze_genre_alignment(self) -> str:
        """Analyze how current prose aligns with genre expectations"""
        combined_prose = ' '.join(self.prose_samples)
        return self._analyze_genre_fit(combined_prose)
    
    def _get_adaptation_recommendations(self, genre: str) -> str:
        """Get specific recommendations for adapting to genre"""
        recommendations = {
            "fantasy": "- Add more sensory descriptions of magical elements\n- Use archaic or formal language sparingly for authenticity\n- Include world-building details naturally in narrative",
            "thriller": "- Increase short, punchy sentences during action\n- Add more sensory details that create unease\n- Use present tense for immediacy in action scenes",
            "romance": "- Increase emotional vocabulary and internal thoughts\n- Add more sensory descriptions of physical attraction\n- Balance dialogue with internal reflection",
            "science fiction": "- Integrate technical concepts smoothly into narrative\n- Use precise, scientific vocabulary appropriately\n- Balance exposition with character development",
            "mystery": "- Include observational details that could be clues\n- Use precise, investigative language\n- Maintain objective tone in clue presentation"
        }
        
        return recommendations.get(genre.lower(), "Adapt prose style to match genre conventions and reader expectations.")