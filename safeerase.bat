@echo off
REM SafeErase Windows Launcher
REM Automatically detects and launches the best available interface

title SafeErase - Secure Data Wiping Solution

echo.
echo 🔒 SafeErase - Secure Data Wiping Solution
echo ==================================================
echo Professional-grade secure data destruction
echo with tamper-proof certificates
echo.

REM Check for Python
python3 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 not found. Please install Python 3.8 or higher.
    echo    Download from: https://python.org
    pause
    exit /b 1
)

echo ✅ Python 3 detected
echo.

REM Check for CustomTkinter
python3 -c "import customtkinter" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ CustomTkinter available - Launching full GUI...
    python3 python-ui/main.py
    goto :end
)

REM Check for Tkinter
python3 -c "import tkinter" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️ CustomTkinter not available, using basic interface...
    echo.
    echo To install full GUI dependencies, run:
    echo    pip install customtkinter pillow pyyaml
    echo.
    python3 run_safeerase.py
    goto :end
)

REM Fallback to web demo
echo ⚠️ GUI libraries not available
echo 🌐 Opening web demo instead...
echo.
if exist "demo\web_demo.html" (
    start "" "demo\web_demo.html"
    echo ✅ Web demo opened in browser
) else (
    echo ❌ Web demo not found
)

echo.
echo 🐍 Running Python demo as fallback...
if exist "run_python_demo_standalone.py" (
    python3 run_python_demo_standalone.py
) else (
    echo ❌ Python demo not found
)

:end
echo.
echo 👋 Thank you for using SafeErase!
pause
