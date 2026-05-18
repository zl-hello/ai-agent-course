"""
Practice 07: 链式工具调用模块
实现链式工具调用的完整流程
"""

import json
import re
from typing import Dict, Any, List, Optional, Callable, Generator
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChainedCallContext:
    """
    链式调用上下文管理器
    用于在多个工具调用之间传递数据和状态
    """
    # 用户原始请求
    user_request: str
    
    # 调用历史记录
    call_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # 中间变量存储
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # 当前迭代次数
    current_iteration: int = 0
    
    # 最大迭代次数（防止无限循环）
    max_iterations: int = 10
    
    # 是否完成
    is_completed: bool = False
    
    # 最终结果
    final_result: Optional[str] = None
    
    # 消息历史（用于LLM对话）
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化消息历史"""
        if not self.messages:
            self.messages = []
    
    def add_call_record(self, tool_name: str, parameters: Dict[str, Any], 
                       result: Dict[str, Any]) -> None:
        """
        添加调用记录
        
        Args:
            tool_name: 工具名称
            parameters: 调用参数
            result: 执行结果
        """
        record = {
            "step": self.current_iteration + 1,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "success": result.get("success", False)
        }
        self.call_history.append(record)
        self.current_iteration += 1
        
        # 存储结果到变量（供后续步骤使用）
        var_name = f"{tool_name}_result"
        self.variables[var_name] = result
    
    def set_variable(self, name: str, value: Any) -> None:
        """设置中间变量"""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """获取中间变量"""
        return self.variables.get(name, default)
    
    def has_reached_max_iterations(self) -> bool:
        """检查是否达到最大迭代次数"""
        return self.current_iteration >= self.max_iterations
    
    def mark_completed(self, final_result: str) -> None:
        """标记任务完成"""
        self.is_completed = True
        self.final_result = final_result
    
    def get_execution_summary(self) -> str:
        """获取执行摘要"""
        summary = f"链式调用执行摘要:\n"
        summary += f"  用户请求: {self.user_request}\n"
        summary += f"  执行步骤: {self.current_iteration}/{self.max_iterations}\n"
        summary += f"  完成状态: {'已完成' if self.is_completed else '未完成'}\n"
        
        if self.call_history:
            summary += f"\n  调用历史:\n"
            for record in self.call_history:
                status = "[OK]" if record["success"] else "[FAIL]"
                summary += f"    步骤 {record['step']}: {status} {record['tool_name']}\n"
        
        return summary
    
    def build_analysis_prompt(self) -> str:
        """
        构建分析提示词（包含用户请求和已执行的步骤历史）
        
        Returns:
            分析提示词
        """
        prompt = f"""你是一个智能助手，需要通过链式工具调用来完成用户的请求。

## 用户原始请求
{self.user_request}

## 已执行的工具调用历史
"""
        
        if self.call_history:
            for record in self.call_history:
                prompt += f"\n### 步骤 {record['step']}: {record['tool_name']}\n"
                prompt += f"- 工具名: {record['tool_name']}\n"
                prompt += f"- 参数: {json.dumps(record['parameters'], ensure_ascii=False)}\n"
                
                # 简化结果展示
                result = record['result']
                if result.get('success'):
                    # 提取关键信息
                    if 'content' in result:
                        content = result['content']
                        if len(content) > 200:
                            content = content[:200] + "..."
                        prompt += f"- 结果: {content}\n"
                    elif 'items' in result:
                        items = result['items']
                        prompt += f"- 结果: 找到 {len(items)} 个项目\n"
                    else:
                        prompt += f"- 结果: {json.dumps(result, ensure_ascii=False)}\n"
                else:
                    prompt += f"- 错误: {result.get('error', '未知错误')}\n"
        else:
            prompt += "尚未执行任何工具调用。\n"
        
        prompt += f"""
## 当前状态
- 已执行步骤数: {self.current_iteration}
- 最大允许步骤: {self.max_iterations}
- 可用变量: {list(self.variables.keys())}

## 可用工具列表

1. **list_files**: 列出目录中的文件
   - 参数: directory (目录路径)
   - 返回: items (文件列表)

2. **read_file**: 读取文件内容
   - 参数: directory (目录), filename (文件名)
   - 返回: content (文件内容)

3. **search_chat_history**: 搜索对话历史
   - 参数: query (搜索关键词)
   - 返回: results (搜索结果列表)

4. **generate_summary**: 生成摘要
   - 参数: content (需要摘要的内容)
   - 返回: summary (摘要内容)

5. **load_skill_content**: 加载技能内容
   - 参数: skill_name (技能名称)
   - 返回: content (技能内容)

6. **search_files**: 搜索包含关键词的文件
   - 参数: directory (目录), keyword (关键词)
   - 返回: matches (匹配文件列表)

7. **write_file**: 写入文件
   - 参数: directory (目录), filename (文件名), content (内容)
   - 返回: success (是否成功)

8. **fetch_webpage**: 获取网页内容
   - 参数: url (网页URL)
   - 返回: content (网页内容)

## 决策规则说明

请分析当前状态，决定下一步操作：

1. **如果任务已经完成**，或者你已经获得了足够的信息来回答用户，请返回完成标记
2. **如果任务还未完成**，需要继续调用工具来获取更多信息，请返回工具调用信息
3. **如果需要用户补充信息**，请返回需要信息的标记

## 上下文变量使用方式

- 每个工具的执行结果会自动存储在上下文中
- 变量命名格式：`工具名_result`（如 list_files_result、read_file_result）
- 可用变量列表已在"当前状态"中提供
- 后续工具可以通过变量名引用之前的结果
- 例如：使用 `list_files_result` 获取文件列表

## JSON 输出格式要求

**<1> 完成任务时：**
```json
{{"done": true, "answer": "最终回答内容"}}
```

**<2> 继续调用工具时：**
```json
{{"done": false, "tool_call": {{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}}}
```

**<3> 需要更多信息时：**
```json
{{"done": false, "need_info": "需要询问的问题"}}
```

## 链式调用示例

**示例1：文件搜索链式调用**
```
用户：查找 practice06 目录下所有包含 'def' 关键词的文件，并总结

步骤1: search_files(directory="practice06", keyword="def")
       → 返回: ["agent.py", "tools.py"]

步骤2: read_file(filename="agent.py")
       → 返回: 文件内容

步骤3: generate_summary(content=文件内容)
       → 返回: 摘要

步骤4: 任务完成，返回摘要
```

**示例2：多文件操作**
```
用户：读取 1.txt 和 2.txt，相加后写入 result.txt

步骤1: read_file(filename="1.txt")
       → 返回: content="100"

步骤2: read_file(filename="2.txt")
       → 返回: content="200"

步骤3: write_file(filename="result.txt", content="300")
       → 返回: 成功

步骤4: 任务完成
```

**示例3：网页处理链式调用**
```
用户：访问网页并总结内容，保存到文件

步骤1: fetch_webpage(url="https://example.com")
       → 返回: 网页HTML内容

步骤2: generate_summary(content=网页内容)
       → 返回: 摘要

步骤3: write_file(filename="summary.txt", content=摘要)
       → 返回: 成功

步骤4: 任务完成
```

请直接返回JSON，不要包含其他解释文字。
"""
        
        return prompt


def parse_llm_response(response: str) -> Dict[str, Any]:
    """
    解析LLM响应
    支持新的JSON格式：{"done": true/false, ...}
    
    Args:
        response: LLM响应文本
        
    Returns:
        解析后的字典，统一格式为 {"done": bool, ...}
    """
    # 尝试提取JSON
    try:
        # 查找代码块中的JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # 查找普通JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                # 直接解析整个响应
                data = json.loads(response)
        
        # 统一转换为新的格式
        if "done" in data:
            # 已经是新格式
            return data
        elif "action" in data:
            # 旧格式转换为新格式
            action = data.get("action")
            if action == "complete":
                return {
                    "done": True,
                    "answer": data.get("answer", "任务完成")
                }
            elif action == "call_tool":
                return {
                    "done": False,
                    "tool_call": {
                        "name": data.get("tool_name"),
                        "arguments": data.get("parameters", {})
                    }
                }
            elif action == "need_info":
                return {
                    "done": False,
                    "need_info": data.get("question", "需要更多信息")
                }
        
        return data
        
    except json.JSONDecodeError:
        # 如果不是JSON，返回完成格式
        return {
            "done": True,
            "answer": response
        }


def execute_chained_tool_call(
    user_request: str,
    tool_executor: Callable[[str, Dict[str, Any]], Dict[str, Any]],
    llm_caller: Callable[[List[Dict[str, str]]], str],
    system_prompt: str = "",
    max_iterations: int = 10
) -> Dict[str, Any]:
    """
    执行链式工具调用的完整流程
    
    Args:
        user_request: 用户请求
        tool_executor: 工具执行函数
        llm_caller: LLM调用函数
        system_prompt: 系统提示词
        max_iterations: 最大迭代次数
        
    Returns:
        执行结果
    """
    print(f"\n[链式调用] 开始处理请求: {user_request}")
    print(f"[链式调用] 最大迭代次数: {max_iterations}")
    
    # 初始化上下文
    context = ChainedCallContext(
        user_request=user_request,
        max_iterations=max_iterations
    )
    
    # <1> 初始化消息历史，包含 system prompt
    if system_prompt:
        context.messages.append({"role": "system", "content": system_prompt})
    
    # <2> 循环最多 max_iterations 次
    while not context.has_reached_max_iterations():
        print(f"\n[迭代 {context.current_iteration + 1}/{max_iterations}]")
        
        # - 构建分析提示词（包含用户请求和已执行的步骤历史）
        analysis_prompt = context.build_analysis_prompt()
        
        # - 调用 LLM 决定下一步操作
        context.messages.append({"role": "user", "content": analysis_prompt})
        
        print("  调用 LLM 分析...")
        llm_response = llm_caller(context.messages)
        
        context.messages.append({"role": "assistant", "content": llm_response})
        
        # - 解析 LLM 响应（支持新的 JSON 格式）
        decision = parse_llm_response(llm_response)
        
        done = decision.get("done", True)
        
        print(f"  LLM 决定: {'完成' if done else '继续调用'}")
        
        # - 如果任务完成，返回最终回答
        if done:
            answer = decision.get("answer", "任务完成")
            context.mark_completed(answer)
            print(f"  [OK] 任务完成")
            break
        
        # - 如果需要更多信息
        elif "need_info" in decision:
            question = decision.get("need_info", "需要更多信息")
            context.mark_completed(f"需要更多信息: {question}")
            print(f"  [INFO] 需要更多信息: {question}")
            break
        
        # - 如果需继续调用，执行工具并记录到上下文
        elif "tool_call" in decision:
            tool_call = decision.get("tool_call", {})
            tool_name = tool_call.get("name")
            parameters = tool_call.get("arguments", {})
            
            if not tool_name:
                print(f"  [WARN] 工具名称缺失")
                break
            
            print(f"  执行工具: {tool_name}")
            print(f"  参数: {json.dumps(parameters, ensure_ascii=False)}")
            
            try:
                result = tool_executor(tool_name, parameters)
                
                # 记录到上下文
                context.add_call_record(tool_name, parameters, result)
                
                if result.get("success"):
                    print(f"  [OK] 工具执行成功")
                else:
                    print(f"  [FAIL] 工具执行失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                context.add_call_record(tool_name, parameters, error_result)
                print(f"  [ERROR] 工具执行异常: {e}")
        
        else:
            print(f"  [WARN] 无法解析 LLM 决策")
            break
    
    # 检查是否达到最大迭代次数
    if context.has_reached_max_iterations() and not context.is_completed:
        context.mark_completed("达到最大迭代次数，任务未完成")
        print(f"\n[WARN] 达到最大迭代次数 ({max_iterations})")
    
    print(f"\n[链式调用] 执行完成")
    print(context.get_execution_summary())
    
    return {
        "success": context.is_completed,
        "final_result": context.final_result,
        "call_history": context.call_history,
        "iterations": context.current_iteration,
        "variables": context.variables
    }


# 工具定义
CHAINED_TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "execute_chained_tool_call",
            "description": "执行链式工具调用，通过多步骤工具调用来完成复杂任务。前一个工具的输出作为后一个工具的输入。",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_request": {
                        "type": "string",
                        "description": "用户的完整请求描述"
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "最大迭代次数，防止无限循环",
                        "default": 10
                    }
                },
                "required": ["user_request"]
            }
        }
    }
]


if __name__ == "__main__":
    # 测试链式工具调用
    print("=" * 60)
    print("测试链式工具调用")
    print("=" * 60)
    
    # 模拟工具执行函数
    def mock_tool_executor(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        print(f"    [模拟执行] {tool_name}({params})")
        
        if tool_name == "list_files":
            return {
                "success": True,
                "items": [
                    {"name": "README.md", "type": "file"},
                    {"name": "agent.py", "type": "file"},
                    {"name": "utils", "type": "directory"}
                ]
            }
        elif tool_name == "read_file":
            return {
                "success": True,
                "content": "# README\n\nThis is a test file."
            }
        
        return {"success": True, "result": "mock result"}
    
    # 模拟 LLM 调用函数（使用新的 JSON 格式）
    def mock_llm_caller(messages: List[Dict[str, str]]) -> str:
        # 模拟 LLM 的决策
        user_msg = messages[-1]["content"]
        
        if "list_files" not in str(messages):
            # 第一步：列出文件
            return '''```json
{"done": false, "tool_call": {"name": "list_files", "arguments": {"directory": "."}}}
```'''
        elif "read_file" not in str(messages):
            # 第二步：读取文件
            return '''```json
{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": ".", "filename": "README.md"}}}
```'''
        else:
            # 完成任务
            return '''```json
{"done": true, "answer": "目录中包含 README.md、agent.py 和 utils 目录。README.md 的内容是：'# README\\n\\nThis is a test file.'"}
```'''
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="分析当前目录并读取 README 文件",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手。",
        max_iterations=5
    )
    
    print("\n最终结果:")
    print(result["final_result"])
