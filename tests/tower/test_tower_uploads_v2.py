#!/usr/bin/env python
"""
测试Tower API的文件上传、获取和删除功能（尝试团队特定版本）
"""

import json
import requests
import sys
import os
import time

# 从文件加载令牌
def load_token():
    try:
        with open('tower_token.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载令牌出错: {str(e)}")
        return None

# 获取团队ID
def get_team_id():
    try:
        with open('tower_teams.json', 'r') as f:
            teams_data = json.load(f)
            if 'data' in teams_data and len(teams_data['data']) > 0:
                return teams_data['data'][0]['id']
    except Exception as e:
        print(f"读取团队信息出错: {str(e)}")
    
    # 如果读取失败，使用硬编码的团队ID
    return "b3ba75b397716408e24fccbeb54ca2c6"

# 获取项目ID
def get_project_id():
    try:
        with open('tower_team_projects.json', 'r') as f:
            projects_data = json.load(f)
            if 'data' in projects_data and len(projects_data['data']) > 0:
                return projects_data['data'][0]['id']
    except Exception as e:
        print(f"读取项目信息出错: {str(e)}")
    
    # 如果读取失败，使用硬编码的项目ID
    return "5dc713a15ab57a0bcefcc2969729b6c4"

# 上传文件（尝试不同的路径）
def upload_file(access_token, file_path, team_id, project_id):
    """尝试多种路径上传文件到Tower"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    print(f"要上传的文件: {file_name}, 大小: {file_size} 字节")
    
    # 尝试不同的上传路径
    upload_paths = [
        # 基本路径
        "https://tower.im/api/v1/uploads",
        # 团队特定路径
        f"https://tower.im/api/v1/teams/{team_id}/uploads",
        # 项目特定路径
        f"https://tower.im/api/v1/projects/{project_id}/uploads",
        # 团队+项目路径
        f"https://tower.im/api/v1/teams/{team_id}/projects/{project_id}/uploads",
        # 尝试v2 API
        "https://tower.im/api/v2/uploads",
        # 尝试不同的参数格式
        "https://tower.im/api/v1/attachments"
    ]
    
    for url in upload_paths:
        # 准备文件数据
        with open(file_path, 'rb') as file_obj:
            files = {
                'file': (file_name, file_obj, 'text/plain')
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            # 可选的表单数据
            data = {
                'name': file_name,
                'desc': '通过API上传的测试文件'
            }
            
            try:
                print(f"\n尝试上传文件到 {url}...")
                response = requests.post(url, headers=headers, files=files, data=data)
                print(f"上传状态码: {response.status_code}")
                
                if response.status_code in [200, 201, 202]:
                    print("文件上传成功!")
                    try:
                        result = response.json()
                        print(f"响应内容前100个字符: {str(result)[:100]}...")
                        return result
                    except json.JSONDecodeError:
                        print(f"响应不是有效的JSON: {response.text[:200]}...")
                else:
                    print(f"上传响应内容: {response.text[:200]}...")
            except Exception as e:
                print(f"上传出错: {str(e)}")
    
    return None

# 获取文件详情
def get_file(access_token, file_id):
    """获取文件详情"""
    url = f"https://tower.im/api/v1/uploads/{file_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n获取文件 {file_id} 详情...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取文件详情!")
            result = response.json()
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 删除文件
def delete_file(access_token, file_id):
    """删除文件"""
    url = f"https://tower.im/api/v1/uploads/{file_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n删除文件 {file_id}...")
        print(f"请求: {url}")
        response = requests.delete(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 202, 204]:
            print("成功删除文件!")
            return True
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return False

# 创建测试文件
def create_test_file(content="这是一个测试文件内容"):
    """创建一个测试文本文件"""
    file_path = "tower_test_file.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"创建测试文件: {file_path}")
    return file_path

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
    
    # 3. 获取团队和项目ID
    team_id = get_team_id()
    project_id = get_project_id()
    print(f"使用团队ID: {team_id}")
    print(f"使用项目ID: {project_id}")
    
    # 4. 创建测试文件
    test_file_path = create_test_file(f"这是一个测试文件，创建于 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 5. 上传文件
    upload_result = upload_file(access_token, test_file_path, team_id, project_id)
    
    if upload_result:
        # 保存上传结果
        with open('tower_upload_result.json', 'w', encoding='utf-8') as f:
            json.dump(upload_result, f, indent=2, ensure_ascii=False)
        print(f"上传结果已保存到 tower_upload_result.json")
        
        # 获取上传的文件ID
        try:
            file_id = upload_result.get('data', {}).get('id')
            print(f"上传的文件ID: {file_id}")
            
            if file_id:
                # 6. 获取文件详情
                file_details = get_file(access_token, file_id)
                
                if file_details:
                    with open('tower_file_details.json', 'w', encoding='utf-8') as f:
                        json.dump(file_details, f, indent=2, ensure_ascii=False)
                    print(f"文件详情已保存到 tower_file_details.json")
                
                # 7. 删除文件
                print("等待2秒后删除文件...")
                time.sleep(2)  # 稍微等待一下，确保文件已完全处理
                
                if delete_file(access_token, file_id):
                    print("文件已成功删除")
                else:
                    print("文件删除失败")
            else:
                print("无法从上传响应中提取文件ID")
        except Exception as e:
            print(f"处理文件信息时出错: {str(e)}")
    
    # 8. 清理测试文件
    try:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"已删除本地测试文件 {test_file_path}")
    except Exception as e:
        print(f"删除本地测试文件时出错: {str(e)}")
    
    print("\n文件API测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())