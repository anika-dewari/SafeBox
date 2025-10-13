# SafeBox CLI Demo Script
# Author: Ritika
# Purpose: Automated demo of all features

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SafeBox CLI Demo" -ForegroundColor Cyan
Write-Host "Banker's Algorithm Implementation" -ForegroundColor Cyan
Write-Host "Developed by: Ritika" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Pause-Demo {
    param([string]$message = "Press Enter to continue...")
    Write-Host ""
    Write-Host $message -ForegroundColor Yellow
    Read-Host
    Write-Host ""
}

# Demo 1: Load Example
Write-Host "Demo 1: Loading Example Scenario" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py load-example" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py load-example

# Demo 2: Check State
Write-Host ""
Write-Host "Demo 2: Checking System State" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py check-state" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py check-state

# Demo 3: Request Resources (Safe)
Write-Host ""
Write-Host "Demo 3: Requesting Resources (Safe Request)" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py request 1 1 0 2" -ForegroundColor Gray
Write-Host "Process 1 requests [1 CPU, 0 Memory, 2 Disk]" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py request 1 1 0 2

# Demo 4: Initialize New System
Write-Host ""
Write-Host "Demo 4: Initializing New System" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py init 10 5 7 --names CPU,Memory,Disk" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py init 10 5 7 --names "CPU,Memory,Disk"

# Demo 5: Add Process
Write-Host ""
Write-Host "Demo 5: Adding a Process" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py add-process 0 WebServer 7 5 3" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py add-process 0 WebServer 7 5 3

# Demo 6: Request Resources for New Process
Write-Host ""
Write-Host "Demo 6: Requesting Resources for WebServer" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py request 0 2 2 2" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py request 0 2 2 2

# Demo 7: Export Report
Write-Host ""
Write-Host "Demo 7: Exporting Report" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py export-report demo_report.txt" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py export-report demo_report.txt
Write-Host "Report saved to: demo_report.txt" -ForegroundColor Green

# Demo 8: Run Test Suite
Write-Host ""
Write-Host "Demo 8: Running Test Suite" -ForegroundColor Green
Write-Host "Command: python cli/safebox_cli.py test-suite" -ForegroundColor Gray
Pause-Demo
python cli/safebox_cli.py test-suite

# Completion
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demo Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary of what we demonstrated:" -ForegroundColor Yellow
Write-Host "✓ Loaded example scenario with 5 processes" -ForegroundColor White
Write-Host "✓ Checked system state (safe/unsafe)" -ForegroundColor White
Write-Host "✓ Requested resources (safe allocation)" -ForegroundColor White
Write-Host "✓ Initialized new system" -ForegroundColor White
Write-Host "✓ Added custom process" -ForegroundColor White
Write-Host "✓ Exported detailed report" -ForegroundColor White
Write-Host "✓ Ran comprehensive test suite" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "- Try the web dashboard: python web/app.py" -ForegroundColor White
Write-Host "- Read documentation in docs/ folder" -ForegroundColor White
Write-Host "- Explore more CLI commands: python cli/safebox_cli.py --help" -ForegroundColor White
Write-Host ""
