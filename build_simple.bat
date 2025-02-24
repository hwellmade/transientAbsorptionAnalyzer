@echo off
echo Building executable...
poetry run pyinstaller ^
    --name TransientAbsorptionAnalyser ^
    --onefile ^
    --windowed ^
    --clean ^
    --hidden-import PySide6 ^
    --hidden-import numpy ^
    --hidden-import pandas ^
    --hidden-import matplotlib ^
    --hidden-import scipy ^
    transient_absorption_analyser/src/main.py

if errorlevel 1 (
    echo Build failed! Please check the error messages above.
    pause
    exit /b 1
)

echo Build complete! Executable can be found in the dist folder.
pause 