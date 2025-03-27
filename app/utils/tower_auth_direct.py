"""
Tower API 直接认证工具
用于直接保存获取到的访问令牌
"""

import sys
import json
from app.utils.tower_api import save_token

def save_tokens_directly(access_token, refresh_token, expires_in):
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
    
    print("访问令牌保存成功!")
    print(f"访问令牌: {access_token[:10]}...")
    print(f"刷新令牌: {refresh_token[:10]}...")
    print(f"有效期: {expires_in}秒")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("使用方法: python -m app.utils.tower_auth_direct <access_token> <refresh_token> <expires_in>")
        sys.exit(1)
    
    access_token = sys.argv[1]
    refresh_token = sys.argv[2]
    expires_in = sys.argv[3]
    
    if save_tokens_directly(access_token, refresh_token, expires_in):
        sys.exit(0)
    else:
        sys.exit(1)