"""
Exposition Budget Tracker

TaskMaster Task 44.5: Add Exposition Budget Tracking
Monitors and limits exposition content in generated prose according to scene requirements.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import logging


class ExpositionType(Enum):
    """Types of exposition content"""
    BACKSTORY = "backstory"
    WORLD_BUILDING = "world_building"
    CHARACTER_DESCRIPTION = "character_description"
    SETTING_DESCRIPTION = "setting_description"
    INTERNAL_THOUGHTS = "internal_thoughts"
    CONTEXT_EXPLANATION = "context_explanation"
    SCENE_SETUP = "scene_setup"


@dataclass
class ExpositionBudget:
    """Budget constraints for different types of exposition"""
    
    # Overall limits
    max_exposition_percentage: float = 0.15  # 15% of total content
    max_total_exposition_words: Optional[int] = None
    
    # Type-specific limits
    max_backstory_sentences: int = 2
    max_world_building_sentences: int = 1
    max_character_description_sentences: int = 2
    max_setting_description_sentences: int = 3
    max_context_explanation_sentences: int = 2
    
    # Behavioral settings
    allow_character_thoughts: bool = True
    allow_scene_setup_exposition: bool = True
    strict_enforcement: bool = True
    
    # Advanced settings
    exposition_density_threshold: float = 0.3  # Max 30% exposition per paragraph
    backstory_depth_limit: int = 1  # How far back to go (1 = immediate past)


@dataclass
class ExpositionEntry:
    """Individual exposition entry for tracking"""
    exposition_type: ExpositionType
    content: str
    word_count: int
    sentence_count: int
    timestamp: datetime = field(default_factory=datetime.now)
    source_section: str = ""
    necessity_score: float = 0.5  # 0-1 scale of how necessary this exposition is


class ExpositionTracker:
    """
    TaskMaster Task 44.5: Exposition Budget Tracking
    
    Monitors exposition content during prose generation and enforces budget limits.
    Provides feedback and warnings when limits are exceeded.
    Tracks different types of exposition separately for fine-grained control.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ExpositionTracker")
        self.reset()
        
        # Exposition detection patterns
        self.exposition_patterns = {
            ExpositionType.BACKSTORY: [
                r'\b(had been|used to|years ago|in the past|previously|before)',
                r'\b(remembered|recalled|thought back|looked back)',
                r'\b(once|formerly|earlier|long ago)'
            ],
            ExpositionType.WORLD_BUILDING: [
                r'\b(in this world|in their society|the system|the way things)',
                r'\b(everyone knew|it was known|the rules|the law)',
                r'\b(tradition|custom|culture|society)'
            ],
            ExpositionType.CHARACTER_DESCRIPTION: [
                r'\b(was known for|had always been|was the type)',
                r'\b(tall|short|dark|blonde|strong|weak) (man|woman|person)',
                r'\b(personality|character|nature|temperament)'
            ],
            ExpositionType.SETTING_DESCRIPTION: [
                r'\b(the room|the building|the place|the area)',
                r'\b(located|situated|positioned|built)',
                r'\b(atmosphere|environment|surroundings)'
            ],
            ExpositionType.INTERNAL_THOUGHTS: [
                r'\b(thought|wondered|considered|reflected)',
                r'\b(realized|understood|knew|felt)',
                r'\b(mind|thoughts|consciousness)'
            ],
            ExpositionType.CONTEXT_EXPLANATION: [
                r'\b(because|since|due to|as a result)',
                r'\b(explanation|reason|cause|background)',
                r'\b(this meant|it was important|the significance)'
            ]
        }
    
    def reset(self):
        """Reset tracker for new scene"""
        self.budget: Optional[ExpositionBudget] = None
        self.exposition_entries: List[ExpositionEntry] = []
        self.total_prose_words: int = 0
        self.warnings: List[str] = []
    
    def initialize_budget(self, budget: ExpositionBudget):
        """Initialize exposition budget for tracking"""
        self.budget = budget
        self.logger.debug(f"Initialized exposition budget with {budget.max_exposition_percentage:.1%} limit")
    
    def add_exposition(self, exposition_type: str, content: str, 
                      source_section: str = "", necessity_score: float = 0.5):
        """
        Add exposition content to tracking
        
        Args:
            exposition_type: Type of exposition (matches ExpositionType enum values)
            content: The exposition content
            source_section: Source section where this exposition appears
            necessity_score: How necessary this exposition is (0-1 scale)
        """
        
        try:
            exp_type = ExpositionType(exposition_type)
        except ValueError:
            exp_type = ExpositionType.CONTEXT_EXPLANATION  # Default
        
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        
        entry = ExpositionEntry(
            exposition_type=exp_type,
            content=content,
            word_count=word_count,
            sentence_count=sentence_count,
            source_section=source_section,
            necessity_score=necessity_score
        )
        
        self.exposition_entries.append(entry)
        
        # Check for budget violations
        if self.budget:
            self._check_budget_violations(entry)
        
        self.logger.debug(f"Added {exp_type.value} exposition: {word_count} words, {sentence_count} sentences")
    
    def add_prose_content(self, prose: str):
        """Add non-exposition prose content for percentage calculations"""
        
        # Auto-detect and categorize exposition in the prose
        self._auto_detect_exposition(prose)
        
        # Update total word count
        self.total_prose_words += len(prose.split())
    
    def is_budget_exceeded(self) -> bool:
        """Check if exposition budget has been exceeded"""
        
        if not self.budget:
            return False
        
        # Check overall percentage limit
        total_exposition_words = sum(entry.word_count for entry in self.exposition_entries)
        if self.total_prose_words > 0:
            exposition_percentage = total_exposition_words / self.total_prose_words
            if exposition_percentage > self.budget.max_exposition_percentage:
                return True
        
        # Check type-specific limits
        if self._check_type_specific_limits():
            return True
        
        return False
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get detailed exposition usage report"""
        
        total_exposition_words = sum(entry.word_count for entry in self.exposition_entries)
        total_exposition_sentences = sum(entry.sentence_count for entry in self.exposition_entries)
        
        # Calculate by type
        usage_by_type = {}
        for exp_type in ExpositionType:
            entries = [e for e in self.exposition_entries if e.exposition_type == exp_type]
            usage_by_type[exp_type.value] = {
                'word_count': sum(e.word_count for e in entries),
                'sentence_count': sum(e.sentence_count for e in entries),
                'entry_count': len(entries)
            }
        
        # Calculate percentages
        exposition_percentage = (total_exposition_words / self.total_prose_words * 100) if self.total_prose_words > 0 else 0
        
        return {
            'total_exposition_words': total_exposition_words,
            'total_exposition_sentences': total_exposition_sentences,
            'total_prose_words': self.total_prose_words,
            'exposition_percentage': exposition_percentage,
            'usage_by_type': usage_by_type,
            'budget_exceeded': self.is_budget_exceeded(),
            'warnings': self.warnings.copy(),
            'budget_limits': {
                'max_percentage': self.budget.max_exposition_percentage * 100 if self.budget else None,
                'max_backstory_sentences': self.budget.max_backstory_sentences if self.budget else None,
                'max_world_building_sentences': self.budget.max_world_building_sentences if self.budget else None
            }
        }
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for reducing exposition if over budget"""
        
        recommendations = []
        
        if not self.is_budget_exceeded():
            return ["Exposition usage is within budget limits."]
        
        # Analyze by type and necessity
        for exp_type in ExpositionType:
            entries = [e for e in self.exposition_entries if e.exposition_type == exp_type]
            if not entries:
                continue
            
            total_words = sum(e.word_count for e in entries)
            avg_necessity = sum(e.necessity_score for e in entries) / len(entries)
            
            if total_words > 50 and avg_necessity < 0.4:  # Low necessity, high word count
                recommendations.append(f"Consider reducing {exp_type.value.replace('_', ' ')} - {total_words} words with low necessity score")
            
            if exp_type == ExpositionType.BACKSTORY and len(entries) > (self.budget.max_backstory_sentences if self.budget else 2):
                recommendations.append("Reduce backstory exposition - consider showing through action instead")
            
            if exp_type == ExpositionType.WORLD_BUILDING and len(entries) > (self.budget.max_world_building_sentences if self.budget else 1):
                recommendations.append("Limit world-building exposition - integrate into dialogue or action")
        
        # General recommendations
        total_exposition = sum(entry.word_count for entry in self.exposition_entries)
        if total_exposition > 0:
            high_exposition_entries = [e for e in self.exposition_entries if e.word_count > 30]
            if high_exposition_entries:
                recommendations.append(f"Break up {len(high_exposition_entries)} long exposition blocks into smaller pieces")
        
        return recommendations if recommendations else ["Consider reducing overall exposition content."]
    
    def _auto_detect_exposition(self, prose: str):
        """Automatically detect exposition in prose using patterns"""
        
        sentences = re.split(r'[.!?]+', prose)
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            detected_types = []
            
            # Check against each exposition type pattern
            for exp_type, patterns in self.exposition_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        detected_types.append(exp_type)
                        break
            
            # If exposition detected, add to tracking
            if detected_types:
                # Use most specific type
                exp_type = detected_types[0]  # Could be enhanced with priority logic
                
                # Calculate necessity score based on patterns
                necessity_score = self._calculate_necessity_score(sentence, exp_type)
                
                # Add to tracking (but don't double-count if already added manually)
                existing_content = [e.content for e in self.exposition_entries]
                if sentence.strip() not in existing_content:
                    self.add_exposition(exp_type.value, sentence.strip(), "auto_detected", necessity_score)
    
    def _calculate_necessity_score(self, sentence: str, exp_type: ExpositionType) -> float:
        """Calculate how necessary this exposition is (simplified heuristic)"""
        
        # Base scores by type
        base_scores = {
            ExpositionType.SCENE_SETUP: 0.8,  # Usually necessary
            ExpositionType.CONTEXT_EXPLANATION: 0.6,
            ExpositionType.CHARACTER_DESCRIPTION: 0.4,
            ExpositionType.SETTING_DESCRIPTION: 0.5,
            ExpositionType.WORLD_BUILDING: 0.3,
            ExpositionType.BACKSTORY: 0.2,  # Often can be shown instead
            ExpositionType.INTERNAL_THOUGHTS: 0.7
        }
        
        base_score = base_scores.get(exp_type, 0.5)
        
        # Adjust based on sentence characteristics
        word_count = len(sentence.split())
        
        # Shorter exposition tends to be more focused/necessary
        if word_count < 10:
            base_score += 0.1
        elif word_count > 25:
            base_score -= 0.2
        
        # Look for action verbs (less exposition-heavy)
        action_verbs = ['moved', 'ran', 'grabbed', 'shouted', 'turned', 'looked']
        if any(verb in sentence.lower() for verb in action_verbs):
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _check_budget_violations(self, new_entry: ExpositionEntry):
        """Check for budget violations with new entry"""
        
        if not self.budget:
            return
        
        # Check type-specific limits
        type_entries = [e for e in self.exposition_entries if e.exposition_type == new_entry.exposition_type]
        
        if new_entry.exposition_type == ExpositionType.BACKSTORY:
            if len(type_entries) > self.budget.max_backstory_sentences:
                self.warnings.append(f"Backstory sentence limit exceeded: {len(type_entries)}/{self.budget.max_backstory_sentences}")
        
        elif new_entry.exposition_type == ExpositionType.WORLD_BUILDING:
            if len(type_entries) > self.budget.max_world_building_sentences:
                self.warnings.append(f"World-building sentence limit exceeded: {len(type_entries)}/{self.budget.max_world_building_sentences}")
        
        # Check overall percentage
        if self.total_prose_words > 0:
            total_exposition_words = sum(entry.word_count for entry in self.exposition_entries)
            exposition_percentage = total_exposition_words / self.total_prose_words
            
            if exposition_percentage > self.budget.max_exposition_percentage:
                self.warnings.append(f"Overall exposition percentage exceeded: {exposition_percentage:.1%}/{self.budget.max_exposition_percentage:.1%}")
    
    def _check_type_specific_limits(self) -> bool:
        """Check if any type-specific limits are exceeded"""
        
        if not self.budget:
            return False
        
        # Count sentences by type
        type_counts = {}
        for entry in self.exposition_entries:
            exp_type = entry.exposition_type
            type_counts[exp_type] = type_counts.get(exp_type, 0) + entry.sentence_count
        
        # Check limits
        if type_counts.get(ExpositionType.BACKSTORY, 0) > self.budget.max_backstory_sentences:
            return True
        
        if type_counts.get(ExpositionType.WORLD_BUILDING, 0) > self.budget.max_world_building_sentences:
            return True
        
        if type_counts.get(ExpositionType.CHARACTER_DESCRIPTION, 0) > self.budget.max_character_description_sentences:
            return True
        
        if type_counts.get(ExpositionType.SETTING_DESCRIPTION, 0) > self.budget.max_setting_description_sentences:
            return True
        
        if type_counts.get(ExpositionType.CONTEXT_EXPLANATION, 0) > self.budget.max_context_explanation_sentences:
            return True
        
        return False
    
    def can_add_exposition(self, exp_type: ExpositionType, word_count: int) -> bool:
        """Check if exposition can be added without exceeding budget"""
        
        if not self.budget:
            return True
        
        # Check type-specific limits
        current_count = len([e for e in self.exposition_entries if e.exposition_type == exp_type])
        
        type_limits = {
            ExpositionType.BACKSTORY: self.budget.max_backstory_sentences,
            ExpositionType.WORLD_BUILDING: self.budget.max_world_building_sentences,
            ExpositionType.CHARACTER_DESCRIPTION: self.budget.max_character_description_sentences,
            ExpositionType.SETTING_DESCRIPTION: self.budget.max_setting_description_sentences,
            ExpositionType.CONTEXT_EXPLANATION: self.budget.max_context_explanation_sentences
        }
        
        limit = type_limits.get(exp_type, 999)  # No limit for other types
        if current_count >= limit:
            return False
        
        # Check overall percentage
        if self.total_prose_words > 0:
            current_exposition_words = sum(entry.word_count for entry in self.exposition_entries)
            projected_total = current_exposition_words + word_count
            projected_percentage = projected_total / (self.total_prose_words + word_count)
            
            if projected_percentage > self.budget.max_exposition_percentage:
                return False
        
        return True