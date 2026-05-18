"""
Practice 06: 带技能管理的 AI Agent
基于 Practice 05，实现：
1. 自动读取 agents/skills 目录下的技能列表
2. 解析 SKILL.md 文件的 YAML frontmatter
3. 当 LLM 判断需要使用某个技能时，自动加载该技能内容到 system prompt
"""

import json
import os
import sys
import signal
import re
import io
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime

# 设置 stdout 和 stderr 为 UTF-8 编码（解决 Windows 控制台乱码问题）
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 尝试导入 requests，如果不可用则使用 urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

# 添加当前目录到路径（确保能导入同级模块）
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入技能管理模块
from skills_manager import (
    list_available_skills, 
    format_skills_for_prompt,
    format_skills_as_json,
    load_skill_content,
    SKILL_TOOLS_DEFINITION,
    execute_skill_tool
)


# 全局变量用于控制程序退出
running = True


def signal_handler(sig, frame):
    """处理Ctrl+C信号，优雅退出"""
    global running
    print("\n\n[再见] 再见！")
    running = False
    sys.exit(0)


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """读取.env文件并解析为字典"""
    env_vars = {}
    
    # 尝试多个路径查找 .env 文件
    possible_paths = [
        env_path,  # 当前目录
        os.path.join(os.path.dirname(os.path.abspath(__file__)), env_path),  # 脚本所在目录
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), env_path),  # 上级目录
    ]
    
    found_path = None
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            break
    
    if not found_path:
        raise FileNotFoundError(f"找不到.env文件。已查找路径:\n" + 
                               "\n".join([f"  - {os.path.abspath(p)}" for p in possible_paths]))
    
    with open(found_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')
    
    return env_vars


def create_llm_request(messages: List[Dict[str, str]], 
                       model: str,
                       api_key: str,
                       base_url: str,
                       tools: Optional[List[Dict]] = None,
                       stream: bool = True) -> Dict[str, Any]:
    """构建LLM API请求体"""
    parsed = urlparse(base_url)
    host = parsed.netloc
    
    if '/v1' in parsed.path and not parsed.path.endswith('/chat/completions'):
        path = parsed.path.rstrip('/') + "/chat/completions"
    elif parsed.path:
        path = parsed.path
    else:
        path = "/v1/chat/completions"
    
    request_body = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    if tools:
        request_body["tools"] = tools
        request_body["tool_choice"] = "auto"
    
    return {
        "host": host,
        "path": path,
        "api_key": api_key,
        "body": request_body
    }


def stream_llm_response(request_config: Dict[str, Any]) -> Generator[str, None, None]:
    """流式调用LLM API"""
    host = request_config["host"]
    path = request_config["path"]
    api_key = request_config["api_key"]
    body = request_config["body"]
    
    protocol = "https" if host.endswith(':443') or 'https' in host else "http"
    clean_host = host.replace(':443', '').replace('https://', '').replace('http://', '')
    url = f"{protocol}://{clean_host}{path}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    if api_key and api_key != 'sk-no-key-needed':
        headers["Authorization"] = f"Bearer {api_key}"
    
    if HAS_REQUESTS:
        try:
            response = requests.post(
                url,
                json=body,
                headers=headers,
                stream=True,
                timeout=30,
                allow_redirects=False
            )
            
            if response.status_code in (301, 302, 307, 308):
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    response = requests.post(
                        redirect_url,
                        json=body,
                        headers=headers,
                        stream=True,
                        timeout=30
                    )
            
            if response.status_code == 403:
                error_msg = "API 访问被拒绝 (HTTP 403)。可能原因:\n"
                error_msg += "  1. API 密钥无效或已过期\n"
                error_msg += "  2. 账户余额不足\n"
                error_msg += "  3. 请求频率限制\n"
                error_msg += "  4. 模型不可用或需要额外权限\n"
                error_msg += f"\n请检查 .env 文件中的 API 配置，或尝试使用其他模型。"
                raise Exception(error_msg)
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8', errors='replace').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        
                        if data == '[DONE]':
                            return
                        
                        try:
                            json_data = json.loads(data)
                            delta = json_data.get('choices', [{}])[0].get('delta', {})
                            
                            if 'tool_calls' in delta:
                                yield json.dumps({"tool_calls": delta['tool_calls']})
                            
                            content = delta.get('content', '')
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求错误: {e}")
    else:
        import urllib.request
        from urllib.error import HTTPError
        
        max_redirects = 5
        redirect_count = 0
        current_url = url
        
        while redirect_count < max_redirects:
            req = urllib.request.Request(
                current_url,
                data=json.dumps(body).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            response = None
            try:
                response = urllib.request.urlopen(req, timeout=30)
                break
                
            except HTTPError as e:
                if e.code in (301, 302, 307, 308):
                    redirect_url = e.headers.get('Location')
                    if redirect_url:
                        current_url = redirect_url
                        redirect_count += 1
                        continue
                    else:
                        raise Exception(f"HTTP Error {e.code}: 重定向但没有 Location 头")
                else:
                    error_body = e.read().decode('utf-8')
                    raise Exception(f"API错误 (HTTP {e.code}): {error_body}")
        
        if response is None:
            raise Exception(f"达到最大重定向次数 ({max_redirects})")
        
        try:
            buffer = b""
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                
                buffer += chunk
                
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    line = line.decode('utf-8', errors='replace').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        
                        if data == '[DONE]':
                            return
                        
                        try:
                            json_data = json.loads(data)
                            delta = json_data.get('choices', [{}])[0].get('delta', {})
                            
                            if 'tool_calls' in delta:
                                yield json.dumps({"tool_calls": delta['tool_calls']})
                            
                            content = delta.get('content', '')
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue
        finally:
            response.close()


def non_stream_llm_response(request_config: Dict[str, Any]) -> Dict[str, Any]:
    """非流式调用LLM API"""
    host = request_config["host"]
    path = request_config["path"]
    api_key = request_config["api_key"]
    body = request_config["body"]
    
    body["stream"] = False
    
    protocol = "https" if host.endswith(':443') or 'https' in host else "http"
    clean_host = host.replace(':443', '').replace('https://', '').replace('http://', '')
    url = f"{protocol}://{clean_host}{path}"
    
    headers = {"Content-Type": "application/json"}
    
    if api_key and api_key != 'sk-no-key-needed':
        headers["Authorization"] = f"Bearer {api_key}"
    
    if HAS_REQUESTS:
        try:
            response = requests.post(
                url,
                json=body,
                headers=headers,
                timeout=30,
                allow_redirects=False
            )
            
            if response.status_code == 403:
                error_msg = "API 访问被拒绝 (HTTP 403)。可能原因:\n"
                error_msg += "  1. API 密钥无效或已过期\n"
                error_msg += "  2. 账户余额不足\n"
                error_msg += "  3. 请求频率限制\n"
                error_msg += "  4. 模型不可用或需要额外权限\n"
                error_msg += f"\n请检查 .env 文件中的 API 配置，或尝试使用其他模型。"
                raise Exception(error_msg)
            
            if response.status_code in (301, 302, 307, 308):
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    response = requests.post(
                        redirect_url,
                        json=body,
                        headers=headers,
                        timeout=30
                    )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求错误: {e}")
    else:
        import urllib.request
        from urllib.error import HTTPError
        
        max_redirects = 5
        redirect_count = 0
        current_url = url
        
        while redirect_count < max_redirects:
            req = urllib.request.Request(
                current_url,
                data=json.dumps(body).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            response = None
            try:
                response = urllib.request.urlopen(req, timeout=30)
                break
                
            except HTTPError as e:
                if e.code in (301, 302, 307, 308):
                    redirect_url = e.headers.get('Location')
                    if redirect_url:
                        current_url = redirect_url
                        redirect_count += 1
                        continue
                    else:
                        raise Exception(f"HTTP Error {e.code}: 重定向但没有 Location 头")
                else:
                    error_body = e.read().decode('utf-8')
                    raise Exception(f"API错误 (HTTP {e.code}): {error_body}")
        
        if response is None:
            raise Exception(f"达到最大重定向次数 ({max_redirects})")
        
        try:
            result = json.loads(response.read().decode('utf-8'))
            return result
        finally:
            response.close()


class SkillsAgent:
    """带技能管理功能的 AI Agent"""
    
    def __init__(self, env_vars: Dict[str, str]):
        self.env_vars = env_vars
        self.model = env_vars.get('LLM_MODEL') or env_vars.get('MODEL_NAME', 'gpt-3.5-turbo')
        self.api_key = env_vars.get('LLM_API_KEY') or env_vars.get('OPENAI_API_KEY', 'sk-no-key-needed')
        self.base_url = env_vars.get('LLM_BASE_URL') or env_vars.get('BASE_URL', 'https://api.openai.com/v1')
        
        self.is_local_model = 'localhost' in self.base_url or '127.0.0.1' in self.base_url or ':11434' in self.base_url
        
        if not self.is_local_model and not env_vars.get('LLM_API_KEY') and not env_vars.get('OPENAI_API_KEY'):
            raise ValueError("LLM_API_KEY 未在.env中配置")
        
        # 初始化对话历史
        self.conversation_history = []
        
        # 加载可用技能
        print("[系统] 正在加载技能列表...")
        self.available_skills = list_available_skills()
        print(f"[系统] 已加载 {len(self.available_skills)} 个技能\n")
        
        # 当前激活的技能内容
        self.active_skill_content = None
        self.active_skill_name = None
        
        # 构建基础系统提示词
        self.base_system_prompt = self._build_base_system_prompt()
        self._init_conversation()
        
        # 工具定义
        self.tools = SKILL_TOOLS_DEFINITION
    
    def _build_base_system_prompt(self) -> str:
        """构建基础系统提示词（包含JSON格式的技能列表）"""
        base_prompt = """你是一个智能助手，具备多种技能能力。

## 可用技能列表（JSON格式）

"""
        # 添加 JSON 格式的技能列表
        if self.available_skills:
            skills_json = format_skills_as_json(self.available_skills)
            base_prompt += f"```json\n{skills_json}\n```\n"
        else:
            base_prompt += "```json\n{\"skills\": []}\n```\n"
        
        base_prompt += """
## 技能使用规则

1. **分析用户需求**：根据用户的输入，判断是否需要使用某个技能
2. **触发词识别**：每个技能都有特定的触发词，例如：
   - "写通知"、"撰写通知" → 触发 notice 技能
   - "搜索"、"查找" → 触发 web_search 技能
   - "分析代码"、"检查代码" → 触发 code_analysis 技能
3. **自动加载技能**：当判断需要使用某个技能时，系统会自动加载该技能的完整内容到提示词中
4. **严格遵循技能规范**：加载技能内容后，必须严格按照技能文档中的规则执行

## 工具说明

1. **list_available_skills**: 列出所有可用的技能
   - 当用户询问"你有什么技能"、"你能做什么"等问题时调用

2. **load_skill_content**: 加载指定技能的完整内容
   - 当需要详细了解某个技能的具体功能和使用方法时调用
   - 参数: skill_name (技能名称)

请根据用户的需求，选择合适的技能来帮助完成任务。"""
        
        return base_prompt
    
    def _build_full_system_prompt(self) -> str:
        """构建完整的系统提示词（基础提示词 + 激活的技能内容）"""
        prompt = self.base_system_prompt
        
        # 如果有激活的技能，添加技能内容
        if self.active_skill_content and self.active_skill_name:
            prompt += f"""

## 当前激活技能: {self.active_skill_name}

以下内容是你必须严格遵循的技能规范：

{self.active_skill_content}

---
**重要**: 以上是你当前必须遵循的技能规范。请严格按照上述规则执行任务。
"""
        
        return prompt
    
    def _update_system_prompt(self):
        """更新对话历史中的 system prompt"""
        full_prompt = self._build_full_system_prompt()
        
        # 更新或添加 system 消息
        if self.conversation_history and self.conversation_history[0].get('role') == 'system':
            self.conversation_history[0]['content'] = full_prompt
        else:
            self.conversation_history.insert(0, {'role': 'system', 'content': full_prompt})
    
    def _detect_skill_from_input(self, user_input: str) -> Optional[str]:
        """
        从用户输入中检测可能需要使用的技能
        
        Args:
            user_input: 用户输入
            
        Returns:
            技能名称，如果未检测到则返回 None
        """
        user_input_lower = user_input.lower()
        
        # 定义技能触发词映射
        skill_triggers = {
            'notice': ['写通知', '撰写通知', '修改通知', '润色通知', '通知怎么写', '帮我写个通知', '通知'],
            'file_operations': ['列出文件', '创建文件', '读取文件', '删除文件', '重命名文件', '文件操作'],
            'web_search': ['搜索', '查找', '查询', '网上搜索', 'google', '百度'],
            'code_analysis': ['分析代码', '检查代码', '代码审查', 'code review', '优化代码']
        }
        
        for skill_name, triggers in skill_triggers.items():
            for trigger in triggers:
                if trigger in user_input_lower:
                    # 检查技能是否存在
                    for skill in self.available_skills:
                        if skill['name'] == skill_name:
                            return skill_name
        
        return None
    
    def _load_skill(self, skill_name: str) -> bool:
        """
        加载指定技能的内容
        
        Args:
            skill_name: 技能名称
            
        Returns:
            是否成功加载
        """
        result = load_skill_content(skill_name)
        
        if result.get('success'):
            self.active_skill_name = skill_name
            self.active_skill_content = result.get('content', '')
            self._update_system_prompt()
            print(f"[系统] 已加载技能: {skill_name}")
            return True
        else:
            print(f"[警告] 加载技能失败: {result.get('error')}")
            return False
    
    def _init_conversation(self):
        """初始化对话历史"""
        full_prompt = self._build_full_system_prompt()
        self.conversation_history = [
            {'role': 'system', 'content': full_prompt}
        ]
    
    def _should_list_skills(self, user_input: str) -> bool:
        """判断是否应该列出技能"""
        skill_keywords = [
            '有什么技能', '你能做什么', '你会什么', '可用功能',
            '有什么功能', '支持什么', '技能列表', '能力列表'
        ]
        
        user_input_lower = user_input.lower()
        for keyword in skill_keywords:
            if keyword in user_input_lower:
                return True
        
        return False
    
    def _execute_tool_calls(self, tool_calls: List[Dict]) -> List[Dict]:
        """执行工具调用"""
        results = []
        
        for tool_call in tool_calls:
            function_info = tool_call.get('function', {})
            tool_name = function_info.get('name')
            arguments_str = function_info.get('arguments', '{}')
            
            try:
                parameters = json.loads(arguments_str)
            except json.JSONDecodeError:
                parameters = {}
            
            print(f"  📋 执行: {tool_name}")
            
            # 执行技能工具
            result = execute_skill_tool(tool_name, parameters)
            
            if result.get('success'):
                print(f"  ✅ 成功")
                
                # 如果是加载技能内容，同时更新 system prompt
                if tool_name == 'load_skill_content' and parameters.get('skill_name'):
                    skill_name = parameters['skill_name']
                    self._load_skill(skill_name)
            else:
                print(f"  ❌ 失败: {result.get('error')}")
            
            results.append({
                "tool_call_id": tool_call.get('id'),
                "result": result
            })
        
        return results
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入并返回响应"""
        # 检查是否应该列出技能
        if self._should_list_skills(user_input):
            formatted_skills = format_skills_for_prompt(self.available_skills)
            response_content = f"以下是我可用的技能：\n\n{formatted_skills}"
            
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_content})
            
            return {
                "content": response_content,
                "history_length": len(self.conversation_history)
            }
        
        # 检测是否需要加载技能
        detected_skill = self._detect_skill_from_input(user_input)
        if detected_skill:
            if detected_skill != self.active_skill_name:
                print(f"[系统] 检测到可能需要使用技能: {detected_skill}")
                self._load_skill(detected_skill)
        
        # 普通对话流程
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 构建请求
        request_config = create_llm_request(
            messages=self.conversation_history,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            tools=self.tools,
            stream=True
        )
        
        # 收集完整响应
        full_response = ""
        tool_calls_buffer = []
        
        # 流式获取响应
        for chunk in stream_llm_response(request_config):
            try:
                chunk_data = json.loads(chunk)
                if isinstance(chunk_data, dict) and 'tool_calls' in chunk_data:
                    tool_calls_buffer.extend(chunk_data['tool_calls'])
                    continue
            except (json.JSONDecodeError, TypeError):
                pass
            
            print(chunk, end="", flush=True)
            full_response += chunk
        
        # 处理工具调用
        if tool_calls_buffer:
            print(f"\n[工具] 检测到 {len(tool_calls_buffer)} 个工具调用")
            
            assistant_msg = {
                "role": "assistant",
                "content": full_response if full_response else None,
                "tool_calls": tool_calls_buffer
            }
            self.conversation_history.append(assistant_msg)
            
            # 执行工具
            tool_results = self._execute_tool_calls(tool_calls_buffer)
            
            # 添加工具结果到历史
            for result in tool_results:
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": json.dumps(result["result"], ensure_ascii=False)
                })
            
            # 第二次调用获取最终响应
            print("\n[AI] ", end="", flush=True)
            
            second_request = create_llm_request(
                messages=self.conversation_history,
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                stream=True
            )
            
            final_response = ""
            for chunk in stream_llm_response(second_request):
                print(chunk, end="", flush=True)
                final_response += chunk
            
            full_response = final_response
        
        # 添加助手回复到历史
        if full_response:
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
        
        return {
            "content": full_response,
            "history_length": len(self.conversation_history)
        }
    
    def clear_history(self):
        """清空对话历史"""
        # 重置激活的技能
        self.active_skill_content = None
        self.active_skill_name = None
        self._init_conversation()
        print("\n🗑️  对话历史已清空，技能状态已重置")
    
    def get_history_summary(self) -> str:
        """获取历史记录摘要"""
        user_msg_count = sum(1 for m in self.conversation_history if m.get('role') == 'user')
        assistant_msg_count = sum(1 for m in self.conversation_history if m.get('role') == 'assistant')
        active_skill = f" | 当前技能: {self.active_skill_name}" if self.active_skill_name else ""
        return f"历史: {user_msg_count} 用户消息, {assistant_msg_count} AI回复{active_skill}"
    
    def _generate_mock_response(self, user_input: str) -> str:
        """生成模拟响应（用于 API 不可用时演示功能）"""
        # 如果当前有激活的技能，根据技能生成响应
        if self.active_skill_name == 'notice':
            # 检测用户是否指定了部门
            import re
            dept_match = re.search(r'(\w+部)', user_input)
            if dept_match:
                dept = dept_match.group(1)
            else:
                dept = "XX部"
            
            return f"""{dept}通知

各位同事：

根据国家法定节假日安排，现将五一劳动节放假事宜通知如下：

一、放假时间：5月1日至5月5日，共5天
二、上班时间：5月6日（星期一）正常上班
三、注意事项：
   1. 请各部门做好节前安全检查
   2. 值班人员请保持通讯畅通
   3. 外出请注意安全

{dept}
2024年5月1日

---
(这是模拟响应，用于演示 notice 技能功能)
实际使用时请配置有效的 API 密钥。"""
        
        # 默认响应
        return f"""我收到了你的消息："{user_input}"

当前激活技能: {self.active_skill_name or '无'}

(这是模拟响应，用于演示功能。实际使用时请配置有效的 API 密钥。)"""


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🎯 Practice 06: 技能管理 Agent")
    print("=" * 60)
    print("\n⚠️  重要提示:")
    print("   请先运行 Python 程序，然后在程序提示符下输入！")
    print("   不要在 PowerShell/终端命令行直接输入中文！")
    print("\n功能特点:")
    print("  - 自动读取 agents/skills 目录下的技能")
    print("  - 解析 SKILL.md 文件的 YAML frontmatter")
    print("  - 自动检测并加载匹配的技能")
    print("  - 将技能内容注入 system prompt")
    print("\n命令:")
    print("  /clear  - 清空对话历史")
    print("  /history- 查看历史记录")
    print("  /skills - 显示技能列表")
    print("  /skill  - 显示当前激活的技能")
    print("  /exit   - 退出程序")
    print("  Ctrl+C  - 强制退出")
    print("\n" + "-" * 60)


def main():
    """主函数"""
    print_banner()
    
    try:
        # 加载配置
        env_vars = load_env_file()
        agent = SkillsAgent(env_vars)
        
        print(f"✅ 已连接到: {env_vars.get('LLM_MODEL', 'unknown')}")
        print(f"📊 {agent.get_history_summary()}")
        print("-" * 60)
        print("\n💡 提示: 输入 '/exit' 退出，'/skills' 查看技能列表")
        print("   示例: '帮我写个关于五一放假的通知'\n")
        
        while running:
            try:
                # 获取用户输入
                user_input = input("👤 你: ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input == '/exit':
                    print("\n👋 再见！")
                    break
                
                if user_input == '/clear':
                    agent.clear_history()
                    continue
                
                if user_input == '/history':
                    print("\n📜 对话历史:")
                    for i, msg in enumerate(agent.conversation_history[1:], 1):
                        role = "👤" if msg.get('role') == 'user' else "🤖"
                        content = msg.get('content', '')
                        if content:
                            print(f"{role} {content[:100]}{'...' if len(content) > 100 else ''}")
                    print()
                    continue
                
                if user_input == '/skills':
                    print("\n📋 可用技能列表:")
                    print(format_skills_for_prompt(agent.available_skills))
                    continue
                
                if user_input == '/skill':
                    if agent.active_skill_name:
                        print(f"\n🔧 当前激活技能: {agent.active_skill_name}")
                        if agent.active_skill_content:
                            preview = agent.active_skill_content[:300]
                            print(f"内容预览:\n{preview}...")
                    else:
                        print("\n🔧 当前没有激活的技能")
                    continue
                
                # 发送消息
                print("🤖 AI: ", end="", flush=True)
                
                try:
                    result = agent.chat(user_input)
                    if not result['content']:
                        print("(无响应)")
                except Exception as e:
                    error_str = str(e)
                    print(f"\n❌ 错误: {error_str}")
                    
                    # 如果是 API 错误，提供模拟响应选项
                    if "API" in error_str or "HTTP" in error_str:
                        print("\n💡 检测到 API 错误，是否使用模拟响应演示功能？(y/n)")
                        try:
                            choice = input("> ").strip().lower()
                            if choice == 'y':
                                # 生成模拟响应
                                mock_response = agent._generate_mock_response(user_input)
                                print(f"\n🤖 AI (模拟): {mock_response}")
                                agent.conversation_history.append({
                                    "role": "assistant",
                                    "content": mock_response
                                })
                        except:
                            pass
                    continue
                
                print()
                
            except EOFError:
                print("\n👋 再见！")
                break
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
                
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}")
        print("\n请按照以下步骤操作:")
        print("1. 复制 env.example 为 .env")
        print("2. 在 .env 中填入你的API密钥")
        print("3. 再次运行此脚本")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
