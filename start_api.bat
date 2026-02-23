@echo off
chcp 65001 >nul
echo ========================================
echo 启动 FAQ API 服务
echo ========================================
echo.

REM 检查 FAQ
if not exist "data\faq_enhanced.json" (
    echo [提示] FAQ 尚未构建，正在构建...
    python scripts\build_faq_enhanced.py
    if errorlevel 1 (
        echo [错误] FAQ 构建失败
        pause
        exit /b 1
    )
)

echo [信息] 启动 FAQ API 服务...
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python scripts\faq_api.py

pause
