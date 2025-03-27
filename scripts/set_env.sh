#!/bin/bash

# 环境变量设置脚本
# 将此脚本中的值替换为您的实际配置
# 使用方法: source scripts/set_env.sh

# Tower API 凭据
export TOWER_CLIENT_ID="您的Tower客户端ID"
export TOWER_CLIENT_SECRET="您的Tower客户端密钥"

# Webhook 令牌
export WEBHOOK_TOKEN="test_secret_token"

# 日志设置
export LOG_LEVEL="INFO"

# 服务配置
export PORT=12345
export HOST="0.0.0.0"

echo "环境变量已设置!"
echo "TOWER_CLIENT_ID=${TOWER_CLIENT_ID}"
echo "WEBHOOK_TOKEN=${WEBHOOK_TOKEN}"
echo "LOG_LEVEL=${LOG_LEVEL}"
echo "服务将运行在 ${HOST}:${PORT}"