@echo off
title 24/7 Smart Gadget AI Store Manager
echo ========================================================
echo    24/7 Smart Gadget AI Store Manager for Shopify
echo ========================================================
echo.
echo Starting server and background daemon...
echo Your browser will open automatically once the dashboard is ready.
echo.

cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python app.py
) else (
    "C:\Users\sahad\AppData\Local\Python\bin\python.exe" app.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Application encountered an issue.
    pause
)
