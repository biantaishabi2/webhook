import logging
import sys
from datetime import datetime
import os
from app.config import LOG_LEVEL

# 创建日志目录
os.makedirs("logs", exist_ok=True)

# 配置日志格式
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# 创建文件处理器
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
file_handler = logging.FileHandler(f"logs/webhook_{current_time}.log")
file_handler.setFormatter(log_format)

# 获取logger实例
def get_logger(name: str):
    logger = logging.getLogger(name)
    
    # 设置日志级别
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger