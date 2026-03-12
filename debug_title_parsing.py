import re

# Test the actual title line from Vaishnavi's resume
title_line = "DevOps Engineer October 2022 - Current"

# Current regex pattern
current_pattern = r'([A-Za-z]+ \d{4})\s*[-–—]\s*(Present|[A-Za-z]+ \d{4})'
current_match = re.search(current_pattern, title_line)

print(f"Title Line: {title_line}")
print(f"Current Pattern: {current_pattern}")
print(f"Current Match: {current_match}")

if current_match:
    print(f"Groups: {current_match.groups()}")
    print(f"Full Match: {current_match.group(0)}")
else:
    print("NO MATCH - This is the problem!")
    
    # Try different patterns
    patterns = [
        r'([A-Za-z]+ \d{4})\s*[-–—]\s*(Present|Current|[A-Za-z]+ \d{4})',
        r'([A-Za-z]+ \d{4})\s*[-–—]\s*(Present|Current)',
        r'(\w+ \d{4})\s*[-–—]\s*(Present|Current|\w+ \d{4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title_line)
        print(f"\nPattern: {pattern}")
        print(f"Match: {match}")
        if match:
            print(f"Groups: {match.groups()}")
