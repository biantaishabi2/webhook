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
import warnings
from app.utils.tower_api import get_access_token, get_todo_details
from asyncio import Lock
from collections import defaultdict

# 抑制pydantic的警告
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")
warnings.filterwarnings("ignore", message="model_validate_strings")

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

# 抑制相关库的INFO日志
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('LiteLLM').setLevel(logging.WARNING)
logging.getLogger('litellm').setLevel(logging.WARNING)
logging.getLogger('autogen').setLevel(logging.ERROR)
logging.getLogger('ag2_wrapper').setLevel(logging.WARNING)

# Tower项目与本地目录的映射关系
PROJECT_MAPPING = {
    "5dc713a15ab57a0bcefcc2969729b6c4": {
        "project_name": "test敏捷迭代",
        "local_path": "tower",
        "description": "测试敏捷迭代项目"
    }
}

# AG2 Two Agent Executor路径
AG2_PATH = "/home/wangbo/document/wangbo/task_planner/ag2-wrapper"

# Tower API配置
TOWER_API_BASE = "https://tower.im/api/v1"

# 添加AG2路径到系统路径
if AG2_PATH not in sys.path:
    sys.path.append(AG2_PATH)

# 用于防止重复处理的锁
_task_locks = defaultdict(Lock)

def get_project_dir(project_id: str) -> Path:
    """
    根据Tower项目ID获取本地项目目录，如果目录不存在则创建
    Args:
        project_id: Tower项目ID
    Returns:
        Path: 项目目录路径
    """
    if project_id not in PROJECT_MAPPING:
        raise ValueError(f"未找到项目ID {project_id} 的映射关系")
    
    project_info = PROJECT_MAPPING[project_id]
    # 获取用户主目录
    home_dir = Path.home()
    # 项目根目录
    projects_root = home_dir / "document" / "wangbo" / "projects"
    project_dir = projects_root / project_info["local_path"]
    
    # 创建项目根目录
    projects_root.mkdir(parents=True, exist_ok=True)
    logger.info(f"项目根目录: {projects_root}")
    
    # 创建项目目录
    project_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"项目目录: {project_dir}")
    
    return project_dir

def setup_task_directory(project_dir: Path, task_id: str) -> Path:
    """
    设置任务工作目录
    Args:
        project_dir: 项目目录
        task_id: 任务ID
    Returns:
        Path: 任务工作目录
    """
    # 创建任务目录
    tasks_dir = project_dir / "tasks"
    task_dir = tasks_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    return task_dir

def load_task_details(task_details: dict, parsed_data: dict) -> tuple:
    """
    加载任务详情并创建任务定义
    Args:
        task_details: Tower API返回的任务详情
        parsed_data: 解析后的webhook数据
    Returns:
        tuple: (task_details, task_definition, prompt)
    """
    try:
        # 提取关键信息
        task_id = parsed_data['todo']['id']
        task_title = parsed_data['todo']['title']
        # 优先使用API返回的详细描述
        task_desc = ""
        if task_details and 'data' in task_details and 'attributes' in task_details['data']:
            task_desc = task_details['data']['attributes'].get('desc', '')
        # 如果API返回的描述为空，则使用webhook数据中的描述
        if not task_desc:
            task_desc = parsed_data['todo'].get('description', '')
        
        project_id = parsed_data['project']['id']
        
        # 获取项目目录
        project_dir = get_project_dir(project_id)
        project_info = PROJECT_MAPPING[project_id]
        logger.info(f"项目目录: {project_dir}")
        
        # 设置任务工作目录
        task_dir = setup_task_directory(project_dir, task_id)
        logger.info(f"任务工作目录: {task_dir}")
        
        # 保存任务详情到工作目录
        details_file = task_dir / "task_details.json"
        with open(details_file, 'w', encoding='utf-8') as f:
            json.dump(task_details, f, indent=2, ensure_ascii=False)
        logger.info(f"任务详情已保存到: {details_file}")
        
        # 构建AG2任务提示
        prompt = f"""
## 任务描述
{task_desc}
"""
        
        # 构建任务定义
        task_definition = {
            'id': task_id,
            'name': task_title,
            'description': prompt,
            'success_criteria': [
                "成功完成Tower任务要求",
                "生成所需的代码文件",
                "代码功能正确且测试通过"
            ],
            'project_id': project_id,
            'project_name': project_info['project_name'],
            'project_dir': str(project_dir),
            'work_dir': str(task_dir)
        }
        
        return task_details, task_definition, prompt
        
    except ValueError as e:
        logger.error(f"项目映射错误: {str(e)}")
        return None, None, None
    except FileNotFoundError as e:
        logger.error(f"项目目录错误: {str(e)}")
        return None, None, None
    except Exception as e:
        logger.error(f"设置工作目录时发生错误: {str(e)}")
        return None, None, None

# 延迟导入AG2模块，确保路径已添加
def import_ag2_modules():
    try:
        # 导入AG2相关模块
        from ag2_wrapper.core.ag2_two_agent_executor import AG2TwoAgentExecutor
        from ag2_wrapper.core.config import ConfigManager, create_openrouter_config
        from ag2_wrapper.core.ag2tools import AG2ToolManager
        from ag2_wrapper.core.ag2_context import ContextManager
        from task_planner.core.context_management import TaskContext
        
        logger.info("成功导入AG2相关模块")
        return {
            "AG2TwoAgentExecutor": AG2TwoAgentExecutor,
            "ConfigManager": ConfigManager,
            "AG2ToolManager": AG2ToolManager,
            "ContextManager": ContextManager,
            "TaskContext": TaskContext,
            "create_openrouter_config": create_openrouter_config
        }
    except ImportError as e:
        logger.error(f"导入AG2模块失败: {str(e)}")
        return None

def create_ag2_executor():
    """创建AG2执行器"""
    try:
        # 导入AG2模块
        modules = import_ag2_modules()
        if not modules:
            return None
        
        # 创建配置管理器
        config = modules["ConfigManager"]()
        
        # 创建工具管理器
        tool_manager = modules["AG2ToolManager"]()
        
        # 使用 create() 方法创建执行器
        executor = modules["AG2TwoAgentExecutor"].create(
            config=config,
            tool_manager=tool_manager
        )
        
        # 等待执行器初始化完成
        if asyncio.iscoroutine(executor):
            executor = asyncio.get_event_loop().run_until_complete(executor)
        
        return executor
    except Exception as e:
        logger.error(f"创建AG2执行器时出错: {str(e)}")
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

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Tower Webhook AG2处理程序')
    parser.add_argument('--raw_payload', type=str, help='原始的完整payload')
    parser.add_argument('--action', type=str, help='动作类型')
    parser.add_argument('--event_type', type=str, help='事件类型')
    args, unknown = parser.parse_known_args()
    
    # 验证必需参数
    if not args.raw_payload:
        logger.error("未提供raw_payload参数")
        return 1
        
    # 检查事件类型，只处理 todos 事件
    if args.event_type != 'todos':
        logger.info(f"跳过非todos事件: {args.event_type}")
        return 0
    
    # 创建日志目录
    log_dir = '/tmp/tower_ag2_logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 解析 raw_payload
    logger.info("="*50)
    logger.info("1. 开始解析webhook payload")
    try:
        payload = json.loads(args.raw_payload)
    except json.JSONDecodeError as e:
        logger.error(f"解析 raw_payload 失败: {str(e)}")
        return 1
    
    # 保存原始工作目录
    original_cwd = os.getcwd()
    logger.info(f"原始工作目录: {original_cwd}")

    # 运行处理函数
    try:
        logger.info("开始处理Tower webhook")
        
        # 解析数据
        parsed_data = parse_tower_payload(payload)
        if not parsed_data:
            logger.error("无法解析Tower webhook数据")
            return 1
        logger.info(f"解析后的Tower webhook数据:\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}")

        # 检查触发条件
        logger.info("2. 检查是否满足AG2触发条件")
        if not should_trigger_ag2(parsed_data):
            logger.info("不满足AG2触发条件，跳过处理")
            return 0
        logger.info("满足AG2触发条件，继续处理")

        # 获取任务详情
        logger.info(f"3. 开始获取任务 {parsed_data['todo']['id']} 的详细信息")
        todo_id = parsed_data['todo']['id']
        task_details = get_todo_details(todo_id) if todo_id else None
        if task_details:
            logger.info("成功获取任务详情")
            # logger.info(f"任务详情:\n{json.dumps(task_details, indent=2, ensure_ascii=False)}") # 任务详情日志太长，暂时注释
        else:
            logger.warning(f"无法获取任务 {todo_id} 的详细信息，将使用webhook数据")
            return 1 # 或者根据需要处理
            
        # 加载任务详情并创建任务定义
        logger.info("4. 开始加载任务详情并创建任务定义")
        task_details, task_definition, prompt = load_task_details(task_details, parsed_data)
        if not task_details or not task_definition:
            logger.error("无法加载任务详情或创建任务定义")
            return 1
        logger.info("成功创建任务定义")
        logger.info(f"任务定义:\n{json.dumps(task_definition, indent=2, ensure_ascii=False)}")

        # 创建执行器
        logger.info("5. 开始创建AG2执行器")
        executor = create_ag2_executor()
        if not executor:
            logger.error("无法创建AG2执行器")
            return 1
        logger.info("成功创建AG2执行器")

        # 创建任务上下文
        logger.info("6. 创建任务上下文")
        modules = import_ag2_modules()
        if not modules:
             return 1
        task_context = modules["TaskContext"](
            task_definition['id'],
            base_dir=Path(task_definition['work_dir']) 
        )
        logger.info(f"成功创建任务上下文, base_dir={task_definition['work_dir']}")
        
        # 切换到项目工作目录!
        project_dir = task_definition['project_dir']
        logger.info(f"7. 切换到项目工作目录: {project_dir}")
        os.chdir(project_dir)
        logger.info(f"当前工作目录已切换为: {os.getcwd()}")
        
        # 执行任务
        logger.info("8. 开始执行AG2任务")
        logger.info(f"任务提示:\n{prompt}")
        start_time = time.time()
        result = executor.execute(
            prompt=prompt,
            task_definition=task_definition,
            task_context=task_context, # 传递 context
            timeout=600
        )
        execution_time = time.time() - start_time
        logger.info("9. AG2任务执行完成")
        logger.info(f"执行耗时: {execution_time:.2f}秒")

        # --- 修改后的结果处理逻辑 ---
        serializable_result = {}
        chat_history = []
        summary = ""
        success = False
        error_msg = ""
        cost = None 
        actual_autogen_result = None # 用于存储内层的 Autogen 结果

        try:
            from autogen import ChatResult
            
            # 先判断外层结果类型
            if isinstance(result, dict) and 'result' in result:
                # 如果是包装器返回的字典，获取内层结果
                actual_autogen_result = result.get("result")
                # 尝试从外层获取状态（如果包装器设置了的话）
                success = result.get("success", False) # 初始 success 基于外层
                error_msg = result.get("error_message", result.get("error", ""))
                logger.info(f"检测到包装器字典结果。内层结果类型: {type(actual_autogen_result)}")
            else:
                # 否则，认为 result 本身就是 Autogen 结果（虽然根据 wrapper 代码不太可能）
                actual_autogen_result = result
                logger.info(f"结果似乎是直接的 Autogen 结果。类型: {type(actual_autogen_result)}")

            # 现在处理 actual_autogen_result (内层结果)
            is_chat_result = isinstance(actual_autogen_result, ChatResult)
            is_dict_result = isinstance(actual_autogen_result, dict)

            if is_chat_result:
                summary = actual_autogen_result.summary or ""
                chat_history = actual_autogen_result.chat_history or []
                cost = actual_autogen_result.cost
                # 安全地访问 error 属性
                inner_error_obj = getattr(actual_autogen_result, 'error', None)
                if inner_error_obj:
                     error_msg = str(inner_error_obj) # 内层错误优先
            elif is_dict_result:
                # 尝试从内层字典中提取信息
                summary = actual_autogen_result.get("summary", "")
                chat_history = actual_autogen_result.get("chat_history", [])
                cost = actual_autogen_result.get("cost")
                # 如果内层字典有错误信息，也记录下来
                inner_error = actual_autogen_result.get("error_message", actual_autogen_result.get("error", ""))
                if inner_error:
                    error_msg = f"{error_msg} | Inner: {inner_error}".strip(" | ")
                # 如果内层字典有 success 标志，它可能更准确
                if "success" in actual_autogen_result:
                    success = actual_autogen_result.get("success", success) # 优先用内层 success
            elif actual_autogen_result is not None: # 如果内层结果不是 None 但也不是 ChatResult 或 dict
                logger.warning(f"内层 Autogen 结果类型未知: {type(actual_autogen_result)}")
                summary = str(actual_autogen_result) # 尝试转为字符串作为摘要
                error_msg = f"{error_msg} | Unknown inner result type: {type(actual_autogen_result)}".strip(" | ")
                # 无法确定成功状态，可能保留外层字典的判断
            else:
                 logger.warning("无法获取有效的内层 Autogen 结果")
                 # 保留可能从外层字典获取的 error_msg 和 success 状态

            # 统一判断成功逻辑 (如果上面没有明确设置 success 或需要根据对话判断)
            # 仅在未明确判断为成功，且有聊天记录时，尝试根据最后消息判断
            if not success and chat_history:
                last_message = chat_history[-1].get("content", "") if chat_history else ""
                if "完成任务" in last_message or "任务完成" in last_message:
                     # 如果外层没有报错，且最后消息是完成，则认为是成功
                     if not error_msg:
                         success = True
            elif not chat_history and not error_msg and summary: # 弱判断：无聊天记录，无错误，有摘要
                 if "error" not in summary.lower() and "failed" not in summary.lower():
                     success = True
                         
            # 构建最终的可序列化结果
            serializable_result = {
                "summary": summary,
                "cost": cost,
                "chat_history": chat_history, 
                "success": success, 
                "error_message": error_msg
            }

            # 记录聊天记录到日志 (如果找到了)
            if chat_history:
                logger.info("--- AG2 对话记录 ---")
                for message in chat_history:
                    role = message.get('role', 'unknown')
                    content = str(message.get('content', '')) #确保内容是字符串
                    log_content = content[:500] + '...' if len(content) > 500 else content
                    logger.info(f"[{role.upper()}]: {log_content}")
                logger.info("--- 对话记录结束 ---")
            else:
                 logger.info("未在结果中找到有效的对话记录 (chat_history)")

        except ImportError:
             logger.warning("无法导入 autogen.ChatResult，处理可能不完整。")
             serializable_result = {"raw_result": str(actual_autogen_result or result), "error": "无法处理 ChatResult"}
             success = False # 无法确定
        except Exception as e:
             logger.error(f"处理 AG2 返回结果时出错: {str(e)}")
             serializable_result = {"error": f"处理结果时出错: {str(e)}"}
             success = False
        # --- 结果处理逻辑结束 ---

        # 使用处理过的、可序列化的结果记录日志
        try:
            logger.info(f"执行结果 (处理后):\n{json.dumps(serializable_result, indent=2, ensure_ascii=False)}")
        except TypeError as json_error:
            logger.error(f"序列化处理后的结果时仍然出错: {json_error}")
            logger.error(f"尝试记录部分结果: success={success}, error='{error_msg}', summary='{summary[:100]}...' ")
            # 记录一个简化的错误信息，避免程序崩溃
            serializable_result = {"error": f"Result serialization failed: {json_error}", "success": success, "summary_preview": summary[:100]}

        # 保存结果到任务目录 (使用可序列化的结果)
        logger.info("10. 保存执行结果")
        result_file_path = Path(task_definition['work_dir']) / f'ag2_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(result_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'task': task_definition,
                # 保存处理后的 serializable_result
                'result': serializable_result, 
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"结果已保存到: {result_file_path.resolve()}")
        
        # 根据提取的 success 状态判断
        if success:
            logger.info("AG2处理成功完成")
            return 0
        else:
            logger.warning(f"AG2处理未执行或失败. Error: {error_msg}")
            return 1 # 返回错误码
    except Exception as e:
        logger.error(f"处理Tower webhook时发生异常: {str(e)}")
        # 记录完整的traceback
        import traceback
        logger.error(traceback.format_exc())
        return 1
    finally:
        # 切换回原来的目录
        if 'original_cwd' in locals() and os.path.exists(original_cwd):
             logger.info(f"切换回原始工作目录: {original_cwd}")
             os.chdir(original_cwd)
             logger.info(f"当前工作目录已恢复为: {os.getcwd()}")
        logger.info("="*50)
        logger.info("Tower webhook处理流程结束")
        logger.info("="*50)

if __name__ == "__main__":
    sys.exit(main())