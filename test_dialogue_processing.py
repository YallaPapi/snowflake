"""
Test to understand how dialogue is being processed
"""

import json
from pathlib import Path

# Check the most recent step 14 artifact
artifacts = sorted(Path('artifacts').glob('*/step_14_panel_composition.json'))
if artifacts:
    with open(artifacts[-1]) as f:
        data = json.load(f)
    
    print(f"Checking artifact: {artifacts[-1]}")
    print("="*60)
    
    # Look for all panels and their dialogue
    for page in data.get('pages', []):
        page_num = page.get('page_number', 0)
        print(f"\nPage {page_num}:")
        for panel in page.get('panels', []):
            panel_num = panel.get('panel_number', 0)
            dialogue = panel.get('dialogue', [])
            print(f"  Panel {panel_num}: {len(dialogue)} dialogue entries")
            for i, d in enumerate(dialogue):
                print(f"    Entry {i+1}: type={d.get('type')}, char={d.get('character')}, text='{d.get('text')}'")

# Also check step 11 data to see the original
print("\n" + "="*60)
print("Checking original script data from step 11:")

# Look for generate_anime_fixed.py's step11_data
import sys
sys.path.insert(0, 'src')

# Import and check the test data directly
exec(open('generate_anime_fixed.py').read())

# The step11_data should now be in locals
if 'step11_data' in locals():
    for page in step11_data['pages']:
        page_num = page['page_number']
        print(f"\nPage {page_num}:")
        for panel in page['panels']:
            panel_num = panel['panel_number']
            dialogue = panel.get('dialogue', [])
            print(f"  Panel {panel_num}: {len(dialogue)} dialogue entries")
            for i, d in enumerate(dialogue):
                print(f"    Entry {i+1}: type={d.get('type')}, char={d.get('character')}, text='{d.get('text')}'")