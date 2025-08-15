'use client';

import { Header, ChatContainer, Features } from '../components';
import { useChat } from '../hooks/useChat';

export default function Home() {
  const {
    messages,
    inputText,
    setInputText,
    isLoading,
    sendMessage,
    handleKeyPress
  } = useChat();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Header />
      
      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <ChatContainer
          messages={messages}
          inputText={inputText}
          setInputText={setInputText}
          onSend={sendMessage}
          onKeyPress={handleKeyPress}
          isLoading={isLoading}
        />
        
        <Features />
      </div>
    </div>
  );
}
