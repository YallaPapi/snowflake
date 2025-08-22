"""Debug text rendering to see if it's called multiple times"""

from src.pipeline.steps.step_14_panel_composition import Step14PanelComposition
from PIL import Image, ImageDraw
import sys

# Monkey-patch the _render_bubble_text method to add logging
original_render = Step14PanelComposition._render_bubble_text

call_count = 0

def logged_render(self, draw, lines, font, x, y, bubble_width, bubble_height, padding, line_height):
    global call_count
    call_count += 1
    print(f"\n_render_bubble_text called (call #{call_count})")
    print(f"  Lines to render: {lines}")
    print(f"  Position: ({x}, {y})")
    print(f"  Bubble size: {bubble_width}x{bubble_height}")
    
    # Call original
    return original_render(self, draw, lines, font, x, y, bubble_width, bubble_height, padding, line_height)

Step14PanelComposition._render_bubble_text = logged_render

# Now test
compositor = Step14PanelComposition()
test_img = Image.new('RGB', (800, 600), 'white')
draw = ImageDraw.Draw(test_img)

compositor._load_fonts()

print("Testing thought bubble with 'Finally found it!'...")
print("="*60)

bounds = compositor._draw_speech_bubble(
    draw,
    "Finally found it!",
    "Sakura",
    100, 100,
    600,
    "thought"
)

print(f"\nTotal calls to _render_bubble_text: {call_count}")
print(f"Expected: 1 call")

if call_count > 1:
    print("ERROR: Text is being rendered multiple times!")
else:
    print("OK: Text rendered once as expected")
    
test_img.save("debug_thought_bubble.png")
print("\nSaved test image as debug_thought_bubble.png")