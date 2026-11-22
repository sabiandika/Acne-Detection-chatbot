@echo off
title Rijema Dira - Backend Server
echo ============================================
echo   Rijema Dira Backend Server
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Menginstall dependencies...
pip install flask flask-cors requests scikit-fuzzy numpy 2>nul
echo.

echo [2/2] Menjalankan server backend...
echo   Server berjalan di http://localhost:5000
echo   Tekan Ctrl+C untuk berhenti
echo.
python app.py

pause
