#!/usr/bin/env python
"""
测试Tower API任务指派功能
"""

import sys
import json
import os
import argparse
from app.utils.tower_api import get_access_token, get_todo_details, assign_todo

def get_team_members():
    """获取团队成员列表，用于选择指派对象"""
    # 这里可以实现获取团队成员的API调用
    # 简化起见，这里暂时返回固定的成员信息
    return [
        {"id": "f91066231c2e352d46ecb35b5e8911c9", "nickname": "王博", "role": "owner"},
        # 可以添加更多成员
    ]

def main():
    """测试Tower API任务指派功能"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试Tower API任务指派功能')
    parser.add_argument('--todo-guid', type=str, help='要指派的Tower任务GUID')
    parser.add_argument('--member-guid', type=str, help='被指派成员的GUID')
    args = parser.parse_args()
    
    print("测试Tower API任务指派...")
    
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
    current_details_file = 'tower_todo_before_assign.json'
    with open(current_details_file, 'w') as f:
        json.dump(todo_details, f, indent=2)
    print(f"当前任务详情已保存到: {current_details_file}")
    
    # 获取任务标题和当前负责人
    task_title = "未知任务"
    current_assignee = "无"
    try:
        if 'data' in todo_details and 'attributes' in todo_details['data']:
            task_title = todo_details['data']['attributes'].get('content', '未知任务')
            
        if 'data' in todo_details and 'relationships' in todo_details['data']:
            assignee_data = todo_details['data']['relationships'].get('assignee', {}).get('data')
            if assignee_data:
                assignee_id = assignee_data.get('id', '')
                # 从included中查找成员名称
                if 'included' in todo_details:
                    for item in todo_details['included']:
                        if item.get('type') == 'members' and item.get('id') == assignee_id:
                            current_assignee = item.get('attributes', {}).get('nickname', '未知')
                            break
    except Exception as e:
        print(f"提取任务信息失败: {str(e)}")
    
    print(f"\n当前任务标题: {task_title}")
    print(f"当前负责人: {current_assignee}")
    
    # 4. 获取可指派的成员
    member_guid = args.member_guid
    if not member_guid:
        members = get_team_members()
        if members:
            print("\n可指派的团队成员:")
            for i, member in enumerate(members):
                print(f"{i+1}. {member['nickname']} (GUID: {member['id']})")
            
            # 使用第一个成员作为默认指派对象
            member_guid = members[0]['id']
            print(f"\n使用默认成员: {members[0]['nickname']} (GUID: {member_guid})")
        else:
            print("未能获取团队成员列表")
            return 1
    
    # 5. 指派任务
    print(f"\n开始指派任务 {todo_guid} 给成员 {member_guid}...")
    assign_result = assign_todo(todo_guid, member_guid)
    
    if assign_result:
        print("\n成功指派任务!")
        # 保存到文件
        output_file = 'tower_todo_after_assign.json'
        with open(output_file, 'w') as f:
            json.dump(assign_result, f, indent=2)
        print(f"指派后的任务详情已保存到: {output_file}")
        
        # 验证指派结果
        new_assignee = "未知"
        try:
            if 'data' in assign_result and 'relationships' in assign_result['data']:
                assignee_data = assign_result['data']['relationships'].get('assignee', {}).get('data')
                if assignee_data:
                    assignee_id = assignee_data.get('id', '')
                    # 检查是否与指定的成员匹配
                    if assignee_id == member_guid:
                        # 从included中查找成员名称
                        if 'included' in assign_result:
                            for item in assign_result['included']:
                                if item.get('type') == 'members' and item.get('id') == assignee_id:
                                    new_assignee = item.get('attributes', {}).get('nickname', '未知')
                                    break
                        print(f"\n任务现在指派给: {new_assignee}")
                        print("\n指派成功验证!")
                    else:
                        print(f"\n警告: 指派后的任务负责人ID与请求不匹配: {assignee_id} != {member_guid}")
                else:
                    print("\n警告: 指派后的任务没有负责人")
        except Exception as e:
            print(f"验证指派结果失败: {str(e)}")
    else:
        print("指派任务失败，API调用失败")
        return 1
    
    print("\nTower API任务指派测试完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())