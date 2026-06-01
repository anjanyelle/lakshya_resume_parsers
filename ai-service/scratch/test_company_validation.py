import sys
from pathlib import Path

# Add parsers directory to path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.entity_validator import get_validator

validator = get_validator()

test_companies = [
    "TCS",
    "Google",
    "Gatnix",
    "Lalataksha",
    "Zylker"
]

test_roles = [
    "Software Engineer",
    "Full Stack Developer",
    "Intern",
    "Founder",
    "CTO",
    "CEO",
    "Trainee",
    "Programmer"
]

print("=" * 60)
print("TESTING COMPANY VALIDATION")
print("=" * 60)
for company in test_companies:
    is_valid, corrected, conf, reason = validator.validate_company(company)
    status = "✅ VALID" if is_valid else "❌ INVALID"
    print(f"{company:<30} -> {status:<10} | Corrected: {corrected:<30} | Conf: {conf:.2f} | Reason: {reason}")

print("\n" + "=" * 60)
print("TESTING ROLE VALIDATION")
print("=" * 60)
for role in test_roles:
    is_valid, corrected, conf, reason = validator.validate_role(role)
    status = "✅ VALID" if is_valid else "❌ INVALID"
    print(f"{role:<30} -> {status:<10} | Corrected: {corrected:<30} | Conf: {conf:.2f} | Reason: {reason}")
