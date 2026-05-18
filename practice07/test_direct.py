"""
直接测试 API 调用
"""
import os
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("直接测试 API 调用")
print("=" * 60)

from agent_with_skills import load_env_file, SkillsAgent, create_llm_request, non_stream_llm_response

# 加载配置
print("\n1. 加载配置...")
env_vars = load_env_file()
print(f"   LLM_BASE_URL: {env_vars.get('LLM_BASE_URL')}")
print(f"   LLM_MODEL: {env_vars.get('LLM_MODEL')}")

# 创建 Agent
print("\n2. 创建 Agent...")
agent = SkillsAgent(env_vars)
print(f"   agent.base_url: {agent.base_url}")
print(f"   agent.host: {agent.host}")
print(f"   agent.model: {agent.model}")

# 测试 API 调用
print("\n3. 测试 API 调用...")
messages = [
    {"role": "system", "content": "你是一个 helpful assistant."},
    {"role": "user", "content": "你好"}
]

request_config = create_llm_request(
    messages=messages,
    model=agent.model,
    api_key=agent.api_key,
    base_url=agent.base_url,
    tools=None,
    stream=False
)

print(f"   request_config['host']: {request_config['host']}")
print(f"   request_config['path']: {request_config['path']}")

print("\n4. 发送请求...")
try:
    response = non_stream_llm_response(request_config)
    print(f"   响应: {response}")
    print("\n[OK] API 调用成功!")
except Exception as e:
    print(f"\n[FAIL] API 调用失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
