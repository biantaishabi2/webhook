from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhooks
import uvicorn
import json
import os
from datetime import datetime

app = FastAPI(
    title="Webhook Service",
    description="A service to receive external webhooks and trigger local Python programs",
    version="0.1.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(webhooks.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Webhook Receiver Service is running"}

@app.post("/")
async def receive_root_webhook(request: Request):
    """
    Handle POST requests to the root path for Tower webhooks
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    
    headers = dict(request.headers)
    # 从请求头获取事件类型 (使用小写键名)
    event_type = headers.get("x-tower-event", "unknown")
    signature = headers.get("x-tower-signature", "")
    
    # Log headers for debugging
    from app.utils.logging import get_logger
    logger = get_logger(__name__)
    logger.info(f"Request headers: {headers}")
    
    # Accept the webhook without token verification for now
    # We'll log everything and analyze the correct authentication pattern
    
    # Log the webhook
    logger.info(f"Received Tower webhook: {event_type}")
    logger.info(f"Payload: {payload}")
    
    # Process the webhook
    from app.services.task_runner import dispatch_task
    
    # 将完整payload保存到日志文件以便分析
    # 使用项目的logs目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 使用时间戳命名日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"webhook_{timestamp}.log")
    
    # 记录webhook信息
    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "event_type": event_type,
            "headers": headers,
            "payload": payload
        }, f, indent=2)
    
    # 提取Tower webhook的参数
    # 由于我们不确定Tower具体的数据结构，先提取一些通用字段
    params = {
        # 使用安全的方式获取可能的字段
        "webhook_id": str(payload.get("id", "")),
        "title": str(payload.get("title", "")),
        "description": str(payload.get("description", "")),
        "status": str(payload.get("status", "")),
        "url": str(payload.get("url", "")),
        "event_type": event_type,
        # 添加原始payload以便脚本能够使用完整数据
        "raw_payload": json.dumps(payload)
    }
    
    # 将所有顶级字段添加为参数
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)):
            params[key] = value
    
    logger.info(f"Extracted params for Tower webhook: {params}")
    task = await dispatch_task("tower", event_type, params)
    
    return {
        "task_id": str(task.id),
        "status": task.status,
        "message": f"Task created for tower:{event_type}"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=12345, reload=True)