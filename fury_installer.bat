@echo off
title Fury Installer
echo ========================================
echo           FURY INSTALLER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install required packages
echo Installing pyMeow...
pip install pyMeow

echo Installing requests...
pip install requests

echo Installing mysql-connector-python...
pip install mysql-connector-python

echo Installing websocket-client...
pip install websocket-client

echo Installing psutil...
pip install psutil

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo ========================================
echo    DEPENDENCIES INSTALLED SUCCESSFULLY
echo ========================================
echo.
echo You can now run build.bat to compile Fury
echo.
pause