import re

# Test various state patterns
text = "New York, Ny"
patterns = [
    (r",\s*[A-Z]{2}\b", "Original - requires 2 uppercase"),
    (r",\s*[A-Z]{1,2}\b", "Fixed - 1-2 uppercase"),  
    (r",\s*[A-Za-z]{2}\b", "Case insensitive - 2 letters"),
    (r",\s*[A-Za-z]{1,2}\b", "Case insensitive - 1-2 letters"),
]

for name, pattern in patterns:
    match = re.search(pattern, text)
    print(f"{name}: {match}")

# Also test common state abbreviations
states = ["NY", "CA", "TX", "FL", "AZ", "MA", "NJ", "CT", "IL", "PA", "GA", "NC", "IN", "KY"]
for state in states:
    print(f"State '{state}' matches 1-2 uppercase: {re.search(r',\s*[A-Z]{1,2}\b', state)}")
    print(f"State '{state}' matches case-insensitive: {re.search(r',\s*[A-Za-z]{1,2}\b', state)}")
