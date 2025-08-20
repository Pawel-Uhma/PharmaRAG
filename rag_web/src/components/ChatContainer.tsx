'use client';

import React, { useRef, useEffect } from 'react';
import { Message as MessageType, Source } from '../types';
import { Message } from './Message';
import { ChatInput } from './ChatInput';
import { LoadingIndicator } from './LoadingIndicator';

interface ChatContainerProps {
  messages: MessageType[];
  inputText: string;
  setInputText: (text: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  isLoading: boolean;
  onSourceClick?: (source: Source) => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  inputText,
  setInputText,
  onSend,
  onKeyPress,
  isLoading,
  onSourceClick
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col h-full bg-primary">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-muted">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-panel border border-ring/20 flex items-center justify-center">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-primary mb-2">Start a conversation</h3>
              <p className="text-muted">Ask me anything about pharmaceuticals, medications, or health topics.</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <Message
                key={message.id}
                message={message}
                onSourceClick={onSourceClick}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-panel border border-ring/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="bg-panel border border-ring/20 rounded-theme p-4 shadow-theme">
                    <LoadingIndicator />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-ring/20 bg-panel p-4">
        <ChatInput
          value={inputText}
          onChange={setInputText}
          onSend={onSend}
          onKeyPress={onKeyPress}
          disabled={isLoading}
          placeholder="Ask me anything about pharmaceuticals..."
        />
      </div>
    </div>
  );
};
