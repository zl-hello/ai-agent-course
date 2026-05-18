"""
测试完整的知识提取流程
"""

import sys
sys.path.insert(0, 'practice05')

from agent_with_knowledge import load_env_file, KnowledgeAgent

def test_full_extraction():
    """测试完整提取流程"""
    print("=" * 60)
    print("测试完整知识提取流程")
    print("=" * 60)
    
    # 加载环境变量
    env_vars = load_env_file()
    
    # 创建 Agent
    agent = KnowledgeAgent(env_vars)
    
    print(f"\n初始状态:")
    stats = agent.get_knowledge_stats()
    print(f"  聊天计数: {stats['current_chat_count']}")
    print(f"  待处理消息: {stats['pending_messages']}")
    print(f"  总记录数: {stats['total_records']}")
    
    # 发送 5 条消息触发提取
    test_messages = [
        "你好，我是李四",
        "我在学习人工智能",
        "我的目标是成为一名AI工程师",
        "我计划每天晚上学习2小时",
        "你能给我一些建议吗？"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n[{i}/5] 用户: {msg}")
        print("AI: ", end="", flush=True)
        
        try:
            result = agent.chat(msg)
            print()  # 换行
            
            # 显示提取信息
            if result.get('extraction') and result['extraction'].get('extracted'):
                print(f"\n[知识提取成功] 已提取 {result['extraction']['count']} 条关键信息")
            
            # 显示当前状态
            stats = agent.get_knowledge_stats()
            print(f"[状态] 聊天计数: {stats['current_chat_count']}, 总记录数: {stats['total_records']}")
            
        except Exception as e:
            print(f"\n[错误] {e}")
            import traceback
            traceback.print_exc()
            return
    
    # 最终统计
    print("\n" + "=" * 60)
    print("最终统计")
    print("=" * 60)
    stats = agent.get_knowledge_stats()
    print(f"日志文件: {stats['log_file_path']}")
    print(f"总记录数: {stats['total_records']}")
    print(f"总提取数: {stats['total_extractions']}")
    print(f"聊天计数: {stats['current_chat_count']}")

if __name__ == "__main__":
    test_full_extraction()
