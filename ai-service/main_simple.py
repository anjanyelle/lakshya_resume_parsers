from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import logging
import time
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug: Check if API keys are loaded
logger.info("=" * 80)
logger.info("ENVIRONMENT VARIABLES CHECK:")
logger.info(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
logger.info(f"ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
logger.info(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
logger.info("=" * 80)

# Create FastAPI app
app = FastAPI(
    title="Resume Parser API (Simplified)",
    description="Simplified resume parsing API for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ParseRequest(BaseModel):
    text: str
    options: Optional[Dict[str, Any]] = {}

class ParseResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# Simple mock parser for testing
class MockParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock parsing function that returns basic extracted info."""
        start_time = time.time()
        
        # Simple text analysis
        lines = text.strip().split('\n')
        name = lines[0].strip() if lines else ""
        
        # Look for email patterns
        import re
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        email = email_match.group() if email_match else ""
        
        # Look for phone patterns
        phone_match = re.search(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
        phone = phone_match.group() if phone_match else ""
        
        processing_time = time.time() - start_time
        
        result = {
            'name': name,
            'email': email,
            'phone': phone,
            'raw_text_length': len(text),
            'lines_count': len(lines),
            'processing_time_ms': processing_time * 1000,
            'parser_type': 'mock_simple',
            'confidence': {
                'overall': 0.85,
                'fields': {
                    'name': 0.9 if name else 0.0,
                    'email': 0.9 if email else 0.0,
                    'phone': 0.8 if phone else 0.0
                }
            }
        }
        
        self.logger.info(f"Mock parsing completed in {processing_time:.2f}s")
        return result

# Initialize mock parser
parser = MockParser()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""
    return HealthResponse(
        status="healthy",
        message="Resume Parser API (Simplified) is running",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="All systems operational (simplified mode)",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/parse", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """Parse resume text."""
    try:
        start_time = time.time()
        
        # Validate input
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Text too short or empty. Please provide meaningful resume text."
            )
        
        # Parse the resume
        result = parser.parse(request.text, request.options)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Successfully parsed resume in {processing_time:.2f}s")
        
        return ParseResponse(
            success=True,
            data=result,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return ParseResponse(
            success=False,
            error=f"Parsing failed: {str(e)}",
            processing_time=time.time() - start_time
        )

@app.get("/stats")
async def get_stats():
    """Get parser statistics."""
    return {
        "parser_type": "mock_simple",
        "status": "running",
        "supported_formats": ["text"],
        "features": [
            "basic_text_extraction",
            "email_detection", 
            "phone_detection",
            "confidence_scoring"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
