'use client'

/**
 * Main chat interface component.
 *
 * This component provides the complete chat experience including:
 * - Message display with conversation history
 * - Message input with send functionality
 * - Real-time typing indicators
 * - Error handling and loading states
 */

import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import { useChatStore } from '@/lib/stores/chatStore'
import { chatApi } from '@/lib/api/chatApi'

interface ChatInterfaceProps {
    className?: string
}

export default function ChatInterface({ className = '' }: ChatInterfaceProps) {
    const [message, setMessage] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [abortController, setAbortController] = useState<AbortController | null>(null)
    const [lastUserMessage, setLastUserMessage] = useState<string>('')
    const inputRef = useRef<HTMLTextAreaElement>(null)

    const {
        messages,
        currentConversationId,
        addMessage,
        setConversationId,
        clearError,
        createNewConversation,
        saveCurrentConversation,
        clearCurrentChat,
    } = useChatStore()

    // Auto-focus input on mount
    useEffect(() => {
        inputRef.current?.focus()
    }, [])

    // Auto-resize textarea
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto'
            inputRef.current.style.height = `${inputRef.current.scrollHeight}px`
        }
    }, [message])

    const handleSendMessage = async () => {
        if (!message.trim() || isLoading) return

        const userMessage = message.trim()
        setLastUserMessage(userMessage)
        setMessage('')
        setError(null)
        setIsLoading(true)

        // Create abort controller for this request
        const controller = new AbortController()
        setAbortController(controller)

        try {
            // Create new conversation if none exists
            let conversationId = currentConversationId
            if (!conversationId) {
                createNewConversation()
                // Get the new conversation ID from the store
                conversationId = useChatStore.getState().currentConversationId
            }

            // Add user message to store
            const userMsgId = crypto.randomUUID()
            addMessage({
                role: 'user',
                content: userMessage,
                timestamp: new Date().toISOString(),
                id: userMsgId,
            })

            // Send to API with abort signal
            const response = await chatApi.sendMessage({
                message: userMessage,
                conversation_id: conversationId,
                model: 'mistral-large-latest',
                temperature: 0.3,
                max_tokens: 500,
            }, controller.signal)

            // Add AI response to store
            addMessage({
                role: 'assistant',
                content: response.message.content,
                timestamp: response.message.timestamp,
                id: response.message.id,
                metadata: response.metadata,
            })

            // Update conversation ID if it's new
            if (!currentConversationId) {
                setConversationId(response.conversation_id)
            }

            // Save the conversation to persist the messages
            saveCurrentConversation()
        } catch (err) {
            if (err instanceof Error && err.name === 'AbortError') {
                setError('Message cancelled')
            } else {
                let errorMessage = 'Failed to send message'
                
                if (err instanceof Error) {
                    if (err.message.includes('429') || err.message.includes('rate limit') || err.message.includes('capacity exceeded')) {
                        errorMessage = '⏳ Mistral AI is busy right now. The system will automatically retry with fallback options. Please wait a moment...'
                    } else if (err.message.includes('network') || err.message.includes('fetch')) {
                        errorMessage = '🌐 Connection issue. Please check your internet connection and try again.'
                    } else {
                        errorMessage = err.message
                    }
                }
                
                setError(errorMessage)
                console.error('Chat error:', err)
            }
        } finally {
            setIsLoading(false)
            setAbortController(null)
            inputRef.current?.focus()
        }
    }

    const handleStopGeneration = () => {
        if (abortController) {
            abortController.abort()
            setIsLoading(false)
            setAbortController(null)
        }
    }

    const handleRedoMessage = async () => {
        if (lastUserMessage && !isLoading) {
            setMessage(lastUserMessage)
            // Automatically send the message again
            const userMessage = lastUserMessage
            setMessage('')
            setError(null)
            setIsLoading(true)

            // Create abort controller for this request
            const controller = new AbortController()
            setAbortController(controller)

            try {
                // Create new conversation if none exists
                let conversationId = currentConversationId
                if (!conversationId) {
                    createNewConversation()
                    conversationId = useChatStore.getState().currentConversationId
                }

                // Add user message to store
                const userMsgId = crypto.randomUUID()
                addMessage({
                    role: 'user',
                    content: userMessage,
                    timestamp: new Date().toISOString(),
                    id: userMsgId,
                })

                // Send to API with abort signal
                const response = await chatApi.sendMessage({
                    message: userMessage,
                    conversation_id: conversationId,
                    model: 'mistral-large-latest',
                    temperature: 0.3,
                    max_tokens: 500,
                }, controller.signal)

                // Add AI response to store
                addMessage({
                    role: 'assistant',
                    content: response.message.content,
                    timestamp: response.message.timestamp,
                    id: response.message.id,
                    metadata: response.metadata,
                })

                // Update conversation ID if it's new
                if (!currentConversationId) {
                    setConversationId(response.conversation_id)
                }

                saveCurrentConversation()
            } catch (err) {
                if (err instanceof Error && err.name === 'AbortError') {
                    setError('Message cancelled')
                } else {
                    let errorMessage = 'Failed to send message'
                    
                    if (err instanceof Error) {
                        if (err.message.includes('429') || err.message.includes('rate limit') || err.message.includes('capacity exceeded')) {
                            errorMessage = '⏳ Mistral AI is busy right now. The system will automatically retry with fallback options. Please wait a moment...'
                        } else if (err.message.includes('network') || err.message.includes('fetch')) {
                            errorMessage = '🌐 Connection issue. Please check your internet connection and try again.'
                        } else {
                            errorMessage = err.message
                        }
                    }
                    
                    setError(errorMessage)
                    console.error('Chat error:', err)
                }
            } finally {
                setIsLoading(false)
                setAbortController(null)
                inputRef.current?.focus()
            }
        }
    }

    const handleEditMessage = async (messageId: string, newContent: string) => {
        // Find the message index and edit it
        const messageIndex = messages.findIndex(m => m.id === messageId)
        if (messageIndex === -1) return

        // Remove all messages after the edited one (to regenerate the conversation)
        const messagesToKeep = messages.slice(0, messageIndex)
        
        // Update the edited message
        const editedMessage = {
            ...messages[messageIndex],
            content: newContent,
            timestamp: new Date().toISOString()
        }

        // Clear current chat and rebuild with edited messages
        clearCurrentChat()
        
        // Re-add messages up to and including the edited one
        messagesToKeep.forEach(msg => addMessage(msg))
        addMessage(editedMessage)

        // If the edited message was from user, regenerate AI response
        if (editedMessage.role === 'user') {
            setLastUserMessage(newContent)
            setError(null)
            setIsLoading(true)

            const controller = new AbortController()
            setAbortController(controller)

            try {
                const response = await chatApi.sendMessage({
                    message: newContent,
                    conversation_id: currentConversationId,
                    model: 'mistral-large-latest',
                    temperature: 0.3,
                    max_tokens: 500,
                }, controller.signal)

                addMessage({
                    role: 'assistant',
                    content: response.message.content,
                    timestamp: response.message.timestamp,
                    id: response.message.id,
                    metadata: response.metadata,
                })

                saveCurrentConversation()
            } catch (err) {
                console.error('Error regenerating response:', err)
                setError('Failed to regenerate response')
            } finally {
                setIsLoading(false)
                setAbortController(null)
            }
        }
    }

    const handleResendMessage = async (messageId: string) => {
        const message = messages.find(m => m.id === messageId)
        if (!message || message.role !== 'user' || isLoading) return

        // Set the message content and trigger redo
        setLastUserMessage(message.content)
        handleRedoMessage()
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    const dismissError = () => {
        setError(null)
        clearError()
    }

    return (
        <div
            className={`flex flex-col bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 ${className}`}
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
                    <span className="font-medium text-slate-900 dark:text-slate-100">
                        Mistral AI {isLoading ? '(Thinking...)' : ''}
                    </span>
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400">
                    {messages.length} messages
                </div>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 p-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-red-700 dark:text-red-400">
                            <span>⚠️</span>
                            <span className="text-sm font-medium">{error}</span>
                        </div>
                        <button
                            onClick={dismissError}
                            className="text-red-500 hover:text-red-700 dark:hover:text-red-300"
                        >
                            ✕
                        </button>
                    </div>
                </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-hidden">
                <MessageList 
                    messages={messages} 
                    isLoading={isLoading} 
                    onEditMessage={handleEditMessage}
                    onResendMessage={handleResendMessage}
                />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-700">
                <div className="flex space-x-3">
                    <div className="flex-1 relative">
                        <textarea
                            ref={inputRef}
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask Mistral AI anything..."
                            className="w-full resize-none rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors"
                            rows={1}
                            maxLength={10000}
                            disabled={isLoading}
                        />
                        <div className="absolute bottom-2 right-2 text-xs text-slate-400">
                            {message.length}/10000
                        </div>
                    </div>

                    {/* Control Buttons */}
                    <div className="flex space-x-2">
                        {/* Redo Button */}
                        {lastUserMessage && !isLoading && (
                            <button
                                onClick={handleRedoMessage}
                                className="flex items-center justify-center w-10 h-12 bg-slate-500 hover:bg-slate-600 text-white rounded-lg transition-colors"
                                title="Redo last message"
                            >
                                <span>🔄</span>
                            </button>
                        )}

                        {/* Stop Button */}
                        {isLoading && (
                            <button
                                onClick={handleStopGeneration}
                                className="flex items-center justify-center w-10 h-12 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                                title="Stop generation"
                            >
                                <span>⏹️</span>
                            </button>
                        )}

                        {/* Send Button */}
                        <button
                            onClick={handleSendMessage}
                            disabled={!message.trim() || isLoading}
                            className="flex items-center justify-center w-12 h-12 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-600 rounded-lg transition-colors"
                        >
                            {isLoading ? (
                                <span className="animate-spin">⏳</span>
                            ) : (
                                <span>📤</span>
                            )}
                        </button>
                    </div>
                </div>

                <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                    Press Enter to send, Shift+Enter for new line
                </div>
            </div>
        </div>
    )
}
