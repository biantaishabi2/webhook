#!/usr/bin/env python
"""
测试Tower API，尝试JSONAPI格式
"""

import json
import requests
import sys
import os

# 从文件加载令牌
def load_token():
    try:
        with open('tower_token.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载令牌出错: {str(e)}")
        return None

# 尝试不同的项目列表API
def try_different_project_apis(access_token):
    """尝试不同的项目API路径和格式"""
    apis = [
        # 标准API v1路径
        {
            "url": "https://tower.im/api/v1/projects", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        },
        # 尝试API v1，显式指定Accept为jsonapi格式
        {
            "url": "https://tower.im/api/v1/projects", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.api+json"
            }
        },
        # 尝试API v1，加上jsonapi路径
        {
            "url": "https://tower.im/api/v1/jsonapi/projects", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        },
        # 尝试无版本号路径
        {
            "url": "https://tower.im/api/projects", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        },
        # 尝试团队级别的项目
        {
            "url": "https://tower.im/api/v1/teams/current/projects", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        }
    ]
    
    print("\n尝试不同的项目API路径...")
    
    for api in apis:
        try:
            print(f"\n请求: {api['url']}")
            print(f"请求头: {api['headers']}")
            response = requests.get(api['url'], headers=api['headers'])
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("请求成功!")
                try:
                    result = response.json()
                    print(f"响应内容前100个字符: {str(result)[:100]}...")
                    return api['url'], result
                except json.JSONDecodeError:
                    print(f"响应不是有效的JSON: {response.text[:200]}...")
            else:
                print(f"API响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"请求出错: {str(e)}")
    
    return None, None

# 尝试不同任务详情API
def try_different_todo_apis(access_token, todo_guid):
    """尝试不同的任务API路径和格式"""
    apis = [
        # 标准API v1路径
        {
            "url": f"https://tower.im/api/v1/todos/{todo_guid}", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        },
        # 尝试API v1，显式指定Accept为jsonapi格式
        {
            "url": f"https://tower.im/api/v1/todos/{todo_guid}", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.api+json"
            }
        },
        # 尝试API v1，加上jsonapi路径
        {
            "url": f"https://tower.im/api/v1/jsonapi/todos/{todo_guid}", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        },
        # 尝试无版本号路径
        {
            "url": f"https://tower.im/api/todos/{todo_guid}", 
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        },
        # 尝试使用query参数
        {
            "url": f"https://tower.im/api/v1/todos", 
            "params": {"guid": todo_guid},
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        }
    ]
    
    print("\n尝试不同的任务API路径...")
    
    for api in apis:
        try:
            url = api['url']
            headers = api['headers']
            params = api.get('params', None)
            
            print(f"\n请求: {url}")
            if params:
                print(f"参数: {params}")
            print(f"请求头: {headers}")
            
            response = requests.get(url, headers=headers, params=params)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("请求成功!")
                try:
                    result = response.json()
                    print(f"响应内容前100个字符: {str(result)[:100]}...")
                    return url, result
                except json.JSONDecodeError:
                    print(f"响应不是有效的JSON: {response.text[:200]}...")
            else:
                print(f"API响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"请求出错: {str(e)}")
    
    return None, None

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
    
    # 3. 尝试不同的项目API
    success_url, projects = try_different_project_apis(access_token)
    
    if projects:
        # 保存项目列表
        with open('tower_projects_jsonapi.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"\n项目列表已保存到 tower_projects_jsonapi.json")
    
    # 4. 尝试不同的任务API
    todo_guid = "6e20ab472bdecba96d586cd033651367"
    print(f"\n使用任务ID: {todo_guid}")
    
    success_url, todo_details = try_different_todo_apis(access_token, todo_guid)
    
    if todo_details:
        # 保存任务详情
        with open('tower_todo_details_jsonapi.json', 'w', encoding='utf-8') as f:
            json.dump(todo_details, f, indent=2, ensure_ascii=False)
        print(f"\n任务详情已保存到 tower_todo_details_jsonapi.json")
    
    print("\nAPI测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())