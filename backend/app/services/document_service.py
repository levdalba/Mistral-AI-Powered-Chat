"""
Document service implementation.

This module handles all document-related business logic including file upload,
text processing, embedding generation, and vector search functionality.
"""

import os
import time
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import structlog
from fastapi import UploadFile

from app.config import get_settings
from app.models.document import (
    DocumentChunk,
    DocumentInfo,
    DocumentQueryResponse,
    DocumentStatus,
    DocumentUploadResponse,
)
from app.utils.exceptions import DocumentServiceError

# Get application settings
settings = get_settings()
logger = structlog.get_logger(__name__)


class DocumentService:
    """
    Service class for handling document operations.
    
    This service manages document upload, processing, embedding generation,
    and vector search functionality for Q&A capabilities.
    """
    
    def __init__(self):
        """
        Initialize the document service.
        
        Sets up storage directories and initializes in-memory storage
        for document metadata and embeddings.
        """
        try:
            # Create upload directory if it doesn't exist
            os.makedirs(settings.upload_directory, exist_ok=True)
            
            # In-memory storage for demo purposes
            # In production, this would be replaced with a database
            self.documents: dict = {}
            self.document_chunks: dict = {}
            
            logger.info("Document service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize document service", error=str(e))
            raise DocumentServiceError(f"Failed to initialize document service: {str(e)}")
    
    async def upload_document(self, file: UploadFile) -> DocumentUploadResponse:
        """
        Upload and process a document.
        
        Args:
            file: Uploaded file object
            
        Returns:
            DocumentUploadResponse: Upload confirmation with metadata
            
        Raises:
            DocumentServiceError: If upload or processing fails
        """
        try:
            # Validate file type
            if not self._is_valid_file_type(file.filename):
                raise DocumentServiceError(
                    f"Unsupported file type. Allowed types: {settings.allowed_file_types}"
                )
            
            # Generate document ID
            document_id = f"doc_{uuid4().hex[:8]}"
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            max_size = settings.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                raise DocumentServiceError(
                    f"File too large. Maximum size: {settings.max_file_size_mb}MB"
                )
            
            # Save file
            file_path = os.path.join(settings.upload_directory, f"{document_id}_{file.filename}")
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create document info
            document_info = DocumentInfo(
                document_id=document_id,
                filename=file.filename,
                file_type=self._get_file_extension(file.filename),
                file_size=file_size,
                status=DocumentStatus.PROCESSING,
                upload_time=datetime.utcnow(),
            )
            
            # Store document info
            self.documents[document_id] = document_info
            
            # Process document (simplified for demo)
            chunks_count = await self._process_document(document_id, file_path)
            
            # Update document status
            document_info.status = DocumentStatus.READY
            document_info.processing_time = datetime.utcnow()
            document_info.chunks_count = chunks_count
            
            logger.info(
                "Document uploaded and processed",
                document_id=document_id,
                filename=file.filename,
                chunks_count=chunks_count,
            )
            
            return DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                file_size=file_size,
                status=DocumentStatus.READY,
                chunks_count=chunks_count,
                message="Document uploaded and processed successfully",
            )
            
        except DocumentServiceError:
            raise
        except Exception as e:
            logger.error("Error uploading document", error=str(e), filename=file.filename)
            raise DocumentServiceError(f"Failed to upload document: {str(e)}")
    
    async def query_documents(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        max_results: int = 5,
        similarity_threshold: float = 0.7,
    ) -> DocumentQueryResponse:
        """
        Query documents with a natural language question.
        
        Args:
            question: Question to ask about documents
            document_ids: Optional specific document IDs to search
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            DocumentQueryResponse: AI-generated answer with sources
            
        Raises:
            DocumentServiceError: If query processing fails
        """
        try:
            start_time = time.time()
            
            # For demo purposes, return a mock response
            # In production, this would do actual vector search and LLM processing
            
            # Simulate finding relevant chunks
            relevant_chunks = []
            search_document_ids = document_ids or list(self.documents.keys())
            
            for doc_id in search_document_ids[:max_results]:
                if doc_id in self.document_chunks:
                    chunk = self.document_chunks[doc_id][0]  # Get first chunk as demo
                    chunk.similarity_score = 0.85  # Mock similarity score
                    relevant_chunks.append(chunk)
            
            # Generate mock answer
            answer = f"Based on the uploaded documents, here's what I found regarding '{question}': " \
                    f"The documents contain relevant information that addresses your question. " \
                    f"This is a demonstration response that would normally be generated by Mistral AI " \
                    f"based on the document content."
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return DocumentQueryResponse(
                question=question,
                answer=answer,
                sources=relevant_chunks,
                confidence_score=0.8,
                processing_time_ms=processing_time_ms,
            )
            
        except Exception as e:
            logger.error("Error querying documents", error=str(e), question=question)
            raise DocumentServiceError(f"Failed to query documents: {str(e)}")
    
    async def list_documents(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[DocumentInfo]:
        """
        List all uploaded documents.
        
        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            
        Returns:
            List[DocumentInfo]: List of document information
        """
        try:
            documents = list(self.documents.values())
            return documents[offset:offset + limit]
            
        except Exception as e:
            logger.error("Error listing documents", error=str(e))
            raise DocumentServiceError(f"Failed to list documents: {str(e)}")
    
    async def get_document_info(self, document_id: str) -> Optional[DocumentInfo]:
        """
        Get information about a specific document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            DocumentInfo: Document information or None if not found
        """
        try:
            return self.documents.get(document_id)
            
        except Exception as e:
            logger.error("Error getting document info", error=str(e), document_id=document_id)
            raise DocumentServiceError(f"Failed to get document info: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all associated data.
        
        Args:
            document_id: Document identifier
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        try:
            if document_id not in self.documents:
                return False
            
            # Remove document data
            del self.documents[document_id]
            
            if document_id in self.document_chunks:
                del self.document_chunks[document_id]
            
            # TODO: Remove actual file from disk
            
            logger.info("Document deleted", document_id=document_id)
            return True
            
        except Exception as e:
            logger.error("Error deleting document", error=str(e), document_id=document_id)
            raise DocumentServiceError(f"Failed to delete document: {str(e)}")
    
    def _is_valid_file_type(self, filename: str) -> bool:
        """
        Check if file type is allowed.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if file type is allowed
        """
        if not filename:
            return False
        
        file_extension = self._get_file_extension(filename)
        return file_extension.lower() in [ext.lower() for ext in settings.allowed_file_types]
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Get file extension from filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            str: File extension without the dot
        """
        return filename.split('.')[-1] if '.' in filename else ''
    
    async def _process_document(self, document_id: str, file_path: str) -> int:
        """
        Process document and create chunks.
        
        Args:
            document_id: Document identifier
            file_path: Path to the uploaded file
            
        Returns:
            int: Number of chunks created
        """
        try:
            # For demo purposes, create mock chunks
            # In production, this would use actual text extraction and chunking
            
            mock_chunks = [
                DocumentChunk(
                    chunk_id=f"chunk_{document_id}_{i}",
                    document_id=document_id,
                    content=f"This is mock chunk {i} from document {document_id}. "
                           f"In a real implementation, this would contain actual "
                           f"extracted text from the document.",
                    chunk_index=i,
                    page_number=i + 1,
                )
                for i in range(3)  # Create 3 mock chunks
            ]
            
            self.document_chunks[document_id] = mock_chunks
            
            logger.info(
                "Document processed",
                document_id=document_id,
                chunks_created=len(mock_chunks),
            )
            
            return len(mock_chunks)
            
        except Exception as e:
            logger.error("Error processing document", error=str(e), document_id=document_id)
            raise DocumentServiceError(f"Failed to process document: {str(e)}")
