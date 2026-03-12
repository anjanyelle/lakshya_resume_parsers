from app.services.parser.work_experience_parser import WorkExperienceParser

parser = WorkExperienceParser()

test_strings = [
    'New York, Ny',
    'Sunnyvale, Ca', 
    'Goldman Sachs',
    'Walmart Global e Commerce'
]

for text in test_strings:
    is_company = parser._looks_like_company(text)
    is_title = parser._looks_like_title(text)
    is_location = parser._parse_location(text) is not None
    
    print(f'"{text}"')
    print(f'  Company: {is_company}')
    print(f'  Title:   {is_title}')
    print(f'  Location:{is_location}')
    print()
