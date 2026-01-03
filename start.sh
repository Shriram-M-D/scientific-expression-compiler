#!/bin/bash
# Quick Start Script for Scientific Expression Compiler (Linux/Mac)
# This script builds the C++ compiler and starts the Flask server

echo "============================================================"
echo "Scientific Expression Compiler - Quick Start"
echo "============================================================"
echo ""

# Step 1: Check for g++ compiler
echo "[1/4] Checking for C++ compiler..."
if ! command -v g++ &> /dev/null; then
    echo "ERROR: g++ not found! Please install g++."
    exit 1
fi
echo "OK: g++ found"
echo ""

# Step 2: Build C++ compiler
echo "[2/4] Building C++ compiler..."
cd compiler
make clean > /dev/null 2>&1
make
if [ ! -f "compiler" ]; then
    echo "ERROR: Compilation failed!"
    cd ..
    exit 1
fi
echo "OK: Compiler built successfully"
cd ..
echo ""

# Step 3: Check Python and install dependencies
echo "[3/4] Setting up Python backend..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.8 or higher."
    exit 1
fi
echo "OK: Python found"

cd backend
pip3 install -q -r requirements.txt
cd ..
echo ""

# Step 4: Start the server
echo "[4/4] Starting Flask server..."
echo ""
echo "============================================================"
echo "Server will start on: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

cd backend
python3 app.py
