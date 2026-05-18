"""
测试阿里云百炼 API 调用
"""

import os
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 加载环境变量
from agent_with_skills import load_env_file, create_llm_request, non_stream_llm_response

print("=" * 60)
print("测试阿里云百炼 API")
print("=" * 60)

# 加载配置
env_vars = load_env_file()
base_url = env_vars.get('LLM_BASE_URL', '')
model = env_vars.get('LLM_MODEL', '')
api_key = env_vars.get('LLM_API_KEY', '')

print(f"\nAPI 配置:")
print(f"  Base URL: {base_url}")
print(f"  Model: {model}")
print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: 未设置")

# 构建请求
messages = [
    {"role": "system", "content": "你是一个 helpful assistant."},
    {"role": "user", "content": "你好，请简单介绍一下自己"}
]

print("\n构建请求...")
request_config = create_llm_request(
    messages=messages,
    model=model,
    api_key=api_key,
    base_url=base_url,
    tools=None,
    stream=False
)

print(f"  Host: {request_config['host']}")
print(f"  Path: {request_config['path']}")
print(f"  Request Body: {request_config['body']}")

# 发送请求
print("\n发送 API 请求...")
try:
    response = non_stream_llm_response(request_config)
    
    print("\n响应结果:")
    if "choices" in response and len(response["choices"]) > 0:
        choice = response["choices"][0]
        if "message" in choice:
            content = choice["message"].get("content", "")
            print(f"  AI 回复: {content[:200]}...")
        else:
            print(f"  响应: {choice}")
    else:
        print(f"  完整响应: {response}")
    
    print("\n[OK] API 调用成功！")
    
except Exception as e:
    print(f"\n[FAIL] API 调用失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
