"""
Query Interface for Scene Engine Persistence

This implements subtask 48.4: Query Interface
Provides flexible, composable query interface for complex scene retrieval,
filtering, aggregation, and reporting operations.
"""

from typing import List, Optional, Dict, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, not_, desc, asc, func, case, text
from sqlalchemy.sql import extract

from .models import (
    Project, SceneCardDB, ProseContent, ChainLinkDB, Character,
    SceneSequenceDB, ValidationLog, SceneTypeEnum, ViewpointTypeEnum,
    TenseTypeEnum, ChainLinkTypeEnum, get_db
)
from ..models import SceneType, ViewpointType, TenseType


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class AggregateFunction(Enum):
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"


@dataclass
class QueryFilter:
    """Represents a query filter condition"""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, like, ilike, in, not_in, is_null, is_not_null
    value: Any
    
    def __post_init__(self):
        valid_operators = [
            'eq', 'ne', 'gt', 'gte', 'lt', 'lte', 
            'like', 'ilike', 'in', 'not_in', 'is_null', 'is_not_null'
        ]
        if self.operator not in valid_operators:
            raise ValueError(f"Invalid operator: {self.operator}. Must be one of {valid_operators}")


@dataclass
class QuerySort:
    """Represents a query sort condition"""
    field: str
    direction: SortDirection = SortDirection.ASC


@dataclass
class QueryAggregate:
    """Represents an aggregation operation"""
    function: AggregateFunction
    field: str
    alias: str


class QueryError(Exception):
    """Base exception for query operations"""
    pass


class SceneCardQueryBuilder:
    """Builder for scene card queries"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.query = self.db.query(SceneCardDB)
        self.joins_applied = set()
        self.filters = []
        self.sorts = []
        self.limit_value = None
        self.offset_value = None
        self.group_by_fields = []
        self.having_filters = []
    
    def filter_by_project(self, project_id: int) -> 'SceneCardQueryBuilder':
        """Filter scenes by project"""
        self.query = self.query.filter(SceneCardDB.project_id == project_id)
        return self
    
    def filter_by_type(self, scene_type: Union[SceneType, List[SceneType]]) -> 'SceneCardQueryBuilder':
        """Filter scenes by type(s)"""
        if isinstance(scene_type, list):
            enum_types = [SceneTypeEnum(st.value) for st in scene_type]
            self.query = self.query.filter(SceneCardDB.scene_type.in_(enum_types))
        else:
            self.query = self.query.filter(SceneCardDB.scene_type == SceneTypeEnum(scene_type.value))
        return self
    
    def filter_by_pov(self, pov: Union[str, List[str]]) -> 'SceneCardQueryBuilder':
        """Filter scenes by POV character(s)"""
        if isinstance(pov, list):
            self.query = self.query.filter(SceneCardDB.pov.in_(pov))
        else:
            self.query = self.query.filter(SceneCardDB.pov == pov)
        return self
    
    def filter_by_status(self, status: Union[str, List[str]]) -> 'SceneCardQueryBuilder':
        """Filter scenes by status"""
        if isinstance(status, list):
            self.query = self.query.filter(SceneCardDB.status.in_(status))
        else:
            self.query = self.query.filter(SceneCardDB.status == status)
        return self
    
    def filter_by_chapter(self, chapter_number: Union[int, List[int]]) -> 'SceneCardQueryBuilder':
        """Filter scenes by chapter number(s)"""
        if isinstance(chapter_number, list):
            self.query = self.query.filter(SceneCardDB.chapter_number.in_(chapter_number))
        else:
            self.query = self.query.filter(SceneCardDB.chapter_number == chapter_number)
        return self
    
    def filter_by_word_count(self, min_words: Optional[int] = None, 
                           max_words: Optional[int] = None) -> 'SceneCardQueryBuilder':
        """Filter scenes by word count range"""
        if min_words is not None:
            self.query = self.query.filter(SceneCardDB.word_count >= min_words)
        if max_words is not None:
            self.query = self.query.filter(SceneCardDB.word_count <= max_words)
        return self
    
    def filter_by_quality_score(self, min_score: Optional[float] = None,
                              max_score: Optional[float] = None) -> 'SceneCardQueryBuilder':
        """Filter scenes by quality score range"""
        if min_score is not None:
            self.query = self.query.filter(SceneCardDB.quality_score >= min_score)
        if max_score is not None:
            self.query = self.query.filter(SceneCardDB.quality_score <= max_score)
        return self
    
    def filter_by_date_range(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           date_field: str = "created_at") -> 'SceneCardQueryBuilder':
        """Filter scenes by date range"""
        field = getattr(SceneCardDB, date_field)
        if start_date:
            self.query = self.query.filter(field >= start_date)
        if end_date:
            self.query = self.query.filter(field <= end_date)
        return self
    
    def search_content(self, search_term: str, 
                      fields: Optional[List[str]] = None) -> 'SceneCardQueryBuilder':
        """Search within scene content fields"""
        if fields is None:
            fields = ['scene_crucible', 'place', 'time']
        
        conditions = []
        for field in fields:
            if hasattr(SceneCardDB, field):
                field_attr = getattr(SceneCardDB, field)
                conditions.append(field_attr.ilike(f'%{search_term}%'))
        
        if conditions:
            self.query = self.query.filter(or_(*conditions))
        return self
    
    def join_prose(self) -> 'SceneCardQueryBuilder':
        """Join with prose content"""
        if 'prose' not in self.joins_applied:
            self.query = self.query.outerjoin(ProseContent)
            self.joins_applied.add('prose')
        return self
    
    def join_project(self) -> 'SceneCardQueryBuilder':
        """Join with project"""
        if 'project' not in self.joins_applied:
            self.query = self.query.join(Project)
            self.joins_applied.add('project')
        return self
    
    def filter_by_prose_content(self, search_term: str) -> 'SceneCardQueryBuilder':
        """Filter by prose content"""
        self.join_prose()
        self.query = self.query.filter(
            and_(
                ProseContent.content.ilike(f'%{search_term}%'),
                ProseContent.is_current_version == True
            )
        )
        return self
    
    def filter_by_readability_score(self, min_score: Optional[float] = None,
                                  max_score: Optional[float] = None) -> 'SceneCardQueryBuilder':
        """Filter by prose readability score"""
        self.join_prose()
        if min_score is not None:
            self.query = self.query.filter(ProseContent.readability_score >= min_score)
        if max_score is not None:
            self.query = self.query.filter(ProseContent.readability_score <= max_score)
        return self
    
    def order_by(self, field: str, direction: SortDirection = SortDirection.ASC) -> 'SceneCardQueryBuilder':
        """Add ordering to query"""
        if hasattr(SceneCardDB, field):
            field_attr = getattr(SceneCardDB, field)
            if direction == SortDirection.DESC:
                self.query = self.query.order_by(desc(field_attr))
            else:
                self.query = self.query.order_by(asc(field_attr))
        return self
    
    def limit(self, limit: int) -> 'SceneCardQueryBuilder':
        """Add limit to query"""
        self.limit_value = limit
        return self
    
    def offset(self, offset: int) -> 'SceneCardQueryBuilder':
        """Add offset to query"""
        self.offset_value = offset
        return self
    
    def paginate(self, page: int, per_page: int = 20) -> 'SceneCardQueryBuilder':
        """Add pagination to query"""
        self.limit_value = per_page
        self.offset_value = (page - 1) * per_page
        return self
    
    def execute(self) -> List[SceneCardDB]:
        """Execute the query and return results"""
        query = self.query
        
        if self.limit_value:
            query = query.limit(self.limit_value)
        if self.offset_value:
            query = query.offset(self.offset_value)
        
        return query.all()
    
    def count(self) -> int:
        """Get count of matching records"""
        return self.query.count()
    
    def first(self) -> Optional[SceneCardDB]:
        """Get first matching record"""
        return self.query.first()
    
    def exists(self) -> bool:
        """Check if any matching records exist"""
        return self.db.query(self.query.exists()).scalar()


class ChainLinkQueryBuilder:
    """Builder for chain link queries"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.query = self.db.query(ChainLinkDB)
    
    def filter_by_project(self, project_id: int) -> 'ChainLinkQueryBuilder':
        """Filter chain links by project"""
        self.query = self.query.filter(ChainLinkDB.project_id == project_id)
        return self
    
    def filter_by_type(self, chain_type: Union[str, List[str]]) -> 'ChainLinkQueryBuilder':
        """Filter chain links by type"""
        if isinstance(chain_type, list):
            enum_types = [ChainLinkTypeEnum(ct) for ct in chain_type]
            self.query = self.query.filter(ChainLinkDB.chain_type.in_(enum_types))
        else:
            self.query = self.query.filter(ChainLinkDB.chain_type == ChainLinkTypeEnum(chain_type))
        return self
    
    def filter_by_source_scene(self, scene_id: Union[str, List[str]]) -> 'ChainLinkQueryBuilder':
        """Filter by source scene ID(s)"""
        if isinstance(scene_id, list):
            self.query = self.query.filter(ChainLinkDB.source_scene_id.in_(scene_id))
        else:
            self.query = self.query.filter(ChainLinkDB.source_scene_id == scene_id)
        return self
    
    def filter_by_target_scene(self, scene_id: Union[str, List[str]]) -> 'ChainLinkQueryBuilder':
        """Filter by target scene ID(s)"""
        if isinstance(scene_id, list):
            self.query = self.query.filter(ChainLinkDB.target_scene_id.in_(scene_id))
        else:
            self.query = self.query.filter(ChainLinkDB.target_scene_id == scene_id)
        return self
    
    def filter_by_validity(self, is_valid: bool) -> 'ChainLinkQueryBuilder':
        """Filter by validity status"""
        self.query = self.query.filter(ChainLinkDB.is_valid == is_valid)
        return self
    
    def filter_by_validation_score(self, min_score: Optional[float] = None,
                                 max_score: Optional[float] = None) -> 'ChainLinkQueryBuilder':
        """Filter by validation score range"""
        if min_score is not None:
            self.query = self.query.filter(ChainLinkDB.validation_score >= min_score)
        if max_score is not None:
            self.query = self.query.filter(ChainLinkDB.validation_score <= max_score)
        return self
    
    def order_by(self, field: str, direction: SortDirection = SortDirection.ASC) -> 'ChainLinkQueryBuilder':
        """Add ordering to query"""
        if hasattr(ChainLinkDB, field):
            field_attr = getattr(ChainLinkDB, field)
            if direction == SortDirection.DESC:
                self.query = self.query.order_by(desc(field_attr))
            else:
                self.query = self.query.order_by(asc(field_attr))
        return self
    
    def execute(self) -> List[ChainLinkDB]:
        """Execute the query"""
        return self.query.all()
    
    def count(self) -> int:
        """Get count of matching records"""
        return self.query.count()


class AggregationQueryBuilder:
    """Builder for aggregation queries"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def scene_statistics_by_project(self, project_id: int) -> Dict[str, Any]:
        """Get comprehensive scene statistics for a project"""
        
        # Basic counts
        total_scenes = self.db.query(func.count(SceneCardDB.id)).filter(
            SceneCardDB.project_id == project_id
        ).scalar()
        
        # Scene type breakdown
        type_counts = self.db.query(
            SceneCardDB.scene_type,
            func.count(SceneCardDB.id).label('count')
        ).filter(
            SceneCardDB.project_id == project_id
        ).group_by(SceneCardDB.scene_type).all()
        
        # POV breakdown
        pov_counts = self.db.query(
            SceneCardDB.pov,
            func.count(SceneCardDB.id).label('count')
        ).filter(
            SceneCardDB.project_id == project_id
        ).group_by(SceneCardDB.pov).order_by(desc('count')).all()
        
        # Status breakdown
        status_counts = self.db.query(
            SceneCardDB.status,
            func.count(SceneCardDB.id).label('count')
        ).filter(
            SceneCardDB.project_id == project_id
        ).group_by(SceneCardDB.status).all()
        
        # Word count statistics
        word_stats = self.db.query(
            func.sum(SceneCardDB.word_count).label('total_words'),
            func.avg(SceneCardDB.word_count).label('avg_words'),
            func.min(SceneCardDB.word_count).label('min_words'),
            func.max(SceneCardDB.word_count).label('max_words')
        ).filter(SceneCardDB.project_id == project_id).first()
        
        # Quality score statistics
        quality_stats = self.db.query(
            func.avg(SceneCardDB.quality_score).label('avg_quality'),
            func.min(SceneCardDB.quality_score).label('min_quality'),
            func.max(SceneCardDB.quality_score).label('max_quality')
        ).filter(SceneCardDB.project_id == project_id).first()
        
        return {
            'total_scenes': total_scenes,
            'scene_types': {str(type_enum.value): count for type_enum, count in type_counts},
            'pov_distribution': {pov: count for pov, count in pov_counts},
            'status_distribution': {status: count for status, count in status_counts},
            'word_count_stats': {
                'total': int(word_stats.total_words or 0),
                'average': round(float(word_stats.avg_words or 0), 2),
                'minimum': int(word_stats.min_words or 0),
                'maximum': int(word_stats.max_words or 0)
            },
            'quality_stats': {
                'average': round(float(quality_stats.avg_quality or 0), 2),
                'minimum': round(float(quality_stats.min_quality or 0), 2),
                'maximum': round(float(quality_stats.max_quality or 0), 2)
            }
        }
    
    def prose_analytics_by_project(self, project_id: int) -> Dict[str, Any]:
        """Get prose content analytics for a project"""
        
        # Join prose content with scene cards
        query_base = self.db.query(ProseContent).join(SceneCardDB).filter(
            and_(
                SceneCardDB.project_id == project_id,
                ProseContent.is_current_version == True
            )
        )
        
        # Basic prose statistics
        prose_stats = query_base.with_entities(
            func.count(ProseContent.id).label('total_prose_scenes'),
            func.sum(ProseContent.word_count).label('total_prose_words'),
            func.avg(ProseContent.word_count).label('avg_prose_words'),
            func.avg(ProseContent.readability_score).label('avg_readability'),
            func.avg(ProseContent.sentiment_score).label('avg_sentiment')
        ).first()
        
        # Readability distribution
        readability_ranges = [
            (0, 30, 'difficult'),
            (30, 50, 'fairly_difficult'),
            (50, 60, 'standard'),
            (60, 70, 'fairly_easy'),
            (70, 80, 'easy'),
            (80, 100, 'very_easy')
        ]
        
        readability_dist = {}
        for min_score, max_score, label in readability_ranges:
            count = query_base.filter(
                and_(
                    ProseContent.readability_score >= min_score,
                    ProseContent.readability_score < max_score
                )
            ).count()
            readability_dist[label] = count
        
        return {
            'total_prose_scenes': int(prose_stats.total_prose_scenes or 0),
            'total_prose_words': int(prose_stats.total_prose_words or 0),
            'average_scene_words': round(float(prose_stats.avg_prose_words or 0), 2),
            'average_readability': round(float(prose_stats.avg_readability or 0), 2),
            'average_sentiment': round(float(prose_stats.avg_sentiment or 0), 2),
            'readability_distribution': readability_dist
        }
    
    def chain_link_analytics_by_project(self, project_id: int) -> Dict[str, Any]:
        """Get chain link analytics for a project"""
        
        # Basic chain link statistics
        total_links = self.db.query(func.count(ChainLinkDB.id)).filter(
            ChainLinkDB.project_id == project_id
        ).scalar()
        
        valid_links = self.db.query(func.count(ChainLinkDB.id)).filter(
            and_(
                ChainLinkDB.project_id == project_id,
                ChainLinkDB.is_valid == True
            )
        ).scalar()
        
        # Chain type distribution
        type_counts = self.db.query(
            ChainLinkDB.chain_type,
            func.count(ChainLinkDB.id).label('count')
        ).filter(
            ChainLinkDB.project_id == project_id
        ).group_by(ChainLinkDB.chain_type).all()
        
        # Validation score statistics
        validation_stats = self.db.query(
            func.avg(ChainLinkDB.validation_score).label('avg_score'),
            func.min(ChainLinkDB.validation_score).label('min_score'),
            func.max(ChainLinkDB.validation_score).label('max_score')
        ).filter(ChainLinkDB.project_id == project_id).first()
        
        return {
            'total_chain_links': total_links,
            'valid_chain_links': valid_links,
            'validity_percentage': round((valid_links / total_links * 100) if total_links > 0 else 0, 2),
            'chain_type_distribution': {str(type_enum.value): count for type_enum, count in type_counts},
            'validation_score_stats': {
                'average': round(float(validation_stats.avg_score or 0), 2),
                'minimum': round(float(validation_stats.min_score or 0), 2),
                'maximum': round(float(validation_stats.max_score or 0), 2)
            }
        }
    
    def timeline_analytics(self, project_id: int, days: int = 30) -> Dict[str, Any]:
        """Get timeline analytics for project activity"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Scene creation timeline
        scene_timeline = self.db.query(
            func.date(SceneCardDB.created_at).label('date'),
            func.count(SceneCardDB.id).label('scenes_created')
        ).filter(
            and_(
                SceneCardDB.project_id == project_id,
                SceneCardDB.created_at >= cutoff_date
            )
        ).group_by(func.date(SceneCardDB.created_at)).all()
        
        # Prose update timeline
        prose_timeline = self.db.query(
            func.date(ProseContent.created_at).label('date'),
            func.count(ProseContent.id).label('prose_updates')
        ).join(SceneCardDB).filter(
            and_(
                SceneCardDB.project_id == project_id,
                ProseContent.created_at >= cutoff_date
            )
        ).group_by(func.date(ProseContent.created_at)).all()
        
        return {
            'period_days': days,
            'scene_creation_timeline': [
                {'date': str(date), 'count': count} 
                for date, count in scene_timeline
            ],
            'prose_update_timeline': [
                {'date': str(date), 'count': count}
                for date, count in prose_timeline
            ]
        }


class QueryInterface:
    """Main query interface providing all query capabilities"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or next(get_db())
        self.aggregator = AggregationQueryBuilder(self.db)
    
    def scene_cards(self) -> SceneCardQueryBuilder:
        """Get scene card query builder"""
        return SceneCardQueryBuilder(self.db)
    
    def chain_links(self) -> ChainLinkQueryBuilder:
        """Get chain link query builder"""
        return ChainLinkQueryBuilder(self.db)
    
    def aggregate(self) -> AggregationQueryBuilder:
        """Get aggregation query builder"""
        return self.aggregator
    
    def advanced_search(self, project_id: int, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced multi-entity search"""
        results = {
            'scene_cards': [],
            'prose_matches': [],
            'chain_links': [],
            'characters': []
        }
        
        search_term = search_params.get('query', '')
        include_prose = search_params.get('include_prose', True)
        include_chains = search_params.get('include_chains', True)
        
        if search_term:
            # Search scene cards
            scene_query = self.scene_cards().filter_by_project(project_id)
            scene_results = scene_query.search_content(search_term).execute()
            results['scene_cards'] = [
                {
                    'id': scene.id,
                    'scene_id': scene.scene_id,
                    'scene_type': scene.scene_type.value,
                    'pov': scene.pov,
                    'scene_crucible': scene.scene_crucible
                }
                for scene in scene_results
            ]
            
            # Search prose content if requested
            if include_prose:
                prose_matches = self.db.query(ProseContent).join(SceneCardDB).filter(
                    and_(
                        SceneCardDB.project_id == project_id,
                        ProseContent.content.ilike(f'%{search_term}%'),
                        ProseContent.is_current_version == True
                    )
                ).all()
                
                results['prose_matches'] = [
                    {
                        'scene_id': prose.scene_card.scene_id,
                        'word_count': prose.word_count,
                        'match_context': self._extract_context(prose.content, search_term)
                    }
                    for prose in prose_matches
                ]
            
            # Search chain links if requested
            if include_chains:
                chain_matches = self.db.query(ChainLinkDB).filter(
                    and_(
                        ChainLinkDB.project_id == project_id,
                        or_(
                            ChainLinkDB.trigger_content.ilike(f'%{search_term}%'),
                            ChainLinkDB.target_seed.ilike(f'%{search_term}%'),
                            ChainLinkDB.bridging_content.ilike(f'%{search_term}%')
                        )
                    )
                ).all()
                
                results['chain_links'] = [
                    {
                        'chain_id': chain.chain_id,
                        'chain_type': chain.chain_type.value,
                        'source_scene_id': chain.source_scene_id,
                        'target_scene_id': chain.target_scene_id
                    }
                    for chain in chain_matches
                ]
        
        return results
    
    def export_query_results(self, query_builder: Union[SceneCardQueryBuilder, ChainLinkQueryBuilder],
                           format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export query results in specified format"""
        results = query_builder.execute()
        
        if format == "json":
            if isinstance(query_builder, SceneCardQueryBuilder):
                return {
                    "scenes": [
                        {
                            "id": scene.id,
                            "scene_id": scene.scene_id,
                            "scene_type": scene.scene_type.value,
                            "pov": scene.pov,
                            "scene_crucible": scene.scene_crucible,
                            "word_count": scene.word_count,
                            "status": scene.status,
                            "created_at": scene.created_at.isoformat()
                        }
                        for scene in results
                    ]
                }
            elif isinstance(query_builder, ChainLinkQueryBuilder):
                return {
                    "chain_links": [
                        {
                            "id": link.id,
                            "chain_id": link.chain_id,
                            "chain_type": link.chain_type.value,
                            "source_scene_id": link.source_scene_id,
                            "target_scene_id": link.target_scene_id,
                            "is_valid": link.is_valid,
                            "validation_score": link.validation_score
                        }
                        for link in results
                    ]
                }
        
        elif format == "csv":
            # Return CSV string (implementation depends on requirements)
            pass
        
        return results
    
    def _extract_context(self, content: str, search_term: str, context_length: int = 100) -> str:
        """Extract context around search term"""
        lower_content = content.lower()
        lower_term = search_term.lower()
        
        index = lower_content.find(lower_term)
        if index == -1:
            return ""
        
        start = max(0, index - context_length // 2)
        end = min(len(content), index + len(search_term) + context_length // 2)
        
        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context
    
    def close(self):
        """Close database session"""
        if self.db:
            self.db.close()