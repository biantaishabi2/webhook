# Webhook 接收服务

基于FastAPI的webhook接收服务，用于接收外部系统的webhook请求，并根据请求内容触发本地Python程序执行。

## 功能特点

- 支持多种webhook来源（GitHub, GitLab, Tower, 自定义系统等）
- 使用简单的token认证机制确保安全
- 异步执行本地Python程序
- 提供任务状态查询API
- 支持通过 Cloudflare Tunnel 进行内网穿透，暴露本地服务到公网

## 安装

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置环境变量:
```bash
# 默认已创建.env文件，包含测试token
# 若需修改，编辑.env文件
```

## 启动服务

使用提供的脚本启动服务:
```bash
./start_service.sh
```

或手动启动:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 12345 --reload
```

## 使用内网穿透暴露服务

如果你的服务运行在无公网IP的环境中，可以使用 Cloudflare Tunnel 进行内网穿透:

```bash
# 启动临时隧道
sudo systemctl start cloudflared.service

# 查看隧道URL
sudo journalctl -u cloudflared.service | grep -E "https://.*?\.trycloudflare\.com" | tail -1
```

获取到的公网URL可用于配置webhook回调地址，形式为:
`https://<tunnel-url>/api/webhooks/{source}`

也可以使用固定域名 `https://webhook.biantaishabi.xyz/api/webhooks/{source}`

## API文档

启动服务后，访问 http://localhost:12345/docs 查看API文档。

### 主要接口:

1. `POST /api/webhooks/{source}` - 接收webhook请求
   - 路径参数: `source` - webhook来源(github, gitlab, tower, custom)
   - 请求头: `X-Webhook-Token` - 认证令牌
   - 或查询参数: `?token=xxx` - 认证令牌

2. `POST /` - 接收Tower直接发送的webhook请求
   - 请求头: `X-Tower-Signature` - Tower提供的签名

3. `GET /api/tasks/{task_id}` - 获取任务状态
   - 路径参数: `task_id` - 任务ID

## 测试

使用提供的测试脚本:

```bash
# 测试本地服务
./test_webhook.sh

# 测试 Cloudflare 隧道 URL
./test_cloudflare_webhook.sh
```

测试结果将显示:
1. 发送到webhook端点的请求
2. 返回的响应和任务ID
3. 任务状态信息
4. 被调用的Python程序的日志

## 配置本地程序

修改 `app/services/task_runner.py` 中的程序映射关系，将webhook事件与本地Python程序关联起来:

```python
program_mapping = {
    "github:push": "/path/to/your/script.py",
    "gitlab:push": "/path/to/another/script.py",
    "custom:data_update": "/path/to/data/processor.py",
}
```

## 安全建议

- 生产环境中应使用环境变量设置Token，并定期更换
- 限制API访问来源
- 考虑使用HTTPS

## Tower API集成

服务已集成Tower API，可获取待办事项的详细信息。

### 配置Tower API访问令牌

1. 访问以下URL获取授权码:
   ```
   https://tower.im/oauth/authorize?client_id=0d7e96f946d17a4a86ff03619b3f5687ce4c2194253533142025cc9b2a0f842c&response_type=code
   ```

2. 获取授权码后，运行:
   ```
   python -m app.utils.tower_auth <授权码>
   ```

3. 配置完成后，webhook接收到Tower待办事项更新后，会自动获取详情并保存。

## 许可证

MIT

test
test
test
test
test
test
test
test
test
test
test
test
test
test
test
test
testtest
test
test
test
test
# webhook
