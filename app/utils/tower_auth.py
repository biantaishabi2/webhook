"""
Tower API 认证工具
用于获取Tower API访问令牌
"""

import sys
import requests
import json
from app.utils.tower_api import CLIENT_ID, CLIENT_SECRET, save_token

def get_token_from_code(authorization_code):
    """使用授权码获取访问令牌"""
    url = "https://tower.im/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": authorization_code,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        # 保存令牌数据
        save_token(token_data)
        
        print("访问令牌获取成功!")
        print(f"访问令牌: {token_data['access_token']}")
        print(f"刷新令牌: {token_data['refresh_token']}")
        print(f"有效期: {token_data['expires_in']}秒")
        
        return token_data
    except Exception as e:
        print(f"获取访问令牌失败: {str(e)}")
        if hasattr(response, 'text'):
            print(f"错误响应: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python -m app.utils.tower_auth <授权码>")
        sys.exit(1)
    
    authorization_code = sys.argv[1]
    get_token_from_code(authorization_code)