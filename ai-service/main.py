from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import logging
import time
import os
import torch
from typing import Optional, Dict, Any, List
from collections import defaultdict

from parsers.master_parser import MasterParser

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

# Global master parser instance (will be initialized at startup)
master_parser: Optional[MasterParser] = None

# Import matching engine
try:
    from matching.matching_engine import MatchingEngine
    MATCHING_ENGINE_AVAILABLE = True
except ImportError as e:
    MATCHING_ENGINE_AVAILABLE = False
    logger.warning(f"Matching engine not available: {e}")

# Initialize matching engine if available
matching_engine = None
if MATCHING_ENGINE_AVAILABLE:
    try:
        matching_engine = MatchingEngine()
        logger.info("Matching engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize matching engine: {e}")
        MATCHING_ENGINE_AVAILABLE = False

# Global metrics tracking
parse_metrics = {
    'total_parses': 0,
    'total_parse_time_ms': 0.0,
    'total_confidence_score': 0.0,
    'successful_parses': 0,
    'failed_parses': 0,
    'error_counts': defaultdict(int)
}

# Pydantic Models
class ParseRequest(BaseModel):
    file_path: str
    candidate_id: str
    llm_provider: Optional[str] = None

class ParseTextRequest(BaseModel):
    text: str
    candidate_id: str

class BatchParseRequest(BaseModel):
    files: List[Dict[str, str]]  # List of {file_path, candidate_id}

class BenchmarkRequest(BaseModel):
    text: str

class ParseResponse(BaseModel):
    candidate_id: str
    status: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    websites: List[str] = []
    skills: List[str] = []
    work_experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    job_titles: List[str] = []
    companies: List[str] = []
    locations: List[str] = []
    confidence: Dict[str, Any] = {}
    needs_review: bool = False
    quality_level: str = "medium"
    processing_metrics: Dict[str, Any] = {}
    summary: Optional[str] = None
    years_of_experience: Optional[float] = None
    dates: List[str] = []
    source_info: Optional[Dict[str, Any]] = None
    text_info: Optional[Dict[str, Any]] = None
    
    # Validators to ensure None values are converted to empty lists
    @field_validator('websites', 'skills', 'work_experience', 'education', 'job_titles', 'companies', 'locations', 'dates', mode='before')
    @classmethod
    def empty_list_for_none(cls, v):
        return [] if v is None else v
    
    @field_validator('confidence', 'processing_metrics', mode='before')
    @classmethod
    def empty_dict_for_none(cls, v):
        return {} if v is None else v

class BatchParseResponse(BaseModel):
    status: str
    total_files: int
    successful_parses: int
    failed_parses: int
    results: List[ParseResponse]
    errors: List[Dict[str, str]]

class MetricsResponse(BaseModel):
    total_parses_count: int
    average_parse_time_ms: float
    average_confidence_score: float
    successful_parse_rate: float
    model_name: str
    model_type: str
    supported_entities: List[str]
    device: str
    cache_size: str
    parser_health: Dict[str, Any]
    error_breakdown: Dict[str, int]

class BenchmarkResponse(BaseModel):
    status: str
    processing_time: float
    timing_breakdown: Dict[str, float]
    parsed_data: Dict[str, Any]
    confidence_scores: Dict[str, Any]

class MatchRequest(BaseModel):
    candidate_data: Dict[str, Any]
    job_data: Dict[str, Any]

class MatchResponse(BaseModel):
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    experience_gap_years: float
    recommendation: str
    reason: str

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
            "parse": "POST /parse - Parse resume file using MasterParser",
            "parse_text": "POST /parse-text - Parse raw text using MasterParser",
            "parse_batch": "POST /parse-batch - Parse multiple resume files",
            "benchmark": "POST /benchmark - Benchmark parsing performance",
            "metrics": "GET /metrics - Get parsing metrics and system health",
            "health": "GET /health - Service health check",
            "docs": "GET /docs - API documentation",
            "redoc": "GET /redoc - Alternative documentation"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if not master_parser:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            extractor_available=False,
            supported_formats=[]
        )
    
    # Get parser health from master parser
    parser_health = master_parser.get_parser_health()
    overall_healthy = parser_health['overall']['status'] == 'healthy'
    
    # Get supported formats
    try:
        supported_formats = master_parser.get_supported_file_types()
    except Exception:
        supported_formats = []
    
    return HealthResponse(
        status="healthy" if overall_healthy else "degraded",
        version="1.0.0",
        extractor_available=parser_health.get('text_extractor', {}).get('available', False),
        supported_formats=supported_formats
    )

@app.post("/parse", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """
    Parse resume file using MasterParser.
    
    Args:
        request: ParseRequest containing file_path and candidate_id
    
    Returns:
        ParseResponse with comprehensive parsed data from MasterParser
    """
    if not master_parser:
        raise HTTPException(
            status_code=503,
            detail="Parsing service is not available"
        )
    
    start_time = time.time()
    
    try:
        # Validate file exists
        if not os.path.exists(request.file_path):
            parse_metrics['failed_parses'] += 1
            parse_metrics['error_counts']['file_not_found'] += 1
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {request.file_path}"
            )
        
        # Validate file is supported
        supported_formats = master_parser.get_supported_file_types()
        file_ext = os.path.splitext(request.file_path)[1].lower()
        if file_ext not in supported_formats:
            parse_metrics['failed_parses'] += 1
            parse_metrics['error_counts']['unsupported_format'] += 1
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported formats: {supported_formats}"
            )
        
        logger.info(f"Parsing file: {request.file_path} for candidate: {request.candidate_id}")
        if request.llm_provider:
            logger.info(f"Using LLM provider: {request.llm_provider}")
        
        # Parse using MasterParser
        result = master_parser.parse_file(request.file_path, request.candidate_id, request.llm_provider)
        
        # Update metrics
        parse_time = (time.time() - start_time) * 1000
        parse_metrics['total_parses'] += 1
        parse_metrics['total_parse_time_ms'] += parse_time
        parse_metrics['successful_parses'] += 1
        
        if result['status'] == 'success':
            confidence_score = result.get('confidence', {}).get('overall', 0.0)
            parse_metrics['total_confidence_score'] += confidence_score
        
        logger.info(f"Successfully parsed resume for candidate: {request.candidate_id} in {parse_time:.1f}ms")
        
        return ParseResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        parse_metrics['failed_parses'] += 1
        parse_metrics['error_counts']['parsing_error'] += 1
        logger.error(f"Error parsing file {request.file_path}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse file: {str(e)}"
        )

@app.post("/parse-text", response_model=ParseResponse)
async def parse_text_direct(request: ParseTextRequest):
    """
    Parse raw text directly using MasterParser.
    
    Args:
        request: ParseTextRequest containing text and candidate_id
    
    Returns:
        ParseResponse with comprehensive parsed data from MasterParser
    """
    if not master_parser:
        raise HTTPException(
            status_code=503,
            detail="Parsing service is not available"
        )
    
    # Validate text length
    if len(request.text.strip()) < 50:
        parse_metrics['failed_parses'] += 1
        parse_metrics['error_counts']['text_too_short'] += 1
        raise HTTPException(
            status_code=400,
            detail="Resume text too short. Minimum 50 characters required."
        )
    
    start_time = time.time()
    
    try:
        logger.info(f"Parsing text for candidate: {request.candidate_id}")
        
        # Parse using MasterParser
        result = master_parser.parse_text(request.text, request.candidate_id)
        
        # Update metrics
        parse_time = (time.time() - start_time) * 1000
        parse_metrics['total_parses'] += 1
        parse_metrics['total_parse_time_ms'] += parse_time
        parse_metrics['successful_parses'] += 1
        
        if result['status'] == 'success':
            confidence_score = result.get('confidence', {}).get('overall', 0.0)
            parse_metrics['total_confidence_score'] += confidence_score
        
        logger.info(f"Successfully parsed text for candidate: {request.candidate_id} in {parse_time:.1f}ms")
        
        return ParseResponse(**result)
        
    except Exception as e:
        parse_metrics['failed_parses'] += 1
        parse_metrics['error_counts']['text_parsing_error'] += 1
        logger.error(f"Error parsing text for candidate {request.candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse text: {str(e)}"
        )

@app.post("/parse-batch", response_model=BatchParseResponse)
async def parse_batch(request: BatchParseRequest):
    """
    Parse multiple resume files in batch.
    
    Args:
        request: BatchParseRequest containing list of {file_path, candidate_id}
    
    Returns:
        BatchParseResponse with results for all files
    """
    if not master_parser:
        raise HTTPException(
            status_code=503,
            detail="Parsing service is not available"
        )
    
    # Validate batch size
    if len(request.files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Batch size too large. Maximum 10 files allowed per batch."
        )
    
    if len(request.files) == 0:
        raise HTTPException(
            status_code=400,
            detail="Batch cannot be empty. Please provide at least one file."
        )
    
    logger.info(f"Starting batch parse of {len(request.files)} files")
    
    results = []
    errors = []
    successful_parses = 0
    
    for file_info in request.files:
        try:
            file_path = file_info.get('file_path')
            candidate_id = file_info.get('candidate_id')
            
            if not file_path or not candidate_id:
                errors.append({
                    'file_path': file_path or 'unknown',
                    'candidate_id': candidate_id or 'unknown',
                    'error': 'Missing file_path or candidate_id'
                })
                continue
            
            # Parse individual file
            result = master_parser.parse_file(file_path, candidate_id)
            results.append(ParseResponse(**result))
            
            if result['status'] == 'success':
                successful_parses += 1
                # Update metrics
                parse_metrics['total_parses'] += 1
                parse_metrics['successful_parses'] += 1
                confidence_score = result.get('confidence', {}).get('overall', 0.0)
                parse_metrics['total_confidence_score'] += confidence_score
            else:
                errors.append({
                    'file_path': file_path,
                    'candidate_id': candidate_id,
                    'error': result.get('error', 'Unknown parsing error')
                })
                parse_metrics['failed_parses'] += 1
                parse_metrics['error_counts']['batch_parse_error'] += 1
                
        except Exception as e:
            errors.append({
                'file_path': file_info.get('file_path', 'unknown'),
                'candidate_id': file_info.get('candidate_id', 'unknown'),
                'error': str(e)
            })
            parse_metrics['failed_parses'] += 1
            parse_metrics['error_counts']['batch_file_error'] += 1
    
    failed_parses = len(request.files) - successful_parses
    
    logger.info(f"Batch parse completed: {successful_parses}/{len(request.files)} successful")
    
    return BatchParseResponse(
        status="completed",
        total_files=len(request.files),
        successful_parses=successful_parses,
        failed_parses=failed_parses,
        results=results,
        errors=errors
    )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get parsing metrics and system health information.
    
    Returns:
        MetricsResponse with comprehensive metrics and health data
    """
    try:
        # Calculate averages
        total_parses = parse_metrics['total_parses']
        avg_parse_time = parse_metrics['total_parse_time_ms'] / total_parses if total_parses > 0 else 0.0
        avg_confidence = parse_metrics['total_confidence_score'] / total_parses if total_parses > 0 else 0.0
        success_rate = parse_metrics['successful_parses'] / total_parses if total_parses > 0 else 0.0
        
        # Get model and device info from AI parser
        if master_parser and hasattr(master_parser, 'ai_parser') and master_parser.ai_parser:
            model_info = master_parser.ai_parser.get_model_info()
            model_name = model_info.get('model_name', 'Unknown')
            model_type = model_info.get('model_type', 'Unknown')
            supported_entities = model_info.get('supported_entities', [])
            device = "GPU" if torch.cuda.is_available() else "CPU"
        else:
            model_name = "Unknown"
            model_type = "Unknown"
            supported_entities = []
            device = "CPU"
        
        # Get parser health
        parser_health = master_parser.get_parser_health() if master_parser else {}
        
        # Get pipeline metrics from last parse
        pipeline_metrics = master_parser.get_pipeline_metrics() if master_parser else {}
        
        return MetricsResponse(
            total_parses_count=total_parses,
            average_parse_time_ms=round(avg_parse_time, 2),
            average_confidence_score=round(avg_confidence, 3),
            successful_parse_rate=round(success_rate, 3),
            model_name=model_name,
            model_type=model_type,
            supported_entities=supported_entities,
            device=device,
            cache_size="Unknown",  # Could be enhanced to check model cache
            parser_health=parser_health,
            error_breakdown=dict(parse_metrics['error_counts'])
        )
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )

@app.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_parsing(request: BenchmarkRequest):
    """
    Benchmark the full parsing pipeline with timing metrics.
    
    Args:
        request: BenchmarkRequest containing text to parse
    
    Returns:
        BenchmarkResponse with timing breakdown and parsed data
    """
    if not master_parser:
        raise HTTPException(
            status_code=503,
            detail="Parsing service is not available"
        )
    
    # Validate text length
    if len(request.text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Resume text too short. Minimum 50 characters required."
        )
    
    try:
        logger.info("Running parsing pipeline benchmark...")
        
        # Parse using MasterParser
        result = master_parser.parse_text(request.text, "benchmark_candidate")
        
        # Get detailed timing metrics
        pipeline_metrics = master_parser.get_pipeline_metrics()
        
        # Convert to expected format
        timing_breakdown = {}
        for step, time_ms in pipeline_metrics.items():
            if step != 'percentages' and step != 'performance_analysis':
                timing_breakdown[step.replace('_ms', '')] = time_ms / 1000  # Convert to seconds
        
        logger.info(f"Benchmark completed in {pipeline_metrics.get('total_ms', 0):.1f}ms")
        
        return BenchmarkResponse(
            status="success",
            processing_time=pipeline_metrics.get('total_ms', 0) / 1000,  # Convert to seconds
            timing_breakdown=timing_breakdown,
            parsed_data=result,
            confidence_scores=result.get('confidence', {})
        )
        
    except Exception as e:
        logger.error(f"Error during benchmark: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Benchmark failed: {str(e)}"
        )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            details=f"Status code: {exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with consistent error response format."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details=str(exc)
        ).dict()
    )

@app.post("/match", response_model=MatchResponse)
async def match_candidate_to_job(request: MatchRequest):
    """
    Match a candidate to a job using the semantic matching engine.
    
    Args:
        request: MatchRequest containing candidate_data and job_data
        
    Returns:
        MatchResponse with detailed scoring and recommendations
    """
    if not MATCHING_ENGINE_AVAILABLE or not matching_engine:
        raise HTTPException(
            status_code=503,
            detail="Matching engine not available"
        )
    
    try:
        logger.info(f"Matching candidate to job")
        
        # Extract candidate and job data
        candidate_data = request.candidate_data
        job_data = request.job_data
        
        # Validate required fields
        if not candidate_data or not job_data:
            raise HTTPException(
                status_code=400,
                detail="Both candidate_data and job_data are required"
            )
        
        # Perform matching using the matching engine
        match_result = matching_engine.calculate_match_score(candidate_data, job_data)
        
        logger.info(f"Matching completed: {match_result['recommendation']} ({match_result['overall_score']})")
        
        return MatchResponse(**match_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in matching: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Matching failed: {str(e)}"
        )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event - initialize MasterParser."""
    global master_parser
    
    logger.info("Resume Parser AI Service starting up...")
    logger.info(f"FastAPI version: {app.version}")
    
    try:
        # Load MasterParser (which initializes all sub-parsers)
        logger.info("Loading MasterParser...")
        master_parser = MasterParser()
        logger.info("✅ MasterParser loaded successfully")
        
        logger.info("🎉 All models loaded — service ready!")
        
        # Log supported file formats
        supported_formats = master_parser.get_supported_file_types()
        logger.info(f"Supported file formats: {supported_formats}")
        
        # Log parser health
        health = master_parser.get_parser_health()
        logger.info(f"Parser health: {health['overall']['status']} ({health['overall']['available_parsers']}/{health['overall']['total_parsers']} parsers available)")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MasterParser: {e}")
        # Continue with available models
        logger.warning("Service starting with degraded functionality")

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
