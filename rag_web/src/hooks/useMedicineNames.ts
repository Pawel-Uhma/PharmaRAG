import { useState, useEffect } from 'react';
import { MedicineNamesData } from '../types/medicine_names_types';

export const useMedicineNames = () => {
  const [names, setNames] = useState<string[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMedicineNames = async () => {
      try {
        setLoading(true);
        setLoadingProgress(0);
        setIsInitialLoad(true);
        
        // Load from static JSON file
        const response = await fetch('/medicine_names_minimal.json');
        if (!response.ok) {
          throw new Error('Failed to load medicine names');
        }
        
        const data: MedicineNamesData = await response.json();
        setTotalCount(data.total_count);
        
        // Simulate real-time loading by adding names in batches
        const batchSize = 50; // Load 50 names at a time
        const totalBatches = Math.ceil(data.names.length / batchSize);
        
        for (let i = 0; i < totalBatches; i++) {
          const startIndex = i * batchSize;
          const endIndex = Math.min(startIndex + batchSize, data.names.length);
          const batch = data.names.slice(startIndex, endIndex);
          
          // Add a small delay to simulate real-time loading
          await new Promise(resolve => setTimeout(resolve, 10));
          
          setNames(prevNames => [...prevNames, ...batch]);
          setLoadingProgress(((i + 1) / totalBatches) * 100);
        }
        
        setError(null);
        console.log(`Loaded ${data.names.length} medicine names in batches`);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error loading medicine names:', err);
      } finally {
        setLoading(false);
        setIsInitialLoad(false);
      }
    };

    loadMedicineNames();
  }, []);

  return { 
    names, 
    totalCount, 
    loading, 
    loadingProgress, 
    isInitialLoad, 
    error 
  };
};
