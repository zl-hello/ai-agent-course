"""
Practice 07: 链式工具调用 AI Agent
基于 Practice 06，实现：
1. 链式工具调用（Chained Tool Calls）
2. 前一个工具的输出作为后一个工具的输入参数
3. LLM 能够根据中间结果自主决定下一步工具调用
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

# 导入链式工具模块
from chained_tools import (
    ChainedCallContext,
    CHAINED_TOOLS_DEFINITION,
    execute_chained_tool_call
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
    
    # 处理不同 API 的路径格式
    if parsed.path.endswith('/chat/completions'):
        # 路径已经包含完整的 endpoint
        path = parsed.path
    elif '/v1' in parsed.path:
        # 路径包含 /v1 但没有 /chat/completions
        path = parsed.path.rstrip('/') + "/chat/completions"
    elif parsed.path:
        # 有其他路径，追加 chat/completions
        path = parsed.path.rstrip('/') + "/chat/completions"
    else:
        # 默认路径
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
        
        # OpenRouter 需要额外的 HTTP 头
        if 'openrouter.ai' in host:
            headers["HTTP-Referer"] = "https://localhost"
            headers["X-Title"] = "Practice 07 Agent"
    
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
            
            if response.status_code == 400:
                error_body = response.text[:500]
                error_msg = f"API 请求格式错误 (HTTP 400)。\n"
                error_msg += f"响应内容: {error_body}\n"
                error_msg += "可能原因:\n"
                error_msg += "  1. 模型名称格式不正确\n"
                error_msg += "  2. 请求参数不符合 API 要求\n"
                error_msg += "  3. 该模型需要额外的请求头或参数\n"
                raise Exception(error_msg)
            
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
        
        # OpenRouter 需要额外的 HTTP 头
        if 'openrouter.ai' in host:
            headers["HTTP-Referer"] = "https://localhost"
            headers["X-Title"] = "Practice 07 Agent"
    
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
        
        # 解析 host
        from urllib.parse import urlparse
        parsed = urlparse(self.base_url)
        self.host = parsed.netloc
        
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
        
        # 工具定义（合并技能工具和链式工具）
        self.tools = SKILL_TOOLS_DEFINITION + CHAINED_TOOLS_DEFINITION
    
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

### 技能管理工具
1. **list_available_skills**: 列出所有可用的技能
   - 当用户询问"你有什么技能"、"你能做什么"等问题时调用

2. **load_skill_content**: 加载指定技能的完整内容
   - 当需要详细了解某个技能的具体功能和使用方法时调用
   - 参数: skill_name (技能名称)

### 链式工具调用（Chained Tool Calls）
3. **execute_chained_tool_call**: 执行链式工具调用
   
   **适用场景**：当用户需要多步骤处理时使用，例如：
   - "分析目录并读取文件"
   - "搜索历史并总结"
   - "查找包含关键词的文件并总结内容"
   - "读取多个文件并进行计算"
   
   **工具调用顺序依赖关系**：
   - 链式调用中，工具之间存在顺序依赖
   - 前一个工具的输出结果会作为后一个工具的输入参数
   - 必须等待前一个工具执行完成后，才能执行下一个工具
   
   **如何根据中间结果决定后续操作**：
   1. 分析已执行工具的返回结果
   2. 判断是否已获得足够信息完成任务
   3. 如果信息不足，决定下一个需要调用的工具
   4. 从上一个结果中提取必要参数传递给下一个工具
   
   **上下文变量使用方式**：
   - 每个工具的执行结果会存储在上下文中
   - 变量命名格式：`{tool_name}_result`
   - 例如：`list_files_result`、`read_file_result`
   - 后续工具可以通过变量名引用之前的结果
   
   **链式调用示例**：
   
   *示例1：分析目录并读取文件*
   ```
   用户：分析 practice07 目录并读取 README 文件
   
   步骤1: list_files(directory="practice07")
          → 返回: ["README.md", "agent.py", "chained_tools.py"]
   
   步骤2: read_file(directory="practice07", filename="README.md")
          → 使用步骤1的结果，读取 README.md
          → 返回: 文件内容
   
   步骤3: 任务完成，返回文件内容摘要
   ```
   
   *示例2：搜索并总结*
   ```
   用户：搜索历史关于通知的内容并总结
   
   步骤1: search_chat_history(query="通知")
          → 返回: [{role:"user", content:"帮我写个通知"}, ...]
   
   步骤2: generate_summary(content=搜索结果)
          → 使用步骤1的 results 作为输入
          → 返回: 摘要内容
   
   步骤3: 任务完成，返回摘要
   ```
   
   *示例3：多文件操作*
   ```
   用户：读取两个文件并计算和
   
   步骤1: read_file(filename="1.txt")
          → 返回: content="100"
   
   步骤2: read_file(filename="2.txt")
          → 返回: content="200"
   
   步骤3: 计算 100 + 200 = 300
   
   步骤4: write_file(filename="result.txt", content="300")
          → 返回: 写入成功
   
   步骤5: 任务完成
   ```
   
   **参数说明**:
   - user_request: 用户的完整请求描述
   - max_iterations: 最大迭代次数（默认10，防止无限循环）

请根据用户的需求，选择合适的工具和技能来帮助完成任务。"""
        
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
        """执行工具调用（支持链式工具）"""
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
            
            # 执行链式工具
            if tool_name == 'execute_tool_chain':
                result = self._execute_chained_tool(parameters)
            # 执行技能工具
            else:
                result = execute_skill_tool(tool_name, parameters)
                
                if result.get('success'):
                    # 如果是加载技能内容，同时更新 system prompt
                    if tool_name == 'load_skill_content' and parameters.get('skill_name'):
                        skill_name = parameters['skill_name']
                        self._load_skill(skill_name)
            
            if result.get('success'):
                print(f"  ✅ 成功")
            else:
                print(f"  ❌ 失败: {result.get('error')}")
            
            results.append({
                "tool_call_id": tool_call.get('id'),
                "result": result
            })
        
        return results
    
    def _execute_chained_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行链式工具调用"""
        user_request = parameters.get('user_request', '')
        max_iterations = parameters.get('max_iterations', 10)
        
        # 使用新的 execute_chained_tool_call 函数
        from chained_tools import execute_chained_tool_call
        
        result = execute_chained_tool_call(
            user_request=user_request,
            tool_executor=self._execute_base_tool,
            llm_caller=self._call_llm_for_chain,
            system_prompt=self._build_base_system_prompt(),
            max_iterations=max_iterations
        )
        
        return {
            "success": result["success"],
            "result": result,
            "message": f"链式调用执行{'成功' if result['success'] else '失败'}，共 {result['iterations']} 步"
        }
    
    def _call_llm_for_chain(self, messages: List[Dict[str, str]]) -> str:
        """
        为链式调用提供 LLM 调用功能
        
        Args:
            messages: 消息历史
            
        Returns:
            LLM 响应文本
        """
        # 使用 create_llm_request 构建正确的请求配置
        request_config = create_llm_request(
            messages=messages,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            tools=None,
            stream=False
        )
        
        try:
            response = non_stream_llm_response(request_config)
            
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice:
                    return choice["message"].get("content", "")
            
            return json.dumps({"action": "complete", "answer": "无法解析LLM响应"})
            
        except Exception as e:
            # 如果 API 调用失败，返回模拟响应（用于演示）
            print(f"  [WARN] LLM 调用失败，使用模拟响应: {e}")
            return self._generate_mock_llm_response(messages)
    
    def _execute_base_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行基础工具（供链式调用使用）"""
        # 这里可以扩展更多基础工具
        if tool_name == 'list_files':
            return self._tool_list_files(parameters)
        elif tool_name == 'read_file':
            return self._tool_read_file(parameters)
        elif tool_name == 'search_chat_history':
            return self._tool_search_history(parameters)
        elif tool_name == 'generate_summary':
            return self._tool_generate_summary(parameters)
        elif tool_name == 'search_files':
            return self._tool_search_files(parameters)
        elif tool_name == 'write_file':
            return self._tool_write_file(parameters)
        elif tool_name == 'fetch_webpage':
            return self._tool_fetch_webpage(parameters)
        elif tool_name == 'load_skill_content':
            result = execute_skill_tool(tool_name, parameters)
            if result.get('success') and parameters.get('skill_name'):
                self._load_skill(parameters['skill_name'])
            return result
        else:
            return execute_skill_tool(tool_name, parameters)
    
    def _tool_list_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """列出目录文件"""
        import os
        directory = parameters.get('directory', '.')
        
        try:
            items = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file"
                })
            return {"success": True, "items": items, "directory": directory}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _tool_read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """读取文件内容"""
        import os
        directory = parameters.get('directory', '.')
        filename = parameters.get('filename')
        
        if not filename:
            return {"success": False, "error": "未指定文件名"}
        
        try:
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return {"success": True, "content": content, "filename": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _tool_search_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """搜索对话历史"""
        query = parameters.get('query', '').lower()
        results = []
        
        for msg in self.conversation_history:
            if msg.get('role') in ['user', 'assistant']:
                content = msg.get('content', '')
                if query in content.lower():
                    results.append({
                        "role": msg.get('role'),
                        "content": content[:200] + "..." if len(content) > 200 else content
                    })
        
        return {"success": True, "results": results, "query": query}
    
    def _tool_generate_summary(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """生成摘要"""
        content = parameters.get('content', '')
        
        if isinstance(content, list):
            content = "\n".join([str(item) for item in content])
        
        # 简单的摘要生成逻辑
        sentences = content.split('\n')[:3]  # 取前3行
        summary = "\n".join(sentences)
        
        return {"success": True, "summary": summary}
    
    def _tool_search_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """搜索包含关键词的文件"""
        import os
        directory = parameters.get('directory', '.')
        keyword = parameters.get('keyword', '')
        
        if not keyword:
            return {"success": False, "error": "未指定关键词"}
        
        try:
            matches = []
            for root, dirs, files in os.walk(directory):
                # 限制搜索深度
                if root.count(os.sep) - directory.count(os.sep) >= 2:
                    continue
                    
                for filename in files:
                    if filename.endswith('.py') or filename.endswith('.txt') or filename.endswith('.md'):
                        filepath = os.path.join(root, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                                content = f.read()
                                if keyword in content:
                                    matches.append({
                                        "filename": filename,
                                        "path": filepath,
                                        "preview": content[:100] + "..." if len(content) > 100 else content
                                    })
                        except:
                            continue
            
            return {"success": True, "matches": matches, "keyword": keyword, "directory": directory}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _tool_write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """写入文件"""
        import os
        directory = parameters.get('directory', '.')
        filename = parameters.get('filename')
        content = parameters.get('content', '')
        
        if not filename:
            return {"success": False, "error": "未指定文件名"}
        
        try:
            filepath = os.path.join(directory, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(content))
            return {"success": True, "filename": filename, "path": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _tool_fetch_webpage(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取网页内容"""
        url = parameters.get('url', '')
        
        if not url:
            return {"success": False, "error": "未指定URL"}
        
        try:
            import urllib.request
            import urllib.error
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='replace')
                
            # 简单的HTML清理
            import re
            # 移除script和style标签
            html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
            html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', '', html)
            # 清理空白
            text = re.sub(r'\n\s*\n', '\n', text)
            text = text.strip()
            
            return {"success": True, "content": text[:5000], "url": url}  # 限制内容长度
        except Exception as e:
            return {"success": False, "error": f"获取网页失败: {str(e)}"}
    
    def _generate_mock_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """
        生成模拟的 LLM 响应（用于 API 不可用时演示链式调用功能）
        使用新的 JSON 格式：{"done": true/false, ...}
        
        Args:
            messages: 消息历史
            
        Returns:
            模拟的 LLM 响应（JSON格式）
        """
        import json
        
        # 获取最后一条用户消息
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break
        
        # 根据消息内容决定模拟响应（使用新的格式）
        if "list_files" not in last_message and "read_file" not in last_message:
            # 第一步：列出文件
            return '''```json
{"done": false, "tool_call": {"name": "list_files", "arguments": {"directory": "."}}}
```'''
        elif "list_files_result" in last_message or ("list_files" in last_message and "read_file" not in last_message):
            # 第二步：读取文件
            return '''```json
{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": ".", "filename": "README.md"}}}
```'''
        else:
            # 完成任务
            return '''```json
{"done": true, "answer": "目录中包含 README.md、agent_with_skills.py、chained_tools.py 等文件。README.md 的内容是关于 Practice 07 链式工具调用的说明。"}
```'''
    
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
    print("🎯 Practice 07: 链式工具调用 Agent")
    print("=" * 60)
    print("\n⚠️  重要提示:")
    print("   请先运行 Python 程序，然后在程序提示符下输入！")
    print("   不要在 PowerShell/终端命令行直接输入中文！")
    print("\n功能特点:")
    print("  - 链式工具调用（Chained Tool Calls）")
    print("  - 前一个工具的输出作为后一个工具的输入")
    print("  - LLM 根据中间结果自主决定下一步工具调用")
    print("  - 自动读取 agents/skills 目录下的技能")
    print("\n链式工具示例:")
    print("  1. 分析目录并读取文件")
    print("     输入: '分析目录 ./practice07 并读取文件'")
    print("     流程: 列出文件 → 读取第一个文本文件")
    print("  2. 搜索历史并总结")
    print("     输入: '搜索历史关于通知的内容并总结'")
    print("     流程: 搜索历史 → 生成摘要")
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
                try:
                    user_input = input("👤 你: ").strip()
                except EOFError:
                    # 处理管道输入或重定向时的 EOF
                    print("\n[系统] 检测到输入结束，退出程序")
                    break
                
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
