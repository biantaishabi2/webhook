#!/usr/bin/env python
"""
调试token读取问题的脚本
"""

import os
import sys
from dotenv import load_dotenv

# 测试环境变量读取
def debug_env():
    print("==== 环境变量测试 ====")
    
    # 测试直接读取
    direct_token = os.environ.get("WEBHOOK_TOKEN")
    print(f"直接读取: WEBHOOK_TOKEN = '{direct_token}'")
    
    # 测试dotenv读取
    print("\n加载.env文件...")
    load_dotenv(verbose=True)
    
    dotenv_token = os.environ.get("WEBHOOK_TOKEN")
    print(f"dotenv读取: WEBHOOK_TOKEN = '{dotenv_token}'")
    
    # 测试默认值
    default_token = os.environ.get("WEBHOOK_TOKEN", "默认值")
    print(f"带默认值读取: WEBHOOK_TOKEN = '{default_token}'")
    
    # 打印所有环境变量
    print("\n环境变量列表: ")
    for k, v in os.environ.items():
        if "TOKEN" in k:
            print(f"  {k} = {v}")

if __name__ == "__main__":
    debug_env()