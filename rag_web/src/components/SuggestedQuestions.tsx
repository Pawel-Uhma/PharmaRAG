'use client';

import React from 'react';

interface SuggestedQuestionsProps {
  questions: string[];
  onQuestionClick: (question: string) => void;
}

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onQuestionClick
}) => {
  if (questions.length === 0) return null;

  return (
    <div className="mb-3 sm:mb-4 p-3 sm:p-4 bg-accent-bg border border-accent-light rounded-theme">
      <h3 className="text-xs sm:text-sm font-medium text-accent mb-2 sm:mb-3">Przykładowe pytania:</h3>
      <div className="flex flex-wrap gap-1.5 sm:gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="px-2 sm:px-3 py-1.5 sm:py-2 text-xs bg-panel border border-accent-light text-accent hover:bg-accent-light hover:border-accent rounded-theme transition-all duration-200 hover:scale-105 shadow-theme min-h-[32px] sm:min-h-[36px]"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
};
