"""
Database Models for Scene Engine Persistence

This implements subtask 48.1: Design Data Models for Scene Cards, Prose, and Chain Links
Defines SQLAlchemy ORM models for storing all scene engine components.
"""

from typing import Optional, List
from datetime import datetime
import json
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, Boolean, 
    Float, ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.dialects.sqlite import BLOB
import enum

# Database setup
Base = declarative_base()

# Create engine (will be configured by environment)
engine = create_engine(
    "sqlite:///scene_engine.db",
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    connect_args={"check_same_thread": False}  # For SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enums for database
class SceneTypeEnum(enum.Enum):
    PROACTIVE = "proactive"
    REACTIVE = "reactive"


class ViewpointTypeEnum(enum.Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    OMNISCIENT = "omniscient"


class TenseTypeEnum(enum.Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class OutcomeTypeEnum(enum.Enum):
    SETBACK = "setback"
    VICTORY = "victory"
    MIXED = "mixed"


class CompressionTypeEnum(enum.Enum):
    FULL = "full"
    SUMMARIZED = "summarized"
    SKIP = "skip"


class ChainLinkTypeEnum(enum.Enum):
    SETBACK_TO_REACTIVE = "setback_to_reactive"
    DECISION_TO_PROACTIVE = "decision_to_proactive"
    VICTORY_TO_PROACTIVE = "victory_to_proactive"
    MIXED_TO_REACTIVE = "mixed_to_reactive"
    MIXED_TO_PROACTIVE = "mixed_to_proactive"
    SEQUEL_BRIDGE = "sequel_bridge"
    CHAPTER_BREAK = "chapter_break"


class TransitionTypeEnum(enum.Enum):
    IMMEDIATE = "immediate"
    COMPRESSED = "compressed"
    SEQUEL = "sequel"
    TIME_CUT = "time_cut"
    POV_SHIFT = "pov_shift"
    LOCATION_SHIFT = "location_shift"


class ChainStrengthEnum(enum.Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    BROKEN = "broken"


# Core database models

class Project(Base):
    """Top-level project containing scenes and sequences"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    author = Column(String(100))
    genre = Column(String(50))
    target_word_count = Column(Integer)
    current_word_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(String(20), default="1.0.0")
    status = Column(String(20), default="draft")  # draft, in_progress, completed
    
    # Settings
    settings = Column(JSON)  # Project-specific settings
    
    # Relationships
    scene_cards = relationship("SceneCardDB", back_populates="project", cascade="all, delete-orphan")
    chain_links = relationship("ChainLinkDB", back_populates="project", cascade="all, delete-orphan")
    sequences = relationship("SceneSequenceDB", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}')>"


class Character(Base):
    """Character information referenced by scenes"""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    role = Column(String(50))  # protagonist, antagonist, supporting, etc.
    description = Column(Text)
    
    # Character arc information
    goals = Column(JSON)  # List of character goals
    conflicts = Column(JSON)  # List of character conflicts
    arc_phase = Column(String(50))  # Current phase in character arc
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="characters")
    
    # Indexes
    __table_args__ = (
        Index("idx_character_project_name", "project_id", "name"),
    )
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', role='{self.role}')>"


class SceneCardDB(Base):
    """Database model for Scene Cards"""
    __tablename__ = "scene_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Core scene information
    scene_id = Column(String(100), nullable=False, index=True)
    scene_type = Column(Enum(SceneTypeEnum), nullable=False)
    pov = Column(String(100), nullable=False)
    viewpoint = Column(Enum(ViewpointTypeEnum), nullable=False)
    tense = Column(Enum(TenseTypeEnum), nullable=False)
    
    # Scene content
    scene_crucible = Column(Text, nullable=False)
    place = Column(String(200))
    time = Column(String(200))
    
    # Scene structure data (stored as JSON)
    proactive_data = Column(JSON)  # Proactive scene structure
    reactive_data = Column(JSON)   # Reactive scene structure
    
    # Metadata
    exposition_used = Column(JSON)  # List of exposition items
    chain_link = Column(Text)      # Chain link description
    word_count = Column(Integer, default=0)
    estimated_reading_time = Column(Integer, default=0)
    
    # Status and tracking
    status = Column(String(20), default="draft")  # draft, in_progress, completed
    quality_score = Column(Float, default=0.0)
    validation_status = Column(String(20), default="pending")  # pending, valid, invalid
    
    # Ordering and structure
    chapter_number = Column(Integer)
    scene_number = Column(Integer)
    sequence_order = Column(Integer)  # Order within sequence
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_validated = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="scene_cards")
    prose_content = relationship("ProseContent", back_populates="scene_card", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_scene_project_id", "project_id"),
        Index("idx_scene_type_pov", "scene_type", "pov"),
        Index("idx_scene_chapter_number", "chapter_number", "scene_number"),
        Index("idx_scene_status", "status"),
        UniqueConstraint("project_id", "scene_id", name="uq_scene_project_scene_id"),
    )
    
    def __repr__(self):
        return f"<SceneCardDB(id={self.id}, scene_id='{self.scene_id}', type='{self.scene_type}')>"


class ProseContent(Base):
    """Storage for scene prose content"""
    __tablename__ = "prose_content"
    
    id = Column(Integer, primary_key=True, index=True)
    scene_card_id = Column(Integer, ForeignKey("scene_cards.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="markdown")  # markdown, plain, html
    
    # Metadata
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=0)
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    version_notes = Column(Text)
    is_current_version = Column(Boolean, default=True)
    
    # Content analysis
    readability_score = Column(Float)
    sentiment_score = Column(Float)
    keyword_tags = Column(JSON)  # List of extracted keywords
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scene_card = relationship("SceneCardDB", back_populates="prose_content")
    
    # Indexes
    __table_args__ = (
        Index("idx_prose_scene_card", "scene_card_id"),
        Index("idx_prose_current_version", "is_current_version"),
        Index("idx_prose_word_count", "word_count"),
    )
    
    def __repr__(self):
        return f"<ProseContent(id={self.id}, scene_card_id={self.scene_card_id}, words={self.word_count})>"


class ChainLinkDB(Base):
    """Database model for Chain Links"""
    __tablename__ = "chain_links"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Core chain link data
    chain_id = Column(String(100), nullable=False, index=True)
    chain_type = Column(Enum(ChainLinkTypeEnum), nullable=False)
    transition_type = Column(Enum(TransitionTypeEnum), default=TransitionTypeEnum.IMMEDIATE)
    
    # Source and target scene references
    source_scene_id = Column(String(100), nullable=False)
    source_scene_type = Column(Enum(SceneTypeEnum), nullable=False)
    source_pov = Column(String(100), nullable=False)
    
    target_scene_id = Column(String(100))
    target_scene_type = Column(Enum(SceneTypeEnum))
    target_pov = Column(String(100))
    
    # Transition content
    trigger_content = Column(Text, nullable=False)
    target_seed = Column(Text, nullable=False)
    bridging_content = Column(Text)
    
    # Metadata
    chain_strength = Column(Enum(ChainStrengthEnum), default=ChainStrengthEnum.MODERATE)
    validation_score = Column(Float, default=0.0)
    emotional_continuity = Column(Float, default=0.5)
    narrative_necessity = Column(Float, default=0.5)
    
    # Status
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON)  # List of validation errors
    
    # Context
    story_context = Column(JSON)
    character_state_changes = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_validated = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="chain_links")
    
    # Indexes
    __table_args__ = (
        Index("idx_chain_project_id", "project_id"),
        Index("idx_chain_source_scene", "source_scene_id"),
        Index("idx_chain_target_scene", "target_scene_id"),
        Index("idx_chain_type", "chain_type"),
        Index("idx_chain_validation", "is_valid", "validation_score"),
        UniqueConstraint("project_id", "chain_id", name="uq_chain_project_chain_id"),
    )
    
    def __repr__(self):
        return f"<ChainLinkDB(id={self.id}, chain_id='{self.chain_id}', type='{self.chain_type}')>"


class SceneSequenceDB(Base):
    """Database model for Scene Sequences"""
    __tablename__ = "scene_sequences"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Core sequence data
    sequence_id = Column(String(100), nullable=False, index=True)
    title = Column(String(200))
    description = Column(Text)
    
    # Scene references (stored as JSON list)
    scene_ids = Column(JSON, nullable=False)  # List of scene IDs in order
    
    # Sequence metrics
    total_word_count = Column(Integer, default=0)
    estimated_reading_time = Column(Integer, default=0)
    scene_count = Column(Integer, default=0)
    
    # Quality metrics
    narrative_cohesion = Column(Float, default=0.5)
    pacing_score = Column(Float, default=0.5)
    character_development = Column(Float, default=0.5)
    overall_quality = Column(Float, default=0.5)
    
    # Structure
    dominant_pov = Column(String(100))
    sequence_tone = Column(String(50))
    chapter_start = Column(Integer)
    chapter_end = Column(Integer)
    
    # Status
    status = Column(String(20), default="draft")  # draft, in_progress, completed
    validation_status = Column(String(20), default="pending")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_validated = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="sequences")
    
    # Indexes
    __table_args__ = (
        Index("idx_sequence_project_id", "project_id"),
        Index("idx_sequence_status", "status"),
        Index("idx_sequence_quality", "overall_quality"),
        UniqueConstraint("project_id", "sequence_id", name="uq_sequence_project_sequence_id"),
    )
    
    def __repr__(self):
        return f"<SceneSequenceDB(id={self.id}, sequence_id='{self.sequence_id}', scenes={self.scene_count})>"


class ValidationLog(Base):
    """Log of validation operations and results"""
    __tablename__ = "validation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Target of validation
    target_type = Column(String(50), nullable=False)  # scene_card, chain_link, sequence
    target_id = Column(String(100), nullable=False)   # ID of the validated object
    
    # Validation results
    validation_type = Column(String(50), nullable=False)  # structural, snowflake, quality
    is_valid = Column(Boolean, nullable=False)
    validation_score = Column(Float)
    
    # Details
    errors = Column(JSON)      # List of error messages
    warnings = Column(JSON)    # List of warning messages
    suggestions = Column(JSON) # List of improvement suggestions
    
    # Context
    validator_version = Column(String(20))
    validation_context = Column(JSON)  # Additional context data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_validation_project_target", "project_id", "target_type", "target_id"),
        Index("idx_validation_results", "is_valid", "validation_score"),
        Index("idx_validation_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<ValidationLog(id={self.id}, target='{self.target_type}:{self.target_id}', valid={self.is_valid})>"


class BackupRecord(Base):
    """Record of backup operations"""
    __tablename__ = "backup_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Backup metadata
    backup_id = Column(String(100), nullable=False, unique=True)
    backup_type = Column(String(20), nullable=False)  # full, incremental, scene, sequence
    backup_path = Column(String(500), nullable=False)
    
    # Backup contents
    items_backed_up = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    checksum = Column(String(64))  # SHA-256 checksum
    
    # Metadata
    description = Column(Text)
    backup_format = Column(String(20), default="json")  # json, sqlite, archive
    compression_used = Column(Boolean, default=False)
    
    # Status
    status = Column(String(20), default="completed")  # in_progress, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiration
    
    # Indexes
    __table_args__ = (
        Index("idx_backup_project_id", "project_id"),
        Index("idx_backup_type_status", "backup_type", "status"),
        Index("idx_backup_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<BackupRecord(id={self.id}, backup_id='{self.backup_id}', type='{self.backup_type}')>"


# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)


# Database utility functions
def get_engine():
    """Get the database engine"""
    return engine


def get_session_local():
    """Get session local factory"""
    return SessionLocal


def init_database(database_url: Optional[str] = None):
    """Initialize database with optional custom URL"""
    global engine, SessionLocal
    
    if database_url:
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    create_tables()


if __name__ == "__main__":
    # Create tables when run directly
    create_tables()
    print("Database tables created successfully!")