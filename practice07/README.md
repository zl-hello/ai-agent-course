# Practice 07: 链式工具调用 Agent

基于 Practice 06 的技能管理 Agent，实现链式工具调用（Chained Tool Calls）功能。

## 教学目标

1. **理解链式工具调用概念**
   - 前一个工具的输出作为后一个工具的输入参数
   - LLM 根据中间结果自主决定下一步工具调用

2. **实现工具链管理**
   - 定义工具链结构（ToolChain、ToolNode）
   - 实现工具链的自动检测和执行
   - 处理工具间的数据传递

3. **掌握复杂任务分解**
   - 将复杂任务分解为多个工具调用步骤
   - 实现工具调用的依赖管理
   - 处理工具链执行的错误和异常

## 核心概念

### 链式工具调用

链式工具调用允许 LLM 执行多步骤任务，其中：

```
用户输入: "分析目录 ./docs 并读取第一个文件"

步骤1: list_files(directory="./docs")
       ↓ 输出: ["file1.txt", "file2.txt", "dir1"]
       
步骤2: read_file(filename="file1.txt")
       ↓ 使用步骤1的输出
       
最终结果: 文件内容
```

### 工具链结构

```python
ToolChain:
  - name: 工具链名称
  - description: 描述
  - trigger_keywords: 触发关键词
  - nodes: 工具节点列表
    
ToolNode:
  - tool_name: 工具名称
  - parameters: 参数（支持模板）
  - depends_on: 依赖的前一个节点
  - output_mapping: 输出到参数的映射
```

## 项目结构

```
practice07/
├── agent_with_skills.py    # 主程序（集成链式工具调用）
├── chained_tools.py        # 链式工具调用模块
├── skills_manager.py       # 技能管理模块
├── README.md              # 说明文档
├── start.bat              # Windows 启动脚本
└── 使用说明.txt            # 中文使用说明

agents/skills/             # 技能目录
├── code_analysis/SKILL.md
├── file_operations/SKILL.md
├── notice/SKILL.md
└── web_search/SKILL.md
```

## 文件说明

### chained_tools.py

链式工具调用的核心实现：

- **ChainExecutor**: 链式执行器，管理工具链的注册和执行
- **ToolChain**: 工具链数据类，定义工具链结构
- **ToolNode**: 工具节点数据类，定义单个工具调用
- **execute_chained_tool**: 链式工具执行函数

### agent_with_skills.py

主程序，集成链式工具调用：

- 支持技能管理（Practice 06 功能）
- 支持链式工具调用（Practice 07 新增）
- 自动检测用户意图，选择合适的工具链
- 执行工具链并返回结果

## 内置工具链

### 1. analyze_and_read（分析并读取）

**触发词**: "分析目录"、"查看目录内容"、"读取目录文件"

**流程**:
1. `list_files(directory)` - 列出目录中的所有文件
2. `read_file(filename)` - 读取第一个文本文件

**示例**:
```
用户: 分析目录 ./practice07 并读取文件

AI: [执行链式工具]
    [节点] list_files: 列出目录中的所有文件
        参数: {"directory": "./practice07"}
        ✅ 成功
    
    [节点] read_file: 读取第一个文本文件
        参数: {"directory": "./practice07", "filename": "README.md"}
        ✅ 成功

[链式调用] 执行完成: 2/2 成功, 0 失败
```

### 2. search_and_summarize（搜索并总结）

**触发词**: "搜索历史"、"查找记录"、"总结历史"

**流程**:
1. `search_chat_history(query)` - 搜索聊天历史
2. `generate_summary(content)` - 生成搜索结果摘要

**示例**:
```
用户: 搜索历史关于通知的内容并总结

AI: [执行链式工具]
    [节点] search_history: 搜索聊天历史
        参数: {"query": "通知"}
        ✅ 成功
    
    [节点] summarize: 生成搜索结果摘要
        参数: {"content": [...]}
        ✅ 成功
```

### 3. skill_and_execute（技能执行）

**触发词**: "使用技能"、"按技能执行"、"根据技能"

**流程**:
1. `load_skill_content(skill_name)` - 加载技能内容
2. `process_with_context(context, task)` - 使用技能上下文处理任务

**示例**:
```
用户: 使用 notice 技能帮我写个放假通知

AI: [执行链式工具]
    [节点] load_skill: 加载技能内容
        参数: {"skill_name": "notice"}
        ✅ 成功
    
    [节点] execute_with_skill: 使用技能上下文处理任务
        ✅ 成功
```

## 使用方法

### 1. 配置环境

确保项目根目录有 `.env` 文件：
```bash
# 复制示例文件
copy .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
```

### 2. 运行程序

**Windows（推荐）**:
```bash
# 双击 start.bat 文件
# 或在 PowerShell 中执行：
cd practice07
.\start.bat
```

**命令行**:
```bash
cd practice07
python agent_with_skills.py
```

### 3. 测试链式工具

#### 测试1: 分析目录并读取文件
```
👤 你: 分析目录 ./practice07 并读取文件

🤖 AI: [执行链式工具]
    [节点] list_files: 列出目录中的所有文件
        参数: {"directory": "./practice07"}
        ✅ 成功
        找到 5 个文件/目录
    
    [节点] read_file: 读取第一个文本文件
        参数: {"filename": "README.md"}
        ✅ 成功
        读取了文件内容 (1234 字符)

[链式调用] 执行完成: 2/2 成功

文件内容如下：
...
```

#### 测试2: 搜索历史并总结
```
👤 你: 搜索历史关于通知的内容并总结

🤖 AI: [执行链式工具]
    [节点] search_history: 搜索聊天历史
        参数: {"query": "通知"}
        ✅ 成功
        找到 3 条相关记录
    
    [节点] summarize: 生成搜索结果摘要
        ✅ 成功

摘要：
用户之前询问过关于通知撰写的问题，包括...
```

#### 测试3: 使用技能
```
👤 你: 使用 notice 技能帮我写个五一放假通知

🤖 AI: [执行链式工具]
    [节点] load_skill: 加载技能内容
        参数: {"skill_name": "notice"}
        ✅ 成功
    
    [节点] execute_with_skill: 使用技能上下文处理任务
        ✅ 成功

XX部通知

各位同事：

根据国家法定节假日安排...
```

## 核心代码解析

### 链式执行器

```python
class ChainExecutor:
    def __init__(self, tool_executor):
        self.tool_executor = tool_executor
        self.chains = {}
    
    def execute_chain(self, chain, context):
        """执行工具链"""
        node_results = {}
        
        for node in chain.nodes:
            # 解析参数（支持模板和引用）
            resolved_params = self._resolve_parameter(
                node.parameters, context, node_results
            )
            
            # 执行工具
            result = self.tool_executor(node.tool_name, resolved_params)
            node_results[node.node_id] = result
        
        return {"completed": True, "node_results": node_results}
```

### 参数解析

```python
def _resolve_parameter(self, value, context, node_results):
    """解析参数值，处理模板和引用"""
    if isinstance(value, str):
        # 处理 {variable} 模板
        if value.startswith("{") and value.endswith("}"):
            var_name = value[1:-1]
            
            # 从上下文查找
            if var_name in context:
                return context[var_name]
            
            # 从节点结果查找
            for result in node_results.values():
                if var_name in result:
                    return result[var_name]
    
    return value
```

## 扩展工具链

你可以轻松添加新的工具链：

```python
def _register_default_chains(self):
    # 添加新的工具链
    self.register_chain(ToolChain(
        name="my_custom_chain",
        description="自定义工具链",
        trigger_keywords=["关键词1", "关键词2"],
        nodes=[
            ToolNode(
                node_id="step1",
                tool_name="tool_a",
                parameters={"input": "{user_input}"},
                description="第一步"
            ),
            ToolNode(
                node_id="step2",
                tool_name="tool_b",
                parameters={"data": "{step1_result}"},
                description="第二步",
                depends_on="step1"
            )
        ]
    ))
```

## 注意事项

1. **依赖管理**: 确保工具节点的 `depends_on` 指向正确的节点ID
2. **参数映射**: 使用 `{}` 语法引用上下文变量或前面节点的输出
3. **错误处理**: 工具链执行过程中任何一个节点失败，后续节点将不会执行
4. **循环依赖**: 避免创建循环依赖的工具链

## 下一步学习

- 添加更多基础工具（如文件操作、网络请求等）
- 实现条件分支（根据中间结果选择不同的后续工具）
- 支持并行执行（多个独立工具同时执行）
- 添加工具链的可视化展示
