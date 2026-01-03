@echo off
REM Quick Start Script for Scientific Expression Compiler
REM This script builds the C++ compiler and starts the Flask server

echo ============================================================
echo Scientific Expression Compiler - Quick Start
echo ============================================================
echo.

REM Step 1: Check for g++ compiler
echo [1/4] Checking for C++ compiler...
g++ --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: g++ not found in PATH!
    echo.
    echo To build the C++ compiler, you need g++. Options:
    echo   1. Install MinGW-w64: https://www.mingw-w64.org/
    echo   2. Use WSL with g++ installed
    echo   3. Add g++ to your PATH if already installed
    echo.
    echo If compiler.exe already exists, we'll skip building.
    echo.
    set SKIP_BUILD=1
) else (
    echo OK: g++ found
    set SKIP_BUILD=0
)
echo.

REM Step 2: Build C++ compiler
echo [2/4] Building C++ compiler...

if "%SKIP_BUILD%"=="1" (
    if exist compiler\compiler.exe (
        echo Compiler already exists, skipping build
        echo OK: Using existing compiler.exe
    ) else (
        echo ERROR: g++ not found and compiler.exe does not exist!
        echo Please install g++ and run this script again, or build manually.
        echo.
        pause
        exit /b 1
    )
) else (
    cd compiler
    if exist compiler.exe del compiler.exe
    if exist *.o del *.o

    echo Compiling source files...
    g++ -std=c++17 -Wall -Wextra -O2 -c lexer.cpp -o lexer.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to compile lexer.cpp
        cd ..
        pause
        exit /b 1
    )
    
    g++ -std=c++17 -Wall -Wextra -O2 -c parser.cpp -o parser.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to compile parser.cpp
        cd ..
        pause
        exit /b 1
    )
    
    g++ -std=c++17 -Wall -Wextra -O2 -c ast.cpp -o ast.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to compile ast.cpp
        cd ..
        pause
        exit /b 1
    )
    
    g++ -std=c++17 -Wall -Wextra -O2 -c evaluator.cpp -o evaluator.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to compile evaluator.cpp
        cd ..
        pause
        exit /b 1
    )
    
    g++ -std=c++17 -Wall -Wextra -O2 -c calculus.cpp -o calculus.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to compile calculus.cpp
        cd ..
        pause
        exit /b 1
    )
    
    g++ -std=c++17 -Wall -Wextra -O2 -c main.cpp -o main.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to compile main.cpp
        cd ..
        pause
        exit /b 1
    )

    echo Linking executable...
    g++ -std=c++17 -Wall -Wextra -O2 -o compiler.exe lexer.o parser.o ast.o evaluator.o calculus.o main.o
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to link compiler.exe
        cd ..
        pause
        exit /b 1
    )

    if not exist compiler.exe (
        echo ERROR: Compilation failed!
        cd ..
        pause
        exit /b 1
    )
    
    echo Cleaning up object files...
    del *.o >nul 2>&1
    
    echo OK: Compiler built successfully
    cd ..
)
echo.

REM Step 3: Check Python and install dependencies
echo [3/4] Setting up Python backend...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo OK: Python found

cd backend
python -m pip install -q -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Failed to install some dependencies
)
cd ..
echo.

REM Step 4: Start the server
echo [4/4] Starting Flask server...
echo.
echo ============================================================
echo Server will start on: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd backend
python app.py
