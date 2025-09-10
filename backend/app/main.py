"""
FastAPI main application module.

This is the entry point for the Mistral AI Chat Backend application.
It sets up the FastAPI app with all necessary middleware, routers, and configurations.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api import analytics, chat, documents
from app.config import get_settings
from app.utils.exceptions import setup_exception_handlers
from app.utils.logger import setup_logging

# Get application settings
settings = get_settings()

# Setup structured logging
setup_logging(settings.log_level, settings.log_format)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    This includes initializing services, setting up database connections,
    and cleaning up resources.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control back to FastAPI during application runtime
    """
    # Startup events
    logger.info("Starting Mistral AI Chat Backend", version=settings.version)
    
    try:
        # Initialize services here
        logger.info("All services initialized successfully")
        yield
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    finally:
        # Shutdown events
        logger.info("Shutting down Mistral AI Chat Backend")


# Create FastAPI application instance
app = FastAPI(
    title="Mistral AI Chat Backend",
    description="""
    A high-performance backend service that integrates with Mistral AI for 
    intelligent chat functionality and document Q&A capabilities.
    
    ## Features
    
    * **Chat API**: Real-time chat with Mistral AI models
    * **Document Processing**: PDF upload and vector search  
    * **Analytics**: Performance metrics and usage tracking
    * **Authentication**: JWT-based user authentication
    * **Rate Limiting**: API protection and fair usage
    
    ## Authentication
    
    This API uses JWT bearer tokens for authentication. Include your token 
    in the Authorization header: `Bearer <your-token>`
    """,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routers
app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    documents.router,
    prefix="/api/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"],
    responses={404: {"description": "Not found"}},
)


@app.get("/", tags=["Health"])
async def root() -> JSONResponse:
    """
    Root endpoint providing basic API information.
    
    Returns:
        JSONResponse: Basic API information and status
    """
    return JSONResponse(
        content={
            "message": "Mistral AI Chat Backend",
            "version": settings.version,
            "status": "healthy",
            "docs": "/docs",
            "redoc": "/redoc",
        }
    )


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        JSONResponse: Application health status
    """
    try:
        # Add any health checks here (database connectivity, external APIs, etc.)
        return JSONResponse(
            content={
                "status": "healthy",
                "version": settings.version,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
