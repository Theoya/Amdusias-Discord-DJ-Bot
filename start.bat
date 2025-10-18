@echo off
echo ========================================
echo   Amdusias Discord DJ Bot
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting bot...
echo.
python main.py

pause
