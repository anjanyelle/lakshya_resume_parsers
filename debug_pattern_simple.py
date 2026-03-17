import re

# Test the pattern step by step
text = '''Bank of America North Carolina
Sr. Full Stack Developer July 2021 - Present'''

print("Testing simple pattern...")
print("Text:", repr(text))

# Simple pattern for company + title + date
pattern = r'([A-Za-z\s&\-]+)\n([A-Za-z\s&\-\.]+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*(?:Present|Current|[A-Za-z]+(?:\s+\d{4})?)'

try:
    job_pattern = re.compile(pattern, re.IGNORECASE)
    matches = list(job_pattern.finditer(text))
    print(f"Found {len(matches)} matches")
    for match in matches:
        print(f"Company: '{match.group(1)}'")
        print(f"Title/Date: '{match.group(2)}'")
except Exception as e:
    print(f"Error: {e}")
    print(f"Pattern: {pattern}")

# Test even simpler pattern
print("\nTesting simpler pattern...")
simple_pattern = r'([A-Za-z\s&\-]+)\n([A-Za-z\s&\-\.]+\s+July\s+\d{4}\s*[-–—]\s*Present)'
try:
    simple_job_pattern = re.compile(simple_pattern, re.IGNORECASE)
    simple_matches = list(simple_job_pattern.finditer(text))
    print(f"Found {len(matches)} matches")
    for match in simple_matches:
        print(f"Company: '{match.group(1)}'")
        print(f"Title/Date: '{match.group(2)}'")
except Exception as e:
    print(f"Error: {e}")
    print(f"Simple pattern: {simple_pattern}")
