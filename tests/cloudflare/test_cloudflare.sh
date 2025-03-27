#!/bin/bash

# 测试脚本: 对Cloudflare tunneled webhook服务进行测试
# 用法: ./test_cloudflare.sh

# 设置变量
DOMAIN="app.biantaishabi.xyz"
TOKEN="test_secret_token"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始测试 Cloudflare tunneled webhook 服务 (${DOMAIN})${NC}"

# 测试1: 健康检查
echo -e "\n${YELLOW}1. 测试健康检查 (详细模式)${NC}"
curl -v "https://${DOMAIN}/health"

# 测试2: 使用Header验证的自定义webhook
echo -e "\n${YELLOW}2. 测试Header验证webhook (详细模式)${NC}"
curl -v -X POST "https://${DOMAIN}/api/webhooks/custom" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: ${TOKEN}" \
  -d '{"event_type":"test_event","params":{"timestamp":"'$(date +%s)'","test_param":"value"}}'

# 测试3: 使用查询参数验证的webhook
echo -e "\n${YELLOW}3. 测试查询参数验证webhook (详细模式)${NC}"
curl -v -X POST "https://${DOMAIN}/api/webhooks/custom?token=${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"event_type":"param_test","params":{"test":"query_param_value"}}'

echo -e "\n${YELLOW}所有测试完成${NC}"