#!/usr/bin/env python
"""
示例Python程序，用于测试webhook触发

此程序会被webhook服务调用，参数通过命令行传递
"""

import sys
import argparse
import json
import time
from datetime import datetime

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Hello World Webhook处理程序')
    parser.add_argument('--repository', type=str, help='仓库名称')
    parser.add_argument('--branch', type=str, help='分支名称')
    parser.add_argument('--commit', type=str, help='提交ID')
    parser.add_argument('--timestamp', type=float, help='时间戳')
    parser.add_argument('--test_param1', type=str, help='测试参数1')
    parser.add_argument('--test_param2', type=str, help='测试参数2')
    
    args = parser.parse_args()
    
    # 记录日志
    with open('/tmp/webhook_test.log', 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] Webhook triggered!\n")
        f.write(f"Arguments: {json.dumps(vars(args), indent=2)}\n")
        f.write("-" * 40 + "\n")
    
    # 打印信息
    print(f"Hello from webhook triggered script!")
    print(f"Current time: {datetime.now().isoformat()}")
    print(f"Received parameters: {json.dumps(vars(args), indent=2)}")
    
    # 模拟处理时间
    print("Processing...")
    time.sleep(1)
    print("Done!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())