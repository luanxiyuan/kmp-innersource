#!/bin/bash

echo "正在停止所有 Rasa 服务..."
echo

# 关闭所有 Rasa 相关进程
pkill -f "rasa run"

echo "服务已停止"
