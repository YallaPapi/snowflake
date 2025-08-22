"""Debug dialogue processing in Step 14"""

# Create minimal test data
step11_data = {
    "pages": [
        {
            "page_number": 1,
            "panels": [
                {
                    "panel_number": 2,
                    "dialogue": [
                        {"character": "Sakura", "type": "thought", "text": "Finally found it!"}
                    ]
                }
            ]
        }
    ]
}

step13_data = {
    "panels": [
        {
            "page": 1,
            "panel": 2,
            "file_path": "dummy.png"
        }
    ]
}

# Test the dialogue merging
from src.pipeline.steps.step_14_panel_composition import Step14PanelComposition

compositor = Step14PanelComposition()

# Get panels for page
page_data = step11_data["pages"][0]
panel_images = step13_data["panels"]

print("Original dialogue from step11:")
for panel in page_data["panels"]:
    if panel["panel_number"] == 2:
        print(f"  Panel 2 dialogue: {panel['dialogue']}")

print("\nCalling _get_panels_for_page...")
page_panels = compositor._get_panels_for_page(0, page_data, panel_images)

print(f"\nResult: {len(page_panels)} panels")
for i, panel in enumerate(page_panels):
    dialogue = panel.get('dialogue', [])
    print(f"Panel {i+1} dialogue: {dialogue}")
    print(f"  Number of entries: {len(dialogue)}")
    if dialogue:
        for j, d in enumerate(dialogue):
            print(f"    Entry {j+1}: {d}")