@echo off
REM Iris Authentication System - Windows Startup Script

title Iris Authentication System
color 0B
cls

echo.
echo ========================================
echo   IRIS AUTHENTICATION SYSTEM v1.0
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dependencies not found. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [SUCCESS] All dependencies installed
echo.

REM Start backend
echo [INFO] Starting Backend Server (Flask)...
echo.
cd backend
start "Iris Auth Backend" cmd /k "python app.py"
echo [SUCCESS] Backend started on http://localhost:5000
echo.

REM Wait for backend to initialize
timeout /t 3

REM Start GUI
echo [INFO] Starting GUI Application...
cd ..\gui
python gui.py

pause
