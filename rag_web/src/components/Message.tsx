import { Message as MessageType } from '../types';

interface MessageProps {
  message: MessageType;
}

export default function Message({ message }: MessageProps) {
  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] ${
          message.isUser
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg'
            : 'bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-100 shadow-sm'
        } rounded-2xl px-6 py-4`}
      >
        <p className="text-sm leading-relaxed font-medium">{message.text}</p>
        <p className={`text-xs mt-3 ${
          message.isUser ? 'text-blue-100' : 'text-gray-500'
        } font-medium`}>
          {message.timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          })}
        </p>
      </div>
    </div>
  );
}
