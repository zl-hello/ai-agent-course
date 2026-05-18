"""
Practice 03: 文件操作工具模块
提供5个文件操作功能，供LLM工具调用使用
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


def list_files(directory: str) -> Dict[str, Any]:
    """
    列出指定目录下的所有文件和文件夹
    
    Args:
        directory: 目标目录路径
        
    Returns:
        包含文件列表和详细信息的字典
    """
    try:
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"目录不存在: {directory}"
            }
        
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"路径不是目录: {directory}"
            }
        
        items = []
        for item_name in os.listdir(directory):
            item_path = os.path.join(directory, item_name)
            stat_info = os.stat(item_path)
            
            item_info = {
                "name": item_name,
                "path": item_path,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": stat_info.st_size if os.path.isfile(item_path) else None,
                "created": datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "permissions": oct(stat_info.st_mode)[-3:]
            }
            items.append(item_info)
        
        return {
            "success": True,
            "directory": directory,
            "count": len(items),
            "items": items
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"权限不足，无法访问目录: {directory}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"列出文件时出错: {str(e)}"
        }


def rename_file(directory: str, old_name: str, new_name: str) -> Dict[str, Any]:
    """
    重命名指定目录下的文件
    
    Args:
        directory: 文件所在目录
        old_name: 原文件名
        new_name: 新文件名
        
    Returns:
        操作结果字典
    """
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(old_path):
            return {
                "success": False,
                "error": f"文件不存在: {old_path}"
            }
        
        if os.path.exists(new_path):
            return {
                "success": False,
                "error": f"目标文件已存在: {new_path}"
            }
        
        os.rename(old_path, new_path)
        
        return {
            "success": True,
            "message": f"文件重命名成功",
            "old_path": old_path,
            "new_path": new_path
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"权限不足，无法重命名文件"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"重命名文件时出错: {str(e)}"
        }


def delete_file(directory: str, filename: str) -> Dict[str, Any]:
    """
    删除指定目录下的文件
    
    Args:
        directory: 文件所在目录
        filename: 要删除的文件名
        
    Returns:
        操作结果字典
    """
    try:
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }
        
        if os.path.isdir(file_path):
            return {
                "success": False,
                "error": f"路径是目录，不是文件: {file_path}"
            }
        
        os.remove(file_path)
        
        return {
            "success": True,
            "message": f"文件删除成功",
            "deleted_path": file_path
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"权限不足，无法删除文件"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"删除文件时出错: {str(e)}"
        }


def create_file(directory: str, filename: str, content: str) -> Dict[str, Any]:
    """
    在指定目录下创建新文件并写入内容
    
    Args:
        directory: 目标目录
        filename: 文件名
        content: 文件内容
        
    Returns:
        操作结果字典
    """
    try:
        # 确保目录存在
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_path = os.path.join(directory, filename)
        
        if os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件已存在: {file_path}"
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True,
            "message": f"文件创建成功",
            "file_path": file_path,
            "size": file_size,
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"权限不足，无法创建文件"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"创建文件时出错: {str(e)}"
        }


def read_file(directory: str, filename: str) -> Dict[str, Any]:
    """
    读取指定目录下文件的内容
    
    Args:
        directory: 文件所在目录
        filename: 文件名
        
    Returns:
        包含文件内容的字典
    """
    try:
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }
        
        if os.path.isdir(file_path):
            return {
                "success": False,
                "error": f"路径是目录，不是文件: {file_path}"
            }
        
        # 检查文件大小，避免读取过大的文件
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:  # 1MB
            return {
                "success": False,
                "error": f"文件过大 ({file_size} bytes)，无法读取"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "file_path": file_path,
            "size": file_size,
            "content": content
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"权限不足，无法读取文件"
        }
    except UnicodeDecodeError:
        return {
            "success": False,
            "error": f"文件不是文本文件，无法解码"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件时出错: {str(e)}"
        }


# 工具定义，用于发送给LLM
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出指定目录下的所有文件和文件夹，包括文件大小、创建时间、修改时间、权限等基本信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要列出的目录路径，例如: './documents' 或 'C:/Users/username/Desktop'"
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "重命名指定目录下的文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "old_name": {
                        "type": "string",
                        "description": "原文件名"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "新文件名"
                    }
                },
                "required": ["directory", "old_name", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除指定目录下的文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "filename": {
                        "type": "string",
                        "description": "要删除的文件名"
                    }
                },
                "required": ["directory", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "在指定目录下创建新文件并写入内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "要创建文件的目录路径"
                    },
                    "filename": {
                        "type": "string",
                        "description": "新文件的名称"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入文件的内容"
                    }
                },
                "required": ["directory", "filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定目录下文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "文件所在的目录路径"
                    },
                    "filename": {
                        "type": "string",
                        "description": "要读取的文件名"
                    }
                },
                "required": ["directory", "filename"]
            }
        }
    }
]


# 工具映射表，用于根据函数名调用对应功能
TOOL_MAP = {
    "list_files": list_files,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "create_file": create_file,
    "read_file": read_file
}


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据工具名称和参数执行对应的工具函数
    
    Args:
        tool_name: 工具名称
        parameters: 工具参数
        
    Returns:
        工具执行结果
    """
    if tool_name not in TOOL_MAP:
        return {
            "success": False,
            "error": f"未知工具: {tool_name}"
        }
    
    tool_func = TOOL_MAP[tool_name]
    
    try:
        result = tool_func(**parameters)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"执行工具时出错: {str(e)}"
        }


if __name__ == "__main__":
    # 测试工具函数
    print("=" * 60)
    print("测试文件工具模块")
    print("=" * 60)
    
    test_dir = "./test_files"
    
    # 测试1: 创建文件
    print("\n1. 创建文件测试:")
    result = create_file(test_dir, "test.txt", "这是一个测试文件的内容。\n第二行内容。")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试2: 列出文件
    print("\n2. 列出文件测试:")
    result = list_files(test_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试3: 读取文件
    print("\n3. 读取文件测试:")
    result = read_file(test_dir, "test.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试4: 重命名文件
    print("\n4. 重命名文件测试:")
    result = rename_file(test_dir, "test.txt", "renamed_test.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试5: 删除文件
    print("\n5. 删除文件测试:")
    result = delete_file(test_dir, "renamed_test.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
