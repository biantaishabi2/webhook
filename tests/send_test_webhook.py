import requests
import json
import os
import argparse
from datetime import datetime
import uuid

# 默认 webhook 地址
DEFAULT_WEBHOOK_URL = "http://127.0.0.1:12345/"

# --- 直接在此处定义 Payload ---
DEFAULT_PAYLOAD = {
  "action": "created",
  "data": {
    "project": {
      "guid": "5dc713a15ab57a0bcefcc2969729b6c4",
      "name": "test敏捷迭代"
    },
    "todo": {
      "guid": "3cb5099ee118308450440e6a5c4fb134", # 这是 测试20 的 GUID
      "title": "测试20 ",
      "updated_at": "2025-03-29T07:15:09.910Z",
      "handler": {
        "guid": "f91066231c2e352d46ecb35b5e8911c9",
        "nickname": "王博"
      },
      "due_at": None,
      "labels": [],
      "priority": "normal",
      "desc": "<p>计算1+1结果写入result.md, 路径在/home/wangbo/document/wangbo/projects/test_agile</p>", # 使用之前测试的描述，你可以修改
      "parent": {}
    },
    "todolist": {
      "guid": "36a965becd322f70671bff87f6ae84b2",
      "title": "自动化任务",
      "desc": None
    }
  }
}
# --- Payload 定义结束 ---

def send_webhook(url: str, payload: dict, event_type: str = "todos"):
    """发送模拟的Tower Webhook请求"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Test-Webhook-Script-Hardcoded',
        'X-Tower-Event': event_type,
        'X-Tower-Delivery': str(uuid.uuid4()) # 模拟一个唯一的 delivery ID
        # 'X-Tower-Signature': '...' # 如果需要，可以添加签名验证逻辑
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # 如果请求失败 (状态码 >= 400)，则抛出异常

        print(f"Webhook sent successfully to {url}")
        print(f"Status Code: {response.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("Response Body (non-JSON):")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook to {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Send a hardcoded test Tower webhook payload to a specified URL.")
    parser.add_argument(
        "-u", "--url",
        default=DEFAULT_WEBHOOK_URL,
        help=f"The URL of the webhook receiver service (default: {DEFAULT_WEBHOOK_URL})"
    )
    parser.add_argument(
        "-e", "--event-type",
        default="todos",
        choices=["todos", "attachments", "comments", "etc"], # 可以根据需要扩展
        help="The value for the X-Tower-Event header (default: todos)"
    )

    args = parser.parse_args()

    # 直接使用硬编码的 Payload
    payload_data = DEFAULT_PAYLOAD

    # 发送 webhook
    send_webhook(args.url, payload_data, args.event_type)

if __name__ == "__main__":
    main()
