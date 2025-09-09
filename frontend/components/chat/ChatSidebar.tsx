'use client'

/**
 * Chat sidebar component for managing conversations.
 *
 * Features:
 * - New chat button
 * - Conversation history
 * - Delete conversations
 * - Switch between conversations
 */

import { useState } from 'react'
import {
    Plus,
    MessageSquare,
    Trash2,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react'
import { useChatStore } from '@/lib/stores/chatStore'
import { formatDistanceToNow } from 'date-fns'

interface ChatSidebarProps {
    isOpen: boolean
    onToggle: () => void
}

export default function ChatSidebar({ isOpen, onToggle }: ChatSidebarProps) {
    const {
        conversations,
        currentConversationId,
        createNewConversation,
        loadConversation,
        deleteConversation,
        clearCurrentChat,
    } = useChatStore()

    const handleNewChat = () => {
        clearCurrentChat()
        createNewConversation()
    }

    const handleLoadConversation = (conversationId: string) => {
        loadConversation(conversationId)
    }

    const handleDeleteConversation = (
        conversationId: string,
        e: React.MouseEvent
    ) => {
        e.stopPropagation()
        if (confirm('Are you sure you want to delete this conversation?')) {
            deleteConversation(conversationId)
        }
    }

    const formatDate = (dateString: string) => {
        try {
            return formatDistanceToNow(new Date(dateString), {
                addSuffix: true,
            })
        } catch {
            return 'Unknown'
        }
    }

    return (
        <>
            {/* Toggle Button */}
            <button
                onClick={onToggle}
                className={`fixed top-4 left-4 z-50 p-2 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors ${
                    isOpen ? 'translate-x-80' : 'translate-x-0'
                }`}
            >
                {isOpen ? (
                    <ChevronLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                ) : (
                    <ChevronRight className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                )}
            </button>

            {/* Sidebar */}
            <div
                className={`fixed top-0 left-0 h-full w-80 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 transform transition-transform duration-300 ease-in-out z-40 ${
                    isOpen ? 'translate-x-0' : '-translate-x-full'
                }`}
            >
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <button
                            onClick={handleNewChat}
                            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            <span>New Chat</span>
                        </button>
                    </div>

                    {/* Conversations List */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-2">
                        <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3">
                            Chat History
                        </h3>

                        {conversations.length === 0 ? (
                            <div className="text-center text-slate-400 dark:text-slate-500 py-8">
                                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p className="text-sm">No conversations yet</p>
                                <p className="text-xs">
                                    Start a new chat to begin
                                </p>
                            </div>
                        ) : (
                            conversations.map((conversation) => (
                                <div
                                    key={conversation.id}
                                    onClick={() =>
                                        handleLoadConversation(conversation.id)
                                    }
                                    className={`group p-3 rounded-lg cursor-pointer transition-colors ${
                                        currentConversationId ===
                                        conversation.id
                                            ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                                            : 'hover:bg-slate-50 dark:hover:bg-slate-800 border border-transparent'
                                    }`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1 min-w-0">
                                            <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                                                {conversation.title ||
                                                    'New Conversation'}
                                            </h4>
                                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                                {conversation.messages.length}{' '}
                                                messages •{' '}
                                                {formatDate(
                                                    conversation.updated_at
                                                )}
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) =>
                                                handleDeleteConversation(
                                                    conversation.id,
                                                    e
                                                )
                                            }
                                            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded transition-all"
                                        >
                                            <Trash2 className="w-3 h-3 text-red-500" />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Footer */}
                    <div className="p-4 border-t border-slate-200 dark:border-slate-700">
                        <div className="text-xs text-slate-400 dark:text-slate-500 text-center">
                            {conversations.length} conversation
                            {conversations.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
            </div>

            {/* Overlay */}
            {isOpen && (
                <div
                    onClick={onToggle}
                    className="fixed inset-0 bg-black/20 z-30"
                />
            )}
        </>
    )
}
