# ============================================================================
# COMPLETE GOOGLE COLAB TRAINING SCRIPT
# COPY THIS ENTIRE FILE AND PASTE INTO A SINGLE COLAB CELL
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

# Install packages (use Colab's default torch and numpy)
get_ipython().system('pip install -q transformers==4.44.0 datasets==2.19.0 accelerate==0.33.0 evaluate==0.4.1 seqeval')

print("\n✅ Dependencies installed")
print("   (Ignore dependency warnings - they don't affect training)")
print("\n⚠️  IMPORTANT: Restart runtime now to avoid numpy conflicts")
print("   Click: Runtime > Restart runtime")
print("   Then run the cell below to continue training")
print("="*60)

# Step 6: START TRAINING
print("\n" + "="*60)
print("STEP 6: START TRAINING")
print("="*60)
print("🏋️  Training DeBERTa model...")
print("⏱️  Expected time: ~60-70 minutes on T4 GPU")
print("📊 Dataset: 15,433 train + 1,930 test sentences")
print("🎯 Target F1 Score: ~96%")
print("")
print("="*60)
print("TRAINING OUTPUT:")
print("="*60)

get_ipython().system('python training/train_colab_standalone.py')

# Step 7: Verify training completed
print("\n" + "="*60)
print("STEP 7: VERIFY TRAINING RESULTS")
print("="*60)

if os.path.exists('models/resume-ner-deberta'):
    print("✅ Model training completed!")
    
    # Show model files
    print("\n📂 Model files:")
    result = subprocess.run(['ls', '-lh', 'models/resume-ner-deberta/'], capture_output=True, text=True)
    print(result.stdout)
    
    # Get model size
    import os
    total_size = 0
    for dirpath, dirnames, filenames in os.walk('models/resume-ner-deberta'):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    print(f"💾 Total model size: {total_size / 1024 / 1024:.1f} MB")
    
    # Load label mappings
    import json
    label_file = 'models/resume-ner-deberta/label_mappings.json'
    if os.path.exists(label_file):
        with open(label_file, 'r') as f:
            mappings = json.load(f)
        print(f"\n🏷️  Labels ({len(mappings['labels'])} total):")
        print(f"   {', '.join(mappings['labels'][:15])}...")
else:
    print("❌ Model directory not found!")
    print("   Training may have failed. Check the output above.")
    raise SystemExit("Training failed")

# Step 8: Download model
print("\n" + "="*60)
print("STEP 8: DOWNLOAD MODEL")
print("="*60)
print("📦 Creating ZIP file...")

os.chdir('models')
get_ipython().system('zip -r -q resume-ner-deberta.zip resume-ner-deberta')

zip_path = 'resume-ner-deberta.zip'
if os.path.exists(zip_path):
    size_mb = os.path.getsize(zip_path) / 1024 / 1024
    print(f"✅ ZIP created: {size_mb:.1f} MB")
    
    print("\n📥 Downloading model...")
    files.download(zip_path)
    print("✅ Download started! Check your browser downloads.")
else:
    print("❌ Failed to create ZIP file")

# Final summary
print("\n" + "="*60)
print("🎉 TRAINING COMPLETE!")
print("="*60)
print("✅ Model trained successfully")
print("✅ Model downloaded to your computer")
print("")
print("📋 Next Steps:")
print("   1. Extract resume-ner-deberta.zip")
print("   2. Copy to your project: ai-service/models/resume-ner-deberta/")
print("   3. Restart your AI service")
print("   4. Test with real resumes!")
print("")
print("🎯 Expected Performance:")
print("   • Precision: ~97%")
print("   • Recall: ~96%")
print("   • F1 Score: ~96%")
print("="*60)
