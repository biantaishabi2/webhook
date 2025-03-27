# 环境变量设置指南

本文档说明如何配置项目所需的环境变量，特别是与Tower API集成相关的敏感凭据。

## 敏感信息处理

项目使用环境变量来处理敏感信息，如API密钥和客户端密钥，避免将这些信息硬编码在代码中。

## 环境变量列表

以下是项目需要的主要环境变量：

| 环境变量 | 说明 | 默认值 |
|---------|------|-------|
| `TOWER_CLIENT_ID` | Tower API客户端ID | - |
| `TOWER_CLIENT_SECRET` | Tower API客户端密钥 | - |
| `WEBHOOK_TOKEN` | Webhook认证令牌 | `test_secret_token` |
| `PORT` | 服务监听端口 | `12345` |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 配置方法

### 方法1: 使用.env文件

1. 在 `config` 目录下创建 `.env` 文件：

```bash
cp config/samples/env.sample config/.env
```

2. 编辑 `.env` 文件，填入您的实际配置：

```bash
# Tower API 凭据
TOWER_CLIENT_ID="您的Tower客户端ID"
TOWER_CLIENT_SECRET="您的Tower客户端密钥"

# 其他配置...
```

这种方法的优点是启动脚本会自动加载这些变量。

### 方法2: 使用环境变量脚本

1. 编辑 `scripts/set_env.sh` 脚本：

```bash
vi scripts/set_env.sh
```

2. 更新脚本中的值，然后运行：

```bash
source scripts/set_env.sh
```

这种方法适合临时设置或测试不同的配置。

### 方法3: 直接设置环境变量

```bash
export TOWER_CLIENT_ID="您的Tower客户端ID"
export TOWER_CLIENT_SECRET="您的Tower客户端密钥"
# 设置其他变量...
```

## 注意事项

1. **不要将含有实际密钥的 `.env` 文件提交到版本控制系统**
2. 在生产环境中，建议通过系统配置（如systemd环境变量）设置这些值
3. 对于systemd服务，可以在服务文件中使用 `Environment=KEY=VALUE` 语法

## 验证配置

可以使用以下命令验证环境变量是否正确设置：

```bash
python -c "import os; print(f'TOWER_CLIENT_ID: {os.environ.get(\"TOWER_CLIENT_ID\", \"未设置\")}')"
```

## 获取Tower API凭据

如需获取Tower API凭据，请联系Tower管理员或参考Tower API文档。