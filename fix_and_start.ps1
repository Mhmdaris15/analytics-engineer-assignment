# Fix bcrypt compatibility and start server
Write-Host "Installing bcrypt and passlib in virtual environment..." -ForegroundColor Cyan

# Activate virtual environment and install packages
& .\venv\Scripts\Activate.ps1

# Install compatible versions
pip install "passlib[bcrypt]" bcrypt==4.0.1 --quiet

Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Write-Host ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
