'use client';

import React, { useState, useMemo } from 'react';

interface DocumentFile {
  name: string;
  filename: string;
  content?: string;
}

interface CorporaLibraryProps {
  documents: DocumentFile[];
  onDocumentSelect: (document: DocumentFile) => void;
  selectedDocument?: DocumentFile;
}

export const CorporaLibrary: React.FC<CorporaLibraryProps> = ({
  documents,
  onDocumentSelect,
  selectedDocument
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Group documents by first letter
  const groupedDocuments = useMemo(() => {
    const filtered = searchQuery.trim() === '' 
      ? documents 
      : documents.filter(doc => 
          doc.name.toLowerCase().includes(searchQuery.toLowerCase())
        );

    if (searchQuery.trim() !== '') {
      return { 'Wyniki wyszukiwania': filtered };
    }

    const grouped: Record<string, DocumentFile[]> = {};
    filtered.forEach(doc => {
      const firstLetter = doc.name.charAt(0).toUpperCase();
      if (!grouped[firstLetter]) {
        grouped[firstLetter] = [];
      }
      grouped[firstLetter].push(doc);
    });

    // Sort groups alphabetically
    return Object.fromEntries(
      Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b))
    );
  }, [documents, searchQuery]);

  const handleDocumentClick = (document: DocumentFile) => {
    onDocumentSelect(document);
  };

  return (
    <div className="w-80 h-full bg-panel border-r border-accent-light flex flex-col shadow-theme">
      {/* Header */}
      <div className="p-4 border-b border-accent-light">
        <h2 className="text-lg font-semibold text-primary mb-4">Biblioteka Korpora</h2>
        
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="Szukaj leków..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 pl-10 bg-elevated border border-accent-light rounded-theme text-primary placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent shadow-theme"
          />
          <svg 
            className="absolute left-3 top-2.5 w-4 h-4 text-muted"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto p-2">
        {Object.entries(groupedDocuments).map(([group, docs]) => (
          <div key={group} className="mb-4">
            {/* Group Header */}
            <div className="px-2 py-1 mb-2">
              <h3 className="text-sm font-semibold text-muted uppercase tracking-wide">
                {group}
              </h3>
            </div>
            
            {/* Documents in Group */}
            <div className="space-y-1">
              {docs.map((doc) => (
                <DocumentItem
                  key={doc.filename}
                  document={doc}
                  isSelected={selectedDocument?.filename === doc.filename}
                  onClick={() => handleDocumentClick(doc)}
                />
              ))}
            </div>
          </div>
        ))}
        
        {Object.keys(groupedDocuments).length === 0 && (
          <div className="text-center py-8 text-muted">
            <p>Nie znaleziono dokumentów</p>
          </div>
        )}
      </div>
    </div>
  );
};

interface DocumentItemProps {
  document: DocumentFile;
  isSelected: boolean;
  onClick: () => void;
}

const DocumentItem: React.FC<DocumentItemProps> = ({
  document,
  isSelected,
  onClick
}) => {
  return (
    <div
      className={`group relative p-3 rounded-theme cursor-pointer transition-all duration-200 ${
        isSelected
          ? 'bg-accent text-white shadow-theme'
          : 'hover:bg-accent-light border border-transparent hover:border-accent'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className={`text-sm font-medium truncate ${
            isSelected ? 'text-white' : 'text-primary'
          }`}>
            {document.name}
          </h3>
          <p className={`text-xs mt-1 ${
            isSelected ? 'text-white/80' : 'text-muted'
          }`}>
            {document.filename}
          </p>
        </div>
        
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <svg className={`w-4 h-4 ${
            isSelected ? 'text-white' : 'text-muted'
          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      </div>
    </div>
  );
};
