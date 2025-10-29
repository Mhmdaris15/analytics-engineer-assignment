# Analytics Engineer API - PowerShell Start Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Analytics Engineer API Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if requirements are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$requiresInstall = $false

try {
    $fastapi = python -c "import fastapi; print(fastapi.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $requiresInstall = $true
    }
} catch {
    $requiresInstall = $true
}

if ($requiresInstall) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
}

# Create data directory if it doesn't exist
if (-Not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
}

# Start the server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting API Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API will be available at:" -ForegroundColor Yellow
Write-Host "  • http://localhost:8000" -ForegroundColor White
Write-Host "  • http://localhost:8000/docs (Interactive API documentation)" -ForegroundColor White
Write-Host "  • http://localhost:8000/redoc (Alternative documentation)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
