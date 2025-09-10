// API configuration utility
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  RAG_ANSWER: `${API_BASE_URL}/rag/answer`,
  MEDICINE_NAMES_PAGINATED: `${API_BASE_URL}/medicine-names/paginated`,
  MEDICINE_NAMES_SEARCH: `${API_BASE_URL}/medicine-names/search`,
  DOCUMENTS: (medicineName: string) => `${API_BASE_URL}/documents/${encodeURIComponent(medicineName)}`,
} as const;
