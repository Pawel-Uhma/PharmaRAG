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
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            message.isUser 
              ? 'bg-accent text-white' 
              : 'bg-panel border border-ring/20 text-primary'
          }`}>
            {message.isUser ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            )}
          </div>

          {/* Message Content */}
          <div className={`flex-1 ${message.isUser ? 'text-right' : ''}`}>
            <div className={`inline-block p-4 rounded-theme shadow-theme ${
              message.isUser
                ? 'bg-accent text-white'
                : 'bg-panel border border-ring/20 text-primary'
            }`}>
              <div className="prose prose-sm max-w-none">
                {renderTextWithCitations(message.text, message.sources)}
              </div>
              
              {/* Message Metadata */}
              <div className={`mt-3 text-xs opacity-70 ${message.isUser ? 'text-white' : 'text-muted'}`}>
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
