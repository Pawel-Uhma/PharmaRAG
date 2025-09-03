import { useState, useEffect } from 'react';
import { useMedicineNames } from './useMedicineNames';

export interface DocumentFile {
  name: string;
  filename: string;
  source?: string;
  h1?: string;
  h2?: string;
  content?: string;
}

export interface MedicineName {
  name: string;
}

export const useCorpora = () => {
  const { 
    names: medicineNames, 
    totalCount, 
    loading: isLoading, 
    loadingProgress,
    isInitialLoad,
    error: namesError,
    currentPage,
    totalPages,
    hasNext,
    hasPrevious,
    searchQuery,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    search,
    clearSearch
  } = useMedicineNames();
  const [selectedDocument, setSelectedDocument] = useState<DocumentFile | undefined>();
  const [selectedMedicineName, setSelectedMedicineName] = useState<string | undefined>();
  const [isDocumentLoading, setIsDocumentLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectDocument = async (medicineName: string) => {
    try {
      console.log('Selecting document for:', medicineName);
      
      // Immediately set the selected medicine name and start loading
      setSelectedMedicineName(medicineName);
      setIsDocumentLoading(true);
      setError(null);
      
      // Fetch the full document when a medicine name is clicked
      const response = await fetch(`http://localhost:8000/documents/${encodeURIComponent(medicineName)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const document = await response.json();
      console.log('Document received:', document);
      setSelectedDocument(document);
      setIsDocumentLoading(false);
      console.log('Document state updated');
    } catch (err) {
      console.error('Error loading document:', err);
      setError('Failed to load document');
      setIsDocumentLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedDocument(undefined);
    setSelectedMedicineName(undefined);
    setIsDocumentLoading(false);
    setError(null);
  };

  // Combine errors from names loading and document loading
  const combinedError = namesError || error;

  return {
    medicineNames,
    selectedDocument,
    selectedMedicineName,
    isLoading,
    isDocumentLoading,
    loadingProgress,
    isInitialLoad,
    error: combinedError,
    selectDocument,
    clearSelection,
    totalCount,
    currentPage,
    totalPages,
    hasNext,
    hasPrevious,
    searchQuery,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    search,
    clearSearch
  };
};
