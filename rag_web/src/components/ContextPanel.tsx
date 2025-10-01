'use client';

import React from 'react';
import { ContextPanelState, Source, Chunk, Message } from '../types';

interface ContextPanelProps {
  state: ContextPanelState;
  onStateChange: (state: ContextPanelState) => void;
  currentMessage?: Message;
  allMessages?: Message[];
  sources?: Source[];
  onSourceClick?: (source: Source) => void;
}

export const ContextPanel: React.FC<ContextPanelProps> = ({
  state,
  onStateChange,
  currentMessage,
  allMessages = [],
  sources = [],
  onSourceClick
}) => {
  const tabs = [
    { id: 'sources', label: 'Źródła', icon: '📚' },
    { id: 'history', label: 'Historia', icon: '⏱️' }
  ] as const;

  const handleTabClick = (tabId: typeof tabs[number]['id']) => {
    onStateChange({ ...state, activeTab: tabId });
  };

  const renderSourcesTab = () => (
    <div className="space-y-4">
      {sources.length === 0 ? (
        <div className="text-center py-8 text-muted">
          <p>Brak dostępnych źródeł</p>
        </div>
      ) : (
        sources.map((source, index) => (
          <div
            key={source.id}
            className={`p-4 rounded-theme border cursor-pointer transition-all duration-200 ${
              state.selectedSource?.id === source.id
                ? 'border-accent bg-accent-light shadow-theme'
                : 'border-accent-light hover:border-accent bg-panel hover:shadow-theme'
            }`}
            onClick={() => {
              onStateChange({ ...state, selectedSource: source });
              onSourceClick?.(source);
            }}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xs px-2 py-1 rounded-full bg-accent-light text-accent border border-accent">
                    {source.type}
                  </span>
                  {source.metadata?.relevance_score && (
                    <span className="text-xs text-accent/80">
                      Wynik: {Math.round(source.metadata.relevance_score * 100)}%
                    </span>
                  )}
                </div>
                <h4 className="font-medium text-primary mb-2">{source.title}</h4>
                {source.metadata?.h2 && (
                  <p className="text-sm text-primary mb-2">
                    <span className="text-accent/80">Nagłówek:</span> {source.metadata.h2}
                  </p>
                )}
                {source.metadata?.chunk_content && (
                  <div className="mt-3 p-3 bg-accent-bg rounded-md border border-accent-light">
                    <p className="text-xs text-accent/80 mb-1">Użyta zawartość:</p>
                    <p className="text-sm text-primary leading-relaxed">
                      {source.metadata.chunk_content}
                    </p>
                  </div>
                )}
                {source.url && (
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-accent hover:text-accent-hover underline break-all"
                  >
                    {source.url}
                  </a>
                )}
                {source.metadata?.author && (
                  <p className="text-sm text-accent/80 mt-2">
                    Autor: {source.metadata.author}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );

  const renderHistoryTab = () => {
    // Get all messages with metadata (bot responses)
    const messagesWithMetadata = allMessages.filter(msg => !msg.isUser && msg.metadata?.documentMetadata);
    
    if (messagesWithMetadata.length === 0) {
      return (
        <div className="text-center py-8 text-muted">
          <p>Brak dostępnych metadanych odpowiedzi</p>
        </div>
      );
    }

    // Calculate total chunks used across all messages
    const totalChunks = messagesWithMetadata.reduce((total, msg) => 
      total + (msg.metadata?.documentMetadata?.length || 0), 0
    );

    return (
      <div className="space-y-4">
        {/* Summary */}
        <div className="p-3 rounded-theme border border-accent bg-accent-light">
          <div className="text-sm text-accent font-medium">
            Historia kontekstu: {messagesWithMetadata.length} odpowiedzi, {totalChunks} fragmentów dokumentów
          </div>
        </div>
        
        {messagesWithMetadata.map((message, messageIndex) => (
          <div key={message.id} className="p-4 rounded-theme border border-accent-light bg-accent-bg shadow-theme">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-accent">Odpowiedź #{messagesWithMetadata.length - messageIndex}</h4>
              <span className="text-xs text-accent/60">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
            
            <div className="space-y-2 text-sm">
              {message.metadata?.processingTime && (
                <div>
                  <span className="text-accent/80">Czas przetwarzania:</span> {message.metadata.processingTime}ms
                </div>
              )}
              
              {message.metadata?.documentMetadata && message.metadata.documentMetadata.length > 0 && (
                <div>
                  <span className="text-accent/80">Użyte dokumenty:</span>
                  <div className="mt-2 space-y-2">
                    {message.metadata.documentMetadata.map((doc, docIndex) => (
                      <div key={`${message.id}-${docIndex}`} className="pl-3 border-l-2 border-accent">
                        <div className="text-xs text-accent font-medium">{doc.h1}</div>
                        {doc.h2 && <div className="text-xs text-accent/80">{doc.h2}</div>}
                        <div className="text-xs text-accent/80">Wynik: {Math.round(doc.relevance_score * 100)}%</div>
                        {doc.chunk_content && (
                          <div className="mt-1 text-xs text-accent/80 bg-accent-light/50 p-2 rounded">
                            {doc.chunk_content}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderTabContent = () => {
    switch (state.activeTab) {
      case 'sources':
        return renderSourcesTab();
      case 'history':
        return renderHistoryTab();
      default:
        return null;
    }
  };

  return (
    <>
      {/* Mobile Overlay - only show when panel is open */}
      {state.isOpen && <div className="lg:hidden fixed inset-0 bg-black/50 z-40" onClick={() => onStateChange({ ...state, isOpen: false })} />}
      
      {/* Context Panel */}
      <div className={`w-full lg:w-96 h-full bg-panel border-l border-accent-light flex flex-col shadow-theme min-h-0 fixed lg:relative right-0 top-0 z-50 lg:z-auto transition-transform duration-300 ease-in-out ${
        state.isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'
      }`}>
        {/* Header */}
        <div className="flex-shrink-0 p-3 sm:p-4 border-b border-accent-light flex items-center justify-between">
          <h2 className="text-lg font-semibold text-accent">Kontekst</h2>
          <button
            onClick={() => onStateChange({ ...state, isOpen: false })}
            className="lg:hidden p-1 rounded-theme text-muted hover:text-accent hover:bg-accent-light transition-all duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex-shrink-0 flex border-b border-accent-light">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={`flex-1 px-3 sm:px-4 py-2 sm:py-3 text-sm font-medium transition-colors duration-200 ${
                state.activeTab === tab.id
                  ? 'text-accent border-b-2 border-accent bg-accent-light'
                  : 'text-muted hover:text-accent hover:bg-accent-light/50'
              }`}
            >
              <span className="mr-1 sm:mr-2">{tab.icon}</span>
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 min-h-0">
          {renderTabContent()}
        </div>
      </div>
    </>
  );
};
