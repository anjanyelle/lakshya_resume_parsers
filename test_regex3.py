import re

# Test step by step
test = 'New York, Ny'
print(f'Testing: "{test}"')

# Test if word boundary is the issue
LOCATION_RE1 = re.compile(r"([A-Za-z\s\.]{2,40}),\s*([A-Za-z]{2})\b")
match1 = LOCATION_RE1.search(test)
print(f'Without \\b: {match1}')

# Test with exact case
LOCATION_RE2 = re.compile(r"([A-Za-z\s\.]+),\s*([A-Za-z]{2})")
match2 = LOCATION_RE2.search(test)
print(f'Without boundaries: {match2}')

# Test the actual pattern being used
LOCATION_RE = re.compile(r"\b([A-Za-z\s\.]{2,40}),\s*([A-Za-z]{2})\b")
match3 = LOCATION_RE.search(test)
print(f'Current pattern: {match3}')
