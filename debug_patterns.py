import re

# Test the location patterns
test_strings = [
    "Bank of America North Carolina",
    "Starbucks California", 
    "Credit Karma San Francisco",
    "Amazon Hyderabad, India",
    "ADP Hyderabad, India"
]

location_patterns = [
    r'(.+?)\s+(North Carolina|California|San Francisco|Hyderabad|India)$',  # Known locations
    r'(Starbucks)\s+(California)$',  # Starbucks California
    r'(Credit Karma)\s+(San Francisco)$',  # Credit Karma San Francisco  
    r'(Amazon)\s+(Hyderabad,\s*India)$',  # Amazon Hyderabad, India
    r'(ADP)\s+(Hyderabad,\s*India)$',  # ADP Hyderabad, India
    r'([A-Za-z\s&\-]+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$',  # Company + Location (capitalized location)
]

for test_str in test_strings:
    print(f"Testing: '{test_str}'")
    for i, pattern in enumerate(location_patterns):
        match = re.match(pattern, test_str)
        if match:
            print(f"  Pattern {i+1} MATCHED: company='{match.group(1)}', location='{match.group(2) if len(match.groups()) > 1 else None}'")
            break
    else:
        print(f"  No patterns matched")
    print()
