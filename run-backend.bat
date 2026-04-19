@echo off
echo ========================================
echo   OGB Game Server - Starting...
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Starting server on http://localhost:5000
echo ========================================
echo.

python app.py
