"""
Test script to reproduce Panel 2 issue with "Finally found it!" thought bubble
"""

from src.pipeline.steps.step_14_panel_composition import Step14PanelComposition
from PIL import Image, ImageDraw

# Create test instance
compositor = Step14PanelComposition()

# Create a test image  
test_img = Image.new('RGB', (800, 600), 'white')
draw = ImageDraw.Draw(test_img)

# Load fonts
compositor._load_fonts()

# Test Panel 2 dialogue that's causing issues
panel2_dialogue = {
    "text": "Finally found it!",
    "character": "Sakura",
    "type": "thought"
}

print(f"Testing dialogue: '{panel2_dialogue['text']}'")
print(f"Character: {panel2_dialogue['character']}")
print(f"Type: {panel2_dialogue['type']}")

# Get font
font = compositor.fonts.get('comic_36', compositor.fonts.get('comic_24'))

# Test text wrapping to see what happens
max_width = 400
print(f"\nTesting _wrap_text_professional with max_width={max_width}:")
wrapped_lines = compositor._wrap_text_professional(panel2_dialogue["text"], font, max_width)
print(f"Wrapped into {len(wrapped_lines)} lines:")
for i, line in enumerate(wrapped_lines, 1):
    print(f"  Line {i}: '{line}'")

# Draw the thought bubble
print("\nDrawing thought bubble...")
bounds = compositor._draw_speech_bubble(
    draw,
    panel2_dialogue["text"],
    panel2_dialogue["character"],
    100,  # x
    100,  # y
    600,  # max_width
    panel2_dialogue["type"]
)

print(f"Bubble bounds: {bounds}")

# Save test image
test_img.save("test_panel2_issue.png")
print("\nTest image saved as test_panel2_issue.png")
print("Check if multiple bubbles or overlapping text appears!")