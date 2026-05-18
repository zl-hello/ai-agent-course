"""
Practice 04: AnythingLLM 查询工具模块
使用 subprocess 调用 curl 命令访问 AnythingLLM API
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional


def query_anythingllm(message: str, 
                      api_key: Optional[str] = None, 
                      workspace_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    使用 curl 命令查询 AnythingLLM 工作区
    
    Args:
        message: 要发送的查询消息
        api_key: AnythingLLM API 密钥，如果为 None 则从环境变量读取
        workspace_slug: 工作区标识符，如果为 None 则从环境变量读取
        
    Returns:
        包含查询结果的字典
    """
    # 从环境变量获取配置（如果未提供）
    if api_key is None:
        api_key = os.environ.get('ANYTHINGLLM_API_KEY')
    
    if workspace_slug is None:
        workspace_slug = os.environ.get('ANYTHINGLLM_WORKSPACE_SLUG', 'default')
    
    # 检查配置
    if not api_key:
        return {
            "success": False,
            "error": "未配置 AnythingLLM API 密钥。请在 .env 文件中设置 ANYTHINGLLM_API_KEY"
        }
    
    if not workspace_slug:
        return {
            "success": False,
            "error": "未配置 AnythingLLM 工作区标识符。请在 .env 文件中设置 ANYTHINGLLM_WORKSPACE_SLUG"
        }
    
    # 构建 API URL
    base_url = os.environ.get('ANYTHINGLLM_BASE_URL', 'http://localhost:3001')
    url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    
    # 构建请求体
    request_body = {
        "message": message,
        "mode": "chat"
    }
    
    # 将请求体转换为 JSON 字符串（确保中文正确编码）
    json_data = json.dumps(request_body, ensure_ascii=False)
    
    # 构建 curl 命令
    # 注意：使用 --data-binary 和 -H "Content-Type: application/json" 确保中文编码正确
    curl_command = [
        'curl',
        '-s',  # 静默模式
        '-X', 'POST',
        url,
        '-H', 'Content-Type: application/json',
        '-H', f'Authorization: Bearer {api_key}',
        '--data-binary', json_data.encode('utf-8')
    ]
    
    try:
        # 执行 curl 命令
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        
        # 检查命令是否成功执行
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"curl 命令执行失败: {result.stderr}",
                "command": ' '.join(curl_command[:5]) + '...'  # 部分命令用于调试
            }
        
        # 解析响应
        if not result.stdout:
            return {
                "success": False,
                "error": "API 返回空响应"
            }
        
        try:
            response_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"无法解析 API 响应: {e}",
                "raw_response": result.stdout[:500]  # 前500字符用于调试
            }
        
        # 检查响应中是否包含错误
        if 'error' in response_data:
            return {
                "success": False,
                "error": f"API 错误: {response_data['error']}"
            }
        
        # 提取回复内容
        # AnythingLLM 的响应格式可能包含 textResponse 或类似字段
        text_response = response_data.get('textResponse') or \
                       response_data.get('response') or \
                       response_data.get('message') or \
                       response_data.get('content')
        
        if not text_response:
            return {
                "success": True,
                "response": "API 返回了响应，但没有找到文本内容",
                "raw_data": response_data
            }
        
        return {
            "success": True,
            "response": text_response,
            "workspace": workspace_slug,
            "sources": response_data.get('sources', []),
            "raw_data": response_data
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "请求超时（60秒），请检查 AnythingLLM 服务是否正常运行"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "找不到 curl 命令，请确保 curl 已安装并添加到系统 PATH"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"查询过程中发生错误: {str(e)}"
        }


def check_anythingllm_health(base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    检查 AnythingLLM 服务是否正常运行
    
    Args:
        base_url: AnythingLLM 服务地址，默认为 http://localhost:3001
        
    Returns:
        包含健康检查结果的字典
    """
    if base_url is None:
        base_url = os.environ.get('ANYTHINGLLM_BASE_URL', 'http://localhost:3001')
    
    url = f"{base_url}/api/docs/"
    
    curl_command = [
        'curl',
        '-s',
        '-o', '/dev/null',  # 不输出响应体
        '-w', '%{http_code}',  # 只输出 HTTP 状态码
        url
    ]
    
    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        http_code = result.stdout.strip()
        
        if http_code == '200':
            return {
                "success": True,
                "status": "healthy",
                "message": "AnythingLLM 服务运行正常",
                "url": base_url
            }
        else:
            return {
                "success": False,
                "status": "unhealthy",
                "message": f"AnythingLLM 服务返回异常状态码: {http_code}",
                "url": base_url
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "status": "timeout",
            "message": "连接超时，请检查 AnythingLLM 服务是否已启动",
            "url": base_url
        }
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"健康检查失败: {str(e)}",
            "url": base_url
        }


# 工具定义，用于发送给 LLM
ANYTHINGLLM_TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "query_anythingllm",
            "description": "查询 AnythingLLM 文档仓库中的信息。当用户提到'文档仓库'、'文件仓库'、'仓库'、'知识库'或需要查询已上传文档的内容时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "要查询的问题或消息内容"
                    }
                },
                "required": ["message"]
            }
        }
    }
]


def execute_anythingllm_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行 AnythingLLM 工具
    
    Args:
        tool_name: 工具名称
        parameters: 工具参数
        
    Returns:
        工具执行结果
    """
    if tool_name == "query_anythingllm":
        message = parameters.get("message", "")
        if not message:
            return {
                "success": False,
                "error": "缺少必需的参数: message"
            }
        return query_anythingllm(message)
    else:
        return {
            "success": False,
            "error": f"未知的 AnythingLLM 工具: {tool_name}"
        }
