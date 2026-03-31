#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

# Test the exact logic
text = """YESHWANTH 
 https:www.linkedin.cominyeshwanth-s91 1(937)-234-7891  yeshwanths.yrs@gmail.com
Design and develop robust, scalable, and high-performance distributed systems."""

lines = text.splitlines()[:5]
print(f"Total lines: {len(lines)}")
print(f"Lines: {lines}")
print()

candidates = []

# First, check for all-uppercase names in the first 3 lines
for idx, line in enumerate(lines[:3]):
    print(f"\nProcessing line {idx}: {repr(line)}")
    line = line.strip()
    print(f"  Stripped: {repr(line)}")
    words = line.split()
    print(f"  Words: {words}")
    print(f"  Word count: {len(words)}")
    
    # Single word on first line is likely a name
    if idx == 0:
        print(f"  Checking single-word name on line 0:")
        print(f"    len(words) == 1: {len(words) == 1}")
        print(f"    len(line) >= 2: {len(line) >= 2}")
        print(f"    len(line) <= 30: {len(line) <= 30}")
        print(f"    line.isalpha(): {line.isalpha()}")
        print(f"    line.isupper(): {line.isupper()}")
        
        if len(words) == 1 and len(line) >= 2 and len(line) <= 30 and line.isalpha() and line.isupper():
            proper_name = line.capitalize()
            candidates.append(proper_name)
            print(f"  ✅ FOUND single-word uppercase name: {line} -> {proper_name}")
            continue
        else:
            print(f"  ❌ Did not match single-word criteria")
    
    # Multi-word uppercase names
    if (2 <= len(words) <= 4 and 
        line.replace(' ', '').replace('-', '').replace("'", '').isalpha() and
        line.isupper() and
        all(len(word) >= 2 for word in words) and
        len(line) <= 50):
        proper_name = ' '.join(word.capitalize() for word in words)
        candidates.append(proper_name)
        print(f"  ✅ FOUND multi-word uppercase name: {line} -> {proper_name}")

print(f"\n\nFinal candidates: {candidates}")
