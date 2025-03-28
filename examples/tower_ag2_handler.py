#!/usr/bin/env python
"""
Tower Webhook AG2执行处理器

专门用于处理来自Tower的webhook请求，并根据特定条件调用AG2 Two Agent Executor
"""

import sys
import os
import argparse
import json
import logging
import time
import asyncio
from pathlib import Path
from datetime import datetime
import re
import requests
from app.utils.tower_api import get_access_token, get_todo_details

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'ag2_handler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

# AG2 Two Agent Executor路径
AG2_PATH = "/home/wangbo/document/wangbo/task_planner/ag2-wrapper"

# Tower API配置
TOWER_API_BASE = "https://tower.im/api/v1"

# 添加AG2路径到系统路径
if AG2_PATH not in sys.path:
    sys.path.append(AG2_PATH)

# 延迟导入AG2模块，确保路径已添加
def import_ag2_modules():
    try:
        # 导入AG2相关模块
        from ag2_wrapper.core.ag2_two_agent_executor import AG2TwoAgentExecutor
        from ag2_wrapper.core.config import ConfigManager
        from ag2_wrapper.core.ag2tools import AG2ToolManager
        from ag2_wrapper.core.ag2_context import ContextManager
        from task_planner.core.context_management import TaskContext
        
        logger.info("成功导入AG2相关模块")
        return {
            "AG2TwoAgentExecutor": AG2TwoAgentExecutor,
            "ConfigManager": ConfigManager,
            "AG2ToolManager": AG2ToolManager,
            "ContextManager": ContextManager,
            "TaskContext": TaskContext
        }
    except ImportError as e:
        logger.error(f"导入AG2模块失败: {str(e)}")
        return None

async def create_ag2_executor():
    """创建AG2 TwoAgentExecutor实例"""
    modules = import_ag2_modules()
    if not modules:
        logger.error("无法创建AG2执行器：模块导入失败")
        return None
    
    try:
        # 实例化所需组件
        config = modules["ConfigManager"]()
        tool_manager = modules["AG2ToolManager"]()
        context_manager = modules["ContextManager"](cwd=os.getcwd())
        
        # 创建执行器
        executor = await modules["AG2TwoAgentExecutor"].create(
            config=config,
            tool_manager=tool_manager,
            context_manager=context_manager
        )
        
        logger.info("成功创建AG2执行器实例")
        return executor
    except Exception as e:
        logger.error(f"创建AG2执行器时发生错误: {str(e)}")
        return None

def parse_tower_payload(payload):
    """解析Tower webhook payload"""
    try:
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload
            
        # 提取关键信息
        action = data.get('action', '')
        project_data = data.get('data', {}).get('project', {})
        todo_data = data.get('data', {}).get('todo', {})
        todolist_data = data.get('data', {}).get('todolist', {})
        
        # 构建结构化数据
        result = {
            'action': action,
            'project': {
                'id': project_data.get('guid', ''),
                'name': project_data.get('name', '')
            },
            'todo': {
                'id': todo_data.get('guid', ''),
                'title': todo_data.get('title', ''),
                'updated_at': todo_data.get('updated_at', ''),
                'handler': todo_data.get('handler', {}).get('nickname', ''),
                'handler_id': todo_data.get('handler', {}).get('guid', ''),
                'due_at': todo_data.get('due_at'),
                'labels': todo_data.get('labels', []),
                'priority': todo_data.get('priority', 'normal'),
                'description': todo_data.get('desc', '')
            },
            'todolist': {
                'id': todolist_data.get('guid', ''),
                'title': todolist_data.get('title', ''),
                'description': todolist_data.get('desc')
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"解析Tower payload失败: {str(e)}")
        return None

def should_trigger_ag2(parsed_data):
    """
    判断是否应该触发AG2执行器
    
    触发条件:
    1. 带有特定标签的任务（如"AG2", "AI", "自动化"）
    2. 任务标题包含特定关键词（如"[AG2]", "[AI]", "[自动]"）
    3. 任务列表名称为特定值（如"自动化任务", "AI处理"）
    """
    # 1. 检查标签
    trigger_labels = ["AG2", "AI", "自动化", "自动", "GPT"]
    task_labels = parsed_data.get('todo', {}).get('labels', [])
    for label in trigger_labels:
        if label in task_labels:
            logger.info(f"检测到触发标签: {label}")
            return True
    
    # 2. 检查标题关键词
    trigger_keywords = [r"\[AG2\]", r"\[AI\]", r"\[自动\]", r"\[GPT\]", r"\[自动化\]"]
    task_title = parsed_data.get('todo', {}).get('title', '')
    for keyword in trigger_keywords:
        if re.search(keyword, task_title, re.IGNORECASE):
            logger.info(f"检测到触发关键词: {keyword}")
            return True
    
    # 3. 检查任务列表名称
    trigger_lists = ["自动化任务", "AI处理", "AG2任务", "GPT处理"]
    todolist_title = parsed_data.get('todolist', {}).get('title', '')
    if todolist_title in trigger_lists:
        logger.info(f"检测到触发列表: {todolist_title}")
        return True
    
    return False

# 使用从tower_api.py导入的get_access_token和get_todo_details函数
# 不需要自己实现，复用项目中现有的功能

def extract_task_description(parsed_data, task_details=None):
    """从解析的数据中提取任务描述"""
    # 优先使用从API获取的详细描述
    description = ""
    
    # 如果有API获取的任务详情，从中提取
    if task_details:
        try:
            # 尝试从不同格式的API响应提取描述
            if 'data' in task_details and 'attributes' in task_details['data']:
                description = task_details['data']['attributes'].get('desc', '')
            elif 'desc' in task_details:
                description = task_details['desc']
        except Exception as e:
            logger.warning(f"从API响应提取描述失败: {str(e)}")
    
    # 如果API没有返回描述或提取失败，使用webhook中的描述
    if not description:
        description = parsed_data.get('todo', {}).get('description', '')
    
    # 如果描述仍为空，使用标题作为描述
    if not description:
        title = parsed_data.get('todo', {}).get('title', '')
        # 移除触发关键词
        for pattern in [r"\[AG2\]", r"\[AI\]", r"\[自动\]", r"\[GPT\]", r"\[自动化\]"]:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE).strip()
        description = title
    
    # 添加标准前缀
    task_id = parsed_data.get('todo', {}).get('id', '')
    project_name = parsed_data.get('project', {}).get('name', '')
    task_title = parsed_data.get('todo', {}).get('title', '')
    
    formatted_description = f"""
# Tower任务自动处理

## 任务信息
- 项目: {project_name}
- 任务ID: {task_id}
- 标题: {task_title}

## 任务描述
{description}

请完成上述任务并给出详细的执行过程和结果。当任务完成时，请回复"完成任务"。
"""
    
    return formatted_description

def create_task_definition(parsed_data, task_details=None):
    """创建任务定义"""
    return {
        'id': parsed_data.get('todo', {}).get('id', ''),
        'name': parsed_data.get('todo', {}).get('title', ''),
        'description': extract_task_description(parsed_data, task_details),
        'priority': parsed_data.get('todo', {}).get('priority', 'normal'),
        'due_at': parsed_data.get('todo', {}).get('due_at'),
        'timeout': 600,  # 10分钟超时
    }

async def process_tower_webhook(payload):
    """处理Tower webhook"""
    # 解析payload
    parsed_data = parse_tower_payload(payload)
    if not parsed_data:
        logger.error("无法解析Tower webhook数据")
        return False
    
    # 记录解析后的数据
    logger.info(f"解析后的Tower webhook数据:\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}")
    
    # 判断是否触发AG2
    if not should_trigger_ag2(parsed_data):
        logger.info("不满足AG2触发条件，跳过处理")
        return False
    
    # 获取任务详情
    todo_id = parsed_data.get('todo', {}).get('id', '')
    task_details = None
    if todo_id:
        logger.info(f"开始获取任务 {todo_id} 的详细信息")
        task_details = get_todo_details(todo_id)
        if task_details:
            logger.info(f"成功获取任务详情")
            # 记录任务详情以便分析
            details_file = f'/tmp/tower_ag2_logs/task_details_{todo_id}.json'
            os.makedirs(os.path.dirname(details_file), exist_ok=True)
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(task_details, f, indent=2, ensure_ascii=False)
            logger.info(f"任务详情已保存到: {details_file}")
        else:
            logger.warning(f"无法获取任务 {todo_id} 的详细信息，将使用webhook数据")
    
    # 创建任务上下文和定义
    modules = import_ag2_modules()
    if not modules:
        return False
    
    task_context = modules["TaskContext"](parsed_data.get('todo', {}).get('id', ''))
    task_definition = create_task_definition(parsed_data, task_details)
    
    # 创建执行器
    executor = await create_ag2_executor()
    if not executor:
        logger.error("无法创建AG2执行器")
        return False
    
    try:
        # 记录开始执行信息
        logger.info(f"开始执行AG2任务: {task_definition['name']}")
        start_time = time.time()
        
        # 执行任务
        result = executor.execute(
            prompt=task_definition['description'],
            task_definition=task_definition,
            task_context=task_context,
            context_data={
                'tower_task': task_details,
                'webhook_data': parsed_data
            },
            timeout=task_definition['timeout']
        )
        
        # 记录执行时间和结果
        execution_time = time.time() - start_time
        logger.info(f"AG2任务执行完成，耗时: {execution_time:.2f}秒")
        logger.info(f"执行结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 保存结果到文件
        log_dir = '/tmp/tower_ag2_logs'
        os.makedirs(log_dir, exist_ok=True)
        task_id = task_definition['id']
        
        result_file = f'{log_dir}/ag2_result_{task_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'task': task_definition,
                'result': result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"结果已保存到: {result_file}")
        return True
        
    except Exception as e:
        logger.error(f"执行AG2任务时出错: {str(e)}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Tower Webhook AG2处理程序')
    parser.add_argument('--raw_payload', type=str, help='原始的完整payload')
    parser.add_argument('--action', type=str, help='动作类型')
    args, unknown = parser.parse_known_args()
    
    # 验证必需参数
    if not args.raw_payload:
        logger.error("未提供raw_payload参数")
        return 1
    
    # 创建日志目录
    log_dir = '/tmp/tower_ag2_logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 运行异步处理函数
    try:
        logger.info("开始处理Tower webhook")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(process_tower_webhook(args.raw_payload))
        if result:
            logger.info("AG2处理成功完成")
            return 0
        else:
            logger.warning("AG2处理未执行或失败")
            return 0  # 返回0以避免webhook处理失败
    except Exception as e:
        logger.error(f"处理Tower webhook时发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())