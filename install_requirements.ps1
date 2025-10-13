Write-Host 'Installing SafeBox Python Requirements...' -ForegroundColor Cyan
py -m pip install --upgrade pip
py -m pip install fastapi==0.115.0
py -m pip install uvicorn[standard]==0.30.6
py -m pip install psutil==6.0.0
py -m pip install flask==3.0.0
py -m pip install flask-cors==4.0.0
py -m pip install rich==13.7.0
py -m pip install pytest==7.4.3
Write-Host 'Installation complete!' -ForegroundColor Green
