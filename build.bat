@echo off
echo Installing project dependencies...
poetry install
if errorlevel 1 (
    echo Failed to install dependencies
    exit /b 1
)

echo Getting Poetry environment information...
for /f "tokens=* USEBACKQ" %%F in (`poetry env info --path`) do set POETRY_VENV=%%F

echo Converting logo to icon...
poetry run python -c "from PIL import Image; img = Image.open('transient_absorption_analyser/resources/logo.png'); img.save('transient_absorption_analyser/resources/icon.ico')"

echo Building executable...
poetry run pyinstaller ^
    --name TransientAbsorptionAnalyser ^
    --onedir ^
    --windowed ^
    --clean ^
    --icon=transient_absorption_analyser/resources/icon.ico ^
    --add-data "transient_absorption_analyser/resources/*;resources/" ^
    --hidden-import=numpy ^
    --hidden-import=pandas ^
    --hidden-import=matplotlib ^
    --hidden-import=scipy ^
    --hidden-import=PySide6 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtGui ^
    --collect-all PySide6 ^
    --collect-all matplotlib ^
    --collect-data matplotlib ^
    --collect-data scipy ^
    --collect-data numpy ^
    --collect-data pandas ^
    --add-binary "%POETRY_VENV%\Lib\site-packages\PySide6\plugins\platforms\*;platforms/" ^
    --add-binary "%POETRY_VENV%\Lib\site-packages\PySide6\plugins\styles\*;styles/" ^
    --add-binary "%POETRY_VENV%\Lib\site-packages\PySide6\Qt6Core.dll;." ^
    --add-binary "%POETRY_VENV%\Lib\site-packages\PySide6\Qt6Gui.dll;." ^
    --add-binary "%POETRY_VENV%\Lib\site-packages\PySide6\Qt6Widgets.dll;." ^
    transient_absorption_analyser/src/main.py

if errorlevel 1 (
    echo Build failed! Please check the error messages above.
    pause
    exit /b 1
)

echo Build complete! Executable can be found in the dist/TransientAbsorptionAnalyser folder.
echo.
echo Note: The executable is now in a folder. Distribute the entire folder for the application to work.
pause 