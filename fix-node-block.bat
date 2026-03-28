@echo off
set "ROOT=%~dp0"
set "SCRIPT=%ROOT%frontend\scripts\unblock-node-spawn.ps1"

if not exist "%SCRIPT%" (
  echo ERROR: %SCRIPT% not found.
  pause
  exit /b 1
)

powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT%"
pause
