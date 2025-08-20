'use client';

import { Header, ChatContainer, ConversationsSidebar, ContextPanel } from '../components';
import { useChat } from '../hooks/useChat';
import { ThemeProvider } from '../contexts/ThemeContext';

function HomeContent() {
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

  const currentMessage = messages[messages.length - 1];
  const currentSources = currentMessage?.sources || [];
  const currentChunks = currentMessage?.sources?.flatMap(source => 
    source.id === currentMessage.sources?.[0]?.id ? [] : []
  ) || [];

  const handleSourceClick = (source: any) => {
    setContextPanel(prev => ({
      ...prev,
      activeTab: 'sources',
      selectedSource: source
    }));
  };

  return (
    <div className="min-h-screen bg-primary">
      <Header />
      
      {/* Main Content - 3-Pane Layout */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Sidebar - Conversations */}
        <ConversationsSidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={setCurrentConversationId}
          onCreateNew={createNewConversation}
          onDeleteConversation={deleteConversation}
          onUpdateTitle={updateConversationTitle}
        />
        
        {/* Center - Chat */}
        <div className="flex-1 flex flex-col">
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
        
        {/* Right Sidebar - Context Panel */}
        <ContextPanel
          state={contextPanel}
          onStateChange={setContextPanel}
          currentMessage={currentMessage}
          sources={currentSources}
          chunks={currentChunks}
        />
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <HomeContent />
    </ThemeProvider>
  );
}
