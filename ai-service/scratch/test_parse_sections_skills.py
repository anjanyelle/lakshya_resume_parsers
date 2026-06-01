import sys
import os
import asyncio

# Add ai-service to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import parse_sections, ParseSectionsRequest

async def test_skills_post_processing():
    print("Testing parse-sections skills post-processing...")
    print("=" * 60)
    
    # We will pass a job title containing a skill (like "SpringBoot Developer", "Node.js Developer")
    # without explicitly specifying those skills in skills_text.
    request = ParseSectionsRequest(
        experience_text="""
        Node.js Developer
        ABC Corp
        2022 - Present
        - Built microservices using SpringBoot and Python.
        """,
        skills_text="Docker",
        education_text="BS in Computer Science",
        contact_text="John Doe\njohn.doe@example.com"
    )
    
    # Call parse_sections
    response = await parse_sections(request)
    
    print(f"Status: {response.status}")
    print(f"Parsed Work Experience: {response.work_experience}")
    print(f"Original Skills Request: 'Docker'")
    print(f"Parsed & Post-Processed Skills: {response.skills}")
    
    # Assertions
    skills_lower = [s.lower() for s in response.skills]
    
    print(f"\nChecking extracted skills: {skills_lower}")
    
    # Check if Docker is in skills (from original request)
    assert "docker" in skills_lower, "Docker was not preserved in skills!"
    
    # Check if Node.js was extracted from title/description
    assert "node.js" in skills_lower, "Node.js was not extracted from job title/description!"
    
    # Check if SpringBoot was extracted from title/description
    assert "springboot" in skills_lower or "spring boot" in skills_lower, "SpringBoot was not extracted from description!"
    
    print("\n[SUCCESS] All assertions passed successfully!")
    print("[SUCCESS] Skills post-processing in parse-sections is working beautifully!")

if __name__ == "__main__":
    asyncio.run(test_skills_post_processing())
