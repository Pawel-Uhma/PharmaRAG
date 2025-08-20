'use client';

import React, { useState } from 'react';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  onKeyPress,
  disabled = false,
  placeholder = "Type your message..."
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = () => {
    if (value.trim() && !disabled) {
      onSend();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else {
      onKeyPress(e);
    }
  };

  return (
    <div className="relative">
      <div className={`relative flex items-end space-x-3 p-3 rounded-theme border transition-all duration-200 ${
        isFocused
          ? 'border-accent/50 bg-elevated shadow-theme'
          : 'border-ring/20 bg-panel hover:border-ring/30'
      }`}>
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={disabled}
            placeholder={placeholder}
            rows={1}
            className="w-full resize-none bg-transparent text-primary placeholder-muted border-none outline-none text-sm leading-relaxed pr-12"
            style={{
              minHeight: '24px',
              maxHeight: '120px'
            }}
          />
          
          {/* Character count */}
          <div className="absolute bottom-0 right-0 text-xs text-muted">
            {value.length}/4000
          </div>
        </div>

        {/* Send Button */}
        <button
          onClick={handleSubmit}
          disabled={!value.trim() || disabled}
          className={`flex-shrink-0 p-2 rounded-theme transition-all duration-200 ${
            value.trim() && !disabled
              ? 'bg-accent text-white hover:bg-accent/90 hover:scale-105 shadow-theme'
              : 'bg-panel text-muted cursor-not-allowed'
          }`}
          title="Send message"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      {/* Helper text */}
      <div className="mt-2 text-xs text-muted text-center">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
};
