/**
 * Chat API client for communicating with the Mistral AI backend.
 *
 * Provides methods for:
 * - Sending chat messages
 * - Retrieving conversation history
 * - Managing conversations
 */

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export interface ChatMessageRequest {
    message: string
    conversation_id?: string
    model?: string
    temperature?: number
    max_tokens?: number
    context?: any[]
}

export interface ChatMessageResponse {
    message: {
        id: string
        role: 'assistant'
        content: string
        timestamp: string
    }
    conversation_id: string
    metadata: {
        model_used: string
        tokens_used: number
        prompt_tokens: number
        completion_tokens: number
        response_time_ms: number
        finish_reason: string
    }
    context_used: number
}

export interface ConversationHistory {
    conversation_id: string
    messages: Array<{
        id: string
        role: 'user' | 'assistant' | 'system'
        content: string
        timestamp: string
        metadata?: any
    }>
    summary: {
        conversation_id: string
        title?: string
        message_count: number
        created_at: string
        last_activity: string
        total_tokens: number
    }
    total_pages: number
    current_page: number
}

export interface ConversationMetrics {
    conversation_id: string
    title?: string
    message_count: number
    total_tokens: number
    avg_response_time_ms: number
    created_at: string
    last_activity: string
    min_response_time_ms: number
    max_response_time_ms: number
    total_cost_estimate: number
}

class ChatApiClient {
    private baseUrl: string

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`

        const config: RequestInit = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        }

        try {
            const response = await fetch(url, config)

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(
                    errorData.detail ||
                        errorData.message ||
                        `HTTP ${response.status}: ${response.statusText}`
                )
            }

            return await response.json()
        } catch (error) {
            if (error instanceof Error) {
                throw error
            }
            throw new Error('Network request failed')
        }
    }

    /**
     * Send a chat message to the AI
     */
    async sendMessage(
        request: ChatMessageRequest,
        abortSignal?: AbortSignal
    ): Promise<ChatMessageResponse> {
        // Optimize parameters for faster response
        const optimizedRequest = {
            ...request,
            temperature: request.temperature || 0.3, // Lower temperature for faster, more focused responses
            max_tokens: request.max_tokens || 500,   // Limit tokens for faster responses
        }

        return this.request<ChatMessageResponse>('/api/chat/message', {
            method: 'POST',
            body: JSON.stringify(optimizedRequest),
            signal: abortSignal,
        })
    }

    /**
     * Get conversation history
     */
    async getConversationHistory(
        conversationId: string,
        limit?: number,
        offset?: number
    ): Promise<ConversationHistory> {
        const params = new URLSearchParams()
        if (limit) params.append('limit', limit.toString())
        if (offset) params.append('offset', offset.toString())

        const queryString = params.toString()
        const endpoint = `/api/chat/history/${conversationId}${queryString ? `?${queryString}` : ''}`

        return this.request<ConversationHistory>(endpoint)
    }

    /**
     * List all conversations with metadata
     */
    async listConversations(
        limit: number = 20,
        offset: number = 0
    ): Promise<ConversationMetrics[]> {
        const params = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString(),
        })

        return this.request<ConversationMetrics[]>(
            `/api/chat/conversations?${params}`
        )
    }

    /**
     * Delete a conversation
     */
    async deleteConversation(
        conversationId: string
    ): Promise<{ message: string }> {
        return this.request<{ message: string }>(
            `/api/chat/history/${conversationId}`,
            {
                method: 'DELETE',
            }
        )
    }

    /**
     * Health check
     */
    async healthCheck(): Promise<{ status: string; version: string }> {
        return this.request<{ status: string; version: string }>('/health')
    }
}

// Export singleton instance
export const chatApi = new ChatApiClient()

// Export class for custom instances
export { ChatApiClient }
