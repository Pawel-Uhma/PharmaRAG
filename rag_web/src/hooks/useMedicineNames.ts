import { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '../utils/api';

interface PaginatedMedicineNamesResponse {
  names: string[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export const useMedicineNames = () => {
  const [names, setNames] = useState<string[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  const [pageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');

  const loadPage = async (page: number, query?: string) => {
    try {
      setLoading(true);
      setLoadingProgress(0);
      
      const isSearch = query && query.trim() !== '';
      const endpoint = isSearch 
        ? `${API_ENDPOINTS.MEDICINE_NAMES_SEARCH}?query=${encodeURIComponent(query!)}&page=${page}&page_size=${pageSize}`
        : `${API_ENDPOINTS.MEDICINE_NAMES_PAGINATED}?page=${page}&page_size=${pageSize}`;
      
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: PaginatedMedicineNamesResponse = await response.json();
      
      setNames(data.names);
      setTotalCount(data.total_count);
      setCurrentPage(data.page);
      setTotalPages(data.total_pages);
      setHasNext(data.has_next);
      setHasPrevious(data.has_previous);
      setLoadingProgress(100);
      setError(null);
      
      const action = isSearch ? 'searched' : 'loaded';
      console.log(`${action} page ${data.page}/${data.total_pages} with ${data.names.length} medicine names`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error loading medicine names:', err);
    } finally {
      setLoading(false);
      setIsInitialLoad(false);
    }
  };

  // Load first page on initial mount
  useEffect(() => {
    loadPage(1);
  }, []);

  // Debounced search function
  const debouncedSearch = useCallback(
    (() => {
      let timeoutId: NodeJS.Timeout;
      return (query: string) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          setSearchQuery(query);
          if (query.trim() === '') {
            // If search is cleared, go back to first page of all medicines
            loadPage(1);
          } else if (query.trim().length >= 3) {
            // Only search if query has 3 or more characters
            loadPage(1, query);
          } else {
            // For queries with less than 3 characters, just show first page without search
            loadPage(1);
          }
        }, 300); // 300ms delay
      };
    })(),
    []
  );

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      loadPage(page, searchQuery);
    }
  };

  const goToNextPage = () => {
    if (hasNext) {
      goToPage(currentPage + 1);
    }
  };

  const goToPreviousPage = () => {
    if (hasPrevious) {
      goToPage(currentPage - 1);
    }
  };

  const search = (query: string) => {
    debouncedSearch(query);
  };

  const clearSearch = () => {
    setSearchQuery('');
    loadPage(1);
  };

  return { 
    names, 
    totalCount, 
    loading, 
    loadingProgress, 
    isInitialLoad, 
    error,
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
