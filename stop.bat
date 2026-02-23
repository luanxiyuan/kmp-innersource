@echo off
chcp 65001 >nul
echo 正在停止所有 Rasa 服务...
echo.

REM 关闭所有 Python 进程
taskkill /f /im python.exe /fi "windowtitle eq Rasa*" >nul 2>&1

echo 服务已停止
pause
