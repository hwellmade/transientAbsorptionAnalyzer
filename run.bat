@echo off
echo Starting Transient Absorption Analyser...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
python -c "import sys; ver = sys.version_info; exit(0 if ver.major >= 3 and ver.minor >= 11 else 1)"
if errorlevel 1 (
    echo Error: Python 3.11 or higher is required
    echo Current Python version:
    python --version
    pause
    exit /b 1
)

REM Install or upgrade required packages
echo Installing/Upgrading required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install required packages
    echo Please run the following command manually:
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run the application
echo Starting application...
python -m transient_absorption_analyser.src.main
if errorlevel 1 (
    echo Error: Application failed to start
    pause
    exit /b 1
)

rmdir /s /q build dist
del *.spec 