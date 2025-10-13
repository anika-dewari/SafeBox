# SafeBox Installation & Quick Start Guide
# Author: Ritika
# Purpose: Easy setup for all components

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SafeBox Installation Script" -ForegroundColor Cyan
Write-Host "Ritika's Implementation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from python.org" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Available Commands:" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Start Web Dashboard:" -ForegroundColor Yellow
Write-Host "   python web/app.py" -ForegroundColor White
Write-Host "   Then open: http://localhost:5000" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Use CLI:" -ForegroundColor Yellow
Write-Host "   python cli/safebox_cli.py load-example" -ForegroundColor White
Write-Host "   python cli/safebox_cli.py check-state" -ForegroundColor White
Write-Host "   python cli/safebox_cli.py test-suite" -ForegroundColor White
Write-Host ""

Write-Host "3. Run Tests:" -ForegroundColor Yellow
Write-Host "   pytest tests/test_banker.py -v" -ForegroundColor White
Write-Host ""

Write-Host "4. View Documentation:" -ForegroundColor Yellow
Write-Host "   docs/deadlock-prevention.md    - Theory" -ForegroundColor White
Write-Host "   docs/UI_GUIDE.md               - Usage Guide" -ForegroundColor White
Write-Host "   docs/presentation.md           - Presentation" -ForegroundColor White
Write-Host "   RITIKA_IMPLEMENTATION.md       - Summary" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Demo (Auto-starting Web Server)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Start web dashboard now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Starting SafeBox Web Dashboard..." -ForegroundColor Green
    Write-Host "Open your browser to: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    python web/app.py
} else {
    Write-Host ""
    Write-Host "Setup complete! Run 'python web/app.py' when ready." -ForegroundColor Green
    Write-Host ""
}
