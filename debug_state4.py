import re

text = "New York, Ny"

# The issue is word boundaries. Let's test
patterns = [
    (r",\s*[A-Z]{1,2}\b", "With word boundary"),
    (r",\s*[A-Z]{1,2}(?!\w)", "With negative lookahead"),
    (r",\s*[A-Z]{1,2}(?:\s|$)", "With end of string or space"),
]

for name, pattern in patterns:
    match = re.search(pattern, text)
    print(f"{name}: '{pattern}' -> {match}")

# Test the actual match
for name, pattern in patterns:
    match = re.search(pattern, text)
    if match:
        print(f"  MATCHED: '{match.group()}'")
    else:
        print(f"  NO MATCH")
