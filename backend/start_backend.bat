@echo off
title Rijema Dira - Backend Server
echo ============================================
echo   Rijema Dira Backend Server
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Menginstall dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Gagal menginstall dependencies.
    pause
    exit /b 1
)
echo.

echo [2/2] Menjalankan server backend...
echo   Server berjalan di http://localhost:5000
echo   Tekan Ctrl+C untuk berhenti
echo.
python app.py

pause
