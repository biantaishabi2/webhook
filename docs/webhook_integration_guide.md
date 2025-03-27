# Webhook 集成指南

本文档介绍如何在 Webhook 服务中添加和配置新的服务端点。

## 系统工作原理

### 概述

该webhook系统通过以下流程工作：

1. **接收webhooks**：
   - FastAPI应用（`app/main.py`）提供HTTP接口接收外部系统的webhook请求
   - 根据路径（如根路径或`/api`前缀）路由到不同处理函数

2. **配置管理**：
   - `app/config.py`定义了三种关键配置：
     - `WEBHOOK_CONFIGS`：设置每种服务的认证方式（token、签名、IP等）
     - `PROGRAM_CONFIGS`：定义处理程序的执行配置（命令、参数、超时等）
     - `WEBHOOK_TO_PROGRAM_MAPPING`：建立webhook和执行程序之间的映射规则

3. **任务分发流程**：
   - 接收webhook请求后，根据来源（source）和事件类型（event_type）确定处理程序
   - `dispatch_task`函数根据映射规则选择适当的处理脚本
   - 创建任务（Task对象）并保存到内存存储中
   - 异步启动任务执行进程

4. **任务执行**：
   - `run_program`函数通过子进程执行外部Python程序
   - 将webhook数据作为命令行参数传递给处理脚本
   - 跟踪执行状态（等待、运行中、完成、失败）
   - 捕获输出和错误信息，更新任务结果

## 添加新的服务端点

以下是添加新服务端点的完整步骤，以Jira为例：

### 1. 更新配置文件

在`app/config.py`中添加新服务配置：

```python
# 添加服务认证配置
WEBHOOK_CONFIGS["jira"] = WebhookAuthConfig(
    token=os.environ.get("JIRA_WEBHOOK_TOKEN", ""),
    auth_type="token",
)

# 添加处理程序配置
PROGRAM_CONFIGS["jira_issue"] = ProgramConfig(
    command="python /home/wangbo/document/wangbo/dev/webhook/examples/jira_webhook_handler.py",
    params=["issue_key", "issue_type", "priority"],
)

# 添加映射规则
WEBHOOK_TO_PROGRAM_MAPPING["jira"] = {
    "issue_created": [
        MappingRule(condition="issue_type == 'bug'", program="jira_issue"),
    ],
    "issue_updated": [
        MappingRule(condition="True", program="jira_issue"),
    ],
}
```

### 2. 创建处理程序脚本

创建`examples/jira_webhook_handler.py`：

```python
#!/usr/bin/env python
"""
Jira webhook处理程序
专门用于处理来自Jira的webhook请求
"""

import sys
import argparse
import json
import os
from datetime import datetime

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Jira Webhook处理程序')
    parser.add_argument('--issue_key', type=str, help='Issue Key')
    parser.add_argument('--issue_type', type=str, help='Issue Type')
    parser.add_argument('--priority', type=str, help='Priority')
    parser.add_argument('--event_type', type=str, help='事件类型')
    parser.add_argument('--raw_payload', type=str, help='原始的完整payload')
    
    args, unknown = parser.parse_known_args()
    
    # 创建日志目录
    log_dir = '/tmp/jira_webhook_logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = f'{log_dir}/jira_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # 记录所有信息
    with open(log_file, 'w') as f:
        f.write(f"[{datetime.now().isoformat()}] Jira Webhook triggered!\n")
        f.write(f"Event Type: {args.event_type}\n")
        f.write(f"Known Arguments: {json.dumps(vars(args), indent=2)}\n")
    
    print(f"Jira webhook handler executed successfully!")
    print(f"Event type: {args.event_type}")
    print(f"Issue: {args.issue_key}, Type: {args.issue_type}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 3. 更新任务运行程序

在`app/services/task_runner.py`中添加映射：

```python
program_mapping = {
    # 现有映射保持不变
    "github:push": "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py",
    # ...
    
    # 添加新的Jira映射
    "jira:issue_created": "/home/wangbo/document/wangbo/dev/webhook/examples/jira_webhook_handler.py",
    "jira:issue_updated": "/home/wangbo/document/wangbo/dev/webhook/examples/jira_webhook_handler.py",
}
```

### 4. 添加路由处理逻辑

有两种方法可以添加路由处理逻辑：

#### 方法1: 在现有路由器中添加

修改`app/routers/webhooks.py`文件：

```python
# 在receive_webhook函数中添加Jira处理逻辑
elif source == "jira":
    event_type = request.headers.get("X-Jira-Event-Type", "unknown")
    # 提取Jira特定参数
    params = {
        "issue_key": payload.get("issue", {}).get("key", ""),
        "issue_type": payload.get("issue", {}).get("fields", {}).get("issuetype", {}).get("name", ""),
        "priority": payload.get("issue", {}).get("fields", {}).get("priority", {}).get("name", ""),
        "raw_payload": json.dumps(payload)
    }
```

#### 方法2: 创建专门的端点

在`app/main.py`中添加专门的端点：

```python
@app.post("/jira")
async def receive_jira_webhook(request: Request):
    """
    处理Jira webhook
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    
    headers = dict(request.headers)
    event_type = headers.get("X-Jira-Event-Type", "unknown")
    
    logger = get_logger(__name__)
    logger.info(f"Received Jira webhook: {event_type}")
    
    # 提取Jira参数
    params = {
        "issue_key": payload.get("issue", {}).get("key", ""),
        "issue_type": payload.get("issue", {}).get("fields", {}).get("issuetype", {}).get("name", ""),
        "priority": payload.get("issue", {}).get("fields", {}).get("priority", {}).get("name", ""),
        "raw_payload": json.dumps(payload)
    }
    
    task = await dispatch_task("jira", event_type, params)
    
    return {
        "task_id": str(task.id),
        "status": task.status,
        "message": f"Task created for jira:{event_type}"
    }
```

## 配置说明

### 服务认证配置 (WEBHOOK_CONFIGS)

- **auth_type**: 认证类型，可选值：
  - `"none"`: 不进行认证
  - `"signature"`: 使用签名认证
  - `"token"`: 使用令牌认证
  - `"ip"`: 使用IP地址认证

- **token/secret**: 根据认证类型提供令牌或密钥
- **allowed_ips**: 允许的IP地址列表

### 程序执行配置 (PROGRAM_CONFIGS)

- **command**: 执行的命令
- **params**: 需要从webhook提取的参数列表
- **working_dir**: 工作目录
- **timeout**: 超时时间（秒）
- **run_async**: 是否异步运行

### 映射规则 (WEBHOOK_TO_PROGRAM_MAPPING)

- **condition**: 条件表达式，如 `"issue_type == 'bug'"`
- **program**: 符合条件时执行的程序配置名称

## 最佳实践

1. **安全性考虑**：
   - 在生产环境中限制CORS来源
   - 使用合适的认证机制验证webhook来源
   - 不要在代码中硬编码令牌，使用环境变量

2. **参数提取**：
   - 针对每个服务提取特定参数
   - 使用安全的方式获取嵌套字段，避免键不存在时出错
   - 始终包含原始payload以便完整处理

3. **错误处理**：
   - 捕获并记录解析错误
   - 为每种webhook类型提供合理的默认行为
   - 确保即使处理失败也能返回有用的响应

4. **日志记录**：
   - 记录所有接收到的webhook事件
   - 记录关键参数和处理步骤
   - 保存原始payload以便调试和重放

## 测试新配置

1. 使用模拟请求测试端点：
   ```bash
   curl -X POST http://localhost:12345/api/webhooks/jira \
     -H "Content-Type: application/json" \
     -H "X-Jira-Event-Type: issue_created" \
     -d '{"issue":{"key":"PROJ-123","fields":{"issuetype":{"name":"bug"},"priority":{"name":"High"}}}}'
   ```

2. 或使用专用端点（如果使用方法2）：
   ```bash
   curl -X POST http://localhost:12345/jira \
     -H "Content-Type: application/json" \
     -H "X-Jira-Event-Type: issue_created" \
     -d '{"issue":{"key":"PROJ-123","fields":{"issuetype":{"name":"bug"},"priority":{"name":"High"}}}}'
   ```

3. 检查返回的任务ID和状态

4. 查看日志文件：
   ```bash
   cat /tmp/jira_webhook_logs/jira_*.log
   ```