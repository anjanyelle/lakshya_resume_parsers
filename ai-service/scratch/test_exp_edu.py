import requests
import json
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

test_text = """
John Smith
john.smith@email.com | +91 9876543210 | Bangalore, India

WORK EXPERIENCE
Senior Software Engineer
TCS (Tata Consultancy Services)
Jan 2021 - Present
- Developed microservices using Python and FastAPI
- Led a team of 5 developers on critical banking project

Software Engineer
Infosys Limited
June 2018 - December 2020
- Built REST APIs using Node.js and Express
- Worked on React frontend development

EDUCATION
B.Tech in Computer Science
VTU (Visvesvaraya Technological University)
2014 - 2018
GPA: 8.5/10

SKILLS
Python, JavaScript, React, Node.js, FastAPI, PostgreSQL, Docker, Git
"""

issues = []

try:
    resp = requests.post("http://127.0.0.1:8000/parse-text", json={
        "text": test_text,
        "candidate_id": "test-001"
    }, timeout=120)

    data = resp.json()
    print("HTTP STATUS:", resp.status_code)
    print("PARSE STATUS:", data.get("status"))
    print()

    print("=" * 55)
    print("CONTACT INFO")
    print("=" * 55)
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    print("  NAME :", name)
    print("  EMAIL:", email)
    print("  PHONE:", phone)
    if not name: issues.append("MISSING: name not extracted")
    if not email: issues.append("MISSING: email not extracted")
    if not phone: issues.append("MISSING: phone not extracted")

    print()
    print("=" * 55)
    we_list = data.get("work_experience", [])
    print(f"WORK EXPERIENCE  ({len(we_list)} found, expected 2)")
    print("=" * 55)
    for i, w in enumerate(we_list):
        title = w.get("job_title") or w.get("title") or "???"
        company = w.get("company_name") or w.get("company") or "???"
        start = w.get("start_date") or "???"
        end = w.get("end_date") or "Present"
        desc = w.get("description") or ""
        print(f"  [{i+1}] Title:   {title}")
        print(f"       Company: {company}")
        print(f"       Dates:   {start} -> {end}")
        if desc:
            print(f"       Desc:    {desc[:60]}...")
        print()
        if title == "???": issues.append(f"MISSING: work_experience[{i}] has no title")
        if company == "???": issues.append(f"MISSING: work_experience[{i}] has no company")

    if len(we_list) == 0:
        issues.append("CRITICAL: No work experience extracted at all!")
    elif len(we_list) < 2:
        issues.append(f"WARNING: Only {len(we_list)} work experience found (expected 2)")

    # Check TCS full name
    if we_list and "tata" not in str(we_list[0].get("company_name","")).lower() and \
       "tcs" not in str(we_list[0].get("company_name","")).lower():
        issues.append("MINOR: TCS full name not preserved in company field")

    print("=" * 55)
    edu_list = data.get("education", [])
    print(f"EDUCATION  ({len(edu_list)} found, expected 1)")
    print("=" * 55)
    for i, e in enumerate(edu_list):
        degree = e.get("degree") or e.get("degree_name") or "???"
        institution = e.get("institution") or e.get("institution_name") or "???"
        field = e.get("field_of_study") or "???"
        start = e.get("start_year") or e.get("start_date") or "???"
        end = e.get("end_year") or e.get("end_date") or "???"
        gpa = e.get("gpa") or "N/A"
        print(f"  [{i+1}] Degree:      {degree}")
        print(f"       Field:       {field}")
        print(f"       Institution: {institution}")
        print(f"       Years:       {start} -> {end}")
        print(f"       GPA:         {gpa}")
        print()
        if degree == "???": issues.append(f"MISSING: education[{i}] has no degree")
        if institution == "???": issues.append(f"MISSING: education[{i}] has no institution")

    if len(edu_list) == 0:
        issues.append("CRITICAL: No education extracted at all!")

    print("=" * 55)
    skills = data.get("skills", [])
    print(f"SKILLS  ({len(skills)} found, expected 8)")
    print("=" * 55)
    print("  ", skills)
    if len(skills) == 0:
        issues.append("CRITICAL: No skills extracted!")
    elif len(skills) < 5:
        issues.append(f"WARNING: Only {len(skills)} skills found")

    print()
    print("=" * 55)
    print("CONFIDENCE:", json.dumps(data.get("confidence", {}), indent=2))
    print()

    # Final verdict
    print("=" * 55)
    print("VERDICT")
    print("=" * 55)
    if not issues:
        print("  ALL OK - Experience and Education parsing working correctly!")
    else:
        print(f"  {len(issues)} ISSUE(S) FOUND:")
        for issue in issues:
            print(f"    - {issue}")

except Exception as ex:
    print("ERROR:", ex)
