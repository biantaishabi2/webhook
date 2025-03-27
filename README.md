# Webhook 服务

基于FastAPI的webhook接收服务，用于接收外部系统的webhook请求，并根据请求内容触发本地Python程序执行。

## 功能特点

- 支持多种webhook来源（GitHub, GitLab, Tower等）
- 使用token认证机制确保安全
- 异步执行本地Python程序
- 提供任务状态查询API
- 支持通过Cloudflare Tunnel进行内网穿透

## 快速开始

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 设置环境变量:
```bash
# 复制示例环境变量文件
cp config/samples/env.sample config/.env

# 编辑.env文件，填入您的Tower凭据
vi config/.env

# 或使用环境变量脚本
source scripts/set_env.sh
```

3. 启动服务:
```bash
# 方法1: 使用启动脚本
./scripts/start_service.sh

# 方法2: 使用systemd服务
sudo systemctl start webhook.service
```

## 系统服务

查看服务使用说明 [服务管理文档](docs/systemd_service.md)

## API文档

启动服务后，访问 http://localhost:12345/docs 查看API文档。

## 项目结构

```
/webhook/
  /app/            # 核心应用代码
    /models/       # 数据模型
    /routers/      # API路由
    /services/     # 服务层
    /utils/        # 工具函数
  /tests/          # 测试目录
    /tower/        # Tower API测试
    /webhook/      # Webhook测试
    /cloudflare/   # Cloudflare测试
    /fixtures/     # 测试数据
  /config/         # 配置文件
    /samples/      # 示例配置(不含敏感信息)
  /docs/           # 文档
  /scripts/        # 工具和启动脚本
  /services/       # 服务配置文件
  /examples/       # 示例代码
```

## 测试

```bash
# 测试Webhook
./tests/webhook/test_webhook.sh

# 测试Cloudflare隧道
./tests/cloudflare/test_cloudflare.sh
```

## 文档

- [Tower API使用指南](docs/Tower_api_guide.md)
- [Tower API官方文档](docs/Tower_api_doc.md)
- [Tower Webhook集成指南](docs/tower_webhook_integration.md)
- [Tower AG2集成指南](docs/tower_ag2_integration.md)
- [Cloudflare隧道指南](docs/cloudflared_tunnel_guide.md)
- [系统服务管理](docs/systemd_service.md)
- [环境变量设置指南](docs/environment_setup.md)

## 许可证

MIT