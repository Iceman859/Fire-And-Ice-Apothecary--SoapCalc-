@echo off
REM SoapCalc - Soap Making Calculator
REM This batch file runs the application using the Python virtual environment

cd /d "%~dp0"

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Run the application
python main.py

REM Pause if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Error running application. Press any key to exit...
    pause
)
