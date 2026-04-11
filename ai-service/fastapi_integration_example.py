#!/usr/bin/env python3
"""
FastAPI Integration Example for Resume Parsing Pipeline
Shows how to integrate the pipeline into a FastAPI application
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import logging
from resume_parser_pipeline import parse_resume

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Resume Parser API", version="1.0.0")

# Request/Response models
class ResumeParseRequest(BaseModel):
    resume_text: str
    model_path: str = "./models/resume-ner-deberta"

class ExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str
    location: str

class EducationEntry(BaseModel):
    degree: str
    institution: str
    start_date: str
    end_date: str

class ResumeParseResponse(BaseModel):
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    success: bool
    message: str = ""


@app.post("/api/parse-resume", response_model=ResumeParseResponse)
async def parse_resume_endpoint(request: ResumeParseRequest):
    """
    Parse resume text and extract structured information
    
    Args:
        request: Resume parse request with text and optional model path
        
    Returns:
        Structured resume data with experience and education
    """
    try:
        logger.info(f"Parsing resume (length: {len(request.resume_text)} chars)")
        
        # Validate input
        if not request.resume_text or len(request.resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume text is too short or empty"
            )
        
        # Parse resume
        result = parse_resume(
            resume_text=request.resume_text,
            model_path=request.model_path
        )
        
        # Convert to response model
        experience = [ExperienceEntry(**exp) for exp in result['experience']]
        education = [EducationEntry(**edu) for edu in result['education']]
        
        logger.info(f"Parsing complete: {len(experience)} experience, {len(education)} education")
        
        return ResumeParseResponse(
            experience=experience,
            education=education,
            success=True,
            message=f"Successfully extracted {len(experience)} experience entries and {len(education)} education entries"
        )
        
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing resume: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "resume-parser"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "parse": "/api/parse-resume",
            "health": "/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
