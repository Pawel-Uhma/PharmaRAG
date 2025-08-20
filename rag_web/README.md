# PharmaRAG - Super-Modern RAG Chat UI

A premium, minimal, and fast RAG chatbot with an always-visible Context Inspector built with Next.js 15, React 19, and Tailwind CSS 4.

## ✨ Features

### 🎨 **Modern Design System**
- **Dark mode by default** with light mode toggle
- **Design tokens** with CSS custom properties
- **Smooth transitions** and micro-animations (<200ms)
- **WCAG 2.2 AA** accessible design
- **Responsive layout** for all screen sizes

### 🏗️ **3-Pane Layout**
- **Left Sidebar**: Conversation management with history
- **Center**: Main chat interface with citation chips
- **Right Panel**: Context Inspector with multiple tabs

### 🔍 **Rich Context UX**
- **Sources Tab**: View document sources with relevance scores
- **Chunks Tab**: Examine text chunks used for responses
- **Inspector Tab**: Detailed metadata and analysis
- **History Tab**: Response metadata and processing info

### 💬 **Enhanced Chat Experience**
- **Inline citation chips** linking to sources
- **Conversation management** with titles and history
- **Optimistic send** for snappy feel
- **Skeleton loaders** during processing
- **Real-time updates** with smooth scrolling

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
cd rag_web
npm install
npm run dev
```

### Environment Setup
Make sure your RAG service is running on `http://localhost:8000` or update the API endpoint in `src/hooks/useChat.ts`.

## 🏗️ Architecture

### Core Components
- **`ConversationsSidebar`**: Manages chat history and conversations
- **`ChatContainer`**: Main chat interface with messages
- **`ContextPanel`**: Right-side context inspector
- **`Message`**: Enhanced message component with citations
- **`ChatInput`**: Smart input with character count and validation

### State Management
- **`useChat`**: Enhanced hook with conversation management
- **`ThemeContext`**: Dark/light mode state
- **Local storage**: Theme preference persistence

### Design System
- **CSS Custom Properties**: Theme variables for consistent styling
- **Tailwind CSS 4**: Utility-first CSS framework
- **Custom animations**: Smooth transitions and micro-interactions

## 🎯 Usage

### Starting a Conversation
1. Click the "+" button in the left sidebar
2. Type your pharmaceutical question
3. Press Enter or click Send

### Exploring Context
1. Click on citation chips `[1]`, `[2]`, etc. in responses
2. Use the right panel tabs to explore:
   - **Sources**: Document origins and metadata
   - **Chunks**: Text segments used for answers
   - **Inspector**: Detailed analysis
   - **History**: Processing information

### Managing Conversations
- **Edit titles**: Click the edit icon on conversation items
- **Delete conversations**: Use the trash icon
- **Switch between chats**: Click on any conversation in the sidebar

## 🔧 Customization

### Theme Colors
Edit `src/styles/theme.css` to customize the color scheme:

```css
:root {
  --bg: #0c0f14;
  --accent: #8ab4ff;
  --ring: #7aa2ff;
  /* ... more variables */
}
```

### Adding New Context Tabs
Extend the `ContextPanel` component to add new inspection tabs:

```tsx
const tabs = [
  { id: 'sources', label: 'Sources', icon: '📚' },
  { id: 'chunks', label: 'Chunks', icon: '🔍' },
  { id: 'inspector', label: 'Inspector', icon: '🔬' },
  { id: 'history', label: 'History', icon: '⏱️' },
  { id: 'custom', label: 'Custom', icon: '✨' }, // Add new tab
];
```

## 🧪 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Style
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Automatic code formatting
- **Component structure**: Functional components with hooks

## 📱 Responsive Design

The UI automatically adapts to different screen sizes:
- **Desktop**: Full 3-pane layout
- **Tablet**: Collapsible sidebars
- **Mobile**: Stacked layout with navigation

## 🔒 Security

- **Input validation**: Sanitized user inputs
- **API security**: Secure communication with RAG service
- **XSS protection**: React's built-in security features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Next.js 15** for the React framework
- **Tailwind CSS 4** for the design system
- **React 19** for the UI library
- **Pharmaceutical community** for domain expertise
