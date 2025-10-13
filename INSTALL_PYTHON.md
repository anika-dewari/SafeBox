# SafeBox Python Installation Guide

## Problem: Python not found

The 'python' or 'py' command is not recognized because Python is not properly installed or not in your PATH.

## Solution: Install Python

### Method 1: Using Winget (Recommended)

Open PowerShell as Administrator and run:

```powershell
winget install Python.Python.3.12
```

After installation, close and reopen PowerShell, then run:
```powershell
python --version
```

### Method 2: Download from Python.org

1. Visit: https://www.python.org/downloads/
2. Download Python 3.12 (latest version)
3. Run the installer
4. IMPORTANT: Check "Add Python to PATH" during installation
5. Click "Install Now"

### Method 3: Microsoft Store

1. Open Microsoft Store
2. Search for "Python 3.12"
3. Click "Get" to install
4. Close and reopen PowerShell

## After Installing Python

Navigate to the SafeBox directory and run:

```powershell
cd C:\Users\Dell\Documents\GitHub\SafeBox_

# Run the installation batch file
.\install.bat
```

Or install packages manually:

```powershell
python -m pip install --upgrade pip
python -m pip install fastapi==0.115.0
python -m pip install uvicorn[standard]==0.30.6
python -m pip install psutil==6.0.0
python -m pip install flask==3.0.0
python -m pip install flask-cors==4.0.0
python -m pip install rich==13.7.0
python -m pip install pytest==7.4.3
```

## Verify Installation

```powershell
python --version
python -m pip list
```

## Quick Start After Installation

```powershell
# Start Web Dashboard
python web/app.py

# Or use CLI
python cli/safebox_cli.py load-example
```

## Troubleshooting

If 'python' still not recognized after installation:

1. Find Python installation directory (usually):
   - C:\Users\Dell\AppData\Local\Programs\Python\Python312
   - C:\Python312

2. Add to PATH manually:
   - Search "Environment Variables" in Windows
   - Edit "Path" under System Variables
   - Add Python directory and Scripts subdirectory
   - Click OK and restart PowerShell

3. Try using full path:
   ```powershell
   C:\Users\Dell\AppData\Local\Programs\Python\Python312\python.exe -m pip install flask
   ```
