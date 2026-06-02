import sys
import os

path = 'app/api/v1/endpoints/upload.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

imports = """from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.education_parser import EducationParser
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Form
"""

if 'extract_text' not in content:
    content = content.replace('from fastapi.responses import HTMLResponse', 'from fastapi.responses import HTMLResponse\n' + imports)

endpoints = """

class SectionPreviewResponse(BaseModel):
    filename: str
    extraction_method: str
    raw_text_length: int
    raw_text: str
    total_sections: int
    sections: dict[str, dict[str, Any]]
    detected_sections: list[str]
    missing_sections: list[str]
    validation_metadata: dict[str, Any]

@router.post("/preview-sections", response_model=SectionPreviewResponse)
async def preview_sections_endpoint(file: UploadFile = File(...), force_ocr: bool = Form(False)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        temp_file.write(data)
        temp_path = Path(temp_file.name)
    
    try:
        extracted = extract_text(temp_path)
        text = extracted.text
        
        parser = SectionParser()
        parsed_sections = parser.parse(text)
        
        sections_dict = {}
        detected_sections = []
        for key, result in parsed_sections.items():
            if result.content:
                text_content = "\\n".join(result.content)
                sections_dict[key] = {
                    "text": text_content,
                    "char_count": len(text_content)
                }
                detected_sections.append(key)
                
        standard_sections = ['summary', 'experience', 'education', 'skills', 'certifications', 'projects', 'contact']
        missing_sections = [s for s in standard_sections if s not in detected_sections]
        
        return SectionPreviewResponse(
            filename=file.filename,
            extraction_method="auto",
            raw_text_length=len(text),
            raw_text=text,
            total_sections=len(sections_dict),
            sections=sections_dict,
            detected_sections=detected_sections,
            missing_sections=missing_sections,
            validation_metadata={"spacy_available": False, "warnings": []}
        )
    finally:
        import os
        os.unlink(temp_path)

class ParseSectionsRequest(BaseModel):
    experience_text: Optional[str] = None
    education_text: Optional[str] = None
    skills_text: Optional[str] = None
    summary_text: Optional[str] = None
    certifications_text: Optional[str] = None
    projects_text: Optional[str] = None
    contact_text: Optional[str] = None
    raw_text: Optional[str] = None

class ParseSectionsResponse(BaseModel):
    status: str
    work_experience: list[dict[str, Any]] = []
    education: list[dict[str, Any]] = []
    skills: list[str] = []
    summary: Optional[str] = None
    certifications: list[str] = []
    projects: list[str] = []
    processing_time_ms: float
    message: str

@router.post("/parse-sections", response_model=ParseSectionsResponse)
async def parse_sections_endpoint(request: ParseSectionsRequest):
    import time
    start_time = time.time()
    
    work_experience = []
    education = []
    
    if request.experience_text:
        parser = WorkExperienceParser()
        result = parser.parse_experience_section(request.experience_text)
        for job in result:
            work_experience.append({
                "job_title": job.title,
                "company_name": job.company,
                "start_date": job.start_date.isoformat() if job.start_date else None,
                "end_date": job.end_date.isoformat() if job.end_date else None,
                "is_current": job.is_current,
                "location": job.location,
                "description": job.description
            })
            
    if request.education_text:
        parser = EducationParser()
        result = parser.parse_education_section(request.education_text)
        for edu in result:
            education.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_date": edu.start_date.isoformat() if edu.start_date else None,
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
                "gpa": edu.gpa
            })
            
    processing_time_ms = (time.time() - start_time) * 1000
    return ParseSectionsResponse(
        status="success",
        work_experience=work_experience,
        education=education,
        skills=[],
        summary=request.summary_text if request.summary_text else None,
        certifications=[],
        projects=[],
        processing_time_ms=processing_time_ms,
        message="Parsed successfully"
    )
"""

if 'preview_sections_endpoint' not in content:
    content += endpoints

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated upload.py successfully.')
