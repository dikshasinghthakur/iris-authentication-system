#!/bin/bash
# Iris Authentication System - Unix/Linux Startup Script

echo ""
echo "========================================"
echo "  IRIS AUTHENTICATION SYSTEM v1.0"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

echo "[INFO] Python found:"
python3 --version
echo ""

# Check dependencies
echo "[INFO] Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "[WARNING] Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "[SUCCESS] All dependencies installed"
echo ""

# Start backend
echo "[INFO] Starting Backend Server (Flask)..."
cd backend
python3 app.py &
BACKEND_PID=$!
echo "[SUCCESS] Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend
sleep 3

# Start GUI
echo "[INFO] Starting GUI Application..."
cd ../gui
python3 gui.py

# Cleanup
kill $BACKEND_PID 2>/dev/null
