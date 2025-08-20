"""
Content Refinement for Scene Generation

This implements subtask 44.3: Content Refinement
Post-generation content improvement and validation system that enhances
generated scenes for quality, compliance, and narrative effectiveness.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib

from ..models import SceneCard, SceneType, ViewpointType, TenseType
from ..validation.service import SceneValidationService, ValidationRequest, ValidationResponse


class RefinementType(Enum):
    """Types of content refinement"""
    STRUCTURE = "structure"
    STYLE = "style"
    CONSISTENCY = "consistency"
    PACING = "pacing"
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    CHARACTER = "character"
    TONE = "tone"
    GRAMMAR = "grammar"
    SNOWFLAKE_COMPLIANCE = "snowflake_compliance"


class RefinementPriority(Enum):
    """Priority levels for refinements"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


@dataclass
class RefinementIssue:
    """Represents an issue found during content analysis"""
    issue_id: str
    refinement_type: RefinementType
    priority: RefinementPriority
    description: str
    location: str  # Where in the content the issue occurs
    suggestion: str
    
    # Context information
    line_number: Optional[int] = None
    character_position: Optional[int] = None
    affected_text: Optional[str] = None
    
    # Resolution tracking
    resolved: bool = False
    resolution_method: Optional[str] = None
    resolution_confidence: float = 0.0
    
    def __post_init__(self):
        if not self.issue_id:
            self.issue_id = f"issue_{int(datetime.utcnow().timestamp())}_{hash(self.description)}"


@dataclass
class RefinementSuggestion:
    """Specific suggestion for improving content"""
    suggestion_id: str
    original_text: str
    improved_text: str
    refinement_type: RefinementType
    confidence_score: float
    reasoning: str
    
    # Implementation details
    requires_ai_generation: bool = False
    affects_structure: bool = False
    impact_scope: str = "local"  # local, scene, story
    
    def __post_init__(self):
        if not self.suggestion_id:
            self.suggestion_id = f"suggestion_{int(datetime.utcnow().timestamp())}_{hash(self.original_text)}"


@dataclass
class RefinementReport:
    """Comprehensive report on content analysis and refinement"""
    content_id: str
    analysis_timestamp: datetime
    original_word_count: int
    
    # Issues and suggestions
    issues_found: List[RefinementIssue] = field(default_factory=list)
    suggestions_made: List[RefinementSuggestion] = field(default_factory=list)
    
    # Quality metrics
    overall_quality_score: float = 0.0
    structure_score: float = 0.0
    style_score: float = 0.0
    consistency_score: float = 0.0
    snowflake_compliance_score: float = 0.0
    
    # Processing statistics
    processing_time_seconds: float = 0.0
    refinements_applied: int = 0
    confidence_threshold: float = 0.7
    
    # Final state
    refinement_complete: bool = False
    final_word_count: int = 0
    improvement_percentage: float = 0.0


class ContentAnalyzer:
    """Analyzes content for potential refinement opportunities"""
    
    def __init__(self, validation_service: Optional[SceneValidationService] = None):
        self.validation_service = validation_service or SceneValidationService()
        
        # Analysis patterns
        self.dialogue_patterns = {
            'untagged_dialogue': r'"[^"]*"(?!\s*[,.]?\s*\w+\s+(?:said|asked|replied|whispered|shouted))',
            'repetitive_tags': r'(said|asked|replied)\s+\w+.*?\1\s+\w+',
            'adverb_heavy': r'\w+ly\s*[,.]?\s*"\s*\w+\s+(?:said|asked|replied)',
        }
        
        self.pacing_patterns = {
            'run_on_sentences': r'[.!?]\s+\w+.*?[.!?]\s+\w+.*?[.!?]\s+\w+.*?[.!?]',
            'choppy_rhythm': r'(?:[.!?]\s+){4,}\w+[.!?]',
            'paragraph_length': r'\n\n(.+?)(?=\n\n|\Z)',
        }
        
        self.consistency_patterns = {
            'pov_shifts': r'\b(I|me|my|mine)\b.*?\b(he|she|they|him|her|them)\b',
            'tense_inconsistency': r'\b(was|were|had)\b.*?\b(is|are|has|will)\b',
            'name_variations': r'\b([A-Z][a-z]+)\b.*?\b([A-Z][a-z]*\1|[A-Z][a-z]+)\b',
        }
    
    def analyze_content(self, scene_card: SceneCard, prose_content: str) -> RefinementReport:
        """Perform comprehensive content analysis"""
        
        start_time = datetime.utcnow()
        content_id = f"analysis_{int(start_time.timestamp())}"
        
        issues = []
        suggestions = []
        
        # Analyze structure
        structure_issues = self._analyze_structure(scene_card, prose_content)
        issues.extend(structure_issues)
        
        # Analyze prose style
        style_issues = self._analyze_style(prose_content)
        issues.extend(style_issues)
        
        # Analyze consistency
        consistency_issues = self._analyze_consistency(prose_content)
        issues.extend(consistency_issues)
        
        # Analyze dialogue
        dialogue_issues = self._analyze_dialogue(prose_content)
        issues.extend(dialogue_issues)
        
        # Analyze pacing
        pacing_issues = self._analyze_pacing(prose_content)
        issues.extend(pacing_issues)
        
        # Analyze Snowflake compliance
        compliance_issues = self._analyze_snowflake_compliance(scene_card)
        issues.extend(compliance_issues)
        
        # Generate suggestions from issues
        for issue in issues:
            suggestion = self._generate_suggestion_from_issue(issue, prose_content)
            if suggestion:
                suggestions.append(suggestion)
        
        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(scene_card, prose_content, issues)
        
        # Create refinement report
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return RefinementReport(
            content_id=content_id,
            analysis_timestamp=start_time,
            original_word_count=len(prose_content.split()),
            issues_found=issues,
            suggestions_made=suggestions,
            overall_quality_score=quality_scores['overall'],
            structure_score=quality_scores['structure'],
            style_score=quality_scores['style'],
            consistency_score=quality_scores['consistency'],
            snowflake_compliance_score=quality_scores['snowflake_compliance'],
            processing_time_seconds=processing_time
        )
    
    def _analyze_structure(self, scene_card: SceneCard, prose_content: str) -> List[RefinementIssue]:
        """Analyze scene structure issues"""
        
        issues = []
        
        # Check scene opening
        if not prose_content.strip():
            issues.append(RefinementIssue(
                issue_id="",
                refinement_type=RefinementType.STRUCTURE,
                priority=RefinementPriority.CRITICAL,
                description="Scene has no prose content",
                location="entire_scene",
                suggestion="Generate prose content for the scene"
            ))
            return issues
        
        first_paragraph = prose_content.split('\n\n')[0] if '\n\n' in prose_content else prose_content
        
        # Check for weak opening
        weak_openings = ['the', 'it', 'there', 'when', 'as']
        first_word = first_paragraph.split()[0].lower() if first_paragraph.split() else ""
        
        if first_word in weak_openings:
            issues.append(RefinementIssue(
                issue_id="",
                refinement_type=RefinementType.STRUCTURE,
                priority=RefinementPriority.MEDIUM,
                description="Scene opens with weak construction",
                location="opening_sentence",
                suggestion="Start with character action or strong imagery",
                affected_text=first_paragraph.split('.')[0] if '.' in first_paragraph else first_paragraph[:100]
            ))
        
        # Check scene ending
        paragraphs = prose_content.split('\n\n')
        if len(paragraphs) > 1:
            last_paragraph = paragraphs[-1]
            
            # Check for weak ending
            if len(last_paragraph.split()) < 10:
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.STRUCTURE,
                    priority=RefinementPriority.HIGH,
                    description="Scene ending is too brief",
                    location="final_paragraph",
                    suggestion="Expand the scene's conclusion to show clear resolution or transition",
                    affected_text=last_paragraph
                ))
        
        # Check for scene structure based on type
        if scene_card.scene_type == SceneType.PROACTIVE:
            if not self._contains_goal_indicators(prose_content):
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                    priority=RefinementPriority.HIGH,
                    description="Proactive scene lacks clear goal indicators",
                    location="throughout_scene", 
                    suggestion="Include text showing character's specific goal or intention"
                ))
            
            if not self._contains_conflict_indicators(prose_content):
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                    priority=RefinementPriority.HIGH,
                    description="Proactive scene lacks conflict indicators",
                    location="throughout_scene",
                    suggestion="Show obstacles or opposition to the character's goal"
                ))
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if not self._contains_reaction_indicators(prose_content):
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                    priority=RefinementPriority.HIGH,
                    description="Reactive scene lacks emotional reaction indicators",
                    location="throughout_scene",
                    suggestion="Show character's emotional response to previous events"
                ))
        
        return issues
    
    def _analyze_style(self, prose_content: str) -> List[RefinementIssue]:
        """Analyze prose style issues"""
        
        issues = []
        
        # Check for repetitive sentence structure
        sentences = re.split(r'[.!?]+', prose_content)
        if len(sentences) > 3:
            similar_starts = 0
            for i in range(len(sentences) - 1):
                current_start = sentences[i].strip()[:10].lower()
                next_start = sentences[i + 1].strip()[:10].lower()
                if current_start and next_start and current_start == next_start:
                    similar_starts += 1
            
            if similar_starts > 2:
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.STYLE,
                    priority=RefinementPriority.MEDIUM,
                    description="Repetitive sentence structure detected",
                    location="throughout_scene",
                    suggestion="Vary sentence beginnings and structures for better flow"
                ))
        
        # Check for excessive adverbs
        adverbs = re.findall(r'\b\w+ly\b', prose_content)
        if len(adverbs) > len(prose_content.split()) * 0.05:  # More than 5% adverbs
            issues.append(RefinementIssue(
                issue_id="",
                refinement_type=RefinementType.STYLE,
                priority=RefinementPriority.LOW,
                description="Excessive use of adverbs",
                location="throughout_scene",
                suggestion="Replace adverbs with stronger verbs or more precise descriptions"
            ))
        
        # Check for passive voice overuse
        passive_patterns = [r'\bwas\s+\w+ed\b', r'\bwere\s+\w+ed\b', r'\bbeing\s+\w+ed\b']
        passive_count = sum(len(re.findall(pattern, prose_content, re.IGNORECASE)) 
                           for pattern in passive_patterns)
        
        if passive_count > len(prose_content.split()) * 0.03:  # More than 3% passive
            issues.append(RefinementIssue(
                issue_id="",
                refinement_type=RefinementType.STYLE,
                priority=RefinementPriority.MEDIUM,
                description="Overuse of passive voice",
                location="throughout_scene",
                suggestion="Convert to active voice for more dynamic prose"
            ))
        
        return issues
    
    def _analyze_consistency(self, prose_content: str) -> List[RefinementIssue]:
        """Analyze consistency issues"""
        
        issues = []
        
        # Check for POV consistency
        pov_indicators = {
            'first': [r'\b(I|me|my|mine)\b'],
            'third': [r'\b(he|she|him|her|his|hers)\b']
        }
        
        first_person_count = sum(len(re.findall(pattern, prose_content, re.IGNORECASE))
                               for pattern in pov_indicators['first'])
        third_person_count = sum(len(re.findall(pattern, prose_content, re.IGNORECASE))
                               for pattern in pov_indicators['third'])
        
        if first_person_count > 0 and third_person_count > 0:
            if min(first_person_count, third_person_count) > 2:  # Significant presence of both
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.CONSISTENCY,
                    priority=RefinementPriority.HIGH,
                    description="Inconsistent point of view",
                    location="throughout_scene",
                    suggestion="Maintain consistent POV throughout the scene"
                ))
        
        # Check for tense consistency
        past_tense = len(re.findall(r'\b(was|were|had|went|came|said|did)\b', prose_content, re.IGNORECASE))
        present_tense = len(re.findall(r'\b(is|are|has|goes|comes|says|does)\b', prose_content, re.IGNORECASE))
        
        if past_tense > 0 and present_tense > 0:
            if min(past_tense, present_tense) > max(past_tense, present_tense) * 0.3:
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.CONSISTENCY,
                    priority=RefinementPriority.MEDIUM,
                    description="Inconsistent verb tense",
                    location="throughout_scene",
                    suggestion="Maintain consistent tense throughout the scene"
                ))
        
        return issues
    
    def _analyze_dialogue(self, prose_content: str) -> List[RefinementIssue]:
        """Analyze dialogue quality"""
        
        issues = []
        
        # Check for dialogue presence and quality
        dialogue_matches = re.findall(r'"[^"]*"', prose_content)
        
        if dialogue_matches:
            # Check for untagged dialogue
            untagged_count = 0
            for match in dialogue_matches:
                # Look for dialogue tags within 20 characters after the quote
                context_after = prose_content[prose_content.find(match) + len(match):prose_content.find(match) + len(match) + 20]
                if not re.search(r'\s*(said|asked|replied|whispered|shouted|answered)', context_after, re.IGNORECASE):
                    untagged_count += 1
            
            if untagged_count > len(dialogue_matches) * 0.7:  # More than 70% untagged
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.DIALOGUE,
                    priority=RefinementPriority.MEDIUM,
                    description="Most dialogue lacks attribution tags",
                    location="dialogue_sections",
                    suggestion="Add dialogue tags for clarity, but vary beyond 'said'"
                ))
            
            # Check for repetitive dialogue tags
            tag_pattern = r'(said|asked|replied|whispered|shouted)'
            tag_matches = re.findall(tag_pattern, prose_content, re.IGNORECASE)
            
            if tag_matches:
                said_count = tag_matches.count('said') + tag_matches.count('Said')
                if said_count > len(tag_matches) * 0.8:  # More than 80% are "said"
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.DIALOGUE,
                        priority=RefinementPriority.LOW,
                        description="Overuse of 'said' in dialogue tags",
                        location="dialogue_sections",
                        suggestion="Vary dialogue tags with 'asked', 'replied', 'whispered', etc."
                    ))
        
        return issues
    
    def _analyze_pacing(self, prose_content: str) -> List[RefinementIssue]:
        """Analyze pacing and rhythm"""
        
        issues = []
        
        # Analyze sentence length variety
        sentences = [s.strip() for s in re.split(r'[.!?]+', prose_content) if s.strip()]
        
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            
            # Check for monotonous sentence length
            similar_length_count = sum(1 for length in lengths 
                                     if abs(length - avg_length) < 2)
            
            if similar_length_count > len(lengths) * 0.7:  # More than 70% similar length
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.PACING,
                    priority=RefinementPriority.MEDIUM,
                    description="Sentences are too similar in length",
                    location="throughout_scene",
                    suggestion="Vary sentence length for better rhythm and pacing"
                ))
            
            # Check for extremely long sentences
            very_long = [s for s in sentences if len(s.split()) > 35]
            if len(very_long) > len(sentences) * 0.2:  # More than 20% very long
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.PACING,
                    priority=RefinementPriority.HIGH,
                    description="Too many overly complex sentences",
                    location="throughout_scene",
                    suggestion="Break up long sentences for better readability",
                    affected_text=very_long[0][:100] + "..." if very_long else ""
                ))
        
        # Analyze paragraph length
        paragraphs = [p.strip() for p in prose_content.split('\n\n') if p.strip()]
        
        if paragraphs:
            # Check for wall-of-text paragraphs
            long_paragraphs = [p for p in paragraphs if len(p.split()) > 150]
            
            if long_paragraphs:
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.PACING,
                    priority=RefinementPriority.MEDIUM,
                    description="Some paragraphs are too long",
                    location="long_paragraphs",
                    suggestion="Break long paragraphs into smaller, more digestible chunks"
                ))
        
        return issues
    
    def _analyze_snowflake_compliance(self, scene_card: SceneCard) -> List[RefinementIssue]:
        """Analyze compliance with Snowflake Method principles"""
        
        issues = []
        
        # Check scene crucible
        if not scene_card.scene_crucible or len(scene_card.scene_crucible) < 20:
            issues.append(RefinementIssue(
                issue_id="",
                refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                priority=RefinementPriority.CRITICAL,
                description="Scene crucible is missing or too brief",
                location="scene_metadata",
                suggestion="Provide a clear, detailed scene crucible describing the core conflict"
            ))
        
        # Check scene-specific structure
        if scene_card.scene_type == SceneType.PROACTIVE:
            if scene_card.proactive:
                if not scene_card.proactive.goal or len(scene_card.proactive.goal) < 10:
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                        priority=RefinementPriority.HIGH,
                        description="Proactive goal is missing or too vague",
                        location="proactive_structure",
                        suggestion="Define a specific, measurable goal for the character"
                    ))
                
                if not scene_card.proactive.conflict or len(scene_card.proactive.conflict) < 10:
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                        priority=RefinementPriority.HIGH,
                        description="Proactive conflict is missing or unclear",
                        location="proactive_structure",
                        suggestion="Clearly define what opposes the character's goal"
                    ))
                
                if not scene_card.proactive.setback or len(scene_card.proactive.setback) < 10:
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                        priority=RefinementPriority.HIGH,
                        description="Proactive setback is missing or weak",
                        location="proactive_structure",
                        suggestion="Show how the conflict prevents goal achievement"
                    ))
            else:
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                    priority=RefinementPriority.CRITICAL,
                    description="Proactive scene missing required structure",
                    location="scene_structure",
                    suggestion="Add Goal-Conflict-Setback structure to proactive scene"
                ))
        
        elif scene_card.scene_type == SceneType.REACTIVE:
            if scene_card.reactive:
                if not scene_card.reactive.reaction or len(scene_card.reactive.reaction) < 10:
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                        priority=RefinementPriority.HIGH,
                        description="Reactive reaction is missing or too brief",
                        location="reactive_structure",
                        suggestion="Show authentic emotional response to the setback"
                    ))
                
                if not scene_card.reactive.dilemma or len(scene_card.reactive.dilemma) < 10:
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                        priority=RefinementPriority.HIGH,
                        description="Reactive dilemma is missing or unclear",
                        location="reactive_structure",
                        suggestion="Present difficult choice with competing values"
                    ))
                
                if not scene_card.reactive.decision or len(scene_card.reactive.decision) < 10:
                    issues.append(RefinementIssue(
                        issue_id="",
                        refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                        priority=RefinementPriority.HIGH,
                        description="Reactive decision is missing or vague",
                        location="reactive_structure",
                        suggestion="Show clear decision that launches next scene"
                    ))
            else:
                issues.append(RefinementIssue(
                    issue_id="",
                    refinement_type=RefinementType.SNOWFLAKE_COMPLIANCE,
                    priority=RefinementPriority.CRITICAL,
                    description="Reactive scene missing required structure",
                    location="scene_structure",
                    suggestion="Add Reaction-Dilemma-Decision structure to reactive scene"
                ))
        
        return issues
    
    def _contains_goal_indicators(self, prose_content: str) -> bool:
        """Check if prose contains goal-related language"""
        goal_indicators = [
            r'\bwant\w*\b', r'\bneed\w*\b', r'\bmust\b', r'\bhave to\b',
            r'\bplan\w*\b', r'\bintend\w*\b', r'\bgoal\b', r'\bobjective\b'
        ]
        
        return any(re.search(pattern, prose_content, re.IGNORECASE) 
                  for pattern in goal_indicators)
    
    def _contains_conflict_indicators(self, prose_content: str) -> bool:
        """Check if prose contains conflict-related language"""
        conflict_indicators = [
            r'\bbut\b', r'\bhowever\b', r'\bunfortunately\b', r'\bproblem\b',
            r'\bobstacle\b', r'\bdifficult\b', r'\bimpossible\b', r'\bblocked\b',
            r'\bstopped\b', r'\bprevented\b', r'\bopposed\b'
        ]
        
        return any(re.search(pattern, prose_content, re.IGNORECASE)
                  for pattern in conflict_indicators)
    
    def _contains_reaction_indicators(self, prose_content: str) -> bool:
        """Check if prose contains emotional reaction language"""
        reaction_indicators = [
            r'\bfelt\b', r'\bemotion\w*\b', r'\bangry\b', r'\bsad\b', r'\bfrustrated\b',
            r'\bshocked\b', r'\bsurprised\b', r'\brelieved\b', r'\bworried\b',
            r'\bheart\b.*\b(raced|pounded|sank)\b', r'\bstomach\b.*\b(dropped|churned)\b'
        ]
        
        return any(re.search(pattern, prose_content, re.IGNORECASE)
                  for pattern in reaction_indicators)
    
    def _generate_suggestion_from_issue(self, issue: RefinementIssue, 
                                      prose_content: str) -> Optional[RefinementSuggestion]:
        """Generate specific improvement suggestion from issue"""
        
        if not issue.affected_text:
            return None
        
        # This is a simplified example - in practice would use AI models for better suggestions
        suggestion_text = issue.affected_text
        
        if issue.refinement_type == RefinementType.STYLE:
            if "adverb" in issue.description.lower():
                # Remove adverbs and strengthen verbs
                suggestion_text = re.sub(r'\s+\w+ly\b', '', suggestion_text)
        
        elif issue.refinement_type == RefinementType.PACING:
            if "long" in issue.description.lower():
                # Split long sentences
                sentences = suggestion_text.split('. ')
                if len(sentences) > 1:
                    suggestion_text = '. '.join(sentences[:2]) + '. [Continue in next sentence]'
        
        return RefinementSuggestion(
            suggestion_id="",
            original_text=issue.affected_text,
            improved_text=suggestion_text,
            refinement_type=issue.refinement_type,
            confidence_score=0.6,  # Default medium confidence
            reasoning=issue.suggestion,
            requires_ai_generation=True,
            affects_structure=issue.refinement_type == RefinementType.STRUCTURE
        )
    
    def _calculate_quality_scores(self, scene_card: SceneCard, prose_content: str, 
                                issues: List[RefinementIssue]) -> Dict[str, float]:
        """Calculate quality scores based on analysis"""
        
        # Count issues by priority
        critical_issues = len([i for i in issues if i.priority == RefinementPriority.CRITICAL])
        high_issues = len([i for i in issues if i.priority == RefinementPriority.HIGH])
        medium_issues = len([i for i in issues if i.priority == RefinementPriority.MEDIUM])
        low_issues = len([i for i in issues if i.priority == RefinementPriority.LOW])
        
        # Base score starts high and decreases with issues
        base_score = 1.0
        
        # Deduct points for issues (weighted by priority)
        base_score -= critical_issues * 0.3
        base_score -= high_issues * 0.2
        base_score -= medium_issues * 0.1
        base_score -= low_issues * 0.05
        
        base_score = max(0.0, base_score)  # Don't go below 0
        
        # Calculate category-specific scores
        structure_issues = [i for i in issues if i.refinement_type == RefinementType.STRUCTURE]
        style_issues = [i for i in issues if i.refinement_type == RefinementType.STYLE]
        consistency_issues = [i for i in issues if i.refinement_type == RefinementType.CONSISTENCY]
        snowflake_issues = [i for i in issues if i.refinement_type == RefinementType.SNOWFLAKE_COMPLIANCE]
        
        structure_score = max(0.0, 1.0 - len(structure_issues) * 0.2)
        style_score = max(0.0, 1.0 - len(style_issues) * 0.15)
        consistency_score = max(0.0, 1.0 - len(consistency_issues) * 0.2)
        snowflake_score = max(0.0, 1.0 - len(snowflake_issues) * 0.25)
        
        return {
            'overall': base_score,
            'structure': structure_score,
            'style': style_score,
            'consistency': consistency_score,
            'snowflake_compliance': snowflake_score
        }


class RefinementProcessor:
    """Processes refinement suggestions and applies improvements"""
    
    def __init__(self, analyzer: Optional[ContentAnalyzer] = None):
        self.analyzer = analyzer or ContentAnalyzer()
        self.applied_refinements = []
        
    def apply_refinements(self, scene_card: SceneCard, prose_content: str,
                        refinements: List[RefinementSuggestion],
                        confidence_threshold: float = 0.7) -> Tuple[SceneCard, str, List[str]]:
        """Apply selected refinements to content"""
        
        refined_prose = prose_content
        applied_changes = []
        updated_scene_card = scene_card
        
        # Sort refinements by confidence and priority
        sorted_refinements = sorted(refinements, 
                                  key=lambda r: r.confidence_score, reverse=True)
        
        for refinement in sorted_refinements:
            if refinement.confidence_score < confidence_threshold:
                continue
            
            try:
                # Apply text-based refinements
                if refinement.original_text in refined_prose:
                    refined_prose = refined_prose.replace(
                        refinement.original_text, 
                        refinement.improved_text,
                        1  # Only replace first occurrence
                    )
                    applied_changes.append(f"Applied {refinement.refinement_type.value} refinement")
                    self.applied_refinements.append(refinement)
                
                # Apply structural refinements to scene card
                if refinement.affects_structure:
                    updated_scene_card = self._apply_structural_refinement(
                        updated_scene_card, refinement
                    )
                
            except Exception as e:
                # Log refinement application error but continue
                applied_changes.append(f"Failed to apply refinement: {str(e)}")
        
        return updated_scene_card, refined_prose, applied_changes
    
    def _apply_structural_refinement(self, scene_card: SceneCard, 
                                   refinement: RefinementSuggestion) -> SceneCard:
        """Apply structural changes to scene card"""
        
        # This is a simplified implementation - would need more sophisticated logic
        # to actually modify scene card structure based on refinements
        
        if refinement.refinement_type == RefinementType.SNOWFLAKE_COMPLIANCE:
            # Could update scene crucible, goals, etc. based on refinement
            if "crucible" in refinement.reasoning.lower():
                # Update scene crucible if needed
                if len(scene_card.scene_crucible) < 20:
                    scene_card.scene_crucible = refinement.improved_text[:200]
        
        return scene_card
    
    def get_refinement_statistics(self) -> Dict[str, Any]:
        """Get statistics about applied refinements"""
        
        if not self.applied_refinements:
            return {'total_refinements': 0}
        
        by_type = {}
        total_confidence = 0
        
        for refinement in self.applied_refinements:
            ref_type = refinement.refinement_type.value
            by_type[ref_type] = by_type.get(ref_type, 0) + 1
            total_confidence += refinement.confidence_score
        
        avg_confidence = total_confidence / len(self.applied_refinements)
        
        return {
            'total_refinements': len(self.applied_refinements),
            'refinements_by_type': by_type,
            'average_confidence': avg_confidence,
            'most_common_type': max(by_type.keys(), key=lambda k: by_type[k]) if by_type else None
        }


class ContentRefiner:
    """High-level content refinement coordinator"""
    
    def __init__(self, analyzer: Optional[ContentAnalyzer] = None,
                 processor: Optional[RefinementProcessor] = None):
        self.analyzer = analyzer or ContentAnalyzer()
        self.processor = processor or RefinementProcessor(self.analyzer)
        
    def refine_scene_content(self, scene_card: SceneCard, prose_content: str,
                           refinement_goals: Optional[List[RefinementType]] = None,
                           confidence_threshold: float = 0.7) -> Tuple[SceneCard, str, RefinementReport]:
        """Perform complete content refinement process"""
        
        start_time = datetime.utcnow()
        
        # Analyze content
        analysis_report = self.analyzer.analyze_content(scene_card, prose_content)
        
        # Filter suggestions based on refinement goals
        relevant_suggestions = analysis_report.suggestions_made
        
        if refinement_goals:
            relevant_suggestions = [
                s for s in relevant_suggestions 
                if s.refinement_type in refinement_goals
            ]
        
        # Apply refinements
        refined_scene_card, refined_prose, applied_changes = self.processor.apply_refinements(
            scene_card, prose_content, relevant_suggestions, confidence_threshold
        )
        
        # Update report with final results
        analysis_report.refinement_complete = True
        analysis_report.final_word_count = len(refined_prose.split())
        analysis_report.refinements_applied = len(applied_changes)
        analysis_report.processing_time_seconds = (datetime.utcnow() - start_time).total_seconds()
        
        # Calculate improvement percentage
        if analysis_report.original_word_count > 0:
            word_change = analysis_report.final_word_count - analysis_report.original_word_count
            analysis_report.improvement_percentage = (word_change / analysis_report.original_word_count) * 100
        
        return refined_scene_card, refined_prose, analysis_report
    
    def get_refinement_summary(self) -> Dict[str, Any]:
        """Get comprehensive refinement statistics"""
        
        analyzer_stats = {}  # Would collect from analyzer if it tracked stats
        processor_stats = self.processor.get_refinement_statistics()
        
        return {
            'processor_statistics': processor_stats,
            'analyzer_statistics': analyzer_stats,
            'total_sessions': 1,  # Would track across sessions
            'success_rate': 1.0   # Would calculate from successful refinements
        }