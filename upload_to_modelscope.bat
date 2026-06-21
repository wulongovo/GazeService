@echo off
chcp 65001 >nul
cd /d "E:\pycharm\GazeService"
if errorlevel 1 echo [WARN] 上一步可能失败
git init
if errorlevel 1 echo [WARN] 上一步可能失败
git remote add modelscope https://oauth2:ms-0914727e-34ab-4422-81ed-9080c30ecef6@www.modelscope.cn/wulongovo/GazeService.git
if errorlevel 1 echo [WARN] 上一步可能失败
git add .
if errorlevel 1 echo [WARN] 上一步可能失败
git commit -m "Initial commit: AI Gaze Service"
if errorlevel 1 echo [WARN] 上一步可能失败
git push modelscope master --force
if errorlevel 1 echo [WARN] 上一步可能失败
pause
