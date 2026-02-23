@echo off
chcp 65001 >nul
echo ========================================
echo 本地 AI 知识库对话系统 - 初始化脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...

REM 检查虚拟环境是否已存在
if exist "venv" (
    echo [信息] 虚拟环境已存在
    choice /C YN /M "是否删除并重新创建虚拟环境？"
    if errorlevel 2 (
        echo [跳过] 保留现有虚拟环境
        goto activate_venv
    )
    echo 正在删除现有虚拟环境...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    echo.
    echo 可能的原因：
    echo 1. Python 正在运行中，请关闭所有 Python 进程
    echo 2. 权限不足，请以管理员身份运行
    echo 3. venv 文件夹被锁定，请手动删除 venv 文件夹后重试
    echo.
    pause
    exit /b 1
)

:activate_venv
echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/5] 安装依赖包...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo [4/5] 安装 spaCy 中文模型...
pip install https://github.com/explosion/spacy-models/releases/download/zh_core_web_sm-3.7.0/zh_core_web_sm-3.7.0.tar.gz
if errorlevel 1 (
    echo [警告] spaCy 中文模型安装失败，将使用默认配置
)

echo [5/5] 创建必要目录...
if not exist "confluence_html" mkdir confluence_html
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "rasa_config" mkdir rasa_config
if not exist "webchat" mkdir webchat
if not exist "scripts" mkdir scripts
if not exist "actions" mkdir actions

echo.
echo ========================================
echo 初始化完成！
echo ========================================
echo.
echo 接下来的步骤:
echo.
echo 1. 将 Confluence 导出的 HTML 文件放入 confluence_html 目录
echo.
echo 2. 复制环境变量配置（可选）:
echo    copy .env.example .env
echo    然后编辑 .env 文件填入 API 密钥
echo.
echo 3. 运行以下命令构建 FAQ:
echo    python scripts\build_faq_enhanced.py
echo.
echo 4. 运行以下命令训练 Rasa 模型:
echo    rasa train
echo.
echo 5. 运行 .\start.bat 启动服务
echo.
pause
