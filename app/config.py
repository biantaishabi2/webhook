import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# 安全配置
class WebhookAuthConfig(BaseModel):
    secret: Optional[str] = None
    token: Optional[str] = None
    auth_type: str = "none"  # "none", "signature", "token", "ip"
    allowed_ips: List[str] = []

# 程序执行配置
class ProgramConfig(BaseModel):
    command: str
    params: List[str] = []
    working_dir: Optional[str] = None
    timeout: int = 300  # 秒
    run_async: bool = True

# 映射规则
class MappingRule(BaseModel):
    condition: str
    program: str

# 当前配置
WEBHOOK_CONFIGS: Dict[str, WebhookAuthConfig] = {
    "github": WebhookAuthConfig(
        secret=os.environ.get("GITHUB_WEBHOOK_SECRET", ""),
        auth_type="signature",
    ),
    "gitlab": WebhookAuthConfig(
        token=os.environ.get("GITLAB_WEBHOOK_TOKEN", ""),
        auth_type="token",
    ),
    "custom": WebhookAuthConfig(
        auth_type="none",
    ),
}

PROGRAM_CONFIGS: Dict[str, ProgramConfig] = {
    "deploy": ProgramConfig(
        command="python /path/to/deploy.py",
        params=["branch", "commit"],
    ),
    "test": ProgramConfig(
        command="python /path/to/test.py",
        params=["branch"],
    ),
    "analyze": ProgramConfig(
        command="python /path/to/analyze.py",
        params=["data"],
    ),
}

# 映射规则
WEBHOOK_TO_PROGRAM_MAPPING: Dict[str, Dict[str, List[MappingRule]]] = {
    "github": {
        "push": [
            MappingRule(condition="branch == 'main'", program="deploy"),
            MappingRule(condition="branch == 'dev'", program="test"),
        ],
    },
    "gitlab": {
        "push": [
            MappingRule(condition="branch == 'main'", program="deploy"),
        ],
    },
    "custom": {
        "data_update": [
            MappingRule(condition="True", program="analyze"),
        ],
    },
}

# 日志配置
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")