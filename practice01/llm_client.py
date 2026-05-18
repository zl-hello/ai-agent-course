"""
Practice 01: 使用Python标准HTTP库调用LLM API
功能：读取.env配置，调用LLM，统计token消耗、时间和速度
"""

import http.client
import json
import os
import time
from urllib.parse import urlparse
from typing import Dict, Any, Optional


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """读取.env文件并解析为字典"""
    env_vars = {}
    
    # 获取项目根目录的.env文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    env_file = os.path.join(project_root, env_path)
    
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"找不到.env文件: {env_file}")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


class LLMClient:
    """使用Python标准HTTP库的LLM客户端"""
    
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
        
        # 解析URL
        parsed = urlparse(self.base_url)
        self.host = parsed.netloc
        self.path_prefix = parsed.path.rstrip('/')
        self.is_https = parsed.scheme == 'https'
    
    def _get_connection(self):
        """创建HTTP连接"""
        if self.is_https:
            return http.client.HTTPSConnection(self.host)
        return http.client.HTTPConnection(self.host)
    
    def _build_request_body(self, messages: list) -> Dict[str, Any]:
        """构建请求体"""
        if self.provider == 'anthropic':
            return {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages
            }
        else:  # openai 或其他兼容格式
            return {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.provider == 'anthropic':
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
            # 移除Bearer前缀
            headers.pop("Authorization", None)
        
        return headers
    
    def _get_endpoint(self) -> str:
        """获取API端点"""
        if self.provider == 'anthropic':
            return f"{self.path_prefix}/messages"
        return f"{self.path_prefix}/chat/completions"
    
    def _parse_response(self, response_data: Dict) -> Dict[str, Any]:
        """解析响应，提取关键信息"""
        if self.provider == 'anthropic':
            content = response_data.get('content', [{}])[0].get('text', '')
            usage = response_data.get('usage', {})
            return {
                'content': content,
                'input_tokens': usage.get('input_tokens', 0),
                'output_tokens': usage.get('output_tokens', 0),
                'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            }
        else:  # openai格式
            choices = response_data.get('choices', [{}])
            content = choices[0].get('message', {}).get('content', '')
            usage = response_data.get('usage', {})
            return {
                'content': content,
                'input_tokens': usage.get('prompt_tokens', 0),
                'output_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0)
            }
    
    def chat(self, messages: list) -> Dict[str, Any]:
        """
        发送聊天请求并返回结果和统计信息
        
        Returns:
            {
                'content': str,          # LLM回复内容
                'input_tokens': int,     # 输入token数
                'output_tokens': int,    # 输出token数
                'total_tokens': int,     # 总token数
                'elapsed_time': float,   # 耗时(秒)
                'tokens_per_second': float  # token/秒速度
            }
        """
        # 准备请求
        body = self._build_request_body(messages)
        headers = self._get_headers()
        endpoint = self._get_endpoint()
        
        # 记录开始时间
        start_time = time.time()
        
        # 发送请求
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
            
        finally:
            conn.close()
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 解析响应
        result = self._parse_response(response_data)
        
        # 计算速度
        tokens_per_second = result['output_tokens'] / elapsed_time if elapsed_time > 0 else 0
        
        return {
            **result,
            'elapsed_time': round(elapsed_time, 3),
            'tokens_per_second': round(tokens_per_second, 2)
        }


def main():
    """主函数：演示如何使用LLMClient"""
    print("=" * 60)
    print("Practice 01: LLM HTTP Client")
    print("=" * 60)
    
    try:
        # 1. 加载环境变量
        print("\n[1] 加载.env配置...")
        env_vars = load_env_file()
        print(f"   提供商: {env_vars.get('LLM_PROVIDER')}")
        print(f"   模型: {env_vars.get('LLM_MODEL')}")
        print(f"   Base URL: {env_vars.get('LLM_BASE_URL')}")
        
        # 2. 创建客户端
        print("\n[2] 初始化LLM客户端...")
        client = LLMClient(env_vars)
        
        # 3. 准备对话消息
        messages = [
            {"role": "system", "content": "你是一个有帮助的AI助手。"},
            {"role": "user", "content": "请用一句话介绍Python编程语言。"}
        ]
        
        # 4. 发送请求
        print("\n[3] 发送请求...")
        print(f"   用户: {messages[1]['content']}")
        print("-" * 60)
        
        result = client.chat(messages)
        
        # 5. 显示结果
        print("\n[4] 响应结果:")
        print(f"   AI回复: {result['content']}")
        print("-" * 60)
        
        # 6. 显示统计信息
        print("\n[5] 统计信息:")
        print(f"   输入Token:  {result['input_tokens']}")
        print(f"   输出Token:  {result['output_tokens']}")
        print(f"   总Token:    {result['total_tokens']}")
        print(f"   耗时:       {result['elapsed_time']} 秒")
        print(f"   Token速度:  {result['tokens_per_second']} tokens/秒")
        
        print("\n" + "=" * 60)
        print("调用成功!")
        print("=" * 60)
        
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
