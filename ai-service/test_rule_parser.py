#!/usr/bin/env python3
"""
Test rule-based parser directly to see if it's working.
"""

import re

def extract_email(text):
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_phone(text):
    """Extract phone numbers from text."""
    # Indian phone patterns
    patterns = [
        r'\+91[-\s]?(\d{5})[-\s]?(\d{5})',  # +91 87904 33333
        r'(\d{3})[-\s]?(\d{3})[-\s]?(\d{4})',  # 879-043-3333
        r'(\d{10})',  # 8790433333
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            if isinstance(matches[0], tuple):
                return ''.join(matches[0])
            return matches[0]
    return None

def extract_github(text):
    """Extract GitHub profile from text."""
    github_pattern = r'github\.com/[\w\-]+'
    matches = re.findall(github_pattern, text, re.IGNORECASE)
    return matches[0] if matches else None

def extract_skills(text):
    """Extract technical skills from text."""
    skill_keywords = {
        'react', 'reactjs', 'react.js', 'vue', 'vuejs', 'angular', 'angularjs',
        'javascript', 'typescript', 'node', 'nodejs', 'node.js', 'express',
        'python', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'database',
        'git', 'github', 'gitlab', 'bitbucket', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'cloud', 'devops', 'ci/cd', 'jenkins',
        'rest', 'restful', 'api', 'graphql', 'microservices',
        'webpack', 'vite', 'babel', 'eslint', 'prettier', 'jest',
        'linux', 'ubuntu', 'windows', 'mac', 'unix', 'shell', 'bash'
    }
    
    found_skills = []
    words = re.findall(r'\b\w+\b', text.lower())
    
    for word in words:
        if word in skill_keywords:
            found_skills.append(word.title())
    
    return list(set(found_skills))

# Test text
test_text = """Anjan Yelle
Senior Frontend Developer
Hyderabad, India
+91-8790439333
anjanyelss@gmail.com
github.com/anjanyelles
React.js, TypeScript, Node.js"""

print("🔍 Testing Rule-Based Parser")
print("=" * 50)
print(f"Input text:\n{test_text}\n")

print("Extracted entities:")
email = extract_email(test_text)
print(f"Email: {email}")

phone = extract_phone(test_text)
print(f"Phone: {phone}")

github = extract_github(test_text)
print(f"GitHub: {github}")

skills = extract_skills(test_text)
print(f"Skills: {skills}")

# Calculate simple confidence
score = 0
total = 4
if email: score += 1
if phone: score += 1
if github: score += 1
if skills: score += 1

confidence = score / total
print(f"\nSimple confidence: {confidence:.2f} ({confidence*100:.0f}%)")
