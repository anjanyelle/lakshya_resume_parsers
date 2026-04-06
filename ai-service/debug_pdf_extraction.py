#!/usr/bin/env python3
"""Debug PDF text extraction to see what's being extracted."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.text_extractor import TextExtractor

# Test with one of the problematic PDFs
pdf_paths = [
    "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/e263d46b-69c8-4d0f-8b3d-b1492a3ac082_Untitled_document__4_.pdf",
    "/Users/anjanyelle/Desktop/untitled folder 3/Lakshya-LLM-Resume-Parser/backend/src/uploads/d605bd07-16a9-453f-b70c-f101535f824c_Untitled_document__2_.pdf"
]

extractor = TextExtractor()

for pdf_path in pdf_paths:
    if not Path(pdf_path).exists():
        print(f"⚠️  File not found: {pdf_path}")
        continue
    
    print("\n" + "=" * 70)
    print(f"📄 PDF: {Path(pdf_path).name}")
    print("=" * 70)
    
    result = extractor.extract_from_pdf(pdf_path)
    
    text = result.get('text', '')
    method = result.get('method', 'unknown')
    
    print(f"\n🔍 Extraction method: {method}")
    print(f"📏 Text length: {len(text)} characters")
    print(f"\n📝 EXTRACTED TEXT:")
    print("-" * 70)
    print(text)
    print("-" * 70)
    
    # Check for problematic patterns
    if "Role:" in text and "Location:" in text:
        print("\n❌ PROBLEM DETECTED: Text contains 'Role:' and 'Location:' labels")
        print("   This suggests the PDF has a table/form layout that's being extracted incorrectly")
        
        # Show the problematic section
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'Role:' in line or 'Location:' in line or 'Company:' in line:
                print(f"\n   Line {i}: {line}")
