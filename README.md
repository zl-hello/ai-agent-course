# AI Agent 开发教学项目

本项目是一个循序渐进的 AI 智能体开发教程，通过实践练习帮助学习者掌握构建 AI Agent 的核心技能。

---

## 项目结构

```
zhou4/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python 依赖
├── env.example              # 环境变量模板
├── .gitignore               # Git 排除文件
├── venv/                    # Python 虚拟环境
├── src/                     # 核心源码目录
│   ├── agent/               # 智能体核心模块
│   ├── tools/               # 工具模块
│   └── memory/              # 记忆/向量存储模块
├── practice01/              # 练习 01：HTTP 客户端
├── practice02/              # 练习 02：交互式聊天
├── practice03/              # 练习 03：工具调用
├── practice04/              # 练习 04：记忆压缩
├── practice05/              # 练习 05：知识提取与搜索
├── tests/                   # 测试目录
├── docs/                    # 文档目录
└── config/                  # 配置文件目录
```

---

## 练习目录

### Practice 01: LLM HTTP 客户端

**文件位置**: `practice01/llm_client.py`

#### 功能用途
使用 Python 标准库 `http.client` 实现一个 LLM API 客户端，不依赖第三方库（如 `requests` 或 `openai` SDK），直接与 LLM 提供商的 API 进行 HTTP 通信。

主要功能：
- 从项目根目录的 `.env` 文件读取配置（API Key、模型、Base URL 等）
- 支持多种 LLM 提供商（OpenAI、Anthropic、自定义 API）
- 使用标准 HTTP 库发送 POST 请求
- 解析 JSON 响应并提取 AI 回复内容
- 统计并计算：
  - 输入 Token 数量
  - 输出 Token 数量
  - 总 Token 消耗
  - 请求耗时（秒）
  - Token 生成速度（tokens/秒）

#### 教学目标

1. **环境配置管理**
   - 学习使用 `.env` 文件管理敏感配置（API Key）
   - 理解环境变量与代码分离的重要性

2. **Python 标准库 HTTP 编程**
   - 掌握 `http.client` 模块的基本用法
   - 理解 HTTP 请求/响应流程
   - 学习构建 HTTP 请求头和请求体

3. **LLM API 集成**
   - 了解 OpenAI 和 Anthropic API 的请求/响应格式差异
   - 学习如何适配不同提供商的 API 规范
   - 理解 RESTful API 的设计原则

4. **性能监控基础**
   - 学习使用 `time` 模块测量代码执行时间
   - 理解 Token 消耗统计的意义
   - 掌握基础性能指标的计算方法

5. **代码组织与工程实践**
   - 面向对象编程：封装 LLMClient 类
   - 类型提示（Type Hints）的使用
   - 错误处理与异常管理

#### 使用示例

```bash
# 1. 配置环境变量
cp env.example .env
# 编辑 .env 填入你的 API Key

# 2. 运行练习
python practice01/llm_client.py
```

#### 预期输出

```
============================================================
Practice 01: LLM HTTP Client
============================================================

[1] 加载.env配置...
   提供商: openai
   模型: gpt-3.5-turbo
   Base URL: https://api.openai.com/v1

[2] 初始化LLM客户端...

[3] 发送请求...
   用户: 请用一句话介绍Python编程语言。
------------------------------------------------------------

[4] 响应结果:
   AI回复: Python是一种简洁优雅的高级编程语言...
------------------------------------------------------------

[5] 统计信息:
   输入Token:  25
   输出Token:  18
   总Token:    43
   耗时:       1.234 秒
   Token速度:  14.59 tokens/秒

============================================================
调用成功!
============================================================
```

---

### Practice 02: 交互式终端聊天

**文件位置**: `practice02/interactive_chat.py`

#### 功能用途
构建一个类似 ChatGPT 的交互式终端聊天程序，支持持续对话、流式输出和对话历史管理。

主要功能：
- **交互式终端界面**: 循环接收用户输入，直到用户主动退出
- **流式输出**: AI 回复内容实时逐字显示，提升用户体验
- **历史记录管理**: 自动维护多轮对话上下文
  - 每次对话自动添加到历史
  - 支持 `/clear` 命令清空历史
  - 支持 `/history` 命令查看历史摘要
- **优雅退出**: 支持 `/exit` 命令或 `Ctrl+C` 退出程序
- **命令系统**: 内置常用命令（/clear, /history, /exit）

#### 教学目标

1. **流式数据处理**
   - 理解 HTTP 流式响应（Streaming Response）原理
   - 学习使用 Python 生成器（Generator）处理流式数据
   - 掌握实时输出技术（`flush=True`）

2. **对话状态管理**
   - 理解对话上下文（Context）的重要性
   - 学习维护对话历史列表
   - 掌握 Token 限制与历史裁剪策略

3. **交互式程序设计**
   - 学习构建命令行交互界面
   - 掌握输入循环和命令解析
   - 理解信号处理（Signal Handling）实现优雅退出

4. **用户体验优化**
   - 实时反馈：流式输出减少等待感
   - 状态可见：显示历史记录统计
   - 错误恢复：异常处理和用户提示

5. **程序架构设计**
   - 分离界面层与业务逻辑层
   - 设计可扩展的命令系统
   - 状态封装与管理

#### 使用示例

```bash
# 运行交互式聊天
python practice02/interactive_chat.py
```

#### 预期输出

```
============================================================
🤖 Practice 02: 交互式终端聊天
============================================================

命令:
  /clear  - 清空对话历史
  /history- 查看历史记录
  /exit   - 退出程序
  Ctrl+C  - 强制退出

------------------------------------------------------------
✅ 已连接到: gpt-3.5-turbo
📊 历史: 0 用户消息, 0 AI回复
------------------------------------------------------------

👤 你: 你好，请介绍一下Python
🤖 AI: 你好！Python是一种高级编程语言，由Guido van Rossum于1991年创建。它以简洁、易读的语法著称，强调代码的可读性和简洁性。Python广泛应用于Web开发、数据分析、人工智能、科学计算等领域，拥有丰富的库和框架生态系统。

👤 你: /history
📜 对话历史:
1. 👤 你好，请介绍一下Python
2. 🤖 你好！Python是一种高级编程语言...

👤 你: /exit

👋 再见！
```

#### 支持的命令

| 命令 | 功能 |
|------|------|
| `/clear` | 清空对话历史（保留系统提示） |
| `/history` | 显示对话历史摘要 |
| `/exit` | 退出程序 |
| Ctrl+C | 强制退出程序 |

---

### Practice 03: 工具调用 Agent

**文件位置**: 
- `practice03/agent_with_tools.py` - 主程序
- `practice03/file_tools.py` - 文件工具模块

#### 功能用途
实现 Function Calling（工具调用）功能，让 AI Agent 能够执行本地文件操作。基于 Practice 01 的 HTTP 客户端架构，扩展支持工具定义和调用。

**5个文件操作工具：**

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `list_files` | 列出目录文件 | directory |
| `rename_file` | 重命名文件 | directory, old_name, new_name |
| `delete_file` | 删除文件 | directory, filename |
| `create_file` | 创建文件 | directory, filename, content |
| `read_file` | 读取文件 | directory, filename |

**工作流程：**
1. 用户输入指令（如"帮我创建一个叫test.txt的文件，内容是Hello World"）
2. LLM 分析需求，决定调用哪些工具
3. Agent 执行工具调用
4. 将工具执行结果返回给 LLM
5. LLM 生成最终回复

#### 教学目标

1. **Function Calling 原理**
   - 理解工具定义（Tool Definition）的 JSON Schema 格式
   - 学习 LLM 如何决定调用工具
   - 掌握工具调用与正常对话的区别

2. **工具系统架构**
   - 工具注册与映射机制
   - 参数解析与验证
   - 工具执行与结果处理

3. **多轮对话管理**
   - 处理包含工具调用的复杂对话流程
   - 维护 tool_call_id 关联
   - 构建完整的对话上下文

4. **本地系统集成**
   - Python 文件操作（os 模块）
   - 错误处理与权限管理
   - 安全边界控制

5. **Agent 能力扩展**
   - 从纯对话到行动（从 Say 到 Do）
   - 工具组合使用
   - 任务分解与执行

#### 使用示例

```bash
# 运行工具调用 Agent
python practice03/agent_with_tools.py
```

#### 预期对话

```
============================================================
🛠️  Practice 03: 工具调用 Agent
============================================================

可用工具:
  📁 list_files   - 列出目录文件
  ✏️  rename_file  - 重命名文件
  🗑️  delete_file  - 删除文件
  📝 create_file  - 创建文件
  📖 read_file    - 读取文件

命令:
  /clear  - 清空对话历史
  /history- 查看历史记录
  /exit   - 退出程序
  Ctrl+C  - 强制退出

------------------------------------------------------------
✅ 已连接到: gpt-3.5-turbo
📊 历史: 0 用户消息, 0 AI回复
------------------------------------------------------------

👤 你: 在当前目录创建一个hello.txt文件，内容是"Hello, World!"
🔧 检测到 1 个工具调用
  📋 执行: create_file
     参数: {"directory": "./", "filename": "hello.txt", "content": "Hello, World!"}
  ✅ 成功
🤖 AI: 已成功创建文件 hello.txt，内容为 "Hello, World!"。

👤 你: 列出当前目录的所有文件
🔧 检测到 1 个工具调用
  📋 执行: list_files
     参数: {"directory": "./"}
  ✅ 成功
🤖 AI: 当前目录包含以下文件：
- hello.txt (文件, 14 bytes)
- agent_with_tools.py (文件, 8.5 KB)
- file_tools.py (文件, 6.2 KB)

👤 你: 把hello.txt重命名为greeting.txt
🔧 检测到 1 个工具调用
  📋 执行: rename_file
     参数: {"directory": "./", "old_name": "hello.txt", "new_name": "greeting.txt"}
  ✅ 成功
🤖 AI: 文件已成功重命名为 greeting.txt。
```

#### 工具调用流程图

```
用户输入
    ↓
LLM 分析 → 决定调用工具
    ↓
构建 tool_calls
    ↓
Agent 执行工具
    ↓
返回工具结果
    ↓
LLM 生成回复
    ↓
展示给用户
```

---

### Practice 04: AnythingLLM 查询 Agent

**文件位置**: 
- `practice04/agent_with_tools.py` - 主程序
- `practice04/file_tools.py` - 文件工具模块
- `practice04/anythingllm_tools.py` - AnythingLLM 查询工具模块

#### 功能用途
在 Practice 03 工具调用的基础上，添加 AnythingLLM 文档仓库查询功能。使用 subprocess 调用 curl 命令访问 AnythingLLM API，实现文档知识库的智能查询。

**新增工具：**
| 工具名 | 功能 | 触发条件 |
|--------|------|----------|
| `query_anythingllm` | 查询文档仓库 | 用户提到"文档仓库"、"文件仓库"、"仓库"、"知识库" |

**技术特点：**
- 使用 subprocess 调用 curl 命令
- 支持中文编码（UTF-8）
- 从 `.env` 读取 API 配置
- 自动处理 API 认证

#### 教学目标

1. **外部 API 集成**
   - 学习使用 subprocess 调用系统命令
   - 理解 curl 命令参数和 HTTP 请求构建
   - 掌握 API 密钥管理和环境变量配置

2. **中文编码处理**
   - 理解 Unicode 和 UTF-8 编码
   - 学习处理中文内容的特殊注意事项
   - 掌握 `--data-binary` 与 `-d` 参数的区别

3. **工具系统扩展**
   - 在现有 Agent 中添加新工具
   - 合并多个工具模块
   - 更新系统提示词识别新意图

4. **错误处理与调试**
   - 处理 API 连接错误
   - 解析命令行输出
   - 实现健康检查功能

5. **文档驱动开发**
   - 阅读 API 文档（http://localhost:3001/api/docs/）
   - 根据文档构建请求
   - 处理不同响应格式

#### 查询流程

```
用户输入（包含"文档仓库"等关键词）
    ↓
LLM 识别意图 → 决定调用 query_anythingllm
    ↓
构建 curl 命令
    - URL: /api/v1/workspace/{slug}/chat
    - Header: Authorization: Bearer {api_key}
    - Body: {"message": "...", "mode": "chat"}
    ↓
subprocess.run() 执行 curl
    ↓
解析 JSON 响应
    ↓
提取 textResponse 字段
    ↓
返回查询结果
```

#### 环境配置

在 `.env` 文件中添加：
```bash
# AnythingLLM 配置
ANYTHINGLLM_BASE_URL=http://localhost:3001
ANYTHINGLLM_API_KEY=your-api-key
ANYTHINGLLM_WORKSPACE_SLUG=your-workspace
```

#### 使用示例

```bash
# 运行 AnythingLLM 查询 Agent
python practice04/agent_with_tools.py
```

#### 预期输出

```
============================================================
🛠️  Practice 04: AnythingLLM 查询 Agent
============================================================

可用工具:
  📁 list_files       - 列出目录文件
  ✏️  rename_file      - 重命名文件
  🗑️  delete_file      - 删除文件
  📝 create_file      - 创建文件
  📖 read_file        - 读取文件
  🔍 query_anythingllm- 查询文档仓库

命令:
  /clear  - 清空对话历史
  /history- 查看历史记录
  /exit   - 退出程序
  Ctrl+C  - 强制退出

------------------------------------------------------------
✅ 已连接到: gpt-3.5-turbo
📊 历史: 0 用户消息, 0 AI回复
✅ AnythingLLM: 服务运行正常
------------------------------------------------------------

👤 你: 查询文档仓库中关于 Python 的资料
🔧 检测到 1 个工具调用
  📋 执行: query_anythingllm
     参数: {"message": "Python"}
  ✅ 成功
🤖 AI: 根据文档仓库的查询结果，我找到了以下关于 Python 的资料：
[文档内容...]

👤 你: 在知识库中搜索 API 设计相关内容
🔧 检测到 1 个工具调用
  📋 执行: query_anythingllm
     参数: {"message": "API 设计"}
  ✅ 成功
🤖 AI: 文档仓库中有关于 API 设计的最佳实践文档...
```

---

### Practice 05: 带知识提取和搜索的 Agent

**文件位置**: `practice05/agent_with_knowledge.py`

#### 功能用途
在 Practice 04 的基础上，实现智能知识提取和搜索功能：
1. **自动知识提取**：每5次聊天自动提取关键信息（5W规则）
2. **本地持久化**：将提取的知识保存到 `D:\chat-log\log.txt`
3. **智能搜索**：支持 `/search` 命令和语义化搜索意图识别

**5W规则提取：**
| 字段 | 说明 | 必需 |
|------|------|------|
| Who | 涉及的人物、角色 | 是 |
| What | 具体事件、行为 | 是 |
| When | 时间信息 | 可选 |
| Where | 地点信息 | 可选 |
| Why | 目的、原因 | 可选 |

**搜索触发方式：**
1. `/search 关键词` - 显式搜索命令
2. 语义化触发 - "查找..."、"我记得..."、"之前说过..."
3. LLM 自动判断 - 模型根据上下文决定是否需要搜索

**新增命令：**
| 命令 | 功能 |
|------|------|
| `/stats` | 查看知识提取统计 |
| `/search XXX` | 搜索聊天历史 |

#### 教学目标

1. **结构化信息提取**
   - 学习使用 LLM 进行结构化数据提取
   - 掌握 5W 信息组织方法
   - 理解信息抽取的置信度评估

2. **本地知识库构建**
   - 实现增量式知识存储
   - 学习 JSON Lines 格式存储
   - 掌握文件系统操作与数据持久化

3. **语义搜索实现**
   - 理解关键词匹配 vs 语义搜索
   - 实现多字段联合搜索
   - 掌握搜索结果排序与展示

4. **意图识别**
   - 学习基于规则的意图识别
   - 理解 LLM 意图判断的原理
   - 掌握多层级意图分类

5. **知识增强对话**
   - 将搜索结果融入对话上下文
   - 实现知识引导的回复生成
   - 理解 RAG（检索增强生成）基础

#### 知识提取流程

```
用户发送消息
    ↓
添加到消息缓冲区
    ↓
用户消息计数 +1
    ↓
达到5次? → 是 → 构建5W提取提示
    ↓ 否              ↓
继续对话         调用LLM提取
                    ↓
              解析JSON结果
                    ↓
              追加写入log.txt
                    ↓
              清空缓冲区
```

#### 搜索流程

```
用户输入
    ↓
以/search开头? 或 包含搜索关键词?
    ↓
是 → 提取搜索关键词
    ↓
读取log.txt所有记录
    ↓
在5W字段中匹配关键词
    ↓
返回匹配结果
    ↓
将结果注入对话上下文
    ↓
LLM生成基于知识的回复
```

#### 使用示例

```bash
# 运行带知识提取和搜索的 Agent
python practice05/agent_with_knowledge.py
```

#### 预期输出

```
============================================================
Practice 05: 带知识提取和搜索的 Agent
============================================================

功能特点:
  - 每5次聊天自动提取关键信息（5W规则）
  - 保存到 D:\chat-log\log.txt
  - 支持 /search 命令搜索历史
  - 自动识别搜索意图

命令:
  /clear       - 清空对话历史
  /history     - 查看历史记录
  /stats       - 查看知识提取统计
  /search XXX  - 搜索聊天历史
  /exit        - 退出程序
  Ctrl+C       - 强制退出

------------------------------------------------------------
[OK] 已连接到: qwen-plus
[INFO] 历史: 0 用户消息, 0 AI回复 | 上下文: 272 字符
[INFO] 知识库: 0 条记录, 0 条提取
[INFO] 提取间隔: 每 5 次聊天
------------------------------------------------------------

[你] 你好，我叫张三
[AI] 你好张三！很高兴认识你。

[你] 我在北京工作
[AI] 那很好啊，北京是个大城市。

... (继续对话，达到5次后自动提取) ...

[知识提取] 正在分析对话并提取关键信息...
[知识提取] 已提取并保存 2 条关键信息

[你] /search 张三
[搜索] 正在搜索: 张三
[搜索] 找到 1 条相关记录
[AI] 根据历史记录，张三是你的名字，你在北京工作。

[你] 我之前说过我在哪里工作？
[搜索] 正在搜索: 在哪里工作
[搜索] 找到 1 条相关记录
[AI] 你之前提到过你在北京工作。
```

---

## 快速开始

### 环境准备

```bash
# 1. 激活虚拟环境
.\venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 运行练习

```bash
# Practice 01: HTTP 客户端
python practice01/llm_client.py

# Practice 02: 交互式聊天
python practice02/interactive_chat.py

# Practice 03: 工具调用
python practice03/agent_with_tools.py

# Practice 04: AnythingLLM 查询
python practice04/agent_with_tools.py

# Practice 05: 知识提取与搜索
python practice05/agent_with_knowledge.py

# Practice 06: 技能管理
python practice06/agent_with_skills.py
```

---

## 依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| python-dotenv | >=0.19.0 | 环境变量加载 |
| pydantic | >=1.10.0 | 数据验证 |
| openai | >=1.0.0 | OpenAI API SDK |
| anthropic | >=0.8.0 | Anthropic API SDK |
| chromadb | >=0.4.0 | 向量数据库 |
| sentence-transformers | >=2.2.0 | 文本嵌入模型 |
| pytest | >=7.0.0 | 测试框架 |

---

## 学习路径建议

1. **Practice 01** → 掌握基础 HTTP 通信和 LLM API 调用
2. **Practice 02** → 实现流式输出和对话历史管理
3. **Practice 03** → 实现工具调用（Function Calling）
4. **Practice 04** → 集成 AnythingLLM 文档查询功能
5. **Practice 05** → 实现知识提取与搜索
6. **Practice 06** → 实现技能管理系统
7. **Practice 07** (待添加) → 实现 Agent 决策循环
8. **Practice 08** (待添加) → 多 Agent 协作

---

## 贡献

欢迎提交 Issue 和 PR 来改进教学内容！

---

## 许可证

MIT License
