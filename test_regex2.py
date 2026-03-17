import re

# Test the fixed regex
LOCATION_RE = re.compile(r"\b([A-Za-z\s\.]{2,40}),\s*([A-Z]{2})\b")

test_strings = ['New York, Ny', 'Sunnyvale, Ca', 'Austin, TX', 'Bloomfield, CT']

for text in test_strings:
    match = LOCATION_RE.search(text)
    if match:
        print(f'"{text}" -> MATCH: "{match.group(1)}", "{match.group(2)}"')
    else:
        print(f'"{text}" -> NO MATCH')
        
# Test character by character
print('\n--- Debugging New York, Ny ---')
test = 'New York, Ny'
for i, char in enumerate(test):
    print(f'{i}: "{char}" (ord: {ord(char)})')
