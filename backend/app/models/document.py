"""
Document-related Pydantic models.

This module defines all data models related to document processing,
upload, storage, and query functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class DocumentStatus(str, Enum):
    """Enumeration of possible document processing statuses."""
    
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class DocumentInfo(BaseModel):
    """
    Document information and metadata.
    
    Contains all metadata about an uploaded document including
    processing status, file information, and chunk statistics.
    """
    
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type/extension")
    file_size: int = Field(..., description="File size in bytes")
    status: DocumentStatus = Field(..., description="Processing status")
    upload_time: datetime = Field(..., description="Upload timestamp")
    processing_time: Optional[datetime] = Field(default=None, description="Processing completion time")
    chunks_count: int = Field(default=0, description="Number of text chunks created")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    
    class Config:
        """Pydantic configuration for DocumentInfo."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class DocumentUploadResponse(BaseModel):
    """
    Response model for document upload.
    
    Contains confirmation of successful upload and basic
    document metadata.
    """
    
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    status: DocumentStatus = Field(..., description="Current processing status")
    chunks_count: int = Field(default=0, description="Number of chunks created")
    message: str = Field(..., description="Upload status message")


class DocumentChunk(BaseModel):
    """
    Individual document chunk with content and metadata.
    
    Represents a processed text chunk from a document
    with embedding and source information.
    """
    
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Position in document")
    page_number: Optional[int] = Field(default=None, description="Source page number")
    similarity_score: Optional[float] = Field(default=None, description="Similarity score for search results")
    
    class Config:
        """Pydantic configuration for DocumentChunk."""
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_123_001",
                "document_id": "doc_123",
                "content": "This is a sample text chunk from the document...",
                "chunk_index": 0,
                "page_number": 1,
                "similarity_score": 0.85,
            }
        }


class DocumentQueryRequest(BaseModel):
    """
    Request model for document queries.
    
    Contains the question and optional parameters for
    searching and querying documents.
    """
    
    question: str = Field(..., min_length=1, max_length=1000, description="Question to ask about documents")
    document_ids: Optional[List[str]] = Field(default=None, description="Specific document IDs to search")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    
    @validator("similarity_threshold")
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v


class DocumentQueryResponse(BaseModel):
    """
    Response model for document queries.
    
    Contains the AI-generated answer along with source
    document chunks and metadata.
    """
    
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI-generated answer")
    sources: List[DocumentChunk] = Field(..., description="Source document chunks")
    confidence_score: float = Field(..., description="Confidence in the answer")
    processing_time_ms: float = Field(..., description="Query processing time")
    
    class Config:
        """Pydantic configuration for DocumentQueryResponse."""
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of this document?",
                "answer": "The main topic discusses...",
                "sources": [
                    {
                        "chunk_id": "chunk_123_001",
                        "document_id": "doc_123",
                        "content": "Relevant text from document...",
                        "chunk_index": 0,
                        "page_number": 1,
                        "similarity_score": 0.92,
                    }
                ],
                "confidence_score": 0.85,
                "processing_time_ms": 1250.5,
            }
        }
