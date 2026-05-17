# Libera el puerto y arranca el API en desarrollo.
# Uso: .\dev.ps1
#      .\dev.ps1 -Port 8001

param([int]$Port = 8000)

$ErrorActionPreference = "SilentlyContinue"
Set-Location $PSScriptRoot

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $listeners) {
    $pid = $conn.OwningProcess
    if ($pid -and $pid -ne 0) {
        Write-Host "Puerto $Port ocupado por PID $pid — terminando proceso..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
    }
}

Start-Sleep -Seconds 1

if (-not (Test-Path .\.venv\Scripts\uvicorn.exe)) {
    Write-Host "No existe .venv. Ejecuta primero: .\setup.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Arrancando API en http://127.0.0.1:$Port ..." -ForegroundColor Green
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port $Port --host 127.0.0.1
