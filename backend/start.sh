#!/bin/bash
# Render startup script for FastAPI

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
