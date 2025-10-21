@echo off
echo ===================================
echo AquaRisk Monitor - Setup and Launch
echo ===================================

REM Set environment variables for the application
set FLASK_APP=run.py
set FLASK_DEBUG=True
set SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.7+ and add it to your PATH.
    pause
    exit /B 1
)

echo Using SQLite database for development...

REM Create virtual environment if it doesn't exist
IF NOT EXIST venv (
    echo Creating Python virtual environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /B 1
    )
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /B 1
)

echo Installing dependencies...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some dependencies failed to install.
    choice /C YN /M "Continue anyway?"
    IF %ERRORLEVEL% EQU 2 exit /B 1
)

REM Initialize the database
echo Initializing the database with default data...
python -c "from app import create_app, db; from run import init_db; app = create_app(); app.app_context().push(); db.create_all(); init_db()"
IF %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to initialize database.
    choice /C YN /M "Continue anyway?"
    IF %ERRORLEVEL% EQU 2 exit /B 1
)

REM Clean any potential cached files
echo Cleaning cache to ensure fresh styles are loaded...
IF EXIST "app/static/__pycache__" rmdir /S /Q "app/static/__pycache__"
IF EXIST "app/__pycache__" rmdir /S /Q "app/__pycache__"

echo.
echo ============================================
echo Setup complete! Starting AquaRisk Monitor...
echo ============================================
echo.
echo Default login credentials:
echo   Admin: admin@aquarisk.org / Admin@123
echo   Clinic: clinic@aquarisk.org / Clinic@123
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the application
python run.py

echo Application has stopped.
pause
