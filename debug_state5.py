import re

text = "New York, Ny"

# Test exact matching
pattern = r",\s*[A-Z]{1,2}(?:\s|$)"
match = re.search(pattern, text)

print(f"Text: '{text}'")
print(f"Pattern: {pattern}")
print(f"Match: {match}")

if match:
    print(f"Full match: '{match.group()}'")
    print(f"Group 1: '{match.group(1)}'")
    print(f"Group 2: '{match.group(2) if match.lastindex >= 2 else 'None'}'")

# Test character by character
for i, char in enumerate(text):
    print(f"{i}: '{char}' (ord: {ord(char)})")

# Test with space after
text2 = "New York, Ny "
match2 = re.search(pattern, text2)
print(f"\nWith space: '{text2}'")
print(f"Match with space: {match2}")
