export default function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-100 rounded-2xl px-6 py-4 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className="text-sm font-medium text-gray-700">Analyzing your question...</span>
        </div>
      </div>
    </div>
  );
}
