#!/bin/bash

echo "Starting Real-Time Pair Programming API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Using default configuration."
    echo "   Copy .env.example to .env and configure if needed."
fi

# Start the server
echo ""
echo "✅ Starting FastAPI server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   WebSocket Test: Open websocket_test.html in browser"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
