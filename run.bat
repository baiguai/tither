@echo off

REM Church Tithing Accounting App - Setup Script (Windows)

cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Launch the app
echo Launching Tither accounting app...
python tither.py