# PharmaRAG Web Application

A modern, well-structured React/Next.js application for pharmaceutical information assistance using AI.

## 🏗️ Project Structure

```
src/
├── app/
│   ├── globals.css          # Global styles with Tailwind CSS
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page (clean and minimal)
├── components/               # Reusable UI components
│   ├── index.ts             # Component exports
│   ├── Header.tsx           # Application header with branding
│   ├── ChatContainer.tsx    # Main chat interface container
│   ├── Message.tsx          # Individual message component
│   ├── LoadingIndicator.tsx # Loading state indicator
│   ├── ChatInput.tsx        # Chat input and send button
│   └── Features.tsx         # Feature showcase section
├── hooks/                    # Custom React hooks
│   └── useChat.ts           # Chat state management and API logic
└── types/                    # TypeScript type definitions
    └── index.ts             # Application interfaces and types
```

## 🎯 Architecture Benefits

### **Separation of Concerns**
- **UI Components**: Pure presentation components with no business logic
- **Custom Hooks**: Business logic and state management separated from UI
- **Types**: Centralized type definitions for better maintainability

### **Reusability**
- Components can be easily reused across different parts of the application
- Custom hooks can be shared between components
- Type definitions ensure consistency across the codebase

### **Maintainability**
- Each component has a single responsibility
- Easy to locate and modify specific functionality
- Clear separation between logic and presentation

### **Testing**
- Components can be tested in isolation
- Business logic in hooks can be tested separately
- Clear interfaces make mocking easier

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🎨 Design Features

- **Modern UI**: Glassmorphism effects with backdrop blur
- **Responsive Design**: Works seamlessly on all device sizes
- **Tailwind CSS**: Utility-first CSS framework for rapid development
- **Smooth Animations**: Hover effects and transitions for better UX
- **Accessibility**: Proper focus states and keyboard navigation

## 🔧 Customization

### Adding New Components
1. Create the component in `src/components/`
2. Export it from `src/components/index.ts`
3. Import and use in your pages

### Adding New Hooks
1. Create the hook in `src/hooks/`
2. Follow the naming convention `use[FeatureName]`
3. Import and use in your components

### Modifying Types
1. Update interfaces in `src/types/index.ts`
2. Components and hooks will automatically get the new types

## 📱 Component Usage Examples

```tsx
// Using the chat hook
import { useChat } from '../hooks/useChat';

function MyComponent() {
  const { messages, sendMessage, isLoading } = useChat();
  // ... component logic
}

// Using individual components
import { Header, ChatContainer } from '../components';

function MyPage() {
  return (
    <div>
      <Header />
      <ChatContainer {...props} />
    </div>
  );
}
```

## 🎯 Best Practices

1. **Keep components small and focused**
2. **Use custom hooks for complex logic**
3. **Maintain consistent prop interfaces**
4. **Follow TypeScript best practices**
5. **Use semantic HTML elements**
6. **Implement proper error boundaries**
7. **Optimize for performance with React.memo when needed**

## 🔄 State Management

The application uses React's built-in state management with custom hooks:
- **useChat**: Manages chat messages, input state, and API calls
- **Local State**: Component-specific state managed with useState
- **No External State Libraries**: Keeps the bundle size minimal

## 🌟 Future Enhancements

- [ ] Add dark mode support
- [ ] Implement message persistence
- [ ] Add user authentication
- [ ] Implement real-time updates
- [ ] Add message search functionality
- [ ] Implement message reactions
- [ ] Add file upload support
- [ ] Implement voice input/output
