from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import time
import os
from typing import Optional

from parsers.text_extractor import TextExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title='Resume Parser AI',
    description='AI-powered resume parsing and text extraction service',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3001',  # Node.js backend
        'http://localhost:3000',  # React frontend
        'http://localhost:5173',  # Vite dev server
        'https://lakshya-llm-resume-parser-ated.vercel.app'
    ],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['*']
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response

# Initialize TextExtractor
try:
    extractor = TextExtractor()
    logger.info("TextExtractor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize TextExtractor: {e}")
    extractor = None

# Pydantic Models
class ParseRequest(BaseModel):
    file_path: str
    candidate_id: str
    file_type: str

class ParseTextRequest(BaseModel):
    text: str
    candidate_id: str

class ParseResponse(BaseModel):
    candidate_id: str
    status: str
    extracted_text: str
    word_count: int
    quality_score: float
    parsing_method: str

class HealthResponse(BaseModel):
    status: str
    version: str
    extractor_available: bool
    supported_formats: list

class WelcomeResponse(BaseModel):
    message: str
    service: str
    version: str
    endpoints: dict

# Error Response Model
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[str] = None

# Routes
@app.get("/", response_model=WelcomeResponse)
async def root():
    """Root endpoint with welcome message and available endpoints."""
    return WelcomeResponse(
        message="Welcome to Resume Parser AI Service",
        service="Resume Parser AI",
        version="1.0.0",
        endpoints={
            "parse": "POST /parse - Extract text from resume file",
            "parse_text": "POST /parse-text - Parse raw text directly",
            "health": "GET /health - Service health check",
            "docs": "GET /docs - API documentation",
            "redoc": "GET /redoc - Alternative documentation"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    supported_formats = []
    extractor_available = False
    
    if extractor:
        try:
            supported_formats = extractor.get_supported_formats()
            extractor_available = True
        except Exception as e:
            logger.error(f"Error checking extractor: {e}")
    
    return HealthResponse(
        status="healthy" if extractor_available else "degraded",
        version="1.0.0",
        extractor_available=extractor_available,
        supported_formats=supported_formats
    )

@app.post("/parse", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """
    Extract text from a resume file.
    
    Args:
        request: ParseRequest containing file_path, candidate_id, and file_type
    
    Returns:
        ParseResponse with extracted text and metadata
    """
    if not extractor:
        raise HTTPException(
            status_code=503,
            detail="Text extraction service is not available"
        )
    
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {request.file_path}"
            )
        
        # Validate file type
        if not extractor.is_supported(request.file_path):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported formats: {extractor.get_supported_formats()}"
            )
        
        logger.info(f"Processing file: {request.file_path} for candidate: {request.candidate_id}")
        
        # Extract text
        result = extractor.extract(request.file_path)
        
        logger.info(f"Successfully extracted {result['word_count']} words from {request.file_path}")
        
        return ParseResponse(
            candidate_id=request.candidate_id,
            status="success",
            extracted_text=result['text'],
            word_count=result['word_count'],
            quality_score=result['quality_score'],
            parsing_method=result['method']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file {request.file_path}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

@app.post("/parse-text", response_model=ParseResponse)
async def parse_text_direct(request: ParseTextRequest):
    """
    Parse raw text directly without file extraction.
    
    Args:
        request: ParseTextRequest containing text and candidate_id
    
    Returns:
        ParseResponse with cleaned text and metadata
    """
    if not extractor:
        raise HTTPException(
            status_code=503,
            detail="Text extraction service is not available"
        )
    
    try:
        logger.info(f"Processing raw text for candidate: {request.candidate_id}")
        
        # Clean the text
        cleaned_text = extractor.clean_text(request.text)
        
        # Calculate metrics
        word_count = len(cleaned_text.split())
        quality_score = extractor._calculate_quality_score(cleaned_text, word_count)
        
        logger.info(f"Successfully processed {word_count} words for candidate: {request.candidate_id}")
        
        return ParseResponse(
            candidate_id=request.candidate_id,
            status="success",
            extracted_text=cleaned_text,
            word_count=word_count,
            quality_score=quality_score,
            parsing_method="direct"
        )
        
    except Exception as e:
        logger.error(f"Error processing text for candidate {request.candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process text: {str(e)}"
        )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error response format."""
    return ErrorResponse(
        error="HTTP_ERROR",
        message=exc.detail,
        details=f"Status code: {exc.status_code}"
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with consistent error response format."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return ErrorResponse(
        error="INTERNAL_ERROR",
        message="An unexpected error occurred",
        details=str(exc)
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Resume Parser AI Service starting up...")
    logger.info(f"FastAPI version: {app.version}")
    
    if extractor:
        logger.info("TextExtractor is available")
        logger.info(f"Supported formats: {extractor.get_supported_formats()}")
    else:
        logger.warning("TextExtractor is not available")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Resume Parser AI Service shutting down...")

# Run the app
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
