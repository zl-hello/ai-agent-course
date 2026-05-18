"""
测试真实的链式工具调用（使用真实 API）
"""
import os
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("测试真实链式工具调用")
print("=" * 70)

from agent_with_skills import SkillsAgent, load_env_file

# 加载配置
print("\n1. 加载配置...")
env_vars = load_env_file()
print(f"   API: {env_vars.get('LLM_BASE_URL')}")
print(f"   Model: {env_vars.get('LLM_MODEL')}")

# 创建 Agent
print("\n2. 创建 Agent...")
agent = SkillsAgent(env_vars)
print(f"   已连接到: {agent.model}")

# 测试链式调用
print("\n3. 测试链式调用...")
print("-" * 70)

from chained_tools import execute_chained_tool_call

def tool_executor(tool_name, params):
    """执行基础工具"""
    print(f"   [执行工具] {tool_name}({params})")
    return agent._execute_base_tool(tool_name, params)

def llm_caller(messages):
    """调用 LLM"""
    print(f"   [调用LLM] 消息数: {len(messages)}")
    return agent._call_llm_for_chain(messages)

# 执行链式调用
result = execute_chained_tool_call(
    user_request="列出 practice07 目录的文件，然后读取 README.md 文件",
    tool_executor=tool_executor,
    llm_caller=llm_caller,
    system_prompt="你是一个智能助手，擅长文件操作。",
    max_iterations=5
)

print("\n" + "-" * 70)
print("4. 执行结果:")
print(f"   成功: {result['success']}")
print(f"   迭代次数: {result['iterations']}")
print(f"   最终结果: {result['final_result'][:200]}..." if len(str(result['final_result'])) > 200 else f"   最终结果: {result['final_result']}")

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)
