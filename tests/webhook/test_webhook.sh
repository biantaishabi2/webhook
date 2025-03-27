#!/bin/bash

# 设置环境变量
export WEBHOOK_TOKEN="test_secret_token"

# 默认服务URL
SERVER_URL="http://localhost:12345"

# 检查是否提供了URL参数
if [ "$1" != "" ]; then
  SERVER_URL="$1"
fi

echo "===== Webhook 测试脚本 ====="
echo "服务URL: $SERVER_URL"
echo "认证Token: $WEBHOOK_TOKEN"
echo "============================="

# 创建测试目录
mkdir -p tests

# 运行测试脚本
python3 tests/test_webhook.py --url "$SERVER_URL" --token "$WEBHOOK_TOKEN"

# 检查日志文件
echo
echo "检查日志文件 /tmp/webhook_test.log:"
if [ -f /tmp/webhook_test.log ]; then
  tail -n 10 /tmp/webhook_test.log
else
  echo "日志文件不存在，可能表示程序未成功执行"
fi