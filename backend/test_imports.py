#!/usr/bin/env python3

print("🔍 TESTING ALL REQUIRED PACKAGE IMPORTS...")
print("=" * 50)

# Test ML/NLP packages
try:
    import transformers
    print("✅ transformers:", transformers.__version__)
except ImportError as e:
    print("❌ transformers:", str(e))

try:
    import torch
    print("✅ torch:", torch.__version__)
except ImportError as e:
    print("❌ torch:", str(e))

try:
    import spacy
    print("✅ spacy:", spacy.__version__)
    
    # Test spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
        print("✅ en_core_web_sm: Loaded successfully")
    except Exception as e:
        print("❌ en_core_web_sm:", str(e))
        
except ImportError as e:
    print("❌ spacy:", str(e))

# Test document processing
try:
    import pdfplumber
    print("✅ pdfplumber:", pdfplumber.__version__)
except ImportError as e:
    print("❌ pdfplumber:", str(e))

try:
    import docx
    print("✅ python-docx: Available")
except ImportError as e:
    print("❌ python-docx:", str(e))

# Test data processing
try:
    import pandas
    print("✅ pandas:", pandas.__version__)
except ImportError as e:
    print("❌ pandas:", str(e))

try:
    import sklearn
    print("✅ scikit-learn:", sklearn.__version__)
except ImportError as e:
    print("❌ scikit-learn:", str(e))

try:
    import rapidfuzz
    print("✅ rapidfuzz:", rapidfuzz.__version__)
except ImportError as e:
    print("❌ rapidfuzz:", str(e))

# Test utilities
try:
    import dateparser
    print("✅ dateparser: Available")
except ImportError as e:
    print("❌ dateparser:", str(e))

try:
    import langdetect
    print("✅ langdetect: Available")
except ImportError as e:
    print("❌ langdetect:", str(e))

try:
    import numpy
    print("✅ numpy:", numpy.__version__)
except ImportError as e:
    print("❌ numpy:", str(e))

try:
    import PIL
    print("✅ pillow:", PIL.__version__)
except ImportError as e:
    print("❌ pillow:", str(e))

try:
    import requests
    print("✅ requests:", requests.__version__)
except ImportError as e:
    print("❌ requests:", str(e))

try:
    import tqdm
    print("✅ tqdm:", tqdm.__version__)
except ImportError as e:
    print("❌ tqdm:", str(e))

# Test web framework
try:
    import fastapi
    print("✅ fastapi:", fastapi.__version__)
except ImportError as e:
    print("❌ fastapi:", str(e))

try:
    import uvicorn
    print("✅ uvicorn: Available")
except ImportError as e:
    print("❌ uvicorn:", str(e))

# Test database
try:
    import sqlalchemy
    print("✅ sqlalchemy:", sqlalchemy.__version__)
except ImportError as e:
    print("❌ sqlalchemy:", str(e))

try:
    import psycopg2
    print("✅ psycopg2: Available")
except ImportError as e:
    print("❌ psycopg2:", str(e))

print("=" * 50)
print("🎯 PACKAGE IMPORT TEST COMPLETE!")
