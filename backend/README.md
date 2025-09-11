# Mistral AI Chat Backend

A high-performance FastAPI backend service that integrates with Mistral AI for chat functionality and document Q&A.

## Features

- **Chat API**: Real-time chat with Mistral AI models
- **Document Processing**: PDF upload and vector search
- **Analytics**: Performance metrics and usage tracking
- **Authentication**: JWT-based user authentication
- **Rate Limiting**: API protection and fair usage

## Quick Start

### Option 1: Automated Setup (Recommended)

**macOS/Linux:**
```bash
# Make setup script executable and run
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
# Run the batch setup script
setup.bat
```

### Option 2: Manual Setup

1. **Create virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # macOS/Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   # Upgrade pip
   pip install --upgrade pip
   
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (optional)
   pip install -r requirements-dev.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

4. **Run the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   
   # Or use the Makefile (if available)
   make dev
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

### Virtual Environment Management

Always use a virtual environment for development:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Deactivate when done
deactivate
```

### Available Commands

Using the Makefile (macOS/Linux):
```bash
make help          # Show available commands
make setup         # Create virtual environment
make install       # Install dependencies
make dev           # Start development server
make test          # Run tests
make lint          # Run linting
make format        # Format code
make clean         # Clean temporary files
```

### Code Quality

```bash
# Lint code
flake8 app/
mypy app/

# Format code
black app/
isort app/

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
