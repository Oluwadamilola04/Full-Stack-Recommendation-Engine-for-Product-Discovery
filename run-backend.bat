@echo off
REM Start E-commerce Recommendation System Backend

echo.
echo ================================================
echo Starting E-commerce Recommendation Backend
echo ================================================
echo.

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERROR: %PYTHON% not found.
    echo - Run setup.bat after creating %ROOT%.venv, or install Python and recreate the venv.
    pause
    exit /b 1
)

cd /d "%ROOT%backend"

REM Run with uvicorn
call "%PYTHON%" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
