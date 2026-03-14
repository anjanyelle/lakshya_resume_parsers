from backend.app.services.parser.work_experience_parser import WorkExperienceParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_multi_line_header():
    text = "\n".join([
        "Work Experience",
        "Senior Software Engineer",
        "Acme Corporation",
        "San Francisco, CA",
        "Jan 2020 - Present",
        "- Developed microservices",
        "- Improved system performance"
    ])
    parser = WorkExperienceParser()
    print("\n--- Testing Multi-line Header ---")
    jobs = parser.parse_experience_section(text)
    print(f"Jobs found: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"Job {i}: Company: {job.company}, Title: {job.title}, Location: {job.location}, Dates: {job.start_date} to {job.end_date}")

def test_role_recovery():
    text = "\n".join([
        "Work History",
        "Tata Consultancy Services",
        "2018 - 2020",
        "- Worked as a Full Stack Developer",
        "- Managed database migrations"
    ])
    parser = WorkExperienceParser()
    print("\n--- Testing Role Recovery (Full Stack Developer) ---")
    jobs = parser.parse_experience_section(text)
    print(f"Jobs found: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"Job {i}: Company: {job.company}, Title: {job.title}, Confidence: {job.confidence}")

def test_last_job_protection():
    text = "\n".join([
        "Experience",
        "Lead Developer | Innovate Ltd | 2015-2018",
        "- Led a team of 10",
        "Education",
        "Bachelor of Science in Computer Science",
        "Stanford University"
    ])
    parser = WorkExperienceParser()
    print("\n--- Testing Last Job Protection (Education Boundary) ---")
    jobs = parser.parse_experience_section(text)
    print(f"Jobs found: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"Job {i}: Company: {job.company}, Title: {job.title}")
        print(f"Description:\n{job.description}")

def test_dash_patterns():
    text = "\n".join([
        "Work History",
        "Senior Analyst – Global Bank",
        "2010 - 2014",
        "Developed financial models",
        "Tech Startups – Principal Engineer",
        "2008 - 2010",
        "Architected cloud solutions"
    ])
    parser = WorkExperienceParser()
    print("\n--- Testing Dash Patterns ---")
    jobs = parser.parse_experience_section(text)
    print(f"Jobs found: {len(jobs)}")
    for i, job in enumerate(jobs):
        print(f"Job {i}: Company: {job.company}, Title: {job.title}")

if __name__ == "__main__":
    test_multi_line_header()
    test_role_recovery()
    test_last_job_protection()
    test_dash_patterns()
