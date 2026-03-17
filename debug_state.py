import re

text = "New York, Ny"
words = text.split()
print(f"Words: {words}")
print(f"Word count: {len(words)}")

# State/Location pattern (e.g. "Louisville, KY") is NOT a company
state_pattern = r",\s*[A-Z]{2}\b"
match = re.search(state_pattern, text)
print(f"State pattern match: {match}")

# Check if words count logic is working
if 2 <= len(words) <= 5:
    print("Word count condition: PASS")
else:
    print("Word count condition: FAIL")
