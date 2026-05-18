"""
Practice 04: 支持 AnythingLLM 查询的 AI Agent
基于 Practice 03，添加查询文档仓库功能
"""

import http.client
import json
import os
import sys
import time
import signal
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional, Generator

# 添加当前目录到路径（确保能导入同级模块）
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入文件工具模块和 AnythingLLM 工具模块
from file_tools import TOOLS_DEFINITION as FILE_TOOLS, execute_tool as execute_file_tool
from anythingllm_tools import (
    ANYTHINGLLM_TOOLS_DEFINITION, 
    execute_anythingllm_tool,
    query_anythingllm,
    check_anythingllm_health
)


# 全局变量用于控制程序退出
running = True


def signal_handler(sig, frame):
    """处理Ctrl+C信号，优雅退出"""
    global running
    print("\n\n👋 再见！")
    running = False
    sys.exit(0)


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """读取.env文件并解析为字典"""
    env_vars = {}
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    env_file = os.path.join(project_root, env_path)
    
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"找不到.env文件: {env_file}")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


class ToolCallingAgent:
    """支持工具调用的 AI Agent，包含 AnythingLLM 查询功能"""
    
    def __init__(self, env_vars: Dict[str, str]):
        self.provider = env_vars.get('LLM_PROVIDER', 'openai')
        # 支持多种API Key配置方式
        self.api_key = env_vars.get('LLM_API_KEY') or env_vars.get('OPENAI_API_KEY')
        # 支持多种Base URL配置方式
        self.base_url = env_vars.get('LLM_BASE_URL') or env_vars.get('API_BASE_URL', 'https://api.openai.com/v1')
        # 支持多种Model配置方式
        self.model = env_vars.get('LLM_MODEL') or env_vars.get('MODEL_NAME', 'gpt-3.5-turbo')
        self.max_tokens = int(env_vars.get('MAX_TOKENS', 2048))
        self.temperature = float(env_vars.get('TEMPERATURE', 0.7))
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 或 OPENAI_API_KEY 未在.env中配置")
        
        parsed = urlparse(self.base_url)
        self.host = parsed.netloc
        self.path_prefix = parsed.path.rstrip('/')
        self.is_https = parsed.scheme == 'https'
        
        # 对话历史
        self.conversation_history: List[Dict[str, Any]] = []
        
        # 设置 AnythingLLM 环境变量
        if 'ANYTHINGLLM_API_KEY' in env_vars:
            os.environ['ANYTHINGLLM_API_KEY'] = env_vars['ANYTHINGLLM_API_KEY']
        if 'ANYTHINGLLM_WORKSPACE_SLUG' in env_vars:
            os.environ['ANYTHINGLLM_WORKSPACE_SLUG'] = env_vars['ANYTHINGLLM_WORKSPACE_SLUG']
        if 'ANYTHINGLLM_BASE_URL' in env_vars:
            os.environ['ANYTHINGLLM_BASE_URL'] = env_vars['ANYTHINGLLM_BASE_URL']
        
        # 系统提示词（包含工具说明）
        self.system_prompt = self._build_system_prompt()
        self._init_conversation()
    
    def _build_system_prompt(self) -> str:
        """构建包含工具说明的系统提示词"""
        prompt = """你是一个智能助手，可以帮助用户管理文件和查询文档仓库。

## 文件操作工具

1. **list_files** - 列出目录下的文件和文件夹
   - 参数: directory (目录路径)
   - 用途: 查看目录内容，获取文件大小、创建时间等信息

2. **rename_file** - 重命名文件
   - 参数: directory (目录), old_name (原文件名), new_name (新文件名)
   - 用途: 修改文件名

3. **delete_file** - 删除文件
   - 参数: directory (目录), filename (文件名)
   - 用途: 删除指定文件

4. **create_file** - 创建新文件
   - 参数: directory (目录), filename (文件名), content (文件内容)
   - 用途: 创建文件并写入内容

5. **read_file** - 读取文件内容
   - 参数: directory (目录), filename (文件名)
   - 用途: 查看文件内容

## 文档仓库查询工具

6. **query_anythingllm** - 查询 AnythingLLM 文档仓库
   - 参数: message (查询内容)
   - 用途: 在已上传的文档中搜索信息、回答问题
   - 触发条件: 当用户提到"文档仓库"、"文件仓库"、"仓库"、"知识库"或需要查询已上传文档的内容时

## 重要规则

- 当用户请求涉及文件操作时，使用文件工具来完成
- 当用户询问文档仓库、知识库相关内容时，使用 query_anythingllm 工具
- 不要假设操作结果，总是使用工具获取真实信息
- 操作完成后向用户报告结果
- 如果路径不存在，工具会自动创建目录
- 只能操作文件，不能删除目录

请根据用户的需求，选择合适的工具来完成任务。"""
        return prompt
    
    def _init_conversation(self):
        """初始化对话"""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def _get_connection(self):
        """创建HTTP连接"""
        if self.is_https:
            return http.client.HTTPSConnection(self.host)
        return http.client.HTTPConnection(self.host)
    
    def _build_request_body(self, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """构建请求体"""
        body = {
            "model": self.model,
            "messages": self.conversation_history,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        # 添加工具定义
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        
        return body
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.provider == 'anthropic':
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
            headers.pop("Authorization", None)
        
        return headers
    
    def _get_endpoint(self) -> str:
        """获取API端点"""
        if self.provider == 'anthropic':
            return f"{self.path_prefix}/messages"
        return f"{self.path_prefix}/chat/completions"
    
    def _get_all_tools(self) -> List[Dict]:
        """获取所有可用工具定义"""
        # 合并文件工具和 AnythingLLM 工具
        all_tools = FILE_TOOLS.copy()
        all_tools.extend(ANYTHINGLLM_TOOLS_DEFINITION)
        return all_tools
    
    def chat_with_tools(self, user_message: str) -> Dict[str, Any]:
        """
        发送消息并处理可能的工具调用
        
        Args:
            user_message: 用户输入
            
        Returns:
            包含回复内容和工具调用结果的字典
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 第一次调用：获取LLM的响应（可能包含工具调用）
        response = self._call_llm(with_tools=True)
        
        # 检查是否有工具调用
        message = response.get('choices', [{}])[0].get('message', {})
        tool_calls = message.get('tool_calls')
        
        # 处理工具调用
        if tool_calls:
            print(f"\n🔧 检测到 {len(tool_calls)} 个工具调用")
            
            # 添加助手消息（包含工具调用）到历史
            self.conversation_history.append(message)
            
            # 执行每个工具调用
            for tool_call in tool_calls:
                result = self._execute_tool_call(tool_call)
                
                # 添加工具结果到历史
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get('id'),
                    "name": tool_call.get('function', {}).get('name'),
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # 第二次调用：获取LLM对工具结果的回复
            response = self._call_llm(with_tools=False)
            message = response.get('choices', [{}])[0].get('message', {})
        
        # 添加最终回复到历史
        self.conversation_history.append({
            "role": "assistant",
            "content": message.get('content', '')
        })
        
        return {
            'content': message.get('content', ''),
            'history_length': len(self.conversation_history)
        }
    
    def _call_llm(self, with_tools: bool = True) -> Dict[str, Any]:
        """调用LLM API"""
        body = self._build_request_body(
            tools=self._get_all_tools() if with_tools else None
        )
        headers = self._get_headers()
        endpoint = self._get_endpoint()
        
        conn = self._get_connection()
        
        try:
            conn.request(
                "POST",
                endpoint,
                body=json.dumps(body),
                headers=headers
            )
            
            response = conn.getresponse()
            response_data = json.loads(response.read().decode('utf-8'))
            
            if response.status != 200:
                error_msg = response_data.get('error', {}).get('message', str(response_data))
                raise Exception(f"API错误 (HTTP {response.status}): {error_msg}")
            
            return response_data
            
        finally:
            conn.close()
    
    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        function_info = tool_call.get('function', {})
        tool_name = function_info.get('name')
        arguments_str = function_info.get('arguments', '{}')
        
        try:
            parameters = json.loads(arguments_str)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"无法解析参数: {arguments_str}"
            }
        
        print(f"  📋 执行: {tool_name}")
        print(f"     参数: {json.dumps(parameters, ensure_ascii=False)}")
        
        # 判断是文件工具还是 AnythingLLM 工具
        if tool_name == "query_anythingllm":
            result = execute_anythingllm_tool(tool_name, parameters)
        else:
            result = execute_file_tool(tool_name, parameters)
        
        if result.get('success'):
            print(f"  ✅ 成功")
        else:
            print(f"  ❌ 失败: {result.get('error')}")
        
        return result
    
    def clear_history(self):
        """清空对话历史"""
        self._init_conversation()
        print("\n🗑️  对话历史已清空")
    
    def get_history_summary(self) -> str:
        """获取历史记录摘要"""
        user_msg_count = sum(1 for m in self.conversation_history if m.get('role') == 'user')
        assistant_msg_count = sum(1 for m in self.conversation_history if m.get('role') == 'assistant')
        return f"历史: {user_msg_count} 用户消息, {assistant_msg_count} AI回复"


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🛠️  Practice 04: AnythingLLM 查询 Agent")
    print("=" * 60)
    print("\n可用工具:")
    print("  📁 list_files       - 列出目录文件")
    print("  ✏️  rename_file      - 重命名文件")
    print("  🗑️  delete_file      - 删除文件")
    print("  📝 create_file      - 创建文件")
    print("  📖 read_file        - 读取文件")
    print("  🔍 query_anythingllm- 查询文档仓库")
    print("\n命令:")
    print("  /clear  - 清空对话历史")
    print("  /history- 查看历史记录")
    print("  /exit   - 退出程序")
    print("  Ctrl+C  - 强制退出")
    print("\n" + "-" * 60)


def main():
    """主函数"""
    print_banner()
    
    try:
        # 加载配置
        env_vars = load_env_file()
        agent = ToolCallingAgent(env_vars)
        
        print(f"✅ 已连接到: {env_vars.get('LLM_MODEL', 'unknown')}")
        print(f"📊 {agent.get_history_summary()}")
        
        # 检查 AnythingLLM 服务状态
        health = check_anythingllm_health()
        if health['success']:
            print(f"✅ AnythingLLM: {health['message']}")
        else:
            print(f"⚠️  AnythingLLM: {health['message']}")
        
        print("-" * 60 + "\n")
        
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
                
                # 发送消息
                print("🤖 AI: ", end="", flush=True)
                
                try:
                    result = agent.chat_with_tools(user_input)
                    print(result['content'])
                except Exception as e:
                    print(f"\n❌ 错误: {e}")
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
        raise


if __name__ == "__main__":
    main()
