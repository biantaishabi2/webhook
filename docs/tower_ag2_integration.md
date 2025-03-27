# Tower与AG2集成指南

本文档说明如何通过Tower webhook触发AG2 Two Agent Executor自动处理任务。

## 功能概述

当在Tower中创建或更新任务时，满足特定条件的任务会自动触发AG2执行器进行处理。这使得您可以利用AI自动化完成某些类型的任务。

## 触发条件

以下任何条件都会触发AG2执行：

1. **任务标签**：包含以下标签之一的任务：
   - AG2
   - AI
   - 自动化
   - 自动
   - GPT

2. **任务标题**：标题包含以下关键词之一：
   - [AG2]
   - [AI]
   - [自动]
   - [GPT]
   - [自动化]

3. **任务列表**：任务属于以下任务列表之一：
   - 自动化任务
   - AI处理
   - AG2任务
   - GPT处理

## 使用方法

### 1. 创建自动化任务

在Tower中创建任务时：

- 添加标签：`AG2`、`自动化`等
- 或在标题前加前缀：`[AG2] 任务标题`
- 或在"自动化任务"列表中创建任务

### 2. 编写任务描述

任务描述应该包含清晰的指示和要求。Webhook处理程序会自动获取任务详情，并将完整描述传递给AG2执行器。

**示例描述**：
```
请查找项目中所有包含deprecated API调用的文件，并生成一个报告。

报告格式要求：
1. 列出每个文件及行号
2. 提供替代方案建议
3. 估计修复工作量
```

### 3. 监控执行

- AG2会自动处理符合条件的任务
- 执行结果会记录在日志中：`/tmp/tower_ag2_logs/`
- 每个任务执行结果都保存为一个独立的JSON文件

## 结果查看

AG2执行完成后的结果存储在：
```
/tmp/tower_ag2_logs/ag2_result_{task_id}_{timestamp}.json
```

结果文件包含：
- 任务定义
- 执行结果
- 执行时间
- 时间戳

## 配置

AG2 Two Agent Executor的配置文件位于：
```
/home/wangbo/document/wangbo/task_planner/ag2-wrapper/ag2_wrapper/core/config.py
```

## 故障排除

常见问题及解决方案：

1. **AG2未启动**：
   - 检查AG2路径是否正确：`/home/wangbo/document/wangbo/task_planner/ag2-wrapper`
   - 查看日志：`/tmp/tower_ag2_handler.log`

2. **执行超时**：
   - 默认超时时间为10分钟
   - 可在`tower_ag2_handler.py`中修改`timeout`参数

3. **模型或API错误**：
   - 确保环境变量`OPENROUTER_API_KEY`已设置
   - 检查API密钥是否有效
   - 参考AG2配置中的模型设置

## 日志位置

- Tower webhook处理日志：`/tmp/tower_webhook_logs/`
- AG2处理日志：`/tmp/tower_ag2_logs/`
- AG2执行器日志：`/tmp/tower_ag2_handler.log`