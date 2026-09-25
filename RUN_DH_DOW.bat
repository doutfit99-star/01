@echo off
title DH DOW - Modern Video Downloader
color 0A
cls
echo =================================================================
echo                 DH DOW - UNG DUNG TAI VIDEO DA NANG               
echo =================================================================
echo.
echo  [1] Mo bang Cua so Desktop App (PyWebView Native)
echo  [2] Mo bang Trinh duyet Web (Chrome / Edge / Cốc Cốc)
echo.
echo [*] Dang khoi chay DH DOW...
cd /d "%~dp0"
py -3 app.py
pause
