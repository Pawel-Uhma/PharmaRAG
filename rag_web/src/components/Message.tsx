'use client';

import React from 'react';
import { Message as MessageType, Source } from '../types';

interface MessageProps {
  message: MessageType;
  onSourceClick?: (source: Source) => void;
}

export const Message: React.FC<MessageProps> = ({ message, onSourceClick }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderTextWithCitations = (text: string, sources?: Source[]) => {
    if (!sources || sources.length === 0) {
      return <span>{text}</span>;
    }

    // Simple citation replacement - in a real app, you'd want more sophisticated parsing
    const parts = text.split(/(\[\d+\])/);
    
    return parts.map((part, index) => {
      const citationMatch = part.match(/\[(\d+)\]/);
      if (citationMatch) {
        const sourceIndex = parseInt(citationMatch[1]) - 1;
        const source = sources[sourceIndex];
        if (source) {
          return (
            <button
              key={index}
              onClick={() => onSourceClick?.(source)}
              className="inline-flex items-center px-2 py-1 mx-1 text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 rounded-md transition-colors duration-200 cursor-pointer border border-accent/20 hover:border-accent/40"
              title={`Source: ${source.title}`}
            >
              [{citationMatch[1]}]
              <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </button>
          );
        }
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`max-w-3xl ${message.isUser ? 'order-2' : 'order-1'}`}>
        <div className={`flex items-start space-x-3 ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          {/* Avatar - only for bot messages */}
          {!message.isUser && (
            <div className="flex-shrink-0 w-16 h-16 rounded-theme flex items-center justify-center bg-accent-light shadow-theme">
              <img 
                src="/bot.png" 
                alt="Asystent AI" 
                className="w-12 h-12 rounded-full object-cover"
              />
            </div>
          )}

          {/* Message Content */}
          <div className={`flex-1 ${message.isUser ? 'text-right' : ''}`}>
            <div className={`inline-block p-4 rounded-theme shadow-theme ${
              message.isUser
                ? 'bg-gradient-to-br from-accent to-accent-dark text-white shadow-lg'
                : 'bg-panel border border-accent-light text-primary'
            }`}>
              <div className="prose prose-sm max-w-none">
                {renderTextWithCitations(message.text, message.sources)}
              </div>
              
              {/* Message Metadata */}
              <div className={`mt-3 text-xs opacity-70 ${message.isUser ? 'text-white/80' : 'text-muted'}`}>
                <span>{formatTime(message.timestamp)}</span>
                {message.metadata?.processingTime && (
                  <span className="ml-3">
                    {message.metadata.processingTime}ms
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
