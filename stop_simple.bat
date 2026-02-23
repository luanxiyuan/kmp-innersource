@echo off
chcp 65001 >nul
echo ========================================
echo 停止服务
echo ========================================
echo.

echo [信息] 正在停止 FAQ API 服务...
taskkill /f /fi "windowtitle eq FAQ API Server*" >nul 2>&1

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo 服务已停止
echo ========================================
echo.
pause
