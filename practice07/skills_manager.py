"""
Practice 06: 技能管理模块
提供读取和管理 Agent 技能的功能
"""

import json
import os
import re
from typing import Dict, Any, List, Optional


def parse_yaml_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """
    解析 Markdown 文件中的 YAML frontmatter
    
    Args:
        content: 文件内容
        
    Returns:
        解析后的 frontmatter 字典，如果没有则返回 None
    """
    # 匹配 --- 开头和结尾的 YAML frontmatter
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    yaml_content = match.group(1)
    frontmatter = {}
    
    # 解析简单的 key: value 格式
    for line in yaml_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 匹配 key: value 格式
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # 处理列表格式 [item1, item2]
            if value.startswith('[') and value.endswith(']'):
                # 移除方括号并分割
                list_content = value[1:-1]
                value = [item.strip().strip('"\'') for item in list_content.split(',')]
            else:
                # 移除引号
                value = value.strip('"\'')
            
            frontmatter[key] = value
    
    return frontmatter


def read_skill_md(skill_dir: str) -> Optional[Dict[str, Any]]:
    """
    读取技能目录中的 SKILL.md 文件
    
    Args:
        skill_dir: 技能目录路径
        
    Returns:
        包含技能信息的字典，如果读取失败则返回 None
    """
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    
    if not os.path.exists(skill_md_path):
        return None
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 YAML frontmatter
        frontmatter = parse_yaml_frontmatter(content)
        
        if not frontmatter:
            return None
        
        # 提取 name 和 description
        skill_info = {
            'directory': os.path.basename(skill_dir),
            'path': skill_dir,
            'name': frontmatter.get('name', 'unknown'),
            'description': frontmatter.get('description', ''),
            'version': frontmatter.get('version', '1.0.0'),
            'author': frontmatter.get('author', 'unknown'),
            'tags': frontmatter.get('tags', [])
        }
        
        return skill_info
        
    except Exception as e:
        print(f"[错误] 读取技能文件失败 {skill_md_path}: {e}")
        return None


def list_available_skills(skills_base_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    列出所有可用的技能
    
    自动读取 agents/skills 目录下的所有一级子目录，
    读取每个子目录内 SKILL.md 文件的 YAML frontmatter，
    提取 name 和 description 字段。
    
    Args:
        skills_base_dir: 技能基础目录，默认为项目根目录下的 agents/skills
        
    Returns:
        技能信息列表
    """
    if skills_base_dir is None:
        # 默认路径：项目根目录/agents/skills
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        skills_base_dir = os.path.join(project_root, 'agents', 'skills')
    
    skills = []
    
    # 检查目录是否存在
    if not os.path.exists(skills_base_dir):
        print(f"[警告] 技能目录不存在: {skills_base_dir}")
        return skills
    
    if not os.path.isdir(skills_base_dir):
        print(f"[警告] 技能目录路径不是目录: {skills_base_dir}")
        return skills
    
    # 遍历所有一级子目录
    try:
        for item in os.listdir(skills_base_dir):
            item_path = os.path.join(skills_base_dir, item)
            
            # 只处理目录
            if os.path.isdir(item_path):
                skill_info = read_skill_md(item_path)
                
                if skill_info:
                    skills.append(skill_info)
                    print(f"[技能] 加载成功: {skill_info['name']} - {skill_info['description'][:50]}...")
                else:
                    print(f"[警告] 无法读取技能: {item}")
    
    except Exception as e:
        print(f"[错误] 读取技能目录失败: {e}")
    
    return skills


def get_skill_by_name(skill_name: str, skills_base_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    根据名称获取技能信息
    
    Args:
        skill_name: 技能名称
        skills_base_dir: 技能基础目录
        
    Returns:
        技能信息字典，如果未找到则返回 None
    """
    skills = list_available_skills(skills_base_dir)
    
    for skill in skills:
        if skill['name'] == skill_name:
            return skill
    
    return None


def format_skills_for_prompt(skills: List[Dict[str, Any]]) -> str:
    """
    将技能列表格式化为提示词
    
    Args:
        skills: 技能信息列表
        
    Returns:
        格式化后的提示词字符串
    """
    if not skills:
        return "当前没有可用的技能。"
    
    prompt = "## 可用技能列表\n\n"
    
    for i, skill in enumerate(skills, 1):
        prompt += f"{i}. **{skill['name']}** (v{skill['version']})\n"
        prompt += f"   - 描述: {skill['description']}\n"
        if skill['tags']:
            prompt += f"   - 标签: {', '.join(skill['tags'])}\n"
        prompt += "\n"
    
    return prompt


def format_skills_as_json(skills: List[Dict[str, Any]]) -> str:
    """
    将技能列表格式化为 JSON 字符串，用于 system prompt
    
    Args:
        skills: 技能信息列表
        
    Returns:
        JSON 格式的技能列表字符串
    """
    # 只保留 name 和 description 字段
    skills_json = [
        {
            "name": skill['name'],
            "description": skill['description']
        }
        for skill in skills
    ]
    
    return json.dumps({"skills": skills_json}, ensure_ascii=False, indent=2)


def load_skill_content(skill_name: str, skills_base_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    加载技能的完整内容（包括正文）
    
    当 LLM 判断需要使用某个技能时，通过此函数加载该技能的完整内容。
    
    Args:
        skill_name: 技能名称
        skills_base_dir: 技能基础目录
        
    Returns:
        包含技能完整信息的字典
    """
    if skills_base_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        skills_base_dir = os.path.join(project_root, 'agents', 'skills')
    
    # 查找技能目录
    skill_dir = None
    try:
        for item in os.listdir(skills_base_dir):
            item_path = os.path.join(skills_base_dir, item)
            if os.path.isdir(item_path):
                # 读取 SKILL.md 检查名称
                skill_info = read_skill_md(item_path)
                if skill_info and skill_info['name'] == skill_name:
                    skill_dir = item_path
                    break
    except Exception as e:
        return {
            "success": False,
            "error": f"查找技能失败: {e}"
        }
    
    if not skill_dir:
        return {
            "success": False,
            "error": f"未找到技能: {skill_name}"
        }
    
    # 读取完整内容
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
        
        # 解析 frontmatter
        frontmatter = parse_yaml_frontmatter(full_content)
        
        # 提取正文（frontmatter 之后的内容）
        pattern = r'^---\s*\n.*?\n---\s*\n'
        body_content = re.sub(pattern, '', full_content, count=1, flags=re.DOTALL).strip()
        
        return {
            "success": True,
            "name": skill_name,
            "directory": os.path.basename(skill_dir),
            "frontmatter": frontmatter,
            "content": body_content,
            "full_content": full_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"读取技能内容失败: {e}"
        }


# 工具定义，用于发送给 LLM
SKILL_TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "list_available_skills",
            "description": "列出所有可用的技能。当用户询问'你有什么技能'、'你能做什么'、'可用功能'等问题时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill_content",
            "description": "加载指定技能的完整内容（包括正文）。当需要详细了解某个技能的具体功能和使用方法时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "要加载的技能名称"
                    }
                },
                "required": ["skill_name"]
            }
        }
    }
]


def execute_skill_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行技能相关工具
    
    Args:
        tool_name: 工具名称
        parameters: 工具参数
        
    Returns:
        工具执行结果
    """
    if tool_name == "list_available_skills":
        skills = list_available_skills()
        return {
            "success": True,
            "skills": skills,
            "count": len(skills),
            "formatted": format_skills_for_prompt(skills)
        }
    elif tool_name == "load_skill_content":
        skill_name = parameters.get("skill_name")
        if not skill_name:
            return {
                "success": False,
                "error": "缺少 skill_name 参数"
            }
        result = load_skill_content(skill_name)
        if result.get("success"):
            return {
                "success": True,
                "skill_name": result["name"],
                "frontmatter": result["frontmatter"],
                "content_preview": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
            }
        return result
    else:
        return {
            "success": False,
            "error": f"未知的技能工具: {tool_name}"
        }


if __name__ == "__main__":
    # 测试技能管理功能
    print("=" * 60)
    print("测试技能管理模块")
    print("=" * 60)
    
    # 测试列出所有技能
    print("\n1. 列出所有可用技能:")
    skills = list_available_skills()
    print(f"\n找到 {len(skills)} 个技能")
    
    for skill in skills:
        print(f"\n- {skill['name']} (v{skill['version']})")
        print(f"  描述: {skill['description']}")
        print(f"  作者: {skill['author']}")
        print(f"  标签: {', '.join(skill['tags'])}")
    
    # 测试格式化输出
    print("\n" + "=" * 60)
    print("2. 格式化技能列表:")
    print("=" * 60)
    print(format_skills_for_prompt(skills))
    
    # 测试执行工具
    print("=" * 60)
    print("3. 测试工具执行:")
    print("=" * 60)
    result = execute_skill_tool("list_available_skills", {})
    print(f"成功: {result['success']}")
    print(f"技能数量: {result['count']}")
