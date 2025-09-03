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
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [autoSendQuestion, setAutoSendQuestion] = useState<string | null>(null);

  // Initialize suggested questions when component mounts
  useEffect(() => {
    if (messages.length === 0) {
      const questions = getRandomQuestions(3);
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
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-0">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-muted">
              <div className="w-16 h-16 mx-auto mb-4 rounded-theme bg-accent-light flex items-center justify-center shadow-theme">
                <img 
                  src="/bot.png" 
                  alt="Asystent AI" 
                  className="w-8 h-8 rounded-full object-cover"
                />
              </div>
              <h3 className="text-lg font-medium text-primary mb-2">Rozpocznij rozmowę</h3>
              <p className="text-muted">Zadaj mi pytanie o leki.</p>
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
                  <div className="flex-shrink-0 w-8 h-8 rounded-theme bg-accent-light flex items-center justify-center shadow-theme">
                    <img 
                      src="/bot.png" 
                      alt="Asystent AI" 
                      className="w-5 h-5 rounded-full object-cover"
                    />
                  </div>
                  <div className="bg-panel border border-accent-light rounded-theme p-4 shadow-theme">
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
      <div className="flex-shrink-0 border-t border-accent-light bg-panel p-4 shadow-theme">

        
        {/* Show suggested questions only when there are no messages */}
        {messages.length === 0 && (
          <SuggestedQuestions
            questions={suggestedQuestions}
            onQuestionClick={handleQuestionClick}
          />
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
