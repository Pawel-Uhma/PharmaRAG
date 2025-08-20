import { useState, useEffect, useCallback } from 'react';
import { Message, RAGResponse, Conversation, ContextPanelState } from '../types';

export const useChat = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string>('');
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contextPanel, setContextPanel] = useState<ContextPanelState>({
    activeTab: 'sources'
  });

  // Initialize with a default conversation
  useEffect(() => {
    const defaultConversation: Conversation = {
      id: 'default',
      title: 'New Conversation',
      messages: [
        {
          id: '1',
          text: 'Hello! I\'m your pharmaceutical information assistant. Ask me anything about medications, their uses, side effects, or other pharmaceutical topics.',
          isUser: false,
          timestamp: new Date()
        }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      metadata: {
        totalMessages: 1
      }
    };

    setConversations([defaultConversation]);
    setCurrentConversationId('default');
  }, []);

  const currentConversation = conversations.find(c => c.id === currentConversationId);
  const messages = currentConversation?.messages || [];

  const createNewConversation = useCallback(() => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      metadata: {
        totalMessages: 0
      }
    };

    setConversations(prev => [...prev, newConversation]);
    setCurrentConversationId(newConversation.id);
    setInputText('');
  }, []);

  const updateConversationTitle = useCallback((conversationId: string, title: string) => {
    setConversations(prev => prev.map(c => 
      c.id === conversationId 
        ? { ...c, title, updatedAt: new Date() }
        : c
    ));
  }, []);

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading || !currentConversationId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    // Update conversation with user message
    setConversations(prev => prev.map(c => 
      c.id === currentConversationId 
        ? {
            ...c,
            messages: [...c.messages, userMessage],
            updatedAt: new Date(),
            metadata: {
              ...c.metadata,
              totalMessages: c.messages.length + 1,
              lastQuery: inputText
            }
          }
        : c
    ));

    // Update conversation title if it's the first user message
    if (messages.length === 1) { // Only welcome message exists
      updateConversationTitle(currentConversationId, inputText.slice(0, 50));
    }

    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/rag/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: inputText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: RAGResponse = await response.json();
      
      // Debug logging
      console.log('Backend response:', data);
      console.log('Sources:', data.sources);
      console.log('Metadata:', data.metadata);
      
      // Transform backend metadata to frontend format
      // The backend returns metadata as an array of objects with h1, h2, source, relevance_score
      const transformedSources = data.sources.map((source, index) => {
        const docMetadata = data.metadata?.[index] || {};
        console.log(`Transforming source ${index}:`, { source, docMetadata });
        return {
          id: index.toString(),
          title: docMetadata.h1 || String(source), // Use h1 as title, fallback to source
          url: String(source),
          type: 'document' as const,
          metadata: {
            h1: docMetadata.h1 || '',
            h2: docMetadata.h2 || '',
            relevance_score: docMetadata.relevance_score || 0,
            chunk_content: docMetadata.chunk_content || ''
          }
        };
      });
      
      console.log('Transformed sources:', transformedSources);
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        sources: transformedSources,
        metadata: {
          documentMetadata: data.metadata // Pass the full metadata array
        }
      };

      // Update conversation with bot message
      setConversations(prev => prev.map(c => 
        c.id === currentConversationId 
          ? {
              ...c,
              messages: [...c.messages, botMessage],
              updatedAt: new Date(),
              metadata: {
                ...c.metadata,
                totalMessages: c.messages.length + 1
              }
            }
          : c
      ));

      // Set context panel to show sources
      setContextPanel(prev => ({
        ...prev,
        activeTab: 'sources'
      }));

    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error while processing your request. Please try again.',
        isUser: false,
        timestamp: new Date()
      };

      setConversations(prev => prev.map(c => 
        c.id === currentConversationId 
          ? {
              ...c,
              messages: [...c.messages, errorMessage],
              updatedAt: new Date(),
              metadata: {
                ...c.metadata,
                totalMessages: c.messages.length + 1
              }
            }
          : c
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const deleteConversation = useCallback((conversationId: string) => {
    setConversations(prev => prev.filter(c => c.id !== conversationId));
    if (currentConversationId === conversationId) {
      const remainingConversations = conversations.filter(c => c.id !== conversationId);
      if (remainingConversations.length > 0) {
        setCurrentConversationId(remainingConversations[0].id);
      } else {
        createNewConversation();
      }
    }
  }, [currentConversationId, conversations, createNewConversation]);

  return {
    conversations,
    currentConversationId,
    messages,
    inputText,
    setInputText,
    isLoading,
    sendMessage,
    handleKeyPress,
    createNewConversation,
    updateConversationTitle,
    deleteConversation,
    setCurrentConversationId,
    contextPanel,
    setContextPanel
  };
};
