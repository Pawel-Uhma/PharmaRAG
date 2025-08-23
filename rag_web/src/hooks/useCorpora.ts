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
    error: namesError 
  } = useMedicineNames();
  const [selectedDocument, setSelectedDocument] = useState<DocumentFile | undefined>();
  const [error, setError] = useState<string | null>(null);

  // Use static data for medicine names - instant loading!
  // No more API calls needed for the names list

  const selectDocument = async (medicineName: string) => {
    try {
      console.log('Selecting document for:', medicineName);
      // Fetch the full document when a medicine name is clicked
      const response = await fetch(`http://localhost:8000/documents/${encodeURIComponent(medicineName)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const document = await response.json();
      console.log('Document received:', document);
      setSelectedDocument(document);
      console.log('Document state updated');
    } catch (err) {
      console.error('Error loading document:', err);
      setError('Failed to load document');
    }
  };

  const clearSelection = () => {
    setSelectedDocument(undefined);
  };

  // Combine errors from names loading and document loading
  const combinedError = namesError || error;

  return {
    medicineNames,
    selectedDocument,
    isLoading,
    loadingProgress,
    isInitialLoad,
    error: combinedError,
    selectDocument,
    clearSelection,
    totalCount
  };
};
