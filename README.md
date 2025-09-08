# Mistral AI-Powered Chat & Knowledge Assistant

A full-stack web application that combines the power of Mistral AI with modern web technologies to create an intelligent chat interface with document Q&A capabilities.

## 🚀 Features

### Chat Interface
- **Modern Chat UI**: Built with Next.js and Tailwind CSS, similar to "Mistral le Chat"
- **Real-time Conversations**: Seamless interaction with Mistral AI models
- **Theme Support**: Dark/light mode toggle for enhanced user experience
- **Conversation History**: Persistent chat history with IndexedDB

### Document Q&A
- **PDF Upload**: Upload and process PDF documents
- **Semantic Search**: Vector embeddings for intelligent document search
- **Contextual Answers**: Ask questions about uploaded documents
- **Smart Chunking**: Efficient text processing and storage

### Developer Dashboard
- **Performance Metrics**: Response time and token usage tracking
- **Model Analytics**: Latency monitoring and quality scores
- **Usage Statistics**: Comprehensive analytics dashboard

## 🏗️ Architecture

```
mistral-chat-assistant/
├── frontend/                 # Next.js TypeScript application
│   ├── app/                 # App Router structure
│   ├── components/          # Reusable UI components
│   ├── lib/                 # Utilities and configurations
│   └── public/              # Static assets
│
├── backend/                  # FastAPI Python application
│   ├── app/                 # Application core
│   ├── services/            # Business logic services
│   ├── models/              # Data models and schemas
│   └── utils/               # Helper utilities
│
├── docs/                    # Documentation
└── deployment/             # Deployment configurations
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Storage**: IndexedDB for local data

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI Integration**: Mistral SDK + vLLM
- **Vector Storage**: FAISS + SQLite
- **Documentation**: Auto-generated OpenAPI docs

### Deployment
- **Frontend**: Vercel
- **Backend**: Railway/Render
- **Database**: PostgreSQL (production)
- **Monitoring**: Built-in analytics

## 🚦 Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/levdalba/Mistral-AI-Powered-Chat.git
   cd Mistral-AI-Powered-Chat
   ```

2. **Set up environment variables**
   ```bash
   # Copy environment templates
   cp frontend/.env.example frontend/.env.local
   cp backend/.env.example backend/.env
   
   # Add your Mistral API key and other configurations
   ```

3. **Start the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

4. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

## 🔧 Development Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `hotfix/*`: Critical bug fixes

### Commit Convention
Following conventional commits for clean history:
```
feat: add document upload functionality
fix: resolve chat message ordering issue
docs: update API documentation
style: improve chat bubble design
refactor: optimize embedding service
test: add unit tests for chat service
```

### Code Quality
- **Linting**: ESLint + Prettier (Frontend), Black + Flake8 (Backend)
- **Type Safety**: TypeScript strict mode, Python type hints
- **Testing**: Jest + Testing Library (Frontend), Pytest (Backend)
- **Pre-commit Hooks**: Husky for automated checks

## 📊 API Endpoints

### Chat Service
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history` - Retrieve chat history
- `DELETE /api/chat/history` - Clear chat history

### Document Service
- `POST /api/documents/upload` - Upload document
- `POST /api/documents/query` - Query document
- `GET /api/documents/list` - List uploaded documents
- `DELETE /api/documents/{id}` - Delete document

### Analytics Service
- `GET /api/analytics/metrics` - Get performance metrics
- `GET /api/analytics/usage` - Get usage statistics

## 🚀 Deployment

### Frontend (Vercel)
```bash
# Automatic deployment on push to main
vercel --prod
```

### Backend (Railway)
```bash
# Connect repository and deploy
railway login
railway link
railway up
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

## 📈 Performance

- **Response Time**: < 2s for chat responses
- **File Upload**: Supports files up to 10MB
- **Concurrent Users**: Optimized for 100+ concurrent users
- **Embedding Speed**: < 1s for document processing

## 🔒 Security

- API rate limiting
- Input validation and sanitization
- CORS configuration
- Environment variable protection
- Secure file upload handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for the powerful language models
- [Vercel](https://vercel.com/) for frontend hosting
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python framework

---

**Built with ❤️ for Mistral AI Internship Application**
