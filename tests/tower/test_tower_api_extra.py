#!/usr/bin/env python
"""
测试Tower API的扩展功能
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

# 获取项目列表
def get_projects(access_token):
    """获取项目列表"""
    url = "https://tower.im/api/v1/projects"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n获取项目列表...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取项目列表!")
            result = response.json()
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 获取任务列表
def get_todolist(access_token, todolist_id):
    """获取任务列表详情"""
    url = f"https://tower.im/api/v1/todolists/{todolist_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n获取任务列表 {todolist_id} 详情...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取任务列表详情!")
            result = response.json()
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 获取评论
def get_comments(access_token, todo_id):
    """获取任务评论"""
    url = f"https://tower.im/api/v1/todos/{todo_id}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n获取任务 {todo_id} 的评论...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取任务评论!")
            result = response.json()
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 获取团队信息
def get_teams(access_token):
    """获取团队信息"""
    url = "https://tower.im/api/v1/teams"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n获取团队信息...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取团队信息!")
            result = response.json()
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
    
    # 3. 获取团队信息
    teams = get_teams(access_token)
    if teams:
        with open('tower_teams.json', 'w', encoding='utf-8') as f:
            json.dump(teams, f, indent=2, ensure_ascii=False)
        print(f"团队信息已保存到 tower_teams.json")
    
    # 4. 获取项目列表
    projects = get_projects(access_token)
    if projects:
        with open('tower_projects.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"项目列表已保存到 tower_projects.json")
    
    # 5. 获取任务列表详情
    # 从之前的任务详情中获取任务列表ID
    todolist_id = "68f1211586a95d0b21b88a98377d4134"  # 从任务详情中获取
    todolist = get_todolist(access_token, todolist_id)
    if todolist:
        with open('tower_todolist.json', 'w', encoding='utf-8') as f:
            json.dump(todolist, f, indent=2, ensure_ascii=False)
        print(f"任务列表详情已保存到 tower_todolist.json")
    
    # 6. 获取任务评论
    todo_id = "6e20ab472bdecba96d586cd033651367"  # 从任务详情中获取
    comments = get_comments(access_token, todo_id)
    if comments:
        with open('tower_comments.json', 'w', encoding='utf-8') as f:
            json.dump(comments, f, indent=2, ensure_ascii=False)
        print(f"任务评论已保存到 tower_comments.json")
    
    print("\nAPI测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())