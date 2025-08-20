"""
Chain Link Import/Export Functionality

This implements subtask 46.5: Implement Chain Link Import/Export Functionality  
Provides serialization, persistence, and interoperability for chain links and sequences.
"""

from typing import List, Dict, Any, Optional, Union, IO
from dataclasses import asdict
from pathlib import Path
import json
import csv
import yaml
from datetime import datetime
import pickle
from abc import ABC, abstractmethod

from .models import (
    ChainLink, ChainSequence, SceneReference, ChainMetadata,
    ChainLinkType, TransitionType, ChainStrength, ChainValidationResult
)
from ..models import SceneType


class SerializationError(Exception):
    """Exception raised during serialization/deserialization operations"""
    pass


class ChainLinkSerializer(ABC):
    """Abstract base for chain link serializers"""
    
    @abstractmethod
    def serialize(self, chain_link: ChainLink) -> str:
        """Serialize a chain link to string format"""
        pass
    
    @abstractmethod
    def deserialize(self, data: str) -> ChainLink:
        """Deserialize a chain link from string format"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this format"""
        pass


class JSONChainLinkSerializer(ChainLinkSerializer):
    """JSON serializer for chain links"""
    
    def serialize(self, chain_link: ChainLink) -> str:
        """Serialize chain link to JSON"""
        try:
            # Convert to dict using Pydantic's dict() method
            chain_dict = chain_link.dict()
            
            # Convert datetime objects to ISO format
            if 'metadata' in chain_dict and chain_dict['metadata']:
                metadata = chain_dict['metadata']
                if 'created_at' in metadata and metadata['created_at']:
                    metadata['created_at'] = metadata['created_at'].isoformat()
            
            return json.dumps(chain_dict, indent=2, ensure_ascii=False)
        except Exception as e:
            raise SerializationError(f"Failed to serialize chain link to JSON: {e}")
    
    def deserialize(self, data: str) -> ChainLink:
        """Deserialize chain link from JSON"""
        try:
            chain_dict = json.loads(data)
            
            # Convert ISO datetime strings back to datetime objects
            if 'metadata' in chain_dict and chain_dict['metadata']:
                metadata = chain_dict['metadata']
                if 'created_at' in metadata and isinstance(metadata['created_at'], str):
                    metadata['created_at'] = datetime.fromisoformat(metadata['created_at'])
            
            return ChainLink(**chain_dict)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize chain link from JSON: {e}")
    
    def get_file_extension(self) -> str:
        return ".json"


class YAMLChainLinkSerializer(ChainLinkSerializer):
    """YAML serializer for chain links"""
    
    def serialize(self, chain_link: ChainLink) -> str:
        """Serialize chain link to YAML"""
        try:
            chain_dict = chain_link.dict()
            
            # Convert datetime objects to ISO format for YAML
            if 'metadata' in chain_dict and chain_dict['metadata']:
                metadata = chain_dict['metadata']
                if 'created_at' in metadata and metadata['created_at']:
                    metadata['created_at'] = metadata['created_at'].isoformat()
            
            return yaml.dump(chain_dict, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise SerializationError(f"Failed to serialize chain link to YAML: {e}")
    
    def deserialize(self, data: str) -> ChainLink:
        """Deserialize chain link from YAML"""
        try:
            chain_dict = yaml.safe_load(data)
            
            # Convert ISO datetime strings back to datetime objects
            if 'metadata' in chain_dict and chain_dict['metadata']:
                metadata = chain_dict['metadata']
                if 'created_at' in metadata and isinstance(metadata['created_at'], str):
                    metadata['created_at'] = datetime.fromisoformat(metadata['created_at'])
            
            return ChainLink(**chain_dict)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize chain link from YAML: {e}")
    
    def get_file_extension(self) -> str:
        return ".yaml"


class CSVChainLinkSerializer(ChainLinkSerializer):
    """CSV serializer for chain links (simplified format)"""
    
    def serialize(self, chain_link: ChainLink) -> str:
        """Serialize chain link to CSV row format"""
        try:
            # Flatten to essential fields for CSV
            row_data = [
                chain_link.chain_id,
                chain_link.chain_type.value,
                chain_link.transition_type.value,
                chain_link.source_scene.scene_id,
                chain_link.source_scene.scene_type.value,
                chain_link.source_scene.pov_character,
                chain_link.target_scene.scene_id if chain_link.target_scene else "",
                chain_link.trigger_content,
                chain_link.target_seed,
                chain_link.metadata.chain_strength.value if chain_link.metadata else "",
                str(chain_link.is_valid),
                chain_link.bridging_content or ""
            ]
            
            # Create CSV writer in memory
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(row_data)
            return output.getvalue().strip()
        except Exception as e:
            raise SerializationError(f"Failed to serialize chain link to CSV: {e}")
    
    def deserialize(self, data: str) -> ChainLink:
        """Deserialize chain link from CSV row format"""
        try:
            reader = csv.reader([data])
            row = next(reader)
            
            if len(row) < 12:
                raise ValueError("Invalid CSV format - insufficient columns")
            
            # Create scene reference
            source_scene = SceneReference(
                scene_id=row[3],
                scene_type=SceneType(row[4]),
                pov_character=row[5]
            )
            
            target_scene = None
            if row[6]:  # Target scene ID exists
                target_scene = SceneReference(
                    scene_id=row[6],
                    scene_type=SceneType.PROACTIVE,  # Default - would need more info in CSV
                    pov_character=row[5]  # Assume same POV - would need more info
                )
            
            # Create metadata
            metadata = ChainMetadata()
            if row[9]:
                metadata.chain_strength = ChainStrength(row[9])
            
            # Create chain link
            return ChainLink(
                chain_id=row[0],
                chain_type=ChainLinkType(row[1]),
                transition_type=TransitionType(row[2]),
                source_scene=source_scene,
                target_scene=target_scene,
                trigger_content=row[7],
                target_seed=row[8],
                metadata=metadata,
                is_valid=row[10].lower() == 'true',
                bridging_content=row[11] if len(row) > 11 and row[11] else None
            )
        except Exception as e:
            raise SerializationError(f"Failed to deserialize chain link from CSV: {e}")
    
    def get_file_extension(self) -> str:
        return ".csv"
    
    @staticmethod
    def get_csv_header() -> List[str]:
        """Get CSV header row"""
        return [
            "chain_id", "chain_type", "transition_type",
            "source_scene_id", "source_scene_type", "source_pov", "target_scene_id",
            "trigger_content", "target_seed", "chain_strength", "is_valid", "bridging_content"
        ]


class ChainSequenceSerializer:
    """Serializer for complete chain sequences"""
    
    def __init__(self, link_serializer: ChainLinkSerializer = None):
        self.link_serializer = link_serializer or JSONChainLinkSerializer()
    
    def serialize_sequence(self, sequence: ChainSequence) -> str:
        """Serialize complete chain sequence"""
        try:
            # Convert sequence to dict
            sequence_dict = {
                "sequence_id": sequence.sequence_id,
                "title": sequence.title,
                "total_word_count": sequence.total_word_count,
                "estimated_reading_time": sequence.estimated_reading_time,
                "dominant_pov": sequence.dominant_pov,
                "sequence_tone": sequence.sequence_tone,
                "narrative_cohesion": sequence.narrative_cohesion,
                "pacing_score": sequence.pacing_score,
                "character_development": sequence.character_development,
                "scenes": [self._scene_ref_to_dict(scene) for scene in sequence.scenes],
                "chain_links": [link.dict() for link in sequence.chain_links],
                "export_timestamp": datetime.now().isoformat(),
                "format_version": "1.0.0"
            }
            
            if isinstance(self.link_serializer, JSONChainLinkSerializer):
                return json.dumps(sequence_dict, indent=2, ensure_ascii=False)
            elif isinstance(self.link_serializer, YAMLChainLinkSerializer):
                return yaml.dump(sequence_dict, default_flow_style=False, allow_unicode=True)
            else:
                raise SerializationError(f"Unsupported serializer for sequence: {type(self.link_serializer)}")
        
        except Exception as e:
            raise SerializationError(f"Failed to serialize chain sequence: {e}")
    
    def deserialize_sequence(self, data: str) -> ChainSequence:
        """Deserialize complete chain sequence"""
        try:
            if isinstance(self.link_serializer, JSONChainLinkSerializer):
                sequence_dict = json.loads(data)
            elif isinstance(self.link_serializer, YAMLChainLinkSerializer):
                sequence_dict = yaml.safe_load(data)
            else:
                raise SerializationError(f"Unsupported serializer for sequence: {type(self.link_serializer)}")
            
            # Reconstruct scene references
            scenes = [self._dict_to_scene_ref(scene_dict) for scene_dict in sequence_dict["scenes"]]
            
            # Reconstruct chain links
            chain_links = [ChainLink(**link_dict) for link_dict in sequence_dict["chain_links"]]
            
            # Create sequence
            sequence = ChainSequence(
                sequence_id=sequence_dict["sequence_id"],
                title=sequence_dict.get("title"),
                scenes=scenes,
                chain_links=chain_links,
                total_word_count=sequence_dict.get("total_word_count", 0),
                estimated_reading_time=sequence_dict.get("estimated_reading_time", 0),
                dominant_pov=sequence_dict.get("dominant_pov"),
                sequence_tone=sequence_dict.get("sequence_tone"),
                narrative_cohesion=sequence_dict.get("narrative_cohesion", 0.5),
                pacing_score=sequence_dict.get("pacing_score", 0.5),
                character_development=sequence_dict.get("character_development", 0.5)
            )
            
            return sequence
        
        except Exception as e:
            raise SerializationError(f"Failed to deserialize chain sequence: {e}")
    
    def _scene_ref_to_dict(self, scene_ref: SceneReference) -> Dict[str, Any]:
        """Convert scene reference to dictionary"""
        return {
            "scene_id": scene_ref.scene_id,
            "scene_type": scene_ref.scene_type.value,
            "pov_character": scene_ref.pov_character,
            "scene_title": scene_ref.scene_title,
            "chapter_number": scene_ref.chapter_number,
            "scene_number": scene_ref.scene_number,
            "word_count": scene_ref.word_count
        }
    
    def _dict_to_scene_ref(self, scene_dict: Dict[str, Any]) -> SceneReference:
        """Convert dictionary to scene reference"""
        return SceneReference(
            scene_id=scene_dict["scene_id"],
            scene_type=SceneType(scene_dict["scene_type"]),
            pov_character=scene_dict["pov_character"],
            scene_title=scene_dict.get("scene_title"),
            chapter_number=scene_dict.get("chapter_number"),
            scene_number=scene_dict.get("scene_number"),
            word_count=scene_dict.get("word_count")
        )


class ChainLinkImportExportManager:
    """
    Manager for chain link import/export operations
    
    Handles file I/O, format detection, batch operations, and persistence.
    """
    
    def __init__(self):
        self.serializers = {
            'json': JSONChainLinkSerializer(),
            'yaml': YAMLChainLinkSerializer(),
            'yml': YAMLChainLinkSerializer(),
            'csv': CSVChainLinkSerializer()
        }
        self.sequence_serializer = ChainSequenceSerializer()
        self.import_stats = {
            "total_imports": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "formats_used": {}
        }
        self.export_stats = {
            "total_exports": 0,
            "successful_exports": 0,
            "failed_exports": 0,
            "formats_used": {}
        }
    
    # Single chain link operations
    
    def export_chain_link(self, chain_link: ChainLink, file_path: Union[str, Path],
                         format_override: Optional[str] = None) -> bool:
        """
        Export a single chain link to file
        
        Args:
            chain_link: Chain link to export
            file_path: Output file path
            format_override: Optional format override (json, yaml, csv)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            format_name = format_override or self._detect_format_from_extension(file_path)
            
            if format_name not in self.serializers:
                raise SerializationError(f"Unsupported format: {format_name}")
            
            serializer = self.serializers[format_name]
            serialized_data = serializer.serialize(chain_link)
            
            # Write to file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(serialized_data)
            
            self._update_export_stats(format_name, True)
            return True
            
        except Exception as e:
            self._update_export_stats(format_override or 'unknown', False)
            raise SerializationError(f"Failed to export chain link: {e}")
    
    def import_chain_link(self, file_path: Union[str, Path],
                         format_override: Optional[str] = None) -> ChainLink:
        """
        Import a single chain link from file
        
        Args:
            file_path: Input file path
            format_override: Optional format override
            
        Returns:
            Imported chain link
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            format_name = format_override or self._detect_format_from_extension(file_path)
            
            if format_name not in self.serializers:
                raise SerializationError(f"Unsupported format: {format_name}")
            
            serializer = self.serializers[format_name]
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            chain_link = serializer.deserialize(data)
            
            self._update_import_stats(format_name, True)
            return chain_link
            
        except Exception as e:
            self._update_import_stats(format_override or 'unknown', False)
            raise SerializationError(f"Failed to import chain link: {e}")
    
    # Chain sequence operations
    
    def export_chain_sequence(self, sequence: ChainSequence, file_path: Union[str, Path],
                            format_override: Optional[str] = None) -> bool:
        """Export a complete chain sequence to file"""
        try:
            file_path = Path(file_path)
            format_name = format_override or self._detect_format_from_extension(file_path)
            
            # Create appropriate sequence serializer
            if format_name in ['json']:
                self.sequence_serializer.link_serializer = JSONChainLinkSerializer()
            elif format_name in ['yaml', 'yml']:
                self.sequence_serializer.link_serializer = YAMLChainLinkSerializer()
            else:
                raise SerializationError(f"Unsupported format for sequences: {format_name}")
            
            serialized_data = self.sequence_serializer.serialize_sequence(sequence)
            
            # Write to file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(serialized_data)
            
            self._update_export_stats(format_name, True)
            return True
            
        except Exception as e:
            self._update_export_stats(format_override or 'unknown', False)
            raise SerializationError(f"Failed to export chain sequence: {e}")
    
    def import_chain_sequence(self, file_path: Union[str, Path],
                            format_override: Optional[str] = None) -> ChainSequence:
        """Import a complete chain sequence from file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            format_name = format_override or self._detect_format_from_extension(file_path)
            
            # Create appropriate sequence serializer
            if format_name in ['json']:
                self.sequence_serializer.link_serializer = JSONChainLinkSerializer()
            elif format_name in ['yaml', 'yml']:
                self.sequence_serializer.link_serializer = YAMLChainLinkSerializer()
            else:
                raise SerializationError(f"Unsupported format for sequences: {format_name}")
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            sequence = self.sequence_serializer.deserialize_sequence(data)
            
            self._update_import_stats(format_name, True)
            return sequence
            
        except Exception as e:
            self._update_import_stats(format_override or 'unknown', False)
            raise SerializationError(f"Failed to import chain sequence: {e}")
    
    # Batch operations
    
    def export_chain_links_batch(self, chain_links: List[ChainLink], 
                                directory: Union[str, Path],
                                format_name: str = 'json',
                                filename_template: str = "chain_link_{index}") -> List[Path]:
        """Export multiple chain links to files"""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        for i, chain_link in enumerate(chain_links):
            filename = f"{filename_template.format(index=i, id=chain_link.chain_id)}{self.serializers[format_name].get_file_extension()}"
            file_path = directory / filename
            
            try:
                self.export_chain_link(chain_link, file_path, format_name)
                exported_files.append(file_path)
            except SerializationError:
                # Continue with other files
                pass
        
        return exported_files
    
    def import_chain_links_batch(self, directory: Union[str, Path],
                               format_name: Optional[str] = None) -> List[ChainLink]:
        """Import multiple chain links from directory"""
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        chain_links = []
        
        # Find all relevant files
        if format_name:
            pattern = f"*{self.serializers[format_name].get_file_extension()}"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                try:
                    chain_link = self.import_chain_link(file_path, format_name)
                    chain_links.append(chain_link)
                except SerializationError:
                    # Continue with other files
                    pass
        
        return chain_links
    
    def export_to_csv_table(self, chain_links: List[ChainLink], 
                          file_path: Union[str, Path]) -> bool:
        """Export chain links to CSV table format"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            csv_serializer = CSVChainLinkSerializer()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(CSVChainLinkSerializer.get_csv_header())
                
                # Write data rows
                for chain_link in chain_links:
                    csv_row = csv_serializer.serialize(chain_link)
                    # Parse the CSV row back to list for writing
                    reader = csv.reader([csv_row])
                    row_data = next(reader)
                    writer.writerow(row_data)
            
            self._update_export_stats('csv', True)
            return True
            
        except Exception as e:
            self._update_export_stats('csv', False)
            raise SerializationError(f"Failed to export to CSV table: {e}")
    
    def import_from_csv_table(self, file_path: Union[str, Path]) -> List[ChainLink]:
        """Import chain links from CSV table format"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            chain_links = []
            csv_serializer = CSVChainLinkSerializer()
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if row:  # Skip empty rows
                        csv_row = ','.join(f'"{cell}"' for cell in row)
                        chain_link = csv_serializer.deserialize(csv_row)
                        chain_links.append(chain_link)
            
            self._update_import_stats('csv', True)
            return chain_links
            
        except Exception as e:
            self._update_import_stats('csv', False)
            raise SerializationError(f"Failed to import from CSV table: {e}")
    
    # Utility methods
    
    def _detect_format_from_extension(self, file_path: Path) -> str:
        """Detect format from file extension"""
        extension = file_path.suffix.lower().lstrip('.')
        
        if extension in self.serializers:
            return extension
        else:
            raise SerializationError(f"Cannot detect format from extension: {extension}")
    
    def _update_import_stats(self, format_name: str, success: bool):
        """Update import statistics"""
        self.import_stats["total_imports"] += 1
        
        if success:
            self.import_stats["successful_imports"] += 1
        else:
            self.import_stats["failed_imports"] += 1
        
        self.import_stats["formats_used"][format_name] = self.import_stats["formats_used"].get(format_name, 0) + 1
    
    def _update_export_stats(self, format_name: str, success: bool):
        """Update export statistics"""
        self.export_stats["total_exports"] += 1
        
        if success:
            self.export_stats["successful_exports"] += 1
        else:
            self.export_stats["failed_exports"] += 1
        
        self.export_stats["formats_used"][format_name] = self.export_stats["formats_used"].get(format_name, 0) + 1
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """Get import statistics"""
        stats = self.import_stats.copy()
        if stats["total_imports"] > 0:
            stats["success_rate"] = (stats["successful_imports"] / stats["total_imports"]) * 100
        else:
            stats["success_rate"] = 0.0
        return stats
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export statistics"""
        stats = self.export_stats.copy()
        if stats["total_exports"] > 0:
            stats["success_rate"] = (stats["successful_exports"] / stats["total_exports"]) * 100
        else:
            stats["success_rate"] = 0.0
        return stats
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats"""
        return list(self.serializers.keys())
    
    def validate_import_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate an import file without fully importing"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"valid": False, "error": "File not found"}
            
            format_name = self._detect_format_from_extension(file_path)
            
            # Try to parse without creating objects
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            if format_name == 'json':
                json.loads(data)  # Just validate JSON parsing
            elif format_name in ['yaml', 'yml']:
                yaml.safe_load(data)  # Just validate YAML parsing
            elif format_name == 'csv':
                reader = csv.reader(data.splitlines())
                list(reader)  # Just validate CSV parsing
            
            return {
                "valid": True,
                "format": format_name,
                "file_size": file_path.stat().st_size,
                "line_count": len(data.splitlines())
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}


# Convenience functions
def export_chain_link_to_json(chain_link: ChainLink, file_path: Union[str, Path]) -> bool:
    """Export chain link to JSON file"""
    manager = ChainLinkImportExportManager()
    return manager.export_chain_link(chain_link, file_path, 'json')


def import_chain_link_from_json(file_path: Union[str, Path]) -> ChainLink:
    """Import chain link from JSON file"""
    manager = ChainLinkImportExportManager()
    return manager.import_chain_link(file_path, 'json')


def export_chain_sequence_to_json(sequence: ChainSequence, file_path: Union[str, Path]) -> bool:
    """Export chain sequence to JSON file"""
    manager = ChainLinkImportExportManager()
    return manager.export_chain_sequence(sequence, file_path, 'json')


def import_chain_sequence_from_json(file_path: Union[str, Path]) -> ChainSequence:
    """Import chain sequence from JSON file"""
    manager = ChainLinkImportExportManager()
    return manager.import_chain_sequence(file_path, 'json')


def export_chain_links_to_csv(chain_links: List[ChainLink], file_path: Union[str, Path]) -> bool:
    """Export chain links to CSV table"""
    manager = ChainLinkImportExportManager()
    return manager.export_to_csv_table(chain_links, file_path)