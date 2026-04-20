#!/bin/bash
# Installation script for missing resume parser dependencies

echo "=================================="
echo "Installing Resume Parser Dependencies"
echo "=================================="

# Navigate to ai-service directory
cd ai-service

echo ""
echo "Installing PDF extraction libraries..."
pip install pdfplumber pymupdf pytesseract

echo ""
echo "Installing DOCX extraction library..."
pip install python-docx

echo ""
echo "Installing spaCy and model..."
pip install spacy
python -m spacy download en_core_web_sm

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Installed libraries:"
echo "  ✓ pdfplumber (PDF extraction - primary)"
echo "  ✓ pymupdf (PDF extraction - fallback)"
echo "  ✓ pytesseract (OCR - for scanned PDFs)"
echo "  ✓ python-docx (DOCX extraction)"
echo "  ✓ spacy + en_core_web_sm (NLP validation)"
echo ""
echo "You can now run the resume analysis:"
echo "  python3 test_resume_folder_analysis.py resumes/"
