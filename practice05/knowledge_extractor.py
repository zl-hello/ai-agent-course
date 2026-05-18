"""
Practice 05: 关键信息提取模块
每5次聊天提取一次关键信息，按照5W规则记录到本地文件
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


class KnowledgeExtractor:
    """关键信息提取器"""
    
    def __init__(self, log_file_path: str = None):
        if log_file_path is None:
            # 默认使用项目目录下的 chat-log/log.txt
            base_dir = os.path.dirname(os.path.abspath(__file__))
            log_file_path = os.path.join(base_dir, 'chat-log', 'log.txt')
        self.log_file_path = log_file_path
        self.extraction_interval = 5  # 每5次聊天提取一次
        self.chat_count = 0
        self.pending_messages = []  # 待提取的消息缓冲区
        
        # 确保日志目录存在
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """确保日志目录存在"""
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def add_message(self, role: str, content: str) -> Optional[Dict[str, Any]]:
        """
        添加消息到缓冲区，达到阈值时触发提取
        
        Args:
            role: 消息角色 (user/assistant)
            content: 消息内容
            
        Returns:
            达到提取阈值时返回提取结果，否则返回None
        """
        self.pending_messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 只统计用户消息作为触发条件
        if role == "user":
            self.chat_count += 1
            
            # 达到提取阈值
            if self.chat_count >= self.extraction_interval:
                return self._extract_and_save()
         
        return None
    
    def _extract_and_save(self) -> Dict[str, Any]:
        """
        提取关键信息并保存到日志文件
        
        Returns:
            提取结果字典
        """
        # 构建提取提示
        extraction_prompt = self._build_extraction_prompt()
        
        # 清空计数器和缓冲区
        self.chat_count = 0
        messages_to_extract = self.pending_messages.copy()
        self.pending_messages = []
        
        return {
            "should_extract": True,
            "messages": messages_to_extract,
            "extraction_prompt": extraction_prompt,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_extraction_prompt(self) -> str:
        """构建关键信息提取提示"""
        prompt = """请从以下对话中提取关键信息，按照5W规则进行分析：

5W规则：
- Who (谁): 涉及的人物、角色、用户
- What (做了什么): 具体的事件、行为、操作
- When (何时): 时间信息（如果有）
- Where (何地): 地点信息（如果有）
- Why (为什么): 目的、原因、动机（如果有）

待分析的对话：
"""
        
        for msg in self.pending_messages:
            role = "用户" if msg["role"] == "user" else "AI"
            prompt += f"\n{role}: {msg['content']}"
        
        prompt += """

请提取关键信息，以JSON格式返回：
{
    "extractions": [
        {
            "who": "涉及的人物",
            "what": "具体事件",
            "when": "时间（可选）",
            "where": "地点（可选）",
            "why": "原因（可选）",
            "confidence": "置信度(high/medium/low)"
        }
    ]
}

注意：
1. 可以提取多条关键信息
2. 如果某个字段不确定，可以填"unknown"或省略
3. 只提取重要、有价值的信息
4. 确保信息准确，不要编造"""
        
        return prompt
    
    def save_extractions(self, extractions: List[Dict[str, Any]], 
                        original_messages: List[Dict]) -> bool:
        """
        将提取的关键信息保存到日志文件
        
        Args:
            extractions: 提取的关键信息列表
            original_messages: 原始消息列表
            
        Returns:
            是否保存成功
        """
        try:
            # 确保日志目录存在
            self._ensure_log_directory()
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "original_messages": original_messages,
                "extractions": extractions
            }
            
            # 追加写入日志文件
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            return True
            
        except Exception as e:
            print(f"[错误] 保存关键信息失败: {e}")
            return False
    
    def read_log_file(self) -> List[Dict[str, Any]]:
        """
        读取日志文件中的所有记录
        
        Returns:
            日志记录列表
        """
        if not os.path.exists(self.log_file_path):
            return []
        
        records = []
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            record = json.loads(line)
                            records.append(record)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"[错误] 读取日志文件失败: {e}")
        
        return records
    
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        在知识库中搜索相关信息
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的记录列表
        """
        records = self.read_log_file()
        results = []
        
        query_lower = query.lower()
        
        for record in records:
            # 在提取的关键信息中搜索
            for extraction in record.get("extractions", []):
                # 检查所有5W字段
                for field in ["who", "what", "when", "where", "why"]:
                    value = extraction.get(field, "")
                    if value and value != "unknown":
                        if query_lower in str(value).lower():
                            results.append({
                                "record": record,
                                "matched_extraction": extraction,
                                "matched_field": field,
                                "matched_value": value
                            })
                            break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取提取统计信息"""
        records = self.read_log_file()
        total_extractions = sum(len(r.get("extractions", [])) for r in records)
        
        return {
            "log_file_path": self.log_file_path,
            "total_records": len(records),
            "total_extractions": total_extractions,
            "extraction_interval": self.extraction_interval,
            "current_chat_count": self.chat_count,
            "pending_messages": len(self.pending_messages)
        }


# 工具定义，用于LLM调用
KNOWLEDGE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_chat_history",
            "description": "搜索聊天历史记录中的关键信息。当用户发送'/search'开头的消息，或表达查找聊天历史的意图时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或查询内容"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def search_chat_history(query: str, extractor: KnowledgeExtractor) -> Dict[str, Any]:
    """
    搜索聊天历史工具函数
    
    Args:
        query: 搜索查询
        extractor: 知识提取器实例
        
    Returns:
        搜索结果
    """
    results = extractor.search_knowledge(query)
    
    if not results:
        return {
            "success": True,
            "found": False,
            "message": f"未找到与'{query}'相关的历史记录",
            "results": []
        }
    
    # 格式化搜索结果
    formatted_results = []
    for r in results:
        extraction = r["matched_extraction"]
        formatted_results.append({
            "who": extraction.get("who", "unknown"),
            "what": extraction.get("what", "unknown"),
            "when": extraction.get("when", "unknown"),
            "where": extraction.get("where", "unknown"),
            "why": extraction.get("why", "unknown"),
            "matched_field": r["matched_field"],
            "timestamp": r["record"].get("timestamp", "unknown")
        })
    
    return {
        "success": True,
        "found": True,
        "query": query,
        "total_matches": len(results),
        "results": formatted_results
    }


if __name__ == "__main__":
    # 测试知识提取器
    print("=" * 60)
    print("测试知识提取模块")
    print("=" * 60)
    
    extractor = KnowledgeExtractor()
    
    # 模拟添加消息
    test_messages = [
        ("user", "你好，我叫张三"),
        ("assistant", "你好张三！很高兴认识你。"),
        ("user", "我想创建一个项目计划"),
        ("assistant", "好的，请告诉我项目的详细信息。"),
        ("user", "项目要在下周一开始，地点在北京"),
    ]
    
    for role, content in test_messages:
        result = extractor.add_message(role, content)
        print(f"添加消息: {role} - {content[:30]}...")
        if result:
            print(f"触发提取！")
            print(f"提取提示: {result['extraction_prompt'][:200]}...")
    
    print("\n统计信息:")
    stats = extractor.get_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
