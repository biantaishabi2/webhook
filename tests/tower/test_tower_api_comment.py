#!/usr/bin/env python
"""
测试Tower API任务评论功能
"""

import sys
import json
import os
import argparse
from app.utils.tower_api import get_access_token, get_todo_details, create_todo_comment, get_todo_comments

def main():
    """测试Tower API任务评论功能"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试Tower API任务评论功能')
    parser.add_argument('--todo-guid', type=str, help='要添加评论的Tower任务GUID')
    parser.add_argument('--comment', type=str, help='评论内容 (HTML格式)')
    args = parser.parse_args()
    
    print("测试Tower API任务评论...")
    
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
    
    # 获取任务标题
    task_title = "未知任务"
    try:
        if 'data' in todo_details and 'attributes' in todo_details['data']:
            task_title = todo_details['data']['attributes'].get('content', '未知任务')
    except Exception as e:
        print(f"提取任务标题失败: {str(e)}")
    
    print(f"\n当前任务标题: {task_title}")
    
    # 4. 获取当前评论
    print("\n获取当前评论列表...")
    current_comments = get_todo_comments(todo_guid)
    
    if current_comments:
        comments_file = 'tower_todo_comments_before.json'
        with open(comments_file, 'w') as f:
            json.dump(current_comments, f, indent=2)
        print(f"当前评论已保存到: {comments_file}")
        
        comment_count = 0
        try:
            if 'data' in current_comments:
                comment_count = len(current_comments['data'])
        except Exception as e:
            print(f"获取评论数量失败: {str(e)}")
            
        print(f"当前评论数量: {comment_count}")
    else:
        print("未能获取当前评论或任务暂无评论")
    
    # 5. 添加评论
    comment_content = args.comment
    if not comment_content:
        print("没有提供评论内容，使用测试评论")
        comment_content = f"<p>API测试评论 - {os.path.basename(__file__)} - {os.getpid()}</p>"
    
    print(f"\n添加评论: {comment_content}")
    comment_result = create_todo_comment(todo_guid, comment_content)
    
    if comment_result:
        print("\n成功添加评论!")
        # 保存到文件
        output_file = 'tower_comment_result.json'
        with open(output_file, 'w') as f:
            json.dump(comment_result, f, indent=2)
        print(f"评论结果已保存到: {output_file}")
        
        # 验证评论是否成功添加
        new_comments = get_todo_comments(todo_guid)
        if new_comments:
            new_comments_file = 'tower_todo_comments_after.json'
            with open(new_comments_file, 'w') as f:
                json.dump(new_comments, f, indent=2)
            print(f"更新后的评论列表已保存到: {new_comments_file}")
            
            new_comment_count = 0
            try:
                if 'data' in new_comments:
                    new_comment_count = len(new_comments['data'])
            except Exception as e:
                print(f"获取更新后评论数量失败: {str(e)}")
                
            print(f"更新后评论数量: {new_comment_count}")
            
            # 检查最新的评论是否是我们添加的（Tower API返回的评论列表是按时间升序排序的，最新的在最后）
            try:
                if 'data' in new_comments and len(new_comments['data']) > 0:
                    # 获取最后一条评论（最新的）
                    latest_comment = new_comments['data'][-1]
                    if 'attributes' in latest_comment:
                        latest_content = latest_comment['attributes'].get('content', '')
                        print(f"\n最新评论内容: {latest_content}")
                        
                        if comment_content in latest_content:
                            print("\n评论添加成功验证!")
                        else:
                            print("\n警告: 最新评论内容与添加的评论不匹配")
                            
                        # 打印所有评论内容以便验证
                        print("\n所有评论:")
                        for i, comment in enumerate(new_comments['data']):
                            if 'attributes' in comment and 'content' in comment['attributes']:
                                content = comment['attributes']['content']
                                created_at = comment['attributes'].get('created_at', 'unknown')
                                print(f"{i+1}. [{created_at}] {content}")
            except Exception as e:
                print(f"验证最新评论失败: {str(e)}")
    else:
        print("添加评论失败，API调用失败")
        return 1
    
    print("\nTower API评论测试完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())