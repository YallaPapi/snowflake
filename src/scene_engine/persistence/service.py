"""
Persistence Service for Scene Engine

This implements subtask 48.3: Prose Storage
Provides high-level persistence operations with specialized prose storage,
versioning, content analysis, and coordinated CRUD operations.
"""

from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime
import hashlib
import re
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from .models import (
    Project, SceneCardDB, ProseContent, ChainLinkDB, Character, 
    SceneSequenceDB, ValidationLog, get_db
)
from .crud import (
    ProjectCRUD, SceneCardCRUD, ChainLinkCRUD, ProseContentCRUD,
    CharacterCRUD, SceneSequenceCRUD, create_crud_manager
)
from ..models import SceneCard, SceneType
from ..chaining.models import ChainLink, ChainSequence


class PersistenceError(Exception):
    """Base exception for persistence operations"""
    pass


class ContentAnalysisError(PersistenceError):
    """Error in content analysis"""
    pass


class VersioningError(PersistenceError):
    """Error in versioning operations"""
    pass


class ProseAnalyzer:
    """Analyzes prose content for metrics and keywords"""
    
    @staticmethod
    def analyze_content(content: str) -> Dict[str, Any]:
        """Perform comprehensive content analysis"""
        
        # Basic metrics
        word_count = len(content.split())
        character_count = len(content)
        reading_time = max(1, word_count // 250)  # 250 WPM average
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', content)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability approximation (Flesch-Kincaid inspired)
        syllable_count = ProseAnalyzer._estimate_syllables(content)
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (syllable_count / word_count)) if word_count > 0 else 0
        readability_score = max(0, min(100, readability_score))  # Clamp to 0-100
        
        # Sentiment analysis (basic keyword approach)
        sentiment_score = ProseAnalyzer._analyze_sentiment(content)
        
        # Extract keywords
        keywords = ProseAnalyzer._extract_keywords(content)
        
        # Dialogue ratio
        dialogue_words = len(re.findall(r'"[^"]*"', content))
        dialogue_ratio = dialogue_words / word_count if word_count > 0 else 0
        
        return {
            "word_count": word_count,
            "character_count": character_count,
            "reading_time_minutes": reading_time,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "readability_score": round(readability_score, 2),
            "sentiment_score": round(sentiment_score, 2),
            "keywords": keywords,
            "dialogue_ratio": round(dialogue_ratio, 2),
            "syllable_estimate": syllable_count
        }
    
    @staticmethod
    def _estimate_syllables(text: str) -> int:
        """Estimate syllable count using simple heuristics"""
        # Remove non-alphabetic characters and convert to lowercase
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = text.split()
        
        total_syllables = 0
        for word in words:
            # Count vowel groups
            syllables = len(re.findall(r'[aeiouy]+', word))
            # Subtract silent 'e' at end
            if word.endswith('e'):
                syllables -= 1
            # Every word has at least one syllable
            syllables = max(1, syllables)
            total_syllables += syllables
            
        return total_syllables
    
    @staticmethod
    def _analyze_sentiment(content: str) -> float:
        """Basic sentiment analysis using keyword matching"""
        positive_words = [
            'happy', 'joy', 'love', 'wonderful', 'amazing', 'great', 'excellent',
            'beautiful', 'perfect', 'fantastic', 'brilliant', 'success', 'win',
            'triumph', 'victory', 'smile', 'laugh', 'delight', 'pleased'
        ]
        
        negative_words = [
            'sad', 'angry', 'hate', 'terrible', 'awful', 'bad', 'horrible',
            'ugly', 'failure', 'lose', 'defeat', 'pain', 'hurt', 'cry',
            'scream', 'fear', 'terror', 'dark', 'death', 'evil'
        ]
        
        words = re.findall(r'\b\w+\b', content.lower())
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.5  # Neutral
        
        # Return sentiment score between 0 (negative) and 1 (positive)
        return positive_count / total_sentiment_words
    
    @staticmethod
    def _extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
        """Extract key terms from content"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'under',
            'over', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should',
            'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'would', 'could', 'should', 'ought',
            'might', 'must', 'may'
        }
        
        # Extract words, filter stop words and short words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]


class ProseVersionManager:
    """Manages prose content versioning"""
    
    def __init__(self, prose_crud: ProseContentCRUD):
        self.prose_crud = prose_crud
    
    def create_version(self, scene_card_id: int, content: str, 
                      version_notes: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> ProseContent:
        """Create a new version of prose content"""
        
        # Analyze content
        analysis = ProseAnalyzer.analyze_content(content)
        
        # Create content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Check if identical content already exists
        existing_versions = self.prose_crud.get_prose_content_versions(scene_card_id)
        for version in existing_versions:
            existing_hash = hashlib.sha256(version.content.encode()).hexdigest()[:16]
            if existing_hash == content_hash:
                raise VersioningError(f"Identical content already exists in version {version.version}")
        
        # Determine version number
        version_number = self._generate_version_number(existing_versions)
        
        # Create prose content with analysis
        prose_metadata = {
            'content_type': metadata.get('content_type', 'markdown') if metadata else 'markdown',
            'version': version_number,
            'version_notes': version_notes,
            'is_current_version': True,
            'readability_score': analysis['readability_score'],
            'sentiment_score': analysis['sentiment_score'],
            'keyword_tags': analysis['keywords']
        }
        
        if metadata:
            prose_metadata.update(metadata)
        
        # Mark previous version as not current
        current_version = self.prose_crud.get_current_prose_content(scene_card_id)
        if current_version:
            self.prose_crud.db.query(ProseContent).filter(
                ProseContent.id == current_version.id
            ).update({'is_current_version': False})
            self.prose_crud.db.commit()
        
        return self.prose_crud.create_prose_content(
            scene_card_id=scene_card_id,
            content=content,
            metadata=prose_metadata
        )
    
    def rollback_to_version(self, scene_card_id: int, target_version: str) -> ProseContent:
        """Rollback to a specific version"""
        
        # Find target version
        versions = self.prose_crud.get_prose_content_versions(scene_card_id)
        target_prose = None
        
        for version in versions:
            if version.version == target_version:
                target_prose = version
                break
        
        if not target_prose:
            raise VersioningError(f"Version {target_version} not found")
        
        # Create new version from target content
        rollback_notes = f"Rollback to version {target_version}"
        return self.create_version(
            scene_card_id=scene_card_id,
            content=target_prose.content,
            version_notes=rollback_notes
        )
    
    def compare_versions(self, scene_card_id: int, version_a: str, version_b: str) -> Dict[str, Any]:
        """Compare two versions of prose content"""
        
        versions = self.prose_crud.get_prose_content_versions(scene_card_id)
        prose_a = prose_b = None
        
        for version in versions:
            if version.version == version_a:
                prose_a = version
            elif version.version == version_b:
                prose_b = version
        
        if not prose_a or not prose_b:
            raise VersioningError("One or both versions not found")
        
        # Calculate differences
        words_a = prose_a.content.split()
        words_b = prose_b.content.split()
        
        word_diff = len(words_b) - len(words_a)
        char_diff = len(prose_b.content) - len(prose_a.content)
        
        return {
            "version_a": version_a,
            "version_b": version_b,
            "word_count_change": word_diff,
            "character_count_change": char_diff,
            "readability_change": prose_b.readability_score - prose_a.readability_score if prose_b.readability_score and prose_a.readability_score else None,
            "sentiment_change": prose_b.sentiment_score - prose_a.sentiment_score if prose_b.sentiment_score and prose_a.sentiment_score else None,
            "content_similarity": self._calculate_similarity(prose_a.content, prose_b.content)
        }
    
    def _generate_version_number(self, existing_versions: List[ProseContent]) -> str:
        """Generate next version number"""
        if not existing_versions:
            return "1.0.0"
        
        # Find highest version
        max_major = 0
        max_minor = 0
        max_patch = 0
        
        for version in existing_versions:
            try:
                parts = version.version.split('.')
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                patch = int(parts[2]) if len(parts) > 2 else 0
                
                if major > max_major or (major == max_major and minor > max_minor) or \
                   (major == max_major and minor == max_minor and patch > max_patch):
                    max_major, max_minor, max_patch = major, minor, patch
            except (ValueError, IndexError):
                continue
        
        # Increment minor version
        return f"{max_major}.{max_minor + 1}.0"
    
    def _calculate_similarity(self, content_a: str, content_b: str) -> float:
        """Calculate content similarity using simple word overlap"""
        words_a = set(content_a.lower().split())
        words_b = set(content_b.lower().split())
        
        if not words_a and not words_b:
            return 1.0
        
        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)
        
        return len(intersection) / len(union) if union else 0.0


class PersistenceService:
    """High-level persistence service coordinating all CRUD operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or next(get_db())
        self.crud = create_crud_manager(self.db)
        self.version_manager = ProseVersionManager(self.crud['prose_content'])
    
    # Project operations
    def create_project(self, title: str, description: str = "", 
                      author: str = "", genre: str = "",
                      target_word_count: int = 80000,
                      settings: Optional[Dict[str, Any]] = None) -> Project:
        """Create new project with default settings"""
        
        project_id = f"project_{int(datetime.utcnow().timestamp())}"
        project_data = {
            'project_id': project_id,
            'title': title,
            'description': description,
            'author': author,
            'genre': genre,
            'target_word_count': target_word_count,
            'settings': settings or {}
        }
        
        return self.crud['projects'].create_project(project_data)
    
    def get_project_summary(self, project_id: Union[int, str]) -> Dict[str, Any]:
        """Get comprehensive project summary with statistics"""
        project = self.crud['projects'].get_project(project_id)
        if not project:
            raise PersistenceError(f"Project not found: {project_id}")
        
        # Get scene statistics
        scene_stats = self.crud['scene_cards'].get_scene_card_statistics(project.id)
        
        # Get character count
        characters = self.crud['characters'].get_characters(project.id)
        
        # Get sequences count
        sequences = self.crud['sequences'].get_sequences(project.id)
        
        # Get chain links count
        chain_links = self.crud['chain_links'].get_chain_links(project.id)
        
        return {
            "project": {
                "id": project.id,
                "project_id": project.project_id,
                "title": project.title,
                "author": project.author,
                "genre": project.genre,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            },
            "statistics": {
                **scene_stats,
                "character_count": len(characters),
                "sequence_count": len(sequences),
                "chain_link_count": len(chain_links),
                "target_word_count": project.target_word_count,
                "completion_percentage": (scene_stats['total_word_count'] / project.target_word_count * 100) if project.target_word_count > 0 else 0
            }
        }
    
    # Scene Card operations with enhanced features
    def create_scene_card_with_prose(self, project_id: int, scene_card: SceneCard, 
                                   prose_content: Optional[str] = None,
                                   prose_notes: Optional[str] = None) -> Tuple[SceneCardDB, Optional[ProseContent]]:
        """Create scene card with optional initial prose content"""
        
        # Create scene card
        db_scene_card = self.crud['scene_cards'].create_scene_card(project_id, scene_card)
        
        prose_content_obj = None
        if prose_content:
            # Create initial prose version
            prose_content_obj = self.version_manager.create_version(
                scene_card_id=db_scene_card.id,
                content=prose_content,
                version_notes=prose_notes or "Initial version"
            )
            
            # Update scene card word count
            db_scene_card.word_count = prose_content_obj.word_count
            db_scene_card.estimated_reading_time = prose_content_obj.reading_time_minutes
            self.db.commit()
        
        return db_scene_card, prose_content_obj
    
    def update_scene_prose(self, scene_id: Union[int, str], content: str,
                          version_notes: Optional[str] = None,
                          project_id: Optional[int] = None) -> ProseContent:
        """Update scene prose content with versioning"""
        
        # Get scene card
        scene_card = self.crud['scene_cards'].get_scene_card(scene_id, project_id)
        if not scene_card:
            raise PersistenceError(f"Scene card not found: {scene_id}")
        
        # Create new version
        prose_content = self.version_manager.create_version(
            scene_card_id=scene_card.id,
            content=content,
            version_notes=version_notes or "Content update"
        )
        
        # Update scene card metadata
        scene_card.word_count = prose_content.word_count
        scene_card.estimated_reading_time = prose_content.reading_time_minutes
        scene_card.updated_at = datetime.utcnow()
        self.db.commit()
        
        return prose_content
    
    def get_scene_with_prose(self, scene_id: Union[int, str], 
                           project_id: Optional[int] = None,
                           version: Optional[str] = None) -> Dict[str, Any]:
        """Get scene card with current or specific prose version"""
        
        scene_card = self.crud['scene_cards'].get_scene_card(scene_id, project_id)
        if not scene_card:
            raise PersistenceError(f"Scene card not found: {scene_id}")
        
        # Get prose content
        if version:
            prose_versions = self.crud['prose_content'].get_prose_content_versions(scene_card.id)
            prose_content = next((v for v in prose_versions if v.version == version), None)
        else:
            prose_content = self.crud['prose_content'].get_current_prose_content(scene_card.id)
        
        # Convert to Pydantic model
        pydantic_scene = self.crud['scene_cards'].db_to_pydantic(scene_card)
        
        return {
            "scene_card": pydantic_scene,
            "prose_content": {
                "content": prose_content.content if prose_content else "",
                "word_count": prose_content.word_count if prose_content else 0,
                "version": prose_content.version if prose_content else None,
                "version_notes": prose_content.version_notes if prose_content else None,
                "readability_score": prose_content.readability_score if prose_content else None,
                "sentiment_score": prose_content.sentiment_score if prose_content else None,
                "keywords": prose_content.keyword_tags if prose_content else [],
                "created_at": prose_content.created_at if prose_content else None
            } if prose_content else None
        }
    
    # Advanced query operations
    def search_scenes_by_content(self, project_id: int, query: str, 
                                include_prose: bool = True) -> List[Dict[str, Any]]:
        """Search scenes by content in scene cards and optionally prose"""
        
        results = []
        
        # Search scene cards
        scene_results = self.crud['scene_cards'].search_scene_cards(
            project_id=project_id,
            search_term=query,
            search_fields=['scene_crucible', 'place', 'time', 'pov']
        )
        
        for scene in scene_results:
            scene_data = {
                'scene_card': self.crud['scene_cards'].db_to_pydantic(scene),
                'match_type': 'scene_metadata'
            }
            
            if include_prose:
                prose_content = self.crud['prose_content'].get_current_prose_content(scene.id)
                if prose_content:
                    scene_data['prose_content'] = prose_content
            
            results.append(scene_data)
        
        # Search prose content if requested
        if include_prose:
            prose_matches = self.db.query(ProseContent).join(SceneCardDB).filter(
                and_(
                    SceneCardDB.project_id == project_id,
                    ProseContent.content.contains(query),
                    ProseContent.is_current_version == True
                )
            ).all()
            
            for prose in prose_matches:
                # Check if not already included from scene search
                scene_in_results = any(r['scene_card'].scene_id == prose.scene_card.scene_id 
                                     for r in results if 'scene_card' in r)
                
                if not scene_in_results:
                    results.append({
                        'scene_card': self.crud['scene_cards'].db_to_pydantic(prose.scene_card),
                        'prose_content': prose,
                        'match_type': 'prose_content'
                    })
        
        return results
    
    def get_scenes_by_narrative_flow(self, project_id: int, start_scene_id: str, 
                                   depth: int = 5) -> List[Dict[str, Any]]:
        """Get scenes following narrative flow from a starting point"""
        
        flow_scenes = []
        current_scene_id = start_scene_id
        visited_scenes = set()
        
        for _ in range(depth):
            if current_scene_id in visited_scenes:
                break
                
            # Get current scene
            scene_card = self.crud['scene_cards'].get_scene_card(current_scene_id, project_id)
            if not scene_card:
                break
            
            # Get prose content
            prose_content = self.crud['prose_content'].get_current_prose_content(scene_card.id)
            
            # Find outgoing chain links
            chain_links = self.crud['chain_links'].get_chain_links_for_scene(project_id, current_scene_id)
            
            flow_scenes.append({
                'scene_card': self.crud['scene_cards'].db_to_pydantic(scene_card),
                'prose_content': prose_content,
                'outgoing_links': len(chain_links)
            })
            
            visited_scenes.add(current_scene_id)
            
            # Follow strongest chain link
            if chain_links:
                strongest_link = max(chain_links, 
                                   key=lambda link: link.validation_score or 0)
                current_scene_id = strongest_link.target_scene_id
            else:
                break
        
        return flow_scenes
    
    def get_project_health_report(self, project_id: Union[int, str]) -> Dict[str, Any]:
        """Generate comprehensive project health report"""
        
        project = self.crud['projects'].get_project(project_id)
        if not project:
            raise PersistenceError(f"Project not found: {project_id}")
        
        # Scene analysis
        scenes = self.crud['scene_cards'].get_scene_cards(project.id)
        total_scenes = len(scenes)
        scenes_with_prose = sum(1 for scene in scenes 
                               if self.crud['prose_content'].get_current_prose_content(scene.id))
        
        # Chain link analysis
        chain_links = self.crud['chain_links'].get_chain_links(project.id)
        valid_links = sum(1 for link in chain_links if link.is_valid)
        
        # Character analysis
        characters = self.crud['characters'].get_characters(project.id)
        
        # Prose quality analysis
        all_prose = []
        total_readability = 0
        total_sentiment = 0
        prose_count = 0
        
        for scene in scenes:
            prose = self.crud['prose_content'].get_current_prose_content(scene.id)
            if prose:
                all_prose.append(prose)
                if prose.readability_score:
                    total_readability += prose.readability_score
                    prose_count += 1
                if prose.sentiment_score:
                    total_sentiment += prose.sentiment_score
        
        avg_readability = total_readability / prose_count if prose_count > 0 else 0
        avg_sentiment = total_sentiment / prose_count if prose_count > 0 else 0
        
        # Calculate health score
        prose_completion = scenes_with_prose / total_scenes if total_scenes > 0 else 0
        link_validity = valid_links / len(chain_links) if chain_links else 0
        character_density = min(len(characters) / 10, 1.0)  # Assume 10 is good character count
        
        health_score = (prose_completion * 0.4 + link_validity * 0.3 + character_density * 0.3) * 100
        
        return {
            "project_id": project.project_id,
            "health_score": round(health_score, 2),
            "scene_analysis": {
                "total_scenes": total_scenes,
                "scenes_with_prose": scenes_with_prose,
                "prose_completion_percentage": round(prose_completion * 100, 2)
            },
            "chain_analysis": {
                "total_links": len(chain_links),
                "valid_links": valid_links,
                "validity_percentage": round(link_validity * 100, 2) if chain_links else 0
            },
            "character_analysis": {
                "total_characters": len(characters),
                "character_density_score": round(character_density * 100, 2)
            },
            "prose_quality": {
                "average_readability": round(avg_readability, 2),
                "average_sentiment": round(avg_sentiment, 2),
                "total_word_count": sum(prose.word_count for prose in all_prose)
            },
            "recommendations": self._generate_health_recommendations(
                prose_completion, link_validity, character_density, avg_readability
            )
        }
    
    def _generate_health_recommendations(self, prose_completion: float, 
                                       link_validity: float, character_density: float,
                                       avg_readability: float) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if prose_completion < 0.5:
            recommendations.append("Focus on writing prose content for more scenes")
        
        if link_validity < 0.7:
            recommendations.append("Review and fix invalid chain links between scenes")
        
        if character_density < 0.3:
            recommendations.append("Consider developing more characters for story richness")
        
        if avg_readability < 30:
            recommendations.append("Consider simplifying sentence structure for better readability")
        elif avg_readability > 80:
            recommendations.append("Consider adding complexity to prose for sophistication")
        
        if not recommendations:
            recommendations.append("Project health looks excellent! Continue current workflow")
        
        return recommendations
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()