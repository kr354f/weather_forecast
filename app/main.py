"""Main FastAPI application."""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings, validate_settings
from app.routers import weather
from app.models import ErrorResponse
from app.services.weather_service import weather_service


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Weather Forecast Microservice...")
    
    settings = get_settings()
    logger.info(f"Application: {settings.app_name} v{settings.app_version}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    
    # Validate configuration
    if not validate_settings():
        logger.warning("OpenWeatherMap API key not configured. Some features may not work.")
    else:
        logger.info("Configuration validated successfully")
    
    # Initialize services
    async with weather_service:
        logger.info("Weather service initialized")
        
        yield
        
        # Shutdown
        logger.info("Shutting down Weather Forecast Microservice...")
        await weather_service.close()


# Create FastAPI application
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    A comprehensive weather forecast microservice that provides current weather conditions 
    and multi-day forecasts for any location worldwide.
    
    ## Features
    
    * **Current Weather**: Get real-time weather conditions by city name or coordinates
    * **Weather Forecast**: Get up to 5-day weather forecasts
    * **Multiple Location Formats**: Support for city names and geographic coordinates
    * **Health Monitoring**: Built-in health checks and service monitoring
    * **Fast & Reliable**: Async API with robust error handling
    
    ## Authentication
    
    This service requires an OpenWeatherMap API key. Set the `OPENWEATHERMAP_API_KEY` 
    environment variable with your API key.
    
    ## Rate Limits
    
    Rate limits depend on your OpenWeatherMap API plan. The service handles rate limit 
    errors gracefully.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify actual hosts
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    logger.error(f"HTTP {exc.status_code} error at {request.url}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            timestamp=datetime.now(timezone.utc),
            status_code=exc.status_code
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error at {request.url}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            timestamp=datetime.now(timezone.utc),
            status_code=500
        ).dict()
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# Include routers
app.include_router(weather.router)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Root endpoint with service information."""
    settings = get_settings()
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Alternative health check at root level
@app.get("/health", tags=["monitoring"])
async def simple_health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )