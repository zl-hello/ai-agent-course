"""
调试 Agent 配置
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
print("调试 Agent 配置")
print("=" * 60)

# 导入并加载环境变量
from agent_with_skills import load_env_file

print("\n1. 加载环境变量...")
env_vars = load_env_file()

print("\n2. 环境变量内容:")
for key, value in env_vars.items():
    if 'KEY' in key or 'API' in key:
        print(f"  {key} = {value[:30]}...")
    else:
        print(f"  {key} = {value}")

print("\n3. 创建 SkillsAgent...")
from agent_with_skills import SkillsAgent

try:
    agent = SkillsAgent(env_vars)
    
    print("\n4. Agent 配置:")
    print(f"  model: {agent.model}")
    print(f"  base_url: {agent.base_url}")
    print(f"  host: {agent.host}")
    print(f"  api_key: {agent.api_key[:30]}..." if agent.api_key else "  api_key: None")
    print(f"  is_local_model: {agent.is_local_model}")
    
    print("\n[OK] Agent 创建成功！")
    
except Exception as e:
    print(f"\n[FAIL] Agent 创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
