@echo off
chcp 65001 >nul
echo ========================================
echo 本地 AI 知识库对话系统 - 简化版启动
echo ========================================
echo.

REM 检查 FAQ
if not exist "data\faq_enhanced.json" (
    if not exist "data\faq.json" (
        echo [提示] FAQ 尚未构建
        echo.
        set /p build_faq="是否现在构建 FAQ？(y/n): "
        if /i "%build_faq%"=="y" (
            echo.
            echo 开始构建 FAQ...
            python scripts\build_faq_enhanced.py --no-enhance
            if errorlevel 1 (
                echo [错误] FAQ 构建失败
                pause
                exit /b 1
            )
        )
    )
)

echo.
echo ========================================
echo 启动服务...
echo ========================================
echo.

REM 启动 FAQ API 服务
echo [信息] 启动 FAQ API 服务...
start "FAQ API Server" cmd /k "python scripts\faq_api.py"

REM 等待服务启动
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 服务地址:
echo   - API 服务: http://localhost:8000
echo   - API 文档: http://localhost:8000/docs
echo.
echo 现在可以访问 API 文档或使用 webchat
echo.
echo 按 Ctrl+C 可以停止服务
echo.
pause
