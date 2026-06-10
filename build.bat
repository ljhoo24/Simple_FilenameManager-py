@echo off
cd /d "%~dp0FileNameManager"

rem Install PyInstaller if missing
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install PyInstaller. Run: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo.
echo === BUILD START ===
python -m PyInstaller main.spec -y
if errorlevel 1 (
    echo.
    echo === BUILD FAILED ===
    pause
    exit /b 1
)

echo.
echo === BUILD OK ===
echo Output: %CD%\dist\main.exe
pause
