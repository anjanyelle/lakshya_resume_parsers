import asyncio
import os
import sys

from app.db.session import SessionLocal
from app.crud.candidate_crud import candidate
from app.services.parser.section_parser import SectionParser
from app.services.parser.work_experience_parser import WorkExperienceParser

async def test_parse():
    db = SessionLocal()
    try:
        cand_id = "999cc342-85b9-4051-83cf-6e30d9a2a7b9"
        cand = candidate.get(db, id=cand_id)
        if not cand:
            print(f"Candidate {cand_id} not found!")
            return
        
        text = cand.raw_text
        print(f"Loaded resume text length: {len(text)}")
        
        parser = SectionParser(use_spacy=True)
        sections = parser.parse(text)
        
        print(f"Detected Headers: {parser.get_detected_headers()}")
        
        exp_keys = ["experience", "work_experience", "professional_experience"]
        exp_text = ""
        for key in exp_keys:
            if key in sections:
                content = sections[key].content
                if content and len(content) > len(exp_text):
                    exp_text = content
        
        print(f"\\n--- Experience Section Text ---\\n{exp_text[:500]}...\\n")
        
        we_parser = WorkExperienceParser()
        jobs = we_parser.parse_experience_section(exp_text)
        print(f"\\n--- Parsed {len(jobs)} jobs ---")
        for j in jobs:
            print(f"Company: {j.company}, Title: {j.title}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_parse())
