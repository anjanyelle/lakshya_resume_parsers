#!/bin/bash

# Create a clean zip for Google Colab (under 2GB)
# This includes only what's needed for training

echo "🗜️  Creating Colab-ready zip file..."
echo "================================================"

# Create temporary directory
TEMP_DIR="Lakshya-Colab-Training"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/ai-service"

echo "📦 Copying essential files..."

# Copy ai-service structure (without venv and models)
cp -r ai-service/training "$TEMP_DIR/ai-service/"
cp -r ai-service/config "$TEMP_DIR/ai-service/"
cp -r ai-service/parsers "$TEMP_DIR/ai-service/"
cp -r ai-service/matching "$TEMP_DIR/ai-service/"
cp ai-service/*.py "$TEMP_DIR/ai-service/" 2>/dev/null || true
cp ai-service/requirements.txt "$TEMP_DIR/ai-service/" 2>/dev/null || true

# Copy model_loader.py from training folder to ai-service root
if [ -f "ai-service/training/model_loader.py" ]; then
    cp ai-service/training/model_loader.py "$TEMP_DIR/ai-service/"
    echo "  ✅ Copied model_loader.py to ai-service root"
fi

# Remove __pycache__ directories
find "$TEMP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Show what we're including
echo ""
echo "✅ Files included:"
du -sh "$TEMP_DIR"/*

# Create zip file
ZIP_NAME="Lakshya-Colab-Training.zip"
echo ""
echo "🗜️  Creating zip file: $ZIP_NAME"

# Remove old zip if exists
rm -f "$ZIP_NAME"

# Create new zip
zip -r "$ZIP_NAME" "$TEMP_DIR" -q

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Show final size
echo ""
echo "================================================"
echo "✅ Zip file created successfully!"
echo ""
ls -lh "$ZIP_NAME"
echo ""
echo "📊 Size: $(du -sh "$ZIP_NAME" | cut -f1)"
echo ""
echo "🚀 Ready to upload to Google Colab!"
echo "================================================"
