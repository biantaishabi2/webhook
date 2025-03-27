# Agent集成与任务分发设计

本文档描述了基于项目的Agent任务分发系统的设计方案，用于扩展现有webhook服务的功能。

## 1. 系统概述

该系统将允许webhook端点根据不同任务类型调用不同的agent执行工作。每个项目拥有独立的工作目录，与远程代码仓库保持同步，agent可根据任务描述中的文档路径访问和修改文件，完成工作后提交到分支并创建Tower待办事项供人工审核。

## 2. 核心组件

### 2.1 项目管理器 (`app/services/project_manager.py`)

- 管理项目元数据和配置
- 为每个项目分配唯一标识和工作目录
- 处理项目初始化和配置更新
- 提供项目间的隔离

### 2.2 Agent注册表 (`app/services/agent_registry.py`)

- 注册不同类型的agent及其能力
- 维护agent与项目的关联关系
- 根据任务类型和要求选择最合适的agent
- 管理agent的运行时环境和依赖

### 2.3 任务解析器 (`app/services/task_parser.py`)

- 从webhook请求中提取任务相关信息
- 识别任务类型、项目ID和优先级
- 解析任务描述中的文档路径和指令
- 将非结构化描述转换为agent可执行的结构化指令

### 2.4 Git仓库管理器 (`app/services/git_manager.py`)

- 克隆和同步远程仓库
- 创建和切换分支
- 执行代码提交和推送操作
- 处理合并冲突和权限问题

### 2.5 工作空间管理器 (`app/services/workspace_manager.py`)

- 为每个任务创建隔离的工作环境
- 准备必要的文件和资源
- 管理工作空间的生命周期
- 任务完成后清理资源

### 2.6 Tower集成服务 (`app/services/tower_integration.py`)

- 增强现有Tower API集成
- 创建和管理待办事项
- 支持审核工作流
- 提供任务状态更新和通知

## 3. 数据模型

### 3.1 项目模型 (`app/models/project.py`)

```python
class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    repository: RepositoryConfig
    tower: TowerConfig
    agents: List[str]
    workspace_path: str
    metadata: Dict[str, Any] = {}
```

### 3.2 Agent模型 (`app/models/agent.py`)

```python
class Agent(BaseModel):
    id: str
    name: str
    capabilities: List[str]
    projects: List[str] = []
    handle_all_projects: bool = False
    config: Dict[str, Any] = {}
```

### 3.3 任务模型 (`app/models/task.py`)

```python
class Task(BaseModel):
    id: str
    type: str
    project_id: str
    description: str
    document_paths: List[str] = []
    agent_id: Optional[str] = None
    branch_name: Optional[str] = None
    status: str = "pending"
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
```

## 4. 工作流程

### 4.1 任务接收

1. Webhook端点接收请求
2. 验证请求合法性
3. 解析请求内容获取任务信息
4. 创建任务记录

```python
@router.post("/tasks")
async def receive_task_webhook(request: Request):
    payload = await request.json()
    
    # 识别任务类型和项目
    task_type = task_parser.identify_task_type(payload)
    project_id = task_parser.extract_project_id(payload)
    
    # 提取文档路径
    document_paths = task_parser.extract_document_paths(payload)
    
    # 创建任务记录
    task = await task_service.create_task(
        type=task_type,
        project_id=project_id,
        description=payload.get("description", ""),
        document_paths=document_paths
    )
    
    # 异步处理任务
    background_tasks.add_task(process_task, task.id)
    
    return {"task_id": task.id, "status": "accepted"}
```

### 4.2 任务处理

1. 加载项目配置
2. 准备工作环境
3. 选择合适的agent
4. 执行任务

```python
async def process_task(task_id: str):
    task = await task_service.get_task(task_id)
    project = await project_manager.get_project(task.project_id)
    
    # 更新任务状态
    await task_service.update_status(task_id, "processing")
    
    try:
        # 准备工作环境
        workspace = await workspace_manager.setup_workspace(project.id)
        
        # 准备代码仓库
        branch_name = f"task/{task_id}"
        await git_manager.setup_repository(
            workspace_path=workspace.path,
            repo_url=project.repository.url,
            branch_name=branch_name
        )
        
        # 更新任务分支信息
        await task_service.update_branch(task_id, branch_name)
        
        # 选择agent
        agent = await agent_registry.select_agent(task.type, project.id)
        
        # 执行任务
        result = await agent_executor.execute(
            agent_id=agent.id,
            task_id=task.id,
            workspace_path=workspace.path,
            document_paths=task.document_paths
        )
        
        # 提交代码更改
        commit_message = f"完成任务: {task.description[:50]}"
        await git_manager.commit_and_push(
            workspace_path=workspace.path,
            branch_name=branch_name,
            message=commit_message
        )
        
        # 创建Tower待办事项
        todo = await tower_integration.create_review_todo(
            project_id=project.tower.project_id,
            todolist_id=project.tower.todolist_id,
            title=f"审核: {task.description[:50]}",
            description=generate_review_description(task, branch_name, result),
            assignee=project.tower.reviewers[0]  # 可以实现更复杂的分配逻辑
        )
        
        # 更新任务结果
        await task_service.complete_task(
            task_id=task.id,
            result={
                "status": "completed",
                "branch": branch_name,
                "tower_todo_id": todo.id
            }
        )
        
    except Exception as e:
        # 处理错误
        await task_service.fail_task(task_id, str(e))
```

### 4.3 代码审核与合并

1. 审核者在Tower中接收待办事项
2. 审核代码更改
3. 批准后合并分支
4. 更新任务状态

## 5. 项目目录结构

```
/projects/
  /{project_id}/
    /repo/              # 代码仓库
    /docs/              # 项目文档
    /tasks/             # 任务历史记录
    /config.json        # 项目配置
```

## 6. 配置示例

### 6.1 项目配置

```json
{
  "id": "project-123",
  "name": "示例项目",
  "description": "这是一个示例项目",
  "repository": {
    "url": "git@github.com:user/repo.git",
    "credentials": "credentials-id",
    "default_branch": "main"
  },
  "tower": {
    "project_id": "tower-project-id",
    "todolist_id": "review-todolist-id",
    "reviewers": ["user1", "user2"]
  },
  "agents": ["code-review", "doc-generator", "bug-fix"]
}
```

### 6.2 Agent配置

```json
{
  "id": "code-review",
  "name": "代码审查Agent",
  "capabilities": ["code-review", "static-analysis", "best-practices"],
  "projects": ["project-123", "project-456"],
  "handle_all_projects": false,
  "config": {
    "max_files": 10,
    "ignored_patterns": ["*.log", "node_modules/", "dist/"]
  }
}
```

## 7. 实现注意事项

1. **安全性**：
   - 对webhook请求强认证
   - 限制agent访问权限
   - 安全管理代码仓库凭证

2. **可扩展性**：
   - 插件架构支持添加新的agent类型
   - 分布式任务处理支持高并发
   - 模块化设计便于功能扩展

3. **可靠性**：
   - 任务状态持久化
   - 失败重试机制
   - 全面的错误处理和日志记录

4. **开发者体验**：
   - 清晰的项目配置
   - 友好的Tower待办事项格式
   - 详细的任务执行记录

## 8. 后续工作

1. 实现基础架构和核心组件
2. 开发和测试基本的agent类型
3. 构建项目管理和配置界面
4. 完善Tower集成和审核流程
5. 添加监控和指标收集
6. 进行全面的安全审计