"""
Practice 05: 文件操作工具模块
从 Practice 03 复用，提供5个文件操作功能
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


def list_files(directory: str) -> Dict[str, Any]:
    """列出指定目录下的所有文件和文件夹"""
    try:
        if not os.path.exists(directory):
            return {"success": False, "error": f"目录不存在: {directory}"}
        
        items = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            stat = os.stat(item_path)
            
            items.append({
                "name": item,
                "path": item_path,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": stat.st_size if os.path.isfile(item_path) else None,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return {
            "success": True,
            "directory": directory,
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_file(old_path: str, new_path: str) -> Dict[str, Any]:
    """重命名文件或文件夹"""
    try:
        if not os.path.exists(old_path):
            return {"success": False, "error": f"源文件不存在: {old_path}"}
        
        if os.path.exists(new_path):
            return {"success": False, "error": f"目标路径已存在: {new_path}"}
        
        os.rename(old_path, new_path)
        return {
            "success": True,
            "message": f"已重命名: {old_path} -> {new_path}",
            "old_path": old_path,
            "new_path": new_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_file(file_path: str) -> Dict[str, Any]:
    """删除文件或文件夹"""
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"路径不存在: {file_path}"}
        
        if os.path.isdir(file_path):
            import shutil
            shutil.rmtree(file_path)
            return {
                "success": True,
                "message": f"已删除目录: {file_path}",
                "path": file_path,
                "type": "directory"
            }
        else:
            os.remove(file_path)
            return {
                "success": True,
                "message": f"已删除文件: {file_path}",
                "path": file_path,
                "type": "file"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_file(file_path: str, content: str = "") -> Dict[str, Any]:
    """创建新文件"""
    try:
        if os.path.exists(file_path):
            return {"success": False, "error": f"文件已存在: {file_path}"}
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"已创建文件: {file_path}",
            "path": file_path,
            "size": len(content)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_file(file_path: str) -> Dict[str, Any]:
    """读取文件内容"""
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"文件不存在: {file_path}"}
        
        if os.path.isdir(file_path):
            return {"success": False, "error": f"这是一个目录，不是文件: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stat = os.stat(file_path)
        return {
            "success": True,
            "path": file_path,
            "content": content,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


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
                    "directory": {"type": "string", "description": "要列出的目录路径"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "重命名文件或文件夹，将旧路径重命名为新路径",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_path": {"type": "string", "description": "原文件或文件夹路径"},
                    "new_path": {"type": "string", "description": "新文件或文件夹路径"}
                },
                "required": ["old_path", "new_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除指定的文件或文件夹。如果是文件夹，会递归删除其中的所有内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要删除的文件或文件夹路径"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "创建新文件，可以指定文件内容和路径。如果目录不存在会自动创建",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要创建的文件路径"},
                    "content": {"type": "string", "description": "文件内容", "default": ""}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文件的内容，返回文件的完整内容和元数据信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要读取的文件路径"}
                },
                "required": ["file_path"]
            }
        }
    }
]


# 工具映射表
TOOL_MAP = {
    "list_files": list_files,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "create_file": create_file,
    "read_file": read_file
}


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """根据工具名称和参数执行对应的工具函数"""
    if tool_name not in TOOL_MAP:
        return {"success": False, "error": f"未知工具: {tool_name}"}
    
    tool_func = TOOL_MAP[tool_name]
    
    try:
        result = tool_func(**parameters)
        return result
    except Exception as e:
        return {"success": False, "error": f"执行工具时出错: {str(e)}"}
