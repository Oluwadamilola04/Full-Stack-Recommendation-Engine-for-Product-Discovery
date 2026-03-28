$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).
  IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
  Write-Host "Requesting administrator approval to update Windows process mitigations for node.exe..." -ForegroundColor Yellow
  Start-Process powershell.exe -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

Import-Module ProcessMitigations -ErrorAction Stop

Write-Host ""
Write-Host "Checking node.exe mitigation settings..." -ForegroundColor Cyan

try {
  Set-ProcessMitigation -Name node.exe -Disable DisallowChildProcessCreation, AuditChildProcess -ErrorAction Stop
  Write-Host ""
  Write-Host "Done." -ForegroundColor Green
  Write-Host "Child-process blocking has been disabled for node.exe." -ForegroundColor Green
  Write-Host "Close and reopen VS Code or your terminal, then run run-frontend.bat again." -ForegroundColor Green
} catch {
  Write-Host ""
  Write-Host "Could not update the mitigation settings automatically." -ForegroundColor Red
  Write-Host $_.Exception.Message -ForegroundColor Red
  Write-Host ""
  Write-Host "Manual path:" -ForegroundColor Yellow
  Write-Host "Windows Security > App & browser control > Exploit protection settings > Program settings" -ForegroundColor Yellow
  Write-Host "Add C:\Program Files\nodejs\node.exe and turn off Child process creation." -ForegroundColor Yellow
  exit 1
}
