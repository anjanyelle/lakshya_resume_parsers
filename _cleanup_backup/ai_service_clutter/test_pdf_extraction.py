#!/usr/bin/env python3
"""
Test and compare different PDF extraction methods to identify quality issues.
"""

import sys
sys.path.insert(0, '.')
import glob

# Find a sample resume
resume_files = glob.glob('../resumes/*.pdf')
if not resume_files:
    print("ERROR: No resume files found")
    sys.exit(1)

test_file = resume_files[0]
print(f"Testing PDF extraction with: {test_file}")
print("=" * 80)

# Method 1: PyMuPDF (fitz)
print("\n### METHOD 1: PyMuPDF (fitz) ###\n")
try:
    import fitz
    doc = fitz.open(test_file)
    pymupdf_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        pymupdf_text += page.get_text() + "\n"
    doc.close()
    
    print(f"Total length: {len(pymupdf_text)} chars")
    print(f"Word count: {len(pymupdf_text.split())}")
    print(f"Line count: {len(pymupdf_text.splitlines())}")
    print(f"\nFirst 500 chars:\n{pymupdf_text[:500]}")
    print(f"\nFirst 10 lines:")
    for i, line in enumerate(pymupdf_text.splitlines()[:10], 1):
        print(f"{i:2d}: {line}")
except Exception as e:
    print(f"PyMuPDF failed: {e}")
    pymupdf_text = ""

# Method 2: pdfplumber
print("\n" + "=" * 80)
print("\n### METHOD 2: pdfplumber ###\n")
try:
    import pdfplumber
    pdfplumber_text = ""
    with pdfplumber.open(test_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                pdfplumber_text += page_text + "\n"
    
    print(f"Total length: {len(pdfplumber_text)} chars")
    print(f"Word count: {len(pdfplumber_text.split())}")
    print(f"Line count: {len(pdfplumber_text.splitlines())}")
    print(f"\nFirst 500 chars:\n{pdfplumber_text[:500]}")
    print(f"\nFirst 10 lines:")
    for i, line in enumerate(pdfplumber_text.splitlines()[:10], 1):
        print(f"{i:2d}: {line}")
except Exception as e:
    print(f"pdfplumber failed: {e}")
    pdfplumber_text = ""

# Method 3: PyMuPDF with layout preservation
print("\n" + "=" * 80)
print("\n### METHOD 3: PyMuPDF with layout preservation ###\n")
try:
    import fitz
    doc = fitz.open(test_file)
    layout_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Use "text" mode which preserves layout better
        layout_text += page.get_text("text") + "\n"
    doc.close()
    
    print(f"Total length: {len(layout_text)} chars")
    print(f"Word count: {len(layout_text.split())}")
    print(f"Line count: {len(layout_text.splitlines())}")
    print(f"\nFirst 500 chars:\n{layout_text[:500]}")
    print(f"\nFirst 10 lines:")
    for i, line in enumerate(layout_text.splitlines()[:10], 1):
        print(f"{i:2d}: {line}")
except Exception as e:
    print(f"PyMuPDF layout failed: {e}")
    layout_text = ""

# Method 4: PyMuPDF with blocks (structured extraction)
print("\n" + "=" * 80)
print("\n### METHOD 4: PyMuPDF with blocks (structured) ###\n")
try:
    import fitz
    doc = fitz.open(test_file)
    blocks_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")
        # Sort blocks by vertical position (y0) then horizontal (x0)
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        for block in blocks:
            # block[4] is the text content
            if len(block) >= 5:
                blocks_text += block[4] + "\n"
    doc.close()
    
    print(f"Total length: {len(blocks_text)} chars")
    print(f"Word count: {len(blocks_text.split())}")
    print(f"Line count: {len(blocks_text.splitlines())}")
    print(f"\nFirst 500 chars:\n{blocks_text[:500]}")
    print(f"\nFirst 10 lines:")
    for i, line in enumerate(blocks_text.splitlines()[:10], 1):
        print(f"{i:2d}: {line}")
except Exception as e:
    print(f"PyMuPDF blocks failed: {e}")
    blocks_text = ""

# Comparison
print("\n" + "=" * 80)
print("\n### COMPARISON ###\n")
print(f"PyMuPDF:         {len(pymupdf_text):6d} chars, {len(pymupdf_text.split()):5d} words")
print(f"pdfplumber:      {len(pdfplumber_text):6d} chars, {len(pdfplumber_text.split()):5d} words")
print(f"PyMuPDF layout:  {len(layout_text):6d} chars, {len(layout_text.split()):5d} words")
print(f"PyMuPDF blocks:  {len(blocks_text):6d} chars, {len(blocks_text.split()):5d} words")

# Determine best method
methods = {
    'pymupdf': len(pymupdf_text),
    'pdfplumber': len(pdfplumber_text),
    'layout': len(layout_text),
    'blocks': len(blocks_text)
}
best_method = max(methods, key=methods.get)
print(f"\n✅ Best method: {best_method} with {methods[best_method]} chars")
