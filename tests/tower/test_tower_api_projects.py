#!/usr/bin/env python
"""
测试Tower API的项目和任务相关接口
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

# 尝试获取项目列表
def list_projects(access_token):
    """尝试获取项目列表"""
    # 尝试不同的API路径
    urls = [
        "https://tower.im/api/v1/projects",
        "https://tower.im/api/v2/projects"
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("\n尝试获取项目列表...")
    
    for url in urls:
        try:
            print(f"\n请求: {url}")
            response = requests.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("成功获取项目列表!")
                result = response.json()
                print(f"响应内容前100个字符: {str(result)[:100]}...")
                return url, result
            else:
                print(f"API响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"请求出错: {str(e)}")
    
    return None, None

# 尝试获取任务详情
def get_todo_details(access_token, todo_guid):
    """尝试获取任务详情"""
    # 尝试不同的API路径
    urls = [
        f"https://tower.im/api/v1/todos/{todo_guid}",
        f"https://tower.im/api/v2/todos/{todo_guid}",
        f"https://tower.im/api/v1/todos/show?guid={todo_guid}"
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("\n尝试获取任务详情...")
    
    for url in urls:
        try:
            print(f"\n请求: {url}")
            response = requests.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("成功获取任务详情!")
                result = response.json()
                print(f"响应内容前100个字符: {str(result)[:100]}...")
                return url, result
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
    
    # 3. 尝试获取项目列表
    success_url, projects = list_projects(access_token)
    
    if projects:
        # 保存项目列表
        with open('tower_projects.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"\n项目列表已保存到 tower_projects.json")
        
        # 提取项目ID
        try:
            if 'data' in projects and len(projects['data']) > 0:
                print("\n找到的项目:")
                for idx, project in enumerate(projects['data'][:5]):  # 只显示前5个
                    project_id = project.get('id')
                    project_name = project.get('attributes', {}).get('name', 'Unknown')
                    print(f"  {idx+1}. ID: {project_id}, 名称: {project_name}")
        except Exception as e:
            print(f"处理项目列表时出错: {str(e)}")
    
    # 4. 尝试获取任务详情
    # 尝试从webhook日志中获取的任务ID
    todo_guid = "6e20ab472bdecba96d586cd033651367"
    print(f"\n使用任务ID: {todo_guid}")
    
    success_url, todo_details = get_todo_details(access_token, todo_guid)
    
    if todo_details:
        # 保存任务详情
        with open('tower_todo_details.json', 'w', encoding='utf-8') as f:
            json.dump(todo_details, f, indent=2, ensure_ascii=False)
        print(f"\n任务详情已保存到 tower_todo_details.json")
    
    print("\nAPI测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())