"""
Application configuration settings.

This module handles all configuration management including environment variables,
database settings, and service configurations.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="Mistral AI Chat Backend", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    version: str = Field(default="1.0.0", description="Application version")
    
    # Mistral AI Configuration
    mistral_api_key: str = Field(..., description="Mistral AI API key")
    mistral_model: str = Field(default="mistral-large-latest", description="Default Mistral model")
    mistral_base_url: str = Field(default="https://api.mistral.ai", description="Mistral API base URL")
    
    # Database
    database_url: str = Field(default="sqlite:///./mistral_chat.db", description="Database connection URL")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="JWT token expiration")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"], 
        description="Allowed CORS origins"
    )
    
    # File Upload
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    upload_directory: str = Field(default="./uploads", description="Upload directory path")
    allowed_file_types: List[str] = Field(
        default=["pdf", "txt", "docx"], 
        description="Allowed file extensions"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_burst: int = Field(default=10, description="Rate limit burst size")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    
    # Vector Database
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model name"
    )
    vector_db_path: str = Field(default="./vector_db", description="Vector database path")
    chunk_size: int = Field(default=1000, description="Text chunk size for embeddings")
    chunk_overlap: int = Field(default=200, description="Text chunk overlap")
    
    # Cache
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    This function uses lru_cache to ensure settings are loaded only once
    and cached for subsequent calls, improving performance.
    
    Returns:
        Settings: Application configuration settings
    """
    return Settings()
