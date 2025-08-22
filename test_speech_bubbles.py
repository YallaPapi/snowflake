"""
Test script for speech bubble rendering fixes
"""

from src.pipeline.steps.step_14_panel_composition import Step14PanelComposition
from PIL import Image, ImageDraw
import json

# Create test instance
compositor = Step14PanelComposition()

# Create a test image
test_img = Image.new('RGB', (800, 600), 'lightblue')
draw = ImageDraw.Draw(test_img)

# Load fonts
compositor._load_fonts()

# Test dialogue samples
test_dialogues = [
    {
        "text": "This is a test of the improved speech bubble system with much larger text!",
        "character": "Hero",
        "type": "balloon"
    },
    {
        "text": "The text should now be 36pt and properly centered without character names.",
        "character": "Villain", 
        "type": "balloon"
    },
    {
        "text": "I'm thinking about the new text rendering...",
        "character": "Narrator",
        "type": "thought"
    }
]

# Test drawing bubbles
y_position = 50
for dialogue in test_dialogues:
    bounds = compositor._draw_speech_bubble(
        draw,
        dialogue["text"],
        dialogue["character"],
        50,  # x
        y_position,  # y
        700,  # max_width
        dialogue["type"]
    )
    y_position = bounds[3] + 30  # Move to next position

# Save test image
test_img.save("test_speech_bubbles.png")
print("Test image saved as test_speech_bubbles.png")

# Test text wrapping
print("\nTesting text wrapping:")
font = compositor.fonts.get('comic_36', None)
if font:
    test_text = "This is a very long piece of dialogue that should wrap properly within the speech bubble boundaries without breaking words unnecessarily."
    wrapped = compositor._wrap_text_professional(test_text, font, 400)
    print(f"Original: {test_text}")
    print(f"Wrapped ({len(wrapped)} lines):")
    for i, line in enumerate(wrapped, 1):
        print(f"  {i}: {line}")
else:
    print("Could not load font for wrapping test")

print("\nText configuration:")
print(json.dumps(compositor.text_config, indent=2))