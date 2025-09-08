"""
Chat API endpoints.

This module handles all chat-related API endpoints including sending messages,
retrieving chat history, and managing conversations with Mistral AI.
"""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.models.chat import (
    ChatMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationHistory,
    ConversationMetrics,
)
from app.services.chat_service import ChatService
from app.utils.exceptions import ChatServiceError

# Setup router and logging
router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger(__name__)


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send a chat message",
    description="""
    Send a message to the Mistral AI model and receive a response.
    
    This endpoint processes user messages and returns AI-generated responses
    with metadata including token usage, response time, and conversation context.
    """,
)
async def send_message(
    request: ChatMessageRequest,
    chat_service: ChatService = Depends(),
) -> ChatMessageResponse:
    """
    Send a chat message to Mistral AI and get a response.
    
    Args:
        request: Chat message request containing the user message and context
        chat_service: Injected chat service dependency
        
    Returns:
        ChatMessageResponse: AI response with metadata
        
    Raises:
        HTTPException: If message processing fails
    """
    try:
        logger.info(
            "Processing chat message",
            user_message=request.message[:50] + "..." if len(request.message) > 50 else request.message,
            conversation_id=request.conversation_id,
            model=request.model,
        )
        
        # Process the chat message
        response = await chat_service.send_message(
            message=request.message,
            conversation_id=request.conversation_id,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            context=request.context,
        )
        
        logger.info(
            "Chat message processed successfully",
            conversation_id=response.conversation_id,
            tokens_used=response.metadata.tokens_used,
            response_time=response.metadata.response_time_ms,
        )
        
        return response
        
    except ChatServiceError as e:
        logger.error("Chat service error", error=str(e), conversation_id=request.conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat service error: {str(e)}",
        )
    except Exception as e:
        logger.error("Unexpected error in chat", error=str(e), conversation_id=request.conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while processing message",
        )


@router.get(
    "/history/{conversation_id}",
    response_model=ConversationHistory,
    summary="Get conversation history",
    description="""
    Retrieve the complete history of a conversation including all messages
    and metadata.
    """,
)
async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = None,
    offset: int = 0,
    chat_service: ChatService = Depends(),
) -> ConversationHistory:
    """
    Get conversation history for a specific conversation.
    
    Args:
        conversation_id: Unique identifier for the conversation
        limit: Maximum number of messages to return (optional)
        offset: Number of messages to skip (for pagination)
        chat_service: Injected chat service dependency
        
    Returns:
        ConversationHistory: Complete conversation history
        
    Raises:
        HTTPException: If conversation not found or retrieval fails
    """
    try:
        logger.info(
            "Retrieving conversation history",
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )
        
        history = await chat_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
        
        logger.info(
            "Conversation history retrieved",
            conversation_id=conversation_id,
            message_count=len(history.messages),
        )
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving conversation history", error=str(e), conversation_id=conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history",
        )


@router.get(
    "/conversations",
    response_model=List[ConversationMetrics],
    summary="List all conversations",
    description="""
    Get a list of all conversations with basic metadata including
    message count, last activity, and performance metrics.
    """,
)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    chat_service: ChatService = Depends(),
) -> List[ConversationMetrics]:
    """
    List all conversations with metadata.
    
    Args:
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip (for pagination)
        chat_service: Injected chat service dependency
        
    Returns:
        List[ConversationMetrics]: List of conversation summaries
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info("Listing conversations", limit=limit, offset=offset)
        
        conversations = await chat_service.list_conversations(
            limit=limit,
            offset=offset,
        )
        
        logger.info("Conversations listed", count=len(conversations))
        return conversations
        
    except Exception as e:
        logger.error("Error listing conversations", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        )


@router.delete(
    "/history/{conversation_id}",
    summary="Delete conversation",
    description="""
    Delete a specific conversation and all associated messages.
    This action cannot be undone.
    """,
)
async def delete_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(),
) -> dict:
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: Unique identifier for the conversation
        chat_service: Injected chat service dependency
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If conversation not found or deletion fails
    """
    try:
        logger.info("Deleting conversation", conversation_id=conversation_id)
        
        success = await chat_service.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
        
        logger.info("Conversation deleted successfully", conversation_id=conversation_id)
        
        return {
            "message": f"Conversation {conversation_id} deleted successfully",
            "conversation_id": conversation_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting conversation", error=str(e), conversation_id=conversation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )
