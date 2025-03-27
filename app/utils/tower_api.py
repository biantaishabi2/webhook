"""
Tower API 工具模块
用于与Tower API交互，获取任务、项目等详细信息
"""

import requests
import os
import json
from datetime import datetime, timedelta
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Tower应用凭据 - 从环境变量获取
CLIENT_ID = os.environ.get("TOWER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TOWER_CLIENT_SECRET", "")

# 访问令牌存储
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "tower_token.json")

def get_access_token():
    """
    获取Tower API访问令牌，如果存在有效令牌则使用，否则引导用户获取新令牌
    """
    # 检查是否有存储的令牌
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                
            # 检查令牌是否过期
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if expires_at > datetime.now():
                logger.info("使用缓存的Tower访问令牌")
                return token_data['access_token']
        except Exception as e:
            logger.error(f"读取令牌文件出错: {str(e)}")
    
    # 没有有效令牌，提示用户获取
    logger.warning("没有有效的Tower访问令牌")
    print("""
请按照以下步骤获取Tower访问令牌:

1. 设置环境变量:
   export TOWER_CLIENT_ID="您的客户端ID"
   export TOWER_CLIENT_SECRET="您的客户端密钥"

2. 使用内置脚本获取令牌:
   python scripts/get_tower_token.py client
   
   # 或使用密码授权流程:
   python scripts/get_tower_token.py password <username> <password>

3. 也可以直接使用curl (替换变量):
   curl -X POST https://tower.im/oauth/token \\
     -d "client_id=$TOWER_CLIENT_ID" \\
     -d "client_secret=$TOWER_CLIENT_SECRET" \\
     -d "grant_type=password" \\
     -d "username=您的Tower用户名" \\
     -d "password=您的Tower密码"
""")
    return None

def save_token(token_data):
    """保存令牌数据到文件"""
    # 添加过期时间
    expires_in = token_data.get('expires_in', 7200)
    token_data['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    
    # 保存到文件
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    logger.info("Tower访问令牌已保存")

def get_todo_details(todo_guid):
    """
    获取Tower任务的详细信息
    
    Args:
        todo_guid: 任务的GUID
        
    Returns:
        dict: 任务详情，如果获取失败则返回None
    """
    access_token = get_access_token()
    if not access_token:
        logger.error("没有有效的访问令牌，无法获取任务详情")
        return None
    
    # 根据文档，Tower API使用v1版本
    url = f"https://tower.im/api/v1/todos/{todo_guid}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"请求Tower API: {url}")
        response = requests.get(url, headers=headers)
        logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            logger.warning(f"API响应内容: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'status_code') and response.status_code == 401:
            logger.warning("访问令牌可能已过期，请重新获取")
            # 删除过期的令牌文件
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
        return None

def get_todo_comments(todo_guid):
    """获取任务的评论"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    # 同样使用v1版本API
    url = f"https://tower.im/api/v1/todos/{todo_guid}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"请求Tower评论API: {url}")
        response = requests.get(url, headers=headers)
        logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            logger.warning(f"评论API响应内容: {response.text}")
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"获取任务评论失败: {str(e)}")
        return None

def update_todo_desc(todo_guid, new_desc):
    """
    更新Tower任务的描述
    
    Args:
        todo_guid: 任务的GUID
        new_desc: 新的任务描述，HTML格式
        
    Returns:
        dict: 更新后的任务详情，如果更新失败则返回None
    """
    access_token = get_access_token()
    if not access_token:
        logger.error("没有有效的访问令牌，无法更新任务描述")
        return None
    
    # 直接使用主任务API而不是特定的desc端点
    url = f"https://tower.im/api/v1/todos/{todo_guid}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    }
    
    # 尝试简单的表单数据方式
    payload = {
        "desc": new_desc
    }
    
    try:
        logger.info(f"请求Tower更新API: {url}")
        logger.info(f"更新内容: {new_desc}")
        
        # 先尝试非JSON:API格式，使用PUT方法而不是PATCH
        response = requests.put(url, headers=headers, json=payload)
        logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            logger.warning(f"API响应内容: {response.text}")
            
            # 如果第一种方法失败，尝试使用JSON:API格式
            headers["Content-Type"] = "application/vnd.api+json"
            jsonapi_payload = {
                "data": {
                    "type": "todos",
                    "id": todo_guid,
                    "attributes": {
                        "desc": new_desc
                    }
                }
            }
            
            logger.info("尝试JSON:API格式...")
            response = requests.patch(url, headers=headers, json=jsonapi_payload)
            logger.info(f"第二次尝试 API响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"第二次尝试 API响应内容: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"更新任务描述失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'status_code'):
            logger.error(f"HTTP错误代码: {response.status_code}")
            logger.error(f"响应内容: {response.text if hasattr(response, 'text') else '无内容'}")
        return None

def assign_todo(todo_guid, member_guid):
    """
    指派任务负责人
    
    Args:
        todo_guid: 任务的GUID
        member_guid: 成员的GUID
        
    Returns:
        dict: 更新后的任务详情，如果更新失败则返回None
    """
    access_token = get_access_token()
    if not access_token:
        logger.error("没有有效的访问令牌，无法指派任务")
        return None
    
    # 根据文档使用专用API
    url = f"https://tower.im/api/v1/todos/{todo_guid}/assignment"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/json"
    }
    
    # 使用文档中的格式
    payload = {
        "todos_assignment": {
            "assignee_id": member_guid
        }
    }
    
    try:
        logger.info(f"请求Tower任务指派专用API: {url}")
        logger.info(f"指派给成员: {member_guid}")
        
        # 使用PATCH方法更新任务
        response = requests.patch(url, headers=headers, json=payload)
        logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("成功指派任务")
            return response.json()
        else:
            # 记录错误响应
            logger.warning(f"API响应内容: {response.text}")
            
            # 尝试使用普通更新API
            general_url = f"https://tower.im/api/v1/todos/{todo_guid}"
            general_payload = {
                "assignee_guid": member_guid
            }
            
            logger.info(f"尝试普通更新API: {general_url}")
            update_response = requests.put(general_url, headers=headers, json=general_payload)
            logger.info(f"第二次尝试 API响应状态码: {update_response.status_code}")
            
            if update_response.status_code == 200:
                logger.info("使用普通更新API成功指派任务")
                return update_response.json()
            else:
                logger.warning(f"第二次尝试 API响应内容: {update_response.text}")
                
                # 尝试使用JSON:API格式
                headers["Content-Type"] = "application/vnd.api+json"
                jsonapi_payload = {
                    "data": {
                        "type": "todos",
                        "id": todo_guid,
                        "relationships": {
                            "assignee": {
                                "data": {
                                    "id": member_guid,
                                    "type": "members"
                                }
                            }
                        }
                    }
                }
                
                logger.info("尝试JSON:API格式...")
                patch_response = requests.patch(general_url, headers=headers, json=jsonapi_payload)
                logger.info(f"第三次尝试 API响应状态码: {patch_response.status_code}")
                
                if patch_response.status_code == 200:
                    logger.info("使用JSON:API格式成功指派任务")
                    return patch_response.json()
                else:
                    logger.warning(f"第三次尝试 API响应内容: {patch_response.text}")
                
        return None
    except Exception as e:
        logger.error(f"指派任务失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'status_code'):
            logger.error(f"HTTP错误代码: {response.status_code}")
            logger.error(f"响应内容: {response.text if hasattr(response, 'text') else '无内容'}")
        return None

def complete_todo(todo_guid, completed=True):
    """
    完成或重新打开任务
    
    Args:
        todo_guid: 任务的GUID
        completed: 是否完成，True表示完成，False表示重新打开
        
    Returns:
        dict: 更新后的任务详情，如果更新失败则返回None
    """
    access_token = get_access_token()
    if not access_token:
        logger.error("没有有效的访问令牌，无法更新任务状态")
        return None
    
    # 根据当前任务状态决定操作
    current_todo = get_todo_details(todo_guid)
    if not current_todo:
        logger.error("无法获取当前任务状态，操作中止")
        return None
    
    # 检查当前状态
    current_completed = False
    if 'data' in current_todo and 'attributes' in current_todo['data']:
        current_completed = current_todo['data']['attributes'].get('is_completed', False)
    
    # 如果当前状态与目标状态相同，直接返回
    if current_completed == completed:
        logger.info(f"任务已经处于{'完成' if completed else '未完成'}状态，无需更改")
        return current_todo
    
    status_text = "完成" if completed else "重新打开"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.api+json"
    }
    
    try:
        # 根据操作选择API端点
        if completed:
            # 完成任务使用completion端点
            url = f"https://tower.im/api/v1/todos/{todo_guid}/completion"
            logger.info(f"请求Tower任务完成API (POST): {url}")
            response = requests.post(url, headers=headers)
        else:
            # 重新打开任务使用普通更新API
            url = f"https://tower.im/api/v1/todos/{todo_guid}"
            update_payload = {
                "is_completed": False
            }
            logger.info(f"请求Tower任务重新打开API (PUT): {url}")
            response = requests.put(url, headers=headers, json=update_payload)
        
        logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"成功{status_text}任务")
            return response.json()
        else:
            # 记录错误响应
            logger.warning(f"API响应内容: {response.text}")
            
            # 尝试使用JSON:API格式
            logger.info("尝试JSON:API格式...")
            headers["Content-Type"] = "application/vnd.api+json"
            general_url = f"https://tower.im/api/v1/todos/{todo_guid}"
            jsonapi_payload = {
                "data": {
                    "type": "todos",
                    "id": todo_guid,
                    "attributes": {
                        "is_completed": completed
                    }
                }
            }
            
            patch_response = requests.patch(general_url, headers=headers, json=jsonapi_payload)
            logger.info(f"第二次尝试 API响应状态码: {patch_response.status_code}")
            
            if patch_response.status_code == 200:
                logger.info(f"使用JSON:API格式成功{status_text}任务")
                return patch_response.json()
            else:
                logger.warning(f"第二次尝试 API响应内容: {patch_response.text}")
                
                # 尝试使用其他已知端点
                if not completed:
                    # 尝试重新打开任务的特殊URL
                    reopen_url = f"https://tower.im/api/v1/todos/{todo_guid}/reopen"
                    logger.info(f"尝试使用重新打开专用API: {reopen_url}")
                    reopen_response = requests.post(reopen_url, headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.api+json"
                    })
                    logger.info(f"第三次尝试 API响应状态码: {reopen_response.status_code}")
                    
                    if reopen_response.status_code in [200, 201, 204]:
                        logger.info(f"使用专用API成功重新打开任务")
                        # 如果成功但没有返回内容，获取最新任务详情
                        if reopen_response.status_code == 204 or not reopen_response.text:
                            return get_todo_details(todo_guid)
                        return reopen_response.json()
                    else:
                        logger.warning(f"第三次尝试 API响应内容: {reopen_response.text}")
                        
                        # 尝试DELETE方法
                        completion_url = f"https://tower.im/api/v1/todos/{todo_guid}/completion"
                        logger.info(f"尝试使用DELETE方法删除完成状态: {completion_url}")
                        del_response = requests.delete(completion_url, headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.api+json"
                        })
                        logger.info(f"第四次尝试 API响应状态码: {del_response.status_code}")
                        
                        if del_response.status_code in [200, 201, 204]:
                            logger.info(f"使用DELETE方法成功重新打开任务")
                            # 如果成功但没有返回内容，获取最新任务详情
                            if del_response.status_code == 204 or not del_response.text:
                                return get_todo_details(todo_guid)
                            return del_response.json()
                        else:
                            logger.warning(f"第四次尝试 API响应内容: {del_response.text}")
                
        # 获取最新状态
        updated_todo = get_todo_details(todo_guid)
        if updated_todo:
            # 检查最终状态
            final_completed = False
            if 'data' in updated_todo and 'attributes' in updated_todo['data']:
                final_completed = updated_todo['data']['attributes'].get('is_completed', False)
            
            if final_completed == completed:
                logger.info(f"操作成功，任务现在处于{'完成' if completed else '未完成'}状态")
                return updated_todo
            else:
                logger.warning(f"所有API尝试后，任务状态仍不符合期望")
        
        return None
    except Exception as e:
        logger.error(f"{status_text}任务失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'status_code'):
            logger.error(f"HTTP错误代码: {response.status_code}")
            logger.error(f"响应内容: {response.text if hasattr(response, 'text') else '无内容'}")
        return None

def create_todo_comment(todo_guid, comment_content):
    """
    为Tower任务添加评论
    
    Args:
        todo_guid: 任务的GUID
        comment_content: 评论内容，HTML格式
        
    Returns:
        dict: 创建的评论详情，如果创建失败则返回None
    """
    access_token = get_access_token()
    if not access_token:
        logger.error("没有有效的访问令牌，无法添加评论")
        return None
    
    url = f"https://tower.im/api/v1/todos/{todo_guid}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    }
    
    # 使用简单的表单数据方式
    payload = {
        "content": comment_content
    }
    
    try:
        logger.info(f"请求Tower评论创建API: {url}")
        logger.info(f"评论内容: {comment_content}")
        
        # Tower API接受简单的JSON格式
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"API响应状态码: {response.status_code}")
        
        # 如果返回成功的状态码（200或201）
        if response.status_code in [200, 201]:
            logger.info("成功创建评论")
            return response.json()
        else:
            # 记录错误响应
            logger.warning(f"API响应内容: {response.text}")
            
            # 如果第一种方法失败，尝试使用JSON:API格式
            headers["Content-Type"] = "application/vnd.api+json"
            jsonapi_payload = {
                "data": {
                    "type": "comments",
                    "attributes": {
                        "content": comment_content
                    }
                }
            }
            
            logger.info("尝试JSON:API格式...")
            response = requests.post(url, headers=headers, json=jsonapi_payload)
            logger.info(f"第二次尝试 API响应状态码: {response.status_code}")
            
            if response.status_code in [200, 201]:
                logger.info("使用JSON:API格式成功创建评论")
                return response.json()
            else:
                logger.warning(f"第二次尝试 API响应内容: {response.text}")
                response.raise_for_status()
                
        return None
    except Exception as e:
        logger.error(f"创建评论失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'status_code'):
            logger.error(f"HTTP错误代码: {response.status_code}")
            logger.error(f"响应内容: {response.text if hasattr(response, 'text') else '无内容'}")
        return None