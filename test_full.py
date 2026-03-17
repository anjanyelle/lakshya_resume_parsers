import sys
sys.path.append('.')
from app.services.parser.work_experience_parser import WorkExperienceParser

parser = WorkExperienceParser()

# Test the full pipeline
chunk = '''New York, Ny · Goldman Sachs(New York, NY)
2019-01-01 → 2022-01-01'''

print('Input chunk:')
print(chunk)
print()

# Test location parsing
location = parser._parse_location(chunk)
print(f'Location parsing result: {location}')

# Test company/title splitting  
lines = chunk.splitlines()
company, title = parser._split_company_title(lines[0])
print(f'Company/title split: company="{company}", title="{title}"')

# Test location cleanup
final_location, final_company, final_title = parser._extract_and_clean_location(location, company, title, chunk)
print(f'After cleanup: company="{final_company}", title="{final_title}", location="{final_location}"')
