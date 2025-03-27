#!/usr/bin/env python
"""
直接测试获取Tower令牌
"""

import requests
import json
import sys

# Tower应用凭据
CLIENT_ID = "0d7e96f946d17a4a86ff03619b3f5687ce4c2194253533142025cc9b2a0f842c"
CLIENT_SECRET = "33e6f7cc01029fbe427fc5d4b293bf8ed1d44fbb2c10b5734670eb7482cdc37d"

def get_token():
    """直接获取Tower访问令牌"""
    url = "https://tower.im/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        print("正在向Tower请求访问令牌...")
        response = requests.post(url, data=payload)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("\n成功获取访问令牌!")
            print(f"访问令牌: {token_data.get('access_token', 'N/A')}")
            print(f"刷新令牌: {token_data.get('refresh_token', 'N/A')}")
            print(f"有效期: {token_data.get('expires_in', 'N/A')}秒")
            
            # 保存到文件以便后续使用
            with open('tower_token_test.json', 'w') as f:
                json.dump(token_data, f, indent=2)
            print(f"令牌已保存到 tower_token_test.json")
            
            return token_data
        else:
            print(f"获取令牌失败，状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None

if __name__ == "__main__":
    token_data = get_token()
    if token_data:
        print("\n接下来测试使用这个令牌...")
        access_token = token_data.get('access_token')
        
        # 尝试获取当前用户信息作为测试
        try:
            user_url = "https://tower.im/api/v2/members/me"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            print(f"\n使用令牌获取当前用户信息...")
            user_response = requests.get(user_url, headers=headers)
            print(f"状态码: {user_response.status_code}")
            print(f"响应内容: {user_response.text}")
        except Exception as e:
            print(f"测试令牌失败: {str(e)}")
        
        sys.exit(0)
    else:
        sys.exit(1)