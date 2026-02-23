@echo off
chcp 65001 >nul
echo ========================================
echo 更新 FAQ 知识库（支持 AI 增强）
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

echo 开始更新 FAQ 知识库...
echo.

REM 检查是否配置了 API 密钥
if not exist ".env" (
    echo [提示] 未找到 .env 文件，将使用基础模式（不使用 AI 增强）
    echo.
    echo 如需启用 AI 增强，请：
    echo   1. 复制 .env.example 为 .env
    echo   2. 填入你的 API 密钥
    echo.
    set /p use_basic="是否继续使用基础模式？(y/n): "
    if /i not "%use_basic%"=="y" (
        echo 已取消
        pause
        exit /b 1
    )
    python scripts\build_faq_enhanced.py --no-enhance
) else (
    echo [信息] 检测到 .env 配置文件，将启用 AI 增强
    python scripts\build_faq_enhanced.py
)

if errorlevel 1 (
    echo.
    echo [错误] FAQ 更新失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo FAQ 更新完成！
echo ========================================
echo.
echo 注意: FAQ 更新后需要重新训练 Rasa 模型
echo 运行: rasa train
echo 然后重启 Rasa 服务即可使用新的 FAQ
echo.

set /p train_now="是否现在训练模型？(y/n): "
if /i "%train_now%"=="y" (
    echo.
    echo 开始训练 Rasa 模型...
    rasa train
    if errorlevel 1 (
        echo [错误] 模型训练失败
        pause
        exit /b 1
    )
    echo.
    echo 模型训练完成！
)

pause
