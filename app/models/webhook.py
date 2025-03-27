from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID, uuid4

# Webhook请求模型
class WebhookRequest(BaseModel):
    """外部系统发送的webhook原始请求数据模型"""
    payload: Dict[str, Any]
    headers: Dict[str, str] = {}
    source: str

# 任务模型
class Task(BaseModel):
    """任务模型，表示由webhook触发的本地程序执行任务"""
    id: UUID = Field(default_factory=uuid4)
    source: str
    event_type: str
    program: str
    parameters: Dict[str, Any] = {}
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

# 任务创建响应
class TaskResponse(BaseModel):
    """任务创建或查询的响应"""
    task_id: UUID
    status: str
    message: str = "Task accepted"
    
# 任务状态详情
class TaskStatus(BaseModel):
    """任务状态详情"""
    id: UUID
    status: str
    program: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_task(cls, task: Task) -> 'TaskStatus':
        execution_time = None
        if task.started_at and task.completed_at:
            execution_time = (task.completed_at - task.started_at).total_seconds()
        
        return cls(
            id=task.id,
            status=task.status,
            program=task.program,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            execution_time=execution_time,
            error_message=task.error_message,
            result=task.result
        )