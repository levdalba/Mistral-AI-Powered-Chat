'use client'

/**
 * Main chat page component.
 *
 * This is the primary chat interface where users interact with Mistral AI.
 * Features include real-time messaging, conversation history, and document upload.
 */

import { useState, useEffect } from 'react'
import ChatInterface from '@/components/chat/ChatInterface'
import ChatSidebar from '@/components/chat/ChatSidebar'
import ConnectionStatus from '@/components/ConnectionStatus'
import { useChatStore } from '@/lib/stores/chatStore'

export default function HomePage() {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const { currentConversationId, conversations, createNewConversation } = useChatStore()

    // Automatically create a new conversation when the page loads if none exists
    useEffect(() => {
        if (!currentConversationId && conversations.length === 0) {
            createNewConversation()
        }
    }, [currentConversationId, conversations.length, createNewConversation])

    return (
        <>
            <ChatSidebar
                isOpen={sidebarOpen}
                onToggle={() => setSidebarOpen(!sidebarOpen)}
            />

            <main
                className={`min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 transition-all duration-300 flex flex-col ${
                    sidebarOpen ? 'ml-80' : 'ml-0'
                }`}
            >
                <div className="container mx-auto px-4 py-4 max-w-6xl flex-1 flex flex-col">
                    <header className="text-center mb-6">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex-1"></div>
                            <div className="flex-1 text-center">
                                <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
                                    Mistral AI Chat
                                </h1>
                                <p className="text-slate-600 dark:text-slate-400">
                                    Intelligent conversations powered by Mistral
                                    AI
                                </p>
                            </div>
                            <div className="flex-1 flex justify-end">
                                <ConnectionStatus />
                            </div>
                        </div>
                    </header>

                    <div className="flex-1 min-h-0">
                        <ChatInterface className="h-full" />
                    </div>
                </div>
            </main>
        </>
    )
}
