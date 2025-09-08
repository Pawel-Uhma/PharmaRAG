'use client';

import React from 'react';

interface InstructionViewProps {
  onClose: () => void;
}

export const InstructionView: React.FC<InstructionViewProps> = ({ onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-panel rounded-theme shadow-theme max-w-6xl w-full max-h-[130vh] overflow-y-auto">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-theme bg-accent-light flex items-center justify-center">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-primary">Instrukcje PharmaRAG</h1>
                <p className="text-muted">Przewodnik po funkcjonalnościach aplikacji</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-theme text-muted hover:text-accent hover:bg-accent-light transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="space-y-8">
            {/* About Section */}
            <section>
              <h2 className="text-xl font-semibold text-primary mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                O aplikacji
              </h2>
              <div className="bg-accent-light/20 rounded-theme p-6">
                <p className="text-primary leading-relaxed">
                  <strong>PharmaRAG</strong> to inteligentny asystent farmaceutyczny wykorzystujący technologię RAG (Retrieval-Augmented Generation). 
                  Aplikacja umożliwia szybkie wyszukiwanie informacji o lekach, ich składzie, dawkowaniu, przeciwwskazaniach i interakcjach.
                </p>
              </div>
            </section>

            {/* Features Section */}
            <section>
              <h2 className="text-xl font-semibold text-primary mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Główne funkcjonalności
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-panel border border-accent-light rounded-theme p-6">
                  <h3 className="font-semibold text-primary mb-3 flex items-center">
                    <svg className="w-4 h-4 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    Inteligentny Czat
                  </h3>
                  <ul className="text-muted space-y-2 text-sm">
                    <li>• Zadawaj pytania w języku naturalnym</li>
                    <li>• Otrzymuj szczegółowe odpowiedzi z cytatami</li>
                    <li>• Kliknij na cytaty, aby przejść do źródła</li>
                    <li>• Wybierz z sugerowanych pytań</li>
                  </ul>
                </div>
                
                <div className="bg-panel border border-accent-light rounded-theme p-6">
                  <h3 className="font-semibold text-primary mb-3 flex items-center">
                    <svg className="w-4 h-4 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    Biblioteka Dokumentów
                  </h3>
                  <ul className="text-muted space-y-2 text-sm">
                    <li>• Przeglądaj bazę wiedzy o lekach</li>
                    <li>• Wyszukuj konkretne preparaty</li>
                    <li>• Czytaj pełne dokumenty</li>
                    <li>• Nawiguj między stronami</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* How to Use Section */}
            <section>
              <h2 className="text-xl font-semibold text-primary mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Jak korzystać z aplikacji
              </h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <div>
                    <h3 className="font-medium text-primary">Rozpocznij rozmowę</h3>
                    <p className="text-muted text-sm">Wybierz jedną z sugerowanych pytań lub wpisz własne pytanie o leki w polu tekstowym.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h3 className="font-medium text-primary">Analizuj odpowiedzi</h3>
                    <p className="text-muted text-sm">Czytaj szczegółowe odpowiedzi z cytatami. Kliknij na numer cytatu [1], [2] itd., aby przejść do źródła.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h3 className="font-medium text-primary">Przeglądaj bibliotekę</h3>
                    <p className="text-muted text-sm">Przełącz się na zakładkę "Biblioteka", aby przeglądać pełne dokumenty o lekach i wyszukiwać konkretne preparaty.</p>
                  </div>
                </div>
              </div>
            </section>

            {/* Technology Section */}
            <section>
              <h2 className="text-xl font-semibold text-primary mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                Technologie
              </h2>
              <div className="bg-accent-light/20 rounded-theme p-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-primary mb-3">Backend</h3>
                    <ul className="text-muted text-sm space-y-1">
                      <li>• Python & FastAPI</li>
                      <li>• ChromaDB (wektoryzacja)</li>
                      <li>• OpenAI GPT-4</li>
                      <li>• Web scraping & preprocessing</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-medium text-primary mb-3">Frontend</h3>
                    <ul className="text-muted text-sm space-y-1">
                      <li>• Next.js 14 & React</li>
                      <li>• TypeScript</li>
                      <li>• Tailwind CSS</li>
                      <li>• Responsive design</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>

            {/* Contact Section */}
            <section>
              <h2 className="text-xl font-semibold text-primary mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
                Kontakt
              </h2>
              <div className="bg-panel border border-accent-light rounded-theme p-6">
                <p className="text-primary mb-4">
                  To jest projekt portfolio stworzony przez <strong>Pawła Uhma</strong>. 
                  Jeśli masz pytania dotyczące implementacji lub chciałbyś nawiązać współpracę, 
                  zapraszam do kontaktu.
                </p>
                <div className="flex items-center space-x-4 text-sm text-muted">
                  <a
                    href="mailto:paweluhma136@gmail.com"
                    className="hover:underline flex items-center"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    📧 paweluhma136@gmail.com
                  </a>
                  <a
                    href="https://www.linkedin.com/in/pawe%C5%82-uhma-63867b213/"
                    className="hover:underline flex items-center"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    🔗 LinkedIn: /in/paweł-uhma-63867b213/
                  </a>
                  <a
                    href="https://github.com/Pawel-Uhma"
                    className="hover:underline flex items-center"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    💼 GitHub: github.com/Pawel-Uhma
                  </a>
                </div>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-accent-light flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-accent text-white rounded-theme hover:bg-accent-dark transition-colors duration-200 font-medium"
            >
              Zamknij
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
