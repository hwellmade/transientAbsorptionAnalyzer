@echo off
echo Starting Transient Absorption Analyser...
poetry run analyzer
if errorlevel 1 (
    echo Application failed to start
    exit /b 1
)

REM Try running with Python directly (recommended for users)
python -m transient_absorption_analyser.src.main
if not errorlevel 1 goto :eof

REM If Python fails, try Poetry (for developers)
poetry run analyzer
if not errorlevel 1 goto :eof

REM If both methods fail, show error message
echo.
echo Error running the application. Please ensure:
echo 1. Python 3.11 is installed and added to PATH
echo 2. Required packages are installed (pip install -r requirements.txt)
echo.
echo See README.md for detailed installation instructions.
pause

rmdir /s /q build dist
del *.spec 