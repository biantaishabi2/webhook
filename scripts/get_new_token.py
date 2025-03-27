#!/usr/bin/env python
"""
使用授权码获取Tower访问令牌
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Tower应用凭据
CLIENT_ID = "0d7e96f946d17a4a86ff03619b3f5687ce4c2194253533142025cc9b2a0f842c"
CLIENT_SECRET = "33e6f7cc01029fbe427fc5d4b293bf8ed1d44fbb2c10b5734670eb7482cdc37d"

# 授权码 - 从命令行参数获取
AUTH_CODE = "731fbad793a69a78c27c7242829b3a0acc2ddb4ed79c1f3ec58e868e3f35fac2"

# Token文件路径
TOKEN_FILE = "tower_token.json"

def get_token_with_auth_code(auth_code):
    """使用授权码获取访问令牌"""
    url = "https://tower.im/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
    }
    
    print("请求访问令牌...")
    response = requests.post(url, data=payload)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"成功获取令牌：{token_data.get('access_token')[:10]}...")
        
        # 添加过期时间
        expires_in = token_data.get('expires_in', 7200)
        token_data['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        
        # 保存到文件
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"令牌已保存到文件: {TOKEN_FILE}")
        return token_data
    else:
        print(f"获取令牌失败: {response.text}")
        return None

if __name__ == "__main__":
    token_data = get_token_with_auth_code(AUTH_CODE)
    if token_data:
        print("\n令牌信息:")
        print(f"访问令牌: {token_data.get('access_token')[:10]}...")
        print(f"刷新令牌: {token_data.get('refresh_token', 'N/A')[:10] if token_data.get('refresh_token') else 'N/A'}...")
        print(f"令牌类型: {token_data.get('token_type', 'N/A')}")
        print(f"过期时间: {token_data.get('expires_in', 'N/A')} 秒")
        print(f"创建时间: {token_data.get('created_at', 'N/A')}")