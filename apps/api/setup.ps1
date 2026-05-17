# Recrea el entorno virtual si el proyecto se movió o renombró.
# Uso: .\setup.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Creando entorno virtual en apps\api\.venv ..." -ForegroundColor Cyan
if (Test-Path .venv) {
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv

Write-Host "Instalando dependencias ..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host ""
Write-Host "Listo. Activa y arranca el API:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn app.main:app --reload --port 8000"
