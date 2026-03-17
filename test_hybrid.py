from app.services.parser.hybrid_work_experience_parser import HybridWorkExperienceParser

# Test with your actual work experience text
test_text = '''## PROFESSIONAL EXPERIENCE:
Client: Nike Location: Beaverton, OR
Role: Senior Full Stack Developer January 2023 - Current
Responsibilities:
- Designed and developed middle-tier business logic using Java and Spring Boot, implementing RES Tful AP Is to support a Saa S-based retail platform'''

parser = HybridWorkExperienceParser()
result = parser.parse_work_experience(test_text)

print(f'🎯 Hybrid Parser Results:')
print(f'  Method used: {getattr(parser, "method_used", "Unknown")}')
print(f'  Jobs found: {len(result)}')
print(f'  First job: {result[0].title if result else "None"}')
print(f'  Confidence: {getattr(parser, "last_confidence", "Unknown")}')
