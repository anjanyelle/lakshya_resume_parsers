import re

LOCATION_RE = re.compile(r'\b(?!(?:Swift|UI|IT|AI|ML|SQL|AWS|API|JDBC|JSON|NoSQL|REST|GraphQL|SOAP|CI/CD)\b)([A-Za-z \.]{2,40},\s*[A-Z]{2})\b')

test_strings = ['New York, Ny', 'Sunnyvale, Ca', 'Austin, TX']

for text in test_strings:
    match = LOCATION_RE.search(text)
    if match:
        print(f'"{text}" -> MATCH: {match.group(1)}')
    else:
        print(f'"{text}" -> NO MATCH')
