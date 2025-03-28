#!/usr/bin/env python
"""
测试Tower令牌的有效性
"""

import requests
import json
import sys
import os
from datetime import datetime

def get_token_from_file():
    """从配置文件读取Tower访问令牌"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "tower_token.json")
        print(f"正在从配置文件读取令牌: {config_path}")
        
        with open(config_path, 'r') as f:
            token_data = json.load(f)
            
        # 检查令牌是否过期
        if 'expires_at' in token_data:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                print("警告: 令牌已过期!")
            else:
                print("令牌仍在有效期内")
                
        print("\n成功读取令牌!")
        print(f"访问令牌: {token_data.get('access_token', 'N/A')}")
        print(f"刷新令牌: {token_data.get('refresh_token', 'N/A')}")
        print(f"有效期至: {token_data.get('expires_at', 'N/A')}")
        
        return token_data
    except Exception as e:
        print(f"读取令牌文件时发生错误: {str(e)}")
        return None

if __name__ == "__main__":
    token_data = get_token_from_file()
    if token_data:
        print("\n开始测试令牌...")
        access_token = token_data.get('access_token')
        
        # 尝试获取当前用户信息作为测试
        try:
            # 尝试API v1的多个端点
            api_endpoints = [
                "https://tower.im/api/v1/user",                # 用户信息
                "https://tower.im/api/v1/teams",               # 团队列表
                "https://tower.im/api/v1/teams/b3ba75b397716408e24fccbeb54ca2c6/projects"  # 特定团队的项目列表
            ]
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.api+json"
            }
            
            # 尝试所有端点
            success = False
            results = []
            for i, endpoint in enumerate(api_endpoints):
                print(f"\n尝试API端点 #{i+1}: {endpoint}")
                result = {
                    "endpoint": endpoint,
                    "success": False,
                    "status_code": None,
                    "response": None,
                    "error": None
                }
                
                try:
                    response = requests.get(endpoint, headers=headers)
                    result["status_code"] = response.status_code
                    
                    if response.status_code == 200:
                        result["success"] = True
                        result["response"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                        print(f"✅ 成功访问API!")
                        success = True
                    else:
                        result["response"] = response.text
                        print(f"❌ 访问失败 (状态码: {response.status_code})")
                        # 尝试解析错误响应
                        try:
                            error_json = response.json()
                            print(f"  错误详情: {json.dumps(error_json, ensure_ascii=False, indent=2)}")
                        except:
                            print(f"  原始响应: {response.text[:200]}..." if len(response.text) > 200 else f"  原始响应: {response.text}")
                except Exception as e:
                    result["error"] = str(e)
                    print(f"❌ 请求出错: {str(e)}")
                
                results.append(result)
            
            # 输出总结报告
            print("\n=== 测试结果总结 ===")
            print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Token状态: {'有效' if success else '无效'}")
            print(f"测试端点总数: {len(api_endpoints)}")
            print(f"成功端点数: {sum(1 for r in results if r['success'])}")
            print(f"失败端点数: {sum(1 for r in results if not r['success'])}")
            
            print("\n详细结果:")
            for result in results:
                endpoint_name = result["endpoint"].split("/")[-1]
                status = "✅ 成功" if result["success"] else "❌ 失败"
                print(f"\n{status} - {endpoint_name}")
                print(f"  状态码: {result['status_code']}")
                if result["error"]:
                    print(f"  错误: {result['error']}")
                elif result["response"]:
                    print(f"  响应: {result['response'][:100]}..." if len(result['response']) > 100 else f"  响应: {result['response']}")
            
            if not success:
                print("\n❌ 总结: 所有API端点测试均失败，Token可能无效或权限不足")
            else:
                print("\n✅ 总结: 至少有一个API端点测试成功，Token有效")
            
        except Exception as e:
            print(f"\n❌ 测试过程发生错误: {str(e)}")
        
        sys.exit(0 if success else 1)
    else:
        print("\n❌ 无法读取或解析Token文件")
        sys.exit(1)