"""
调试测试 - 检查知识提取功能
"""

import sys
sys.path.insert(0, 'practice05')

from knowledge_extractor import KnowledgeExtractor

def test_extractor():
    """测试提取器"""
    print("=" * 60)
    print("测试知识提取器")
    print("=" * 60)
    
    extractor = KnowledgeExtractor()
    
    print(f"\n初始状态:")
    print(f"  聊天计数: {extractor.chat_count}")
    print(f"  待处理消息: {len(extractor.pending_messages)}")
    print(f"  提取间隔: {extractor.extraction_interval}")
    
    # 添加 5 条用户消息
    for i in range(1, 6):
        print(f"\n添加第 {i} 条用户消息...")
        result = extractor.add_message("user", f"测试消息 {i}")
        print(f"  聊天计数: {extractor.chat_count}")
        print(f"  待处理消息: {len(extractor.pending_messages)}")
        print(f"  触发提取: {result is not None}")
        
        if result:
            print(f"  提取提示长度: {len(result.get('extraction_prompt', ''))}")
            print(f"  待提取消息数: {len(result.get('messages', []))}")
    
    # 检查日志文件
    print(f"\n日志文件路径: {extractor.log_file_path}")
    stats = extractor.get_stats()
    print(f"\n统计信息:")
    print(f"  总记录数: {stats['total_records']}")
    print(f"  总提取数: {stats['total_extractions']}")

if __name__ == "__main__":
    test_extractor()
