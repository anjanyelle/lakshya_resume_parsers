#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import glob

resume_files = glob.glob('../resumes/*.pdf')
test_file = resume_files[0]

from parsers.text_extractor import TextExtractor
extractor = TextExtractor()
result = extractor.extract(test_file)
text = result['text']

lines = text.splitlines()
print("First 5 lines (with repr to see exact content):")
for i, line in enumerate(lines[:5], 1):
    print(f"{i}: {repr(line)}")
    print(f"   Stripped: {repr(line.strip())}")
    print(f"   Words: {line.strip().split()}")
    print(f"   Is alpha only: {line.strip().replace(' ', '').replace('-', '').replace(chr(39), '').isalpha()}")
    print(f"   Is upper: {line.strip().isupper()}")
    print()
