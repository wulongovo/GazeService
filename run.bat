@echo off
chcp 65001 >nul
title AI 眼神空间定位服务
echo ========================================
echo   AI 眼神空间定位服务（仅本机）
echo ========================================
echo.
echo   访问: http://localhost:8000
echo   按 Ctrl+C 停止
echo ========================================
echo.

cd /d "%~dp0"
"venv\Scripts\python.exe" main.py
pause
