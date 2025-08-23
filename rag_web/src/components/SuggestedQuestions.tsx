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
    <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 className="text-sm font-medium text-blue-700 mb-3">Przykładowe pytania:</h3>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="px-3 py-2 text-xs bg-white border border-blue-200 text-blue-700 hover:bg-blue-100 hover:border-blue-300 rounded-lg transition-all duration-200 hover:scale-105 shadow-sm"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
};
