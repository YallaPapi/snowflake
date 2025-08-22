"""
Step 15 Implementation: Graphic Novel Assembly
Assembles composed comic pages into complete graphic novel files (CBZ, PDF, EPUB)
"""

import json
import hashlib
import base64
import io
import zipfile
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET

from src.pipeline.validators.step_15_validator import Step15Validator

class Step15GraphicNovelAssembly:
    """
    Assembles comic pages into complete graphic novel files
    
    Supported formats:
    - CBZ (Comic Book ZIP) - Industry standard
    - PDF - Universal viewing
    - EPUB - E-reader format with images
    - Web format - HTML viewer
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step15Validator()
        
        # Export format configurations
        self.format_configs = {
            "cbz": {
                "extension": ".cbz",
                "mime_type": "application/x-cbz",
                "compression": zipfile.ZIP_DEFLATED
            },
            "pdf": {
                "extension": ".pdf",
                "mime_type": "application/pdf"
            },
            "epub": {
                "extension": ".epub",
                "mime_type": "application/epub+zip"
            },
            "web": {
                "extension": ".html",
                "mime_type": "text/html"
            }
        }
    
    def execute(self,
                step14_artifact: Dict[str, Any],
                step11_artifact: Dict[str, Any],
                project_id: str,
                assembly_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute Step 15: Assemble graphic novel
        
        Args:
            step14_artifact: Composed pages with lettering
            step11_artifact: Comic script metadata
            project_id: Project identifier
            assembly_config: Assembly configuration
            
        Returns:
            Tuple of (success, assembled_novel_artifact, message)
        """
        if not assembly_config:
            assembly_config = {
                "formats": ["cbz", "pdf"],  # Default formats
                "title": "Untitled Graphic Novel",
                "author": "AI Generated",
                "include_cover": True,
                "include_metadata": True
            }
        
        try:
            # Calculate upstream hash
            upstream_hash = hashlib.sha256(
                json.dumps({"step14": step14_artifact, "step11": step11_artifact}, sort_keys=True).encode()
            ).hexdigest()
            
            # Extract metadata
            metadata = self._extract_metadata(step11_artifact, assembly_config)
            
            # Get composed pages
            composed_pages = step14_artifact.get('pages', [])
            
            if not composed_pages:
                return False, {}, "No pages found to assemble"
            
            # Generate cover if requested
            cover_image = None
            if assembly_config.get('include_cover', True):
                cover_image = self._generate_cover(metadata, composed_pages[0])
            
            # Assemble in requested formats
            print(f"Assembling graphic novel in {len(assembly_config['formats'])} formats...")
            assembled_files = {}
            
            for format_name in assembly_config['formats']:
                if format_name not in self.format_configs:
                    print(f"  Warning: Unknown format {format_name}, skipping")
                    continue
                
                print(f"  Assembling {format_name.upper()} format...")
                
                if format_name == 'cbz':
                    file_path = self._assemble_cbz(
                        composed_pages, metadata, cover_image, project_id
                    )
                elif format_name == 'pdf':
                    file_path = self._assemble_pdf(
                        composed_pages, metadata, cover_image, project_id
                    )
                elif format_name == 'epub':
                    file_path = self._assemble_epub(
                        composed_pages, metadata, cover_image, project_id
                    )
                elif format_name == 'web':
                    file_path = self._assemble_web(
                        composed_pages, metadata, cover_image, project_id
                    )
                else:
                    continue
                
                assembled_files[format_name] = file_path
                print(f"    Saved to: {file_path}")
            
            # Create artifact
            artifact = self._create_artifact(
                assembled_files, metadata, composed_pages,
                project_id, upstream_hash, assembly_config
            )
            
            # Validate
            is_valid, errors = self.validator.validate(artifact)
            if not is_valid:
                return False, {}, f"Validation failed: {errors}"
            
            # Save artifact
            artifact_path = self._save_artifact(artifact, project_id)
            
            formats_created = ", ".join(assembled_files.keys())
            return True, artifact, f"Step 15 completed. Created: {formats_created}"
            
        except Exception as e:
            return False, {}, f"Error in Step 15: {str(e)}"
    
    def _extract_metadata(self, step11_artifact: Dict, config: Dict) -> Dict:
        """Extract metadata for the graphic novel"""
        
        metadata = {
            "title": config.get('title', 'Untitled Graphic Novel'),
            "author": config.get('author', 'AI Generated'),
            "created_date": datetime.utcnow().isoformat(),
            "generator": "Snowflake Graphic Novel Pipeline",
            "total_pages": step11_artifact.get('total_pages', 0),
            "total_panels": step11_artifact.get('total_panels', 0),
            "script_format": step11_artifact.get('script_format', 'full_script')
        }
        
        # Add character information
        character_designs = step11_artifact.get('character_designs', {})
        if character_designs:
            metadata['characters'] = list(character_designs.keys())
        
        return metadata
    
    def _generate_cover(self, metadata: Dict, first_page: Dict) -> Dict:
        """Generate a cover image for the graphic novel"""
        
        # Create cover image
        cover_img = Image.new('RGB', (1650, 2550), 'black')
        draw = ImageDraw.Draw(cover_img)
        
        # Try to use a nice font
        try:
            from PIL import ImageFont
            title_font = ImageFont.truetype("arial.ttf", 120)
            author_font = ImageFont.truetype("arial.ttf", 60)
            info_font = ImageFont.truetype("arial.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
        
        # Add gradient background
        for y in range(2550):
            color_value = int(20 + (y / 2550) * 60)  # Dark gradient
            draw.rectangle([(0, y), (1650, y+1)], fill=(color_value, color_value, color_value + 10))
        
        # Add title
        title = metadata['title']
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (1650 - title_width) // 2
        draw.text((title_x, 400), title, fill='white', font=title_font)
        
        # Add decorative line
        draw.rectangle([(300, 600), (1350, 605)], fill='red')
        
        # Add sample panel from first page if available
        if first_page and first_page.get('file_path'):
            try:
                sample_img = Image.open(first_page['file_path'])
                # Resize to fit in cover
                sample_img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                # Center on cover
                sample_x = (1650 - sample_img.width) // 2
                cover_img.paste(sample_img, (sample_x, 700))
            except:
                # Draw placeholder
                draw.rectangle([(325, 700), (1325, 1900)], outline='white', width=3)
                draw.text((825, 1300), "[Preview]", fill='gray', font=info_font, anchor='mm')
        
        # Add author
        author = f"by {metadata['author']}"
        author_bbox = draw.textbbox((0, 0), author, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (1650 - author_width) // 2
        draw.text((author_x, 2000), author, fill='white', font=author_font)
        
        # Add info
        info_text = f"{metadata['total_pages']} Pages • {metadata['total_panels']} Panels"
        info_bbox = draw.textbbox((0, 0), info_text, font=info_font)
        info_width = info_bbox[2] - info_bbox[0]
        info_x = (1650 - info_width) // 2
        draw.text((info_x, 2200), info_text, fill='lightgray', font=info_font)
        
        # Convert to base64
        buffer = io.BytesIO()
        cover_img.save(buffer, format='PNG')
        cover_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "type": "cover",
            "format": "png",
            "base64": cover_base64,
            "dimensions": "1650x2550"
        }
    
    def _assemble_cbz(self, pages: List[Dict], metadata: Dict, 
                     cover: Optional[Dict], project_id: str) -> str:
        """Assemble CBZ (Comic Book ZIP) file"""
        
        project_path = self.project_dir / project_id
        cbz_path = project_path / f"{metadata['title'].replace(' ', '_')}.cbz"
        
        with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
            # Add metadata as ComicInfo.xml (standard for CBZ)
            comic_info = self._create_comic_info_xml(metadata)
            cbz.writestr("ComicInfo.xml", comic_info)
            
            # Add cover if available
            if cover and cover.get('base64'):
                cover_data = base64.b64decode(cover['base64'])
                cbz.writestr("000_cover.png", cover_data)
            
            # Add all pages
            for page in pages:
                page_num = page.get('page_number', 0)
                
                # Try to get image data
                image_data = None
                if page.get('file_path') and os.path.exists(page['file_path']):
                    with open(page['file_path'], 'rb') as f:
                        image_data = f.read()
                elif page.get('image_data', {}).get('base64'):
                    image_data = base64.b64decode(page['image_data']['base64'])
                
                if image_data:
                    filename = f"{page_num:03d}.png"
                    cbz.writestr(filename, image_data)
        
        return str(cbz_path)
    
    def _create_comic_info_xml(self, metadata: Dict) -> str:
        """Create ComicInfo.xml for CBZ metadata"""
        
        root = ET.Element("ComicInfo")
        
        # Add metadata elements
        ET.SubElement(root, "Title").text = metadata['title']
        ET.SubElement(root, "Writer").text = metadata['author']
        ET.SubElement(root, "Publisher").text = "AI Generated"
        ET.SubElement(root, "PageCount").text = str(metadata['total_pages'])
        ET.SubElement(root, "Year").text = str(datetime.now().year)
        ET.SubElement(root, "Month").text = str(datetime.now().month)
        ET.SubElement(root, "Day").text = str(datetime.now().day)
        
        # Add characters if available
        if metadata.get('characters'):
            ET.SubElement(root, "Characters").text = ", ".join(metadata['characters'])
        
        # Convert to string
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _assemble_pdf(self, pages: List[Dict], metadata: Dict,
                     cover: Optional[Dict], project_id: str) -> str:
        """Assemble PDF file"""
        
        project_path = self.project_dir / project_id
        pdf_path = project_path / f"{metadata['title'].replace(' ', '_')}.pdf"
        
        # Collect all images
        images = []
        
        # Add cover if available
        if cover and cover.get('base64'):
            cover_data = base64.b64decode(cover['base64'])
            cover_img = Image.open(io.BytesIO(cover_data))
            images.append(cover_img)
        
        # Add all pages
        for page in pages:
            image = None
            
            # Try to load image
            if page.get('file_path') and os.path.exists(page['file_path']):
                image = Image.open(page['file_path'])
            elif page.get('image_data', {}).get('base64'):
                image_data = base64.b64decode(page['image_data']['base64'])
                image = Image.open(io.BytesIO(image_data))
            
            if image:
                # Convert to RGB if necessary (PDF doesn't support RGBA)
                if image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', image.size, 'white')
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                images.append(image)
        
        # Save as PDF
        if images:
            images[0].save(
                pdf_path,
                "PDF",
                save_all=True,
                append_images=images[1:],
                title=metadata['title'],
                author=metadata['author']
            )
        
        return str(pdf_path)
    
    def _assemble_epub(self, pages: List[Dict], metadata: Dict,
                      cover: Optional[Dict], project_id: str) -> str:
        """Assemble EPUB file (simplified comic EPUB)"""
        
        project_path = self.project_dir / project_id
        epub_path = project_path / f"{metadata['title'].replace(' ', '_')}.epub"
        
        # Create EPUB structure in memory
        with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            # Add mimetype (must be first and uncompressed)
            epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            
            # Add META-INF/container.xml
            container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
            epub.writestr("META-INF/container.xml", container_xml)
            
            # Create content.opf
            content_opf = self._create_epub_content_opf(metadata, pages, cover is not None)
            epub.writestr("OEBPS/content.opf", content_opf)
            
            # Add cover if available
            if cover and cover.get('base64'):
                cover_data = base64.b64decode(cover['base64'])
                epub.writestr("OEBPS/images/cover.png", cover_data)
            
            # Add all page images
            for idx, page in enumerate(pages):
                image_data = None
                
                if page.get('file_path') and os.path.exists(page['file_path']):
                    with open(page['file_path'], 'rb') as f:
                        image_data = f.read()
                elif page.get('image_data', {}).get('base64'):
                    image_data = base64.b64decode(page['image_data']['base64'])
                
                if image_data:
                    epub.writestr(f"OEBPS/images/page_{idx:03d}.png", image_data)
                    
                    # Create XHTML wrapper for image
                    xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Page {idx + 1}</title>
    <style>img {{ max-width: 100%; height: auto; }}</style>
</head>
<body>
    <div><img src="../images/page_{idx:03d}.png" alt="Page {idx + 1}"/></div>
</body>
</html>'''
                    epub.writestr(f"OEBPS/text/page_{idx:03d}.xhtml", xhtml)
        
        return str(epub_path)
    
    def _create_epub_content_opf(self, metadata: Dict, pages: List[Dict], has_cover: bool) -> str:
        """Create content.opf for EPUB"""
        
        opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{metadata['title']}</dc:title>
        <dc:creator>{metadata['author']}</dc:creator>
        <dc:language>en</dc:language>
        <dc:identifier id="uid">graphic-novel-{hash(metadata['title'])}</dc:identifier>
        <meta name="cover" content="cover-image"/>
    </metadata>
    <manifest>'''
        
        # Add cover if available
        if has_cover:
            opf += '''
        <item id="cover-image" href="images/cover.png" media-type="image/png"/>'''
        
        # Add pages
        for idx in range(len(pages)):
            opf += f'''
        <item id="page{idx}" href="text/page_{idx:03d}.xhtml" media-type="application/xhtml+xml"/>
        <item id="image{idx}" href="images/page_{idx:03d}.png" media-type="image/png"/>'''
        
        opf += '''
    </manifest>
    <spine>'''
        
        # Add pages to spine
        for idx in range(len(pages)):
            opf += f'''
        <itemref idref="page{idx}"/>'''
        
        opf += '''
    </spine>
</package>'''
        
        return opf
    
    def _assemble_web(self, pages: List[Dict], metadata: Dict,
                     cover: Optional[Dict], project_id: str) -> str:
        """Assemble web viewer HTML"""
        
        project_path = self.project_dir / project_id
        web_path = project_path / "web_viewer"
        web_path.mkdir(exist_ok=True)
        
        # Save images
        image_files = []
        
        if cover and cover.get('base64'):
            cover_path = web_path / "cover.png"
            with open(cover_path, 'wb') as f:
                f.write(base64.b64decode(cover['base64']))
            image_files.append("cover.png")
        
        for idx, page in enumerate(pages):
            if page.get('file_path') and os.path.exists(page['file_path']):
                # Copy existing file
                import shutil
                dest_path = web_path / f"page_{idx:03d}.png"
                shutil.copy(page['file_path'], dest_path)
                image_files.append(f"page_{idx:03d}.png")
            elif page.get('image_data', {}).get('base64'):
                # Save from base64
                dest_path = web_path / f"page_{idx:03d}.png"
                with open(dest_path, 'wb') as f:
                    f.write(base64.b64decode(page['image_data']['base64']))
                image_files.append(f"page_{idx:03d}.png")
        
        # Create HTML viewer
        html_content = self._create_web_viewer_html(metadata, image_files)
        html_path = web_path / "index.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_path)
    
    def _create_web_viewer_html(self, metadata: Dict, image_files: List[str]) -> str:
        """Create HTML viewer for web format"""
        
        images_json = json.dumps(image_files)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        #header {{
            background: #2a2a2a;
            color: white;
            padding: 20px;
            width: 100%;
            text-align: center;
        }}
        #viewer {{
            max-width: 100%;
            margin: 20px;
        }}
        #viewer img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        }}
        #controls {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            padding: 10px 20px;
            border-radius: 25px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
        }}
        button:hover {{
            background: #45a049;
        }}
        button:disabled {{
            background: #666;
            cursor: not-allowed;
        }}
        #pageInfo {{
            color: white;
            margin: 0 20px;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>{metadata['title']}</h1>
        <p>by {metadata['author']} • {metadata['total_pages']} Pages</p>
    </div>
    
    <div id="viewer">
        <img id="pageImage" src="" alt="Comic Page">
    </div>
    
    <div id="controls">
        <button id="prevBtn" onclick="prevPage()">← Previous</button>
        <span id="pageInfo">Page 1 / {len(image_files)}</span>
        <button id="nextBtn" onclick="nextPage()">Next →</button>
    </div>
    
    <script>
        const images = {images_json};
        let currentPage = 0;
        
        function showPage(index) {{
            if (index >= 0 && index < images.length) {{
                document.getElementById('pageImage').src = images[index];
                document.getElementById('pageInfo').textContent = `Page ${{index + 1}} / ${{images.length}}`;
                currentPage = index;
                
                // Update button states
                document.getElementById('prevBtn').disabled = (index === 0);
                document.getElementById('nextBtn').disabled = (index === images.length - 1);
            }}
        }}
        
        function nextPage() {{
            if (currentPage < images.length - 1) {{
                showPage(currentPage + 1);
            }}
        }}
        
        function prevPage() {{
            if (currentPage > 0) {{
                showPage(currentPage - 1);
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowRight') nextPage();
            if (e.key === 'ArrowLeft') prevPage();
        }});
        
        // Initialize
        showPage(0);
    </script>
</body>
</html>'''
    
    def _create_artifact(self, assembled_files: Dict[str, str], metadata: Dict,
                        pages: List[Dict], project_id: str, 
                        upstream_hash: str, config: Dict) -> Dict:
        """Create Step 15 artifact"""
        
        return {
            "metadata": {
                "step": 15,
                "step_name": "graphic_novel_assembly",
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "source_steps": [11, 14],
                "upstream_hash": upstream_hash
            },
            "novel_metadata": metadata,
            "assembly_config": config,
            "assembled_files": assembled_files,
            "statistics": {
                "formats_created": list(assembled_files.keys()),
                "total_pages": len(pages),
                "has_cover": config.get('include_cover', False),
                "file_sizes": {
                    format_name: os.path.getsize(path) if os.path.exists(path) else 0
                    for format_name, path in assembled_files.items()
                }
            }
        }
    
    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> str:
        """Save artifact"""
        
        project_path = self.project_dir / project_id
        artifact_path = project_path / "step_15_graphic_novel_assembly.json"
        
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)
        
        return str(artifact_path)

if __name__ == "__main__":
    # Test the implementation
    step15 = Step15GraphicNovelAssembly()
    print("Step 15: Graphic Novel Assembly initialized")
    print("Supported formats: CBZ, PDF, EPUB, Web")
    print("Features: Cover generation, metadata embedding, multiple export formats")