@echo off
chcp 65001 >nul
echo ========================================
echo 本地 AI 知识库对话系统 - 启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查是否已经构建 FAQ
if not exist "data\faq_enhanced.json" (
    if not exist "data\faq.json" (
        echo [提示] FAQ 尚未构建
        echo.
        set /p build_faq="是否现在构建 FAQ？(y/n): "
        if /i "%build_faq%"=="y" (
            echo.
            echo 开始构建 FAQ...
            if exist ".env" (
                echo [信息] 检测到 API 配置，将使用 AI 增强
                python scripts\build_faq_enhanced.py
            ) else (
                echo [信息] 未检测到 API 配置，将使用基础模式
                python scripts\build_faq_enhanced.py --no-enhance
            )
            if errorlevel 1 (
                echo [错误] FAQ 构建失败
                pause
                exit /b 1
            )
        )
    )
)

REM 检查模型是否存在
if not exist "models\" (
    echo [提示] Rasa 模型尚未训练
    echo.
    set /p train_model="是否现在训练模型？(y/n): "
    if /i "%train_model%"=="y" (
        echo.
        echo 开始训练 Rasa 模型...
        rasa train
        if errorlevel 1 (
            echo [错误] 模型训练失败
            pause
            exit /b 1
        )
    )
)

echo.
echo ========================================
echo 启动服务...
echo ========================================
echo.
echo 请保持此窗口打开，将在新窗口中启动 Rasa 服务
echo.

REM 启动 Rasa 服务器（新窗口）
start "Rasa Server" cmd /k "rasa run --enable-api --cors ""*"""

REM 等待 5 秒
timeout /t 5 /nobreak >nul

REM 启动动作服务器（新窗口）
start "Rasa Actions" cmd /k "rasa run actions"

REM 等待 5 秒
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 服务地址:
echo   - Rasa Server: http://localhost:5005
echo   - Actions Server: http://localhost:5055
echo.
echo 现在可以打开浏览器访问 webchat\index.html
echo.
echo 按 Ctrl+C 可以停止所有服务
echo.

REM 打开浏览器
start webchat\index.html

REM 等待用户按键
pause

REM 关闭所有 Rasa 进程
taskkill /f /im python.exe /fi "windowtitle eq Rasa*" >nul 2>&1
echo.
echo 服务已停止
pause
