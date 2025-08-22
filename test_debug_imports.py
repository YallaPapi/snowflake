"""Debug imports for graphic novel pipeline"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports...")

try:
    print("1. Importing Step 11...")
    from pipeline.steps.step_11_manuscript_to_script import Step11ManuscriptToScript
    print("   [OK] Step 11 imported successfully")
except Exception as e:
    print(f"   [ERROR] Step 11 import failed: {e}")
    traceback.print_exc()

try:
    print("2. Importing Step 12...")
    from pipeline.steps.step_12_comic_formatter import Step12ComicFormatter
    print("   [OK] Step 12 imported successfully")
except Exception as e:
    print(f"   [ERROR] Step 12 import failed: {e}")
    traceback.print_exc()

try:
    print("3. Importing Step 11 Validator...")
    from pipeline.validators.step_11_validator import Step11Validator
    print("   [OK] Step 11 Validator imported successfully")
except Exception as e:
    print(f"   [ERROR] Step 11 Validator import failed: {e}")
    traceback.print_exc()

try:
    print("4. Importing Step 12 Validator...")
    from pipeline.validators.step_12_validator import Step12Validator
    print("   [OK] Step 12 Validator imported successfully")
except Exception as e:
    print(f"   [ERROR] Step 12 Validator import failed: {e}")
    traceback.print_exc()

print("\nAll imports tested!")