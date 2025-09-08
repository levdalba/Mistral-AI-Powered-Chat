# Mistral AI Chat Frontend

A modern Next.js application providing an intuitive chat interface for the Mistral AI Chat & Knowledge Assistant.

## Features

- **Modern Chat Interface**: Sleek, responsive design similar to "Mistral le Chat"
- **Real-time Conversations**: Seamless interaction with AI models
- **Document Q&A**: Upload and query documents with natural language
- **Dark/Light Theme**: Toggle between themes for optimal user experience
- **Performance Dashboard**: Monitor response times and usage metrics
- **Mobile Responsive**: Optimized for all device sizes

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand for global state
- **Storage**: IndexedDB for local conversation history
- **Icons**: Lucide React icons
- **Animations**: Framer Motion

## Quick Start

1. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser**
   - Navigate to http://localhost:3000

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (dashboard)/       # Dashboard routes
│   ├── chat/             # Chat interface
│   ├── documents/        # Document management
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
│
├── components/            # Reusable UI components
│   ├── ui/               # shadcn/ui components
│   ├── chat/             # Chat-specific components
│   ├── document/         # Document-related components
│   └── analytics/        # Analytics components
│
├── lib/                  # Utilities and configurations
│   ├── api.ts           # API client
│   ├── storage.ts       # IndexedDB wrapper
│   ├── utils.ts         # Utility functions
│   └── types.ts         # TypeScript types
│
├── hooks/                # Custom React hooks
├── stores/               # Zustand stores
└── public/               # Static assets
```

## Environment Variables

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000

# Application Settings
NEXT_PUBLIC_APP_NAME="Mistral AI Chat"
NEXT_PUBLIC_MAX_FILE_SIZE=10485760
NEXT_PUBLIC_SUPPORTED_FORMATS=pdf,txt,docx

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id

# Feature Flags
NEXT_PUBLIC_ENABLE_DOCUMENT_QA=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

## Development

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Run tests
npm run test
```

### Building

```bash
# Build for production
npm run build

# Start production server
npm run start
```

## Deployment

### Vercel (Recommended)

1. **Connect repository to Vercel**
2. **Set environment variables in Vercel dashboard**
3. **Deploy automatically on push to main**

```bash
# Manual deployment
vercel --prod
```

### Other Platforms

```bash
# Build static files
npm run build
npm run export

# Deploy static files to your hosting provider
```

## Features

### Chat Interface

- Real-time messaging with Mistral AI
- Conversation history and persistence
- Message formatting and markdown support
- Typing indicators and loading states
- Error handling and retry mechanisms

### Document Q&A

- Drag & drop file upload
- PDF, TXT, and DOCX support
- Document preview and management
- Semantic search and Q&A
- Source attribution and citations

### Analytics Dashboard

- Performance metrics visualization
- Usage statistics and trends
- System health monitoring
- User analytics and insights

### User Experience

- Responsive design for all devices
- Dark/light theme toggle
- Keyboard shortcuts and accessibility
- Smooth animations and transitions
- Offline support for conversations

## Performance

- **First Load**: < 3s on slow networks
- **Lighthouse Score**: 95+ across all metrics
- **Bundle Size**: Optimized with tree shaking
- **Caching**: Aggressive caching for static assets

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) file for details.
