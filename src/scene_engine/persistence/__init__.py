"""
Scene Engine Persistence Layer

This implements Task 48: Persistence Layer
Provides storage for Scene Cards, prose content, and chain links with CRUD operations,
query capabilities, and backup/recovery mechanisms.
"""

from .models import (
    Base, engine, SessionLocal, get_db,
    Project, SceneCardDB, ProseContent, ChainLinkDB,
    Character, SceneSequenceDB, ValidationLog
)
from .crud import (
    SceneCardCRUD, ChainLinkCRUD, ProseContentCRUD,
    ProjectCRUD, CharacterCRUD, SceneSequenceCRUD
)
from .service import PersistenceService
from .backup import BackupManager, RecoveryManager

__all__ = [
    # Database models
    "Base", "engine", "SessionLocal", "get_db",
    "Project", "SceneCardDB", "ProseContent", "ChainLinkDB",
    "Character", "SceneSequenceDB", "ValidationLog",
    # CRUD operations
    "SceneCardCRUD", "ChainLinkCRUD", "ProseContentCRUD",
    "ProjectCRUD", "CharacterCRUD", "SceneSequenceCRUD",
    # High-level service
    "PersistenceService",
    # Backup/Recovery
    "BackupManager", "RecoveryManager"
]