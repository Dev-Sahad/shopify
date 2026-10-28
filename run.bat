@echo off
echo ========================================================
echo    Smart Gadget AI Dropshipping Assistant for Shopify
echo ========================================================
echo.

cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python app.py
) else (
    "C:\Users\sahad\AppData\Local\Python\bin\python.exe" app.py
)

pause

