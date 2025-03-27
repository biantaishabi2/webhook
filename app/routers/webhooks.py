from fastapi import APIRouter, Request, Depends, HTTPException, Path, Body
from typing import Dict, Any, Optional
from app.models.webhook import WebhookRequest, TaskResponse, TaskStatus
from app.services.task_runner import dispatch_task, get_task
from app.utils.auth import verify_token
from app.utils.logging import get_logger
from uuid import UUID
import json

router = APIRouter()
logger = get_logger(__name__)

@router.post("/webhooks/{source}", response_model=TaskResponse, dependencies=[Depends(verify_token)])
async def receive_webhook(
    request: Request,
    source: str = Path(..., description="Webhook source (github, gitlab, custom)"),
):
    """
    接收来自外部系统的webhook请求
    """
    # 获取请求体和请求头
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        payload = {}
    
    headers = dict(request.headers)
    
    # 确定事件类型
    event_type = "unknown"
    
    # GitHub事件类型
    if source == "github":
        event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    # GitLab事件类型
    elif source == "gitlab":
        event_type = request.headers.get("X-Gitlab-Event", "unknown")
    
    # 自定义事件类型
    elif source == "custom":
        event_type = payload.get("event_type", "unknown")
    
    logger.info(f"Received {source} webhook: {event_type}")
    
    # 提取参数数据
    params = {}
    
    # GitHub参数提取
    if source == "github" and event_type == "push":
        if "repository" in payload and "ref" in payload:
            params = {
                "repository": payload.get("repository", {}).get("name", ""),
                "branch": payload.get("ref", "").replace("refs/heads/", ""),
                "commit": payload.get("after", "")
            }
    
    # GitLab参数提取
    elif source == "gitlab" and event_type == "push":
        params = {
            "repository": payload.get("project", {}).get("name", ""),
            "branch": payload.get("ref", "").replace("refs/heads/", ""),
            "commit": payload.get("after", "")
        }
    
    # 自定义参数提取
    elif source == "custom":
        params = payload.get("params", {})
    
    # 分发任务
    task = await dispatch_task(source, event_type, params)
    
    return TaskResponse(
        task_id=task.id,
        status=task.status,
        message=f"Task created for {source}:{event_type}"
    )

@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: UUID = Path(..., description="Task ID")
):
    """
    获取任务状态
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskStatus.from_task(task)