#!/usr/bin/env python3
"""Test DeBERTa parser availability check."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from parsers.deberta_ner_parser import DeBERTaNerParser

print("🔍 Testing DeBERTa Parser Availability")
print("=" * 70)

parser = DeBERTaNerParser()

print(f"\nModel loaded: {parser.is_loaded}")
print(f"Model object: {parser.model}")
print(f"Tokenizer object: {parser.tokenizer}")
print(f"Structured parser: {parser.structured_parser}")
print(f"is_available(): {parser.is_available()}")

print("\n✅ Test complete")
