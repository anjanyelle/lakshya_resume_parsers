# ============================================================================
# CELL 1: SETUP & INSTALL (Run this first)
# ============================================================================

# Step 1: Verify GPU
import torch
print("="*60)
print("STEP 1: VERIFY GPU")
print("="*60)
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("❌ NO GPU DETECTED!")
    print("   Please enable GPU:")
    print("   1. Runtime > Change runtime type")
    print("   2. Hardware accelerator > T4 GPU")
    print("   3. Save")
    raise SystemExit("GPU required for training")

# Step 2: Upload ZIP file
print("\n" + "="*60)
print("STEP 2: UPLOAD ZIP FILE")
print("="*60)
from google.colab import files
import os

# Clean workspace
os.chdir('/content')
print("🧹 Cleaning workspace...")
import shutil
if os.path.exists('/content/Lakshya-Colab-Training'):
    shutil.rmtree('/content/Lakshya-Colab-Training')
for f in os.listdir('/content'):
    if f.endswith('.zip'):
        os.remove(f'/content/{f}')

# Upload
print("\n📤 Please upload Lakshya-Colab-Training.zip...")
uploaded = files.upload()

if not uploaded:
    raise SystemExit("❌ No file uploaded!")

zip_name = list(uploaded.keys())[0]
print(f"✅ Uploaded: {zip_name} ({len(uploaded[zip_name])/1024:.1f} KB)")

# Step 3: Extract
print("\n" + "="*60)
print("STEP 3: EXTRACT ZIP")
print("="*60)
print(f"📦 Extracting {zip_name}...")
import zipfile
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall('/content')
print("✅ Extracted successfully")

# Verify extraction
if not os.path.exists('/content/Lakshya-Colab-Training'):
    raise SystemExit("❌ Extraction failed! Directory not found.")

# Step 4: Navigate and verify
print("\n" + "="*60)
print("STEP 4: NAVIGATE TO AI-SERVICE")
print("="*60)
os.chdir('/content/Lakshya-Colab-Training/ai-service')
print(f"📍 Current directory: {os.getcwd()}")

# Verify structure
print("\n📂 Verifying package structure...")
if not os.path.exists('training/train_colab_standalone.py'):
    raise SystemExit("❌ Training script not found!")
if not os.path.exists('training/data/simple_dataset_train.conll'):
    raise SystemExit("❌ Training data not found!")
if not os.path.exists('training/data/simple_dataset_test.conll'):
    raise SystemExit("❌ Test data not found!")

print("✅ All files verified")
print("\n📊 Training data:")
import subprocess
result = subprocess.run(['ls', '-lh', 'training/data/'], capture_output=True, text=True)
print(result.stdout)

# Step 5: Install dependencies
print("\n" + "="*60)
print("STEP 5: INSTALL DEPENDENCIES")
print("="*60)
print("📦 Installing transformers, datasets, etc...")
print("   (This may take 2-3 minutes)")
print("")

# Install packages
get_ipython().system('pip install -q transformers==4.44.0 datasets==2.19.0 accelerate==0.33.0 evaluate==0.4.1 seqeval')

print("\n" + "="*60)
print("✅ SETUP COMPLETE!")
print("="*60)
print("\n⚠️  IMPORTANT: Restart runtime to avoid numpy conflicts")
print("   1. Click: Runtime > Restart runtime")
print("   2. After restart, run CELL 2 (training cell)")
print("="*60)
