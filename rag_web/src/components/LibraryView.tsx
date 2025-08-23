'use client';

import React, { useState, useMemo } from 'react';

interface DocumentFile {
  name: string;
  filename: string;
  content?: string;
}

interface LibraryViewProps {
  medicineNames: string[];
  selectedDocument?: DocumentFile;
  onMedicineSelect: (medicineName: string) => void;
  isLoading?: boolean;
  loadingProgress?: number;
  isInitialLoad?: boolean;
  totalCount?: number;
  error?: string | null;
}

export const LibraryView: React.FC<LibraryViewProps> = ({
  medicineNames,
  selectedDocument,
  onMedicineSelect,
  isLoading = false,
  loadingProgress = 0,
  isInitialLoad = false,
  totalCount = 0,
  error = null
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter medicine names based on search query
  const filteredMedicineNames = useMemo(() => {
    if (searchQuery.trim() === '') {
      return medicineNames;
    }
    return medicineNames.filter(name => 
      name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [medicineNames, searchQuery]);

  // Group filtered names by first letter
  const groupedNames = useMemo(() => {
    const grouped: Record<string, string[]> = {};
    filteredMedicineNames.forEach(name => {
      const firstLetter = name.charAt(0).toUpperCase();
      if (!grouped[firstLetter]) {
        grouped[firstLetter] = [];
      }
      grouped[firstLetter].push(name);
    });

    // Sort groups alphabetically
    return Object.fromEntries(
      Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b))
    );
  }, [filteredMedicineNames]);

  const handleMedicineClick = (medicineName: string) => {
    onMedicineSelect(medicineName);
  };

  // Show loading state only if it's the initial load and we have no names yet
  if (isInitialLoad && medicineNames.length === 0) {
    return (
      <div className="max-w-6xl mx-auto w-full">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-lg font-medium text-accent">Ładowanie dokumentów...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="max-w-6xl mx-auto w-full">
        <div className="text-center py-12 text-red-500">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p className="text-lg font-medium">Błąd ładowania dokumentów</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto w-full">
      {/* Loading Progress Bar - Show when loading and we have some names */}
      {isLoading && medicineNames.length > 0 && (
        <div className="mb-6 p-4 bg-accent-bg border border-accent-light rounded-theme">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-accent">Ładowanie dokumentów...</span>
            <span className="text-sm text-accent/80">{Math.round(loadingProgress)}%</span>
          </div>
          <div className="w-full bg-accent-light rounded-full h-2">
            <div 
              className="bg-accent h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${loadingProgress}%` }}
            ></div>
          </div>
          <div className="text-xs text-accent/80 mt-1">
            Załadowano {medicineNames.length} z {totalCount} dokumentów
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-accent/80">
            Znaleziono {filteredMedicineNames.length} z {medicineNames.length} leków
          </div>
          {/* Loading Status Indicator */}
          <div className="flex items-center space-x-2">
            {isLoading ? (
              <div className="flex items-center space-x-2 text-sm text-accent">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-accent"></div>
                <span>Ładowanie...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-sm text-green-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Zakończono</span>
              </div>
            )}
          </div>
        </div>
        <div className="relative">
          <input
            type="text"
            placeholder="Szukaj dokumentów..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 pl-12 bg-elevated border border-accent-light rounded-theme text-primary placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent shadow-theme"
          />
          <svg 
            className="absolute left-4 top-3.5 w-5 h-5 text-accent"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Documents Grid */}
      <div className="space-y-8">
        {Object.entries(groupedNames).map(([group, names]) => (
          <div key={group}>
            {/* Group Header */}
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-accent border-b border-accent-light pb-2">
                {group}
              </h2>
            </div>
            
            {/* Documents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {names.map((name) => (
                <DocumentCard
                  key={name}
                  document={name}
                  isSelected={selectedDocument?.filename === name}
                  onClick={() => handleMedicineClick(name)}
                />
              ))}
            </div>
          </div>
        ))}
        
        {Object.keys(groupedNames).length === 0 && (
          <div className="text-center py-12 text-muted">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-lg font-medium">Nie znaleziono leków</p>
            <p className="text-sm">Spróbuj zmienić wyszukiwanie</p>
          </div>
        )}
      </div>
    </div>
  );
};

interface DocumentCardProps {
  document: string; // Changed to string as it's now a medicine name
  isSelected: boolean;
  onClick: () => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  isSelected,
  onClick
}) => {
  return (
    <div
      className={`group relative p-4 rounded-theme cursor-pointer transition-all duration-200 border ${
        isSelected
          ? 'bg-accent text-white shadow-theme-hover'
          : 'bg-elevated border-accent-light hover:bg-accent-light hover:border-accent hover:shadow-theme-hover'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className={`text-sm font-semibold truncate mb-1 ${
            isSelected ? 'text-white' : 'text-primary'
          }`}>
            {document}
          </h3>
          <p className={`text-xs ${
            isSelected ? 'text-white/80' : 'text-muted'
          }`}>
            {/* No filename for medicine names */}
          </p>
        </div>
        
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <svg className={`w-4 h-4 ${
            isSelected ? 'text-white' : 'text-accent'
          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      </div>
      
      {/* Preview of content */}
      {/* No content preview for medicine names */}
    </div>
  );
};
