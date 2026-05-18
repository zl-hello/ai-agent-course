"""
测试 Practice 05 Agent 功能
非交互式版本，直接测试功能
"""

import sys
sys.path.insert(0, 'practice05')

from agent_with_knowledge import load_env_file, KnowledgeAgent

def test_agent():
    """测试 Agent 功能"""
    print("=" * 60)
    print("Practice 05: 测试知识提取和搜索功能")
    print("=" * 60)
    
    # 加载环境变量
    env_vars = load_env_file()
    print(f"\n[配置] 模型: {env_vars.get('LLM_MODEL', 'unknown')}")
    print(f"[配置] API地址: {env_vars.get('LLM_BASE_URL', 'unknown')}")
    
    # 创建 Agent
    agent = KnowledgeAgent(env_vars)
    print(f"\n[状态] Agent 创建成功")
    print(f"[状态] 本地模型: {agent.is_local_model}")
    print(f"[状态] 历史消息: {len(agent.conversation_history)} 条")
    
    # 测试聊天
    print("\n" + "-" * 60)
    print("测试 1: 普通对话")
    print("-" * 60)
    
    test_messages = [
        "你好，我是张三",
        "我今天在学习 Python",
        "我的目标是成为一名程序员",
        "我计划每天学习 2 小时",
        "你觉得这个计划怎么样？"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n[测试 {i}/5]")
        print(f"[用户] {msg}")
        print("[AI] ", end="", flush=True)
        
        try:
            result = agent.chat(msg)
            print()  # 换行
            
            # 显示提取信息
            if result.get('extraction') and result['extraction'].get('extracted'):
                print(f"\n[知识提取] 已提取 {result['extraction']['count']} 条关键信息")
                
        except Exception as e:
            print(f"\n[错误] {e}")
            return
    
    # 测试搜索功能
    print("\n" + "-" * 60)
    print("测试 2: 搜索功能")
    print("-" * 60)
    
    search_tests = [
        "/search 张三",
        "查找关于 Python 的内容"
    ]
    
    for search_msg in search_tests:
        print(f"\n[用户] {search_msg}")
        print("[AI] ", end="", flush=True)
        
        try:
            result = agent.chat(search_msg)
            print()
        except Exception as e:
            print(f"\n[错误] {e}")
    
    # 显示统计
    print("\n" + "=" * 60)
    print("测试完成 - 统计信息")
    print("=" * 60)
    
    stats = agent.get_knowledge_stats()
    print(f"\n日志文件: {stats['log_file_path']}")
    print(f"总记录数: {stats['total_records']}")
    print(f"总提取数: {stats['total_extractions']}")
    print(f"当前聊天计数: {stats['current_chat_count']}")
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_agent()
