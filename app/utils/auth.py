from fastapi import Request, HTTPException, Header, Depends
from typing import Optional
import os

# 简单的token认证
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN", "test_secret_token")

async def verify_token(request: Request, x_webhook_token: Optional[str] = Header(None, alias="X-Webhook-Token")) -> None:
    """验证webhook请求的token
    
    可以通过以下两种方式提供token:
    1. 请求头: X-Webhook-Token
    2. 查询参数: ?token=xxx
    """
    token = x_webhook_token
    
    # 如果请求头中没有token，尝试从查询参数获取
    if not token:
        token = request.query_params.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    expected_token = WEBHOOK_TOKEN
    print(f"Received token: '{token}', Expected token: '{expected_token}'")
    
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")