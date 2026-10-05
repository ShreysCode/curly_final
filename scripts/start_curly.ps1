$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

Write-Host "=== Curly AI Backend Startup ===" -ForegroundColor Cyan

if (-not (Test-Path ".\.env")) {
    Write-Error ".env not found. Create it from .env.example first."
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python was not found on PATH."
}

try {
    $tags = Invoke-RestMethod "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
    $model = $tags.models | Where-Object { $_.name -eq "llama3.1:8b" }

    if (-not $model) {
        Write-Warning "Ollama is reachable, but llama3.1:8b was not found."
        Write-Host "Expected model: llama3.1:8b" -ForegroundColor Yellow
    } else {
        Write-Host "Ollama: OK (llama3.1:8b available)" -ForegroundColor Green
    }
}
catch {
    Write-Error "Ollama is not reachable at http://127.0.0.1:11434. Start exactly one Ollama server first."
}

Write-Host "Starting Curly on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
