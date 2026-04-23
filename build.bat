@echo off
REM Build script for tither.py
REM Creates a standalone Windows executable using PyInstaller

echo Building tither.py for Windows...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>NUL
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Check if the Python file exists
if not exist "tither.py" (
    echo Error: tither.py not found in current directory
    exit /b 1
)

REM Build the executable
echo Creating standalone executable...
pyinstaller --onefile --name tither --windowed --clean tither.py

echo.
echo Build complete!
echo Executable created: dist\tither.exe
echo.
echo To run: dist\tither.exe

pause