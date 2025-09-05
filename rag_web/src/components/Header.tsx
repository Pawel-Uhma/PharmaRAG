'use client';

import React from 'react';

interface HeaderProps {
  activeView: 'chat' | 'library';
  onChatTabClick: () => void;
  onLibraryTabClick: () => void;
  onInfoClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  activeView, 
  onChatTabClick, 
  onLibraryTabClick,
  onInfoClick
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
          <div className="flex space-x-2">
            <button
              onClick={onChatTabClick}
              className={`group px-6 py-3 rounded-theme text-base font-medium transition-all duration-200 flex items-center space-x-2 ${
                activeView === 'chat'
                  ? 'bg-accent-light text-accent border border-accent shadow-theme'
                  : 'text-muted hover:text-accent hover:bg-accent-light'
              }`}
            >
              <span>Czat</span>
              <svg 
                className={`w-4 h-4 transition-transform duration-200 ${
                  activeView === 'chat' ? 'rotate-0' : 'group-hover:rotate-90'
                }`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <button
              onClick={onLibraryTabClick}
              className={`group px-6 py-3 rounded-theme text-base font-medium transition-all duration-200 flex items-center space-x-2 ${
                activeView === 'library'
                  ? 'bg-accent-light text-accent border border-accent shadow-theme'
                  : 'text-muted hover:text-accent hover:bg-accent-light'
              }`}
            >
              <span>Biblioteka</span>
              <svg 
                className={`w-4 h-4 transition-transform duration-200 ${
                  activeView === 'library' ? 'rotate-0' : 'group-hover:rotate-90'
                }`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
        
        {/* Portfolio Info and Info Button */}
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-muted">Portfolio Project</p>
            <p className="text-sm font-medium text-primary">Paweł Uhma</p>
          </div>
          <button
            onClick={onInfoClick}
            className="p-2 rounded-theme text-muted hover:text-accent hover:bg-accent-light transition-all duration-200 group"
            title="Instrukcje"
          >
            <svg 
              className="w-5 h-5 transition-transform duration-200 group-hover:scale-110" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};
