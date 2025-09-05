'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Message as MessageType, Source } from '../types';
import { Message } from './Message';
import { ChatInput } from './ChatInput';
import { LoadingIndicator } from './LoadingIndicator';
import { SuggestedQuestions } from './SuggestedQuestions';
import { getRandomQuestions } from '../utils/suggestedQuestions';

interface ChatContainerProps {
  messages: MessageType[];
  inputText: string;
  setInputText: (text: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  isLoading: boolean;
  onSourceClick?: (source: Source) => void;
  onToggleContextPanel?: () => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  inputText,
  setInputText,
  onSend,
  onKeyPress,
  isLoading,
  onSourceClick,
  onToggleContextPanel
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [autoSendQuestion, setAutoSendQuestion] = useState<string | null>(null);

  // Initialize suggested questions when component mounts
  useEffect(() => {
    if (messages.length === 0) {
      const questions = getRandomQuestions(5);
      setSuggestedQuestions(questions);
    }
  }, [messages.length]);

  // Auto-send when a suggested question is set
  useEffect(() => {
    if (autoSendQuestion && inputText === autoSendQuestion) {
      setAutoSendQuestion(null);
      setTimeout(() => {
        onSend();
      }, 100);
    }
  }, [inputText, autoSendQuestion, onSend]);

  const handleQuestionClick = (question: string) => {
    // Clear suggested questions when a question is clicked
    setSuggestedQuestions([]);
    
    // Set the auto-send flag and input text
    setAutoSendQuestion(question);
    setInputText(question);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-primary">
      {/* Mobile Context Panel Toggle */}
      <div className="lg:hidden flex-shrink-0 p-3 border-b border-accent-light bg-panel">
        <button
          onClick={onToggleContextPanel}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-accent bg-accent-light border border-accent rounded-theme hover:bg-accent hover:text-white transition-all duration-200"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h2m0-2h10a2 2 0 002-2V7a2 2 0 00-2-2H9m0 2V5a2 2 0 012-2h2a2 2 0 012 2v2" />
          </svg>
          <span>Pokaż kontekst</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4 min-h-0">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-muted px-4">
              <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 rounded-theme bg-accent-light flex items-center justify-center shadow-theme">
                <img 
                  src="/bot.png" 
                  alt="Asystent AI" 
                  className="w-6 h-6 sm:w-8 sm:h-8 rounded-full object-cover"
                />
              </div>
              <h3 className="text-base sm:text-lg font-medium text-primary mb-2">Rozpocznij rozmowę</h3>
              <p className="text-sm sm:text-base text-muted">Zadaj mi pytanie o leki.</p>
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
                <div className="flex items-start space-x-2 sm:space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 sm:w-8 sm:h-8 rounded-theme bg-accent-light flex items-center justify-center shadow-theme">
                    <img 
                      src="/bot.png" 
                      alt="Asystent AI" 
                      className="w-4 h-4 sm:w-5 sm:h-5 rounded-full object-cover"
                    />
                  </div>
                  <div className="bg-panel border border-accent-light rounded-theme p-3 sm:p-4 shadow-theme">
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
      <div className="flex-shrink-0 border-t border-accent-light bg-panel p-3 sm:p-4 shadow-theme">
        {/* Show suggested questions only when there are no messages and not on mobile */}
        {messages.length === 0 && (
          <div className="hidden sm:block">
            <SuggestedQuestions
              questions={suggestedQuestions}
              onQuestionClick={handleQuestionClick}
            />
          </div>
        )}
        <ChatInput
          value={inputText}
          onChange={setInputText}
          onSend={onSend}
          onKeyPress={onKeyPress}
          disabled={isLoading}
          placeholder="Zadaj mi pytanie o farmaceutyki..."
        />
      </div>
    </div>
  );
};
