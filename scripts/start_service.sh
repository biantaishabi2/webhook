#!/bin/bash

# 检查是否安装了必要的依赖
pip install -r requirements.txt

# 加载环境变量 (如果存在)
ENV_FILE="../config/.env"
if [ -f "$ENV_FILE" ]; then
    echo "加载环境变量文件: $ENV_FILE"
    export $(grep -v '^#' $ENV_FILE | xargs)
elif [ -f "config/.env" ]; then
    echo "加载环境变量文件: config/.env"
    export $(grep -v '^#' config/.env | xargs)
else
    echo "警告: 未找到.env文件，使用默认设置"
    # 如果未设置，使用默认环境变量
    export PORT=${PORT:-12345}
    export HOST=${HOST:-0.0.0.0}
fi

# 启动FastAPI服务
echo "正在启动Webhook服务, 端口: ${PORT:-12345}..."
uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-12345} --reload