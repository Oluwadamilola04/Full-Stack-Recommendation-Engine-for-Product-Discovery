@echo off
REM Start E-commerce Recommendation System (Backend + Frontend)

echo.
echo ================================================
echo E-commerce Recommendation System - Full Stack
echo ================================================
echo.
echo IMPORTANT: This will start both backend and frontend
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:5173
echo API Docs available at: http://localhost:8000/docs
echo.

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERROR: %PYTHON% not found.
    echo - Run setup.bat after creating %ROOT%.venv, or install Python and recreate the venv.
    pause
    exit /b 1
)

REM Start Backend in new window
echo Starting Backend...
start "Backend - E-commerce Recommendation System" cmd /k cd /d "%ROOT%backend" ^&^& "%PYTHON%" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start Frontend in new window
echo Starting Frontend...
start "Frontend - E-commerce Recommendation System" cmd /k cd /d "%ROOT%" ^&^& call "%ROOT%run-frontend.bat"

echo.
echo ================================================
echo Both services are starting in separate windows...
echo ================================================
echo.
echo Backend API:     http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Frontend:        http://localhost:5173
echo.
pause
