# Mistral AI Chat Backend

A high-performance FastAPI backend service that integrates with Mistral AI for chat functionality and document Q&A.

## Features

- **Chat API**: Real-time chat with Mistral AI models
- **Document Processing**: PDF upload and vector search
- **Analytics**: Performance metrics and usage tracking
- **Authentication**: JWT-based user authentication
- **Rate Limiting**: API protection and fair usage

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Run the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **View API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── dependencies.py      # Shared dependencies
│   │
│   ├── api/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat endpoints
│   │   ├── documents.py     # Document endpoints
│   │   └── analytics.py     # Analytics endpoints
│   │
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   └── analytics_service.py
│   │
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── document.py
│   │   └── analytics.py
│   │
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── logger.py
│       ├── validators.py
│       └── exceptions.py
│
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── Dockerfile              # Container configuration
```

## Environment Variables

```bash
# Mistral AI Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest

# Database Configuration
DATABASE_URL=sqlite:///./mistral_chat.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# File Upload
MAX_FILE_SIZE_MB=10
UPLOAD_DIRECTORY=./uploads

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## Development

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Run tests
pytest
pytest --cov=app tests/
```

### Database Migration

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

## Deployment

### Docker

```bash
# Build image
docker build -t mistral-chat-backend .

# Run container
docker run -p 8000:8000 mistral-chat-backend
```

### Production

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
