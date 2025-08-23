'use client';

import React from 'react';
import { ContextPanelState, Source, Chunk, Message } from '../types';

interface ContextPanelProps {
  state: ContextPanelState;
  onStateChange: (state: ContextPanelState) => void;
  currentMessage?: Message;
  sources?: Source[];
  onSourceClick?: (source: Source) => void;
}

export const ContextPanel: React.FC<ContextPanelProps> = ({
  state,
  onStateChange,
  currentMessage,
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

  const renderHistoryTab = () => (
    <div className="space-y-4">
      {currentMessage?.metadata ? (
        <div className="p-4 rounded-theme border border-accent-light bg-accent-bg shadow-theme">
          <h4 className="font-medium text-accent mb-3">Metadane odpowiedzi</h4>
          <div className="space-y-2 text-sm">
            {currentMessage.metadata.processingTime && (
              <div>
                <span className="text-accent/80">Czas przetwarzania:</span> {currentMessage.metadata.processingTime}ms
              </div>
            )}
            {currentMessage.metadata.documentMetadata && currentMessage.metadata.documentMetadata.length > 0 && (
              <div>
                <span className="text-accent/80">Użyte dokumenty:</span>
                <div className="mt-2 space-y-2">
                  {currentMessage.metadata.documentMetadata.map((doc, index) => (
                    <div key={index} className="pl-3 border-l-2 border-accent">
                      <div className="text-xs text-accent font-medium">{doc.h1}</div>
                      {doc.h2 && <div className="text-xs text-accent/80">{doc.h2}</div>}
                      <div className="text-xs text-accent/80">Wynik: {Math.round(doc.relevance_score * 100)}%</div>
                      {doc.chunk_content && (
                        <div className="mt-1 text-xs text-accent/80 bg-accent-light/50 p-1 rounded">
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
      ) : (
        <div className="text-center py-8 text-muted">
          <p>Brak dostępnych metadanych odpowiedzi</p>
        </div>
      )}
    </div>
  );

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
    <div className="w-96 h-full bg-panel border-l border-accent-light flex flex-col shadow-theme min-h-0">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-accent-light">
        <h2 className="text-lg font-semibold text-accent">Kontekst</h2>
      </div>

      {/* Tabs */}
      <div className="flex-shrink-0 flex border-b border-accent-light">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors duration-200 ${
              state.activeTab === tab.id
                ? 'text-accent border-b-2 border-accent bg-accent-light'
                : 'text-muted hover:text-accent hover:bg-accent-light/50'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4 min-h-0">
        {renderTabContent()}
      </div>
    </div>
  );
};
