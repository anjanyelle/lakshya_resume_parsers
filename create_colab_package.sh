#!/bin/bash
# Script to create Colab training package

echo "🚀 Creating Colab Training Package..."
echo "======================================"

# Navigate to project root
cd "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser"

# Clean up old package if exists
rm -rf Lakshya-Colab-Training Lakshya-Colab-Training.zip

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p Lakshya-Colab-Training/ai-service/models

# Copy training files
echo "📋 Copying training files..."
cp -r ai-service/training Lakshya-Colab-Training/ai-service/

# Verify data files exist
if [ ! -f "Lakshya-Colab-Training/ai-service/training/data/simple_dataset_train.conll" ]; then
    echo "❌ ERROR: simple_dataset_train.conll not found!"
    exit 1
fi

if [ ! -f "Lakshya-Colab-Training/ai-service/training/data/simple_dataset_test.conll" ]; then
    echo "❌ ERROR: simple_dataset_test.conll not found!"
    exit 1
fi

# Create ZIP
echo "📦 Creating ZIP file..."
zip -r Lakshya-Colab-Training.zip Lakshya-Colab-Training/ -x "*.pyc" -x "__pycache__/*" -x ".DS_Store"

# Get file size
SIZE=$(du -h Lakshya-Colab-Training.zip | cut -f1)

echo ""
echo "✅ Package created successfully!"
echo "======================================"
echo "📦 File: Lakshya-Colab-Training.zip"
echo "📏 Size: $SIZE"
echo ""
echo "📂 Contents:"
ls -lh Lakshya-Colab-Training.zip
echo ""
echo "🔍 Verify structure:"
unzip -l Lakshya-Colab-Training.zip | head -20
echo ""
echo "✅ Ready to upload to Google Colab!"
echo ""
echo "Next steps:"
echo "1. Open: https://colab.research.google.com/"
echo "2. Upload: ai-service/training/Colab_Training_Simple.ipynb"
echo "3. Enable GPU: Runtime → Change runtime type → T4 GPU"
echo "4. Run the cell and upload Lakshya-Colab-Training.zip when prompted"
