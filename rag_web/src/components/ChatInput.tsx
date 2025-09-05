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
      <div className={`relative flex items-end space-x-2 sm:space-x-3 p-2 sm:p-3 rounded-theme border transition-all duration-200 ${
        isFocused
          ? 'border-accent bg-elevated shadow-theme-hover'
          : 'border-accent-light bg-panel hover:border-accent hover:shadow-theme'
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
            className="w-full resize-none bg-transparent text-primary placeholder-muted border-none outline-none text-sm leading-relaxed pr-8 sm:pr-12"
            style={{
              minHeight: '20px',
              maxHeight: '100px'
            }}
          />
          
          {/* Character count */}
          <div className="absolute bottom-0 right-0 text-xs text-muted hidden sm:block">
            {value.length}/4000
          </div>
        </div>

        {/* Send Button */}
        <button
          onClick={handleSubmit}
          disabled={!value.trim() || disabled}
          className={`flex-shrink-0 p-1.5 sm:p-2 rounded-theme transition-all duration-200 ${
            value.trim() && !disabled
              ? 'bg-accent text-white hover:bg-accent/90 hover:scale-105 shadow-theme-hover'
              : 'bg-accent-light text-muted cursor-not-allowed'
          }`}
          title="Wyślij wiadomość"
        >
          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      {/* Helper text */}
      <div className="mt-1 sm:mt-2 text-xs text-muted text-center hidden sm:block">
        Naciśnij Enter aby wysłać, Shift+Enter dla nowej linii
      </div>
    </div>
  );
};
