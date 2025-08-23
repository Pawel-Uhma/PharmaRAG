'use client';

import React from 'react';
import { Conversation } from '../types';

interface ConversationsSidebarProps {
  conversations: Conversation[];
  currentConversationId: string;
  onSelectConversation: (id: string) => void;
  onCreateNew: () => void;
  onDeleteConversation: (id: string) => void;
  onUpdateTitle: (id: string, title: string) => void;
}

export const ConversationsSidebar: React.FC<ConversationsSidebarProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onCreateNew,
  onDeleteConversation,
  onUpdateTitle
}) => {
  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Dzisiaj';
    if (days === 1) return 'Wczoraj';
    if (days < 7) return `${days} dni temu`;
    return date.toLocaleDateString('pl-PL');
  };

  return (
    <div className="w-80 h-full bg-panel border-r border-accent-light flex flex-col shadow-theme">
      {/* Header */}
      <div className="p-4 border-b border-accent-light">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-accent">Rozmowy</h2>
          <button
            onClick={onCreateNew}
            className="p-2 rounded-theme bg-accent hover:bg-accent-hover text-white transition-colors duration-200 shadow-theme"
            title="Nowa rozmowa"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2">
        {conversations.length === 0 ? (
          <div className="text-center py-8 text-muted">
            <p>Brak rozmów</p>
            <button
              onClick={onCreateNew}
              className="mt-2 text-accent hover:text-accent-hover underline"
            >
              Rozpocznij pierwszą rozmowę
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {conversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === currentConversationId}
                onSelect={() => onSelectConversation(conversation.id)}
                onDelete={() => onDeleteConversation(conversation.id)}
                onUpdateTitle={(title) => onUpdateTitle(conversation.id, title)}
                formatDate={formatDate}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onUpdateTitle: (title: string) => void;
  formatDate: (date: Date) => string;
}

const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onDelete,
  onUpdateTitle,
  formatDate
}) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editTitle, setEditTitle] = React.useState(conversation.title);

  const handleTitleSubmit = () => {
    if (editTitle.trim()) {
      onUpdateTitle(editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleTitleSubmit();
    } else if (e.key === 'Escape') {
      setEditTitle(conversation.title);
      setIsEditing(false);
    }
  };

  return (
    <div
      className={`group relative p-3 rounded-theme cursor-pointer transition-all duration-200 ${
        isActive
          ? 'bg-accent text-white shadow-theme'
          : 'hover:bg-accent-light hover:border-accent border border-transparent'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleKeyPress}
              onBlur={handleTitleSubmit}
              className={`w-full bg-transparent border-none outline-none text-sm font-medium ${
                isActive ? 'text-white placeholder-white/80' : 'text-primary'
              }`}
              autoFocus
            />
          ) : (
            <h3 className={`text-sm font-medium truncate ${
              isActive ? 'text-white' : 'text-primary'
            }`}>
              {conversation.title}
            </h3>
          )}
          <p className={`text-xs mt-1 ${
            isActive ? 'text-white/80' : 'text-accent/80'
          }`}>
            {conversation.metadata.totalMessages} wiadomości • {formatDate(conversation.updatedAt)}
          </p>
        </div>
        
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            className={`p-1 rounded hover:bg-white/20 text-white/80 hover:text-white transition-colors ${
              isActive ? 'text-white/80' : 'text-accent hover:text-accent-hover'
            }`}
            title="Edytuj tytuł"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className={`p-1 rounded hover:bg-white/20 hover:text-white transition-colors ${
              isActive ? 'text-white/80' : 'text-accent hover:text-danger'
            }`}
            title="Usuń rozmowę"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};
