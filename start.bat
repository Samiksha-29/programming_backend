@echo off
echo 🚀 Starting Real-Time Pair Programming API...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo  No .env file found. Using default configuration.
    echo  Copy .env.example to .env and configure if needed.
)

REM Start the server
echo.
echo    Starting FastAPI server...
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    WebSocket Test: Open websocket_test.html in browser
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
