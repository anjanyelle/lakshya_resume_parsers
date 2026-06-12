#!/usr/bin/env python3
"""
Download microsoft/deberta-v3-base for NER fine-tuning.
Saves to ./models/deberta-v3-base-pretrained/

Run from ai-service/:
    ./venv/bin/python download_and_prepare_model.py
"""

import os
import sys
from pathlib import Path

MODEL_NAME = 'microsoft/deberta-v3-base'
OUTPUT_DIR = Path(__file__).parent / 'models' / 'deberta-v3-base-pretrained'


def check_dependencies():
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: ./venv/bin/pip install transformers torch sentencepiece protobuf")
        return False


def download_model():
    print("=" * 60)
    print("  DeBERTa-v3-base Download & Prepare")
    print("=" * 60)
    print(f"  Model   : {MODEL_NAME}")
    print(f"  Save to : {OUTPUT_DIR}")
    print(f"  Size    : ~700 MB")
    print("=" * 60)
    print()

    if not check_dependencies():
        sys.exit(1)

    from transformers import AutoTokenizer, AutoModel

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📥 Step 1/2 — Downloading tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.save_pretrained(str(OUTPUT_DIR))
        print("✅ Tokenizer saved\n")
    except Exception as e:
        print(f"❌ Tokenizer download failed: {e}")
        sys.exit(1)

    print("📥 Step 2/2 — Downloading model weights (this takes 3–10 min)...")
    try:
        model = AutoModel.from_pretrained(MODEL_NAME)
        model.save_pretrained(str(OUTPUT_DIR))
        print("✅ Model weights saved\n")
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        sys.exit(1)

    # Verify saved files
    saved_files = sorted(OUTPUT_DIR.iterdir())
    total_mb = sum(f.stat().st_size for f in saved_files if f.is_file()) / 1024 / 1024
    print(f"📁 Saved {len(saved_files)} files — {total_mb:.1f} MB total:")
    for f in saved_files:
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name:<40} {size_mb:>7.1f} MB")

    print()
    print("=" * 60)
    print("✅  DeBERTa-v3-base is ready!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("  1. Auto-label your resumes:")
    print("     cd training")
    print("     ../venv/bin/python label_resumes.py")
    print()
    print("  2. Fine-tune DeBERTa on labeled data:")
    print("     ../venv/bin/python train.py")
    print()
    print("  3. Restart the AI service — State 1 (fine-tuned DeBERTa) will load:")
    print("     cd .. && ./venv/bin/uvicorn main:app --reload --port 8001")
    print("=" * 60)


if __name__ == '__main__':
    download_model()
