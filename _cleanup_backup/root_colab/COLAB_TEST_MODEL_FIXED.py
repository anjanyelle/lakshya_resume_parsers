# ============================================================================
# GOOGLE COLAB - NER MODEL TESTING SCRIPT (FIXED)
# Test your trained model and decide if it's production-ready
# ============================================================================

import os
import sys

# ============================================================================
# STEP 1: MOUNT GOOGLE DRIVE
# ============================================================================
print("="*70)
print("STEP 1: MOUNT GOOGLE DRIVE")
print("="*70)

from google.colab import drive

try:
    if os.path.exists('/content/drive'):
        get_ipython().system('fusermount -u /content/drive')
    drive.mount('/content/drive')
    print("✅ Google Drive mounted\n")
except Exception as e:
    print(f"❌ Drive mount failed: {e}\n")
    raise

# ============================================================================
# STEP 2: INSTALL DEPENDENCIES (FIXED VERSION)
# ============================================================================
print("="*70)
print("STEP 2: INSTALL DEPENDENCIES")
print("="*70)

# Uninstall existing transformers to avoid conflicts
get_ipython().system('pip uninstall -y transformers')

# Install compatible versions
get_ipython().system('pip install -q torch')
get_ipython().system('pip install -q transformers==4.35.0')

print("✅ Dependencies installed")
print("⚠️  IMPORTANT: Restart runtime now!")
print("   Go to: Runtime > Restart runtime")
print("   Then run the cell below (STEP 3 onwards)\n")

# ============================================================================
# AFTER RUNTIME RESTART, RUN FROM HERE
# ============================================================================
