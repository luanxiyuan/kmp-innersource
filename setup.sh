#!/bin/bash

echo "========================================"
echo "本地 AI 知识库对话系统 - 初始化脚本"
echo "========================================"
echo

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi

echo "[1/4] 创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[错误] 创建虚拟环境失败"
    exit 1
fi

echo "[2/4] 激活虚拟环境..."
source venv/bin/activate

echo "[3/4] 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 安装依赖失败"
    exit 1
fi

echo "[4/4] 安装 spaCy 中文模型..."
pip install https://github.com/explosion/spacy-models/releases/download/zh_core_web_sm-3.7.0/zh_core_web_sm-3.7.0.tar.gz
if [ $? -ne 0 ]; then
    echo "[警告] spaCy 中文模型安装失败，将使用默认配置"
fi

echo "创建必要目录..."
mkdir -p confluence_html data models rasa_config webchat scripts actions

echo
echo "========================================"
echo "初始化完成！"
echo "========================================"
echo
echo "接下来的步骤:"
echo
echo "1. 将 Confluence 导出的 HTML 文件放入 confluence_html 目录"
echo
echo "2. 运行以下命令构建 FAQ:"
echo "   python scripts/build_faq.py"
echo
echo "3. 运行以下命令训练 Rasa 模型:"
echo "   rasa train"
echo
echo "4. 运行 ./start.sh 启动服务"
echo
