import { Message as MessageType } from '../types';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';
import ChatInput from './ChatInput';

interface ChatContainerProps {
  messages: MessageType[];
  inputText: string;
  setInputText: (text: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  isLoading: boolean;
}

export default function ChatContainer({
  messages,
  inputText,
  setInputText,
  onSend,
  onKeyPress,
  isLoading
}: ChatContainerProps) {
  return (
    <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
      {/* Messages Area */}
      <div className="h-[600px] overflow-y-auto p-8 space-y-6">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && <LoadingIndicator />}
      </div>

      {/* Input Area */}
      <ChatInput
        inputText={inputText}
        setInputText={setInputText}
        onSend={onSend}
        onKeyPress={onKeyPress}
        isLoading={isLoading}
      />
    </div>
  );
}
