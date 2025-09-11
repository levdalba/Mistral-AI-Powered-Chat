"""
Logging configuration for the Mistral AI Chat Backend.

This module sets up structured logging with configurable output formats
and log levels for better observability and debugging.
"""

import json
import logging
import sys
from typing import Any, Dict

import structlog


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure structured logging for the application.
    
    Sets up structlog with appropriate processors, formatters, and output
    configuration based on the environment and specified preferences.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' or 'console')
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Determine processors based on format
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add format-specific processor
    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    return structlog.get_logger(name)


class RequestLoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses.
    
    This middleware logs incoming requests with relevant metadata
    and response information for monitoring and debugging.
    """
    
    def __init__(self, app):
        """
        Initialize the logging middleware.
        
        Args:
            app: ASGI application instance
        """
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope: Dict[str, Any], receive, send):
        """
        Process HTTP request with logging.
        
        Args:
            scope: ASGI scope dict
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_info = {
            "method": scope.get("method"),
            "path": scope.get("path"),
            "query_string": scope.get("query_string", b"").decode(),
            "client": scope.get("client"),
            "headers": dict(scope.get("headers", [])),
        }
        
        self.logger.info("HTTP request started", **request_info)
        
        # Wrap send to capture response status
        response_status = None
        
        async def send_wrapper(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status")
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
            
            self.logger.info(
                "HTTP request completed",
                method=request_info["method"],
                path=request_info["path"],
                status_code=response_status,
            )
            
        except Exception as e:
            self.logger.error(
                "HTTP request failed",
                method=request_info["method"],
                path=request_info["path"],
                error=str(e),
                exception_type=type(e).__name__,
            )
            raise


class LoggingContext:
    """
    Context manager for adding structured logging context.
    
    This context manager allows adding temporary context to log messages
    that automatically gets removed when exiting the context.
    """
    
    def __init__(self, logger: structlog.BoundLogger, **context):
        """
        Initialize logging context.
        
        Args:
            logger: Structlog logger instance
            **context: Additional context to add to log messages
        """
        self.logger = logger
        self.context = context
        self.bound_logger = None
    
    def __enter__(self) -> structlog.BoundLogger:
        """
        Enter the logging context.
        
        Returns:
            structlog.BoundLogger: Logger with bound context
        """
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the logging context.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        # Context is automatically removed when bound logger goes out of scope
        pass


def log_function_call(func_name: str, **kwargs) -> LoggingContext:
    """
    Create a logging context for function calls.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Additional context for the function call
        
    Returns:
        LoggingContext: Context manager for the function call
    """
    logger = get_logger("function_calls")
    context = {"function": func_name, **kwargs}
    return LoggingContext(logger, **context)


def log_performance(operation: str, duration_ms: float, **metadata) -> None:
    """
    Log performance metrics for operations.
    
    Args:
        operation: Name of the operation
        duration_ms: Duration in milliseconds
        **metadata: Additional performance metadata
    """
    logger = get_logger("performance")
    logger.info(
        "Performance metric",
        operation=operation,
        duration_ms=duration_ms,
        **metadata,
    )


def log_api_call(service: str, endpoint: str, status_code: int, duration_ms: float) -> None:
    """
    Log external API calls.
    
    Args:
        service: Name of the external service
        endpoint: API endpoint called
        status_code: HTTP status code returned
        duration_ms: Request duration in milliseconds
    """
    logger = get_logger("api_calls")
    logger.info(
        "External API call",
        service=service,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
    )
