@echo off
echo Installing SafeBox Python Requirements...
echo.

REM Refresh environment variables
set PATH=%PATH%;C:\Users\Dell\AppData\Local\Programs\Python\Python312;C:\Users\Dell\AppData\Local\Programs\Python\Python312\Scripts

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing fastapi...
python -m pip install fastapi==0.115.0

echo.
echo Installing uvicorn...
python -m pip install uvicorn[standard]==0.30.6

echo.
echo Installing psutil...
python -m pip install psutil==6.0.0

echo.
echo Installing flask...
python -m pip install flask==3.0.0

echo.
echo Installing flask-cors...
python -m pip install flask-cors==4.0.0

echo.
echo Installing rich...
python -m pip install rich==13.7.0

echo.
echo Installing pytest...
python -m pip install pytest==7.4.3

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run:
echo   python web/app.py
echo   python cli/safebox_cli.py load-example
echo.
pause
