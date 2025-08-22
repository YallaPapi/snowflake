"""
Step 14 Implementation: Panel Composition and Lettering
Composites panel images into comic pages with speech bubbles and text
"""

import json
import hashlib
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import math

from src.pipeline.validators.step_14_validator import Step14Validator

class TextRenderingConfig:
    """Configuration for professional comic book text rendering"""
    
    # Font size range for comic book lettering (configurable)
    MIN_FONT_SIZE = 32
    MAX_FONT_SIZE = 40
    DEFAULT_FONT_SIZE = 36
    
    # Text colors - high contrast for readability
    TEXT_COLOR = 'black'  # Always black text on white background
    BUBBLE_FILL_COLOR = 'white'
    BUBBLE_OUTLINE_COLOR = 'black'
    BUBBLE_OUTLINE_WIDTH = 3
    
    # Spacing and padding constants
    LINE_HEIGHT_MULTIPLIER = 1.4  # Professional line spacing
    BUBBLE_PADDING_MIN = 20  # Minimum padding inside bubbles
    BUBBLE_PADDING_MAX = 30  # Maximum padding for larger bubbles
    BUBBLE_PADDING_DEFAULT = 25  # Default padding
    
    # Text wrapping configuration
    MAX_WIDTH_PERCENTAGE = 0.8  # Use up to 80% of available width
    MAX_CHARS_PER_LINE = 30  # Maximum characters per line
    MIN_CHARS_PER_LINE = 15  # Minimum for readability
    
    # Font fallback chain
    FONT_PREFERENCES = [
        "ComicSansMS",  # Primary comic font
        "Comic Sans MS",  # Alternative name
        "arial",  # Fallback to Arial
        "Arial",  # Alternative case
        "helvetica",  # Secondary fallback
        "Helvetica"  # Alternative case
    ]
    
    # Bubble styling
    CORNER_RADIUS_RATIO = 6  # Corner radius as fraction of min dimension
    TAIL_WIDTH = 35  # Width of speech bubble tail
    TAIL_HEIGHT = 25  # Height of speech bubble tail
    THOUGHT_BUBBLE_SIZE = 10  # Size of small thought bubbles
    
    @classmethod
    def get_font_size(cls, priority: str = 'default') -> int:
        """Get appropriate font size based on priority"""
        if priority == 'large':
            return cls.MAX_FONT_SIZE
        elif priority == 'small':
            return cls.MIN_FONT_SIZE
        return cls.DEFAULT_FONT_SIZE
    
    @classmethod
    def get_bubble_padding(cls, text_length: int) -> int:
        """Calculate padding based on text length"""
        if text_length < 20:
            return cls.BUBBLE_PADDING_MIN
        elif text_length > 100:
            return cls.BUBBLE_PADDING_MAX
        return cls.BUBBLE_PADDING_DEFAULT


class Step14PanelComposition:
    """
    Composites panel images into complete comic pages with lettering
    
    Features:
    - Panel layout and composition
    - Speech bubble generation with professional styling
    - Text placement with configurable sizing (32-40pt)
    - Sound effects and captions
    - Page assembly with proper error handling
    """
    
    def __init__(self, project_dir: str = "artifacts", text_config: Optional[TextRenderingConfig] = None):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step14Validator()
        
        # Use provided config or default
        self.text_config = text_config or TextRenderingConfig()
        
        # Page layout configurations
        self.page_layouts = {
            "standard": {"width": 1650, "height": 2550, "dpi": 300, "margin": 50},
            "manga": {"width": 1480, "height": 2100, "dpi": 300, "margin": 40},
            "webcomic": {"width": 800, "height": 1200, "dpi": 150, "margin": 20},
            "square": {"width": 2048, "height": 2048, "dpi": 300, "margin": 40}
        }
        
        # Panel gutter (space between panels)
        self.gutter_width = 10
        
        # Font cache for performance
        self.fonts = {}
        self.font_load_errors = []  # Track font loading issues
    
    def execute(self,
                step13_artifact: Dict[str, Any],
                step11_artifact: Dict[str, Any],
                project_id: str,
                composition_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 14: Composite panels into comic pages
        
        Args:
            step13_artifact: Generated panel images
            step11_artifact: Comic script with dialogue
            project_id: Project identifier
            composition_config: Layout configuration
            
        Returns:
            Tuple of (success, composed_pages_artifact, message)
        """
        if not composition_config:
            composition_config = {
                "layout": "standard",
                "style": "western",
                "add_page_numbers": True,
                "add_borders": True
            }
        
        try:
            # Calculate upstream hash
            upstream_hash = hashlib.sha256(
                json.dumps({"step13": step13_artifact, "step11": step11_artifact}, sort_keys=True).encode()
            ).hexdigest()
            
            # Get panel images and script data
            panel_images = step13_artifact.get('panels', [])
            comic_pages = step11_artifact.get('pages', [])
            
            # Load fonts
            self._load_fonts()
            
            # Composite pages
            print(f"Compositing {len(comic_pages)} pages...")
            composed_pages = []
            
            for page_idx, page_data in enumerate(comic_pages):
                print(f"  Compositing page {page_idx + 1}...")
                
                # Get panels for this page
                page_panels = self._get_panels_for_page(
                    page_idx, page_data, panel_images
                )
                
                # Create composed page
                composed_page = self._composite_page(
                    page_idx, page_data, page_panels, composition_config
                )
                
                composed_pages.append(composed_page)
            
            # Create artifact
            artifact = self._create_artifact(
                composed_pages, comic_pages, project_id, 
                upstream_hash, composition_config
            )
            
            # Validate
            is_valid, errors = self.validator.validate(artifact)
            if not is_valid:
                return False, {}, f"Validation failed: {errors}"
            
            # Save artifact and pages
            artifact_path = self._save_artifact(artifact, project_id)
            
            return True, artifact, f"Step 14 completed. Composited {len(composed_pages)} pages."
            
        except Exception as e:
            return False, {}, f"Error in Step 14: {str(e)}"
    
    def _load_fonts(self):
        """Load fonts for text rendering with comprehensive error handling"""
        self.fonts = {}
        self.font_load_errors = []
        
        # Define font size range for comic book lettering
        font_sizes = range(
            TextRenderingConfig.MIN_FONT_SIZE,
            TextRenderingConfig.MAX_FONT_SIZE + 1,
            2  # Step by 2 for efficiency
        )
        
        # Also include some smaller sizes for page numbers, etc.
        additional_sizes = [12, 16, 20, 24, 28]
        all_sizes = list(set(list(font_sizes) + additional_sizes))
        
        for size in sorted(all_sizes):
            font_loaded = False
            
            # Try each font in the preference chain
            for font_name in TextRenderingConfig.FONT_PREFERENCES:
                try:
                    # Try with .ttf extension
                    self.fonts[f"comic_{size}"] = ImageFont.truetype(f"{font_name}.ttf", size)
                    font_loaded = True
                    break
                except (IOError, OSError):
                    # Try without extension (system font)
                    try:
                        self.fonts[f"comic_{size}"] = ImageFont.truetype(font_name, size)
                        font_loaded = True
                        break
                    except (IOError, OSError):
                        continue
            
            # Fallback to default if no font could be loaded
            if not font_loaded:
                try:
                    # Try to create a larger default font
                    default_font = ImageFont.load_default()
                    # Scale up the default font if possible
                    if hasattr(default_font, 'font'):
                        scaled_font = default_font.font.variant(size=size)
                        self.fonts[f"comic_{size}"] = scaled_font
                    else:
                        self.fonts[f"comic_{size}"] = default_font
                except Exception as e:
                    # Ultimate fallback
                    self.fonts[f"comic_{size}"] = ImageFont.load_default()
                    self.font_load_errors.append(
                        f"Could not load font size {size}: {str(e)}. Using default."
                    )
        
        # Load special style fonts
        self._load_style_fonts()
        
        # Log any font loading issues for debugging
        if self.font_load_errors:
            print(f"Font loading warnings: {len(self.font_load_errors)} issues encountered")
            for error in self.font_load_errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
    
    def _load_style_fonts(self):
        """Load bold and italic font variants"""
        base_size = TextRenderingConfig.DEFAULT_FONT_SIZE
        
        # Bold font
        bold_loaded = False
        for font_base in ['arial', 'Arial', 'helvetica', 'Helvetica']:
            for suffix in ['bd', 'Bold', 'bold', '-Bold']:
                try:
                    self.fonts["bold"] = ImageFont.truetype(f"{font_base}{suffix}.ttf", base_size + 4)
                    bold_loaded = True
                    break
                except (IOError, OSError):
                    continue
            if bold_loaded:
                break
        
        if not bold_loaded:
            self.fonts["bold"] = self.fonts.get(
                f"comic_{base_size + 4}",
                self.fonts.get(f"comic_{base_size}", ImageFont.load_default())
            )
        
        # Italic font
        italic_loaded = False
        for font_base in ['arial', 'Arial', 'helvetica', 'Helvetica']:
            for suffix in ['i', 'Italic', 'italic', '-Italic']:
                try:
                    self.fonts["italic"] = ImageFont.truetype(f"{font_base}{suffix}.ttf", base_size)
                    italic_loaded = True
                    break
                except (IOError, OSError):
                    continue
            if italic_loaded:
                break
        
        if not italic_loaded:
            self.fonts["italic"] = self.fonts.get(
                f"comic_{base_size}",
                ImageFont.load_default()
            )
    
    def _get_panels_for_page(self, page_idx: int, page_data: Dict, 
                             panel_images: List[Dict]) -> List[Dict]:
        """Get panel images for a specific page"""
        page_panels = []
        page_num = page_idx + 1
        
        for panel_data in page_data.get('panels', []):
            panel_num = panel_data.get('panel_number', 1)
            
            # Find corresponding image
            for img_data in panel_images:
                if img_data.get('page') == page_num and img_data.get('panel') == panel_num:
                    # Combine script and image data
                    combined = {
                        **panel_data,
                        'image_data': img_data.get('image_data', {}),
                        'file_path': img_data.get('file_path')
                    }
                    page_panels.append(combined)
                    break
            else:
                # No image found, use placeholder
                page_panels.append(panel_data)
        
        return page_panels
    
    def _composite_page(self, page_idx: int, page_data: Dict, 
                       page_panels: List[Dict], config: Dict) -> Dict:
        """Composite panels into a single page with lettering"""
        
        # Get page layout
        layout_name = config.get('layout', 'standard')
        layout = self.page_layouts.get(layout_name, self.page_layouts['standard'])
        
        # Create page canvas
        page_img = Image.new('RGB', (layout['width'], layout['height']), 'white')
        draw = ImageDraw.Draw(page_img)
        
        # Calculate panel layout
        panel_positions = self._calculate_panel_layout(
            len(page_panels), layout['width'], layout['height'], layout['margin']
        )
        
        # Place each panel
        for panel_idx, (panel_data, position) in enumerate(zip(page_panels, panel_positions)):
            self._place_panel_on_page(
                page_img, panel_data, position, draw
            )
        
        # Add page number if requested
        if config.get('add_page_numbers', True):
            self._add_page_number(draw, page_idx + 1, layout)
        
        # Add borders if requested
        if config.get('add_borders', True):
            self._add_page_border(draw, layout)
        
        # Convert to base64
        buffer = io.BytesIO()
        page_img.save(buffer, format='PNG', dpi=(layout['dpi'], layout['dpi']))
        page_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "page_number": page_idx + 1,
            "panel_count": len(page_panels),
            "layout_used": layout_name,
            "dimensions": f"{layout['width']}x{layout['height']}",
            "image_data": {
                "base64": page_base64,
                "format": "png",
                "dpi": layout['dpi']
            }
        }
    
    def _calculate_panel_layout(self, panel_count: int, width: int, 
                               height: int, margin: int) -> List[Dict]:
        """Calculate panel positions for page layout"""
        positions = []
        
        # Simple grid layout based on panel count
        if panel_count == 1:
            # Full page
            positions.append({
                "x": margin,
                "y": margin,
                "width": width - 2 * margin,
                "height": height - 2 * margin
            })
        elif panel_count == 2:
            # Two horizontal panels
            panel_height = (height - 2 * margin - self.gutter_width) // 2
            positions.append({
                "x": margin,
                "y": margin,
                "width": width - 2 * margin,
                "height": panel_height
            })
            positions.append({
                "x": margin,
                "y": margin + panel_height + self.gutter_width,
                "width": width - 2 * margin,
                "height": panel_height
            })
        elif panel_count == 3:
            # One large panel on top, two small below
            top_height = (height - 2 * margin - self.gutter_width) * 2 // 3
            bottom_height = (height - 2 * margin - self.gutter_width) // 3
            panel_width = (width - 2 * margin - self.gutter_width) // 2
            
            positions.append({
                "x": margin,
                "y": margin,
                "width": width - 2 * margin,
                "height": top_height
            })
            positions.append({
                "x": margin,
                "y": margin + top_height + self.gutter_width,
                "width": panel_width,
                "height": bottom_height
            })
            positions.append({
                "x": margin + panel_width + self.gutter_width,
                "y": margin + top_height + self.gutter_width,
                "width": panel_width,
                "height": bottom_height
            })
        elif panel_count == 4:
            # 2x2 grid
            panel_width = (width - 2 * margin - self.gutter_width) // 2
            panel_height = (height - 2 * margin - self.gutter_width) // 2
            
            for row in range(2):
                for col in range(2):
                    positions.append({
                        "x": margin + col * (panel_width + self.gutter_width),
                        "y": margin + row * (panel_height + self.gutter_width),
                        "width": panel_width,
                        "height": panel_height
                    })
        elif panel_count <= 6:
            # 3x2 grid
            panel_width = (width - 2 * margin - self.gutter_width) // 2
            panel_height = (height - 2 * margin - 2 * self.gutter_width) // 3
            
            for i in range(panel_count):
                row = i // 2
                col = i % 2
                positions.append({
                    "x": margin + col * (panel_width + self.gutter_width),
                    "y": margin + row * (panel_height + self.gutter_width),
                    "width": panel_width,
                    "height": panel_height
                })
        else:
            # 3x3 grid for 7-9 panels
            panel_width = (width - 2 * margin - 2 * self.gutter_width) // 3
            panel_height = (height - 2 * margin - 2 * self.gutter_width) // 3
            
            for i in range(min(panel_count, 9)):
                row = i // 3
                col = i % 3
                positions.append({
                    "x": margin + col * (panel_width + self.gutter_width),
                    "y": margin + row * (panel_height + self.gutter_width),
                    "width": panel_width,
                    "height": panel_height
                })
        
        return positions
    
    def _place_panel_on_page(self, page_img: Image.Image, panel_data: Dict,
                            position: Dict, draw: ImageDraw.Draw):
        """Place a single panel on the page with lettering"""
        
        # Load or create panel image
        panel_img = self._load_panel_image(panel_data, position)
        
        # Paste panel onto page
        page_img.paste(panel_img, (position['x'], position['y']))
        
        # Draw panel border
        draw.rectangle([
            position['x'], position['y'],
            position['x'] + position['width'],
            position['y'] + position['height']
        ], outline='black', width=2)
        
        # Add dialogue and text
        self._add_panel_text(draw, panel_data, position)
    
    def _load_panel_image(self, panel_data: Dict, position: Dict) -> Image.Image:
        """Load panel image from file or base64"""
        
        # Try to load from file first
        if panel_data.get('file_path'):
            try:
                img = Image.open(panel_data['file_path'])
                # Resize to fit position
                img = img.resize((position['width'], position['height']), Image.Resampling.LANCZOS)
                return img
            except:
                pass
        
        # Try base64
        image_data = panel_data.get('image_data', {})
        if image_data.get('base64'):
            try:
                img_bytes = base64.b64decode(image_data['base64'])
                img = Image.open(io.BytesIO(img_bytes))
                img = img.resize((position['width'], position['height']), Image.Resampling.LANCZOS)
                return img
            except:
                pass
        
        # Create placeholder
        img = Image.new('RGB', (position['width'], position['height']), 'lightgray')
        placeholder_draw = ImageDraw.Draw(img)
        
        # Add panel number
        panel_num = panel_data.get('panel_number', '?')
        text = f"Panel {panel_num}"
        font = self.fonts.get('comic_24', ImageFont.load_default())
        
        # Center text
        bbox = placeholder_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (position['width'] - text_width) // 2
        y = (position['height'] - text_height) // 2
        
        placeholder_draw.text((x, y), text, fill='darkgray', font=font)
        
        return img
    
    def _add_panel_text(self, draw: ImageDraw.Draw, panel_data: Dict, position: Dict):
        """Add speech bubbles and text to panel"""
        
        dialogue_entries = panel_data.get('dialogue', [])
        if not dialogue_entries:
            return
        
        # Calculate bubble positions
        bubble_y = position['y'] + 20
        
        for dialogue in dialogue_entries:
            character = dialogue.get('character', 'Unknown')
            text = dialogue.get('text', '')
            bubble_type = dialogue.get('type', 'balloon')
            
            if not text:
                continue
            
            # Create speech bubble
            bubble_bounds = self._draw_speech_bubble(
                draw, text, character,
                position['x'] + 20,
                bubble_y,
                position['width'] - 40,
                bubble_type
            )
            
            # Move to next position
            bubble_y = bubble_bounds[3] + 10
            
            # Don't exceed panel bounds
            if bubble_y > position['y'] + position['height'] - 50:
                break
    
    def _draw_speech_bubble(self, draw: ImageDraw.Draw, text: str, character: str,
                           x: int, y: int, max_width: int, bubble_type: str) -> Tuple:
        """Draw a professional comic book speech bubble with configurable text rendering
        
        Args:
            draw: PIL ImageDraw object
            text: Dialogue text to display (character names NOT included)
            character: Character name (for context only, not displayed)
            x: X position for bubble
            y: Y position for bubble
            max_width: Maximum width constraint
            bubble_type: Type of bubble ('balloon', 'thought', 'shout')
            
        Returns:
            Tuple of bubble boundaries (x1, y1, x2, y2)
        """
        
        # Determine font size based on text length and bubble type
        if bubble_type == 'shout' or len(text) < 20:
            font_size = TextRenderingConfig.get_font_size('large')
        elif len(text) > 100:
            font_size = TextRenderingConfig.get_font_size('small')
        else:
            font_size = TextRenderingConfig.get_font_size('default')
        
        # Get appropriate font with error handling
        font = self._get_font_safe(font_size)
        
        # Calculate dynamic padding based on text length
        padding = TextRenderingConfig.get_bubble_padding(len(text))
        
        # STEP 1: Wrap text FIRST to determine actual text dimensions
        max_text_width = int(max_width * TextRenderingConfig.MAX_WIDTH_PERCENTAGE)
        wrapped_lines = self._wrap_text_professional(text, font, max_text_width)
        
        # STEP 2: Calculate bubble size AFTER text wrapping
        bubble_dimensions = self._calculate_bubble_dimensions(
            wrapped_lines, font, padding
        )
        bubble_width = bubble_dimensions['width']
        bubble_height = bubble_dimensions['height']
        line_height = bubble_dimensions['line_height']
        
        # STEP 3: Draw bubble background based on type
        bubble_bounds = self._draw_bubble_background(
            draw, x, y, bubble_width, bubble_height, bubble_type
        )
        
        # STEP 4: Render text with proper positioning and BLACK color
        self._render_bubble_text(
            draw, wrapped_lines, font, x, y, 
            bubble_width, bubble_height, padding, line_height
        )
        
        return bubble_bounds
    
    def _get_font_safe(self, size: int) -> ImageFont:
        """Safely get a font with fallback handling
        
        Args:
            size: Desired font size
            
        Returns:
            ImageFont object (guaranteed to return something)
        """
        # Try to get the exact size
        font_key = f"comic_{size}"
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        # Try nearest size
        available_sizes = [int(k.split('_')[1]) for k in self.fonts.keys() 
                          if k.startswith('comic_') and k.split('_')[1].isdigit()]
        if available_sizes:
            nearest_size = min(available_sizes, key=lambda x: abs(x - size))
            return self.fonts.get(f"comic_{nearest_size}", ImageFont.load_default())
        
        # Ultimate fallback
        return ImageFont.load_default()
    
    def _wrap_text_professional(self, text: str, font: ImageFont, max_width: int) -> List[str]:
        """Professional text wrapping with proper word breaking and hyphenation
        
        Args:
            text: Text to wrap
            font: Font to use for measurements
            max_width: Maximum line width in pixels
            
        Returns:
            List of wrapped text lines
        """
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test adding this word to current line
            test_line = ' '.join(current_line + [word])
            
            # Measure with proper method
            try:
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(test_line)
                    line_width = bbox[2] - bbox[0]
                else:
                    # Fallback for older PIL versions
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    line_width = bbox[2] - bbox[0]
            except AttributeError:
                # Ultimate fallback - estimate
                line_width = len(test_line) * (font.size * 0.6)
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                # Line would be too long
                if current_line:
                    # Save current line and start new one
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long - need to break it
                    broken_word = self._break_long_word(word, font, max_width)
                    lines.extend(broken_word[:-1])  # Add all but last part
                    current_line = [broken_word[-1]] if broken_word else []
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _break_long_word(self, word: str, font: ImageFont, max_width: int) -> List[str]:
        """Break a long word with hyphenation
        
        Args:
            word: Word to break
            font: Font for measurements
            max_width: Maximum width per line
            
        Returns:
            List of word parts with hyphens
        """
        if len(word) <= 5:  # Don't break very short words
            return [word]
        
        parts = []
        remaining = word
        
        while remaining:
            # Find maximum characters that fit
            for i in range(len(remaining), 0, -1):
                test_part = remaining[:i]
                if i < len(remaining):  # Not the last part
                    test_part += '-'
                
                try:
                    if hasattr(font, 'getbbox'):
                        bbox = font.getbbox(test_part)
                        width = bbox[2] - bbox[0]
                    else:
                        width = len(test_part) * (font.size * 0.6)
                except:
                    width = len(test_part) * 10  # Rough estimate
                
                if width <= max_width or i == 1:
                    if i < len(remaining):
                        parts.append(remaining[:i] + '-')
                        remaining = remaining[i:]
                    else:
                        parts.append(remaining)
                        remaining = ''
                    break
        
        return parts if parts else [word]
    
    def _calculate_bubble_dimensions(self, lines: List[str], font: ImageFont, 
                                    padding: int) -> Dict[str, int]:
        """Calculate bubble dimensions based on wrapped text
        
        Args:
            lines: Wrapped text lines
            font: Font being used
            padding: Padding value
            
        Returns:
            Dictionary with width, height, and line_height
        """
        if not lines:
            return {'width': 100, 'height': 50, 'line_height': 20}
        
        # Calculate line height
        font_size = getattr(font, 'size', TextRenderingConfig.DEFAULT_FONT_SIZE)
        line_height = int(font_size * TextRenderingConfig.LINE_HEIGHT_MULTIPLIER)
        
        # Find maximum line width
        max_line_width = 0
        for line in lines:
            try:
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                else:
                    line_width = len(line) * (font_size * 0.6)
            except:
                line_width = len(line) * 10
            
            max_line_width = max(max_line_width, line_width)
        
        # Calculate dimensions with padding
        bubble_width = int(max_line_width + (padding * 2))
        text_height = len(lines) * line_height
        bubble_height = int(text_height + (padding * 2))
        
        return {
            'width': bubble_width,
            'height': bubble_height,
            'line_height': line_height
        }
    
    def _draw_bubble_background(self, draw: ImageDraw.Draw, x: int, y: int,
                                width: int, height: int, bubble_type: str) -> Tuple:
        """Draw the bubble background shape
        
        Args:
            draw: ImageDraw object
            x, y: Position
            width, height: Dimensions
            bubble_type: Type of bubble
            
        Returns:
            Tuple of bubble boundaries
        """
        if bubble_type == 'thought':
            self._draw_thought_bubble_improved(draw, x, y, width, height)
        elif bubble_type == 'shout':
            self._draw_shout_bubble(draw, x, y, width, height)
        else:
            self._draw_speech_balloon_improved(draw, x, y, width, height)
        
        return (x, y, x + width, y + height)
    
    def _render_bubble_text(self, draw: ImageDraw.Draw, lines: List[str], 
                           font: ImageFont, x: int, y: int, 
                           bubble_width: int, bubble_height: int,
                           padding: int, line_height: int):
        """Render text inside bubble with proper alignment and BLACK color
        
        Args:
            draw: ImageDraw object
            lines: Text lines to render
            font: Font to use
            x, y: Bubble position
            bubble_width, bubble_height: Bubble dimensions
            padding: Internal padding
            line_height: Height between lines
        """
        # Calculate starting Y position (vertically centered)
        total_text_height = len(lines) * line_height
        text_y = y + (bubble_height - total_text_height) // 2
        
        # Render each line
        for line in lines:
            # Calculate line width for centering
            try:
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                else:
                    # Fallback
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_width = bbox[2] - bbox[0]
            except:
                line_width = len(line) * 10  # Rough estimate
            
            # Center horizontally
            text_x = x + (bubble_width - line_width) // 2
            
            # Draw text in BLACK for maximum contrast
            draw.text(
                (text_x, text_y), 
                line, 
                fill=TextRenderingConfig.TEXT_COLOR,  # Always BLACK
                font=font
            )
            
            text_y += line_height
    
    def _draw_speech_balloon_improved(self, draw: ImageDraw.Draw, x: int, y: int, 
                                     width: int, height: int):
        """Draw a professional speech balloon with improved styling"""
        # Calculate corner radius
        radius = min(width, height) // TextRenderingConfig.CORNER_RADIUS_RATIO
        
        # Fill colors from config
        fill_color = TextRenderingConfig.BUBBLE_FILL_COLOR
        outline_color = TextRenderingConfig.BUBBLE_OUTLINE_COLOR
        outline_width = TextRenderingConfig.BUBBLE_OUTLINE_WIDTH
        
        # Draw filled rounded rectangle
        self._draw_rounded_rectangle(
            draw, x, y, width, height, radius, 
            fill_color, outline_color, outline_width
        )
        
        # Draw tail with improved positioning
        tail_x = x + width // 3
        tail_points = [
            (tail_x, y + height - 1),
            (tail_x - TextRenderingConfig.TAIL_WIDTH // 2, 
             y + height + TextRenderingConfig.TAIL_HEIGHT),
            (tail_x + TextRenderingConfig.TAIL_WIDTH // 3, y + height - 2)
        ]
        
        # Draw tail with matching style
        draw.polygon(tail_points, fill=fill_color, outline=outline_color, width=outline_width - 1)
    
    def _draw_rounded_rectangle(self, draw: ImageDraw.Draw, x: int, y: int,
                                width: int, height: int, radius: int,
                                fill_color: str, outline_color: str, outline_width: int):
        """Draw a rounded rectangle with proper fill and outline"""
        # Main rectangular areas
        draw.rectangle([x + radius, y, x + width - radius, y + height], 
                      fill=fill_color, outline=None)
        draw.rectangle([x, y + radius, x + width, y + height - radius], 
                      fill=fill_color, outline=None)
        
        # Corner circles
        corners = [
            (x, y, x + radius * 2, y + radius * 2),  # Top-left
            (x + width - radius * 2, y, x + width, y + radius * 2),  # Top-right
            (x, y + height - radius * 2, x + radius * 2, y + height),  # Bottom-left
            (x + width - radius * 2, y + height - radius * 2, x + width, y + height)  # Bottom-right
        ]
        
        for corner in corners:
            draw.ellipse(corner, fill=fill_color, outline=None)
        
        # Draw outline arcs for corners
        draw.arc([x, y, x + radius * 2, y + radius * 2], 
                180, 270, fill=outline_color, width=outline_width)
        draw.arc([x + width - radius * 2, y, x + width, y + radius * 2], 
                270, 0, fill=outline_color, width=outline_width)
        draw.arc([x, y + height - radius * 2, x + radius * 2, y + height], 
                90, 180, fill=outline_color, width=outline_width)
        draw.arc([x + width - radius * 2, y + height - radius * 2, x + width, y + height], 
                0, 90, fill=outline_color, width=outline_width)
        
        # Draw straight line segments
        draw.line([x + radius, y, x + width - radius, y], 
                 fill=outline_color, width=outline_width)
        draw.line([x + radius, y + height, x + width - radius, y + height], 
                 fill=outline_color, width=outline_width)
        draw.line([x, y + radius, x, y + height - radius], 
                 fill=outline_color, width=outline_width)
        draw.line([x + width, y + radius, x + width, y + height - radius], 
                 fill=outline_color, width=outline_width)
    
    def _draw_shout_bubble(self, draw: ImageDraw.Draw, x: int, y: int,
                          width: int, height: int):
        """Draw a jagged shout/exclamation bubble"""
        # Create star-burst pattern for shouting
        import math
        
        center_x = x + width // 2
        center_y = y + height // 2
        
        # Create jagged outline points
        points = []
        num_points = 16
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            if i % 2 == 0:
                # Outer point
                radius = min(width, height) // 2
            else:
                # Inner point
                radius = min(width, height) // 2.5
            
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        # Draw filled shape
        draw.polygon(points, fill=TextRenderingConfig.BUBBLE_FILL_COLOR, 
                    outline=TextRenderingConfig.BUBBLE_OUTLINE_COLOR, 
                    width=TextRenderingConfig.BUBBLE_OUTLINE_WIDTH)
    
    def _draw_thought_bubble_improved(self, draw: ImageDraw.Draw, x: int, y: int,
                                     width: int, height: int):
        """Draw a simple thought bubble with cloud-like appearance"""
        # Use config colors
        fill_color = TextRenderingConfig.BUBBLE_FILL_COLOR
        outline_color = TextRenderingConfig.BUBBLE_OUTLINE_COLOR
        outline_width = TextRenderingConfig.BUBBLE_OUTLINE_WIDTH
        
        # Simple cloud shape - just overlapping circles
        # This creates a classic thought bubble look
        circles = [
            (x + width * 0.2, y + height * 0.3, width * 0.35),
            (x + width * 0.5, y + height * 0.2, width * 0.4),
            (x + width * 0.7, y + height * 0.3, width * 0.35),
            (x + width * 0.3, y + height * 0.6, width * 0.35),
            (x + width * 0.6, y + height * 0.6, width * 0.35),
        ]
        
        # Draw filled circles first
        for cx, cy, size in circles:
            draw.ellipse([cx - size/2, cy - size/2, cx + size/2, cy + size/2],
                        fill=fill_color)
        
        # Draw outlines
        for cx, cy, size in circles:
            draw.ellipse([cx - size/2, cy - size/2, cx + size/2, cy + size/2],
                        outline=outline_color, width=outline_width)
        
        # Draw thought tail bubbles
        bubble_size = TextRenderingConfig.THOUGHT_BUBBLE_SIZE
        tail_x = x + width // 3
        
        # Three decreasing bubbles
        bubbles = [
            (tail_x - bubble_size // 2, y + height, bubble_size, bubble_size),
            (tail_x - bubble_size // 3, y + height + bubble_size, 
             bubble_size * 0.7, bubble_size * 0.7),
            (tail_x - bubble_size // 4, y + height + bubble_size * 1.5, 
             bubble_size * 0.4, bubble_size * 0.4),
        ]
        
        for bx, by, bw, bh in bubbles:
            draw.ellipse([bx, by, bx + bw, by + bh], 
                        fill=fill_color, outline=outline_color, width=outline_width)
    
    # Note: _wrap_text method has been replaced with _wrap_text_professional above
    
    def _add_page_number(self, draw: ImageDraw.Draw, page_num: int, layout: Dict):
        """Add page number to bottom of page"""
        font = self.fonts.get('comic_12', ImageFont.load_default())
        text = str(page_num)
        
        # Calculate position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (layout['width'] - text_width) // 2
        y = layout['height'] - 30
        
        draw.text((x, y), text, fill='black', font=font)
    
    def _add_page_border(self, draw: ImageDraw.Draw, layout: Dict):
        """Add border around page"""
        draw.rectangle([
            5, 5,
            layout['width'] - 5,
            layout['height'] - 5
        ], outline='black', width=2)
    
    def _create_artifact(self, composed_pages: List[Dict], comic_pages: List[Dict],
                        project_id: str, upstream_hash: str, config: Dict) -> Dict:
        """Create Step 14 artifact"""
        
        return {
            "metadata": {
                "step": 14,
                "step_name": "panel_composition",
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "source_steps": [11, 13],
                "upstream_hash": upstream_hash
            },
            "composition_config": config,
            "pages": composed_pages,
            "statistics": {
                "total_pages": len(composed_pages),
                "total_panels": sum(len(p.get('panels', [])) for p in comic_pages),
                "layout_used": config.get('layout', 'standard'),
                "page_dimensions": self.page_layouts[config.get('layout', 'standard')]
            }
        }
    
    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> str:
        """Save artifact and composed pages"""
        
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create pages directory
        pages_path = project_path / "comic_pages"
        pages_path.mkdir(exist_ok=True)
        
        # Save each page image
        for page_data in artifact['pages']:
            page_num = page_data['page_number']
            image_data = page_data.get('image_data', {})
            
            if image_data.get('base64'):
                # Save the page image
                filename = f"page_{page_num:03d}.png"
                image_path = pages_path / filename
                
                # Decode and save
                image_bytes = base64.b64decode(image_data['base64'])
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Update page data with file path
                page_data['file_path'] = str(image_path)
        
        # Save JSON artifact (without base64 to reduce size)
        save_artifact = artifact.copy()
        for page in save_artifact['pages']:
            if 'image_data' in page and 'base64' in page['image_data']:
                del page['image_data']['base64']
        
        artifact_path = project_path / "step_14_panel_composition.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(save_artifact, f, indent=2, ensure_ascii=False)
        
        return str(artifact_path)

if __name__ == "__main__":
    # Test the implementation
    step14 = Step14PanelComposition()
    print("Step 14: Panel Composition and Lettering initialized")
    print("Features: Panel layout, speech bubbles, text placement")