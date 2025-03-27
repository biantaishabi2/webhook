import requests
import json
import argparse
import os
import time
from uuid import UUID

def test_webhook(url, token, source="custom", event_type="test_event"):
    """
    测试webhook接口
    
    参数:
        url: webhook服务URL (例如 http://localhost:12345 或 https://oe-dr-social-by.trycloudflare.com)
        token: 认证token
        source: webhook来源 (custom, github, gitlab)
        event_type: 事件类型
    """
    # 构建URL
    webhook_url = f"{url}/api/webhooks/{source}"
    
    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Token": token
    }
    
    # 调试输出
    print(f"DEBUG - 使用Token: '{token}'")
    if token != "test_secret_token":
        print("警告: Token与默认值不匹配")
    
    # 准备请求体
    if source == "custom":
        payload = {
            "event_type": event_type,
            "params": {
                "timestamp": time.time(),
                "test_param1": "value1",
                "test_param2": "value2"
            }
        }
    elif source == "github":
        payload = {
            "repository": {"name": "test-repo"},
            "ref": "refs/heads/main",
            "after": "1234567890abcdef"
        }
        headers["X-GitHub-Event"] = event_type
    elif source == "gitlab":
        payload = {
            "project": {"name": "test-repo"},
            "ref": "refs/heads/main",
            "after": "1234567890abcdef"
        }
        headers["X-Gitlab-Event"] = event_type
    
    print(f"发送请求到: {webhook_url}")
    print(f"请求头: {json.dumps(headers, indent=2)}")
    print(f"请求体: {json.dumps(payload, indent=2)}")
    
    # 发送请求
    response = requests.post(webhook_url, json=payload, headers=headers)
    
    # 输出结果
    print(f"\n状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        
        # 获取任务ID
        task_id = response.json().get("task_id")
        if task_id:
            # 等待任务处理
            print("\n等待3秒后检查任务状态...")
            time.sleep(3)
            
            # 检查任务状态
            task_url = f"{url}/api/tasks/{task_id}"
            task_response = requests.get(task_url)
            
            print(f"任务状态请求: {task_url}")
            print(f"任务状态码: {task_response.status_code}")
            if task_response.status_code == 200:
                print(f"任务状态: {json.dumps(task_response.json(), indent=2)}")
    else:
        print(f"错误: {response.text}")
    
    return response.status_code == 200

def test_with_query_param(url, token, source="custom"):
    """测试使用查询参数传递token"""
    webhook_url = f"{url}/api/webhooks/{source}?token={token}"
    
    headers = {"Content-Type": "application/json"}
    payload = {"event_type": "query_param_test", "params": {"test": "value"}}
    
    print(f"\n使用查询参数测试 - 发送请求到: {webhook_url}")
    
    response = requests.post(webhook_url, json=payload, headers=headers)
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"错误: {response.text}")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试Webhook服务')
    parser.add_argument('--url', type=str, default='http://localhost:12345', 
                        help='Webhook服务URL')
    parser.add_argument('--token', type=str, default=os.environ.get('WEBHOOK_TOKEN', 'test_secret_token'),
                        help='认证Token')
    parser.add_argument('--source', type=str, default='custom',
                        help='Webhook来源 (custom, github, gitlab)')
    parser.add_argument('--event', type=str, default='test_event',
                        help='事件类型')
    
    args = parser.parse_args()
    
    # 运行主测试
    success = test_webhook(args.url, args.token, args.source, args.event)
    
    # 测试查询参数方式
    if success:
        test_with_query_param(args.url, args.token, args.source)