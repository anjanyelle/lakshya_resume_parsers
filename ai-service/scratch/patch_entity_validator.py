import os

file_path = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\ai-service\parsers\entity_validator.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "institution = education.get('institution', '').strip()": "institution = (education.get('institution') or '').strip()",
    "degree = education.get('degree', '').strip()": "degree = (education.get('degree') or '').strip()",
    "field = education.get('field_of_study', '').strip()": "field = (education.get('field_of_study') or '').strip()",
    "grade = education.get('grade', '').strip()": "grade = (education.get('grade') or '').strip()",
}

for target, replacement in replacements.items():
    if target in content:
        content = content.replace(target, replacement)
        print(f"Replaced LF: {target}")
    elif target.replace("\n", "\r\n") in content:
        content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"))
        print(f"Replaced CRLF: {target}")
    else:
        print(f"Target not found: {target}")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
