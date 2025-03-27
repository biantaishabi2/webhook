#!/usr/bin/env python
"""
测试Tower API的文件上传功能 - 按照API文档
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

# 上传文件附件并获取guid
def upload_attachment(access_token, file_path):
    """上传文件作为附件并获取guid"""
    url = "https://tower.im/api/v1/attachments"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    print(f"上传附件: {file_name}, 大小: {file_size} 字节")
    
    # 准备文件数据
    with open(file_path, 'rb') as file_obj:
        files = {
            'file': (file_name, file_obj)
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            print(f"上传附件到 {url}...")
            response = requests.post(url, headers=headers, files=files)
            print(f"上传状态码: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                print("附件上传成功!")
                try:
                    result = response.json()
                    print(f"响应内容前100个字符: {str(result)[:100]}...")
                    
                    # 尝试提取附件guid
                    if 'guid' in result:
                        return result['guid']
                    elif 'data' in result and 'id' in result['data']:
                        return result['data']['id']
                    else:
                        print("无法从响应中找到附件guid")
                        return None
                except json.JSONDecodeError:
                    print(f"响应不是有效的JSON: {response.text[:200]}...")
            else:
                print(f"上传响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"上传附件出错: {str(e)}")
    
    return None

# 创建上传（使用附件guid）
def create_upload(access_token, project_id, attachment_guid, name=None):
    """创建上传记录"""
    url = f"https://tower.im/api/v1/projects/{project_id}/uploads"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "attachment_guid": attachment_guid,
        "name": name if name else f"测试文件 {time.strftime('%Y-%m-%d %H:%M')}"
    }
    
    try:
        print(f"\n创建上传记录 {url}...")
        print(f"请求数据: {data}")
        response = requests.post(url, headers=headers, json=data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print("成功创建上传记录!")
            result = response.json()
            print(f"响应内容前100个字符: {str(result)[:100]}...")
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 获取文件详情
def get_upload(access_token, upload_id):
    """获取上传文件详情"""
    url = f"https://tower.im/api/v1/uploads/{upload_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n获取上传 {upload_id} 详情...")
        print(f"请求: {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功获取上传详情!")
            result = response.json()
            return result
        else:
            print(f"API响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    return None

# 删除文件
def delete_upload(access_token, upload_id):
    """删除上传文件"""
    url = f"https://tower.im/api/v1/uploads/{upload_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n删除上传 {upload_id}...")
        print(f"请求: {url}")
        response = requests.delete(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 202, 204]:
            print("成功删除上传!")
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
    
    # 3. 获取项目ID
    project_id = get_project_id()
    print(f"使用项目ID: {project_id}")
    
    # 4. 创建测试文件
    test_file_path = create_test_file(f"这是一个测试文件，创建于 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 5. 上传附件并获取guid
    attachment_guid = upload_attachment(access_token, test_file_path)
    
    if attachment_guid:
        print(f"获取到附件GUID: {attachment_guid}")
        
        # 6. 创建上传记录
        upload_result = create_upload(access_token, project_id, attachment_guid)
        
        if upload_result:
            # 保存上传结果
            with open('tower_upload_result.json', 'w', encoding='utf-8') as f:
                json.dump(upload_result, f, indent=2, ensure_ascii=False)
            print(f"上传结果已保存到 tower_upload_result.json")
            
            # 获取上传的文件ID
            try:
                upload_id = upload_result.get('data', {}).get('id')
                print(f"上传的文件ID: {upload_id}")
                
                if upload_id:
                    # 7. 获取上传详情
                    upload_details = get_upload(access_token, upload_id)
                    
                    if upload_details:
                        with open('tower_upload_details.json', 'w', encoding='utf-8') as f:
                            json.dump(upload_details, f, indent=2, ensure_ascii=False)
                        print(f"上传详情已保存到 tower_upload_details.json")
                    
                    # 8. 删除上传
                    print("等待2秒后删除上传...")
                    time.sleep(2)
                    
                    if delete_upload(access_token, upload_id):
                        print("上传已成功删除")
                    else:
                        print("上传删除失败")
                else:
                    print("无法从上传响应中提取ID")
            except Exception as e:
                print(f"处理上传信息时出错: {str(e)}")
    
    # 9. 清理测试文件
    try:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"已删除本地测试文件 {test_file_path}")
    except Exception as e:
        print(f"删除本地测试文件时出错: {str(e)}")
    
    print("\n文件上传API测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())