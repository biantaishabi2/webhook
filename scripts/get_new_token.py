#!/usr/bin/env python
"""
使用授权码获取Tower访问令牌

用法:
    python get_new_token.py <授权码>

说明:
    此脚本通过授权码方式获取Tower API访问令牌，这是唯一稳定可靠的令牌获取方式。
    授权码可以通过Tower应用控制台获取。
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta

# 从环境变量获取Tower应用凭据
from dotenv import load_dotenv
load_dotenv()  # 加载.env文件中的环境变量

CLIENT_ID = os.environ.get("TOWER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("TOWER_CLIENT_SECRET", "")

# Token文件路径
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "tower_token.json")

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
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("错误: 请提供授权码")
        print("用法: python get_new_token.py <授权码>")
        print(f"\n授权地址: https://tower.im/oauth/authorize?client_id={CLIENT_ID}&response_type=code")
        sys.exit(1)
    
    # 从命令行获取授权码
    auth_code = sys.argv[1]
    
    # 验证环境变量
    if not CLIENT_ID or not CLIENT_SECRET:
        print("错误: 未设置TOWER_CLIENT_ID或TOWER_CLIENT_SECRET环境变量")
        print("请在.env文件中设置这些变量，或通过环境变量导出它们")
        print("export TOWER_CLIENT_ID=your_client_id")
        print("export TOWER_CLIENT_SECRET=your_client_secret")
        sys.exit(1)
    
    # 获取令牌
    token_data = get_token_with_auth_code(auth_code)
    if token_data:
        print("\n令牌信息:")
        print(f"访问令牌: {token_data.get('access_token')[:10]}...")
        print(f"刷新令牌: {token_data.get('refresh_token', 'N/A')[:10] if token_data.get('refresh_token') else 'N/A'}...")
        print(f"令牌类型: {token_data.get('token_type', 'N/A')}")
        print(f"过期时间: {token_data.get('expires_in', 'N/A')} 秒")
        print(f"创建时间: {token_data.get('created_at', 'N/A')}")
        sys.exit(0)
    else:
        print("获取令牌失败")
        sys.exit(1)