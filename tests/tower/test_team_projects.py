#!/usr/bin/env python
"""
测试Tower API获取团队项目
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

# 获取团队项目
def get_team_projects(access_token, team_id):
    """获取特定团队的项目列表"""
    url = f"https://tower.im/api/v1/teams/{team_id}/projects"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n获取团队 {team_id} 的项目...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取团队项目列表!")
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
    
    # 3. 从团队信息文件中获取团队ID
    team_id = None
    try:
        with open('tower_teams.json', 'r') as f:
            teams_data = json.load(f)
            if 'data' in teams_data and len(teams_data['data']) > 0:
                team_id = teams_data['data'][0]['id']
                print(f"找到团队ID: {team_id}")
    except Exception as e:
        print(f"读取团队信息出错: {str(e)}")
    
    if not team_id:
        print("没有找到团队ID，使用硬编码ID")
        team_id = "b3ba75b397716408e24fccbeb54ca2c6"
    
    # 4. 获取团队项目
    projects = get_team_projects(access_token, team_id)
    
    if projects:
        with open('tower_team_projects.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"团队项目列表已保存到 tower_team_projects.json")
        
        # 显示项目信息
        try:
            if 'data' in projects and len(projects['data']) > 0:
                print("\n找到的项目:")
                for idx, project in enumerate(projects['data']):
                    project_id = project.get('id')
                    project_name = project.get('attributes', {}).get('name', 'Unknown')
                    print(f"  {idx+1}. ID: {project_id}, 名称: {project_name}")
            else:
                print("\n没有找到项目")
        except Exception as e:
            print(f"处理项目信息出错: {str(e)}")
    
    print("\nAPI测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())