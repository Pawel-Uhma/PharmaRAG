'use client';

import React from 'react';
import { ContextPanelState, Source, Chunk, Message } from '../types';

interface ContextPanelProps {
  state: ContextPanelState;
  onStateChange: (state: ContextPanelState) => void;
  currentMessage?: Message;
  sources?: Source[];
  chunks?: Chunk[];
}

export const ContextPanel: React.FC<ContextPanelProps> = ({
  state,
  onStateChange,
  currentMessage,
  sources = [],
  chunks = []
}) => {
  const tabs = [
    { id: 'sources', label: 'Sources', icon: '📚' },
    { id: 'chunks', label: 'Chunks', icon: '🔍' },
    { id: 'inspector', label: 'Inspector', icon: '🔬' },
    { id: 'history', label: 'History', icon: '⏱️' }
  ] as const;

  const handleTabClick = (tabId: typeof tabs[number]['id']) => {
    onStateChange({ ...state, activeTab: tabId });
  };

  const renderSourcesTab = () => (
    <div className="space-y-4">
      {sources.length === 0 ? (
        <div className="text-center py-8 text-muted">
          <p>No sources available</p>
        </div>
      ) : (
        sources.map((source, index) => (
          <div
            key={source.id}
            className={`p-4 rounded-theme border cursor-pointer transition-all duration-200 ${
              state.selectedSource?.id === source.id
                ? 'border-accent bg-accent/10'
                : 'border-ring/20 hover:border-ring/40 bg-panel'
            }`}
            onClick={() => onStateChange({ ...state, selectedSource: source })}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xs px-2 py-1 rounded-full bg-accent/10 text-accent">
                    {source.type}
                  </span>
                  {source.metadata?.relevance_score && (
                    <span className="text-xs text-muted">
                      Score: {Math.round(source.metadata.relevance_score * 100)}%
                    </span>
                  )}
                </div>
                <h4 className="font-medium text-primary mb-2">{source.title}</h4>
                {source.metadata?.h2 && (
                  <p className="text-sm text-primary mb-2">
                    <span className="text-muted">Heading:</span> {source.metadata.h2}
                  </p>
                )}
                {source.metadata?.chunk_content && (
                  <div className="mt-3 p-3 bg-muted/20 rounded-md border border-ring/20">
                    <p className="text-xs text-muted mb-1">Content used:</p>
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
                    className="text-sm text-accent hover:text-accent/80 underline break-all"
                  >
                    {source.url}
                  </a>
                )}
                {source.metadata?.author && (
                  <p className="text-sm text-muted mt-2">
                    By {source.metadata.author}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );

  const renderChunksTab = () => (
    <div className="space-y-4">
      {chunks.length === 0 ? (
        <div className="text-center py-8 text-muted">
          <p>No chunks available</p>
        </div>
      ) : (
        chunks.map((chunk) => (
          <div
            key={chunk.id}
            className={`p-4 rounded-theme border cursor-pointer transition-all duration-200 ${
              state.selectedChunk?.id === chunk.id
                ? 'border-accent bg-accent/10'
                : 'border-ring/20 hover:border-ring/40 bg-panel'
            }`}
            onClick={() => onStateChange({ ...state, selectedChunk: chunk })}
          >
            <div className="mb-3">
              <div className="flex items-center justify-between mb-2">
                {chunk.metadata?.relevance_score && (
                  <span className="text-xs px-2 py-1 rounded-full bg-success/10 text-success">
                    Score: {Math.round(chunk.metadata.relevance_score * 100)}%
                  </span>
                )}
                <span className="text-xs text-muted">
                  {chunk.metadata?.startIndex !== undefined && chunk.metadata?.endIndex !== undefined 
                    ? `${chunk.metadata.startIndex}-${chunk.metadata.endIndex}`
                    : 'Position: N/A'
                  }
                </span>
              </div>
            </div>
            <p className="text-sm text-primary leading-relaxed">
              {chunk.text}
            </p>
          </div>
        ))
      )}
    </div>
  );

  const renderInspectorTab = () => {
    const selectedSource = state.selectedSource;
    const selectedChunk = state.selectedChunk;

    return (
      <div className="space-y-6">
        {selectedSource && (
          <div className="p-4 rounded-theme border border-accent/20 bg-accent/5">
            <h4 className="font-medium text-primary mb-3">Selected Source</h4>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-muted">ID:</span> {selectedSource.id}
              </div>
              <div>
                <span className="text-muted">Type:</span> {selectedSource.type}
              </div>
              <div>
                <span className="text-muted">Relevance Score:</span> {selectedSource.metadata?.relevance_score ? Math.round(selectedSource.metadata.relevance_score * 100) + '%' : 'N/A'}
              </div>
              {selectedSource.metadata?.h1 && (
                <div>
                  <span className="text-muted">Name (H1):</span> {selectedSource.metadata.h1}
                </div>
              )}
              {selectedSource.metadata?.h2 && (
                <div>
                  <span className="text-muted">Heading (H2):</span> {selectedSource.metadata.h2}
                </div>
              )}
              {selectedSource.metadata?.chunk_content && (
                <div>
                  <span className="text-muted">Content Used:</span>
                  <div className="mt-2 p-2 bg-muted/20 rounded text-xs">
                    {selectedSource.metadata.chunk_content}
                  </div>
                </div>
              )}
              {selectedSource.metadata?.domain && (
                <div>
                  <span className="text-muted">Domain:</span> {selectedSource.metadata.domain}
                </div>
              )}
              {selectedSource.metadata?.date && (
                <div>
                  <span className="text-muted">Date:</span> {selectedSource.metadata.date}
                </div>
              )}
            </div>
          </div>
        )}

        {selectedChunk && (
          <div className="p-4 rounded-theme border border-success/20 bg-success/5">
            <h4 className="font-medium text-primary mb-3">Selected Chunk</h4>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-muted">ID:</span> {selectedChunk.id}
              </div>
              <div>
                <span className="text-muted">Source ID:</span> {selectedChunk.sourceId}
              </div>
              <div>
                <span className="text-muted">Relevance Score:</span> {selectedChunk.metadata?.relevance_score ? Math.round(selectedChunk.metadata.relevance_score * 100) + '%' : 'N/A'}
              </div>
              <div>
                <span className="text-muted">Position:</span> {selectedChunk.metadata?.startIndex !== undefined && selectedChunk.metadata?.endIndex !== undefined 
                  ? `${selectedChunk.metadata.startIndex}-${selectedChunk.metadata.endIndex}`
                  : 'N/A'
                }
              </div>
            </div>
          </div>
        )}

        {!selectedSource && !selectedChunk && (
          <div className="text-center py-8 text-muted">
            <p>Select a source or chunk to inspect</p>
          </div>
        )}
      </div>
    );
  };

  const renderHistoryTab = () => (
    <div className="space-y-4">
      {currentMessage?.metadata ? (
        <div className="p-4 rounded-theme border border-ring/20 bg-panel">
          <h4 className="font-medium text-primary mb-3">Response Metadata</h4>
          <div className="space-y-2 text-sm">
            {currentMessage.metadata.processingTime && (
              <div>
                <span className="text-muted">Processing Time:</span> {currentMessage.metadata.processingTime}ms
              </div>
            )}
            {currentMessage.metadata.documentMetadata && currentMessage.metadata.documentMetadata.length > 0 && (
              <div>
                <span className="text-muted">Documents Used:</span>
                <div className="mt-2 space-y-2">
                  {currentMessage.metadata.documentMetadata.map((doc, index) => (
                    <div key={index} className="pl-3 border-l-2 border-accent/20">
                      <div className="text-xs text-accent font-medium">{doc.h1}</div>
                      {doc.h2 && <div className="text-xs text-muted">{doc.h2}</div>}
                      <div className="text-xs text-muted">Score: {Math.round(doc.relevance_score * 100)}%</div>
                      {doc.chunk_content && (
                        <div className="mt-1 text-xs text-muted bg-muted/20 p-1 rounded">
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
          <p>No response metadata available</p>
        </div>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (state.activeTab) {
      case 'sources':
        return renderSourcesTab();
      case 'chunks':
        return renderChunksTab();
      case 'inspector':
        return renderInspectorTab();
      case 'history':
        return renderHistoryTab();
      default:
        return null;
    }
  };

  return (
    <div className="w-96 h-full bg-panel border-l border-ring/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-ring/20">
        <h2 className="text-lg font-semibold text-primary">Context</h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-ring/20">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors duration-200 ${
              state.activeTab === tab.id
                ? 'text-accent border-b-2 border-accent bg-accent/5'
                : 'text-muted hover:text-primary hover:bg-elevated'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {renderTabContent()}
      </div>
    </div>
  );
};
