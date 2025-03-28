#!/usr/bin/env python3
"""
Tower API 综合测试脚本
整合了所有Tower API相关的测试功能，包括：
- 获取/刷新访问令牌
- 获取团队和项目信息
- 任务详情获取
- 任务评论功能
- 任务状态更新
- 任务指派功能
"""

import sys
import json
import os
import re
import argparse
from datetime import datetime
from app.utils.tower_api import (
    get_access_token, 
    get_todo_details,
    create_todo_comment,
    get_todo_comments,
    complete_todo,
    update_todo_desc,
    assign_todo
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

def extract_guid_from_log():
    """从最新的webhook日志中提取任务GUID"""
    try:
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "logs"
        )
        if not os.path.exists(log_dir):
            print(f"日志目录不存在: {log_dir}")
            return None
            
        log_files = [f for f in os.listdir(log_dir) if f.startswith('webhook_')]
        if not log_files:
            print("没有找到webhook日志文件")
            return None
            
        latest_log = sorted(log_files)[-1]
        print(f"找到最新的日志文件: {latest_log}")
        
        with open(os.path.join(log_dir, latest_log), 'r') as f:
            content = f.read()
            print(f"日志文件内容:\n{content}")
            
            # 尝试多种可能的格式
            guid_patterns = [
                r'"todo".*?"guid".*?"([a-f0-9]+)"',  # 标准JSON格式
                r'"guid".*?"([a-f0-9]+)".*?"todo"',  # 反向顺序
                r'guid=([a-f0-9]+)',                 # URL参数格式
                r'todo/([a-f0-9]+)',                 # URL路径格式
            ]
            
            for pattern in guid_patterns:
                match = re.search(pattern, content)
                if match:
                    todo_guid = match.group(1)
                    print(f"使用模式 '{pattern}' 从日志中提取的任务GUID: {todo_guid}")
                    return todo_guid
                    
            print("在日志文件中没有找到任务GUID信息")
            print("尝试过的正则表达式模式:")
            for pattern in guid_patterns:
                print(f"- {pattern}")
                
    except Exception as e:
        print(f"从日志提取GUID失败: {str(e)}")
    return None

def save_json_response(data, filename):
    """保存API响应到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"数据已保存到: {filename}")
        return True
    except Exception as e:
        print(f"保存数据到 {filename} 失败: {str(e)}")
        return False

def test_todo_details(todo_guid):
    """测试获取任务详情"""
    print(f"\n=== 测试获取任务详情 ===")
    print(f"任务GUID: {todo_guid}")
    
    todo_details = get_todo_details(todo_guid)
    if not todo_details:
        print("获取任务详情失败")
        return False
        
    save_json_response(todo_details, 'tower_todo_details.json')
    
    # 提取并显示关键信息
    try:
        if 'data' in todo_details and 'attributes' in todo_details['data']:
            attrs = todo_details['data']['attributes']
            print("\n任务信息:")
            print(f"- 标题: {attrs.get('content', '无标题')}")
            print(f"- 描述: {attrs.get('desc', '无描述')}")
            print(f"- 状态: {'已完成' if attrs.get('is_completed', False) else '未完成'}")
            print(f"- 创建时间: {attrs.get('created_at', '未知')}")
            return True
    except Exception as e:
        print(f"解析任务详情失败: {str(e)}")
    return False

def test_todo_comment(todo_guid, comment_text=None):
    """测试任务评论功能"""
    print(f"\n=== 测试任务评论功能 ===")
    
    # 1. 获取当前评论列表
    print("\n获取当前评论列表...")
    comments = get_todo_comments(todo_guid)
    if comments:
        save_json_response(comments, 'tower_comments_before.json')
        try:
            comment_count = len(comments.get('data', []))
            print(f"当前评论数: {comment_count}")
        except Exception as e:
            print(f"解析评论列表失败: {str(e)}")
    
    # 2. 添加新评论
    if not comment_text:
        comment_text = f"<p>API测试评论 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    
    print(f"\n添加新评论: {comment_text}")
    result = create_todo_comment(todo_guid, comment_text)
    
    if result:
        save_json_response(result, 'tower_comment_result.json')
        print("评论添加成功!")
        
        # 3. 再次获取评论列表验证
        print("\n验证评论是否添加成功...")
        updated_comments = get_todo_comments(todo_guid)
        if updated_comments:
            save_json_response(updated_comments, 'tower_comments_after.json')
            try:
                new_count = len(updated_comments.get('data', []))
                print(f"更新后评论数: {new_count}")
                if new_count > comment_count:
                    print("评论数量增加，验证成功!")
                    return True
            except Exception as e:
                print(f"验证评论添加失败: {str(e)}")
    else:
        print("添加评论失败")
    
    return False

def test_todo_status(todo_guid, action='complete'):
    """测试任务状态更新"""
    print(f"\n=== 测试任务状态更新 ===")
    
    # 1. 获取当前状态
    current = get_todo_details(todo_guid)
    if not current:
        print("无法获取任务当前状态")
        return False
    
    try:
        is_completed = current['data']['attributes']['is_completed']
        print(f"当前状态: {'已完成' if is_completed else '未完成'}")
        
        # 2. 更新状态
        should_complete = action == 'complete'
        if should_complete == is_completed:
            print(f"任务已经是{'完成' if should_complete else '未完成'}状态")
            return True
            
        print(f"将任务状态更新为: {'完成' if should_complete else '重新打开'}")
        result = complete_todo(todo_guid, should_complete)
        
        if result:
            save_json_response(result, 'tower_todo_status_update.json')
            new_status = result['data']['attributes']['is_completed']
            if new_status == should_complete:
                print("状态更新成功!")
                return True
            else:
                print("状态未按预期更新")
        else:
            print("更新状态失败")
            
    except Exception as e:
        print(f"处理任务状态时出错: {str(e)}")
    
    return False

def test_todo_desc(todo_guid, new_desc=None):
    """测试更新任务描述"""
    print(f"\n=== 测试更新任务描述 ===")
    
    # 1. 获取当前描述
    current = get_todo_details(todo_guid)
    if not current:
        print("无法获取任务当前信息")
        return False
    
    try:
        current_desc = current['data']['attributes'].get('desc', '无描述')
        print(f"当前描述: {current_desc}")
        
        # 2. 更新描述
        if not new_desc:
            new_desc = f"<p>API测试描述更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        
        print(f"更新描述为: {new_desc}")
        result = update_todo_desc(todo_guid, new_desc)
        
        if result:
            save_json_response(result, 'tower_todo_desc_update.json')
            updated_desc = result['data']['attributes'].get('desc', '')
            # Tower API可能会自动给更新的内容包裹额外的p标签
            if updated_desc == new_desc or updated_desc == f"<p>{new_desc}</p>":
                print("描述更新成功!")
                return True
            else:
                print(f"描述未按预期更新。预期: {new_desc}, 实际: {updated_desc}")
        else:
            print("更新描述失败")
            
    except Exception as e:
        print(f"处理任务描述时出错: {str(e)}")
    
    return False

def test_todo_assign(todo_guid, member_guid=None):
    """测试任务指派"""
    print(f"\n=== 测试任务指派 ===")
    
    if not member_guid:
        print("未提供成员GUID，跳过指派测试")
        return False
    
    print(f"将任务指派给成员: {member_guid}")
    result = assign_todo(todo_guid, member_guid)
    
    if result:
        save_json_response(result, 'tower_todo_assign.json')
        try:
            assigned_to = result['data']['attributes'].get('assigned', {}).get('id')
            if assigned_to == member_guid:
                print("任务指派成功!")
                return True
            else:
                print(f"指派结果与预期不符，当前指派给: {assigned_to}")
        except Exception as e:
            print(f"验证指派结果时出错: {str(e)}")
    else:
        print("指派任务失败")
    
    return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Tower API综合测试工具')
    parser.add_argument('--todo-guid', type=str, help='要测试的Tower任务GUID')
    parser.add_argument('--member-guid', type=str, help='要指派的成员GUID')
    parser.add_argument('--comment', type=str, help='要添加的评论内容')
    parser.add_argument('--desc', type=str, help='要更新的任务描述')
    parser.add_argument('--action', choices=['complete', 'reopen'], help='任务状态操作')
    parser.add_argument('--tests', type=str, nargs='+', 
                      choices=['details', 'comment', 'status', 'desc', 'assign', 'all'],
                      default=['all'],
                      help='要运行的测试类型')
    
    args = parser.parse_args()
    
    # 1. 获取访问令牌 - 使用tower_api.py中的完整缓存逻辑
    access_token = get_access_token()
    if not access_token:
        print("无法获取访问令牌，请按照提示获取新令牌")
        return 1
    
    print(f"使用访问令牌: {access_token[:10]}...")
    
    # 2. 获取任务GUID
    todo_guid = args.todo_guid or extract_guid_from_log()
    if not todo_guid:
        print("无法获取任务GUID，请使用--todo-guid参数指定")
        return 1
    
    # 3. 运行选定的测试
    tests = args.tests
    if 'all' in tests:
        tests = ['details', 'comment', 'status', 'desc', 'assign']
    
    results = {}
    
    for test in tests:
        if test == 'details':
            results['details'] = test_todo_details(todo_guid)
        elif test == 'comment':
            results['comment'] = test_todo_comment(todo_guid, args.comment)
        elif test == 'status':
            results['status'] = test_todo_status(todo_guid, args.action)
        elif test == 'desc':
            results['desc'] = test_todo_desc(todo_guid, args.desc)
        elif test == 'assign':
            results['assign'] = test_todo_assign(todo_guid, args.member_guid)
    
    # 4. 输出测试结果摘要
    print("\n=== 测试结果摘要 ===")
    for test, result in results.items():
        print(f"{test.capitalize()}: {'成功' if result else '失败'}")
    
    # 如果有任何测试失败，返回非零状态码
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main()) 