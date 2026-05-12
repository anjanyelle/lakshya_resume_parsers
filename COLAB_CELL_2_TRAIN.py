# ============================================================================
# CELL 2: TRAINING (Run this after restarting runtime)
# ============================================================================

import os
os.chdir('/content/Lakshya-Colab-Training/ai-service')

# Verify we're in the right place
print("="*60)
print("STARTING TRAINING")
print("="*60)
print(f"📍 Current directory: {os.getcwd()}")

# Verify GPU
import torch
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
else:
    print("❌ No GPU detected!")
    raise SystemExit("GPU required")

# Start training directly (imports handled by training script)
print("\n" + "="*60)
print("🏋️  TRAINING DEBERTA MODEL")
print("="*60)
print("⏱️  Expected time: ~2 hours (12 epochs)")
print("📊 Dataset: 41,884 train + 4,870 test sentences")
print("🎯 Target F1 Score: 98.5-99%")
print("")
print("="*60)
print("TRAINING OUTPUT:")
print("="*60)

get_ipython().system('python training/train_colab_standalone.py')

# Verify training completed
print("\n" + "="*60)
print("VERIFY TRAINING RESULTS")
print("="*60)

if os.path.exists('models/resume-ner-deberta'):
    print("✅ Model training completed!")
    
    # Show model files
    print("\n📂 Model files:")
    import subprocess
    result = subprocess.run(['ls', '-lh', 'models/resume-ner-deberta/'], capture_output=True, text=True)
    print(result.stdout)
    
    # Get model size
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

# Save to Google Drive (more reliable than direct download)
print("\n" + "="*60)
print("SAVE TO GOOGLE DRIVE")
print("="*60)

from google.colab import drive
print("� Mounting Google Drive...")
drive.mount('/content/drive')

# Create directory in Drive
drive_path = '/content/drive/MyDrive/Resume-NER-Models'
get_ipython().system(f'mkdir -p "{drive_path}"')

# Copy model to Drive (no ZIP needed - faster!)
print("\n📤 Copying model to Google Drive...")
print("   (This is faster and more reliable than downloading)")
get_ipython().system(f'cp -r models/resume-ner-deberta "{drive_path}/"')

print("\n✅ Model saved to Google Drive!")
print(f"   Location: MyDrive/Resume-NER-Models/resume-ner-deberta/")

# Verify
print("\n📂 Files in Google Drive:")
get_ipython().system(f'ls -lh "{drive_path}/resume-ner-deberta/"')

# Also create a ZIP in Drive for easy download later
print("\n📦 Creating ZIP in Google Drive...")
os.chdir('/content/drive/MyDrive/Resume-NER-Models')
get_ipython().system('zip -r -q resume-ner-deberta.zip resume-ner-deberta')

zip_size = os.path.getsize('resume-ner-deberta.zip') / 1024 / 1024
print(f"✅ ZIP created in Drive: {zip_size:.1f} MB")
print(f"   Location: MyDrive/Resume-NER-Models/resume-ner-deberta.zip")

# Final summary
print("\n" + "="*60)
print("🎉 TRAINING COMPLETE!")
print("="*60)
print("✅ Model trained successfully")
print("✅ Model saved to Google Drive")
print("")
print("📋 How to Download:")
print("   1. Open Google Drive in your browser")
print("   2. Go to: MyDrive/Resume-NER-Models/")
print("   3. Right-click: resume-ner-deberta.zip")
print("   4. Click: Download")
print("   (Google Drive handles large files better)")
print("")
print("📋 Next Steps:")
print("   1. Download from Google Drive")
print("   2. Extract resume-ner-deberta.zip")
print("   3. Copy to your project: ai-service/models/resume-ner-deberta/")
print("   4. Restart your AI service")
print("   5. Test with real resumes!")
print("")
print("🎯 Expected Performance:")
print("   • Precision: ~98-99%")
print("   • Recall: ~98-99%")
print("   • F1 Score: ~98.5-99%")
print("="*60)
