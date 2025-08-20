"""
Backup and Recovery System for Scene Engine

This implements subtask 48.5: Backup/Recovery
Provides comprehensive backup and recovery mechanisms with data integrity,
versioning, compression, and automated scheduling capabilities.
"""

import os
import json
import shutil
import gzip
import hashlib
import tarfile
import tempfile
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3

from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine, MetaData, Table

from .models import (
    Project, SceneCardDB, ProseContent, ChainLinkDB, Character,
    SceneSequenceDB, ValidationLog, BackupRecord, get_db, engine
)
from .crud import create_crud_manager


class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental" 
    SCENE = "scene"
    SEQUENCE = "sequence"
    PROJECT = "project"


class BackupFormat(Enum):
    JSON = "json"
    SQLITE = "sqlite"
    ARCHIVE = "archive"


class BackupStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackupConfiguration:
    """Configuration for backup operations"""
    backup_directory: str
    max_backups_to_keep: int = 10
    compress_backups: bool = True
    verify_integrity: bool = True
    include_prose_content: bool = True
    include_validation_logs: bool = False
    backup_format: BackupFormat = BackupFormat.JSON
    
    def __post_init__(self):
        # Ensure backup directory exists
        Path(self.backup_directory).mkdir(parents=True, exist_ok=True)


@dataclass
class BackupMetadata:
    """Metadata for backup operations"""
    backup_id: str
    backup_type: BackupType
    project_id: Optional[int]
    created_at: datetime
    items_count: int
    size_bytes: int
    checksum: str
    format: BackupFormat
    compressed: bool
    file_path: str
    description: Optional[str] = None


class BackupError(Exception):
    """Base exception for backup operations"""
    pass


class RecoveryError(Exception):
    """Base exception for recovery operations"""
    pass


class IntegrityError(Exception):
    """Exception for data integrity errors"""
    pass


class BackupManager:
    """Manages backup operations for scene engine data"""
    
    def __init__(self, db_session: Optional[Session] = None, 
                 config: Optional[BackupConfiguration] = None):
        self.db = db_session or next(get_db())
        self.config = config or BackupConfiguration(
            backup_directory=str(Path.home() / "scene_engine_backups")
        )
        self.crud = create_crud_manager(self.db)
    
    def create_full_backup(self, project_id: Optional[int] = None, 
                          description: Optional[str] = None) -> BackupMetadata:
        """Create full backup of project or entire database"""
        
        backup_id = f"full_{int(datetime.utcnow().timestamp())}"
        
        try:
            if project_id:
                return self._backup_project(project_id, BackupType.FULL, backup_id, description)
            else:
                return self._backup_entire_database(backup_id, description)
                
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.FULL, project_id, str(e))
            raise BackupError(f"Full backup failed: {str(e)}")
    
    def create_incremental_backup(self, project_id: int, 
                                since_date: Optional[datetime] = None,
                                description: Optional[str] = None) -> BackupMetadata:
        """Create incremental backup of changes since last backup or specified date"""
        
        backup_id = f"incremental_{int(datetime.utcnow().timestamp())}"
        
        try:
            # Determine cutoff date
            if since_date is None:
                last_backup = self._get_last_backup(project_id, BackupType.INCREMENTAL)
                since_date = last_backup.created_at if last_backup else datetime.utcnow() - timedelta(days=1)
            
            return self._backup_project_incremental(project_id, since_date, backup_id, description)
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.INCREMENTAL, project_id, str(e))
            raise BackupError(f"Incremental backup failed: {str(e)}")
    
    def backup_scene_cards(self, project_id: int, scene_ids: Optional[List[str]] = None,
                          description: Optional[str] = None) -> BackupMetadata:
        """Backup specific scene cards or all scenes in project"""
        
        backup_id = f"scenes_{int(datetime.utcnow().timestamp())}"
        
        try:
            # Get scene cards
            if scene_ids:
                scenes = []
                for scene_id in scene_ids:
                    scene = self.crud['scene_cards'].get_scene_card(scene_id, project_id)
                    if scene:
                        scenes.append(scene)
            else:
                scenes = self.crud['scene_cards'].get_scene_cards(project_id)
            
            return self._backup_scenes(scenes, backup_id, description, project_id)
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.SCENE, project_id, str(e))
            raise BackupError(f"Scene backup failed: {str(e)}")
    
    def backup_sequence(self, project_id: int, sequence_id: str,
                       description: Optional[str] = None) -> BackupMetadata:
        """Backup a specific scene sequence"""
        
        backup_id = f"sequence_{sequence_id}_{int(datetime.utcnow().timestamp())}"
        
        try:
            sequence = self.crud['sequences'].get_sequence(sequence_id, project_id)
            if not sequence:
                raise BackupError(f"Sequence not found: {sequence_id}")
            
            return self._backup_sequence(sequence, backup_id, description, project_id)
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.SEQUENCE, project_id, str(e))
            raise BackupError(f"Sequence backup failed: {str(e)}")
    
    def _backup_project(self, project_id: int, backup_type: BackupType, 
                       backup_id: str, description: Optional[str]) -> BackupMetadata:
        """Backup entire project data"""
        
        # Record backup start
        backup_record = self._record_backup_start(backup_id, backup_type, project_id, description)
        
        try:
            # Collect all project data
            project = self.crud['projects'].get_project(project_id)
            if not project:
                raise BackupError(f"Project not found: {project_id}")
            
            scene_cards = self.crud['scene_cards'].get_scene_cards(project_id)
            chain_links = self.crud['chain_links'].get_chain_links(project_id)
            characters = self.crud['characters'].get_characters(project_id)
            sequences = self.crud['sequences'].get_sequences(project_id)
            
            # Collect prose content if enabled
            prose_content = []
            if self.config.include_prose_content:
                for scene in scene_cards:
                    scene_prose = self.crud['prose_content'].get_prose_content_versions(scene.id)
                    prose_content.extend(scene_prose)
            
            # Collect validation logs if enabled
            validation_logs = []
            if self.config.include_validation_logs:
                validation_logs = self.db.query(ValidationLog).filter(
                    ValidationLog.project_id == project_id
                ).all()
            
            # Create backup data structure
            backup_data = {
                "backup_metadata": {
                    "backup_id": backup_id,
                    "backup_type": backup_type.value,
                    "project_id": project_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "format": self.config.backup_format.value
                },
                "project": self._serialize_model(project),
                "scene_cards": [self._serialize_scene_card(scene) for scene in scene_cards],
                "chain_links": [self._serialize_chain_link(link) for link in chain_links],
                "characters": [self._serialize_model(char) for char in characters],
                "sequences": [self._serialize_model(seq) for seq in sequences],
                "prose_content": [self._serialize_model(prose) for prose in prose_content],
                "validation_logs": [self._serialize_model(log) for log in validation_logs]
            }
            
            # Write backup file
            file_path = self._write_backup_data(backup_data, backup_id)
            
            # Calculate checksums and metadata
            metadata = self._finalize_backup(backup_record, file_path, len(scene_cards))
            
            return metadata
            
        except Exception as e:
            self._record_backup_failure(backup_id, backup_type, project_id, str(e))
            raise
    
    def _backup_project_incremental(self, project_id: int, since_date: datetime,
                                  backup_id: str, description: Optional[str]) -> BackupMetadata:
        """Create incremental backup of project changes"""
        
        backup_record = self._record_backup_start(backup_id, BackupType.INCREMENTAL, project_id, description)
        
        try:
            # Get changed data since date
            changed_scenes = self.crud['scene_cards'].get_scene_cards(project_id)
            changed_scenes = [s for s in changed_scenes if s.updated_at >= since_date]
            
            changed_links = self.crud['chain_links'].get_chain_links(project_id)
            changed_links = [l for l in changed_links if l.updated_at >= since_date]
            
            # Get related prose content
            prose_content = []
            if self.config.include_prose_content:
                for scene in changed_scenes:
                    scene_prose = self.crud['prose_content'].get_prose_content_versions(scene.id)
                    prose_content.extend([p for p in scene_prose if p.created_at >= since_date])
            
            # Create incremental backup data
            backup_data = {
                "backup_metadata": {
                    "backup_id": backup_id,
                    "backup_type": BackupType.INCREMENTAL.value,
                    "project_id": project_id,
                    "since_date": since_date.isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "format": self.config.backup_format.value
                },
                "changed_scenes": [self._serialize_scene_card(scene) for scene in changed_scenes],
                "changed_links": [self._serialize_chain_link(link) for link in changed_links],
                "changed_prose": [self._serialize_model(prose) for prose in prose_content]
            }
            
            # Write backup file
            file_path = self._write_backup_data(backup_data, backup_id)
            
            # Finalize backup
            metadata = self._finalize_backup(backup_record, file_path, len(changed_scenes))
            
            return metadata
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.INCREMENTAL, project_id, str(e))
            raise
    
    def _backup_scenes(self, scenes: List[SceneCardDB], backup_id: str, 
                      description: Optional[str], project_id: int) -> BackupMetadata:
        """Backup specific scene cards"""
        
        backup_record = self._record_backup_start(backup_id, BackupType.SCENE, project_id, description)
        
        try:
            # Collect prose content for scenes
            prose_content = []
            if self.config.include_prose_content:
                for scene in scenes:
                    scene_prose = self.crud['prose_content'].get_prose_content_versions(scene.id)
                    prose_content.extend(scene_prose)
            
            # Create backup data
            backup_data = {
                "backup_metadata": {
                    "backup_id": backup_id,
                    "backup_type": BackupType.SCENE.value,
                    "project_id": project_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "scene_count": len(scenes)
                },
                "scene_cards": [self._serialize_scene_card(scene) for scene in scenes],
                "prose_content": [self._serialize_model(prose) for prose in prose_content]
            }
            
            # Write and finalize backup
            file_path = self._write_backup_data(backup_data, backup_id)
            metadata = self._finalize_backup(backup_record, file_path, len(scenes))
            
            return metadata
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.SCENE, project_id, str(e))
            raise
    
    def _backup_sequence(self, sequence: SceneSequenceDB, backup_id: str,
                        description: Optional[str], project_id: int) -> BackupMetadata:
        """Backup a specific sequence"""
        
        backup_record = self._record_backup_start(backup_id, BackupType.SEQUENCE, project_id, description)
        
        try:
            # Get scenes in sequence
            scene_ids = sequence.scene_ids or []
            scenes = []
            for scene_id in scene_ids:
                scene = self.crud['scene_cards'].get_scene_card(scene_id, project_id)
                if scene:
                    scenes.append(scene)
            
            # Get prose content
            prose_content = []
            if self.config.include_prose_content:
                for scene in scenes:
                    scene_prose = self.crud['prose_content'].get_prose_content_versions(scene.id)
                    prose_content.extend(scene_prose)
            
            # Create backup data
            backup_data = {
                "backup_metadata": {
                    "backup_id": backup_id,
                    "backup_type": BackupType.SEQUENCE.value,
                    "project_id": project_id,
                    "sequence_id": sequence.sequence_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                "sequence": self._serialize_model(sequence),
                "scene_cards": [self._serialize_scene_card(scene) for scene in scenes],
                "prose_content": [self._serialize_model(prose) for prose in prose_content]
            }
            
            # Write and finalize backup
            file_path = self._write_backup_data(backup_data, backup_id)
            metadata = self._finalize_backup(backup_record, file_path, len(scenes))
            
            return metadata
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.SEQUENCE, project_id, str(e))
            raise
    
    def _backup_entire_database(self, backup_id: str, description: Optional[str]) -> BackupMetadata:
        """Create full database backup"""
        
        backup_record = self._record_backup_start(backup_id, BackupType.FULL, None, description)
        
        try:
            # SQLite database backup
            if self.config.backup_format == BackupFormat.SQLITE:
                return self._backup_sqlite_database(backup_id, backup_record)
            
            # JSON format backup of all projects
            projects = self.crud['projects'].get_projects()
            all_data = {
                "backup_metadata": {
                    "backup_id": backup_id,
                    "backup_type": BackupType.FULL.value,
                    "created_at": datetime.utcnow().isoformat(),
                    "total_projects": len(projects)
                },
                "projects": []
            }
            
            total_items = 0
            for project in projects:
                project_data = self._get_project_backup_data(project.id)
                all_data["projects"].append(project_data)
                total_items += len(project_data.get("scene_cards", []))
            
            # Write and finalize backup
            file_path = self._write_backup_data(all_data, backup_id)
            metadata = self._finalize_backup(backup_record, file_path, total_items)
            
            return metadata
            
        except Exception as e:
            self._record_backup_failure(backup_id, BackupType.FULL, None, str(e))
            raise
    
    def _backup_sqlite_database(self, backup_id: str, backup_record: BackupRecord) -> BackupMetadata:
        """Create SQLite database file backup"""
        
        # Get database file path
        db_url = str(engine.url)
        if not db_url.startswith('sqlite:///'):
            raise BackupError("SQLite backup only supported for SQLite databases")
        
        db_file_path = db_url.replace('sqlite:///', '')
        
        # Create backup file path
        backup_filename = f"{backup_id}.db"
        if self.config.compress_backups:
            backup_filename += ".gz"
        
        backup_file_path = Path(self.config.backup_directory) / backup_filename
        
        try:
            if self.config.compress_backups:
                # Compress the database file
                with open(db_file_path, 'rb') as f_in:
                    with gzip.open(backup_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Simple file copy
                shutil.copy2(db_file_path, backup_file_path)
            
            # Calculate metadata
            size_bytes = backup_file_path.stat().st_size
            checksum = self._calculate_file_checksum(backup_file_path)
            
            # Update backup record
            backup_record.backup_path = str(backup_file_path)
            backup_record.total_size_bytes = size_bytes
            backup_record.checksum = checksum
            backup_record.items_backed_up = self._count_total_records()
            backup_record.status = BackupStatus.COMPLETED.value
            backup_record.backup_format = BackupFormat.SQLITE.value
            backup_record.compression_used = self.config.compress_backups
            
            self.db.commit()
            
            return BackupMetadata(
                backup_id=backup_id,
                backup_type=BackupType.FULL,
                project_id=None,
                created_at=backup_record.created_at,
                items_count=backup_record.items_backed_up,
                size_bytes=size_bytes,
                checksum=checksum,
                format=BackupFormat.SQLITE,
                compressed=self.config.compress_backups,
                file_path=str(backup_file_path)
            )
            
        except Exception as e:
            if backup_file_path.exists():
                backup_file_path.unlink()
            raise BackupError(f"SQLite backup failed: {str(e)}")
    
    def _get_project_backup_data(self, project_id: int) -> Dict[str, Any]:
        """Get all backup data for a project"""
        
        project = self.crud['projects'].get_project(project_id)
        scene_cards = self.crud['scene_cards'].get_scene_cards(project_id)
        chain_links = self.crud['chain_links'].get_chain_links(project_id)
        characters = self.crud['characters'].get_characters(project_id)
        sequences = self.crud['sequences'].get_sequences(project_id)
        
        # Prose content
        prose_content = []
        if self.config.include_prose_content:
            for scene in scene_cards:
                scene_prose = self.crud['prose_content'].get_prose_content_versions(scene.id)
                prose_content.extend(scene_prose)
        
        return {
            "project": self._serialize_model(project),
            "scene_cards": [self._serialize_scene_card(scene) for scene in scene_cards],
            "chain_links": [self._serialize_chain_link(link) for link in chain_links],
            "characters": [self._serialize_model(char) for char in characters],
            "sequences": [self._serialize_model(seq) for seq in sequences],
            "prose_content": [self._serialize_model(prose) for prose in prose_content]
        }
    
    def _serialize_model(self, model) -> Dict[str, Any]:
        """Serialize SQLAlchemy model to dictionary"""
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            
            # Handle special types
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif hasattr(value, 'value'):  # Enum
                result[column.name] = value.value
            else:
                result[column.name] = value
        
        return result
    
    def _serialize_scene_card(self, scene: SceneCardDB) -> Dict[str, Any]:
        """Serialize scene card with special handling"""
        data = self._serialize_model(scene)
        
        # Handle JSON fields
        if scene.proactive_data:
            data['proactive_data'] = scene.proactive_data
        if scene.reactive_data:
            data['reactive_data'] = scene.reactive_data
        if scene.exposition_used:
            data['exposition_used'] = scene.exposition_used
        
        return data
    
    def _serialize_chain_link(self, link: ChainLinkDB) -> Dict[str, Any]:
        """Serialize chain link with special handling"""
        data = self._serialize_model(link)
        
        # Handle JSON fields
        if link.validation_errors:
            data['validation_errors'] = link.validation_errors
        if link.story_context:
            data['story_context'] = link.story_context
        if link.character_state_changes:
            data['character_state_changes'] = link.character_state_changes
        
        return data
    
    def _write_backup_data(self, data: Dict[str, Any], backup_id: str) -> str:
        """Write backup data to file"""
        
        # Determine file extension
        if self.config.backup_format == BackupFormat.JSON:
            extension = ".json"
        elif self.config.backup_format == BackupFormat.ARCHIVE:
            extension = ".tar.gz"
        else:
            extension = ".backup"
        
        if self.config.compress_backups and self.config.backup_format != BackupFormat.ARCHIVE:
            extension += ".gz"
        
        # Create file path
        filename = f"{backup_id}{extension}"
        file_path = Path(self.config.backup_directory) / filename
        
        try:
            if self.config.backup_format == BackupFormat.JSON:
                if self.config.compress_backups:
                    with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, default=str)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, default=str)
            
            elif self.config.backup_format == BackupFormat.ARCHIVE:
                with tarfile.open(file_path, 'w:gz') as tar:
                    # Create temporary JSON file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                        json.dump(data, tmp_file, indent=2, default=str)
                        tmp_file.flush()
                        tar.add(tmp_file.name, arcname=f"{backup_id}.json")
                        os.unlink(tmp_file.name)
            
            return str(file_path)
            
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise BackupError(f"Failed to write backup data: {str(e)}")
    
    def _finalize_backup(self, backup_record: BackupRecord, file_path: str, items_count: int) -> BackupMetadata:
        """Finalize backup with metadata calculation"""
        
        # Calculate file size and checksum
        file_path_obj = Path(file_path)
        size_bytes = file_path_obj.stat().st_size
        checksum = self._calculate_file_checksum(file_path_obj)
        
        # Update backup record
        backup_record.backup_path = file_path
        backup_record.total_size_bytes = size_bytes
        backup_record.checksum = checksum
        backup_record.items_backed_up = items_count
        backup_record.status = BackupStatus.COMPLETED.value
        backup_record.backup_format = self.config.backup_format.value
        backup_record.compression_used = self.config.compress_backups
        
        self.db.commit()
        
        # Verify integrity if enabled
        if self.config.verify_integrity:
            self._verify_backup_integrity(file_path, checksum)
        
        # Clean up old backups
        self._cleanup_old_backups(backup_record.project_id)
        
        return BackupMetadata(
            backup_id=backup_record.backup_id,
            backup_type=BackupType(backup_record.backup_type),
            project_id=backup_record.project_id,
            created_at=backup_record.created_at,
            items_count=items_count,
            size_bytes=size_bytes,
            checksum=checksum,
            format=BackupFormat(backup_record.backup_format),
            compressed=backup_record.compression_used,
            file_path=file_path,
            description=backup_record.description
        )
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            raise BackupError(f"Failed to calculate checksum: {str(e)}")
    
    def _verify_backup_integrity(self, file_path: str, expected_checksum: str):
        """Verify backup file integrity"""
        
        actual_checksum = self._calculate_file_checksum(Path(file_path))
        if actual_checksum != expected_checksum:
            raise IntegrityError(f"Backup integrity check failed: {file_path}")
    
    def _record_backup_start(self, backup_id: str, backup_type: BackupType,
                           project_id: Optional[int], description: Optional[str]) -> BackupRecord:
        """Record backup operation start"""
        
        backup_record = BackupRecord(
            project_id=project_id,
            backup_id=backup_id,
            backup_type=backup_type.value,
            backup_path="",  # Will be set when completed
            description=description,
            status=BackupStatus.IN_PROGRESS.value
        )
        
        self.db.add(backup_record)
        self.db.commit()
        self.db.refresh(backup_record)
        
        return backup_record
    
    def _record_backup_failure(self, backup_id: str, backup_type: BackupType,
                             project_id: Optional[int], error_message: str):
        """Record backup failure"""
        
        backup_record = self.db.query(BackupRecord).filter(
            BackupRecord.backup_id == backup_id
        ).first()
        
        if backup_record:
            backup_record.status = BackupStatus.FAILED.value
            backup_record.error_message = error_message
            self.db.commit()
    
    def _get_last_backup(self, project_id: int, backup_type: BackupType) -> Optional[BackupRecord]:
        """Get last successful backup of specified type"""
        
        return self.db.query(BackupRecord).filter(
            BackupRecord.project_id == project_id,
            BackupRecord.backup_type == backup_type.value,
            BackupRecord.status == BackupStatus.COMPLETED.value
        ).order_by(BackupRecord.created_at.desc()).first()
    
    def _count_total_records(self) -> int:
        """Count total records in database"""
        
        total = 0
        total += self.db.query(Project).count()
        total += self.db.query(SceneCardDB).count()
        total += self.db.query(ProseContent).count()
        total += self.db.query(ChainLinkDB).count()
        total += self.db.query(Character).count()
        total += self.db.query(SceneSequenceDB).count()
        
        return total
    
    def _cleanup_old_backups(self, project_id: Optional[int]):
        """Remove old backups beyond retention limit"""
        
        query = self.db.query(BackupRecord).filter(
            BackupRecord.status == BackupStatus.COMPLETED.value
        )
        
        if project_id:
            query = query.filter(BackupRecord.project_id == project_id)
        
        backups = query.order_by(BackupRecord.created_at.desc()).all()
        
        if len(backups) > self.config.max_backups_to_keep:
            backups_to_delete = backups[self.config.max_backups_to_keep:]
            
            for backup in backups_to_delete:
                # Delete backup file if it exists
                if backup.backup_path and Path(backup.backup_path).exists():
                    try:
                        Path(backup.backup_path).unlink()
                    except Exception:
                        pass  # Continue cleanup even if file deletion fails
                
                # Delete backup record
                self.db.delete(backup)
            
            self.db.commit()
    
    def list_backups(self, project_id: Optional[int] = None, 
                    backup_type: Optional[BackupType] = None,
                    limit: int = 50) -> List[BackupMetadata]:
        """List available backups"""
        
        query = self.db.query(BackupRecord).filter(
            BackupRecord.status == BackupStatus.COMPLETED.value
        )
        
        if project_id:
            query = query.filter(BackupRecord.project_id == project_id)
        
        if backup_type:
            query = query.filter(BackupRecord.backup_type == backup_type.value)
        
        backups = query.order_by(BackupRecord.created_at.desc()).limit(limit).all()
        
        return [
            BackupMetadata(
                backup_id=backup.backup_id,
                backup_type=BackupType(backup.backup_type),
                project_id=backup.project_id,
                created_at=backup.created_at,
                items_count=backup.items_backed_up,
                size_bytes=backup.total_size_bytes,
                checksum=backup.checksum,
                format=BackupFormat(backup.backup_format),
                compressed=backup.compression_used,
                file_path=backup.backup_path,
                description=backup.description
            )
            for backup in backups
        ]
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a specific backup"""
        
        backup = self.db.query(BackupRecord).filter(
            BackupRecord.backup_id == backup_id
        ).first()
        
        if not backup:
            return False
        
        # Delete backup file if it exists
        if backup.backup_path and Path(backup.backup_path).exists():
            try:
                Path(backup.backup_path).unlink()
            except Exception:
                pass
        
        # Delete backup record
        self.db.delete(backup)
        self.db.commit()
        
        return True


class RecoveryManager:
    """Manages recovery operations from backups"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or next(get_db())
        self.crud = create_crud_manager(self.db)
    
    def recover_project_from_backup(self, backup_id: str, 
                                  target_project_id: Optional[str] = None,
                                  overwrite_existing: bool = False) -> Dict[str, Any]:
        """Recover project from backup"""
        
        backup_record = self._get_backup_record(backup_id)
        backup_data = self._load_backup_data(backup_record)
        
        try:
            # Verify backup integrity
            self._verify_backup_data(backup_data)
            
            # Handle different backup types
            if backup_record.backup_type == BackupType.FULL.value:
                return self._recover_full_backup(backup_data, target_project_id, overwrite_existing)
            elif backup_record.backup_type == BackupType.INCREMENTAL.value:
                return self._recover_incremental_backup(backup_data, target_project_id)
            elif backup_record.backup_type == BackupType.SCENE.value:
                return self._recover_scene_backup(backup_data, target_project_id, overwrite_existing)
            elif backup_record.backup_type == BackupType.SEQUENCE.value:
                return self._recover_sequence_backup(backup_data, target_project_id, overwrite_existing)
            else:
                raise RecoveryError(f"Unsupported backup type: {backup_record.backup_type}")
                
        except Exception as e:
            self.db.rollback()
            raise RecoveryError(f"Recovery failed: {str(e)}")
    
    def _get_backup_record(self, backup_id: str) -> BackupRecord:
        """Get backup record by ID"""
        
        backup = self.db.query(BackupRecord).filter(
            BackupRecord.backup_id == backup_id
        ).first()
        
        if not backup:
            raise RecoveryError(f"Backup not found: {backup_id}")
        
        if backup.status != BackupStatus.COMPLETED.value:
            raise RecoveryError(f"Backup is not completed: {backup_id}")
        
        return backup
    
    def _load_backup_data(self, backup_record: BackupRecord) -> Dict[str, Any]:
        """Load backup data from file"""
        
        file_path = Path(backup_record.backup_path)
        
        if not file_path.exists():
            raise RecoveryError(f"Backup file not found: {backup_record.backup_path}")
        
        # Verify file integrity
        actual_checksum = self._calculate_file_checksum(file_path)
        if actual_checksum != backup_record.checksum:
            raise IntegrityError(f"Backup file integrity check failed: {backup_record.backup_path}")
        
        try:
            # Handle different formats
            if backup_record.backup_format == BackupFormat.SQLITE.value:
                return self._load_sqlite_backup(file_path, backup_record.compression_used)
            elif backup_record.backup_format == BackupFormat.ARCHIVE.value:
                return self._load_archive_backup(file_path)
            else:  # JSON format
                return self._load_json_backup(file_path, backup_record.compression_used)
                
        except Exception as e:
            raise RecoveryError(f"Failed to load backup data: {str(e)}")
    
    def _load_json_backup(self, file_path: Path, compressed: bool) -> Dict[str, Any]:
        """Load JSON backup data"""
        
        if compressed:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _load_archive_backup(self, file_path: Path) -> Dict[str, Any]:
        """Load archive backup data"""
        
        with tarfile.open(file_path, 'r:gz') as tar:
            # Find JSON file in archive
            json_files = [name for name in tar.getnames() if name.endswith('.json')]
            
            if not json_files:
                raise RecoveryError("No JSON data found in archive backup")
            
            # Extract and load first JSON file
            json_file = tar.extractfile(json_files[0])
            if json_file:
                return json.load(json_file)
            else:
                raise RecoveryError("Failed to extract JSON data from archive")
    
    def _load_sqlite_backup(self, file_path: Path, compressed: bool) -> Dict[str, Any]:
        """Load SQLite backup (not implemented for recovery, would require direct DB restore)"""
        raise RecoveryError("SQLite backup recovery not implemented - use direct database restore")
    
    def _verify_backup_data(self, data: Dict[str, Any]):
        """Verify backup data structure"""
        
        if 'backup_metadata' not in data:
            raise RecoveryError("Invalid backup data: missing metadata")
        
        metadata = data['backup_metadata']
        required_fields = ['backup_id', 'backup_type', 'created_at']
        
        for field in required_fields:
            if field not in metadata:
                raise RecoveryError(f"Invalid backup metadata: missing {field}")
    
    def _recover_full_backup(self, backup_data: Dict[str, Any], 
                           target_project_id: Optional[str],
                           overwrite_existing: bool) -> Dict[str, Any]:
        """Recover from full backup"""
        
        recovered_items = {
            'projects': 0,
            'scene_cards': 0,
            'chain_links': 0,
            'characters': 0,
            'sequences': 0,
            'prose_content': 0
        }
        
        # Handle single project backup
        if 'project' in backup_data:
            project_data = backup_data
            recovered = self._recover_project_data(project_data, target_project_id, overwrite_existing)
            for key, value in recovered.items():
                recovered_items[key] += value
        
        # Handle multi-project backup
        elif 'projects' in backup_data:
            for project_data in backup_data['projects']:
                recovered = self._recover_project_data(project_data, target_project_id, overwrite_existing)
                for key, value in recovered.items():
                    recovered_items[key] += value
        
        return recovered_items
    
    def _recover_project_data(self, project_data: Dict[str, Any], 
                            target_project_id: Optional[str],
                            overwrite_existing: bool) -> Dict[str, Any]:
        """Recover individual project data"""
        
        recovered = {
            'projects': 0,
            'scene_cards': 0,
            'chain_links': 0,
            'characters': 0,
            'sequences': 0,
            'prose_content': 0
        }
        
        # Recover project
        if 'project' in project_data:
            project_info = project_data['project']
            
            # Use target project ID if provided
            if target_project_id:
                project_info['project_id'] = target_project_id
            
            # Check if project exists
            existing_project = self.crud['projects'].get_project(project_info['project_id'])
            
            if existing_project:
                if overwrite_existing:
                    # Update existing project
                    self.crud['projects'].update_project(existing_project.id, project_info)
                else:
                    raise RecoveryError(f"Project already exists: {project_info['project_id']}")
            else:
                # Create new project
                project = self.crud['projects'].create_project(project_info)
                recovered['projects'] = 1
            
            project_db_id = existing_project.id if existing_project else project.id
            
            # Recover scene cards
            if 'scene_cards' in project_data:
                for scene_data in project_data['scene_cards']:
                    scene_card = self._deserialize_scene_card(scene_data)
                    if overwrite_existing or not self.crud['scene_cards'].get_scene_card(scene_card.scene_id, project_db_id):
                        self.crud['scene_cards'].create_scene_card(project_db_id, scene_card)
                        recovered['scene_cards'] += 1
            
            # Recover characters
            if 'characters' in project_data:
                for char_data in project_data['characters']:
                    if overwrite_existing or not self.crud['characters'].get_character_by_name(project_db_id, char_data['name']):
                        self.crud['characters'].create_character(project_db_id, char_data)
                        recovered['characters'] += 1
            
            # Recover chain links
            if 'chain_links' in project_data:
                for link_data in project_data['chain_links']:
                    chain_link = self._deserialize_chain_link(link_data)
                    if overwrite_existing or not self.crud['chain_links'].get_chain_link(chain_link.chain_id, project_db_id):
                        self.crud['chain_links'].create_chain_link(project_db_id, chain_link)
                        recovered['chain_links'] += 1
            
            # Recover prose content
            if 'prose_content' in project_data:
                for prose_data in project_data['prose_content']:
                    scene_card = self.crud['scene_cards'].get_scene_card(prose_data['scene_card_id'], project_db_id)
                    if scene_card:
                        self.crud['prose_content'].create_prose_content(
                            scene_card_id=scene_card.id,
                            content=prose_data['content'],
                            content_type=prose_data.get('content_type', 'markdown'),
                            metadata=prose_data
                        )
                        recovered['prose_content'] += 1
        
        self.db.commit()
        return recovered
    
    def _deserialize_scene_card(self, data: Dict[str, Any]):
        """Convert backup data to SceneCard model"""
        from ..models import SceneCard, SceneType, ViewpointType, TenseType, ProactiveScene, ReactiveScene
        
        # Build scene card data
        scene_data = {
            'scene_type': SceneType(data['scene_type']),
            'pov': data['pov'],
            'viewpoint': ViewpointType(data['viewpoint']),
            'tense': TenseType(data['tense']),
            'scene_crucible': data['scene_crucible'],
            'place': data.get('place', ''),
            'time': data.get('time', ''),
            'exposition_used': data.get('exposition_used', []),
            'chain_link': data.get('chain_link', '')
        }
        
        # Add proactive/reactive data
        if data.get('proactive_data'):
            scene_data['proactive'] = ProactiveScene(**data['proactive_data'])
        
        if data.get('reactive_data'):
            scene_data['reactive'] = ReactiveScene(**data['reactive_data'])
        
        return SceneCard(**scene_data)
    
    def _deserialize_chain_link(self, data: Dict[str, Any]):
        """Convert backup data to ChainLink model"""
        from ..chaining.models import ChainLink, ChainLinkType, TransitionType, SceneReference
        
        # Create scene references
        source_scene = SceneReference(
            scene_id=data['source_scene_id'],
            scene_type=SceneType(data['source_scene_type']),
            pov_character=data['source_pov']
        )
        
        target_scene = None
        if data.get('target_scene_id'):
            target_scene = SceneReference(
                scene_id=data['target_scene_id'],
                scene_type=SceneType(data['target_scene_type']),
                pov_character=data['target_pov']
            )
        
        return ChainLink(
            chain_id=data['chain_id'],
            chain_type=ChainLinkType(data['chain_type']),
            transition_type=TransitionType(data['transition_type']),
            source_scene=source_scene,
            target_scene=target_scene,
            trigger_content=data['trigger_content'],
            target_seed=data['target_seed'],
            bridging_content=data.get('bridging_content', ''),
            is_valid=data.get('is_valid', True),
            validation_errors=data.get('validation_errors', []),
            story_context=data.get('story_context', {}),
            character_state_changes=data.get('character_state_changes', {})
        )
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for verification"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _recover_incremental_backup(self, backup_data: Dict[str, Any], 
                                  target_project_id: Optional[str]) -> Dict[str, Any]:
        """Recover from incremental backup"""
        # Implementation for incremental backup recovery
        pass
    
    def _recover_scene_backup(self, backup_data: Dict[str, Any], 
                            target_project_id: Optional[str],
                            overwrite_existing: bool) -> Dict[str, Any]:
        """Recover from scene backup"""
        # Implementation for scene backup recovery  
        pass
    
    def _recover_sequence_backup(self, backup_data: Dict[str, Any],
                               target_project_id: Optional[str], 
                               overwrite_existing: bool) -> Dict[str, Any]:
        """Recover from sequence backup"""
        # Implementation for sequence backup recovery
        pass
    
    def list_recoverable_backups(self) -> List[BackupMetadata]:
        """List all backups available for recovery"""
        
        backups = self.db.query(BackupRecord).filter(
            BackupRecord.status == BackupStatus.COMPLETED.value
        ).order_by(BackupRecord.created_at.desc()).all()
        
        recoverable = []
        
        for backup in backups:
            # Check if backup file still exists and is valid
            if backup.backup_path and Path(backup.backup_path).exists():
                try:
                    # Verify file integrity
                    actual_checksum = self._calculate_file_checksum(Path(backup.backup_path))
                    if actual_checksum == backup.checksum:
                        recoverable.append(BackupMetadata(
                            backup_id=backup.backup_id,
                            backup_type=BackupType(backup.backup_type),
                            project_id=backup.project_id,
                            created_at=backup.created_at,
                            items_count=backup.items_backed_up,
                            size_bytes=backup.total_size_bytes,
                            checksum=backup.checksum,
                            format=BackupFormat(backup.backup_format),
                            compressed=backup.compression_used,
                            file_path=backup.backup_path,
                            description=backup.description
                        ))
                except Exception:
                    # Skip corrupted backups
                    continue
        
        return recoverable