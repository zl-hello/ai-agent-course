"""
测试 chat 方法
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
print("测试 chat 方法")
print("=" * 60)

from agent_with_skills import load_env_file, SkillsAgent

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

# 测试 chat
print("\n3. 测试 chat...")
print("   发送: 你好")
try:
    result = agent.chat("你好")
    print(f"\n   结果: {result}")
    print("\n[OK] chat 成功!")
except Exception as e:
    print(f"\n[FAIL] chat 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
