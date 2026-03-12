import re

text = "New York, Ny"
words = [w.strip().strip('.,') for w in text.split() if w.strip().strip('.,')]

# Test state pattern
state_pattern_old = r",\s*[A-Z]{2}\b"
state_pattern_new = r",\s*[A-Z]{1,2}\b"

print(f"Text: {text}")
print(f"Words: {words}")
print(f"Word count: {len(words)}")
print(f"Old state pattern match: {re.search(state_pattern_old, text)}")
print(f"New state pattern match: {re.search(state_pattern_new, text)}")
