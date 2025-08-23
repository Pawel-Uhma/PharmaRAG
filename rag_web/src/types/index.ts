export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: Source[];
  metadata?: {
    confidence?: number;
    processingTime?: number;
    documentMetadata?: Array<{
      h1: string;  // Name (main heading)
      h2: string;  // Heading (sub-heading)
      source: string;
      relevance_score: number;
      chunk_content: string;  // Beginning of the chunk content used
    }>;
  };
}

export interface RAGResponse {
  response: string;
  sources: string[];  // Backend returns array of strings
  metadata: Array<{
    h1: string;  // Name (main heading)
    h2: string;  // Heading (sub-heading)
    source: string;
    relevance_score: number;
    chunk_content: string;  // Beginning of the chunk content used
  }>;
}

export interface Source {
  id: string;
  title: string;
  url?: string;
  type: 'document' | 'webpage' | 'database' | 'api';
  metadata?: {
    author?: string;
    date?: string;
    domain?: string;
    relevance_score?: number;
    h1?: string;  // Name (main heading)
    h2?: string;  // Heading (sub-heading)
    chunk_content?: string;  // Beginning of the chunk content used
  };
}

export interface Chunk {
  id: string;
  text: string;
  sourceId: string;
  metadata?: {
    startIndex?: number;
    endIndex?: number;
    relevance_score?: number;
    embedding?: number[];
  };
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  metadata: {
    totalMessages: number;
    lastQuery?: string;
  };
}

export interface ContextPanelState {
  activeTab: 'sources' | 'history';
  selectedSource?: Source;
  chunkToHighlight?: string;
}
