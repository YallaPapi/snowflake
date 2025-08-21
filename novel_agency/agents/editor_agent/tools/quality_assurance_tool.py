"""
Quality Assurance Tool - Professional Standards Verification

Verifies manuscript meets professional publishing standards.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class QualityAssuranceTool(BaseTool):
    """
    Tool for comprehensive quality assurance and professional standards verification.
    """
    
    action: str = Field(..., description="Action to perform: 'assess_overall_quality', 'check_technical_standards', 'evaluate_readability', 'verify_completeness'")
    manuscript: str = Field(default="", description="Complete manuscript for quality assessment")
    target_audience: str = Field(default="adult", description="Target audience for appropriate quality standards")
    genre: str = Field(default="", description="Genre for genre-specific quality standards")
    word_count_target: int = Field(default=80000, description="Target word count for length assessment")
    
    def run(self) -> str:
        """Execute quality assurance tool action"""
        
        if self.action == "assess_overall_quality":
            return self._assess_overall_quality()
        elif self.action == "check_technical_standards":
            return self._check_technical_standards()
        elif self.action == "evaluate_readability":
            return self._evaluate_readability()
        elif self.action == "verify_completeness":
            return self._verify_completeness()
        else:
            return "Error: Invalid action. Use 'assess_overall_quality', 'check_technical_standards', 'evaluate_readability', or 'verify_completeness'"
    
    def _assess_overall_quality(self) -> str:
        """Assess overall manuscript quality"""
        if not self.manuscript:
            return "Error: Manuscript required for quality assessment"
        
        assessment = f"🏆 OVERALL QUALITY ASSESSMENT\n\n"
        
        # Calculate quality metrics
        quality_scores = {}
        quality_issues = []
        
        # Structure quality
        structure_score, structure_issues = self._assess_structure_quality()
        quality_scores['structure'] = structure_score
        quality_issues.extend(structure_issues)
        
        # Prose quality
        prose_score, prose_issues = self._assess_prose_quality()
        quality_scores['prose'] = prose_score
        quality_issues.extend(prose_issues)
        
        # Character quality
        character_score, character_issues = self._assess_character_quality()
        quality_scores['character'] = character_score
        quality_issues.extend(character_issues)
        
        # Pacing quality
        pacing_score, pacing_issues = self._assess_pacing_quality()
        quality_scores['pacing'] = pacing_score
        quality_issues.extend(pacing_issues)
        
        # Overall scoring
        overall_score = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0
        
        assessment += f"**Quality Scores (0-10 scale):**\n"
        for category, score in quality_scores.items():
            assessment += f"{category.title()}: {score:.1f}/10\n"
        assessment += f"**Overall Score: {overall_score:.1f}/10**\n\n"
        
        # Quality rating
        if overall_score >= 8.0:
            rating = "EXCELLENT - Publication Ready"
            rating_symbol = "🟢"
        elif overall_score >= 6.5:
            rating = "GOOD - Minor Revisions Recommended"
            rating_symbol = "🟡"
        elif overall_score >= 5.0:
            rating = "ACCEPTABLE - Moderate Revisions Needed"
            rating_symbol = "🟠"
        else:
            rating = "NEEDS IMPROVEMENT - Major Revisions Required"
            rating_symbol = "🔴"
        
        assessment += f"**Quality Rating: {rating_symbol} {rating}**\n\n"
        
        # Priority issues
        if quality_issues:
            high_priority = [issue for issue in quality_issues if 'CRITICAL' in issue]
            medium_priority = [issue for issue in quality_issues if 'MODERATE' in issue]
            low_priority = [issue for issue in quality_issues if 'MINOR' in issue]
            
            assessment += f"**Priority Issues:**\n"
            if high_priority:
                assessment += f"🔴 Critical Issues: {len(high_priority)}\n"
                for issue in high_priority[:3]:  # Show top 3
                    assessment += f"  - {issue.replace('CRITICAL: ', '')}\n"
            
            if medium_priority:
                assessment += f"🟡 Moderate Issues: {len(medium_priority)}\n"
                for issue in medium_priority[:3]:  # Show top 3
                    assessment += f"  - {issue.replace('MODERATE: ', '')}\n"
            
            if low_priority:
                assessment += f"🟢 Minor Issues: {len(low_priority)}\n"
        
        return assessment
    
    def _check_technical_standards(self) -> str:
        """Check technical writing and formatting standards"""
        if not self.manuscript:
            return "Error: Manuscript required for technical standards check"
        
        technical = f"📝 TECHNICAL STANDARDS CHECK\n\n"
        
        technical_issues = []
        technical_scores = {}
        
        # Grammar and punctuation
        grammar_score, grammar_issues = self._check_grammar_punctuation()
        technical_scores['grammar'] = grammar_score
        technical_issues.extend(grammar_issues)
        
        # Formatting consistency
        format_score, format_issues = self._check_formatting()
        technical_scores['formatting'] = format_score
        technical_issues.extend(format_issues)
        
        # Dialogue formatting
        dialogue_score, dialogue_issues = self._check_dialogue_formatting()
        technical_scores['dialogue'] = dialogue_score
        technical_issues.extend(dialogue_issues)
        
        # Manuscript length
        length_score, length_issues = self._check_manuscript_length()
        technical_scores['length'] = length_score
        technical_issues.extend(length_issues)
        
        # Technical scoring
        technical_avg = sum(technical_scores.values()) / len(technical_scores) if technical_scores else 0
        
        technical += f"**Technical Standards (0-10 scale):**\n"
        for category, score in technical_scores.items():
            technical += f"{category.title()}: {score:.1f}/10\n"
        technical += f"**Technical Average: {technical_avg:.1f}/10**\n\n"
        
        if technical_issues:
            technical += f"**Technical Issues Found: {len(technical_issues)}**\n"
            for i, issue in enumerate(technical_issues[:10], 1):  # Show top 10
                technical += f"{i}. {issue}\n"
            
            if len(technical_issues) > 10:
                technical += f"... and {len(technical_issues) - 10} more issues\n"
        else:
            technical += f"✅ No technical issues detected\n"
        
        return technical
    
    def _evaluate_readability(self) -> str:
        """Evaluate manuscript readability and accessibility"""
        if not self.manuscript:
            return "Error: Manuscript required for readability evaluation"
        
        readability = f"📖 READABILITY EVALUATION\n\n"
        
        # Calculate readability metrics
        word_count = len(self.manuscript.split())
        sentence_count = len([s for s in self.manuscript.split('.') if s.strip()])
        paragraph_count = len([p for p in self.manuscript.split('\n\n') if p.strip()])
        
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        avg_sentences_per_paragraph = sentence_count / paragraph_count if paragraph_count > 0 else 0
        
        readability += f"**Readability Metrics:**\n"
        readability += f"Total words: {word_count:,}\n"
        readability += f"Average words per sentence: {avg_words_per_sentence:.1f}\n"
        readability += f"Average sentences per paragraph: {avg_sentences_per_paragraph:.1f}\n\n"
        
        # Readability assessment
        readability_issues = []
        
        # Sentence length assessment
        if avg_words_per_sentence > 25:
            readability_issues.append("MODERATE: Sentences may be too long for easy reading")
        elif avg_words_per_sentence < 8:
            readability_issues.append("MINOR: Very short sentences may impact flow")
        
        # Paragraph length assessment
        if avg_sentences_per_paragraph > 8:
            readability_issues.append("MODERATE: Paragraphs may be too long for readability")
        elif avg_sentences_per_paragraph < 2:
            readability_issues.append("MINOR: Very short paragraphs may fragment reading experience")
        
        # Vocabulary complexity
        complex_words = [word for word in self.manuscript.split() if len(word) > 8]
        complexity_ratio = len(complex_words) / word_count if word_count > 0 else 0
        
        if complexity_ratio > 0.15 and self.target_audience in ['middle_grade', 'young_adult']:
            readability_issues.append("MODERATE: Vocabulary may be too complex for target audience")
        
        # Dialogue ratio
        dialogue_lines = [line for line in self.manuscript.split('\n') if '"' in line]
        dialogue_ratio = len(dialogue_lines) / (word_count / 20) if word_count > 0 else 0  # Rough estimate
        
        if dialogue_ratio < 0.1:
            readability_issues.append("MINOR: Consider adding more dialogue for reader engagement")
        
        readability += f"**Readability Assessment:**\n"
        if readability_issues:
            for issue in readability_issues:
                readability += f"⚠️ {issue.split(': ', 1)[1]}\n"
        else:
            readability += f"✅ Good readability for target audience ({self.target_audience})\n"
        
        return readability
    
    def _verify_completeness(self) -> str:
        """Verify manuscript completeness"""
        if not self.manuscript:
            return "Error: Manuscript required for completeness verification"
        
        completeness = f"✅ COMPLETENESS VERIFICATION\n\n"
        
        completeness_issues = []
        
        # Check for complete story structure
        structure_elements = self._check_story_structure_completeness()
        completeness_issues.extend(structure_elements)
        
        # Check for unresolved plot threads
        plot_threads = self._check_plot_thread_resolution()
        completeness_issues.extend(plot_threads)
        
        # Check for character arc completion
        character_arcs = self._check_character_arc_completion()
        completeness_issues.extend(character_arcs)
        
        # Check for proper ending
        ending_check = self._check_ending_completeness()
        completeness_issues.extend(ending_check)
        
        completeness += f"**Completeness Check Results:**\n"
        if completeness_issues:
            completeness += f"Issues found: {len(completeness_issues)}\n\n"
            for i, issue in enumerate(completeness_issues, 1):
                completeness += f"{i}. {issue}\n"
        else:
            completeness += f"✅ Manuscript appears complete and resolved\n"
        
        return completeness
    
    def _assess_structure_quality(self) -> tuple:
        """Assess story structure quality"""
        score = 7.0  # Default score
        issues = []
        
        # Check for clear beginning, middle, end
        word_count = len(self.manuscript.split())
        
        if word_count < 50000:
            score -= 1.0
            issues.append("MODERATE: Manuscript may be too short for complete story development")
        elif word_count > 150000:
            score -= 0.5
            issues.append("MINOR: Manuscript may be longer than typical for genre")
        
        # Check for clear story progression
        if 'climax' not in self.manuscript.lower() and 'final' not in self.manuscript.lower():
            score -= 0.5
            issues.append("MODERATE: Climactic elements not clearly evident")
        
        return score, issues
    
    def _assess_prose_quality(self) -> tuple:
        """Assess prose writing quality"""
        score = 7.0  # Default score
        issues = []
        
        # Check sentence variety
        sentences = [s.strip() for s in self.manuscript.split('.') if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        if sentence_lengths:
            length_variance = max(sentence_lengths) - min(sentence_lengths)
            if length_variance < 5:
                score -= 0.5
                issues.append("MINOR: Consider varying sentence lengths for better rhythm")
        
        # Check for show vs tell
        telling_indicators = ['was angry', 'was sad', 'felt happy', 'was beautiful']
        telling_count = sum(1 for indicator in telling_indicators if indicator in self.manuscript.lower())
        
        if telling_count > len(sentences) * 0.1:
            score -= 1.0
            issues.append("MODERATE: Consider showing emotions through actions rather than stating them")
        
        return score, issues
    
    def _assess_character_quality(self) -> tuple:
        """Assess character development quality"""
        score = 7.0  # Default score
        issues = []
        
        # Check for character dialogue
        dialogue_count = self.manuscript.count('"')
        word_count = len(self.manuscript.split())
        
        dialogue_ratio = dialogue_count / (word_count / 100) if word_count > 0 else 0
        
        if dialogue_ratio < 10:  # Less than ~10% dialogue
            score -= 0.5
            issues.append("MINOR: Consider adding more character dialogue")
        
        # Check for character names (simple heuristic)
        capitalized_words = [word for word in self.manuscript.split() if word[0].isupper() and len(word) > 2]
        unique_names = set(capitalized_words)
        
        if len(unique_names) < 3:
            score -= 0.5
            issues.append("MODERATE: Story may need more character development")
        
        return score, issues
    
    def _assess_pacing_quality(self) -> tuple:
        """Assess story pacing quality"""
        score = 7.0  # Default score
        issues = []
        
        # Check for action/reflection balance
        action_words = ['ran', 'jumped', 'grabbed', 'shouted', 'fought', 'raced']
        reflection_words = ['thought', 'considered', 'wondered', 'remembered', 'realized']
        
        action_count = sum(1 for word in action_words if word in self.manuscript.lower())
        reflection_count = sum(1 for word in reflection_words if word in self.manuscript.lower())
        
        if action_count == 0:
            score -= 1.0
            issues.append("MODERATE: Story may lack dynamic action sequences")
        elif reflection_count == 0:
            score -= 1.0
            issues.append("MODERATE: Story may lack character introspection")
        
        return score, issues
    
    def _check_grammar_punctuation(self) -> tuple:
        """Check grammar and punctuation"""
        score = 8.0  # Default high score for technical aspects
        issues = []
        
        # Basic punctuation checks
        if self.manuscript.count('"') % 2 != 0:
            score -= 1.0
            issues.append("CRITICAL: Unmatched quotation marks detected")
        
        # Check for basic formatting
        if not self.manuscript[0].isupper():
            score -= 0.5
            issues.append("MINOR: Manuscript should start with capital letter")
        
        return score, issues
    
    def _check_formatting(self) -> tuple:
        """Check formatting consistency"""
        score = 8.0  # Default high score
        issues = []
        
        # Check paragraph breaks
        lines = self.manuscript.split('\n')
        if len(lines) < 10:
            score -= 1.0
            issues.append("MODERATE: Manuscript may lack proper paragraph breaks")
        
        return score, issues
    
    def _check_dialogue_formatting(self) -> tuple:
        """Check dialogue formatting"""
        score = 8.0  # Default high score
        issues = []
        
        dialogue_lines = [line for line in self.manuscript.split('\n') if '"' in line]
        
        if dialogue_lines:
            # Check for proper dialogue punctuation
            improper_format = 0
            for line in dialogue_lines[:10]:  # Check first 10 dialogue lines
                if '"' in line and not (line.strip().endswith('.') or line.strip().endswith(',') or line.strip().endswith('!') or line.strip().endswith('?')):
                    improper_format += 1
            
            if improper_format > 0:
                score -= improper_format * 0.5
                issues.append(f"MODERATE: {improper_format} dialogue formatting issues detected")
        
        return score, issues
    
    def _check_manuscript_length(self) -> tuple:
        """Check manuscript length appropriateness"""
        score = 8.0  # Default high score
        issues = []
        
        word_count = len(self.manuscript.split())
        
        # Genre-specific length expectations
        genre_ranges = {
            'fantasy': (80000, 120000),
            'science fiction': (80000, 100000),
            'thriller': (70000, 90000),
            'romance': (50000, 90000),
            'mystery': (70000, 90000),
            'literary fiction': (80000, 100000)
        }
        
        if self.genre.lower() in genre_ranges:
            min_words, max_words = genre_ranges[self.genre.lower()]
            
            if word_count < min_words:
                score -= 1.0
                issues.append(f"MODERATE: Length ({word_count:,} words) below typical {self.genre} range ({min_words:,}-{max_words:,})")
            elif word_count > max_words:
                score -= 0.5
                issues.append(f"MINOR: Length ({word_count:,} words) above typical {self.genre} range ({min_words:,}-{max_words:,})")
        
        return score, issues
    
    def _check_story_structure_completeness(self) -> list:
        """Check for complete story structure"""
        issues = []
        
        # Check for story beginning
        if not self.manuscript[:1000].strip():
            issues.append("CRITICAL: Manuscript appears to have no clear beginning")
        
        # Check for story ending
        if not self.manuscript[-1000:].strip():
            issues.append("CRITICAL: Manuscript appears to have no clear ending")
        
        # Check for story development
        if len(self.manuscript.split()) < 10000:
            issues.append("CRITICAL: Manuscript too short for complete story development")
        
        return issues
    
    def _check_plot_thread_resolution(self) -> list:
        """Check for unresolved plot threads"""
        issues = []
        
        # Look for unresolved elements (simplified check)
        unresolved_indicators = ['to be continued', 'will be resolved', 'mystery remains', 'still unknown']
        
        for indicator in unresolved_indicators:
            if indicator in self.manuscript.lower():
                issues.append(f"MODERATE: Potential unresolved plot element: '{indicator}'")
        
        return issues
    
    def _check_character_arc_completion(self) -> list:
        """Check for complete character arcs"""
        issues = []
        
        # Look for character growth indicators
        growth_indicators = ['learned', 'realized', 'changed', 'transformed', 'discovered']
        
        growth_count = sum(1 for indicator in growth_indicators if indicator in self.manuscript.lower())
        
        if growth_count == 0:
            issues.append("MODERATE: Character growth and transformation not clearly evident")
        
        return issues
    
    def _check_ending_completeness(self) -> list:
        """Check for proper story ending"""
        issues = []
        
        ending_portion = self.manuscript[-2000:].lower() if len(self.manuscript) > 2000 else self.manuscript.lower()
        
        # Look for resolution indicators
        resolution_indicators = ['resolved', 'concluded', 'finally', 'end', 'finished']
        
        resolution_count = sum(1 for indicator in resolution_indicators if indicator in ending_portion)
        
        if resolution_count == 0:
            issues.append("MODERATE: Ending may lack clear resolution")
        
        return issues