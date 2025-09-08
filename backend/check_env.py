#!/usr/bin/env python3
"""
Environment verification script for Mistral AI Chat Backend.

This script checks if all required dependencies are properly installed
and the environment is correctly configured.
"""

import sys
import importlib
import os
from typing import List, Tuple


def check_python_version() -> bool:
    """Check if Python version is 3.11 or higher."""
    version = sys.version_info
    required = (3, 11)
    
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if (version.major, version.minor) >= required:
        print("✅ Python version requirement met")
        return True
    else:
        print(f"❌ Python {required[0]}.{required[1]}+ required")
        return False


def check_dependencies() -> bool:
    """Check if all required dependencies are installed."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "mistralai", 
        "pydantic",
        "structlog",
        "httpx",
        "sqlalchemy",
    ]
    
    print("\nChecking dependencies:")
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed")
        return True


def check_environment_file() -> bool:
    """Check if .env file exists and has required variables."""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"\n⚠️  {env_file} file not found")
        print("Copy .env.example to .env and configure your settings")
        return False
    
    required_vars = [
        "MISTRAL_API_KEY",
        "SECRET_KEY",
        "DATABASE_URL",
    ]
    
    print(f"\n✅ {env_file} file found")
    
    # Read .env file and check for required variables
    missing_vars = []
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            for var in required_vars:
                if f"{var}=" not in content or f"{var}=your_" in content:
                    missing_vars.append(var)
    except Exception as e:
        print(f"❌ Error reading {env_file}: {e}")
        return False
    
    if missing_vars:
        print(f"⚠️  Please configure these variables in {env_file}:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("✅ Environment variables configured")
        return True


def check_virtual_environment() -> bool:
    """Check if running in a virtual environment."""
    if hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("Consider using: python -m venv venv && source venv/bin/activate")
        return False


def main():
    """Run all environment checks."""
    print("🔍 Mistral AI Chat Backend - Environment Check")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_virtual_environment(),
        check_dependencies(),
        check_environment_file(),
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 Environment setup complete! You're ready to go.")
        print("\nTo start the development server:")
        print("  uvicorn app.main:app --reload --port 8000")
        print("\nAPI documentation will be available at:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print("❌ Environment setup incomplete. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
