"""
CRUD Operations for Scene Engine Persistence

This implements subtask 48.2: Implement CRUD Operations for Scene Cards
and provides CRUD operations for all persistence models.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .models import (
    Project, SceneCardDB, ProseContent, ChainLinkDB, 
    Character, SceneSequenceDB, ValidationLog,
    SceneTypeEnum, ViewpointTypeEnum, TenseTypeEnum,
    OutcomeTypeEnum, CompressionTypeEnum, ChainLinkTypeEnum
)
from ..models import SceneCard, SceneType, ViewpointType, TenseType
from ..chaining.models import ChainLink, ChainSequence


class CRUDError(Exception):
    """Base exception for CRUD operations"""
    pass


class SceneNotFoundError(CRUDError):
    """Scene card not found"""
    pass


class ChainLinkNotFoundError(CRUDError):
    """Chain link not found"""
    pass


class ValidationError(CRUDError):
    """Validation error in CRUD operation"""
    pass


class BaseCRUD:
    """Base CRUD operations class"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def _handle_db_error(self, operation: str, error: Exception):
        """Handle database errors with appropriate exceptions"""
        if isinstance(error, IntegrityError):
            raise ValidationError(f"Data integrity error in {operation}: {str(error.orig)}")
        elif isinstance(error, SQLAlchemyError):
            raise CRUDError(f"Database error in {operation}: {str(error)}")
        else:
            raise CRUDError(f"Unexpected error in {operation}: {str(error)}")


class ProjectCRUD(BaseCRUD):
    """CRUD operations for Projects"""
    
    def create_project(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project"""
        try:
            db_project = Project(**project_data)
            self.db.add(db_project)
            self.db.commit()
            self.db.refresh(db_project)
            return db_project
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("create_project", e)
    
    def get_project(self, project_id: Union[int, str]) -> Optional[Project]:
        """Get project by ID or project_id"""
        if isinstance(project_id, int):
            return self.db.query(Project).filter(Project.id == project_id).first()
        else:
            return self.db.query(Project).filter(Project.project_id == project_id).first()
    
    def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get list of projects"""
        return self.db.query(Project).offset(skip).limit(limit).all()
    
    def update_project(self, project_id: Union[int, str], update_data: Dict[str, Any]) -> Project:
        """Update project"""
        try:
            project = self.get_project(project_id)
            if not project:
                raise CRUDError(f"Project not found: {project_id}")
            
            for key, value in update_data.items():
                setattr(project, key, value)
            
            project.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(project)
            return project
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("update_project", e)
    
    def delete_project(self, project_id: Union[int, str]) -> bool:
        """Delete project and all related data"""
        try:
            project = self.get_project(project_id)
            if not project:
                return False
            
            self.db.delete(project)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("delete_project", e)


class SceneCardCRUD(BaseCRUD):
    """CRUD operations for Scene Cards"""
    
    def create_scene_card(self, project_id: int, scene_card: SceneCard) -> SceneCardDB:
        """Create a new scene card from Pydantic model"""
        try:
            # Convert Pydantic model to database model
            db_scene_card = self._pydantic_to_db_model(scene_card, project_id)
            
            self.db.add(db_scene_card)
            self.db.commit()
            self.db.refresh(db_scene_card)
            return db_scene_card
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("create_scene_card", e)
    
    def get_scene_card(self, scene_id: Union[int, str], project_id: Optional[int] = None) -> Optional[SceneCardDB]:
        """Get scene card by ID or scene_id"""
        query = self.db.query(SceneCardDB)
        
        if isinstance(scene_id, int):
            query = query.filter(SceneCardDB.id == scene_id)
        else:
            query = query.filter(SceneCardDB.scene_id == scene_id)
            if project_id:
                query = query.filter(SceneCardDB.project_id == project_id)
        
        return query.first()
    
    def get_scene_cards(self, 
                       project_id: Optional[int] = None,
                       scene_type: Optional[SceneType] = None,
                       pov: Optional[str] = None,
                       status: Optional[str] = None,
                       skip: int = 0,
                       limit: int = 100) -> List[SceneCardDB]:
        """Get scene cards with optional filtering"""
        query = self.db.query(SceneCardDB)
        
        if project_id:
            query = query.filter(SceneCardDB.project_id == project_id)
        
        if scene_type:
            query = query.filter(SceneCardDB.scene_type == SceneTypeEnum(scene_type.value))
        
        if pov:
            query = query.filter(SceneCardDB.pov == pov)
        
        if status:
            query = query.filter(SceneCardDB.status == status)
        
        return query.order_by(SceneCardDB.sequence_order, SceneCardDB.created_at).offset(skip).limit(limit).all()
    
    def get_scene_cards_by_chapter(self, project_id: int, chapter_number: int) -> List[SceneCardDB]:
        """Get all scene cards in a specific chapter"""
        return self.db.query(SceneCardDB).filter(
            and_(
                SceneCardDB.project_id == project_id,
                SceneCardDB.chapter_number == chapter_number
            )
        ).order_by(SceneCardDB.scene_number).all()
    
    def get_scene_cards_by_pov(self, project_id: int, pov: str) -> List[SceneCardDB]:
        """Get all scene cards for a specific POV character"""
        return self.db.query(SceneCardDB).filter(
            and_(
                SceneCardDB.project_id == project_id,
                SceneCardDB.pov == pov
            )
        ).order_by(SceneCardDB.sequence_order).all()
    
    def search_scene_cards(self, 
                          project_id: int,
                          search_term: str,
                          search_fields: List[str] = None) -> List[SceneCardDB]:
        """Search scene cards by content"""
        if search_fields is None:
            search_fields = ['scene_crucible', 'place', 'time', 'pov']
        
        conditions = []
        
        if 'scene_crucible' in search_fields:
            conditions.append(SceneCardDB.scene_crucible.contains(search_term))
        if 'place' in search_fields:
            conditions.append(SceneCardDB.place.contains(search_term))
        if 'time' in search_fields:
            conditions.append(SceneCardDB.time.contains(search_term))
        if 'pov' in search_fields:
            conditions.append(SceneCardDB.pov.contains(search_term))
        
        return self.db.query(SceneCardDB).filter(
            and_(
                SceneCardDB.project_id == project_id,
                or_(*conditions)
            )
        ).all()
    
    def update_scene_card(self, scene_id: Union[int, str], update_data: Dict[str, Any], 
                         project_id: Optional[int] = None) -> SceneCardDB:
        """Update scene card"""
        try:
            scene_card = self.get_scene_card(scene_id, project_id)
            if not scene_card:
                raise SceneNotFoundError(f"Scene card not found: {scene_id}")
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(scene_card, key):
                    setattr(scene_card, key, value)
            
            scene_card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(scene_card)
            return scene_card
        except Exception as e:
            self.db.rollback()
            if isinstance(e, SceneNotFoundError):
                raise
            self._handle_db_error("update_scene_card", e)
    
    def update_scene_card_from_pydantic(self, scene_id: Union[int, str], scene_card: SceneCard, 
                                       project_id: Optional[int] = None) -> SceneCardDB:
        """Update scene card from Pydantic model"""
        try:
            db_scene_card = self.get_scene_card(scene_id, project_id)
            if not db_scene_card:
                raise SceneNotFoundError(f"Scene card not found: {scene_id}")
            
            # Update from Pydantic model
            self._update_db_from_pydantic(db_scene_card, scene_card)
            
            db_scene_card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_scene_card)
            return db_scene_card
        except Exception as e:
            self.db.rollback()
            if isinstance(e, SceneNotFoundError):
                raise
            self._handle_db_error("update_scene_card_from_pydantic", e)
    
    def delete_scene_card(self, scene_id: Union[int, str], project_id: Optional[int] = None) -> bool:
        """Delete scene card"""
        try:
            scene_card = self.get_scene_card(scene_id, project_id)
            if not scene_card:
                return False
            
            self.db.delete(scene_card)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("delete_scene_card", e)
    
    def bulk_create_scene_cards(self, project_id: int, scene_cards: List[SceneCard]) -> List[SceneCardDB]:
        """Bulk create scene cards"""
        try:
            db_scene_cards = []
            
            for scene_card in scene_cards:
                db_scene_card = self._pydantic_to_db_model(scene_card, project_id)
                db_scene_cards.append(db_scene_card)
            
            self.db.add_all(db_scene_cards)
            self.db.commit()
            
            for db_scene_card in db_scene_cards:
                self.db.refresh(db_scene_card)
            
            return db_scene_cards
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("bulk_create_scene_cards", e)
    
    def get_scene_card_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get statistics for scene cards in project"""
        total_scenes = self.db.query(func.count(SceneCardDB.id)).filter(
            SceneCardDB.project_id == project_id
        ).scalar()
        
        proactive_scenes = self.db.query(func.count(SceneCardDB.id)).filter(
            and_(
                SceneCardDB.project_id == project_id,
                SceneCardDB.scene_type == SceneTypeEnum.PROACTIVE
            )
        ).scalar()
        
        reactive_scenes = self.db.query(func.count(SceneCardDB.id)).filter(
            and_(
                SceneCardDB.project_id == project_id,
                SceneCardDB.scene_type == SceneTypeEnum.REACTIVE
            )
        ).scalar()
        
        total_words = self.db.query(func.sum(SceneCardDB.word_count)).filter(
            SceneCardDB.project_id == project_id
        ).scalar() or 0
        
        avg_quality = self.db.query(func.avg(SceneCardDB.quality_score)).filter(
            SceneCardDB.project_id == project_id
        ).scalar() or 0.0
        
        return {
            "total_scenes": total_scenes,
            "proactive_scenes": proactive_scenes,
            "reactive_scenes": reactive_scenes,
            "total_word_count": total_words,
            "average_quality_score": float(avg_quality),
            "proactive_ratio": proactive_scenes / total_scenes if total_scenes > 0 else 0
        }
    
    def _pydantic_to_db_model(self, scene_card: SceneCard, project_id: int) -> SceneCardDB:
        """Convert Pydantic SceneCard to database model"""
        # Generate scene_id if not provided
        scene_id = getattr(scene_card, 'scene_id', None) or f"{scene_card.scene_type.value}_{scene_card.pov}_{int(datetime.utcnow().timestamp())}"
        
        db_scene_card = SceneCardDB(
            project_id=project_id,
            scene_id=scene_id,
            scene_type=SceneTypeEnum(scene_card.scene_type.value),
            pov=scene_card.pov,
            viewpoint=ViewpointTypeEnum(scene_card.viewpoint.value),
            tense=TenseTypeEnum(scene_card.tense.value),
            scene_crucible=scene_card.scene_crucible,
            place=scene_card.place,
            time=scene_card.time,
            exposition_used=scene_card.exposition_used,
            chain_link=scene_card.chain_link
        )
        
        # Handle proactive/reactive data
        if scene_card.proactive:
            db_scene_card.proactive_data = scene_card.proactive.dict()
        
        if scene_card.reactive:
            db_scene_card.reactive_data = scene_card.reactive.dict()
        
        return db_scene_card
    
    def _update_db_from_pydantic(self, db_scene_card: SceneCardDB, scene_card: SceneCard):
        """Update database model from Pydantic model"""
        db_scene_card.scene_type = SceneTypeEnum(scene_card.scene_type.value)
        db_scene_card.pov = scene_card.pov
        db_scene_card.viewpoint = ViewpointTypeEnum(scene_card.viewpoint.value)
        db_scene_card.tense = TenseTypeEnum(scene_card.tense.value)
        db_scene_card.scene_crucible = scene_card.scene_crucible
        db_scene_card.place = scene_card.place
        db_scene_card.time = scene_card.time
        db_scene_card.exposition_used = scene_card.exposition_used
        db_scene_card.chain_link = scene_card.chain_link
        
        # Update proactive/reactive data
        if scene_card.proactive:
            db_scene_card.proactive_data = scene_card.proactive.dict()
            db_scene_card.reactive_data = None
        elif scene_card.reactive:
            db_scene_card.reactive_data = scene_card.reactive.dict()
            db_scene_card.proactive_data = None
    
    def db_to_pydantic(self, db_scene_card: SceneCardDB) -> SceneCard:
        """Convert database model to Pydantic SceneCard"""
        from ..models import ProactiveScene, ReactiveScene
        
        # Build base scene card
        scene_data = {
            "scene_type": SceneType(db_scene_card.scene_type.value),
            "pov": db_scene_card.pov,
            "viewpoint": ViewpointType(db_scene_card.viewpoint.value),
            "tense": TenseType(db_scene_card.tense.value),
            "scene_crucible": db_scene_card.scene_crucible,
            "place": db_scene_card.place,
            "time": db_scene_card.time,
            "exposition_used": db_scene_card.exposition_used or [],
            "chain_link": db_scene_card.chain_link
        }
        
        # Add proactive/reactive data
        if db_scene_card.proactive_data:
            scene_data["proactive"] = ProactiveScene(**db_scene_card.proactive_data)
        
        if db_scene_card.reactive_data:
            scene_data["reactive"] = ReactiveScene(**db_scene_card.reactive_data)
        
        return SceneCard(**scene_data)


class ChainLinkCRUD(BaseCRUD):
    """CRUD operations for Chain Links"""
    
    def create_chain_link(self, project_id: int, chain_link: ChainLink) -> ChainLinkDB:
        """Create a new chain link from Pydantic model"""
        try:
            db_chain_link = self._pydantic_to_db_model(chain_link, project_id)
            
            self.db.add(db_chain_link)
            self.db.commit()
            self.db.refresh(db_chain_link)
            return db_chain_link
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("create_chain_link", e)
    
    def get_chain_link(self, chain_id: Union[int, str], project_id: Optional[int] = None) -> Optional[ChainLinkDB]:
        """Get chain link by ID or chain_id"""
        query = self.db.query(ChainLinkDB)
        
        if isinstance(chain_id, int):
            query = query.filter(ChainLinkDB.id == chain_id)
        else:
            query = query.filter(ChainLinkDB.chain_id == chain_id)
            if project_id:
                query = query.filter(ChainLinkDB.project_id == project_id)
        
        return query.first()
    
    def get_chain_links_for_scene(self, project_id: int, scene_id: str) -> List[ChainLinkDB]:
        """Get all chain links originating from a scene"""
        return self.db.query(ChainLinkDB).filter(
            and_(
                ChainLinkDB.project_id == project_id,
                ChainLinkDB.source_scene_id == scene_id
            )
        ).all()
    
    def get_chain_links_to_scene(self, project_id: int, scene_id: str) -> List[ChainLinkDB]:
        """Get all chain links targeting a scene"""
        return self.db.query(ChainLinkDB).filter(
            and_(
                ChainLinkDB.project_id == project_id,
                ChainLinkDB.target_scene_id == scene_id
            )
        ).all()
    
    def get_chain_links(self, 
                       project_id: Optional[int] = None,
                       chain_type: Optional[str] = None,
                       is_valid: Optional[bool] = None,
                       skip: int = 0,
                       limit: int = 100) -> List[ChainLinkDB]:
        """Get chain links with optional filtering"""
        query = self.db.query(ChainLinkDB)
        
        if project_id:
            query = query.filter(ChainLinkDB.project_id == project_id)
        
        if chain_type:
            query = query.filter(ChainLinkDB.chain_type == ChainLinkTypeEnum(chain_type))
        
        if is_valid is not None:
            query = query.filter(ChainLinkDB.is_valid == is_valid)
        
        return query.order_by(ChainLinkDB.created_at).offset(skip).limit(limit).all()
    
    def update_chain_link(self, chain_id: Union[int, str], update_data: Dict[str, Any],
                         project_id: Optional[int] = None) -> ChainLinkDB:
        """Update chain link"""
        try:
            chain_link = self.get_chain_link(chain_id, project_id)
            if not chain_link:
                raise ChainLinkNotFoundError(f"Chain link not found: {chain_id}")
            
            for key, value in update_data.items():
                if hasattr(chain_link, key):
                    setattr(chain_link, key, value)
            
            chain_link.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(chain_link)
            return chain_link
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ChainLinkNotFoundError):
                raise
            self._handle_db_error("update_chain_link", e)
    
    def delete_chain_link(self, chain_id: Union[int, str], project_id: Optional[int] = None) -> bool:
        """Delete chain link"""
        try:
            chain_link = self.get_chain_link(chain_id, project_id)
            if not chain_link:
                return False
            
            self.db.delete(chain_link)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("delete_chain_link", e)
    
    def _pydantic_to_db_model(self, chain_link: ChainLink, project_id: int) -> ChainLinkDB:
        """Convert Pydantic ChainLink to database model"""
        from ..chaining.models import ChainLinkType, TransitionType, ChainStrength
        
        db_chain_link = ChainLinkDB(
            project_id=project_id,
            chain_id=chain_link.chain_id,
            chain_type=ChainLinkTypeEnum(chain_link.chain_type.value),
            transition_type=chain_link.transition_type.name,
            source_scene_id=chain_link.source_scene.scene_id,
            source_scene_type=SceneTypeEnum(chain_link.source_scene.scene_type.value),
            source_pov=chain_link.source_scene.pov_character,
            trigger_content=chain_link.trigger_content,
            target_seed=chain_link.target_seed,
            bridging_content=chain_link.bridging_content,
            is_valid=chain_link.is_valid,
            validation_errors=chain_link.validation_errors,
            story_context=chain_link.story_context,
            character_state_changes=chain_link.character_state_changes
        )
        
        # Add target scene if present
        if chain_link.target_scene:
            db_chain_link.target_scene_id = chain_link.target_scene.scene_id
            db_chain_link.target_scene_type = SceneTypeEnum(chain_link.target_scene.scene_type.value)
            db_chain_link.target_pov = chain_link.target_scene.pov_character
        
        # Add metadata
        if chain_link.metadata:
            db_chain_link.chain_strength = chain_link.metadata.chain_strength.name
            db_chain_link.validation_score = chain_link.metadata.validation_score
            db_chain_link.emotional_continuity = chain_link.metadata.emotional_continuity
            db_chain_link.narrative_necessity = chain_link.metadata.narrative_necessity
        
        return db_chain_link


class ProseContentCRUD(BaseCRUD):
    """CRUD operations for Prose Content"""
    
    def create_prose_content(self, scene_card_id: int, content: str, 
                           content_type: str = "markdown", 
                           metadata: Optional[Dict[str, Any]] = None) -> ProseContent:
        """Create prose content for a scene"""
        try:
            word_count = len(content.split())
            character_count = len(content)
            reading_time = max(1, word_count // 250)  # Assume 250 words per minute
            
            prose_content = ProseContent(
                scene_card_id=scene_card_id,
                content=content,
                content_type=content_type,
                word_count=word_count,
                character_count=character_count,
                reading_time_minutes=reading_time
            )
            
            if metadata:
                for key, value in metadata.items():
                    if hasattr(prose_content, key):
                        setattr(prose_content, key, value)
            
            self.db.add(prose_content)
            self.db.commit()
            self.db.refresh(prose_content)
            return prose_content
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("create_prose_content", e)
    
    def get_current_prose_content(self, scene_card_id: int) -> Optional[ProseContent]:
        """Get current version of prose content for a scene"""
        return self.db.query(ProseContent).filter(
            and_(
                ProseContent.scene_card_id == scene_card_id,
                ProseContent.is_current_version == True
            )
        ).first()
    
    def get_prose_content_versions(self, scene_card_id: int) -> List[ProseContent]:
        """Get all versions of prose content for a scene"""
        return self.db.query(ProseContent).filter(
            ProseContent.scene_card_id == scene_card_id
        ).order_by(desc(ProseContent.created_at)).all()
    
    def update_prose_content(self, scene_card_id: int, content: str,
                           version_notes: Optional[str] = None) -> ProseContent:
        """Update prose content, creating new version"""
        try:
            # Mark current version as not current
            current = self.get_current_prose_content(scene_card_id)
            if current:
                current.is_current_version = False
            
            # Create new version
            word_count = len(content.split())
            character_count = len(content)
            reading_time = max(1, word_count // 250)
            
            # Generate new version number
            latest_version = "1.0.0"
            if current:
                version_parts = current.version.split('.')
                minor_version = int(version_parts[1]) + 1
                latest_version = f"{version_parts[0]}.{minor_version}.0"
            
            new_prose = ProseContent(
                scene_card_id=scene_card_id,
                content=content,
                word_count=word_count,
                character_count=character_count,
                reading_time_minutes=reading_time,
                version=latest_version,
                version_notes=version_notes,
                is_current_version=True
            )
            
            self.db.add(new_prose)
            self.db.commit()
            self.db.refresh(new_prose)
            return new_prose
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("update_prose_content", e)
    
    def delete_prose_content(self, scene_card_id: int, version: Optional[str] = None) -> bool:
        """Delete prose content (specific version or all)"""
        try:
            query = self.db.query(ProseContent).filter(ProseContent.scene_card_id == scene_card_id)
            
            if version:
                query = query.filter(ProseContent.version == version)
            
            prose_content = query.all()
            
            for prose in prose_content:
                self.db.delete(prose)
            
            self.db.commit()
            return len(prose_content) > 0
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("delete_prose_content", e)


class CharacterCRUD(BaseCRUD):
    """CRUD operations for Characters"""
    
    def create_character(self, project_id: int, character_data: Dict[str, Any]) -> Character:
        """Create a new character"""
        try:
            character_data['project_id'] = project_id
            db_character = Character(**character_data)
            
            self.db.add(db_character)
            self.db.commit()
            self.db.refresh(db_character)
            return db_character
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("create_character", e)
    
    def get_character(self, character_id: int) -> Optional[Character]:
        """Get character by ID"""
        return self.db.query(Character).filter(Character.id == character_id).first()
    
    def get_character_by_name(self, project_id: int, name: str) -> Optional[Character]:
        """Get character by name within project"""
        return self.db.query(Character).filter(
            and_(Character.project_id == project_id, Character.name == name)
        ).first()
    
    def get_characters(self, project_id: int) -> List[Character]:
        """Get all characters for a project"""
        return self.db.query(Character).filter(Character.project_id == project_id).all()
    
    def update_character(self, character_id: int, update_data: Dict[str, Any]) -> Character:
        """Update character"""
        try:
            character = self.get_character(character_id)
            if not character:
                raise CRUDError(f"Character not found: {character_id}")
            
            for key, value in update_data.items():
                setattr(character, key, value)
            
            character.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(character)
            return character
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("update_character", e)
    
    def delete_character(self, character_id: int) -> bool:
        """Delete character"""
        try:
            character = self.get_character(character_id)
            if not character:
                return False
            
            self.db.delete(character)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("delete_character", e)


class SceneSequenceCRUD(BaseCRUD):
    """CRUD operations for Scene Sequences"""
    
    def create_sequence(self, project_id: int, sequence_data: Dict[str, Any]) -> SceneSequenceDB:
        """Create a new scene sequence"""
        try:
            sequence_data['project_id'] = project_id
            db_sequence = SceneSequenceDB(**sequence_data)
            
            self.db.add(db_sequence)
            self.db.commit()
            self.db.refresh(db_sequence)
            return db_sequence
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("create_sequence", e)
    
    def get_sequence(self, sequence_id: Union[int, str], project_id: Optional[int] = None) -> Optional[SceneSequenceDB]:
        """Get sequence by ID or sequence_id"""
        query = self.db.query(SceneSequenceDB)
        
        if isinstance(sequence_id, int):
            query = query.filter(SceneSequenceDB.id == sequence_id)
        else:
            query = query.filter(SceneSequenceDB.sequence_id == sequence_id)
            if project_id:
                query = query.filter(SceneSequenceDB.project_id == project_id)
        
        return query.first()
    
    def get_sequences(self, project_id: int) -> List[SceneSequenceDB]:
        """Get all sequences for a project"""
        return self.db.query(SceneSequenceDB).filter(
            SceneSequenceDB.project_id == project_id
        ).order_by(SceneSequenceDB.chapter_start, SceneSequenceDB.created_at).all()
    
    def update_sequence(self, sequence_id: Union[int, str], update_data: Dict[str, Any],
                       project_id: Optional[int] = None) -> SceneSequenceDB:
        """Update sequence"""
        try:
            sequence = self.get_sequence(sequence_id, project_id)
            if not sequence:
                raise CRUDError(f"Sequence not found: {sequence_id}")
            
            for key, value in update_data.items():
                setattr(sequence, key, value)
            
            sequence.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(sequence)
            return sequence
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("update_sequence", e)
    
    def delete_sequence(self, sequence_id: Union[int, str], project_id: Optional[int] = None) -> bool:
        """Delete sequence"""
        try:
            sequence = self.get_sequence(sequence_id, project_id)
            if not sequence:
                return False
            
            self.db.delete(sequence)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self._handle_db_error("delete_sequence", e)


# Factory function for creating CRUD instances
def create_crud_manager(db_session: Session) -> Dict[str, BaseCRUD]:
    """Create CRUD manager with all CRUD operations"""
    return {
        'projects': ProjectCRUD(db_session),
        'scene_cards': SceneCardCRUD(db_session),
        'chain_links': ChainLinkCRUD(db_session),
        'prose_content': ProseContentCRUD(db_session),
        'characters': CharacterCRUD(db_session),
        'sequences': SceneSequenceCRUD(db_session)
    }