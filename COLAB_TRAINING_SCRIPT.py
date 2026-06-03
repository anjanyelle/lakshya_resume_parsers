# ============================================================================
# COMPLETE TRAINING SCRIPT - WITH CLEANED DATA
# Upload this to Google Colab and run it
# ============================================================================

import os
from google.colab import files, drive
import zipfile
import shutil

# Step 0: Check GPU FIRST
print("="*60)
print("STEP 0: CHECK GPU")
print("="*60)
   
import torch
if not torch.cuda.is_available():
    print("❌ NO GPU DETECTED!")
    print("\n⚠️  PLEASE ENABLE GPU:")
    print("   1. Click: Runtime > Change runtime type")
    print("   2. Hardware accelerator: T4 GPU")
    print("   3. Click: Save")
    print("   4. Run this cell again")
    raise SystemExit("GPU required for training")

print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB\n")

# Step 1: Install packages
print("="*60)
print("STEP 1: INSTALL PACKAGES")
print("="*60)
get_ipython().system('pip install -q transformers==4.44.0 datasets==2.19.0 accelerate==0.33.0 evaluate==0.4.1 seqeval scikit-learn')
print("✅ Packages installed\n")

# Step 2: Mount Google Drive
print("="*60)
print("STEP 2: MOUNT GOOGLE DRIVE")
print("="*60)

try:
    if os.path.exists('/content/drive'):
        get_ipython().system('fusermount -u /content/drive')
    drive.mount('/content/drive')
    print("✅ Google Drive mounted\n")
    use_drive = True
except Exception as e:
    print(f"⚠️  Drive mount failed")
    print("⚠️  Will save locally\n")
    use_drive = False

# Step 3: Upload ZIP
print("="*60)
print("STEP 3: UPLOAD ZIP")
print("="*60)
print("📤 Upload Lakshya-Colab-Training-CLEANED.zip...")
print("⚠️  IMPORTANT: Make sure you upload the CLEANED version!")
print("")

os.chdir('/content')

if os.path.exists('/content/Lakshya-Colab-Training-CLEANED'):
    shutil.rmtree('/content/Lakshya-Colab-Training-CLEANED')

uploaded = files.upload()

zip_name = list(uploaded.keys())[0]
print(f"✅ Uploaded: {zip_name}")

# Verify it's the correct file
if 'CLEANED' not in zip_name:
    print("\n" + "="*60)
    print("⚠️  WARNING: This doesn't look like the CLEANED ZIP!")
    print("⚠️  Expected: Lakshya-Colab-Training-CLEANED.zip")
    print(f"⚠️  Got: {zip_name}")
    print("="*60)
    response = input("\nContinue anyway? (yes/no): ")
    if response.lower() != 'yes':
        raise SystemExit("Please upload the correct CLEANED ZIP file")

print("")

# Step 4: Extract
print("="*60)
print("STEP 4: EXTRACT")
print("="*60)
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall('/content')
print("✅ Extracted\n")

# Step 5: Setup
print("="*60)
print("STEP 5: SETUP")
print("="*60)

# Find the extracted directory
if os.path.exists('/content/Lakshya-Colab-Training-CLEANED'):
    os.chdir('/content/Lakshya-Colab-Training-CLEANED/ai-service')
elif os.path.exists('/content/Lakshya-Colab-Training'):
    print("⚠️  WARNING: Found old directory name, not CLEANED version!")
    os.chdir('/content/Lakshya-Colab-Training/ai-service')
else:
    print("❌ ERROR: Cannot find extracted directory!")
    raise SystemExit("Extraction failed")

print(f"📍 Directory: {os.getcwd()}")

# Verify cleaned data files exist
train_file = "training/data/simple_dataset_train_cleaned.conll"
test_file = "training/data/simple_dataset_test_cleaned.conll"

if not os.path.exists(train_file):
    print(f"❌ ERROR: {train_file} not found!")
    print("⚠️  You may have uploaded the wrong ZIP file!")
    raise SystemExit("Cleaned data files not found")

if not os.path.exists(test_file):
    print(f"❌ ERROR: {test_file} not found!")
    print("⚠️  You may have uploaded the wrong ZIP file!")
    raise SystemExit("Cleaned data files not found")

print(f"✅ Training script found")
print(f"✅ Cleaned data files verified\n")

# Step 6: Configure save
print("="*60)
print("STEP 6: CONFIGURE SAVE")
print("="*60)

if use_drive:
    drive_model_dir = '/content/drive/MyDrive/Resume-NER-Models-CLEANED'
    get_ipython().system(f'mkdir -p "{drive_model_dir}"')

    if os.path.exists('models'):
        shutil.rmtree('models')
    get_ipython().system(f'ln -s "{drive_model_dir}" models')
    print(f"✅ Saving to: MyDrive/Resume-NER-Models-CLEANED/\n")
else:
    print(f"✅ Saving to: local models/\n")

# Step 7: Train
print("="*60)
print("STEP 7: TRAINING WITH CLEANED DATA")
print("="*60)
print("🏋️  Training DeBERTa NER Model")
print("⏱️  ~2 hours (12 epochs)")
print("📊 37,243 train + 4,451 test (CLEANED)")
print("🎯 Target F1: 90-92%")
print("")
print("⚠️  IMPORTANT: Watch for these numbers when training starts:")
print("   ✅ Loaded 37243 sentences (train)")
print("   ✅ Loaded 4451 sentences (test)")
print("")
print("   ❌ If you see 41884 or 4870 → WRONG DATA!")
print("")
print("="*60 + "\n")

get_ipython().system('python training/train_colab_standalone.py')

# Step 8: Finalize
print("\n" + "="*60)
print("STEP 8: FINALIZE")
print("="*60)

model_path = None

if use_drive:
    drive_model = f'{drive_model_dir}/resume-ner-deberta'
    if os.path.exists(drive_model):
        model_path = drive_model
        print("✅ Model in Google Drive!")
else:
    local_model = '/content/Lakshya-Colab-Training-CLEANED/ai-service/models/resume-ner-deberta'
    if os.path.exists(local_model):
        model_path = local_model
        print("✅ Model trained!")

if model_path:
    print("\n📦 Creating ZIP...")
    zip_dir = os.path.dirname(model_path)
    os.chdir(zip_dir)
    get_ipython().system('zip -r -q resume-ner-deberta.zip resume-ner-deberta')

    zip_size = os.path.getsize('resume-ner-deberta.zip') / 1024 / 1024

    print("\n" + "="*60)
    print("🎉 SUCCESS!")
    print("="*60)
    print(f"✅ Model: {zip_size:.1f} MB")

    if use_drive:
        print(f"\n📥 Download from:")
        print(f"   https://drive.google.com")
        print(f"   MyDrive/Resume-NER-Models-CLEANED/resume-ner-deberta.zip")
    else:
        print(f"\n📥 Downloading...")
        try:
            files.download('resume-ner-deberta.zip')
            print("✅ Download started!")
        except:
            print("⚠️  Download failed, copy to Drive manually")

    print("\n🎯 Expected F1: 90-92%")
    print("="*60)
else:
    print("❌ Model not found")
