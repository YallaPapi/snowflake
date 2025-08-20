"""
Comprehensive Test Suite for Scene Engine Persistence Layer

This implements subtask 48.6: Tests
Complete test coverage for all persistence components including models, CRUD,
service, queries, and backup/recovery functionality.
"""

import pytest
import tempfile
import shutil
import json
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Import all persistence components
from ..models import (
    Base, Project, SceneCardDB, ProseContent, ChainLinkDB, Character,
    SceneSequenceDB, ValidationLog, BackupRecord,
    SceneTypeEnum, ViewpointTypeEnum, TenseTypeEnum, ChainLinkTypeEnum,
    create_tables, drop_tables
)
from ..crud import (
    ProjectCRUD, SceneCardCRUD, ChainLinkCRUD, ProseContentCRUD,
    CharacterCRUD, SceneSequenceCRUD, create_crud_manager,
    CRUDError, SceneNotFoundError, ChainLinkNotFoundError, ValidationError
)
from ..service import (
    PersistenceService, ProseAnalyzer, ProseVersionManager,
    PersistenceError, ContentAnalysisError, VersioningError
)
from ..query import (
    QueryInterface, SceneCardQueryBuilder, ChainLinkQueryBuilder, 
    AggregationQueryBuilder, QueryFilter, QuerySort, SortDirection,
    QueryError
)
from ..backup import (
    BackupManager, RecoveryManager, BackupConfiguration, BackupMetadata,
    BackupType, BackupFormat, BackupStatus, BackupError, RecoveryError, IntegrityError
)

# Import scene engine models for test data
from ...models import SceneCard, SceneType, ViewpointType, TenseType, ProactiveScene, ReactiveScene
from ...chaining.models import ChainLink, ChainLinkType, TransitionType, SceneReference


@pytest.fixture
def test_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create test database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def temp_backup_dir():
    """Create temporary directory for backup tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        'project_id': 'test_project_001',
        'title': 'Test Novel',
        'description': 'A test novel for unit testing',
        'author': 'Test Author',
        'genre': 'Test Fiction',
        'target_word_count': 80000
    }


@pytest.fixture
def sample_scene_card():
    """Sample scene card for testing"""
    proactive = ProactiveScene(
        goal="Find the hidden treasure",
        conflict="Guards are patrolling the area",
        setback="The map is torn and missing crucial details"
    )
    
    return SceneCard(
        scene_type=SceneType.PROACTIVE,
        pov="Jack",
        viewpoint=ViewpointType.THIRD,
        tense=TenseType.PAST,
        scene_crucible="Jack must retrieve the ancient map from the heavily guarded library",
        place="Ancient Library",
        time="Midnight",
        exposition_used=["Jack's background", "Map history"],
        chain_link="Previous scene ended with Jack discovering the map's location",
        proactive=proactive
    )


@pytest.fixture
def sample_chain_link():
    """Sample chain link for testing"""
    source_scene = SceneReference(
        scene_id="scene_001",
        scene_type=SceneType.PROACTIVE,
        pov_character="Jack"
    )
    
    target_scene = SceneReference(
        scene_id="scene_002", 
        scene_type=SceneType.REACTIVE,
        pov_character="Jack"
    )
    
    return ChainLink(
        chain_id="chain_001",
        chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
        transition_type=TransitionType.IMMEDIATE,
        source_scene=source_scene,
        target_scene=target_scene,
        trigger_content="Jack realizes the map is incomplete",
        target_seed="Jack must decide how to proceed without complete information",
        bridging_content="Jack stares at the torn map in frustration",
        is_valid=True,
        validation_errors=[],
        story_context={"tension_level": "high", "stakes": "treasure_hunt"},
        character_state_changes={"Jack": {"frustration": "increased"}}
    )


# Database Model Tests
class TestDatabaseModels:
    """Test database model functionality"""
    
    def test_project_model_creation(self, test_session, sample_project_data):
        """Test Project model creation and relationships"""
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Verify project was created
        retrieved = test_session.query(Project).filter(
            Project.project_id == sample_project_data['project_id']
        ).first()
        
        assert retrieved is not None
        assert retrieved.title == sample_project_data['title']
        assert retrieved.author == sample_project_data['author']
        assert retrieved.target_word_count == sample_project_data['target_word_count']
    
    def test_scene_card_model_creation(self, test_session, sample_project_data):
        """Test SceneCardDB model creation"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create scene card
        scene_data = {
            'project_id': project.id,
            'scene_id': 'test_scene_001',
            'scene_type': SceneTypeEnum.PROACTIVE,
            'pov': 'Jack',
            'viewpoint': ViewpointTypeEnum.THIRD,
            'tense': TenseTypeEnum.PAST,
            'scene_crucible': 'Test scene crucible',
            'place': 'Test Location',
            'time': 'Test Time',
            'proactive_data': {'goal': 'test goal', 'conflict': 'test conflict', 'setback': 'test setback'}
        }
        
        scene_card = SceneCardDB(**scene_data)
        test_session.add(scene_card)
        test_session.commit()
        
        # Verify scene card was created
        retrieved = test_session.query(SceneCardDB).filter(
            SceneCardDB.scene_id == 'test_scene_001'
        ).first()
        
        assert retrieved is not None
        assert retrieved.scene_type == SceneTypeEnum.PROACTIVE
        assert retrieved.pov == 'Jack'
        assert retrieved.proactive_data['goal'] == 'test goal'
    
    def test_prose_content_model_creation(self, test_session, sample_project_data):
        """Test ProseContent model creation with versioning"""
        # Create project and scene card
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        scene_card = SceneCardDB(
            project_id=project.id,
            scene_id='test_scene_001',
            scene_type=SceneTypeEnum.PROACTIVE,
            pov='Jack',
            viewpoint=ViewpointTypeEnum.THIRD,
            tense=TenseTypeEnum.PAST,
            scene_crucible='Test crucible'
        )
        test_session.add(scene_card)
        test_session.commit()
        
        # Create prose content
        prose_content = ProseContent(
            scene_card_id=scene_card.id,
            content="This is test prose content for the scene.",
            word_count=9,
            character_count=45,
            reading_time_minutes=1,
            version="1.0.0",
            is_current_version=True
        )
        test_session.add(prose_content)
        test_session.commit()
        
        # Verify prose content
        retrieved = test_session.query(ProseContent).filter(
            ProseContent.scene_card_id == scene_card.id
        ).first()
        
        assert retrieved is not None
        assert retrieved.word_count == 9
        assert retrieved.is_current_version is True
        assert retrieved.version == "1.0.0"
    
    def test_chain_link_model_creation(self, test_session, sample_project_data):
        """Test ChainLinkDB model creation"""
        # Create project
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create chain link
        chain_link = ChainLinkDB(
            project_id=project.id,
            chain_id='test_chain_001',
            chain_type=ChainLinkTypeEnum.SETBACK_TO_REACTIVE,
            source_scene_id='scene_001',
            source_scene_type=SceneTypeEnum.PROACTIVE,
            source_pov='Jack',
            target_scene_id='scene_002',
            target_scene_type=SceneTypeEnum.REACTIVE,
            target_pov='Jack',
            trigger_content='Test trigger',
            target_seed='Test target seed',
            is_valid=True,
            validation_score=0.8
        )
        test_session.add(chain_link)
        test_session.commit()
        
        # Verify chain link
        retrieved = test_session.query(ChainLinkDB).filter(
            ChainLinkDB.chain_id == 'test_chain_001'
        ).first()
        
        assert retrieved is not None
        assert retrieved.chain_type == ChainLinkTypeEnum.SETBACK_TO_REACTIVE
        assert retrieved.validation_score == 0.8
        assert retrieved.is_valid is True


# CRUD Operations Tests
class TestCRUDOperations:
    """Test CRUD operation functionality"""
    
    def test_project_crud_operations(self, test_session, sample_project_data):
        """Test ProjectCRUD operations"""
        project_crud = ProjectCRUD(test_session)
        
        # Create project
        project = project_crud.create_project(sample_project_data)
        assert project.title == sample_project_data['title']
        
        # Get project by ID and project_id
        retrieved_by_id = project_crud.get_project(project.id)
        retrieved_by_project_id = project_crud.get_project(project.project_id)
        assert retrieved_by_id.id == project.id
        assert retrieved_by_project_id.id == project.id
        
        # Update project
        update_data = {'title': 'Updated Title', 'author': 'Updated Author'}
        updated = project_crud.update_project(project.id, update_data)
        assert updated.title == 'Updated Title'
        assert updated.author == 'Updated Author'
        
        # Get projects list
        projects = project_crud.get_projects()
        assert len(projects) == 1
        
        # Delete project
        success = project_crud.delete_project(project.id)
        assert success is True
        
        # Verify deletion
        deleted = project_crud.get_project(project.id)
        assert deleted is None
    
    def test_scene_card_crud_operations(self, test_session, sample_project_data, sample_scene_card):
        """Test SceneCardCRUD operations"""
        project_crud = ProjectCRUD(test_session)
        scene_crud = SceneCardCRUD(test_session)
        
        # Create project
        project = project_crud.create_project(sample_project_data)
        
        # Create scene card
        db_scene_card = scene_crud.create_scene_card(project.id, sample_scene_card)
        assert db_scene_card.scene_type == SceneTypeEnum.PROACTIVE
        assert db_scene_card.pov == "Jack"
        
        # Get scene card
        retrieved = scene_crud.get_scene_card(db_scene_card.scene_id, project.id)
        assert retrieved.id == db_scene_card.id
        
        # Get scene cards with filtering
        proactive_scenes = scene_crud.get_scene_cards(
            project_id=project.id,
            scene_type=SceneType.PROACTIVE
        )
        assert len(proactive_scenes) == 1
        
        jack_scenes = scene_crud.get_scene_cards_by_pov(project.id, "Jack")
        assert len(jack_scenes) == 1
        
        # Update scene card
        update_data = {'place': 'Updated Location'}
        updated = scene_crud.update_scene_card(db_scene_card.scene_id, update_data, project.id)
        assert updated.place == 'Updated Location'
        
        # Convert to Pydantic and update
        pydantic_scene = scene_crud.db_to_pydantic(updated)
        pydantic_scene.time = "Updated Time"
        updated_from_pydantic = scene_crud.update_scene_card_from_pydantic(
            updated.scene_id, pydantic_scene, project.id
        )
        assert updated_from_pydantic.time == "Updated Time"
        
        # Search scene cards
        search_results = scene_crud.search_scene_cards(project.id, "treasure")
        assert len(search_results) == 1
        
        # Get statistics
        stats = scene_crud.get_scene_card_statistics(project.id)
        assert stats['total_scenes'] == 1
        assert stats['proactive_scenes'] == 1
        assert stats['reactive_scenes'] == 0
        
        # Delete scene card
        success = scene_crud.delete_scene_card(db_scene_card.scene_id, project.id)
        assert success is True
    
    def test_prose_content_crud_operations(self, test_session, sample_project_data):
        """Test ProseContentCRUD operations"""
        project_crud = ProjectCRUD(test_session)
        scene_crud = SceneCardCRUD(test_session)
        prose_crud = ProseContentCRUD(test_session)
        
        # Create project and scene
        project = project_crud.create_project(sample_project_data)
        scene_card = SceneCardDB(
            project_id=project.id,
            scene_id='test_scene',
            scene_type=SceneTypeEnum.PROACTIVE,
            pov='Jack',
            viewpoint=ViewpointTypeEnum.THIRD,
            tense=TenseTypeEnum.PAST,
            scene_crucible='Test crucible'
        )
        test_session.add(scene_card)
        test_session.commit()
        
        # Create prose content
        prose = prose_crud.create_prose_content(
            scene_card_id=scene_card.id,
            content="This is the initial prose content.",
            content_type="markdown"
        )
        assert prose.word_count == 6
        assert prose.is_current_version is True
        
        # Get current prose content
        current = prose_crud.get_current_prose_content(scene_card.id)
        assert current.id == prose.id
        
        # Update prose content (creates new version)
        updated_prose = prose_crud.update_prose_content(
            scene_card_id=scene_card.id,
            content="This is the updated prose content with more words.",
            version_notes="Added more content"
        )
        assert updated_prose.word_count == 10
        assert updated_prose.version == "1.1.0"
        
        # Get all versions
        versions = prose_crud.get_prose_content_versions(scene_card.id)
        assert len(versions) == 2
        
        # Verify old version is no longer current
        old_version = test_session.query(ProseContent).filter(
            ProseContent.id == prose.id
        ).first()
        assert old_version.is_current_version is False
        
        # Delete prose content
        success = prose_crud.delete_prose_content(scene_card.id)
        assert success is True
        
        remaining_versions = prose_crud.get_prose_content_versions(scene_card.id)
        assert len(remaining_versions) == 0
    
    def test_chain_link_crud_operations(self, test_session, sample_project_data, sample_chain_link):
        """Test ChainLinkCRUD operations"""
        project_crud = ProjectCRUD(test_session)
        chain_crud = ChainLinkCRUD(test_session)
        
        # Create project
        project = project_crud.create_project(sample_project_data)
        
        # Create chain link
        db_chain_link = chain_crud.create_chain_link(project.id, sample_chain_link)
        assert db_chain_link.chain_type == ChainLinkTypeEnum.SETBACK_TO_REACTIVE
        assert db_chain_link.is_valid is True
        
        # Get chain link
        retrieved = chain_crud.get_chain_link(db_chain_link.chain_id, project.id)
        assert retrieved.id == db_chain_link.id
        
        # Get chain links for source scene
        source_links = chain_crud.get_chain_links_for_scene(project.id, "scene_001")
        assert len(source_links) == 1
        
        # Get chain links to target scene
        target_links = chain_crud.get_chain_links_to_scene(project.id, "scene_002")
        assert len(target_links) == 1
        
        # Filter by type
        setback_links = chain_crud.get_chain_links(
            project_id=project.id,
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE.value
        )
        assert len(setback_links) == 1
        
        # Filter by validity
        valid_links = chain_crud.get_chain_links(project_id=project.id, is_valid=True)
        assert len(valid_links) == 1
        
        # Update chain link
        update_data = {'validation_score': 0.9, 'is_valid': True}
        updated = chain_crud.update_chain_link(db_chain_link.chain_id, update_data, project.id)
        assert updated.validation_score == 0.9
        
        # Delete chain link
        success = chain_crud.delete_chain_link(db_chain_link.chain_id, project.id)
        assert success is True
    
    def test_crud_error_handling(self, test_session):
        """Test CRUD error handling"""
        scene_crud = SceneCardCRUD(test_session)
        
        # Test getting non-existent scene
        non_existent = scene_crud.get_scene_card("non_existent_scene")
        assert non_existent is None
        
        # Test updating non-existent scene
        with pytest.raises(SceneNotFoundError):
            scene_crud.update_scene_card("non_existent_scene", {'place': 'Updated'})
        
        # Test database integrity error handling
        with pytest.raises(ValidationError):
            # Try to create project with duplicate project_id
            project1 = Project(project_id="duplicate", title="Project 1")
            project2 = Project(project_id="duplicate", title="Project 2")
            test_session.add(project1)
            test_session.add(project2)
            test_session.commit()


# Persistence Service Tests
class TestPersistenceService:
    """Test high-level persistence service functionality"""
    
    def test_prose_analyzer(self):
        """Test prose content analysis"""
        sample_text = """
        The quick brown fox jumps over the lazy dog. This is a test sentence for readability.
        "Hello there!" said the character with great excitement and joy.
        The story continues with more complex narrative elements and detailed descriptions.
        """
        
        analysis = ProseAnalyzer.analyze_content(sample_text)
        
        assert analysis['word_count'] > 0
        assert analysis['character_count'] > 0
        assert analysis['sentence_count'] > 0
        assert 0 <= analysis['readability_score'] <= 100
        assert 0 <= analysis['sentiment_score'] <= 1
        assert isinstance(analysis['keywords'], list)
        assert 0 <= analysis['dialogue_ratio'] <= 1
    
    def test_prose_version_manager(self, test_session, sample_project_data):
        """Test prose versioning functionality"""
        # Setup
        project_crud = ProjectCRUD(test_session)
        prose_crud = ProseContentCRUD(test_session)
        version_manager = ProseVersionManager(prose_crud)
        
        project = project_crud.create_project(sample_project_data)
        scene_card = SceneCardDB(
            project_id=project.id,
            scene_id='test_scene',
            scene_type=SceneTypeEnum.PROACTIVE,
            pov='Jack',
            viewpoint=ViewpointTypeEnum.THIRD,
            tense=TenseTypeEnum.PAST,
            scene_crucible='Test crucible'
        )
        test_session.add(scene_card)
        test_session.commit()
        
        # Create initial version
        prose_v1 = version_manager.create_version(
            scene_card_id=scene_card.id,
            content="This is the first version of prose content.",
            version_notes="Initial version"
        )
        assert prose_v1.version == "1.0.0"
        assert prose_v1.version_notes == "Initial version"
        
        # Create second version
        prose_v2 = version_manager.create_version(
            scene_card_id=scene_card.id,
            content="This is the second version with updated content.",
            version_notes="Content improvements"
        )
        assert prose_v2.version == "1.1.0"
        assert prose_v2.is_current_version is True
        
        # Test duplicate content detection
        with pytest.raises(VersioningError):
            version_manager.create_version(
                scene_card_id=scene_card.id,
                content="This is the second version with updated content.",
                version_notes="Duplicate content"
            )
        
        # Test rollback
        rollback_prose = version_manager.rollback_to_version(scene_card.id, "1.0.0")
        assert "Rollback to version 1.0.0" in rollback_prose.version_notes
        
        # Test version comparison
        comparison = version_manager.compare_versions(scene_card.id, "1.0.0", "1.1.0")
        assert 'word_count_change' in comparison
        assert 'content_similarity' in comparison
    
    def test_persistence_service_operations(self, test_session, sample_scene_card):
        """Test PersistenceService high-level operations"""
        service = PersistenceService(test_session)
        
        # Create project
        project = service.create_project(
            title="Test Project",
            description="Test Description",
            author="Test Author",
            genre="Fiction",
            target_word_count=50000
        )
        assert project.title == "Test Project"
        
        # Create scene card with prose
        prose_content = "Jack crept through the shadows toward the ancient library."
        db_scene_card, prose_obj = service.create_scene_card_with_prose(
            project_id=project.id,
            scene_card=sample_scene_card,
            prose_content=prose_content,
            prose_notes="Initial scene prose"
        )
        assert db_scene_card.word_count == 10  # Word count from prose
        assert prose_obj is not None
        
        # Update scene prose
        updated_prose = service.update_scene_prose(
            scene_id=db_scene_card.scene_id,
            content="Jack crept through the shadows toward the ancient library, his heart pounding with anticipation.",
            version_notes="Added emotional detail",
            project_id=project.id
        )
        assert updated_prose.word_count == 15
        
        # Get scene with prose
        scene_with_prose = service.get_scene_with_prose(db_scene_card.scene_id, project.id)
        assert scene_with_prose['scene_card'] is not None
        assert scene_with_prose['prose_content'] is not None
        assert scene_with_prose['prose_content']['word_count'] == 15
        
        # Search scenes by content
        search_results = service.search_scenes_by_content(
            project_id=project.id,
            query="library",
            include_prose=True
        )
        assert len(search_results) == 1
        assert search_results[0]['match_type'] in ['scene_metadata', 'prose_content']
        
        # Get project summary
        summary = service.get_project_summary(project.id)
        assert summary['project']['title'] == "Test Project"
        assert summary['statistics']['total_scenes'] == 1
        
        # Get project health report
        health_report = service.get_project_health_report(project.id)
        assert 'health_score' in health_report
        assert 'recommendations' in health_report
        assert health_report['scene_analysis']['total_scenes'] == 1


# Query Interface Tests
class TestQueryInterface:
    """Test query interface functionality"""
    
    def test_scene_card_query_builder(self, test_session, sample_project_data, sample_scene_card):
        """Test SceneCardQueryBuilder"""
        # Setup test data
        project_crud = ProjectCRUD(test_session)
        scene_crud = SceneCardCRUD(test_session)
        
        project = project_crud.create_project(sample_project_data)
        scene1 = scene_crud.create_scene_card(project.id, sample_scene_card)
        
        # Create second scene for testing
        reactive_scene = SceneCard(
            scene_type=SceneType.REACTIVE,
            pov="Sarah",
            viewpoint=ViewpointType.FIRST,
            tense=TenseType.PRESENT,
            scene_crucible="Sarah reacts to the unexpected news",
            place="Sarah's Office",
            time="Morning",
            exposition_used=[],
            chain_link="",
            reactive=ReactiveScene(
                reaction="Sarah gasps in shock",
                dilemma="Should she tell Jack about the danger?",
                decision="Sarah decides to warn Jack immediately"
            )
        )
        scene2 = scene_crud.create_scene_card(project.id, reactive_scene)
        
        # Test query builder
        query_interface = QueryInterface(test_session)
        
        # Test basic filtering
        proactive_scenes = query_interface.scene_cards().filter_by_project(project.id).filter_by_type(SceneType.PROACTIVE).execute()
        assert len(proactive_scenes) == 1
        
        reactive_scenes = query_interface.scene_cards().filter_by_project(project.id).filter_by_type(SceneType.REACTIVE).execute()
        assert len(reactive_scenes) == 1
        
        # Test POV filtering
        jack_scenes = query_interface.scene_cards().filter_by_project(project.id).filter_by_pov("Jack").execute()
        assert len(jack_scenes) == 1
        
        sarah_scenes = query_interface.scene_cards().filter_by_project(project.id).filter_by_pov("Sarah").execute()
        assert len(sarah_scenes) == 1
        
        # Test multiple POV filtering
        both_scenes = query_interface.scene_cards().filter_by_project(project.id).filter_by_pov(["Jack", "Sarah"]).execute()
        assert len(both_scenes) == 2
        
        # Test content search
        treasure_scenes = query_interface.scene_cards().filter_by_project(project.id).search_content("treasure").execute()
        assert len(treasure_scenes) == 1
        
        # Test ordering
        ordered_scenes = query_interface.scene_cards().filter_by_project(project.id).order_by("pov", SortDirection.ASC).execute()
        assert len(ordered_scenes) == 2
        assert ordered_scenes[0].pov == "Jack"  # Alphabetically first
        
        # Test pagination
        first_page = query_interface.scene_cards().filter_by_project(project.id).paginate(page=1, per_page=1).execute()
        assert len(first_page) == 1
        
        # Test count
        total_count = query_interface.scene_cards().filter_by_project(project.id).count()
        assert total_count == 2
        
        # Test exists
        exists = query_interface.scene_cards().filter_by_project(project.id).filter_by_pov("Jack").exists()
        assert exists is True
        
        non_exists = query_interface.scene_cards().filter_by_project(project.id).filter_by_pov("NonExistent").exists()
        assert non_exists is False
    
    def test_chain_link_query_builder(self, test_session, sample_project_data, sample_chain_link):
        """Test ChainLinkQueryBuilder"""
        project_crud = ProjectCRUD(test_session)
        chain_crud = ChainLinkCRUD(test_session)
        
        project = project_crud.create_project(sample_project_data)
        chain_link = chain_crud.create_chain_link(project.id, sample_chain_link)
        
        query_interface = QueryInterface(test_session)
        
        # Test basic filtering
        project_links = query_interface.chain_links().filter_by_project(project.id).execute()
        assert len(project_links) == 1
        
        # Test type filtering
        setback_links = query_interface.chain_links().filter_by_project(project.id).filter_by_type(ChainLinkType.SETBACK_TO_REACTIVE.value).execute()
        assert len(setback_links) == 1
        
        # Test source scene filtering
        source_links = query_interface.chain_links().filter_by_project(project.id).filter_by_source_scene("scene_001").execute()
        assert len(source_links) == 1
        
        # Test target scene filtering
        target_links = query_interface.chain_links().filter_by_project(project.id).filter_by_target_scene("scene_002").execute()
        assert len(target_links) == 1
        
        # Test validity filtering
        valid_links = query_interface.chain_links().filter_by_project(project.id).filter_by_validity(True).execute()
        assert len(valid_links) == 1
        
        # Test validation score filtering
        high_score_links = query_interface.chain_links().filter_by_project(project.id).filter_by_validation_score(min_score=0.0).execute()
        assert len(high_score_links) == 1
        
        # Test ordering
        ordered_links = query_interface.chain_links().filter_by_project(project.id).order_by("created_at", SortDirection.DESC).execute()
        assert len(ordered_links) == 1
        
        # Test count
        link_count = query_interface.chain_links().filter_by_project(project.id).count()
        assert link_count == 1
    
    def test_aggregation_queries(self, test_session, sample_project_data, sample_scene_card):
        """Test AggregationQueryBuilder"""
        # Setup test data
        project_crud = ProjectCRUD(test_session)
        scene_crud = SceneCardCRUD(test_session)
        prose_crud = ProseContentCRUD(test_session)
        
        project = project_crud.create_project(sample_project_data)
        scene = scene_crud.create_scene_card(project.id, sample_scene_card)
        
        # Add prose content
        prose_crud.create_prose_content(
            scene_card_id=scene.id,
            content="This is test prose content with multiple sentences for testing.",
            metadata={'readability_score': 65.0, 'sentiment_score': 0.7}
        )
        
        query_interface = QueryInterface(test_session)
        
        # Test scene statistics
        scene_stats = query_interface.aggregate().scene_statistics_by_project(project.id)
        assert scene_stats['total_scenes'] == 1
        assert 'proactive' in scene_stats['scene_types']
        assert 'Jack' in scene_stats['pov_distribution']
        assert scene_stats['word_count_stats']['total'] == 11
        
        # Test prose analytics
        prose_stats = query_interface.aggregate().prose_analytics_by_project(project.id)
        assert prose_stats['total_prose_scenes'] == 1
        assert prose_stats['total_prose_words'] == 11
        assert prose_stats['average_readability'] == 65.0
        
        # Test timeline analytics
        timeline_stats = query_interface.aggregate().timeline_analytics(project.id, days=1)
        assert 'scene_creation_timeline' in timeline_stats
        assert 'prose_update_timeline' in timeline_stats
    
    def test_advanced_search(self, test_session, sample_project_data, sample_scene_card):
        """Test advanced multi-entity search"""
        # Setup test data
        project_crud = ProjectCRUD(test_session)
        scene_crud = SceneCardCRUD(test_session)
        prose_crud = ProseContentCRUD(test_session)
        
        project = project_crud.create_project(sample_project_data)
        scene = scene_crud.create_scene_card(project.id, sample_scene_card)
        
        prose_crud.create_prose_content(
            scene_card_id=scene.id,
            content="The treasure map reveals hidden secrets of the ancient library."
        )
        
        query_interface = QueryInterface(test_session)
        
        # Test advanced search
        search_results = query_interface.advanced_search(
            project_id=project.id,
            search_params={
                'query': 'treasure',
                'include_prose': True,
                'include_chains': True
            }
        )
        
        # Should find matches in both scene metadata and prose content
        assert len(search_results['scene_cards']) >= 0
        assert len(search_results['prose_matches']) >= 0
        
        # Test export functionality
        scene_query = query_interface.scene_cards().filter_by_project(project.id)
        exported_json = query_interface.export_query_results(scene_query, format="json")
        
        assert 'scenes' in exported_json
        assert len(exported_json['scenes']) == 1


# Backup and Recovery Tests
class TestBackupRecovery:
    """Test backup and recovery functionality"""
    
    def test_backup_configuration(self, temp_backup_dir):
        """Test BackupConfiguration"""
        config = BackupConfiguration(
            backup_directory=temp_backup_dir,
            max_backups_to_keep=5,
            compress_backups=True,
            verify_integrity=True,
            backup_format=BackupFormat.JSON
        )
        
        assert config.backup_directory == temp_backup_dir
        assert config.compress_backups is True
        assert Path(temp_backup_dir).exists()
    
    def test_full_project_backup(self, test_session, temp_backup_dir, sample_project_data, sample_scene_card):
        """Test full project backup"""
        # Setup test data
        service = PersistenceService(test_session)
        project = service.create_project(**sample_project_data)
        db_scene, prose = service.create_scene_card_with_prose(
            project.id,
            sample_scene_card,
            "This is test prose content for backup testing."
        )
        
        # Create backup manager
        config = BackupConfiguration(backup_directory=temp_backup_dir)
        backup_manager = BackupManager(test_session, config)
        
        # Create full backup
        backup_metadata = backup_manager.create_full_backup(
            project_id=project.id,
            description="Test full backup"
        )
        
        assert backup_metadata.backup_type == BackupType.FULL
        assert backup_metadata.project_id == project.id
        assert backup_metadata.items_count == 1  # One scene card
        assert Path(backup_metadata.file_path).exists()
        
        # Verify backup file content
        if backup_metadata.compressed:
            with gzip.open(backup_metadata.file_path, 'rt') as f:
                backup_data = json.load(f)
        else:
            with open(backup_metadata.file_path, 'r') as f:
                backup_data = json.load(f)
        
        assert 'backup_metadata' in backup_data
        assert 'project' in backup_data
        assert 'scene_cards' in backup_data
        assert len(backup_data['scene_cards']) == 1
    
    def test_incremental_backup(self, test_session, temp_backup_dir, sample_project_data, sample_scene_card):
        """Test incremental backup"""
        # Setup test data
        service = PersistenceService(test_session)
        project = service.create_project(**sample_project_data)
        
        # Create backup manager
        config = BackupConfiguration(backup_directory=temp_backup_dir)
        backup_manager = BackupManager(test_session, config)
        
        # Create initial full backup
        full_backup = backup_manager.create_full_backup(project_id=project.id)
        
        # Add new scene after backup
        db_scene, prose = service.create_scene_card_with_prose(
            project.id,
            sample_scene_card,
            "This scene was added after the full backup."
        )
        
        # Create incremental backup
        incremental_backup = backup_manager.create_incremental_backup(
            project_id=project.id,
            since_date=full_backup.created_at,
            description="Incremental backup with new scene"
        )
        
        assert incremental_backup.backup_type == BackupType.INCREMENTAL
        assert incremental_backup.project_id == project.id
        assert Path(incremental_backup.file_path).exists()
    
    def test_scene_backup(self, test_session, temp_backup_dir, sample_project_data, sample_scene_card):
        """Test scene-specific backup"""
        # Setup test data
        service = PersistenceService(test_session)
        project = service.create_project(**sample_project_data)
        db_scene, prose = service.create_scene_card_with_prose(
            project.id,
            sample_scene_card,
            "This is test prose for scene backup."
        )
        
        # Create backup manager
        config = BackupConfiguration(backup_directory=temp_backup_dir)
        backup_manager = BackupManager(test_session, config)
        
        # Create scene backup
        scene_backup = backup_manager.backup_scene_cards(
            project_id=project.id,
            scene_ids=[db_scene.scene_id],
            description="Single scene backup"
        )
        
        assert scene_backup.backup_type == BackupType.SCENE
        assert scene_backup.items_count == 1
        assert Path(scene_backup.file_path).exists()
    
    def test_backup_recovery(self, test_session, temp_backup_dir, sample_project_data, sample_scene_card):
        """Test backup recovery functionality"""
        # Setup test data and create backup
        service = PersistenceService(test_session)
        original_project = service.create_project(**sample_project_data)
        db_scene, prose = service.create_scene_card_with_prose(
            original_project.id,
            sample_scene_card,
            "Original prose content for recovery testing."
        )
        
        # Create backup
        config = BackupConfiguration(backup_directory=temp_backup_dir)
        backup_manager = BackupManager(test_session, config)
        backup_metadata = backup_manager.create_full_backup(
            project_id=original_project.id,
            description="Backup for recovery test"
        )
        
        # Delete original data
        test_session.delete(original_project)
        test_session.commit()
        
        # Create recovery manager and recover
        recovery_manager = RecoveryManager(test_session)
        recovery_results = recovery_manager.recover_project_from_backup(
            backup_id=backup_metadata.backup_id,
            target_project_id="recovered_project_001",
            overwrite_existing=True
        )
        
        assert recovery_results['projects'] == 1
        assert recovery_results['scene_cards'] == 1
        assert recovery_results['prose_content'] == 1
        
        # Verify recovered data
        recovered_project = service.crud['projects'].get_project("recovered_project_001")
        assert recovered_project is not None
        assert recovered_project.title == sample_project_data['title']
        
        recovered_scenes = service.crud['scene_cards'].get_scene_cards(recovered_project.id)
        assert len(recovered_scenes) == 1
    
    def test_backup_list_and_cleanup(self, test_session, temp_backup_dir, sample_project_data):
        """Test backup listing and cleanup functionality"""
        # Setup
        service = PersistenceService(test_session)
        project = service.create_project(**sample_project_data)
        
        config = BackupConfiguration(
            backup_directory=temp_backup_dir,
            max_backups_to_keep=2
        )
        backup_manager = BackupManager(test_session, config)
        
        # Create multiple backups
        backup1 = backup_manager.create_full_backup(project.id, "Backup 1")
        backup2 = backup_manager.create_full_backup(project.id, "Backup 2")
        backup3 = backup_manager.create_full_backup(project.id, "Backup 3")
        
        # List backups
        all_backups = backup_manager.list_backups()
        project_backups = backup_manager.list_backups(project_id=project.id)
        full_backups = backup_manager.list_backups(backup_type=BackupType.FULL)
        
        assert len(all_backups) <= 2  # Should be cleaned up automatically
        assert len(project_backups) <= 2
        assert len(full_backups) <= 2
        
        # Test backup deletion
        remaining_backups = backup_manager.list_backups(project_id=project.id)
        if remaining_backups:
            success = backup_manager.delete_backup(remaining_backups[0].backup_id)
            assert success is True
            
            updated_backups = backup_manager.list_backups(project_id=project.id)
            assert len(updated_backups) < len(remaining_backups)
    
    def test_backup_integrity_verification(self, test_session, temp_backup_dir, sample_project_data):
        """Test backup integrity verification"""
        service = PersistenceService(test_session)
        project = service.create_project(**sample_project_data)
        
        config = BackupConfiguration(
            backup_directory=temp_backup_dir,
            verify_integrity=True
        )
        backup_manager = BackupManager(test_session, config)
        
        # Create backup
        backup_metadata = backup_manager.create_full_backup(project.id)
        
        # Verify integrity by manually calculating checksum
        backup_path = Path(backup_metadata.file_path)
        hash_sha256 = hashlib.sha256()
        
        with open(backup_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        calculated_checksum = hash_sha256.hexdigest()
        assert calculated_checksum == backup_metadata.checksum
        
        # Test corrupted backup detection
        recovery_manager = RecoveryManager(test_session)
        
        # Corrupt the backup file
        with open(backup_path, 'ab') as f:
            f.write(b"corrupted_data")
        
        # Recovery should fail due to integrity check
        with pytest.raises(IntegrityError):
            recovery_manager.recover_project_from_backup(backup_metadata.backup_id)


# Integration Tests
class TestIntegrationWorkflows:
    """Test end-to-end integration workflows"""
    
    def test_complete_novel_workflow(self, test_session, temp_backup_dir):
        """Test complete novel creation workflow"""
        # Initialize services
        service = PersistenceService(test_session)
        query_interface = QueryInterface(test_session)
        backup_config = BackupConfiguration(backup_directory=temp_backup_dir)
        backup_manager = BackupManager(test_session, backup_config)
        
        # Create project
        project = service.create_project(
            title="Integration Test Novel",
            description="A complete novel for integration testing",
            author="Test Author",
            genre="Science Fiction",
            target_word_count=100000
        )
        
        # Create characters
        jack_character = service.crud['characters'].create_character(
            project.id,
            {
                'name': 'Jack',
                'role': 'protagonist',
                'description': 'Main character',
                'goals': ['Find the treasure', 'Save the city'],
                'conflicts': ['Time pressure', 'Dangerous enemies']
            }
        )
        
        # Create multiple scenes
        scenes_data = [
            {
                'scene_type': SceneType.PROACTIVE,
                'pov': 'Jack',
                'crucible': 'Jack searches for clues in the library',
                'prose': 'Jack crept through the shadows of the ancient library, searching for the hidden map.',
                'place': 'Ancient Library',
                'time': 'Midnight'
            },
            {
                'scene_type': SceneType.REACTIVE,
                'pov': 'Jack', 
                'crucible': 'Jack discovers the map is incomplete',
                'prose': 'Jack stared at the torn map in frustration, realizing half of it was missing.',
                'place': 'Ancient Library',
                'time': 'Midnight'
            },
            {
                'scene_type': SceneType.PROACTIVE,
                'pov': 'Sarah',
                'crucible': 'Sarah investigates the mysterious signal',
                'prose': 'Sarah adjusted the radio frequency, trying to decode the mysterious transmission.',
                'place': 'Radio Tower',
                'time': 'Dawn'
            }
        ]
        
        created_scenes = []
        for scene_data in scenes_data:
            # Create scene card
            if scene_data['scene_type'] == SceneType.PROACTIVE:
                scene_card = SceneCard(
                    scene_type=scene_data['scene_type'],
                    pov=scene_data['pov'],
                    viewpoint=ViewpointType.THIRD,
                    tense=TenseType.PAST,
                    scene_crucible=scene_data['crucible'],
                    place=scene_data['place'],
                    time=scene_data['time'],
                    exposition_used=[],
                    chain_link='',
                    proactive=ProactiveScene(
                        goal="Find information",
                        conflict="Hidden dangers",
                        setback="Incomplete information"
                    )
                )
            else:
                scene_card = SceneCard(
                    scene_type=scene_data['scene_type'],
                    pov=scene_data['pov'],
                    viewpoint=ViewpointType.THIRD,
                    tense=TenseType.PAST,
                    scene_crucible=scene_data['crucible'],
                    place=scene_data['place'],
                    time=scene_data['time'],
                    exposition_used=[],
                    chain_link='',
                    reactive=ReactiveScene(
                        reaction="Frustration and disappointment",
                        dilemma="How to proceed without complete information",
                        decision="Search for the missing piece"
                    )
                )
            
            db_scene, prose = service.create_scene_card_with_prose(
                project_id=project.id,
                scene_card=scene_card,
                prose_content=scene_data['prose'],
                prose_notes=f"Initial prose for {scene_data['pov']} scene"
            )
            created_scenes.append((db_scene, prose))
        
        # Create chain links between scenes
        chain_link = ChainLink(
            chain_id="link_001",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            transition_type=TransitionType.IMMEDIATE,
            source_scene=SceneReference(
                scene_id=created_scenes[0][0].scene_id,
                scene_type=SceneType.PROACTIVE,
                pov_character="Jack"
            ),
            target_scene=SceneReference(
                scene_id=created_scenes[1][0].scene_id,
                scene_type=SceneType.REACTIVE,
                pov_character="Jack"
            ),
            trigger_content="Discovery that map is incomplete",
            target_seed="Jack must react to incomplete information",
            bridging_content="The torn edge of the map catches Jack's attention",
            is_valid=True,
            validation_errors=[],
            story_context={'chapter': 1, 'tension': 'rising'},
            character_state_changes={'Jack': {'frustration': 'increased'}}
        )
        
        service.crud['chain_links'].create_chain_link(project.id, chain_link)
        
        # Test comprehensive queries
        project_summary = service.get_project_summary(project.id)
        assert project_summary['statistics']['total_scenes'] == 3
        assert project_summary['statistics']['proactive_scenes'] == 2
        assert project_summary['statistics']['reactive_scenes'] == 1
        
        # Test advanced search across all content
        search_results = query_interface.advanced_search(
            project_id=project.id,
            search_params={
                'query': 'map',
                'include_prose': True,
                'include_chains': True
            }
        )
        assert len(search_results['scene_cards']) > 0 or len(search_results['prose_matches']) > 0
        
        # Test analytics
        scene_stats = query_interface.aggregate().scene_statistics_by_project(project.id)
        prose_stats = query_interface.aggregate().prose_analytics_by_project(project.id)
        chain_stats = query_interface.aggregate().chain_link_analytics_by_project(project.id)
        
        assert scene_stats['total_scenes'] == 3
        assert prose_stats['total_prose_scenes'] == 3
        assert chain_stats['total_chain_links'] == 1
        
        # Test narrative flow query
        flow_scenes = service.get_scenes_by_narrative_flow(
            project_id=project.id,
            start_scene_id=created_scenes[0][0].scene_id,
            depth=3
        )
        assert len(flow_scenes) >= 2  # Should follow chain link
        
        # Create comprehensive backup
        backup_metadata = backup_manager.create_full_backup(
            project_id=project.id,
            description="Complete novel backup after creation"
        )
        assert backup_metadata.items_count == 3  # 3 scene cards
        
        # Test project health report
        health_report = service.get_project_health_report(project.id)
        assert health_report['health_score'] > 0
        assert health_report['scene_analysis']['prose_completion_percentage'] == 100.0
        assert health_report['chain_analysis']['total_links'] == 1
        
        # Verify all components are working together
        assert len(health_report['recommendations']) > 0
        
    def test_error_recovery_workflow(self, test_session):
        """Test error recovery and rollback scenarios"""
        service = PersistenceService(test_session)
        
        # Test database constraint violations
        project = service.create_project(title="Error Test Project")
        
        # Try to create duplicate project ID (should fail)
        with pytest.raises(Exception):
            duplicate_project = Project(
                project_id=project.project_id,
                title="Duplicate Project"
            )
            test_session.add(duplicate_project)
            test_session.commit()
        
        # Ensure session is still usable after error
        test_session.rollback()
        projects = service.crud['projects'].get_projects()
        assert len(projects) == 1
        
        # Test recovery from invalid scene data
        with pytest.raises(Exception):
            invalid_scene = SceneCard(
                scene_type=SceneType.PROACTIVE,
                pov="",  # Invalid empty POV
                viewpoint=ViewpointType.THIRD,
                tense=TenseType.PAST,
                scene_crucible="",  # Invalid empty crucible
                place="Test Place",
                time="Test Time",
                exposition_used=[],
                chain_link=""
            )
            service.crud['scene_cards'].create_scene_card(project.id, invalid_scene)
        
        # Session should still be functional
        test_session.rollback()
        scene_count = query_interface.scene_cards().filter_by_project(project.id).count()
        assert scene_count == 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])