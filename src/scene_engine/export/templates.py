"""
Export Template Management

Minimal implementation to fix import errors.
"""

from typing import Dict, Any
from pydantic import BaseModel


class ExportTemplate(BaseModel):
    """Export template configuration"""
    name: str
    format: str
    settings: Dict[str, Any] = {}


class ExportTemplateManager:
    """Manager for export templates"""
    
    def __init__(self):
        self.templates = {}
    
    def get_template(self, name: str) -> ExportTemplate:
        """Get template by name"""
        return self.templates.get(name, ExportTemplate(name=name, format="text"))
    
    def add_template(self, template: ExportTemplate):
        """Add a template"""
        self.templates[template.name] = template