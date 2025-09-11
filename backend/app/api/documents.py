"""
Document API endpoints.

This module handles all document-related API endpoints including file upload,
document processing, vector search, and document Q&A functionality.
"""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPBearer

from app.models.document import (
    DocumentInfo,
    DocumentQueryRequest,
    DocumentQueryResponse,
    DocumentUploadResponse,
)
from app.services.document_service import DocumentService
from app.utils.exceptions import DocumentServiceError

# Setup router and logging
router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger(__name__)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload a document",
    description="""
    Upload a document (PDF, TXT, DOCX) for processing and Q&A.
    
    The document will be processed, chunked, and indexed for vector search.
    Supported file types: PDF, TXT, DOCX (up to 10MB).
    """,
)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(),
) -> DocumentUploadResponse:
    """
    Upload and process a document for Q&A.
    
    Args:
        file: Document file to upload
        document_service: Injected document service dependency
        
    Returns:
        DocumentUploadResponse: Upload confirmation with document metadata
        
    Raises:
        HTTPException: If upload or processing fails
    """
    try:
        logger.info(
            "Document upload started",
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size if hasattr(file, 'size') else 'unknown',
        )
        
        # Process the uploaded document
        response = await document_service.upload_document(file)
        
        logger.info(
            "Document upload completed",
            document_id=response.document_id,
            filename=response.filename,
            chunks_created=response.chunks_count,
        )
        
        return response
        
    except DocumentServiceError as e:
        logger.error("Document service error", error=str(e), filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document service error: {str(e)}",
        )
    except Exception as e:
        logger.error("Unexpected error in document upload", error=str(e), filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during document upload",
        )


@router.post(
    "/query",
    response_model=DocumentQueryResponse,
    summary="Query documents",
    description="""
    Ask questions about uploaded documents using semantic search and AI.
    
    The system will find relevant document chunks and generate an answer
    based on the document content using Mistral AI.
    """,
)
async def query_documents(
    request: DocumentQueryRequest,
    document_service: DocumentService = Depends(),
) -> DocumentQueryResponse:
    """
    Query documents with natural language questions.
    
    Args:
        request: Document query request with question and options
        document_service: Injected document service dependency
        
    Returns:
        DocumentQueryResponse: AI-generated answer with source references
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(
            "Document query started",
            question=request.question[:50] + "..." if len(request.question) > 50 else request.question,
            document_ids=request.document_ids,
        )
        
        # Process the document query
        response = await document_service.query_documents(
            question=request.question,
            document_ids=request.document_ids,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold,
        )
        
        logger.info(
            "Document query completed",
            sources_found=len(response.sources),
            answer_length=len(response.answer),
        )
        
        return response
        
    except DocumentServiceError as e:
        logger.error("Document service error", error=str(e), question=request.question)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document service error: {str(e)}",
        )
    except Exception as e:
        logger.error("Unexpected error in document query", error=str(e), question=request.question)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during document query",
        )


@router.get(
    "/list",
    response_model=List[DocumentInfo],
    summary="List uploaded documents",
    description="""
    Get a list of all uploaded documents with metadata including
    file information, processing status, and chunk statistics.
    """,
)
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    document_service: DocumentService = Depends(),
) -> List[DocumentInfo]:
    """
    List all uploaded documents with metadata.
    
    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip (for pagination)
        document_service: Injected document service dependency
        
    Returns:
        List[DocumentInfo]: List of document information
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info("Listing documents", limit=limit, offset=offset)
        
        documents = await document_service.list_documents(
            limit=limit,
            offset=offset,
        )
        
        logger.info("Documents listed", count=len(documents))
        return documents
        
    except Exception as e:
        logger.error("Error listing documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents",
        )


@router.get(
    "/{document_id}",
    response_model=DocumentInfo,
    summary="Get document information",
    description="""
    Get detailed information about a specific document including
    metadata, processing status, and chunk information.
    """,
)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(),
) -> DocumentInfo:
    """
    Get information about a specific document.
    
    Args:
        document_id: Unique identifier for the document
        document_service: Injected document service dependency
        
    Returns:
        DocumentInfo: Document information and metadata
        
    Raises:
        HTTPException: If document not found or retrieval fails
    """
    try:
        logger.info("Getting document info", document_id=document_id)
        
        document_info = await document_service.get_document_info(document_id)
        
        if not document_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )
        
        logger.info("Document info retrieved", document_id=document_id)
        return document_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting document info", error=str(e), document_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document information",
        )


@router.delete(
    "/{document_id}",
    summary="Delete document",
    description="""
    Delete a document and all associated data including chunks and embeddings.
    This action cannot be undone.
    """,
)
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(),
) -> dict:
    """
    Delete a document and all its associated data.
    
    Args:
        document_id: Unique identifier for the document
        document_service: Injected document service dependency
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If document not found or deletion fails
    """
    try:
        logger.info("Deleting document", document_id=document_id)
        
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )
        
        logger.info("Document deleted successfully", document_id=document_id)
        
        return {
            "message": f"Document {document_id} deleted successfully",
            "document_id": document_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting document", error=str(e), document_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )
