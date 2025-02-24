@echo off
echo Starting Transient Absorption Analyser...

REM Try running with Python directly (recommended for users)
python -m transient_absorption_analyser.src.main
if not errorlevel 1 (
    echo Application started successfully!
    exit /b 0
)

REM If Python direct method fails, try Poetry (for developers)
where poetry >nul 2>nul
if %errorlevel% equ 0 (
    echo Trying to run with Poetry...
    poetry run analyzer
    if not errorlevel 1 (
        echo Application started successfully!
        exit /b 0
    )
)

REM If both methods fail, show error message
echo.
echo Error running the application. Please ensure:
echo 1. Python 3.11 or higher is installed and added to PATH
echo 2. Required packages are installed (pip install -r requirements.txt)
echo.
echo For detailed installation instructions, please see README.md
pause
exit /b 1

rmdir /s /q build dist
del *.spec 