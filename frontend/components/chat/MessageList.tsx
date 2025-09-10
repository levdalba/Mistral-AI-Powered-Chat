'use client'

/**
 * Message list component for displaying chat messages.
 *
 * Features:
 * - Auto-scrolling to latest message
 * - Message formatting with markdown support
 * - Typing indicator for AI responses
 * - Message metadata display
 * - Edit message functionality
 * - Copy message functionality
 * - Resend message functionality
 */

import { useEffect, useRef, useState } from 'react'

// Simple timestamp formatter without external dependencies
const formatTimestamp = (timestamp: Date | string) => {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays < 7) return `${diffDays} days ago`

    return date.toLocaleDateString()
}

interface Message {
    id: string
    content: string
    role: 'user' | 'assistant' | 'system'
    timestamp: Date | string
    metadata?: {
        tokens_used?: number
        model?: string
        processing_time?: number
        response_time_ms?: number
        model_used?: string
        finish_reason?: string
    }
}

interface MessageListProps {
    messages: Message[]
    isLoading: boolean
    onEditMessage?: (messageId: string, newContent: string) => void
    onResendMessage?: (messageId: string) => void
}

export default function MessageList({
    messages,
    isLoading = false,
    onEditMessage,
    onResendMessage,
}: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const messagesContainerRef = useRef<HTMLDivElement>(null)
    const [autoScroll, setAutoScroll] = useState(true)
    const [isAtBottom, setIsAtBottom] = useState(true)
    const [editingMessageId, setEditingMessageId] = useState<string | null>(
        null
    )
    const [editText, setEditText] = useState('')
    const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)

    // Scroll to bottom when new messages arrive or when auto-scroll is enabled
    useEffect(() => {
        if (autoScroll && messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
        }
    }, [messages, autoScroll])

    // Check if user is at the bottom of the chat
    const handleScroll = () => {
        if (messagesContainerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } =
                messagesContainerRef.current
            const isBottom = scrollTop + clientHeight >= scrollHeight - 10
            setIsAtBottom(isBottom)
            setAutoScroll(isBottom)
        }
    }

    const scrollToBottom = () => {
        setAutoScroll(true)
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const scrollToTop = () => {
        messagesContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const formatTimestampLocal = (timestamp: Date | string) => {
        const date =
            typeof timestamp === 'string' ? new Date(timestamp) : timestamp
        return formatTimestamp(date)
    }

    const handleEditStart = (messageId: string, content: string) => {
        setEditingMessageId(messageId)
        setEditText(content)
    }

    const handleEditSave = () => {
        if (editingMessageId && onEditMessage && editText.trim()) {
            onEditMessage(editingMessageId, editText.trim())
            setEditingMessageId(null)
            setEditText('')
        }
    }

    const handleEditCancel = () => {
        setEditingMessageId(null)
        setEditText('')
    }

    const handleCopyMessage = async (content: string, messageId: string) => {
        try {
            await navigator.clipboard.writeText(content)
            setCopiedMessageId(messageId)
            setTimeout(() => setCopiedMessageId(null), 2000)
        } catch (err) {
            console.error('Failed to copy message:', err)
        }
    }

    const handleResend = (messageId: string) => {
        if (onResendMessage) {
            onResendMessage(messageId)
        }
    }

    if (messages.length === 0 && !isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-center text-gray-500 dark:text-gray-400">
                    <span className="text-6xl">🤖</span>
                    <p className="text-lg font-medium mb-2 mt-4">
                        Start a conversation
                    </p>
                    <p className="text-sm">
                        Send a message to begin chatting with Mistral AI
                    </p>
                </div>
            </div>
        )
    }

    return (
        <div className="flex-1 flex flex-col relative h-full">
            {/* Messages Container with proper scrolling */}
            <div
                ref={messagesContainerRef}
                className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4 h-0 min-h-0 scroll-smooth"
                onScroll={handleScroll}
                style={{
                    scrollbarWidth: 'thin',
                    scrollbarColor: '#cbd5e1 transparent'
                }}
            >
                <div className="space-y-6 max-w-4xl mx-auto">
                    {messages
                        .filter((message) => message.role !== 'system') // Don't show system messages
                        .map((message) => (
                            <div
                                key={message.id}
                                className={`group flex gap-4 ${
                                    message.role === 'user'
                                        ? 'justify-end'
                                        : 'justify-start'
                                }`}
                            >
                                {message.role === 'assistant' && (
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white">
                                            🤖
                                        </div>
                                    </div>
                                )}

                                <div
                                    className={`relative max-w-[80%] ${
                                        message.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-lg px-4 py-3'
                                            : 'bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3'
                                    }`}
                                >
                                    {/* Message Actions - Show on hover */}
                                    <div className="absolute -top-8 right-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex gap-1 bg-white dark:bg-gray-700 rounded-md shadow-lg border dark:border-gray-600 p-1">
                                        <button
                                            onClick={() =>
                                                handleCopyMessage(
                                                    message.content,
                                                    message.id
                                                )
                                            }
                                            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-300"
                                            title="Copy message"
                                        >
                                            {copiedMessageId === message.id
                                                ? '✅'
                                                : '📋'}
                                        </button>

                                        {message.role === 'user' &&
                                            onEditMessage && (
                                                <button
                                                    onClick={() =>
                                                        handleEditStart(
                                                            message.id,
                                                            message.content
                                                        )
                                                    }
                                                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-300"
                                                    title="Edit message"
                                                >
                                                    ✏️
                                                </button>
                                            )}

                                        {message.role === 'user' &&
                                            onResendMessage && (
                                                <button
                                                    onClick={() =>
                                                        handleResend(message.id)
                                                    }
                                                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-300"
                                                    title="Resend message"
                                                >
                                                    🔄
                                                </button>
                                            )}
                                    </div>

                                    {/* Message Content */}
                                    {editingMessageId === message.id ? (
                                        <div className="space-y-3">
                                            <textarea
                                                value={editText}
                                                onChange={(e) =>
                                                    setEditText(e.target.value)
                                                }
                                                className="w-full p-2 border rounded-md resize-none text-gray-900 bg-white border-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                rows={3}
                                                autoFocus
                                            />
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={handleEditSave}
                                                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                                                >
                                                    Save
                                                </button>
                                                <button
                                                    onClick={handleEditCancel}
                                                    className="px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400 dark:bg-gray-600 dark:text-white dark:hover:bg-gray-500"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="whitespace-pre-wrap break-words">
                                            {message.content}
                                        </div>
                                    )}

                                    {/* Message Metadata */}
                                    <div className="flex items-center gap-2 mt-2 text-xs opacity-60">
                                        <span>🕒</span>
                                        <span>
                                            {formatTimestampLocal(
                                                message.timestamp
                                            )}
                                        </span>
                                        {message.metadata && (
                                            <>
                                                {message.metadata
                                                    .tokens_used && (
                                                    <span className="flex items-center gap-1">
                                                        •
                                                        <span>
                                                            {
                                                                message.metadata
                                                                    .tokens_used
                                                            }{' '}
                                                            tokens
                                                        </span>
                                                    </span>
                                                )}
                                                {message.metadata.model && (
                                                    <span className="flex items-center gap-1">
                                                        •
                                                        <span>
                                                            {
                                                                message.metadata
                                                                    .model
                                                            }
                                                        </span>
                                                    </span>
                                                )}
                                                {message.metadata
                                                    .processing_time && (
                                                    <span className="flex items-center gap-1">
                                                        •
                                                        <span>
                                                            {
                                                                message.metadata
                                                                    .processing_time
                                                            }
                                                            ms
                                                        </span>
                                                    </span>
                                                )}
                                            </>
                                        )}
                                    </div>
                                </div>

                                {message.role === 'user' && (
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-white">
                                            👤
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}

                    {/* Loading indicator */}
                    {isLoading && (
                        <div className="flex gap-4 justify-start">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white">
                                    🤖
                                </div>
                            </div>
                            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3">
                                <div className="flex space-x-1">
                                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                                    <div
                                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                                        style={{ animationDelay: '0.1s' }}
                                    ></div>
                                    <div
                                        className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                                        style={{ animationDelay: '0.2s' }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Scroll anchor */}
                <div ref={messagesEndRef} />
            </div>

            {/* Scroll Controls */}
            {!isAtBottom && (
                <button
                    onClick={scrollToBottom}
                    className="absolute bottom-4 right-4 bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-full shadow-lg transition-colors z-10"
                    title="Scroll to bottom"
                >
                    ⬇️
                </button>
            )}

            {messages.length > 5 && (
                <button
                    onClick={scrollToTop}
                    className="absolute top-4 right-4 bg-gray-600 hover:bg-gray-700 text-white p-2 rounded-full shadow-lg transition-colors z-10"
                    title="Scroll to top"
                >
                    ⬆️
                </button>
            )}
        </div>
    )
}
