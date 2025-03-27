#!/usr/bin/env python
"""
获取Tower API访问令牌的独立工具
支持多种授权方式
"""

import sys
import requests
import json
import os
from datetime import datetime, timedelta

# Tower应用凭据 - 从环境变量获取
CLIENT_ID = os.environ.get("TOWER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TOWER_CLIENT_SECRET", "")

# 令牌存储文件
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "tower_token.json")

def get_token_client_credentials():
    """使用客户端凭据方式获取访问令牌"""
    url = "https://tower.im/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        # 保存令牌数据
        save_token(token_data)
        
        print("访问令牌获取成功!")
        print(f"访问令牌: {token_data['access_token'][:10]}...")
        if 'refresh_token' in token_data:
            print(f"刷新令牌: {token_data['refresh_token'][:10]}...")
        print(f"有效期: {token_data['expires_in']}秒")
        
        return token_data
    except Exception as e:
        print(f"获取访问令牌失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"错误响应: {response.text}")
        return None

def get_token_password_grant(username, password):
    """使用密码授权方式获取访问令牌"""
    url = "https://tower.im/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        # 保存令牌数据
        save_token(token_data)
        
        print("访问令牌获取成功!")
        print(f"访问令牌: {token_data['access_token'][:10]}...")
        if 'refresh_token' in token_data:
            print(f"刷新令牌: {token_data['refresh_token'][:10]}...")
        print(f"有效期: {token_data['expires_in']}秒")
        
        return token_data
    except Exception as e:
        print(f"获取访问令牌失败: {str(e)}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"错误响应: {response.text}")
        return None

def save_token(token_data):
    """保存令牌数据到文件"""
    # 添加过期时间
    expires_in = token_data.get('expires_in', 7200)
    token_data['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    
    # 保存到文件
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"Tower访问令牌已保存到 {TOKEN_FILE}")

def show_usage():
    """显示使用帮助"""
    print("""
获取Tower API访问令牌工具

使用方法:
1. 客户端凭据方式 (适用于服务器间通信):
   python get_tower_token.py client

2. 密码授权方式 (适用于用户授权):
   python get_tower_token.py password <username> <password>

3. 直接设置令牌 (如果已经获取到令牌):
   python get_tower_token.py direct <access_token> <refresh_token> <expires_in>
""")

def save_direct_token(access_token, refresh_token, expires_in):
    """直接保存提供的访问令牌信息"""
    try:
        expires_in = int(expires_in)
    except ValueError:
        print(f"无效的过期时间: {expires_in}，使用默认值7200")
        expires_in = 7200
        
    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
        "token_type": "bearer"
    }
    
    # 保存令牌数据
    save_token(token_data)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    auth_type = sys.argv[1].lower()
    
    if auth_type == "client":
        # 客户端凭据方式
        if get_token_client_credentials():
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif auth_type == "password":
        # 密码授权方式
        if len(sys.argv) != 4:
            print("错误: 密码授权方式需要提供用户名和密码")
            show_usage()
            sys.exit(1)
            
        username = sys.argv[2]
        password = sys.argv[3]
        
        if get_token_password_grant(username, password):
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif auth_type == "direct":
        # 直接设置令牌
        if len(sys.argv) != 5:
            print("错误: 直接设置令牌需要提供access_token, refresh_token和expires_in")
            show_usage()
            sys.exit(1)
            
        access_token = sys.argv[2]
        refresh_token = sys.argv[3]
        expires_in = sys.argv[4]
        
        if save_direct_token(access_token, refresh_token, expires_in):
            sys.exit(0)
        else:
            sys.exit(1)
    
    else:
        print(f"错误: 未知的授权类型 '{auth_type}'")
        show_usage()
        sys.exit(1)