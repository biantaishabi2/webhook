#!/usr/bin/env python
"""
Tower webhook处理程序

专门用于处理来自Tower的webhook请求
"""

import sys
import argparse
import json
import time
from datetime import datetime
import os
import requests

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Tower Webhook处理程序')
    # 添加所有可能需要的参数
    parser.add_argument('--webhook_id', type=str, help='Webhook ID')
    parser.add_argument('--title', type=str, help='标题')
    parser.add_argument('--description', type=str, help='描述')
    parser.add_argument('--status', type=str, help='状态')
    parser.add_argument('--url', type=str, help='URL')
    parser.add_argument('--event_type', type=str, help='事件类型')
    parser.add_argument('--raw_payload', type=str, help='原始的完整payload')
    
    # 添加可能的其他参数
    parser.add_argument('--id', type=str, help='记录ID')
    parser.add_argument('--name', type=str, help='名称')
    parser.add_argument('--content', type=str, help='内容')
    
    # 解析所有传递的参数，忽略未知参数
    args, unknown = parser.parse_known_args()
    
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'webhook_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # 记录所有信息
    with open(log_file, 'w') as f:
        f.write(f"[{datetime.now().isoformat()}] Tower Webhook triggered!\n")
        f.write(f"Event Type: {args.event_type}\n")
        f.write(f"Known Arguments: {json.dumps(vars(args), indent=2)}\n")
        f.write(f"Unknown Arguments: {unknown}\n")
        
        # 如果有原始payload，也记录下来
        if args.raw_payload:
            try:
                raw_data = json.loads(args.raw_payload)
                f.write(f"Raw Payload: {json.dumps(raw_data, indent=2)}\n")
            except json.JSONDecodeError:
                f.write(f"Raw Payload (not JSON): {args.raw_payload}\n")
                
        f.write("-" * 40 + "\n")
    
    # 打印信息
    print(f"Tower webhook handler executed successfully!")
    print(f"Current time: {datetime.now().isoformat()}")
    print(f"Event type: {args.event_type}")
    print(f"Log saved to: {log_file}")
    
    # 根据不同的事件类型执行不同的操作
    if args.event_type == "todos" or (args.raw_payload and '"todo"' in args.raw_payload):
        print("处理Tower待办事项事件...")
        
        # 直接从webhook payload中提取所有信息
        if args.raw_payload:
            try:
                payload = json.loads(args.raw_payload)
                print(f"收到Tower webhook - 操作类型: {payload.get('action', '未知')}")
                
                # 提取任务相关信息
                if "data" in payload:
                    data = payload["data"]
                    
                    # 项目信息
                    project = data.get("project", {})
                    project_id = project.get("guid")
                    project_name = project.get("name")
                    print(f"项目: {project_name} (ID: {project_id})")
                    
                    # 任务信息
                    todo = data.get("todo", {})
                    todo_id = todo.get("guid")
                    todo_title = todo.get("title")
                    todo_updated = todo.get("updated_at")
                    todo_priority = todo.get("priority", "普通")
                    todo_due = todo.get("due_at") or "无截止日期"
                    print(f"任务: {todo_title} (ID: {todo_id})")
                    print(f"优先级: {todo_priority}, 截止日期: {todo_due}")
                    
                    # 处理人信息
                    handler = todo.get("handler", {})
                    handler_name = handler.get("nickname", "未分配")
                    print(f"处理人: {handler_name}")
                    
                    # 任务列表信息
                    todolist = data.get("todolist", {})
                    todolist_name = todolist.get("title")
                    print(f"所属任务列表: {todolist_name}")
                    
                    # 保存全部信息到处理后的文件
                    if todo_id:
                        # 创建一个结构化的信息对象
                        task_info = {
                            "action": payload.get("action"),
                            "timestamp": datetime.now().isoformat(),
                            "project": {
                                "id": project_id,
                                "name": project_name
                            },
                            "todo": {
                                "id": todo_id,
                                "title": todo_title,
                                "updated_at": todo_updated,
                                "priority": todo_priority,
                                "due_at": todo_due
                            },
                            "handler": {
                                "name": handler_name
                            },
                            "todolist": {
                                "name": todolist_name
                            }
                        }
                        
                        # 保存处理后的信息
                        info_file = f'{log_dir}/todo_{todo_id}_info.json'
                        with open(info_file, 'w', encoding='utf-8') as f:
                            json.dump(task_info, f, indent=2, ensure_ascii=False)
                        print(f"任务信息已保存到: {info_file}")
                        
                        # 同时保存原始payload
                        raw_file = f'{log_dir}/todo_{todo_id}_raw.json'
                        with open(raw_file, 'w', encoding='utf-8') as f:
                            json.dump(payload, f, indent=2, ensure_ascii=False)
                        print(f"原始webhook数据已保存到: {raw_file}")
                        
                        # 这里可以添加自定义操作，例如:
                        # - 发送通知
                        # - 更新状态跟踪系统
                        # - 触发其他工作流
                        print(f"任务处理完成: {todo_title}")
                    else:
                        print("未找到任务ID，无法处理")
                else:
                    print("Webhook数据缺少'data'字段")
            except Exception as e:
                print(f"处理webhook数据时出错: {str(e)}")
        else:
            print("未收到有效的webhook数据")
        
        print("Tower待办事项处理完成!")
    else:
        print(f"未知事件类型: {args.event_type}, 不做特殊处理")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())