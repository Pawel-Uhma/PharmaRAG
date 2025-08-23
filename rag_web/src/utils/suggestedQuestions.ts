export const SUGGESTED_QUESTIONS = [
  "Jakie są wskazania do stosowania Zatogrip mini?",
  "Czy Zanacodar Combi może być stosowany w ciąży?",
  "Jakie są działania niepożądane Zavicefta?",
  "Czy Zentasta wymaga recepty?",
  "Jakie są przeciwwskazania do stosowania Zykadia?",
  "Czy Zyllt może być stosowany z innymi lekami?",
  "Jakie są dawki Zirabev?",
  "Czy Zatoxin DUO jest bezpieczny dla dzieci?",
  "Jakie są skutki uboczne Zatoxin Katar i alergia?",
  "Czy Zinkorot może być stosowany długoterminowo?",
  "Jakie są interakcje Zolpidem Genoptim?",
  "Czy Zinoxx może powodować senność?",
  "Jakie są wskazania do stosowania Zafrilla?",
  "Czy Zavedos może być podawany domięśniowo?",
  "Jakie są przeciwwskazania do Zevesin?",
  "Czy Zessly może być stosowany u dzieci?",
  "Jakie są działania niepożądane Ziextenzo?",
  "Czy Zetuvit Plus jest dostępny bez recepty?",
  "Jakie są dawki Zoledronic Acid Accord?",
  "Czy Zaranta może być stosowana w cukrzycy?"
];

export const getRandomQuestions = (count: number = 3): string[] => {
  const shuffled = [...SUGGESTED_QUESTIONS].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};
