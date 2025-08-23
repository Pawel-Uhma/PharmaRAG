'use client';

import { Header, ChatContainer, ContextPanel, LibraryView, DocumentViewer } from '../components';
import { useChat } from '../hooks/useChat';
import { useCorpora } from '../hooks/useCorpora';
import { useState, useEffect } from 'react';

function HomeContent() {
  const [activeView, setActiveView] = useState<'chat' | 'library'>('chat');
  
  const {
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
  } = useChat();

  const {
    medicineNames,
    totalCount,
    selectedDocument,
    selectDocument: selectCorporaDocument,
    isLoading: documentsLoading,
    loadingProgress,
    isInitialLoad,
    error: documentsError,
    clearSelection
  } = useCorpora();

  const currentMessage = messages[messages.length - 1];
  const currentSources = currentMessage?.sources || [];
  const currentChunks = currentMessage?.sources?.flatMap(source => 
    source.id === currentMessage.sources?.[0]?.id ? [] : []
  ) || [];

  // Debug: Monitor selectedDocument changes
  useEffect(() => {
    console.log('selectedDocument changed:', selectedDocument);
  }, [selectedDocument]);

  const handleSourceClick = (source: any) => {
    setContextPanel(prev => ({
      ...prev,
      activeTab: 'sources',
      selectedSource: source
    }));
  };

  const handleSourceInContextPanelClick = (source: any) => {
    // Find the document that contains this source
    const sourceMedicineName = source.metadata?.h1 || source.metadata?.source?.split('/')[-1]?.replace('.md', '');
    
    if (sourceMedicineName) {
      // Select the medicine name to load the document
      selectCorporaDocument(sourceMedicineName);
      setActiveView('library');
      // Store the chunk content to highlight later
      setContextPanel(prev => ({
        ...prev,
        selectedSource: source,
        chunkToHighlight: source.metadata?.chunk_content || ''
      }));
    }
  };

  const handleDocumentSelect = async (medicineName: string) => {
    try {
      console.log('handleDocumentSelect called with:', medicineName);
      await selectCorporaDocument(medicineName);
      console.log('selectCorporaDocument completed');
      setActiveView('library');
      console.log('Active view set to library');
    } catch (error) {
      console.error('Error selecting document:', error);
    }
  };

  const handleLibraryTabClick = () => {
    setActiveView('library');
    // Clear any selected document when switching to library
    // setSelectedDocument(null); // This line is removed as per the edit hint
    // Scroll to top when switching to library
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleChatTabClick = () => {
    setActiveView('chat');
    // Clear any selected document when switching to chat
    // setSelectedDocument(null); // This line is removed as per the edit hint
    // Scroll to top when switching to chat
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="h-screen flex flex-col bg-primary overflow-hidden">
      <Header 
        activeView={activeView}
        onChatTabClick={handleChatTabClick}
        onLibraryTabClick={handleLibraryTabClick}
      />
      
      {/* Main Content - 2-Pane Layout */}
      <div className="flex-1 flex min-h-0">
        {/* Center - Main Content */}
        <div className="flex-1 flex flex-col min-h-0">
          {activeView === 'chat' ? (
            <div className="flex-1 flex flex-col min-h-0">
              {/* Chat Interface */}
              <ChatContainer
                messages={messages}
                inputText={inputText}
                setInputText={setInputText}
                onSend={sendMessage}
                onKeyPress={handleKeyPress}
                isLoading={isLoading}
                onSourceClick={handleSourceClick}
              />
            </div>
          ) : (
            <div className="flex-1 flex flex-col min-h-0">
              {/* Library Header */}
              <div className="flex-shrink-0 p-4 border-b border-accent-light bg-accent-bg shadow-theme">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-xl font-bold text-accent mb-2">
                      {selectedDocument ? selectedDocument.name : 'Biblioteka Dokumentów'}
                    </h1>
                    <p className="text-sm text-accent/80">
                      {selectedDocument ? 'Szczegóły dokumentu' : `Przeglądaj ${totalCount} dokumentów farmaceutycznych`}
                    </p>
                  </div>
                  {selectedDocument && (
                    <button
                      onClick={() => clearSelection()}
                      className="px-4 py-2 text-sm text-accent hover:text-accent-hover hover:bg-accent-light rounded-theme transition-colors border border-accent-light hover:border-accent"
                    >
                      ← Powrót do biblioteki
                    </button>
                  )}
                </div>
              </div>
              
              {/* Library Content */}
              <div className="flex-1 overflow-y-auto p-6 min-h-0">
                {selectedDocument ? (
                  <DocumentViewer 
                    document={selectedDocument} 
                    chunkToHighlight={contextPanel.chunkToHighlight}
                    onBackToLibrary={() => clearSelection()}
                  />
                ) : (
                  <LibraryView 
                    medicineNames={medicineNames}
                    selectedDocument={selectedDocument}
                    onMedicineSelect={handleDocumentSelect}
                    isLoading={documentsLoading}
                    loadingProgress={loadingProgress}
                    isInitialLoad={isInitialLoad}
                    totalCount={totalCount}
                    error={documentsError}
                  />
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Right Sidebar - Context Panel (only for chat view) */}
        {activeView === 'chat' && (
          <ContextPanel
            state={contextPanel}
            onStateChange={setContextPanel}
            currentMessage={currentMessage}
            sources={currentSources}
            onSourceClick={handleSourceInContextPanelClick}
          />
        )}
      </div>
    </div>
  );
}

export default function Home() {
  return <HomeContent />;
}
