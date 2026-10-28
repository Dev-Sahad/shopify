@echo off
echo ========================================================
echo    24/7 Smart Gadget AI Store Manager for Shopify
echo ========================================================
echo.
echo Starting server and background bot daemon...
echo Open http://localhost:5000 in your browser.
echo.

cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start http://localhost:5000
    python app.py
) else (
    start http://localhost:5000
    "C:\Users\sahad\AppData\Local\Python\bin\python.exe" app.py
)

pause
