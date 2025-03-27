# Webhook 服务设计文档

## 概述
设计一个基于FastAPI的webhook服务，用于接收外部系统的webhook请求，并根据请求内容触发本地不同的Python程序执行。

## 服务配置

### 本地服务配置

1. 启动FastAPI服务（使用12345端口）:
```bash
# 使用提供的启动脚本
./start_service.sh

# 或手动启动
uvicorn app.main:app --host 0.0.0.0 --port 12345
```

### 内网穿透选项

系统已配置 Cloudflare Tunnel 服务，可用来将本地服务暴露到公网：

#### 方法1: 使用临时隧道（适合测试）

使用系统服务启动临时隧道：
```bash
# 启动临时隧道
sudo systemctl start cloudflared.service

# 查看隧道URL
sudo journalctl -u cloudflared.service | grep -E "https://.*?\.trycloudflare\.com" | tail -1
```

每次重启服务会生成新的随机域名地址。

#### 方法2: 使用永久隧道（适合生产）

系统已配置永久隧道，对应固定域名：
```
https://webhook.biantaishabi.xyz
```

获取到公网URL后，外部系统可以通过 `https://<tunnel-url>/api/webhooks/{source}` 发送webhook请求。

更多配置详情请参考 `/home/wangbo/document/wangbo/dev/webhook/cloudflared_tunnel_guide.md` 和 `/home/wangbo/document/wangbo/dev/webhook/run_both_tunnels.md`。

## 系统架构

### 目录结构
```
app/
├── main.py              # FastAPI应用入口
├── routers/             # 路由定义
│   └── webhooks.py      # webhook路由
├── services/            # 业务逻辑
│   └── task_runner.py   # 执行Python程序
├── models/              # 数据模型
│   └── webhook.py       # webhook请求模型
├── config.py            # 配置文件
└── utils/               # 工具函数
    ├── auth.py          # 身份验证
    └── logging.py       # 日志处理
```

### 核心组件

1. **Webhook接收器**
   - 处理来自不同源的webhook请求（GitHub, GitLab, 自定义系统等）
   - 验证webhook请求的合法性（签名验证、IP白名单等）
   - 解析webhook请求内容，提取关键信息

2. **任务分发器**
   - 根据webhook内容决定需要执行的本地Python程序
   - 支持基于规则的任务分发机制
   - 维护webhook类型与本地程序的映射关系

3. **执行引擎**
   - 异步执行本地Python程序
   - 支持传递参数到本地程序
   - 提供任务状态跟踪和错误处理

4. **配置管理**
   - 管理webhook源配置
   - 管理本地程序路径配置
   - 管理安全配置（密钥、令牌等）

## API设计

### Webhook接收端点

```
POST /api/webhooks/{source}
```

- `{source}`: webhook来源标识（如github, gitlab, custom等）
- 请求体: 来自外部系统的原始webhook数据
- 响应: 任务ID和状态信息

### 任务状态查询端点

```
GET /api/tasks/{task_id}
```

- `{task_id}`: 任务唯一标识
- 响应: 任务执行状态、开始时间、结束时间、执行结果等

### 配置管理端点

```
GET/POST /api/config/webhooks
GET/POST /api/config/programs
```

## 实现细节

### 1. Webhook身份验证

支持多种验证方式:
- 签名验证 (HMAC)
- 令牌验证
- IP白名单验证

### 2. 任务执行方式

提供多种执行方式:
- 直接执行Python脚本
- 通过子进程执行
- 基于消息队列的异步执行

### 3. 错误处理与重试

- 实现异常捕获和错误记录
- 支持任务重试机制
- 失败通知机制

### 4. 安全考虑

- 敏感数据加密存储
- 限制执行权限
- 日志敏感信息脱敏

## 配置示例

```python
# config.py
WEBHOOK_CONFIGS = {
    "github": {
        "secret": "xxx",
        "auth_type": "signature",
    },
    "custom": {
        "token": "xxx",
        "auth_type": "token",
    }
}

PROGRAM_CONFIGS = {
    "deploy": {
        "command": "python /path/to/deploy.py",
        "params": ["branch", "commit"],
    },
    "analyze": {
        "command": "python /path/to/analyze.py",
        "params": ["data"],
    }
}

# 映射规则
WEBHOOK_TO_PROGRAM_MAPPING = {
    "github": {
        "push": {
            "branch == 'main'": "deploy",
            "branch == 'dev'": "test",
        }
    },
    "custom": {
        "data_update": "analyze",
    }
}
```

## 扩展性考虑

1. **插件系统**
   - 支持通过插件扩展webhook源
   - 支持通过插件扩展执行方式

2. **分布式执行**
   - 支持将任务分发到多个执行节点
   - 支持基于Celery等任务队列的分布式执行

3. **Web界面**
   - 提供配置管理界面
   - 提供任务监控界面

## 实现步骤

1. 搭建基本FastAPI应用框架
2. 实现webhook接收与验证
3. 实现任务分发逻辑
4. 实现本地程序执行
5. 添加错误处理与日志
6. 实现配置管理
7. 添加单元测试
8. 部署与文档