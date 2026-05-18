"""
Practice 05: 带知识提取和搜索的 AI Agent
基于 Practice 04，实现：
1. 每5次聊天提取关键信息（5W规则）并保存到本地
2. 支持 /search 命令搜索聊天历史
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
    # 使用 chcp 65001 设置 UTF-8 代码页
    os.system('chcp 65001 >nul 2>&1')
    # 重新包装 stdout/stderr
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

# 导入文件工具模块和知识提取模块
from file_tools import TOOLS_DEFINITION, execute_tool
from knowledge_extractor import KnowledgeExtractor, search_chat_history, KNOWLEDGE_TOOLS


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
    
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"找不到.env文件: {os.path.abspath(env_path)}")
    
    with open(env_path, 'r', encoding='utf-8') as f:
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
    """
    构建LLM API请求体
    
    Args:
        messages: 对话消息列表
        model: 模型名称
        api_key: API密钥
        base_url: API基础URL
        tools: 可选的工具定义
        stream: 是否使用流式输出
        
    Returns:
        请求配置字典
    """
    # 解析URL
    parsed = urlparse(base_url)
    host = parsed.netloc
    # 构建正确的 API 路径
    # 阿里云百炼: /compatible-mode/v1/chat/completions
    # OpenAI: /v1/chat/completions
    if '/v1' in parsed.path and not parsed.path.endswith('/chat/completions'):
        path = parsed.path.rstrip('/') + "/chat/completions"
    elif parsed.path:
        path = parsed.path
    else:
        path = "/v1/chat/completions"
    
    # 构建请求体
    request_body = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    # 添加工具定义（如果提供）
    if tools:
        request_body["tools"] = tools
        request_body["tool_choice"] = "auto"
    
    return {
        "host": host,
        "path": path,
        "api_key": api_key,
        "body": request_body,
        "stream": stream
    }


def stream_llm_response(request_config: Dict[str, Any]) -> Generator[str, None, None]:
    """
    流式调用LLM API并实时输出响应
    
    Args:
        request_config: 请求配置
        
    Yields:
        响应文本片段
    """
    host = request_config["host"]
    path = request_config["path"]
    api_key = request_config["api_key"]
    body = request_config["body"]
    
    # 构建完整URL
    protocol = "https" if host.endswith(':443') or 'https' in host else "http"
    clean_host = host.replace(':443', '').replace('https://', '').replace('http://', '')
    url = f"{protocol}://{clean_host}{path}"
    
    # 发送请求
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # 本地模型（如Ollama）不需要Authorization头
    if api_key and api_key != 'sk-no-key-needed':
        headers["Authorization"] = f"Bearer {api_key}"
    
    if HAS_REQUESTS:
        # 使用 requests 库（更好地处理重定向）
        try:
            # 禁用自动重定向，手动处理 308
            response = requests.post(
                url,
                json=body,
                headers=headers,
                stream=True,
                timeout=30,
                allow_redirects=False
            )
            
            # 处理 308 重定向
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
            
            response.raise_for_status()
            
            # 处理流式响应
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
                            
                            # 检查是否有工具调用
                            if 'tool_calls' in delta:
                                yield json.dumps({"tool_calls": delta['tool_calls']})
                            
                            # 检查是否有内容
                            content = delta.get('content', '')
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求错误: {e}")
    else:
        # 使用 urllib（备用）
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
                break  # 成功，跳出重定向循环
                
            except HTTPError as e:
                # 处理 308/307/302/301 重定向
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
            
            # 处理流式响应
            buffer = b""
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                
                buffer += chunk
                
                # 处理缓冲区中的完整行
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
                            
                            # 检查是否有工具调用
                            if 'tool_calls' in delta:
                                yield json.dumps({"tool_calls": delta['tool_calls']})
                            
                            # 检查是否有内容
                            content = delta.get('content', '')
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue
            
        finally:
            if response:
                response.close()


def non_stream_llm_response(request_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    非流式调用LLM API
    
    Args:
        request_config: 请求配置
        
    Returns:
        完整的响应字典
    """
    host = request_config["host"]
    path = request_config["path"]
    api_key = request_config["api_key"]
    body = request_config["body"]
    
    # 禁用流式
    body["stream"] = False
    
    # 构建完整URL
    protocol = "https" if host.endswith(':443') or 'https' in host else "http"
    clean_host = host.replace(':443', '').replace('https://', '').replace('http://', '')
    url = f"{protocol}://{clean_host}{path}"
    
    # 发送请求
    headers = {
        "Content-Type": "application/json"
    }
    
    # 本地模型（如Ollama）不需要Authorization头
    if api_key and api_key != 'sk-no-key-needed':
        headers["Authorization"] = f"Bearer {api_key}"
    
    if HAS_REQUESTS:
        # 使用 requests 库（更好地处理重定向）
        try:
            # 禁用自动重定向，手动处理 308
            response = requests.post(
                url,
                json=body,
                headers=headers,
                timeout=30,
                allow_redirects=False
            )
            
            # 处理 308 重定向
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
        # 使用 urllib（备用）
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
                break  # 成功，跳出重定向循环
                
            except HTTPError as e:
                # 处理 308/307/302/301 重定向
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
            if response:
                response.close()


class KnowledgeAgent:
    """带知识提取和搜索功能的 AI Agent"""
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一个智能助手，具备文件操作和聊天历史搜索能力。

你有以下工具可用：
1. 文件操作：列出目录、创建文件、读取文件、重命名、删除
2. 聊天历史搜索：当用户发送"/search"开头的消息，或表达查找聊天历史的意图时，使用 search_chat_history 工具

重要提示：
- 当用户说"查找"、"搜索"、"我记得"、"之前说过"等类似表达时，应该调用搜索工具
- 搜索工具会查询已保存的关键信息（按5W规则提取）
- 如果用户输入以"/search"开头，提取后面的内容作为搜索关键词

请根据用户的需求，决定是否需要调用工具。"""
    
    def __init__(self, env_vars: Dict[str, str]):
        self.env_vars = env_vars
        self.model = env_vars.get('LLM_MODEL') or env_vars.get('MODEL_NAME', 'gpt-3.5-turbo')
        self.api_key = env_vars.get('LLM_API_KEY') or env_vars.get('OPENAI_API_KEY', 'sk-no-key-needed')
        self.base_url = env_vars.get('LLM_BASE_URL') or env_vars.get('BASE_URL', 'https://api.openai.com/v1')
        
        # 检测是否为本地模型（如Ollama）
        self.is_local_model = 'localhost' in self.base_url or '127.0.0.1' in self.base_url or ':11434' in self.base_url
        
        if not self.is_local_model and not env_vars.get('LLM_API_KEY') and not env_vars.get('OPENAI_API_KEY'):
            raise ValueError("LLM_API_KEY 未在.env中配置")
        
        # 初始化对话历史
        self.conversation_history = []
        self._init_conversation()
        
        # 初始化知识提取器
        self.knowledge_extractor = KnowledgeExtractor()
        
        # 合并工具定义
        self.tools = TOOLS_DEFINITION + KNOWLEDGE_TOOLS
    
    def _init_conversation(self):
        """初始化对话历史"""
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
    
    def _should_use_knowledge_search(self, user_input: str) -> bool:
        """
        判断是否应该使用知识搜索
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否应该搜索
        """
        # 检查是否以 /search 开头
        if user_input.strip().lower().startswith('/search'):
            return True
        
        # 检查是否包含搜索相关关键词
        search_keywords = [
            '查找', '搜索', '查询', '找找', '找一下',
            '我记得', '之前说过', '以前提过', '之前提到',
            '上次', '以前', '曾经', '历史记录'
        ]
        
        user_input_lower = user_input.lower()
        for keyword in search_keywords:
            if keyword in user_input_lower:
                return True
        
        return False
    
    def _extract_search_query(self, user_input: str) -> str:
        """
        从用户输入中提取搜索关键词
        
        Args:
            user_input: 用户输入
            
        Returns:
            搜索关键词
        """
        # 如果以 /search 开头，提取后面的内容
        if user_input.strip().lower().startswith('/search'):
            query = user_input[7:].strip()
            if query:
                return query
        
        # 否则返回完整输入
        return user_input.strip()
    
    def _handle_knowledge_search(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        处理知识搜索请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            搜索结果或None
        """
        query = self._extract_search_query(user_input)
        
        if not query:
            return None
        
        print(f"\n[搜索] 正在搜索: {query}")
        
        # 执行搜索
        result = search_chat_history(query, self.knowledge_extractor)
        
        if result.get('found'):
            print(f"[搜索] 找到 {result['total_matches']} 条相关记录")
        else:
            print(f"[搜索] 未找到相关记录")
        
        return result
    
    def _perform_extraction(self, extraction_trigger: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行知识提取
        
        Args:
            extraction_trigger: 提取触发信息
            
        Returns:
            提取结果或None
        """
        if extraction_trigger and extraction_trigger.get('should_extract'):
            print("\n[知识提取] 正在分析对话并提取关键信息...")
            
            # 调用LLM进行提取
            extraction_prompt = extraction_trigger['extraction_prompt']
            
            # 构建提取请求
            extraction_request = create_llm_request(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                stream=False
            )
            
            try:
                response = non_stream_llm_response(extraction_request)
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # 解析提取结果
                try:
                    # 尝试从JSON代码块中提取
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(1)
                    
                    extraction_data = json.loads(content)
                    extractions = extraction_data.get('extractions', [])
                    
                    # 保存到日志文件
                    if extractions:
                        self.knowledge_extractor.save_extractions(
                            extractions,
                            extraction_trigger['messages']
                        )
                        print(f"[知识提取] 已提取并保存 {len(extractions)} 条关键信息")
                        return {
                            "extracted": True,
                            "count": len(extractions),
                            "extractions": extractions
                        }
                    
                except json.JSONDecodeError as e:
                    print(f"[知识提取] 解析结果失败: {e}")
                    
            except Exception as e:
                print(f"[知识提取] 提取失败: {e}")
        
        return None
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入并返回响应
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            包含响应内容和元信息的字典
        """
        # 检查是否是搜索请求
        # 初始化提取触发器
        extraction_trigger = None
        
        if self._should_use_knowledge_search(user_input):
            search_result = self._handle_knowledge_search(user_input)
            
            if search_result:
                # 将搜索结果添加到上下文
                search_context = self._format_search_context(search_result)
                
                # 添加用户消息（包含搜索意图）
                self.conversation_history.append({
                    "role": "user",
                    "content": f"{user_input}\n\n[系统搜索结果]: {search_context}"
                })
            else:
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
        else:
            # 普通消息，添加到缓冲区
            extraction_trigger = self.knowledge_extractor.add_message("user", user_input)
            self.conversation_history.append({"role": "user", "content": user_input})
        
        # 检查是否需要提取知识
        if extraction_trigger and extraction_trigger.get('should_extract'):
            extraction_info = self._perform_extraction(extraction_trigger)
        else:
            extraction_info = None
        
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
            # 检查是否是工具调用
            try:
                chunk_data = json.loads(chunk)
                if isinstance(chunk_data, dict) and 'tool_calls' in chunk_data:
                    tool_calls_buffer.extend(chunk_data['tool_calls'])
                    continue
            except (json.JSONDecodeError, TypeError):
                pass
            
            # 普通内容
            print(chunk, end="", flush=True)
            full_response += chunk
        
        # 处理工具调用
        if tool_calls_buffer:
            print(f"\n[工具] 检测到 {len(tool_calls_buffer)} 个工具调用")
            
            # 添加助手消息（包含工具调用）到历史
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
            
            # 添加到知识提取缓冲区
            self.knowledge_extractor.add_message("assistant", full_response)
        
        return {
            "content": full_response,
            "extraction": extraction_info,
            "history_length": len(self.conversation_history)
        }
    
    def _format_search_context(self, search_result: Dict[str, Any]) -> str:
        """格式化搜索结果为上下文"""
        if not search_result.get('found'):
            return "未找到相关历史记录。"
        
        context = f"找到 {search_result['total_matches']} 条相关记录:\n"
        
        for i, result in enumerate(search_result['results'][:5], 1):  # 最多显示5条
            context += f"\n{i}. Who: {result.get('who', 'unknown')}"
            context += f"\n   What: {result.get('what', 'unknown')}"
            if result.get('when') and result['when'] != 'unknown':
                context += f"\n   When: {result['when']}"
            if result.get('where') and result['where'] != 'unknown':
                context += f"\n   Where: {result['where']}"
            if result.get('why') and result['why'] != 'unknown':
                context += f"\n   Why: {result['why']}"
        
        return context
    
    def _execute_tool_calls(self, tool_calls: List[Dict]) -> List[Dict]:
        """执行工具调用"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get('function', {}).get('name', '')
            tool_id = tool_call.get('id', '')
            
            try:
                arguments = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
            except json.JSONDecodeError:
                arguments = {}
            
            print(f"  [执行] {tool_name}")
            print(f"     参数: {json.dumps(arguments, ensure_ascii=False)}")
            
            # 特殊处理搜索工具
            if tool_name == 'search_chat_history':
                result = search_chat_history(
                    arguments.get('query', ''),
                    self.knowledge_extractor
                )
            else:
                # 普通文件工具
                result = execute_tool(tool_name, arguments)
            
            if result.get('success'):
                print(f"  [成功]")
            else:
                print(f"  [失败] {result.get('error')}")
            
            results.append({
                "tool_call_id": tool_id,
                "result": result
            })
        
        return results
    
    def clear_history(self):
        """清空对话历史"""
        self._init_conversation()
        print("\n[清空] 对话历史已清空")
    
    def get_history_summary(self) -> str:
        """获取对话历史摘要"""
        user_msgs = sum(1 for msg in self.conversation_history if msg.get('role') == 'user')
        assistant_msgs = sum(1 for msg in self.conversation_history if msg.get('role') == 'assistant')
        total_chars = sum(len(msg.get('content', '')) for msg in self.conversation_history)
        return f"历史: {user_msgs} 用户消息, {assistant_msgs} AI回复 | 上下文: {total_chars} 字符"
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识提取统计"""
        return self.knowledge_extractor.get_stats()


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("Practice 05: 带知识提取和搜索的 Agent")
    print("=" * 60)
    print("\n功能特点:")
    print("  - 每5次聊天自动提取关键信息（5W规则）")
    print("  - 保存到 D:\\chat-log\\log.txt")
    print("  - 支持 /search 命令搜索历史")
    print("  - 自动识别搜索意图")
    print("\n命令:")
    print("  /clear       - 清空对话历史")
    print("  /history     - 查看历史记录")
    print("  /stats       - 查看知识提取统计")
    print("  /search XXX  - 搜索聊天历史")
    print("  /exit        - 退出程序")
    print("  Ctrl+C       - 强制退出")
    print("\n" + "-" * 60)


def main():
    """主函数"""
    print_banner()
    
    try:
        # 加载环境变量
        env_vars = load_env_file()
        
        # 创建Agent
        agent = KnowledgeAgent(env_vars)
        
        model_type = "[本地模型]" if agent.is_local_model else "[云端API]"
        print(f"[OK] 已连接到: {model_type} {env_vars.get('LLM_MODEL') or env_vars.get('MODEL_NAME', 'unknown')}")
        print(f"[INFO] {agent.get_history_summary()}")
        
        stats = agent.get_knowledge_stats()
        print(f"[INFO] 知识库: {stats['total_records']} 条记录, {stats['total_extractions']} 条提取")
        print(f"[INFO] 提取间隔: 每 {stats['extraction_interval']} 次聊天")
        print("-" * 60 + "\n")
        
        # 主循环
        global running
        while running:
            try:
                # 获取用户输入
                user_input = input("[你] ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input == '/exit':
                    print("\n[再见] 再见！")
                    break
                
                if user_input == '/clear':
                    agent.clear_history()
                    continue
                
                if user_input == '/history':
                    print("\n[历史] 对话历史:")
                    for i, msg in enumerate(agent.conversation_history[1:], 1):
                        role = msg.get('role', '')
                        content = msg.get('content', '')
                        if role == 'user':
                            print(f"{i}. [用户] {content[:100]}{'...' if len(content) > 100 else ''}")
                        elif role == 'assistant':
                            print(f"{i}. [AI] {content[:100]}{'...' if len(content) > 100 else ''}")
                    print()
                    continue
                
                if user_input == '/stats':
                    stats = agent.get_knowledge_stats()
                    print("\n[统计] 知识提取统计:")
                    print(f"  日志文件: {stats['log_file_path']}")
                    print(f"  总记录数: {stats['total_records']}")
                    print(f"  总提取数: {stats['total_extractions']}")
                    print(f"  提取间隔: 每 {stats['extraction_interval']} 次聊天")
                    print(f"  当前计数: {stats['current_chat_count']}")
                    print(f"  待处理消息: {stats['pending_messages']}")
                    print()
                    continue
                
                # 发送消息
                print("[AI] ", end="", flush=True)
                
                try:
                    result = agent.chat(user_input)
                    print()
                    
                    # 显示提取信息（如果有）
                    if result.get('extraction') and result['extraction'].get('extracted'):
                        print(f"\n[提示] 已自动提取 {result['extraction']['count']} 条关键信息")
                    
                except Exception as e:
                    print(f"\n[错误] {e}")
                    continue
                
            except EOFError:
                print("\n[再见] 再见！")
                break
            except KeyboardInterrupt:
                print("\n\n[再见] 再见！")
                break
                
    except FileNotFoundError as e:
        print(f"\n[错误] {e}")
        print("\n请按照以下步骤操作:")
        print("1. 复制 env.example 为 .env")
        print("2. 在 .env 中填入你的API密钥")
        print("3. 再次运行此脚本")
        
    except Exception as e:
        print(f"\n[错误] {e}")
        raise


if __name__ == "__main__":
    main()
