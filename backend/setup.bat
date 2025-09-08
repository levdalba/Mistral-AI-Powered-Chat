@echo off
REM Backend Virtual Environment Setup Script for Windows
REM This script creates and configures a Python virtual environment for the backend

echo 🚀 Setting up Mistral AI Chat Backend Environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
echo ✅ Virtual environment created

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo 🎉 Backend environment setup complete!
echo.
echo To activate the environment in the future, run:
echo   venv\Scripts\activate
echo.
echo To start the development server:
echo   uvicorn app.main:app --reload --port 8000
echo.
echo To deactivate the environment:
echo   deactivate
pause
