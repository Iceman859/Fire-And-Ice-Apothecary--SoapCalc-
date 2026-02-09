@echo off
REM Quick shortcut to run SoapCalc
REM This script can be pinned to the taskbar for easy access

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Run the Python script with the virtual environment's Python
start "" "%~dp0.venv\Scripts\python.exe" main.py
