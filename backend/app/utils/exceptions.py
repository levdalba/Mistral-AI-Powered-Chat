"""
Custom exceptions for the Mistral AI Chat Backend.

This module defines all custom exception classes used throughout
the application for better error handling and debugging.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger(__name__)


class ChatServiceError(Exception):
    """
    Exception raised by the chat service.
    
    This exception is raised when there are errors in chat processing,
    AI model communication, or conversation management.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize chat service error.
        
        Args:
            message: Human-readable error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DocumentServiceError(Exception):
    """
    Exception raised by the document service.
    
    This exception is raised when there are errors in document processing,
    embedding generation, or vector search operations.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize document service error.
        
        Args:
            message: Human-readable error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(Exception):
    """
    Exception raised for input validation errors.
    
    This exception is raised when user input fails validation
    or when data doesn't meet expected formats or constraints.
    """
    
    def __init__(self, message: str, field: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            message: Human-readable error message
            field: Optional field name that failed validation
        """
        super().__init__(message)
        self.message = message
        self.field = field


class RateLimitError(Exception):
    """
    Exception raised when rate limits are exceeded.
    
    This exception is raised when users exceed API rate limits
    or when external service rate limits are hit.
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Human-readable error message
            retry_after: Optional seconds to wait before retrying
        """
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after


class AuthenticationError(Exception):
    """
    Exception raised for authentication failures.
    
    This exception is raised when authentication tokens are invalid,
    expired, or missing.
    """
    
    def __init__(self, message: str = "Authentication required"):
        """
        Initialize authentication error.
        
        Args:
            message: Human-readable error message
        """
        super().__init__(message)
        self.message = message


class AuthorizationError(Exception):
    """
    Exception raised for authorization failures.
    
    This exception is raised when authenticated users don't have
    permission to access certain resources or perform actions.
    """
    
    def __init__(self, message: str = "Insufficient permissions"):
        """
        Initialize authorization error.
        
        Args:
            message: Human-readable error message
        """
        super().__init__(message)
        self.message = message


class ExternalServiceError(Exception):
    """
    Exception raised when external services fail.
    
    This exception is raised when calls to external APIs (like Mistral AI)
    fail due to network issues, service unavailability, or API errors.
    """
    
    def __init__(self, service: str, message: str, status_code: Optional[int] = None):
        """
        Initialize external service error.
        
        Args:
            service: Name of the external service
            message: Human-readable error message
            status_code: Optional HTTP status code from the service
        """
        super().__init__(message)
        self.service = service
        self.message = message
        self.status_code = status_code


async def chat_service_error_handler(request: Request, exc: ChatServiceError) -> JSONResponse:
    """
    Handle chat service errors.
    
    Args:
        request: FastAPI request object
        exc: Chat service exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(
        "Chat service error",
        error=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Chat Service Error",
            "message": exc.message,
            "details": exc.details,
            "type": "chat_service_error",
        },
    )


async def document_service_error_handler(request: Request, exc: DocumentServiceError) -> JSONResponse:
    """
    Handle document service errors.
    
    Args:
        request: FastAPI request object
        exc: Document service exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(
        "Document service error",
        error=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Document Service Error",
            "message": exc.message,
            "details": exc.details,
            "type": "document_service_error",
        },
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle validation errors.
    
    Args:
        request: FastAPI request object
        exc: Validation exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.warning(
        "Validation error",
        error=exc.message,
        field=exc.field,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "field": exc.field,
            "type": "validation_error",
        },
    )


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """
    Handle rate limit errors.
    
    Args:
        request: FastAPI request object
        exc: Rate limit exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.warning(
        "Rate limit exceeded",
        error=exc.message,
        retry_after=exc.retry_after,
        path=request.url.path,
    )
    
    headers = {}
    if exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    
    return JSONResponse(
        status_code=429,
        headers=headers,
        content={
            "error": "Rate Limit Exceeded",
            "message": exc.message,
            "retry_after": exc.retry_after,
            "type": "rate_limit_error",
        },
    )


async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """
    Handle authentication errors.
    
    Args:
        request: FastAPI request object
        exc: Authentication exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.warning(
        "Authentication error",
        error=exc.message,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Error",
            "message": exc.message,
            "type": "authentication_error",
        },
    )


async def authorization_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
    """
    Handle authorization errors.
    
    Args:
        request: FastAPI request object
        exc: Authorization exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.warning(
        "Authorization error",
        error=exc.message,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=403,
        content={
            "error": "Authorization Error",
            "message": exc.message,
            "type": "authorization_error",
        },
    )


async def external_service_error_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    """
    Handle external service errors.
    
    Args:
        request: FastAPI request object
        exc: External service exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(
        "External service error",
        service=exc.service,
        error=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=502,
        content={
            "error": "External Service Error",
            "message": f"{exc.service}: {exc.message}",
            "service": exc.service,
            "status_code": exc.status_code,
            "type": "external_service_error",
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general unhandled exceptions.
    
    Args:
        request: FastAPI request object
        exc: General exception
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(
        "Unhandled exception",
        error=str(exc),
        exception_type=type(exc).__name__,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "type": "internal_server_error",
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up all exception handlers for the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(ChatServiceError, chat_service_error_handler)
    app.add_exception_handler(DocumentServiceError, document_service_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler)
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(ExternalServiceError, external_service_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured successfully")
