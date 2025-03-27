#!/usr/bin/env python
"""
全面测试Tower API
"""

import json
import requests
import sys

# Tower应用凭据
CLIENT_ID = "0d7e96f946d17a4a86ff03619b3f5687ce4c2194253533142025cc9b2a0f842c"
CLIENT_SECRET = "33e6f7cc01029fbe427fc5d4b293bf8ed1d44fbb2c10b5734670eb7482cdc37d"

# 从文件加载令牌
def load_token():
    try:
        with open('tower_token.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载令牌出错: {str(e)}")
        return None

# 使用refresh_token刷新访问令牌
def refresh_token(token_data):
    refresh_token = token_data.get('refresh_token')
    if not refresh_token:
        print("没有可用的刷新令牌")
        return None
    
    url = "https://tower.im/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    try:
        print("尝试刷新访问令牌...")
        response = requests.post(url, data=payload)
        print(f"刷新响应状态码: {response.status_code}")
        print(f"刷新响应内容: {response.text}")
        
        if response.status_code == 200:
            new_token_data = response.json()
            # 保存新令牌
            with open('tower_token.json', 'w') as f:
                json.dump(new_token_data, f, indent=2)
            print("成功刷新并保存令牌")
            return new_token_data
    except Exception as e:
        print(f"刷新令牌时出错: {str(e)}")
    
    return None

# 尝试使用不同的API路径获取任务
def try_get_task(access_token, todo_guid):
    # 尝试不同的API路径和请求方式
    api_paths = [
        f"https://tower.im/api/v1/todos/{todo_guid}",
        f"https://tower.im/api/v1/todos?id={todo_guid}",
        f"https://tower.im/api/v1/todos?guid={todo_guid}"
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("\n尝试不同的API路径获取任务...")
    
    for api_path in api_paths:
        try:
            print(f"\n请求: {api_path}")
            print(f"请求头: {headers}")
            response = requests.get(api_path, headers=headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("成功获取任务!")
                result = response.json()
                print(f"响应内容前100个字符: {str(result)[:100]}...")
                return result
            else:
                print(f"API响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"请求出错: {str(e)}")
    
    return None

# 尝试获取用户信息
def try_get_user_info(access_token):
    url = "https://tower.im/api/v1/members/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n尝试获取当前用户信息...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取用户信息!")
            result = response.json()
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 尝试列出团队
def try_list_teams(access_token):
    url = "https://tower.im/api/v1/teams"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n尝试列出团队...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取团队列表!")
            result = response.json()
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 主函数
def main():
    # 1. 加载令牌
    token_data = load_token()
    if not token_data:
        print("无法加载访问令牌")
        return 1
    
    # 2. 获取访问令牌
    access_token = token_data.get('access_token')
    if not access_token:
        print("访问令牌不可用")
        return 1
    
    print(f"使用访问令牌: {access_token[:10]}...")
    
    # 3. 尝试获取用户信息
    user_info = try_get_user_info(access_token)
    
    # 4. 尝试列出团队
    teams = try_list_teams(access_token)
    
    # 5. 尝试获取任务
    # todo_guid从之前的日志获取
    todo_guid = "6e20ab472bdecba96d586cd033651367"
    task_info = try_get_task(access_token, todo_guid)
    
    if task_info:
        # 保存任务信息
        with open('tower_task_info.json', 'w', encoding='utf-8') as f:
            json.dump(task_info, f, indent=2, ensure_ascii=False)
        print(f"\n任务信息已保存到 tower_task_info.json")
    
    print("\nAPI测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())