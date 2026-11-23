@echo off
title Rijema Dira - Full System
echo ============================================
echo   Rijema Dira - Skincare Chatbot System
echo ============================================
echo.
echo Memulai Backend + Frontend secara bersamaan...
echo.

:: Jalankan backend di window terpisah
echo [1/2] Menjalankan Backend (Flask + Chatbot)...
start "Rijema Dira Backend" cmd /k "cd /d "%~dp0backend" && pip install flask flask-cors requests scikit-fuzzy numpy 2>nul && python app.py"

:: Tunggu backend siap
echo      Menunggu backend siap...
timeout /t 3 /nobreak >nul

:: Jalankan frontend
echo [2/2] Menjalankan Frontend (Vite + React)...
start "Rijema Dira Frontend" cmd /k "cd /d "%~dp0" && npx vite --open"

echo.
echo ============================================
echo   Sistem sudah berjalan!
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:5000
echo   Chatbot  : http://localhost:5173/chatbot
echo ============================================
echo.
echo Pastikan Ollama juga sudah berjalan (ollama serve)
echo Tekan tombol apa saja untuk menutup jendela ini...
pause >nul
