import re

# Simplified test of the core issue
text = "New York, Ny · Goldman Sachs(New York, NY)"

# Test location regex directly
LOCATION_RE = re.compile(r"\b([A-Za-z\s\.]{2,40}),\s*([A-Za-z]{2})\b")
match = LOCATION_RE.search(text)

if match:
    print(f"Location regex MATCH: '{match.group(1)}', '{match.group(2)}'")
else:
    print("Location regex NO MATCH")

# Test why _looks_like_company fails
def test_looks_like_company(text):
    if not text:
        return False
    cleaned = text.strip()
    if cleaned.startswith("##"):
        return False
    
    # State/Location pattern (e.g. "Louisville, KY") is NOT a company
    if re.search(r",\s*[A-Z]{2}\b", text):
        return False
    
    return True  # This is the issue!

print(f"\nTesting _looks_like_company('New York, Ny'): {test_looks_like_company('New York, Ny')}")

# Test _parse_location
def test_parse_location(text):
    if not text:
        return None
    # Avoid bullet points or lines that look like descriptions
    if text.lstrip().startswith(("-", "•", "*")):
        return None
        
    match = LOCATION_RE.search(text)
    if match:
        candidate = match.group(1).strip()
        # Double check: if it's "Swift, UI", discard it
        if re.search(r"\b(Swift|UI|IT|AI|ML|SQL|AWS|API|JDBC|JSON|NoSQL|REST|GraphQL|SOAP|CI/CD)\b", candidate):
            return None
        return candidate
    return None

print(f"Testing _parse_location('New York, Ny'): {test_parse_location('New York, Ny')}")
