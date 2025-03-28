"""
Tower测试工具函数
"""

import json
import os
from datetime import datetime, timedelta

def get_token_path():
    """获取标准的token文件路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "tower_token.json")

def load_tower_token():
    """从标准位置加载Tower令牌"""
    try:
        # 使用正确的配置路径
        config_path = get_token_path()
        print(f"尝试从 {config_path} 加载令牌")
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"从标准路径加载令牌出错: {str(e)}")
        
        # 尝试备用路径
        try:
            with open('tower_token.json', 'r') as f:
                token_data = json.load(f)
                print("从当前目录成功加载令牌")
                
                # 如果没有expires_at字段，添加它
                if 'expires_at' not in token_data and 'expires_in' in token_data:
                    expires_in = token_data.get('expires_in', 7200)
                    token_data['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
                    
                    # 同时保存到标准位置
                    try:
                        os.makedirs(os.path.dirname(config_path), exist_ok=True)
                        with open(config_path, 'w') as cf:
                            json.dump(token_data, cf, indent=2)
                        print(f"已将令牌同步保存到标准位置: {config_path}")
                    except Exception as save_e:
                        print(f"保存令牌到标准位置失败: {str(save_e)}")
                
                return token_data
        except Exception as backup_e:
            print(f"从备用路径加载令牌也失败: {str(backup_e)}")
            
        return None