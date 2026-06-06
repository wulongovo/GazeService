@echo off
chcp 65001 >nul
title AI 眼神空间定位服务
echo ========================================
echo   AI 眼神空间定位服务
echo ========================================
echo.
echo   正在启动服务...
echo.

cd /d "%~dp0"

REM 启动 FastAPI 服务（后台）
start "GazeService" /B "venv\Scripts\python.exe" main.py

REM 等待服务启动
timeout /t 6 /nobreak >nul

echo   服务已启动: http://localhost:8000
echo.
echo   正在开启外网访问（localtunnel）...
echo.

REM 启动 localtunnel
npx localtunnel --port 8000

pause
