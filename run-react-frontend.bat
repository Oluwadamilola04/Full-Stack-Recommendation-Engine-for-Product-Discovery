@echo off
REM Start the React/Vite frontend explicitly

echo.
echo ================================================
echo Starting React/Vite Frontend
echo ================================================
echo.

set "ROOT=%~dp0"
set "NODE=C:\Program Files\nodejs\node.exe"
set "NPM=C:\Program Files\nodejs\npm.cmd"

if not exist "%NODE%" (
    echo ERROR: %NODE% not found.
    pause
    exit /b 1
)

if not exist "%NPM%" (
    echo ERROR: %NPM% not found.
    pause
    exit /b 1
)

cd /d "%ROOT%frontend"
call "%NODE%" "%ROOT%frontend\scripts\check-node-spawn.js"
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo Starting React frontend on http://127.0.0.1:5173
echo.
call "%NPM%" run dev -- --host 127.0.0.1
pause
