import asyncio
import subprocess
import shlex
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from uuid import UUID

from app.models.webhook import Task
from app.utils.logging import get_logger

logger = get_logger(__name__)

# 存储任务信息的内存字典
tasks_store: Dict[str, Task] = {}

async def run_program(task: Task) -> None:
    """异步执行本地Python程序"""
    task.status = "running"
    task.started_at = datetime.now()
    tasks_store[str(task.id)] = task
    
    try:
        # 构建命令
        base_command = f"python {task.program}"
        command_args = []
        
        # 添加参数
        for key, value in task.parameters.items():
            # 跳过None值
            if value is None:
                continue
                
            if isinstance(value, (str, int, float, bool)):
                # 对字符串做额外处理，确保包含空格或特殊字符的值被正确引用
                if isinstance(value, str):
                    # 如果是特别长的JSON字符串或包含引号，用单引号包围
                    if '"' in value or len(value) > 100:
                        value = f"'{value}'"
                    # 包含空格的一般参数，用双引号包围
                    elif ' ' in value:
                        value = f'"{value}"'
                
                command_args.append(f"--{key}={value}")
        
        full_command = f"{base_command} {' '.join(command_args)}"
        logger.info(f"Running command: {full_command}")
        
        # 执行命令
        process = await asyncio.create_subprocess_shell(
            full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # 更新任务状态
        if process.returncode == 0:
            task.status = "completed"
            task.result = {
                "stdout": stdout.decode().strip() if stdout else "",
                "returncode": 0
            }
            logger.info(f"Task {task.id} completed successfully")
        else:
            task.status = "failed"
            task.error_message = stderr.decode().strip() if stderr else "Unknown error"
            task.result = {
                "stdout": stdout.decode().strip() if stdout else "",
                "stderr": stderr.decode().strip() if stderr else "",
                "returncode": process.returncode
            }
            logger.error(f"Task {task.id} failed: {task.error_message}")
    
    except Exception as e:
        logger.exception(f"Error executing task {task.id}: {str(e)}")
        task.status = "failed"
        task.error_message = str(e)
    
    finally:
        task.completed_at = datetime.now()
        tasks_store[str(task.id)] = task

def get_task(task_id: UUID) -> Optional[Task]:
    """从存储中获取任务信息"""
    return tasks_store.get(str(task_id))

def get_all_tasks() -> List[Task]:
    """获取所有任务"""
    return list(tasks_store.values())

async def dispatch_task(source: str, event_type: str, data: Dict[str, Any]) -> Task:
    """创建并分发任务"""
    # 这里可以从配置中读取映射关系，决定执行哪个程序
    # 为简化示例，这里直接映射
    program_mapping = {
        "github:push": "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py",
        "gitlab:push": "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py",
        "custom:data_update": "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py",
        "custom:test_event": "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py",
        "custom:query_param_test": "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py",
        # 添加Tower webhook映射
        "tower:todos": "/home/wangbo/document/wangbo/dev/webhook/examples/tower_webhook_handler.py",
        # AG2执行器映射
        "tower:created": "/home/wangbo/document/wangbo/dev/webhook/examples/tower_ag2_handler.py",
        "tower:updated": "/home/wangbo/document/wangbo/dev/webhook/examples/tower_ag2_handler.py",
    }
    
    program_key = f"{source}:{event_type}"
    
    # 为Tower事件设置专门的处理程序
    if source == "tower":
        default_program = "/home/wangbo/document/wangbo/dev/webhook/examples/tower_webhook_handler.py"
    else:
        default_program = "/home/wangbo/document/wangbo/dev/webhook/examples/hello_world.py"
    
    program_path = program_mapping.get(program_key, default_program)
    
    # 记录找不到映射的情况
    if program_key not in program_mapping:
        logger.warning(f"No specific mapping found for {program_key}, using default handler: {default_program}")
    
    # 创建任务
    task = Task(
        source=source,
        event_type=event_type,
        program=program_path,
        parameters=data
    )
    
    # 保存任务
    tasks_store[str(task.id)] = task
    
    # 异步执行
    asyncio.create_task(run_program(task))
    
    logger.info(f"Task {task.id} dispatched for {program_key}")
    return task