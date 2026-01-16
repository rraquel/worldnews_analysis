#!/bin/bash

# Launch script for Global Conflict Analysis Interface

echo "🌍 Starting Global Conflict Analysis Interface..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create .env file from .env.example and add your API keys."
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Launch Streamlit
echo ""
echo "🚀 Launching interface..."
echo "Opening browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
