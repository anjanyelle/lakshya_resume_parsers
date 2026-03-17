import re

# Test the patterns
client_pattern = re.compile(r'^Client:\s*.+?$')
role_pattern_header = re.compile(r'^Role:\s*.+?$')

test_lines = [
    'Client: Morgan Stanley',
    'New York, NY             Role: SR. BIG DATA ENGINEER',
    'June 2023 - Current                Responsibilities:'
]

print("Testing patterns:")
for line in test_lines:
    print(f"\nLine: {repr(line)}")
    if client_pattern.match(line):
        print("  Matches client_pattern")
    if role_pattern_header.match(line):
        print("  Matches role_pattern_header")
    if 'Role:' in line and re.search(r'[A-Z]{2}', line):
        print("  Matches combined location/role pattern")
