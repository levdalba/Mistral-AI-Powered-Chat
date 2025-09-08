"""
Chat service implementation.

This module handles all chat-related business logic including message processing,
conversation management, and integration with Mistral AI models.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import structlog
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage

from app.config import get_settings
from app.models.chat import (
    ChatMessage,
    ChatMessageResponse,
    ConversationHistory,
    ConversationMetrics,
    ConversationSummary,
    MessageRole,
    ResponseMetadata,
)
from app.utils.exceptions import ChatServiceError

# Get application settings
settings = get_settings()
logger = structlog.get_logger(__name__)


class ChatService:
    """
    Service class for handling chat operations.
    
    This service manages conversations, processes messages through Mistral AI,
    and maintains conversation history and analytics.
    """
    
    def __init__(self):
        """
        Initialize the chat service.
        
        Sets up the Mistral AI client and initializes storage for
        conversation history and metrics.
        """
        try:
            self.client = MistralClient(api_key=settings.mistral_api_key)
            # In-memory storage for demo purposes
            # In production, this would be replaced with a database
            self.conversations: Dict[str, List[ChatMessage]] = {}
            self.conversation_metadata: Dict[str, ConversationSummary] = {}
            self.response_metrics: Dict[str, List[ResponseMetadata]] = {}
            
            logger.info("Chat service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize chat service", error=str(e))
            raise ChatServiceError(f"Failed to initialize chat service: {str(e)}")
    
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        context: Optional[List[ChatMessage]] = None,
    ) -> ChatMessageResponse:
        """
        Send a message to Mistral AI and get a response.
        
        Args:
            message: User message content
            conversation_id: Optional conversation identifier
            model: Mistral model to use (defaults to configured model)
            temperature: Response randomness (0.0 to 2.0)
            max_tokens: Maximum response tokens
            context: Optional conversation context
            
        Returns:
            ChatMessageResponse: AI response with metadata
            
        Raises:
            ChatServiceError: If message processing fails
        """
        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv_{uuid4().hex[:8]}"
            
            # Use default model if not specified
            if not model:
                model = settings.mistral_model
            
            start_time = time.time()
            
            # Prepare conversation context
            messages = self._prepare_conversation_context(
                message, conversation_id, context
            )
            
            # Convert to Mistral format
            mistral_messages = [
                MistralChatMessage(role=msg.role.value, content=msg.content)
                for msg in messages
            ]
            
            logger.info(
                "Sending message to Mistral AI",
                conversation_id=conversation_id,
                model=model,
                context_messages=len(mistral_messages),
            )
            
            # Call Mistral AI
            response = self.client.chat(
                model=model,
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Extract response content
            ai_message_content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # Calculate token usage
            usage = response.usage
            tokens_used = usage.total_tokens
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            
            # Create response message
            ai_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=ai_message_content,
                timestamp=datetime.utcnow(),
            )
            
            # Create response metadata
            metadata = ResponseMetadata(
                model_used=model,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                response_time_ms=response_time_ms,
                finish_reason=finish_reason,
            )
            
            # Store messages in conversation history
            self._store_conversation_messages(
                conversation_id, 
                [
                    ChatMessage(
                        role=MessageRole.USER,
                        content=message,
                        timestamp=datetime.utcnow(),
                    ),
                    ai_message,
                ]
            )
            
            # Store response metrics
            self._store_response_metrics(conversation_id, metadata)
            
            logger.info(
                "Message processed successfully",
                conversation_id=conversation_id,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
            )
            
            return ChatMessageResponse(
                message=ai_message,
                conversation_id=conversation_id,
                metadata=metadata,
                context_used=len(messages),
            )
            
        except Exception as e:
            logger.error(
                "Error processing message",
                error=str(e),
                conversation_id=conversation_id,
            )
            raise ChatServiceError(f"Failed to process message: {str(e)}")
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Optional[ConversationHistory]:
        """
        Retrieve conversation history.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            ConversationHistory: Complete conversation history or None if not found
        """
        try:
            if conversation_id not in self.conversations:
                logger.warning("Conversation not found", conversation_id=conversation_id)
                return None
            
            messages = self.conversations[conversation_id]
            
            # Apply pagination
            if limit:
                paginated_messages = messages[offset:offset + limit]
            else:
                paginated_messages = messages[offset:]
            
            # Get conversation summary
            summary = self.conversation_metadata.get(conversation_id)
            if not summary:
                summary = self._create_conversation_summary(conversation_id, messages)
            
            # Calculate pagination info
            total_messages = len(messages)
            page_size = limit or total_messages
            total_pages = (total_messages + page_size - 1) // page_size if page_size > 0 else 1
            current_page = (offset // page_size) + 1 if page_size > 0 else 1
            
            return ConversationHistory(
                conversation_id=conversation_id,
                messages=paginated_messages,
                summary=summary,
                total_pages=total_pages,
                current_page=current_page,
            )
            
        except Exception as e:
            logger.error(
                "Error retrieving conversation history",
                error=str(e),
                conversation_id=conversation_id,
            )
            raise ChatServiceError(f"Failed to retrieve conversation history: {str(e)}")
    
    async def list_conversations(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ConversationMetrics]:
        """
        List all conversations with metrics.
        
        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List[ConversationMetrics]: List of conversation metrics
        """
        try:
            conversation_ids = list(self.conversations.keys())[offset:offset + limit]
            metrics = []
            
            for conv_id in conversation_ids:
                conversation_metrics = self._calculate_conversation_metrics(conv_id)
                if conversation_metrics:
                    metrics.append(conversation_metrics)
            
            logger.info("Listed conversations", count=len(metrics))
            return metrics
            
        except Exception as e:
            logger.error("Error listing conversations", error=str(e))
            raise ChatServiceError(f"Failed to list conversations: {str(e)}")
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all associated data.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        try:
            if conversation_id not in self.conversations:
                logger.warning("Conversation not found for deletion", conversation_id=conversation_id)
                return False
            
            # Remove conversation data
            del self.conversations[conversation_id]
            
            if conversation_id in self.conversation_metadata:
                del self.conversation_metadata[conversation_id]
            
            if conversation_id in self.response_metrics:
                del self.response_metrics[conversation_id]
            
            logger.info("Conversation deleted", conversation_id=conversation_id)
            return True
            
        except Exception as e:
            logger.error(
                "Error deleting conversation",
                error=str(e),
                conversation_id=conversation_id,
            )
            raise ChatServiceError(f"Failed to delete conversation: {str(e)}")
    
    def _prepare_conversation_context(
        self,
        message: str,
        conversation_id: str,
        context: Optional[List[ChatMessage]] = None,
    ) -> List[ChatMessage]:
        """
        Prepare conversation context for the AI model.
        
        Args:
            message: Current user message
            conversation_id: Conversation identifier
            context: Optional external context
            
        Returns:
            List[ChatMessage]: Complete conversation context
        """
        messages = []
        
        # Add conversation history if available
        if conversation_id in self.conversations:
            # Use last 10 messages for context (adjust based on model limits)
            history_messages = self.conversations[conversation_id][-10:]
            messages.extend(history_messages)
        
        # Add external context if provided
        if context:
            messages.extend(context)
        
        # Add current user message
        messages.append(ChatMessage(
            role=MessageRole.USER,
            content=message,
            timestamp=datetime.utcnow(),
        ))
        
        return messages
    
    def _store_conversation_messages(
        self,
        conversation_id: str,
        messages: List[ChatMessage],
    ) -> None:
        """
        Store messages in conversation history.
        
        Args:
            conversation_id: Conversation identifier
            messages: Messages to store
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].extend(messages)
        
        # Update conversation metadata
        all_messages = self.conversations[conversation_id]
        summary = self._create_conversation_summary(conversation_id, all_messages)
        self.conversation_metadata[conversation_id] = summary
    
    def _store_response_metrics(
        self,
        conversation_id: str,
        metadata: ResponseMetadata,
    ) -> None:
        """
        Store response metrics for analytics.
        
        Args:
            conversation_id: Conversation identifier
            metadata: Response metadata to store
        """
        if conversation_id not in self.response_metrics:
            self.response_metrics[conversation_id] = []
        
        self.response_metrics[conversation_id].append(metadata)
    
    def _create_conversation_summary(
        self,
        conversation_id: str,
        messages: List[ChatMessage],
    ) -> ConversationSummary:
        """
        Create summary for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            messages: All messages in the conversation
            
        Returns:
            ConversationSummary: Conversation summary
        """
        if not messages:
            return ConversationSummary(
                conversation_id=conversation_id,
                message_count=0,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                total_tokens=0,
            )
        
        # Calculate total tokens from metrics
        total_tokens = 0
        if conversation_id in self.response_metrics:
            total_tokens = sum(
                metric.tokens_used 
                for metric in self.response_metrics[conversation_id]
            )
        
        # Generate title from first user message
        title = None
        first_user_message = next(
            (msg for msg in messages if msg.role == MessageRole.USER), 
            None
        )
        if first_user_message:
            title = first_user_message.content[:50] + ("..." if len(first_user_message.content) > 50 else "")
        
        return ConversationSummary(
            conversation_id=conversation_id,
            title=title,
            message_count=len(messages),
            created_at=messages[0].timestamp,
            last_activity=messages[-1].timestamp,
            total_tokens=total_tokens,
        )
    
    def _calculate_conversation_metrics(
        self,
        conversation_id: str,
    ) -> Optional[ConversationMetrics]:
        """
        Calculate performance metrics for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            ConversationMetrics: Performance metrics or None if not found
        """
        if conversation_id not in self.conversations:
            return None
        
        messages = self.conversations[conversation_id]
        metrics = self.response_metrics.get(conversation_id, [])
        summary = self.conversation_metadata.get(conversation_id)
        
        if not summary:
            summary = self._create_conversation_summary(conversation_id, messages)
        
        # Calculate performance metrics
        response_times = [metric.response_time_ms for metric in metrics]
        total_tokens = sum(metric.tokens_used for metric in metrics)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        min_response_time = min(response_times) if response_times else 0.0
        max_response_time = max(response_times) if response_times else 0.0
        
        # Estimate cost (rough calculation, adjust based on actual pricing)
        total_cost_estimate = total_tokens * 0.0001  # Example: $0.0001 per token
        
        return ConversationMetrics(
            conversation_id=conversation_id,
            title=summary.title,
            message_count=len(messages),
            total_tokens=total_tokens,
            avg_response_time_ms=avg_response_time,
            created_at=summary.created_at,
            last_activity=summary.last_activity,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            total_cost_estimate=total_cost_estimate,
        )
