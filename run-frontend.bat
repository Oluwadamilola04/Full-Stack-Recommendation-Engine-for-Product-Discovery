@echo off
REM Start E-commerce Recommendation System Frontend

echo.
echo ================================================
echo Starting E-commerce Recommendation Frontend
echo ================================================
echo.

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERROR: %PYTHON% not found.
    echo - Recreate the project virtual environment and try again.
    pause
    exit /b 1
)

echo Starting stable frontend fallback on http://127.0.0.1:5173
echo Use run-react-frontend.bat when you want to test the React/Vite frontend explicitly.
echo.
cd /d "%ROOT%frontend\static"
call "%PYTHON%" -m http.server 5173 --bind 127.0.0.1

pause
