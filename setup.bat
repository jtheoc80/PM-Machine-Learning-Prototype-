@echo off
REM Setup script for Pressure Relief Valve LLM Agent (Windows)

echo ================================================
echo   Pressure Relief Valve LLM Agent - Setup
echo ================================================
echo.

REM Check Python version
echo Checking Python version...
python --version 2>&1 | findstr /R "Python 3\.[89]" >nul || python --version 2>&1 | findstr /R "Python 3\.1[0-9]" >nul
if errorlevel 1 (
    echo Error: Python 3.8 or higher is required
    python --version
    pause
    exit /b 1
)
echo OK: Python version check passed
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo OK: Virtual environment created
) else (
    echo OK: Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo OK: Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo OK: pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
echo (This may take a few minutes...)
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed
echo.

REM Create necessary directories
echo Creating directories...
if not exist "data\uploads" mkdir data\uploads
if not exist "data\cache" mkdir data\cache
if not exist "models" mkdir models
if not exist "logs" mkdir logs
type nul > data\uploads\.gitkeep
type nul > data\cache\.gitkeep
type nul > models\.gitkeep
echo OK: Directories created
echo.

REM Create sample dataset
echo Creating sample dataset...
python main.py --create-sample >nul 2>&1
echo OK: Sample dataset created
echo.

echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo To get started:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run the demo:
echo      python demo.py
echo.
echo   3. Or start interactive mode:
echo      python main.py --interactive
echo.
echo   4. Or start the web API:
echo      python api.py
echo.
echo For more information, see README.md
echo.
pause
