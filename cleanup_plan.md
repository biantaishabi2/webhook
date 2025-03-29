# 项目整理记录

## 已完成整理

项目文件已按以下结构整理：

```
/webhook/
  /app/            # 核心应用代码
    /models/       # 数据模型
    /routers/      # API路由
    /services/     # 服务层
    /utils/        # 工具函数
  /tests/          # 测试目录
    /tower/        # Tower API测试 (原test_tower_*.py文件)
    /webhook/      # Webhook测试
    /cloudflare/   # Cloudflare测试
    /fixtures/     # 测试数据 (原tower_*.json文件)
  /config/         # 配置文件
    /samples/      # 示例配置(不含敏感信息)
  /docs/           # 文档
  /scripts/        # 工具和启动脚本
  /services/       # 服务配置文件
  /examples/       # 示例代码
```

## 文件移动记录

1. **测试脚本**:
   - Tower API测试文件 -> tests/tower/
   - Cloudflare测试文件 -> tests/cloudflare/
   - Webhook测试文件 -> tests/webhook/

2. **JSON数据文件**:
   - 所有tower_*.json文件 -> tests/fixtures/

3. **脚本文件**:
   - start_service.sh -> scripts/
   - get_new_token.py -> scripts/
   - get_tower_token.py -> scripts/
   - debug_token.py -> scripts/

4. **服务配置文件**:
   - webhook.service -> services/

## 注意事项

1. 需要修改部分引用路径，确保脚本能正常工作
2. 敏感配置文件(包含token)应添加到.gitignore
3. 测试前请检查路径是否正确

## 下一步计划

1. 创建.gitignore文件，排除敏感数据
2. 更新测试脚本中的路径引用
3. 增加适当的测试文档