'use client';

import React from 'react';

interface DocumentFile {
  name: string;
  filename: string;
  content?: string;
}

interface DocumentViewerProps {
  document?: DocumentFile;
  chunkToHighlight?: string;
  onBackToLibrary?: () => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ document, chunkToHighlight, onBackToLibrary }) => {
  const contentRef = React.useRef<HTMLDivElement>(null);

  // Debug: Log received props
  console.log('DocumentViewer received props:', { document, chunkToHighlight, onBackToLibrary });

  // Scroll to highlighted text when chunkToHighlight changes
  React.useEffect(() => {
    if (chunkToHighlight && contentRef.current) {
      const highlightedElement = contentRef.current.querySelector('mark');
      if (highlightedElement) {
        highlightedElement.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }
  }, [chunkToHighlight]);

  if (!document) {
    return (
      <div className="flex-1 bg-panel flex items-center justify-center">
        <div className="text-center text-muted">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-lg font-medium text-primary">Wybierz dokument do wyświetlenia</p>
          <p className="text-sm">Wybierz lek z biblioteki aby zobaczyć jego szczegóły</p>
        </div>
      </div>
    );
  }

  // Function to highlight text if it matches chunkToHighlight
  const highlightText = (text: string) => {
    if (!chunkToHighlight || !text.includes(chunkToHighlight)) {
      return text;
    }
    
    const parts = text.split(chunkToHighlight);
    return parts.map((part, index) => (
      <React.Fragment key={index}>
        {part}
        {index < parts.length - 1 && (
          <mark className="bg-accent-light text-accent px-1 rounded border border-accent">
            {chunkToHighlight}
          </mark>
        )}
      </React.Fragment>
    ));
  };

  // Simple markdown-like rendering for the content
  const renderContent = (content: string) => {
    if (!content) {
      return (
        <div className="text-center py-8 text-muted">
          <p>Zawartość dokumentu niedostępna</p>
        </div>
      );
    }

    // Split content into lines and render with basic markdown support
    const lines = content.split('\n');
    
    return lines.map((line, index) => {
      // Handle headers
      if (line.startsWith('# ')) {
        return (
          <h1 key={index} className="text-2xl font-bold text-accent mb-4 mt-6 first:mt-0">
            {line.substring(2)}
          </h1>
        );
      }
      
      if (line.startsWith('## ')) {
        return (
          <h2 key={index} className="text-xl font-semibold text-accent mb-3 mt-5">
            {line.substring(3)}
          </h2>
        );
      }
      
      if (line.startsWith('### ')) {
        return (
          <h3 key={index} className="text-lg font-medium text-accent mb-2 mt-4">
            {line.substring(4)}
          </h3>
        );
      }
      
      // Handle tables
      if (line.includes('|') && line.includes('---')) {
        return null; // Skip separator lines
      }
      
      if (line.includes('|') && !line.startsWith('|')) {
        const cells = line.split('|').filter(cell => cell.trim());
        return (
          <div key={index} className="flex space-x-4 py-1">
            {cells.map((cell, cellIndex) => (
              <span key={cellIndex} className="text-sm text-primary flex-1">
                {highlightText(cell.trim())}
              </span>
            ))}
          </div>
        );
      }
      
      if (line.includes('|') && line.startsWith('|')) {
        const cells = line.split('|').filter(cell => cell.trim());
        return (
          <div key={index} className="flex space-x-4 py-1 bg-accent-bg rounded px-2 border border-accent-light">
            {cells.map((cell, cellIndex) => (
              <span key={cellIndex} className="text-sm text-primary flex-1 font-medium">
                {highlightText(cell.trim())}
              </span>
            ))}
          </div>
        );
      }
      
      // Handle bullet points
      if (line.trim().startsWith('•')) {
        return (
          <div key={index} className="flex items-start py-1">
            <span className="text-accent mr-2 mt-1">•</span>
            <span className="text-sm text-primary flex-1">{highlightText(line.trim().substring(1).trim())}</span>
          </div>
        );
      }
      
      // Handle numbered lists
      if (/^\d+\./.test(line.trim())) {
        return (
          <div key={index} className="flex items-start py-1">
            <span className="text-accent mr-2 mt-1 text-sm font-medium">
              {line.trim().match(/^\d+\./)?.[0]}
            </span>
            <span className="text-sm text-primary flex-1">
              {highlightText(line.trim().replace(/^\d+\./, '').trim())}
            </span>
          </div>
        );
      }
      
      // Handle empty lines
      if (line.trim() === '') {
        return <div key={index} className="h-2" />;
      }
      
      // Regular text
      return (
        <p key={index} className="text-sm text-primary leading-relaxed py-1">
          {highlightText(line)}
        </p>
      );
    });
  };

  return (
    <div className="flex-1 bg-panel flex flex-col">
      {/* Document Header */}
      <div className="p-4 border-b border-accent-light bg-accent-bg shadow-theme">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-accent mb-2">{document.name}</h1>
            <p className="text-sm text-accent/80">{document.filename}</p>
            {chunkToHighlight && (
              <div className="mt-2 p-2 bg-accent-light border border-accent rounded text-xs text-accent">
                🔍 Podświetlona zawartość z odpowiedzi czatu
              </div>
            )}
          </div>
          {onBackToLibrary && (
            <button
              onClick={onBackToLibrary}
              className="px-4 py-2 text-sm text-accent hover:text-accent-hover hover:bg-accent-light rounded-theme transition-colors border border-accent-light hover:border-accent"
            >
              ← Powrót do biblioteki
            </button>
          )}
        </div>
      </div>
      
      {/* Document Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {document.content ? (
            <div className="prose prose-sm max-w-none" ref={contentRef}>
              {renderContent(document.content)}
            </div>
          ) : (
            <div className="text-center py-8 text-muted">
              <p>Zawartość dokumentu nie została załadowana</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
