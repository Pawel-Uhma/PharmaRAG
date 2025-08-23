export default function Features() {
  const features = [
    {
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: "Dokładne informacje",
      description: "Otrzymuj wiarygodne, aktualne informacje farmaceutyczne ze sprawdzonych źródeł.",
      gradient: "from-green-400 to-emerald-500"
    },
    {
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: "Natychmiastowe odpowiedzi",
      description: "Odpowiedzi napędzane AI, które zapewniają szybkie odpowiedzi na Twoje pytania farmaceutyczne.",
      gradient: "from-blue-400 to-indigo-500"
    },
    {
      icon: (
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      title: "Bezpieczne i prywatne",
      description: "Twoje rozmowy są prywatne i bezpieczne, zapewniając poufność Twoich zapytań zdrowotnych.",
      gradient: "from-purple-400 to-pink-500"
    }
  ];

  return (
    <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
      {features.map((feature, index) => (
        <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-accent-light shadow-theme hover:shadow-theme-hover transition-all duration-300">
          <div className={`w-12 h-12 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-4 shadow-theme`}>
            {feature.icon}
          </div>
          <h3 className="text-lg font-semibold text-primary mb-2">{feature.title}</h3>
          <p className="text-muted text-sm">{feature.description}</p>
        </div>
      ))}
    </div>
  );
}
