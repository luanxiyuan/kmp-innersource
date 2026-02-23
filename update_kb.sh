#!/bin/bash

echo "========================================"
echo "更新 FAQ 知识库（支持 AI 增强）"
echo "========================================"
echo

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[错误] 虚拟环境不存在，请先运行 ./setup.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "开始更新 FAQ 知识库..."
echo

# 检查是否配置了 API 密钥
if [ ! -f ".env" ]; then
    echo "[提示] 未找到 .env 文件，将使用基础模式（不使用 AI 增强）"
    echo
    echo "如需启用 AI 增强，请："
    echo "  1. 复制 .env.example 为 .env"
    echo "  2. 填入你的 API 密钥"
    echo
    read -p "是否继续使用基础模式？(y/n): " use_basic
    if [ "$use_basic" != "y" ]; then
        echo "已取消"
        exit 1
    fi
    python scripts/build_faq_enhanced.py --no-enhance
else
    echo "[信息] 检测到 .env 配置文件，将启用 AI 增强"
    python scripts/build_faq_enhanced.py
fi

if [ $? -ne 0 ]; then
    echo
    echo "[错误] FAQ 更新失败"
    exit 1
fi

echo
echo "========================================"
echo "FAQ 更新完成！"
echo "========================================"
echo
echo "注意: FAQ 更新后需要重新训练 Rasa 模型"
echo "运行: rasa train"
echo "然后重启 Rasa 服务即可使用新的 FAQ"
echo

read -p "是否现在训练模型？(y/n): " train_now
if [ "$train_now" = "y" ]; then
    echo
    echo "开始训练 Rasa 模型..."
    rasa train
    if [ $? -ne 0 ]; then
        echo "[错误] 模型训练失败"
        exit 1
    fi
    echo
    echo "模型训练完成！"
fi
