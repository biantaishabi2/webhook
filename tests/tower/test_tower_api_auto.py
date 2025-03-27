#!/usr/bin/env python
"""
测试Tower API集成功能 - 自动版
"""

import sys
import json
import os
import re
from app.utils.tower_api import get_access_token, get_todo_details, get_todo_comments

def extract_guid_from_log():
    """从webhook日志中提取任务GUID"""
    log_dir = '/tmp/tower_webhook_logs'
    try:
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.startswith('tower_')]
            if log_files:
                # 按文件名排序，获取最新的日志
                latest_log = sorted(log_files)[-1]
                with open(os.path.join(log_dir, latest_log), 'r') as f:
                    content = f.read()
                    if 'Raw Payload' in content:
                        # 通过正则表达式从payload中提取todo GUID
                        match = re.search(r'"todo".*?"guid".*?"([a-f0-9]+)"', content)
                        if match:
                            return match.group(1)
    except Exception as e:
        print(f"提取GUID时出错: {str(e)}")
    
    return None

def find_guid_from_payload_file():
    """从保存的payload文件中提取任务GUID"""
    try:
        payload_file = '/tmp/tower_webhook_payload.json'
        if os.path.exists(payload_file):
            with open(payload_file, 'r') as f:
                data = json.load(f)
                if 'data' in data and 'todo' in data['data']:
                    return data['data']['todo'].get('guid')
    except Exception as e:
        print(f"从payload文件提取GUID时出错: {str(e)}")
    
    return None

def main():
    """测试Tower API功能"""
    print("测试Tower API访问...")
    
    # 1. 获取访问令牌
    access_token = get_access_token()
    if not access_token:
        print("没有可用的访问令牌，请按照指示获取授权码并配置")
        return 1
    
    print(f"成功获取访问令牌: {access_token[:10]}...")
    
    # 2. 尝试不同方法获取任务GUID
    todo_guid = extract_guid_from_log() or find_guid_from_payload_file()
    
    if not todo_guid:
        print("无法自动获取任务GUID，请手动提供")
        # 提供一个硬编码的GUID进行测试
        todo_guid = "6e20ab472bdecba96d586cd033651367"  # 这是从先前看到的payload中提取的
    
    print(f"使用任务GUID: {todo_guid}")
    
    # 3. 获取任务详情
    print(f"\n获取任务 {todo_guid} 的详细信息...")
    todo_details = get_todo_details(todo_guid)
    
    if todo_details:
        print("\n成功获取任务详情!")
        # 保存到文件
        output_file = 'tower_todo_details.json'
        with open(output_file, 'w') as f:
            json.dump(todo_details, f, indent=2)
        print(f"任务详情已保存到: {output_file}")
        
        # 打印部分信息
        print("\n任务基本信息:")
        print(f"标题: {todo_details.get('title', 'N/A')}")
        print(f"描述: {todo_details.get('desc', 'N/A')}")
        print(f"状态: {todo_details.get('status', 'N/A')}")
        print(f"创建时间: {todo_details.get('created_at', 'N/A')}")
        
        # 4. 获取任务评论
        print("\n获取任务评论...")
        comments = get_todo_comments(todo_guid)
        
        if comments:
            comments_file = 'tower_todo_comments.json'
            with open(comments_file, 'w') as f:
                json.dump(comments, f, indent=2)
            print(f"任务评论已保存到: {comments_file}")
            print(f"评论数量: {len(comments)}")
        else:
            print("未找到任务评论或获取失败")
    else:
        print("无法获取任务详情，API调用失败")
        return 1
    
    print("\nTower API测试完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())