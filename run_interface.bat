@echo off
REM Launch script for Global Conflict Analysis Interface (Windows)

echo.
echo 🌍 Starting Global Conflict Analysis Interface...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ⚠️  Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo 📦 Checking dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Please create .env file from .env.example and add your API keys.
    echo.
    pause
)

REM Launch Streamlit
echo.
echo 🚀 Launching interface...
echo Opening browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py
