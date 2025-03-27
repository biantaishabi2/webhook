#!/usr/bin/env python
"""
测试Tower API任务更新功能
"""

import sys
import json
import os
import argparse
from app.utils.tower_api import get_access_token, get_todo_details, update_todo_desc

def main():
    """测试Tower API任务更新功能"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试Tower API任务更新功能')
    parser.add_argument('--todo-guid', type=str, help='要更新的Tower任务GUID')
    parser.add_argument('--desc', type=str, help='新的任务描述 (HTML格式)')
    args = parser.parse_args()
    
    print("测试Tower API任务更新...")
    
    # 1. 获取访问令牌
    access_token = get_access_token()
    if not access_token:
        print("没有可用的访问令牌，请按照指示获取授权码并配置")
        return 1
    
    print(f"成功获取访问令牌: {access_token[:10]}...")
    
    # 2. 获取任务ID
    todo_guid = args.todo_guid
    if not todo_guid:
        # 尝试从最近的webhook日志中获取任务ID
        try:
            log_dir = '/tmp/tower_webhook_logs'
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.startswith('tower_')]
                if log_files:
                    latest_log = sorted(log_files)[-1]
                    with open(os.path.join(log_dir, latest_log), 'r') as f:
                        content = f.read()
                        if '"guid"' in content and '"todo"' in content:
                            import re
                            match = re.search(r'"todo".*?"guid".*?"([a-f0-9]+)"', content)
                            if match:
                                todo_guid = match.group(1)
                                print(f"从日志中提取的任务GUID: {todo_guid}")
        except Exception as e:
            print(f"获取测试任务ID失败: {str(e)}")
    
    if not todo_guid:
        print("没有提供任务GUID，请使用--todo-guid参数指定")
        return 1
    
    # 3. 先获取任务当前详情
    print(f"\n获取任务 {todo_guid} 的当前详细信息...")
    todo_details = get_todo_details(todo_guid)
    
    if not todo_details:
        print("无法获取任务详情，API调用失败")
        return 1
    
    # 保存当前详情
    current_details_file = 'tower_todo_before_update.json'
    with open(current_details_file, 'w') as f:
        json.dump(todo_details, f, indent=2)
    print(f"当前任务详情已保存到: {current_details_file}")
    
    # 从JSON:API格式中提取当前描述
    current_desc = "无描述"
    try:
        if 'data' in todo_details and 'attributes' in todo_details['data']:
            current_desc = todo_details['data']['attributes'].get('desc', '无描述')
    except Exception as e:
        print(f"提取当前描述失败: {str(e)}")
    
    print(f"\n当前任务描述: {current_desc}")
    
    # 4. 更新任务描述
    new_desc = args.desc
    if not new_desc:
        print("没有提供新描述，使用测试描述")
        new_desc = f"<p>API测试更新 - {os.path.basename(__file__)} - {os.getpid()}</p>"
    
    print(f"\n更新任务描述为: {new_desc}")
    updated_todo = update_todo_desc(todo_guid, new_desc)
    
    if updated_todo:
        print("\n成功更新任务描述!")
        # 保存到文件
        output_file = 'tower_todo_after_update.json'
        with open(output_file, 'w') as f:
            json.dump(updated_todo, f, indent=2)
        print(f"更新后的任务详情已保存到: {output_file}")
        
        # 检查更新是否成功
        updated_desc = "无法获取"
        try:
            if 'data' in updated_todo and 'attributes' in updated_todo['data']:
                updated_desc = updated_todo['data']['attributes'].get('desc', '无描述')
        except Exception as e:
            print(f"提取更新后描述失败: {str(e)}")
        
        print(f"\n更新后的任务描述: {updated_desc}")
        
        if updated_desc == new_desc:
            print("\n描述更新成功验证!")
        else:
            print("\n警告: 更新后的描述与请求的描述不匹配")
    else:
        print("更新任务描述失败，API调用失败")
        return 1
    
    print("\nTower API更新测试完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())