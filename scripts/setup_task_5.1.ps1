# Task 5.1 Setup Script
# Run this script to install dependencies for keyword extraction

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Task 5.1: Keyword Extraction Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated!" -ForegroundColor Yellow
    Write-Host "Please activate your virtual environment first:" -ForegroundColor Yellow
    Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✓ Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Install spaCy
Write-Host "Installing spaCy..." -ForegroundColor Cyan
pip install spacy==3.6.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install spaCy" -ForegroundColor Red
    exit 1
}

Write-Host "✓ spaCy installed successfully" -ForegroundColor Green
Write-Host ""

# Download spaCy English model
Write-Host "Downloading spaCy English language model..." -ForegroundColor Cyan
python -m spacy download en_core_web_sm

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to download spaCy model" -ForegroundColor Red
    exit 1
}

Write-Host "✓ spaCy model downloaded successfully" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Cyan
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spaCy working correctly')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Verification failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now:" -ForegroundColor Cyan
Write-Host "  1. Run tests: cd backend; python test_keyword_extraction.py" -ForegroundColor White
Write-Host "  2. Start server: cd backend; python app.py" -ForegroundColor White
Write-Host "  3. Test API endpoints" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - README: docs/tasks/TASK_5.1_README.md" -ForegroundColor White
Write-Host "  - Quickstart: docs/tasks/TASK_5.1_QUICKSTART.md" -ForegroundColor White
Write-Host ""
