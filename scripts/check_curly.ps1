$ErrorActionPreference = "Continue"

Write-Host "=== Curly AI Environment Check ===" -ForegroundColor Cyan

Write-Host "Python:" -NoNewline
python --version

Write-Host "Ollama:" -NoNewline
try {
    $tags = Invoke-RestMethod "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
    $model = $tags.models | Where-Object { $_.name -eq "llama3.1:8b" }
    if ($model) { Write-Host " OK - llama3.1:8b" -ForegroundColor Green }
    else { Write-Host " RUNNING - llama3.1:8b NOT FOUND" -ForegroundColor Yellow }
}
catch {
    Write-Host " NOT REACHABLE" -ForegroundColor Red
}

Write-Host "Curly API:" -NoNewline
try {
    $health = Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 3
    Write-Host " $($health.status)" -ForegroundColor Green
    $health | Format-List
}
catch {
    Write-Host " NOT REACHABLE" -ForegroundColor Red
}

Write-Host "Tests:" -ForegroundColor Cyan
pytest -q
