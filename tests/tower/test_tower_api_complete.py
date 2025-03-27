#!/usr/bin/env python3
"""
Tower API 完成/重新打开任务测试脚本
"""

import sys
import argparse
import json
from app.utils.tower_api import get_todo_details, complete_todo
from app.utils.logging import get_logger

logger = get_logger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试Tower API完成/重新打开任务')
    parser.add_argument('todo_guid', help='任务GUID')
    parser.add_argument('--action', choices=['complete', 'reopen'], default='complete',
                      help='操作类型: complete或reopen (默认: complete)')
    
    args = parser.parse_args()
    
    # 首先获取任务当前状态
    before = get_todo_details(args.todo_guid)
    if not before:
        logger.error("无法获取任务详情，操作已停止")
        return 1
    
    # 显示任务当前状态
    if 'data' in before and 'attributes' in before['data']:
        attributes = before['data']['attributes']
        is_completed = attributes.get('is_completed', False)
        logger.info(f"任务当前状态: {'已完成' if is_completed else '未完成'}")
        logger.info(f"任务内容: {attributes.get('content', '无内容')}")
    else:
        logger.warning("获取任务状态失败，响应格式不正确")
        return 1
    
    # 根据操作选择是否标记为已完成
    completed = args.action == 'complete'
    if completed == is_completed:
        logger.warning(f"任务已经{'完成' if completed else '未完成'}状态，将尝试再次设置相同状态")
    
    # 调用API进行更新
    logger.info(f"正在{'完成' if completed else '重新打开'}任务...")
    result = complete_todo(args.todo_guid, completed)
    
    if not result:
        logger.error("API调用失败，未能更新任务状态")
        return 1
    
    # 检查API返回的状态
    if 'data' in result and 'attributes' in result['data']:
        attributes = result['data']['attributes']
        new_status = attributes.get('is_completed', None)
        logger.info(f"API返回的任务状态: {'已完成' if new_status else '未完成'}")
        
        if new_status == completed:
            logger.info(f"任务已成功{'完成' if completed else '重新打开'}")
            # 打印任务详情的JSON格式
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        else:
            logger.warning(f"任务状态未按预期更新: 请求{'完成' if completed else '未完成'}，但API返回{'完成' if new_status else '未完成'}")
    else:
        logger.warning("API响应格式不符合预期")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())