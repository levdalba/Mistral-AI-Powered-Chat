'use client'

import React from 'react'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: Date | string
}

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  onEditMessage?: (messageId: string, newContent: string) => void
  onResendMessage?: (messageId: string) => void
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  return (
    <div className="flex-1 p-4">
      <div className="space-y-4">
        {messages.filter(m => m.role !== 'system').map((message) => (
          <div key={message.id} className={`p-3 rounded-lg ${
            message.role === 'user' ? 'bg-blue-500 text-white ml-12' : 'bg-gray-100 mr-12'
          }`}>
            {message.content}
          </div>
        ))}
        {isLoading && (
          <div className="bg-gray-100 p-3 rounded-lg mr-12">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageList
