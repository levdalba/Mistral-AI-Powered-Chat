"""
Chat-related Pydantic models.

This module defines all data models related to chat functionality including
message structures, conversation history, and response metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    """Enumeration of possible message roles in a conversation."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """
    Individual chat message model.
    
    Represents a single message in a conversation with metadata
    about the sender, content, and timing.
    """
    
    id: UUID = Field(default_factory=uuid4, description="Unique message identifier")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., min_length=1, max_length=50000, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")
    
    class Config:
        """Pydantic configuration for ChatMessage."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class ChatMessageRequest(BaseModel):
    """
    Request model for sending a chat message.
    
    Contains the user message and conversation context needed
    to generate an appropriate AI response.
    """
    
    message: str = Field(..., min_length=1, max_length=10000, description="User message content")
    conversation_id: Optional[str] = Field(default=None, description="Conversation identifier")
    model: str = Field(default="mistral-large-latest", description="Mistral model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Response randomness")
    max_tokens: int = Field(default=1000, ge=1, le=4096, description="Maximum response tokens")
    context: Optional[List[ChatMessage]] = Field(default=None, description="Conversation context")
    
    @validator("temperature")
    def validate_temperature(cls, v):
        """Validate temperature parameter is within reasonable bounds."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @validator("max_tokens")
    def validate_max_tokens(cls, v):
        """Validate max_tokens parameter is reasonable."""
        if not 1 <= v <= 4096:
            raise ValueError("max_tokens must be between 1 and 4096")
        return v


class ResponseMetadata(BaseModel):
    """
    Metadata about an AI response.
    
    Contains performance metrics and technical details
    about the response generation process.
    """
    
    model_used: str = Field(..., description="Model that generated the response")
    tokens_used: int = Field(..., description="Total tokens consumed")
    prompt_tokens: int = Field(..., description="Tokens in the prompt")
    completion_tokens: int = Field(..., description="Tokens in the completion")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    finish_reason: str = Field(..., description="Why the response finished")
    
    class Config:
        """Pydantic configuration for ResponseMetadata."""
        schema_extra = {
            "example": {
                "model_used": "mistral-large-latest",
                "tokens_used": 150,
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "response_time_ms": 1250.5,
                "finish_reason": "stop",
            }
        }


class ChatMessageResponse(BaseModel):
    """
    Response model for chat message requests.
    
    Contains the AI-generated response along with conversation
    context and performance metadata.
    """
    
    message: ChatMessage = Field(..., description="AI response message")
    conversation_id: str = Field(..., description="Conversation identifier")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    context_used: int = Field(..., description="Number of context messages used")
    
    class Config:
        """Pydantic configuration for ChatMessageResponse."""
        schema_extra = {
            "example": {
                "message": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "role": "assistant",
                    "content": "Hello! How can I help you today?",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "metadata": None,
                },
                "conversation_id": "conv_123",
                "metadata": {
                    "model_used": "mistral-large-latest",
                    "tokens_used": 150,
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "response_time_ms": 1250.5,
                    "finish_reason": "stop",
                },
                "context_used": 3,
            }
        }


class ConversationSummary(BaseModel):
    """
    Summary information about a conversation.
    
    Provides high-level metrics and metadata about
    a conversation without the full message history.
    """
    
    conversation_id: str = Field(..., description="Conversation identifier")
    title: Optional[str] = Field(default=None, description="Conversation title")
    message_count: int = Field(..., description="Total number of messages")
    created_at: datetime = Field(..., description="Conversation creation time")
    last_activity: datetime = Field(..., description="Last message timestamp")
    total_tokens: int = Field(default=0, description="Total tokens used")
    
    class Config:
        """Pydantic configuration for ConversationSummary."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ConversationHistory(BaseModel):
    """
    Complete conversation history model.
    
    Contains all messages in a conversation along with
    summary information and metadata.
    """
    
    conversation_id: str = Field(..., description="Conversation identifier")
    messages: List[ChatMessage] = Field(..., description="All conversation messages")
    summary: ConversationSummary = Field(..., description="Conversation summary")
    total_pages: int = Field(default=1, description="Total pages for pagination")
    current_page: int = Field(default=1, description="Current page number")
    
    class Config:
        """Pydantic configuration for ConversationHistory."""
        schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "messages": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "role": "user",
                        "content": "Hello!",
                        "timestamp": "2024-01-01T12:00:00Z",
                    },
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "role": "assistant", 
                        "content": "Hello! How can I help you today?",
                        "timestamp": "2024-01-01T12:00:01Z",
                    },
                ],
                "summary": {
                    "conversation_id": "conv_123",
                    "title": "General Chat",
                    "message_count": 2,
                    "created_at": "2024-01-01T12:00:00Z",
                    "last_activity": "2024-01-01T12:00:01Z",
                    "total_tokens": 50,
                },
                "total_pages": 1,
                "current_page": 1,
            }
        }


class ConversationMetrics(BaseModel):
    """
    Performance metrics for a conversation.
    
    Contains analytics data about conversation performance
    including response times, token usage, and quality metrics.
    """
    
    conversation_id: str = Field(..., description="Conversation identifier")
    title: Optional[str] = Field(default=None, description="Conversation title")
    message_count: int = Field(..., description="Total number of messages")
    total_tokens: int = Field(..., description="Total tokens used")
    avg_response_time_ms: float = Field(..., description="Average response time")
    created_at: datetime = Field(..., description="Conversation creation time")
    last_activity: datetime = Field(..., description="Last message timestamp")
    
    # Performance metrics
    min_response_time_ms: float = Field(default=0.0, description="Fastest response time")
    max_response_time_ms: float = Field(default=0.0, description="Slowest response time")
    total_cost_estimate: float = Field(default=0.0, description="Estimated total cost")
    
    class Config:
        """Pydantic configuration for ConversationMetrics."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "title": "Technical Discussion",
                "message_count": 15,
                "total_tokens": 2500,
                "avg_response_time_ms": 1250.5,
                "created_at": "2024-01-01T12:00:00Z",
                "last_activity": "2024-01-01T14:30:00Z",
                "min_response_time_ms": 800.0,
                "max_response_time_ms": 2100.0,
                "total_cost_estimate": 0.15,
            }
        }
