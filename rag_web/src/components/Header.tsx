'use client';

import React from 'react';

interface HeaderProps {
  activeView: 'chat' | 'library';
  onChatTabClick: () => void;
  onLibraryTabClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  activeView, 
  onChatTabClick, 
  onLibraryTabClick 
}) => {
  return (
    <header className="bg-panel border-b border-accent-light px-6 py-4 shadow-theme">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3">
            <div className="w-20 h-20 flex items-center justify-center">
              <img 
                src="/book.png" 
                alt="PharmaRAG" 
                className="w-16 h-16"
              />
            </div>
            <div>
              <h1 className="text-xl font-bold text-primary">PharmaRAG</h1>
              <p className="text-sm text-muted">Asystent Farmaceutyczny</p>
            </div>
          </div>
          
          {/* Navigation Tabs */}
          <div className="flex space-x-1">
            <button
              onClick={onChatTabClick}
              className={`px-4 py-2 rounded-theme-sm text-sm font-medium transition-all duration-200 ${
                activeView === 'chat'
                  ? 'bg-accent-light text-accent border border-accent shadow-theme'
                  : 'text-muted hover:text-accent hover:bg-accent-light'
              }`}
            >
              Czat
            </button>
            <button
              onClick={onLibraryTabClick}
              className={`px-4 py-2 rounded-theme-sm text-sm font-medium transition-all duration-200 ${
                activeView === 'library'
                  ? 'bg-accent-light text-accent border border-accent shadow-theme'
                  : 'text-muted hover:text-accent hover:bg-accent-light'
              }`}
            >
              Biblioteka
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
