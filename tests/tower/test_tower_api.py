#!/usr/bin/env python
"""
测试Tower API集成功能
"""

import sys
import json
import os
from app.utils.tower_api import get_access_token, get_todo_details, get_todo_comments

def main():
    """测试Tower API功能"""
    print("测试Tower API访问...")
    
    # 1. 获取访问令牌
    access_token = get_access_token()
    if not access_token:
        print("没有可用的访问令牌，请按照指示获取授权码并配置")
        return 1
    
    print(f"成功获取访问令牌: {access_token[:10]}...")
    
    # 2. 测试数据
    todo_guid = input("请输入要测试的Tower任务GUID (来自webhook日志): ")
    if not todo_guid:
        print("没有提供任务GUID，使用测试值")
        # 使用最后一个webhook中的任务ID
        try:
            log_dir = '/tmp/tower_webhook_logs'
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.startswith('tower_')]
                if log_files:
                    latest_log = sorted(log_files)[-1]
                    with open(os.path.join(log_dir, latest_log), 'r') as f:
                        content = f.read()
                        if '"guid"' in content and '"todo"' in content:
                            import re
                            match = re.search(r'"todo".*?"guid".*?"([a-f0-9]+)"', content)
                            if match:
                                todo_guid = match.group(1)
                                print(f"从日志中提取的任务GUID: {todo_guid}")
        except Exception as e:
            print(f"获取测试任务ID失败: {str(e)}")
    
    if not todo_guid:
        print("无法获取任务GUID，测试失败")
        return 1
    
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