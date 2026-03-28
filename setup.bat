@echo off
REM E-commerce Recommendation System - Initial Setup Script for Windows

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

echo.
echo Starting E-commerce Recommendation System Setup...
echo.

REM Prefer the repo's venv so we don't depend on global python.exe PATH aliases.
if not exist "%PYTHON%" (
    echo ERROR: %PYTHON% not found.
    echo - Install Python 3.11+ and create a venv at %ROOT%.venv, or recreate it if missing.
    exit /b 1
)

echo Using Python: %PYTHON%

REM Backend setup
echo.
echo Setting up Backend...
cd /d "%ROOT%backend"

echo Installing backend dependencies...
call "%PYTHON%" -m pip install --upgrade pip
call "%PYTHON%" -m pip install -r requirements.txt
if exist "requirements-ml.txt" (
    echo Installing optional ML dependencies (numpy/pandas/scikit-learn)...
    call "%PYTHON%" -m pip install -r requirements-ml.txt
)

if not exist ".env" (
    echo Creating backend\.env from .env.example...
    copy .env.example .env
    echo NOTE: SQLite works by default; edit backend\.env to use Postgres/Redis if desired.
)

cd /d "%ROOT%"

REM Frontend setup (optional)
echo.
echo Setting up Frontend...
cd /d "%ROOT%frontend"

where node >nul 2>&1
if errorlevel 1 (
    if exist "C:\Program Files\nodejs\node.exe" (
        set "PATH=C:\Program Files\nodejs;%PATH%"
    ) else (
        echo NOTE: Node.js is not installed or not on PATH, skipping frontend install.
        echo - Install Node.js 20+ then run: cd frontend ^&^& npm install
    cd /d "%ROOT%"
    echo.
    echo Setup complete (backend only).
    exit /b 0
    )
)

echo Installing frontend dependencies...
call npm install

cd /d "%ROOT%"

echo.
echo Setup complete!
echo.
echo Run backend:
echo   cd backend ^&^& ..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
echo.
echo Run frontend:
echo   cd frontend ^&^& npm run dev
