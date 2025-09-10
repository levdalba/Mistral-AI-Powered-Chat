#!/bin/bash

# Test script for Mistral AI Chat App
# Tests both backend API and frontend connectivity

echo "🚀 Testing Mistral AI Chat App"
echo "================================="

# Test 1: Backend Health Check
echo -n "1. Backend Health Check: "
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ PASSED"
else
    echo "❌ FAILED - Backend not responding"
    exit 1
fi

# Test 2: Backend Chat API
echo -n "2. Backend Chat API: "
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat/message \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, test message", "model": "mistral-large-latest"}')

if echo "$CHAT_RESPONSE" | grep -q "assistant"; then
    echo "✅ PASSED"
    echo "   Response: $(echo "$CHAT_RESPONSE" | jq -r '.message.content' 2>/dev/null || echo 'JSON parsing failed')"
else
    echo "❌ FAILED - Chat API not working"
    echo "   Response: $CHAT_RESPONSE"
fi

# Test 3: Frontend Accessibility
echo -n "3. Frontend Server: "
if curl -s http://localhost:3001 >/dev/null; then
    echo "✅ PASSED"
else
    if curl -s http://localhost:3000 >/dev/null; then
        echo "✅ PASSED (port 3000)"
    else
        echo "❌ FAILED - Frontend not responding"
    fi
fi

# Test 4: CORS Configuration
echo -n "4. CORS Configuration: "
CORS_RESPONSE=$(curl -s -I -X OPTIONS http://localhost:8000/api/chat/message \
    -H "Origin: http://localhost:3001" \
    -H "Access-Control-Request-Method: POST")

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
    echo "✅ PASSED"
else
    # Try with port 3000
    CORS_RESPONSE=$(curl -s -I -X OPTIONS http://localhost:8000/api/chat/message \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST")
    if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
        echo "✅ PASSED (port 3000)"
    else
        echo "❌ FAILED - CORS not configured properly"
    fi
fi

echo ""
echo "🎉 Testing Complete!"
echo ""
echo "📱 Frontend: http://localhost:3001 or http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
