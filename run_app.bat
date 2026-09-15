@echo off
setlocal

REM Run this file by double-clicking it, or type run_app.bat in Command Prompt.
REM It always uses this project's isolated .venv Python interpreter.
cd /d "%~dp0"
set "APP_PY=%CD%\.venv\Scripts\python.exe"

if not exist "%APP_PY%" (
    echo Creating the project virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

"%APP_PY%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Preparing pip in the virtual environment...
    "%APP_PY%" -m ensurepip --upgrade
    if errorlevel 1 goto :error
)

echo Checking project dependencies...
"%APP_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Starting AI Startup Idea Validator...
"%APP_PY%" -m streamlit run ui\streamlit_app.py
goto :eof

:error
echo.
echo The app could not start. Review the error above and try again.
pause
exit /b 1
