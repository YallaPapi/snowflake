#!/usr/bin/env python3
"""Test DOCX and EPUB export functionality"""

import json
from pathlib import Path
from src.export.manuscript_exporter import ManuscriptExporter

def test_export():
    # Create a minimal manuscript for testing
    manuscript = {
        "manuscript": {
            "chapters": [
                {
                    "number": 1,
                    "title": "Chapter 1: The Beginning",
                    "scenes": [
                        {
                            "scene_number": 1,
                            "pov": "Test Character",
                            "type": "Proactive",
                            "summary": "Opening scene",
                            "prose": "This is the opening scene. " * 50,  # ~50 words
                            "word_count": 50
                        },
                        {
                            "scene_number": 2,
                            "pov": "Test Character",
                            "type": "Reactive",
                            "summary": "Response scene",
                            "prose": "This is the response scene. " * 50,
                            "word_count": 50
                        }
                    ]
                },
                {
                    "number": 2,
                    "title": "Chapter 2: The Middle",
                    "scenes": [
                        {
                            "scene_number": 3,
                            "pov": "Test Character",
                            "type": "Proactive",
                            "summary": "Middle scene",
                            "prose": "This is the middle scene. " * 50,
                            "word_count": 50
                        }
                    ]
                }
            ],
            "total_chapters": 2,
            "total_scenes": 3,
            "total_word_count": 150
        },
        "metadata": {
            "project_id": "test_export",
            "title": "Test Novel",
            "author": "Test Author"
        }
    }
    
    # Initialize exporter
    exporter = ManuscriptExporter(project_dir="test_exports")
    
    # Test DOCX export
    print("Testing DOCX export...")
    try:
        docx_path = exporter.export_docx(
            manuscript,
            project_id="test_export"
        )
        print(f"[PASS] DOCX exported to {docx_path}")
    except Exception as e:
        print(f"[FAIL] DOCX export failed: {e}")
    
    # Test EPUB export
    print("\nTesting EPUB export...")
    try:
        epub_path = exporter.export_epub(
            manuscript,
            project_id="test_export"
        )
        print(f"[PASS] EPUB exported to {epub_path}")
    except Exception as e:
        print(f"[FAIL] EPUB export failed: {e}")
    
    # Test Markdown export
    print("\nTesting Markdown export...")
    try:
        md_path = exporter.export_markdown(
            manuscript,
            project_id="test_export"
        )
        print(f"[PASS] Markdown exported to {md_path}")
    except Exception as e:
        print(f"[FAIL] Markdown export failed: {e}")
    
    # List exported files
    export_dir = Path("test_exports/test_export")
    if export_dir.exists():
        print(f"\nExported files:")
        for file in export_dir.iterdir():
            size = file.stat().st_size
            print(f"  - {file.name} ({size:,} bytes)")

if __name__ == "__main__":
    test_export()