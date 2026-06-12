import os

file_path = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\ai-service\parsers\rule_parser.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """                # For compound skills with dots, also match without dots
                if '.' in skill_lower:
                    skill_without_dots = skill_lower.replace('.', '')
                    escaped_without_dots = re.escape(skill_without_dots)
                    pattern += r'|\\b' + escaped_without_dots + r'\\b'"""

replacement = """                # For compound skills with dots, also match without dots
                if '.' in skill_lower:
                    skill_without_dots = skill_lower.replace('.', '')
                    escaped_without_dots = re.escape(skill_without_dots)
                    pattern += r'|\\b' + escaped_without_dots + r'\\b'
                
                # For compound skills with spaces, also match without spaces (e.g. 'Spring Boot' -> 'SpringBoot')
                if ' ' in skill_lower:
                    skill_without_spaces = skill_lower.replace(' ', '')
                    escaped_without_spaces = re.escape(skill_without_spaces)
                    pattern += r'|\\b' + escaped_without_spaces + r'\\b'"""

# We do a replacement handling both CRLF and LF
if target in content:
    content = content.replace(target, replacement)
    print("Replaced LF version")
elif target.replace("\n", "\r\n") in content:
    content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"))
    print("Replaced CRLF version")
else:
    print("Target not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
