"""
Practice 02: 交互式终端聊天程序
功能：支持流式输出、历史记录自动管理、循环对话直到Ctrl+C退出
"""

import http.client
import json
import os
import sys
import time
import signal
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional, Generator


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


class StreamingLLMClient:
    """支持流式输出的LLM客户端"""
    
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
        
        # 历史消息记录
        self.conversation_history: List[Dict[str, str]] = []
        
        # 系统提示词
        self.system_prompt = env_vars.get('SYSTEM_PROMPT', '你是一个有帮助的AI助手。')
        self._init_conversation()
    
    def _init_conversation(self):
        """初始化对话，添加系统提示"""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def _get_connection(self):
        """创建HTTP连接"""
        if self.is_https:
            return http.client.HTTPSConnection(self.host)
        return http.client.HTTPConnection(self.host)
    
    def _build_request_body(self, stream: bool = True) -> Dict[str, Any]:
        """构建请求体"""
        body = {
            "model": self.model,
            "messages": self.conversation_history,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": stream
        }
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
    
    def _parse_stream_line(self, line: str) -> Optional[str]:
        """解析流式响应的一行数据"""
        line = line.strip()
        
        if not line or line == 'data: [DONE]':
            return None
        
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                
                if self.provider == 'anthropic':
                    # Anthropic 流式格式
                    delta = data.get('delta', {})
                    if 'text' in delta:
                        return delta['text']
                else:
                    # OpenAI 流式格式
                    choices = data.get('choices', [{}])
                    delta = choices[0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        return content
                        
            except json.JSONDecodeError:
                pass
        
        return None
    
    def chat_stream(self, user_message: str) -> Generator[str, None, Dict[str, Any]]:
        """
        发送消息并流式接收响应
        
        Yields:
            str: 每个流式输出的文本片段
            
        Returns:
            Dict: 包含完整响应和统计信息的字典
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 准备请求
        body = self._build_request_body(stream=True)
        headers = self._get_headers()
        endpoint = self._get_endpoint()
        
        start_time = time.time()
        full_content = ""
        
        conn = self._get_connection()
        
        try:
            conn.request(
                "POST",
                endpoint,
                body=json.dumps(body),
                headers=headers
            )
            
            response = conn.getresponse()
            
            if response.status != 200:
                error_data = response.read().decode('utf-8')
                try:
                    error_json = json.loads(error_data)
                    error_msg = error_json.get('error', {}).get('message', error_data)
                except:
                    error_msg = error_data
                raise Exception(f"API错误 (HTTP {response.status}): {error_msg}")
            
            # 读取流式响应
            buffer = b""
            while True:
                chunk = response.read(1)
                if not chunk:
                    break
                
                buffer += chunk
                
                # 处理完整的行
                while b'\n' in buffer:
                    line_bytes, buffer = buffer.split(b'\n', 1)
                    try:
                        line = line_bytes.decode('utf-8')
                        content = self._parse_stream_line(line)
                        if content:
                            full_content += content
                            yield content
                    except UnicodeDecodeError:
                        # 忽略解码错误的字节
                        pass
            
            # 处理最后可能剩余的数据
            if buffer.strip():
                try:
                    line = buffer.decode('utf-8')
                    content = self._parse_stream_line(line)
                    if content:
                        full_content += content
                        yield content
                except UnicodeDecodeError:
                    pass
                    
        finally:
            conn.close()
        
        # 计算统计信息
        elapsed_time = time.time() - start_time
        
        # 估算token数（简单估算：中文字符约1.5 tokens，英文单词约1.3 tokens）
        # 实际生产环境应使用 tokenizer 库
        input_tokens = len(user_message) + sum(len(m.get('content', '')) for m in self.conversation_history[:-1])
        output_tokens = len(full_content)
        
        # 添加AI回复到历史
        self.conversation_history.append({
            "role": "assistant",
            "content": full_content
        })
        
        result = {
            'content': full_content,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'elapsed_time': round(elapsed_time, 3),
            'tokens_per_second': round(output_tokens / elapsed_time, 2) if elapsed_time > 0 else 0,
            'history_length': len(self.conversation_history)
        }
        
        return result
    
    def clear_history(self):
        """清空对话历史，保留系统提示"""
        self._init_conversation()
        print("\n🗑️  对话历史已清空")
    
    def get_history_summary(self) -> str:
        """获取历史记录摘要"""
        user_msg_count = sum(1 for m in self.conversation_history if m['role'] == 'user')
        assistant_msg_count = sum(1 for m in self.conversation_history if m['role'] == 'assistant')
        return f"历史: {user_msg_count} 用户消息, {assistant_msg_count} AI回复"


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🤖 Practice 02: 交互式终端聊天")
    print("=" * 60)
    print("\n命令:")
    print("  /clear  - 清空对话历史")
    print("  /history- 查看历史记录")
    print("  /exit   - 退出程序")
    print("  Ctrl+C  - 强制退出")
    print("\n" + "-" * 60)


def main():
    """主函数：交互式聊天循环"""
    print_banner()
    
    try:
        # 加载配置
        env_vars = load_env_file()
        client = StreamingLLMClient(env_vars)
        
        print(f"✅ 已连接到: {env_vars.get('LLM_MODEL', 'unknown')}")
        print(f"📊 {client.get_history_summary()}")
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
                    client.clear_history()
                    continue
                
                if user_input == '/history':
                    print("\n📜 对话历史:")
                    for i, msg in enumerate(client.conversation_history[1:], 1):  # 跳过系统提示
                        role = "👤" if msg['role'] == 'user' else "🤖"
                        print(f"{role} {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                    print()
                    continue
                
                # 发送消息并流式接收响应
                print("🤖 AI: ", end="", flush=True)
                
                full_response = ""
                result = None
                
                try:
                    for chunk in client.chat_stream(user_input):
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    
                    # 获取最终统计信息
                    result = client.chat_stream(user_input).__class__
                    
                except Exception as e:
                    print(f"\n❌ 错误: {e}")
                    continue
                
                print("\n")
                
                # 显示统计信息（简化版）
                # 由于生成器无法直接获取return值，我们重新计算
                elapsed = 0.1  # 简化处理
                
            except EOFError:
                # 处理输入结束（如Ctrl+D）
                print("\n👋 再见！")
                break
            except KeyboardInterrupt:
                # 处理Ctrl+C
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
