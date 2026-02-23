#!/bin/bash

echo "========================================"
echo "本地 AI 知识库对话系统 - 启动脚本"
echo "========================================"
echo

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[错误] 虚拟环境不存在，请先运行 ./setup.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查是否已经构建 FAQ
if [ ! -f "data/faq_enhanced.json" ]; then
    if [ ! -f "data/faq.json" ]; then
        echo "[提示] FAQ 尚未构建"
        echo
        read -p "是否现在构建 FAQ？(y/n): " build_faq
        if [ "$build_faq" = "y" ]; then
            echo
            echo "开始构建 FAQ..."
            if [ -f ".env" ]; then
                echo "[信息] 检测到 API 配置，将使用 AI 增强"
                python scripts/build_faq_enhanced.py
            else
                echo "[信息] 未检测到 API 配置，将使用基础模式"
                python scripts/build_faq_enhanced.py --no-enhance
            fi
            if [ $? -ne 0 ]; then
                echo "[错误] FAQ 构建失败"
                exit 1
            fi
        fi
    fi
fi

# 检查模型是否存在
if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then
    echo "[提示] Rasa 模型尚未训练"
    echo
    read -p "是否现在训练模型？(y/n): " train_model
    if [ "$train_model" = "y" ]; then
        echo
        echo "开始训练 Rasa 模型..."
        rasa train
        if [ $? -ne 0 ]; then
            echo "[错误] 模型训练失败"
            exit 1
        fi
    fi
fi

echo
echo "========================================"
echo "启动服务..."
echo "========================================"
echo

# 启动 Rasa 服务器（后台）
echo "启动 Rasa Server..."
rasa run --enable-api --cors "*" &
RASA_PID=$!
echo "Rasa Server PID: $RASA_PID"

# 等待 5 秒
sleep 5

# 启动动作服务器（后台）
echo "启动 Actions Server..."
rasa run actions &
ACTIONS_PID=$!
echo "Actions Server PID: $ACTIONS_PID"

# 等待 5 秒
sleep 5

echo
echo "========================================"
echo "服务启动完成！"
echo "========================================"
echo
echo "服务地址:"
echo "  - Rasa Server: http://localhost:5005"
echo "  - Actions Server: http://localhost:5055"
echo
echo "现在可以打开浏览器访问 webchat/index.html"
echo
echo "按 Ctrl+C 可以停止所有服务"
echo

# 捕获 Ctrl+C 信号
trap "echo; echo 正在停止服务...; kill $RASA_PID $ACTIONS_PID 2>/dev/null; echo 服务已停止; exit 0" SIGINT

# 打开浏览器（Linux/macOS）
if command -v xdg-open > /dev/null; then
    xdg-open webchat/index.html
elif command -v open > /dev/null; then
    open webchat/index.html
fi

# 等待用户中断
wait
