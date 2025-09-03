'use client';

import React from 'react';

interface DocumentFile {
  name: string;
  filename: string;
  source?: string;
  h1?: string;
  h2?: string;
  content?: string;
}

interface DocumentViewerProps {
  document?: DocumentFile;
  selectedMedicineName?: string;
  isDocumentLoading?: boolean;
  chunkToHighlight?: string;
  onBackToLibrary?: () => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ 
  document, 
  selectedMedicineName,
  isDocumentLoading = false,
  chunkToHighlight, 
  onBackToLibrary 
}) => {
  const contentRef = React.useRef<HTMLDivElement>(null);

  // Debug: Log received props
  console.log('DocumentViewer received props:', { document, selectedMedicineName, isDocumentLoading, chunkToHighlight, onBackToLibrary });

  if (!selectedMedicineName) {
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

  // Show loading state when document is being loaded
  if (isDocumentLoading) {
    return (
      <div className="flex-1 bg-panel flex flex-col">
        {/* Document Header */}
        <div className="p-4 border-b border-accent-light bg-accent-bg shadow-theme">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-accent mb-2">{selectedMedicineName}</h1>
              <p className="text-sm text-accent/80">Ładowanie dokumentu...</p>
            </div>
            <div className="flex items-center space-x-3">
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
        </div>
        
        {/* Loading Content */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-accent mx-auto mb-4"></div>
            <p className="text-lg font-medium text-accent">Ładowanie dokumentu...</p>
            <p className="text-sm text-accent/80 mt-2">Pobieranie szczegółów dla {selectedMedicineName}</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state if document failed to load
  if (!document) {
    return (
      <div className="flex-1 bg-panel flex flex-col">
        {/* Document Header */}
        <div className="p-4 border-b border-accent-light bg-accent-bg shadow-theme">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-accent mb-2">{selectedMedicineName}</h1>
              <p className="text-sm text-red-500">Błąd ładowania dokumentu</p>
            </div>
            <div className="flex items-center space-x-3">
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
        </div>
        
        {/* Error Content */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-red-500">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-lg font-medium">Nie udało się załadować dokumentu</p>
            <p className="text-sm mt-2">Dokument dla {selectedMedicineName} nie mógł zostać pobrany</p>
          </div>
        </div>
      </div>
    );
  }

  // Markdown-style content rendering with proper header detection
  const renderContent = (content: string) => {
    if (!content) {
      return (
        <div className="text-center py-8 text-muted">
          <p>Zawartość dokumentu niedostępna</p>
        </div>
      );
    }

    // Split content into lines
    const lines = content.split('\n');
    
    const renderedContent = lines.map((line, index) => {
      const trimmedLine = line.trim();
      
      // Skip empty lines
      if (trimmedLine === '') {
        return <div key={index} className="h-3" />;
      }
      
      // Handle markdown H1 headers (lines starting with #)
      if (trimmedLine.startsWith('# ')) {
        return (
          <h1 key={index} className="text-4xl font-bold text-blue-600 mb-6 mt-8 first:mt-0">
            {trimmedLine.substring(2)}
          </h1>
        );
      }
      
      // Handle markdown H2 headers (lines starting with ##)
      if (trimmedLine.startsWith('## ')) {
        const headerText = trimmedLine.substring(3);
        return (
          <h2 key={index} className="text-3xl font-bold text-black mb-4 mt-6">
            {headerText}
          </h2>
        );
      }
      
      // Skip duplicate content that follows headers (e.g., if content has both "## Header" and "Some text: Header")
      if (index > 0) {
        const previousLine = lines[index - 1].trim();
        if (previousLine.startsWith('## ') || previousLine.startsWith('# ') || previousLine.startsWith('### ')) {
          const previousHeader = previousLine.replace(/^#+\s*/, '');
          // If current line contains the same header text, skip it
          if (trimmedLine.includes(previousHeader) && trimmedLine.length < previousHeader.length + 20) {
            return null; // Skip this line
          }
        }
      }
      
      // Handle markdown H3 headers (lines starting with ###)
      if (trimmedLine.startsWith('### ')) {
        return (
          <h3 key={index} className="text-2xl font-semibold text-blue-600 mb-3 mt-6">
            {trimmedLine.substring(4)}
          </h3>
        );
      }
      
      // Handle tables (lines with pipe characters)
      if (trimmedLine.includes('|')) {
        const cells = trimmedLine.split('|').filter(cell => cell.trim());
        
        // Check if this looks like a header row (contains words like "Nazwa", "Preparat", "Postać", etc.)
        const isHeaderRow = cells.some(cell => 
          cell.toLowerCase().includes('nazwa') || 
          cell.toLowerCase().includes('preparat') || 
          cell.toLowerCase().includes('postać') ||
          cell.toLowerCase().includes('dawka') ||
          cell.toLowerCase().includes('opakowanie') ||
          cell.toLowerCase().includes('producent') ||
          cell.toLowerCase().includes('cena')
        );
        
        if (isHeaderRow) {
          return (
            <div key={index} className="flex space-x-4 py-3 bg-blue-50 rounded px-4 border border-blue-200 mb-2">
              {cells.map((cell, cellIndex) => (
                <span key={cellIndex} className="text-sm text-blue-800 flex-1 font-semibold">
                  {cell.trim()}
                </span>
              ))}
            </div>
          );
        } else {
          return (
            <div key={index} className="flex space-x-4 py-2 border-b border-gray-200">
              {cells.map((cell, cellIndex) => (
                <span key={cellIndex} className="text-sm text-black flex-1">
                  {cell.trim()}
                </span>
              ))}
            </div>
          );
        }
      }
      
      // Handle bullet points (lines starting with specific characters)
      if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-') || trimmedLine.startsWith('*')) {
        return (
          <div key={index} className="flex items-start py-1">
            <span className="text-blue-600 mr-3 mt-1 text-lg">•</span>
            <span className="text-sm text-black flex-1 leading-relaxed">{trimmedLine.substring(1).trim()}</span>
          </div>
        );
      }
      
      // Handle numbered lists
      if (/^\d+\./.test(trimmedLine)) {
        return (
          <div key={index} className="flex items-start py-1">
            <span className="text-blue-600 mr-3 mt-1 text-sm font-medium min-w-[20px]">
              {trimmedLine.match(/^\d+\./)?.[0]}
            </span>
            <span className="text-sm text-black flex-1 leading-relaxed">
              {trimmedLine.replace(/^\d+\./, '').trim()}</span>
          </div>
        );
      }
      
      // Regular text - check if it's a short descriptive line
      if (trimmedLine.length < 80 && !trimmedLine.includes('|')) {
        return (
          <p key={index} className="text-base text-gray-700 leading-relaxed py-2">
            {trimmedLine}
          </p>
        );
      }
      
      // Longer text paragraphs
      return (
        <p key={index} className="text-sm text-black leading-relaxed py-1">
          {trimmedLine}
        </p>
      );
    });
    
    return renderedContent;
  };

  return (
    <div className="flex-1 bg-panel flex flex-col">
      {/* Document Header */}
      <div className="p-4 border-b border-accent-light bg-accent-bg shadow-theme">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-accent mb-2">{document.name}</h1>
            <p className="text-sm text-accent/80">{document.filename}</p>
          </div>
          <div className="flex items-center space-x-3">
            {document.source && (
              <a
                href={document.source}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-sm text-accent hover:text-accent-hover hover:bg-accent-light rounded-theme transition-colors border border-accent-light hover:border-accent flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Zobacz źródło
              </a>
            )}
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
      </div>
      
      {/* Document Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {document.content ? (
            <div className="max-w-none" ref={contentRef}>
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
