#!/bin/bash
# Safe model replacement script

echo "======================================================================"
echo "🔄 REPLACING PRODUCTION MODEL WITH NEW TRAINED MODEL"
echo "======================================================================"
echo ""

# Set paths
OLD_MODEL="ai-service/models/resume-ner-deberta"
NEW_MODEL="ai-service/models-test/resume-ner-deberta"
BACKUP_MODEL="ai-service/models/resume-ner-deberta-backup-$(date +%Y%m%d-%H%M%S)"

# Check if new model exists
if [ ! -d "$NEW_MODEL" ]; then
    echo "❌ Error: New model not found at $NEW_MODEL"
    echo "Please ensure you've downloaded and extracted the model first."
    exit 1
fi

# Check if old model exists
if [ ! -d "$OLD_MODEL" ]; then
    echo "⚠️  Warning: No existing production model found at $OLD_MODEL"
    echo "Will create new production model location."
else
    # Backup old model
    echo "📦 Step 1: Backing up current production model..."
    mv "$OLD_MODEL" "$BACKUP_MODEL"
    if [ $? -eq 0 ]; then
        echo "✅ Backup created: $BACKUP_MODEL"
    else
        echo "❌ Failed to backup model"
        exit 1
    fi
fi

# Move new model to production
echo ""
echo "🚀 Step 2: Moving new model to production..."
mv "$NEW_MODEL" "$OLD_MODEL"
if [ $? -eq 0 ]; then
    echo "✅ New model is now in production: $OLD_MODEL"
else
    echo "❌ Failed to move new model"
    # Restore backup if move failed
    if [ -d "$BACKUP_MODEL" ]; then
        echo "🔄 Restoring backup..."
        mv "$BACKUP_MODEL" "$OLD_MODEL"
    fi
    exit 1
fi

# Verify new model
echo ""
echo "🔍 Step 3: Verifying new model..."
if [ -f "$OLD_MODEL/config.json" ] && [ -f "$OLD_MODEL/label_mappings.json" ]; then
    echo "✅ Model files verified"
else
    echo "⚠️  Warning: Some model files may be missing"
fi

echo ""
echo "======================================================================"
echo "✅ MODEL REPLACEMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "📊 Summary:"
echo "   Old model backed up to: $BACKUP_MODEL"
echo "   New model active at:    $OLD_MODEL"
echo ""
echo "📝 Next steps:"
echo "   1. Test your application with the new model"
echo "   2. If everything works well, you can delete the backup:"
echo "      rm -rf $BACKUP_MODEL"
echo "   3. If there are issues, restore the backup:"
echo "      mv $BACKUP_MODEL $OLD_MODEL"
echo ""
echo "======================================================================"
