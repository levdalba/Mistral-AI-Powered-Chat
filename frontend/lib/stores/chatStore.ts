/**
 * Chat store using Zustand for state management.
 *
 * Manages:
 * - Current conversation messages
 * - Conversation ID tracking
 * - Message history
 * - Error states
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface ChatMessage {
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: string
    metadata?: {
        model_used?: string
        tokens_used?: number
        response_time_ms?: number
        finish_reason?: string
    }
}

export interface Conversation {
    id: string
    title?: string
    messages: ChatMessage[]
    created_at: string
    updated_at: string
}

interface ChatState {
    // Current conversation
    currentConversationId: string | null
    messages: ChatMessage[]

    // All conversations
    conversations: Conversation[]

    // UI state
    isLoading: boolean
    error: string | null

    // Actions
    addMessage: (message: ChatMessage) => void
    setMessages: (messages: ChatMessage[]) => void
    clearMessages: () => void
    clearCurrentChat: () => void

    setConversationId: (id: string) => void
    loadConversation: (id: string) => void
    createNewConversation: () => void
    deleteConversation: (id: string) => void

    setLoading: (loading: boolean) => void
    setError: (error: string | null) => void
    clearError: () => void

    // Conversation management
    saveCurrentConversation: () => void
    getConversationTitle: (messages: ChatMessage[]) => string
}

export const useChatStore = create<ChatState>()(
    persist(
        (set, get) => ({
            // Initial state
            currentConversationId: null,
            messages: [],
            conversations: [],
            isLoading: false,
            error: null,

            // Message actions
            addMessage: (message) => {
                set((state) => {
                    const newMessages = [...state.messages, message]

                    // Auto-save conversation
                    if (state.currentConversationId) {
                        const conversationIndex = state.conversations.findIndex(
                            (conv) => conv.id === state.currentConversationId
                        )

                        if (conversationIndex >= 0) {
                            const updatedConversations = [
                                ...state.conversations,
                            ]
                            updatedConversations[conversationIndex] = {
                                ...updatedConversations[conversationIndex],
                                messages: newMessages,
                                updated_at: new Date().toISOString(),
                                title:
                                    updatedConversations[conversationIndex]
                                        .title ||
                                    get().getConversationTitle(newMessages),
                            }

                            return {
                                messages: newMessages,
                                conversations: updatedConversations,
                            }
                        }
                    }

                    return { messages: newMessages }
                })
            },

            setMessages: (messages) => set({ messages }),

            clearMessages: () => set({ messages: [] }),

            clearCurrentChat: () => set({ 
                messages: [], 
                currentConversationId: null, 
                error: null,
                isLoading: false 
            }),

            // Conversation actions
            setConversationId: (id) => set({ currentConversationId: id }),

            loadConversation: (id) => {
                const conversation = get().conversations.find(
                    (conv) => conv.id === id
                )
                if (conversation) {
                    set({
                        currentConversationId: id,
                        messages: conversation.messages,
                        error: null,
                    })
                }
            },

            createNewConversation: () => {
                const newId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
                const newConversation: Conversation = {
                    id: newId,
                    messages: [],
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                }

                set((state) => ({
                    currentConversationId: newId,
                    messages: [],
                    conversations: [newConversation, ...state.conversations],
                    error: null,
                }))
            },

            deleteConversation: (id) => {
                set((state) => {
                    const updatedConversations = state.conversations.filter(
                        (conv) => conv.id !== id
                    )

                    // If deleting current conversation, clear it
                    if (state.currentConversationId === id) {
                        return {
                            conversations: updatedConversations,
                            currentConversationId: null,
                            messages: [],
                        }
                    }

                    return { conversations: updatedConversations }
                })
            },

            // UI state actions
            setLoading: (loading) => set({ isLoading: loading }),
            setError: (error) => set({ error }),
            clearError: () => set({ error: null }),

            // Helper functions
            saveCurrentConversation: () => {
                const state = get()
                if (!state.currentConversationId || state.messages.length === 0)
                    return

                const conversationIndex = state.conversations.findIndex(
                    (conv) => conv.id === state.currentConversationId
                )

                if (conversationIndex >= 0) {
                    const updatedConversations = [...state.conversations]
                    updatedConversations[conversationIndex] = {
                        ...updatedConversations[conversationIndex],
                        messages: state.messages,
                        updated_at: new Date().toISOString(),
                        title:
                            updatedConversations[conversationIndex].title ||
                            state.getConversationTitle(state.messages),
                    }

                    set({ conversations: updatedConversations })
                } else {
                    // Create new conversation
                    const newConversation: Conversation = {
                        id: state.currentConversationId,
                        title: state.getConversationTitle(state.messages),
                        messages: state.messages,
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                    }

                    set((prevState) => ({
                        conversations: [
                            newConversation,
                            ...prevState.conversations,
                        ],
                    }))
                }
            },

            getConversationTitle: (messages) => {
                const firstUserMessage = messages.find(
                    (msg) => msg.role === 'user'
                )
                if (firstUserMessage) {
                    return firstUserMessage.content.length > 50
                        ? firstUserMessage.content.substring(0, 50) + '...'
                        : firstUserMessage.content
                }
                return 'New Conversation'
            },
        }),
        {
            name: 'mistral-chat-store',
            partialize: (state) => ({
                conversations: state.conversations,
                currentConversationId: state.currentConversationId,
                messages: state.messages,
            }),
        }
    )
)
