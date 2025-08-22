"""
Step 12 Implementation: Comic Script Professional Formatter
Formats Step 11 comic scripts into professional industry-standard outputs
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from src.pipeline.validators.step_12_validator import Step12Validator

class Step12ComicFormatter:
    """
    Step 12: Formats comic scripts into professional industry-standard outputs
    
    Based on PRD research for:
    - Full Script (DC Style) format
    - Character design sheets with turnarounds
    - Professional script templates
    - Export to multiple formats (PDF, DOCX, TXT)
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step12Validator()
        
        # Professional format templates from PRD
        self.script_templates = {
            "dc_style": "full_script_dc",
            "marvel_method": "marvel_plot_first", 
            "indie": "flexible_format"
        }
        
        # Export formats supported
        self.export_formats = ["txt", "docx", "pdf", "fountain"]
    
    def execute(self, 
                step11_artifact: Dict[str, Any], 
                project_id: str,
                model_config: Optional[Dict[str, Any]] = None,
                format_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 12: Format comic script professionally
        
        Args:
            step11_artifact: Step 11 comic script data
            project_id: Project identifier
            model_config: Model configuration (not used in this step)
            format_options: Optional formatting preferences
            
        Returns:
            Tuple of (success, formatted_artifacts, message)
        """
        if not model_config:
            model_config = {}
            
        if not format_options:
            format_options = {
                "script_format": "dc_style",
                "include_character_sheets": True,
                "include_panel_layouts": True,
                "export_formats": ["txt"],
                "template_style": "professional"
            }
        
        try:
            # Calculate upstream hash for traceability
            upstream_hash = hashlib.sha256(
                json.dumps(step11_artifact, sort_keys=True).encode()
            ).hexdigest()
            
            # Progress tracking
            try:
                from src.ui.progress_tracker import get_global_tracker
                tracker = get_global_tracker()
            except ImportError:
                tracker = None
            
            # Generate formatted outputs with progress tracking
            formatted_outputs = self._generate_formatted_outputs(
                step11_artifact, format_options, tracker
            )
            
            # Create formatted artifact
            formatted_artifact = self._create_formatted_artifact(
                formatted_outputs, step11_artifact, project_id, 
                format_options, upstream_hash
            )
            
            # Validate formatted artifact
            is_valid, validation_message = self.validator.validate(formatted_artifact)
            if not is_valid:
                return False, {}, f"Formatted script validation failed: {validation_message}"
            
            # Export to requested formats
            export_paths = self._export_to_formats(
                formatted_artifact, project_id, 
                format_options.get('export_formats', ['txt'])
            )
            formatted_artifact['export_paths'] = export_paths
            
            # Save main artifact
            artifact_path = self._save_artifact(formatted_artifact, project_id)
            
            return True, formatted_artifact, f"Step 12 artifact saved to {artifact_path}"
            
        except Exception as e:
            return False, {}, f"Error in Step 12 execution: {str(e)}"
    
    def _generate_formatted_outputs(self, step11_artifact: Dict[str, Any], 
                                   format_options: Dict[str, Any], 
                                   tracker=None) -> Dict[str, Any]:
        """Generate all formatted outputs with progress tracking"""
        formatted_outputs = {}
        total_tasks = 4  # script, character_sheets, layouts, production_notes
        current_task = 0
        
        print("Generating formatted outputs...")
        
        # 1. Professional script format
        if tracker:
            tracker.update_step_progress(current_task, total_tasks, "Formatting professional script...")
        else:
            print("  Formatting professional script...")
        
        script_output = self._format_professional_script(
            step11_artifact, 
            format_options.get('script_format', 'dc_style')
        )
        formatted_outputs['professional_script'] = script_output
        current_task += 1
        
        # 2. Character design sheets
        if format_options.get('include_character_sheets', True):
            if tracker:
                tracker.update_step_progress(current_task, total_tasks, "Creating character design sheets...")
            else:
                print("  Creating character design sheets...")
            
            character_sheets = self._create_character_sheets(
                step11_artifact.get('character_designs', {}),
                step11_artifact.get('pages', [])
            )
            formatted_outputs['character_sheets'] = character_sheets
        current_task += 1
        
        # 3. Panel layout guides  
        if format_options.get('include_panel_layouts', True):
            if tracker:
                tracker.update_step_progress(current_task, total_tasks, "Creating panel layout guides...")
            else:
                print("  Creating panel layout guides...")
            
            layout_guides = self._create_panel_layout_guides(
                step11_artifact.get('pages', [])
            )
            formatted_outputs['panel_layouts'] = layout_guides
        current_task += 1
        
        # 4. Production notes
        if tracker:
            tracker.update_step_progress(current_task, total_tasks, "Generating production notes...")
        else:
            print("  Generating production notes...")
        
        production_notes = self._create_production_notes(
            step11_artifact,
            format_options
        )
        formatted_outputs['production_notes'] = production_notes
        current_task += 1
        
        # Final progress update
        if tracker:
            tracker.update_step_progress(total_tasks, total_tasks, "All formatted outputs generated")
        
        return formatted_outputs
    
    def _create_formatted_artifact(self, formatted_outputs: Dict[str, Any], 
                                  step11_artifact: Dict[str, Any],
                                  project_id: str, format_options: Dict[str, Any],
                                  upstream_hash: str) -> Dict[str, Any]:
        """Create the Step 12 formatted artifact"""
        return {
            "metadata": {
                "step": 12,
                "step_name": "comic_formatter",
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "source_step": 11,
                "format_type": format_options.get('script_format', 'dc_style'),
                "upstream_hash": upstream_hash
            },
            "format_options": format_options,
            "formatted_outputs": formatted_outputs,
            "export_info": {
                "formats_generated": format_options.get('export_formats', ['txt']),
                "template_style": format_options.get('template_style', 'professional'),
                "total_pages": step11_artifact.get('total_pages', 0),
                "total_panels": step11_artifact.get('total_panels', 0)
            }
        }
    
    def _format_professional_script(self, comic_script: Dict[str, Any], 
                                  format_type: str) -> Dict[str, Any]:
        """
        Format script according to professional industry standards
        Based on PRD research for Full Script (DC Style)
        """
        pages = comic_script.get('pages', [])
        character_designs = comic_script.get('character_designs', {})
        
        if format_type == "dc_style":
            return self._format_dc_full_script(pages, character_designs)
        elif format_type == "marvel_method":
            return self._format_marvel_method(pages, character_designs)
        else:
            # Default to DC style
            return self._format_dc_full_script(pages, character_designs)
    
    def _format_dc_full_script(self, pages: List[Dict], characters: Dict) -> Dict[str, Any]:
        """
        Format in Full Script (DC Style) per PRD research
        
        Format example from PRD:
        PAGE 1 (5 panels)
        PANEL 1: Description...
          CHARACTER (BALLOON): "Dialogue here."
          CHARACTER (CAPTION): "Caption here."
        """
        formatted_script = {
            "format_name": "Full Script (DC Style)",
            "description": "Panel-by-panel breakdown with complete dialogue and art direction",
            "script_content": []
        }
        
        # Header information
        script_lines = [
            "COMIC BOOK SCRIPT",
            "Format: Full Script (DC Style)",
            "Panel-by-panel breakdown with complete art direction",
            "",
            "CHARACTER REFERENCE:",
        ]
        
        # Character reference section
        for char_name, design in characters.items():
            script_lines.extend([
                f"{char_name.upper()}:",
                f"  Description: {design.get('description', 'N/A')}",
                f"  Build: {design.get('height', 'N/A')} / {design.get('build', 'N/A')}",
                f"  Hair/Eyes: {design.get('hair', 'N/A')} / {design.get('eyes', 'N/A')}",
                ""
            ])
        
        script_lines.extend(["", "SCRIPT:", "=" * 50, ""])
        
        # Format each page
        for page in pages:
            page_number = page.get('page_number', 1)
            panel_count = page.get('panel_count', 0)
            
            script_lines.append(f"PAGE {page_number} ({panel_count} panels)")
            script_lines.append("-" * 40)
            
            # Format each panel
            for panel in page.get('panels', []):
                panel_num = panel.get('panel_number', 1)
                description = panel.get('description', '')
                
                # Panel header with shot type if available
                shot_type = panel.get('shot_type', '').upper()
                if shot_type:
                    script_lines.append(f"PANEL {panel_num} ({shot_type}): {description}")
                else:
                    script_lines.append(f"PANEL {panel_num}: {description}")
                
                # Dialogue formatting
                for dialogue in panel.get('dialogue', []):
                    char_name = dialogue.get('character', '').upper()
                    dialogue_type = dialogue.get('type', 'balloon').upper()
                    text = dialogue.get('text', '')
                    
                    script_lines.append(f"  {char_name} ({dialogue_type}): \"{text}\"")
                
                # Add transition note if specified
                transition = panel.get('transition_type', '')
                if transition and transition != 'action_to_action':  # Don't note default
                    script_lines.append(f"  [TRANSITION: {transition.replace('_', '-').title()}]")
                
                script_lines.append("")  # Blank line after panel
            
            script_lines.append("")  # Blank line after page
        
        formatted_script['script_content'] = script_lines
        return formatted_script
    
    def _format_marvel_method(self, pages: List[Dict], characters: Dict) -> Dict[str, Any]:
        """
        Format in Marvel Method style (plot first, dialogue after art)
        """
        formatted_script = {
            "format_name": "Marvel Method (Plot First)",
            "description": "Plot outline for artist, dialogue added after pencils",
            "script_content": []
        }
        
        script_lines = [
            "COMIC BOOK PLOT OUTLINE",
            "Format: Marvel Method (Plot First)", 
            "Artist interprets visually, writer adds dialogue after pencils",
            "",
            "CHARACTERS:",
        ]
        
        # Character descriptions
        for char_name, design in characters.items():
            script_lines.extend([
                f"{char_name}: {design.get('description', 'N/A')}",
            ])
        
        script_lines.extend(["", "PLOT BREAKDOWN:", "=" * 40, ""])
        
        # Simplified plot format
        for page in pages:
            page_num = page.get('page_number', 1)
            script_lines.append(f"PAGE {page_num}:")
            
            # Combine panel actions into page description
            page_actions = []
            for panel in page.get('panels', []):
                description = panel.get('description', '')
                page_actions.append(description)
            
            script_lines.append(" ".join(page_actions))
            script_lines.append("")
        
        formatted_script['script_content'] = script_lines
        return formatted_script
    
    def _create_character_sheets(self, character_designs: Dict, pages: List[Dict]) -> Dict[str, Any]:
        """
        Create character design sheets with turnarounds and expressions
        Following PRD requirements for visual consistency
        """
        character_sheets = {
            "format_name": "Character Design Sheets",
            "description": "Visual reference for artists and colorists",
            "characters": {}
        }
        
        for char_name, design in character_designs.items():
            # Count character appearances
            appearances = 0
            for page in pages:
                for panel in page.get('panels', []):
                    if char_name.lower() in [c.lower() for c in panel.get('characters', [])]:
                        appearances += 1
            
            character_sheet = {
                "character_name": char_name,
                "appearances": appearances,
                "design_notes": {
                    "physical_description": design.get('description', 'N/A'),
                    "height_build": f"{design.get('height', 'N/A')} / {design.get('build', 'N/A')}",
                    "hair_eyes": f"{design.get('hair', 'N/A')} / {design.get('eyes', 'N/A')}",
                    "distinguishing_features": design.get('distinguishing_features', 'N/A'),
                    "typical_clothing": design.get('typical_clothing', 'N/A'),
                    "color_palette": design.get('color_palette', 'N/A')
                },
                "art_requirements": [
                    "Full-body front view",
                    "Full-body back view", 
                    "Profile (side view)",
                    "4-6 facial expressions (happy, sad, angry, surprised, neutral, determined)",
                    "Scale comparison with other characters",
                    "Signature items/props",
                    "Color reference"
                ],
                "consistency_notes": [
                    f"Character appears in {appearances} panels",
                    "Maintain proportions across all panels",
                    "Keep clothing/hair consistent unless story requires change",
                    "Reference this sheet for all appearances"
                ]
            }
            
            character_sheets['characters'][char_name] = character_sheet
        
        return character_sheets
    
    def _create_panel_layout_guides(self, pages: List[Dict]) -> Dict[str, Any]:
        """
        Create panel layout guides for artists
        Based on PRD panel composition best practices
        """
        layout_guides = {
            "format_name": "Panel Layout Guides",
            "description": "Page composition and flow guidance for artists",
            "pages": []
        }
        
        for page in pages:
            page_number = page.get('page_number', 1)
            panel_count = page.get('panel_count', 0)
            
            # Determine recommended layout based on panel count
            if panel_count <= 4:
                layout_style = "Large panels for impact"
            elif panel_count <= 6:
                layout_style = "Standard grid layout"
            elif panel_count <= 9:
                layout_style = "Dense layout - use carefully"
            else:
                layout_style = "OVERCROWDED - reduce panels"
            
            # Analyze dramatic moments for panel sizing
            dramatic_panels = []
            for panel in page.get('panels', []):
                description = panel.get('description', '').lower()
                if any(word in description for word in ['wide shot', 'establishing', 'reveals', 'dramatic']):
                    dramatic_panels.append(panel.get('panel_number'))
            
            page_guide = {
                "page_number": page_number,
                "panel_count": panel_count,
                "layout_recommendation": layout_style,
                "dramatic_panels": dramatic_panels,
                "flow_notes": [
                    "Follow standard left-to-right, top-to-bottom reading flow",
                    "Use panel size to control pacing",
                    "Large panels for important moments",
                    "Small panels for quick actions"
                ],
                "composition_notes": self._analyze_page_composition(page)
            }
            
            layout_guides['pages'].append(page_guide)
        
        return layout_guides
    
    def _analyze_page_composition(self, page: Dict) -> List[str]:
        """Analyze page composition and provide artist notes"""
        notes = []
        panels = page.get('panels', [])
        
        # Check for page turn moments (last panel on even pages)
        page_number = page.get('page_number', 1)
        if page_number % 2 == 0:  # Even page (right-hand page)
            last_panel = panels[-1] if panels else None
            if last_panel:
                description = last_panel.get('description', '').lower()
                if any(word in description for word in ['reveal', 'surprise', 'dramatic', 'cliffhanger']):
                    notes.append("CONSIDER: This page ends with dramatic moment - good for page turn reveal")
        
        # Check panel transition flow
        transitions = [panel.get('transition_type', '') for panel in panels]
        if 'scene_to_scene' in transitions:
            notes.append("Scene changes present - use clear visual breaks")
        
        if len(transitions) > 7:
            notes.append("WARNING: High panel density may impact readability")
        
        return notes
    
    def _create_production_notes(self, comic_script: Dict, format_options: Dict) -> Dict[str, Any]:
        """
        Create production notes for the creative team
        """
        stats = comic_script.get('panel_statistics', {})
        
        production_notes = {
            "format_name": "Production Notes",
            "description": "Technical specifications and guidelines for production team",
            "script_statistics": {
                "total_pages": comic_script.get('total_pages', 0),
                "total_panels": comic_script.get('total_panels', 0),
                "average_panels_per_page": stats.get('avg_panels_per_page', 0),
                "maximum_panels_per_page": stats.get('max_panels_per_page', 0),
                "average_words_per_panel": stats.get('avg_words_per_panel', 0),
                "maximum_words_per_panel": stats.get('max_words_per_panel', 0)
            },
            "industry_compliance": {
                "panel_density": "PASS" if stats.get('max_panels_per_page', 0) <= 9 else "REVIEW NEEDED",
                "word_density": "PASS" if stats.get('max_words_per_panel', 0) <= 50 else "REVIEW NEEDED",
                "format_standard": format_options.get('script_format', 'dc_style').upper()
            },
            "team_guidelines": {
                "letterer_notes": [
                    f"Maximum {stats.get('max_words_per_panel', 0)} words per panel",
                    "Follow standard balloon placement guidelines",
                    "Avoid covering character faces with balloons"
                ],
                "artist_notes": [
                    f"Average {stats.get('avg_panels_per_page', 0):.1f} panels per page", 
                    "Reference character design sheets for consistency",
                    "Panel size should reflect story pacing"
                ],
                "colorist_notes": [
                    "Character color palettes in design sheets",
                    "Mood notes provided per panel",
                    "Maintain lighting consistency within scenes"
                ]
            }
        }
        
        return production_notes
    
    def _export_to_formats(self, formatted_artifact: Dict, project_id: str, 
                          export_formats: List[str]) -> Dict[str, str]:
        """Export formatted script to requested file formats"""
        export_paths = {}
        
        project_path = self.project_dir / project_id
        
        for format_type in export_formats:
            if format_type == "txt":
                export_paths['txt'] = self._export_txt(formatted_artifact, project_path)
            elif format_type == "pdf":
                export_paths['pdf'] = self._export_pdf_placeholder(formatted_artifact, project_path)
            elif format_type == "docx":
                export_paths['docx'] = self._export_docx_placeholder(formatted_artifact, project_path)
            elif format_type == "fountain":
                export_paths['fountain'] = self._export_fountain_placeholder(formatted_artifact, project_path)
        
        return export_paths
    
    def _export_txt(self, formatted_artifact: Dict, project_path: Path) -> str:
        """Export as professional text file"""
        txt_path = project_path / "step_12_comic_script_formatted.txt"
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            # Write professional script
            script = formatted_artifact['formatted_outputs']['professional_script']
            f.write("\n".join(script['script_content']))
            
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("CHARACTER DESIGN SHEETS\n")
            f.write("=" * 60 + "\n\n")
            
            # Write character sheets
            if 'character_sheets' in formatted_artifact['formatted_outputs']:
                char_sheets = formatted_artifact['formatted_outputs']['character_sheets']
                for char_name, sheet in char_sheets.get('characters', {}).items():
                    f.write(f"{char_name.upper()} DESIGN SHEET\n")
                    f.write("-" * 30 + "\n")
                    
                    design_notes = sheet.get('design_notes', {})
                    for key, value in design_notes.items():
                        f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                    
                    f.write("\nArt Requirements:\n")
                    for req in sheet.get('art_requirements', []):
                        f.write(f"• {req}\n")
                    
                    f.write("\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("PRODUCTION NOTES\n")
            f.write("=" * 60 + "\n\n")
            
            # Write production notes
            if 'production_notes' in formatted_artifact['formatted_outputs']:
                prod_notes = formatted_artifact['formatted_outputs']['production_notes']
                
                stats = prod_notes.get('script_statistics', {})
                f.write("SCRIPT STATISTICS:\n")
                for key, value in stats.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                
                f.write("\nINDUSTRY COMPLIANCE:\n")
                compliance = prod_notes.get('industry_compliance', {})
                for key, value in compliance.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        
        return str(txt_path)
    
    def _export_pdf_placeholder(self, formatted_artifact: Dict, project_path: Path) -> str:
        """Placeholder for PDF export (would require PDF generation library)"""
        # TODO: Implement PDF export using reportlab or similar
        placeholder_path = project_path / "step_12_comic_script_formatted.pdf.placeholder"
        with open(placeholder_path, 'w') as f:
            f.write("PDF export would be generated here using reportlab library\n")
            f.write(f"Source: {formatted_artifact['metadata']['project_id']}\n")
        return str(placeholder_path)
    
    def _export_docx_placeholder(self, formatted_artifact: Dict, project_path: Path) -> str:
        """Placeholder for DOCX export (would require python-docx library)"""
        # TODO: Implement DOCX export using python-docx
        placeholder_path = project_path / "step_12_comic_script_formatted.docx.placeholder" 
        with open(placeholder_path, 'w') as f:
            f.write("DOCX export would be generated here using python-docx library\n")
            f.write(f"Source: {formatted_artifact['metadata']['project_id']}\n")
        return str(placeholder_path)
    
    def _export_fountain_placeholder(self, formatted_artifact: Dict, project_path: Path) -> str:
        """Placeholder for Fountain format export (screenplay format adapted for comics)"""
        # TODO: Implement Fountain format export
        placeholder_path = project_path / "step_12_comic_script_formatted.fountain.placeholder"
        with open(placeholder_path, 'w') as f:
            f.write("Fountain format export would be generated here\n")
            f.write(f"Source: {formatted_artifact['metadata']['project_id']}\n")
        return str(placeholder_path)
    
    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> str:
        """Save the formatted comic script artifact following Snowflake patterns"""
        # Ensure project directory exists
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON artifact
        artifact_path = project_path / "step_12_formatted_comic.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        return str(artifact_path)

if __name__ == "__main__":
    # Test execution
    step12 = Step12ComicFormatter("test_artifacts")
    print("Step 12: Comic Script Formatter initialized")