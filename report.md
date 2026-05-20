**人工智能提示工程**

Prompt Engineering 讲义

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**【核心目标】让同学们明白如何向AI提问，并完成代码实践**

**目 录**

01 什么是提示工程
........................................................... 3

02 提示工程核心概念体系
........................................................... 5

03 基础提示词技巧（角色与结构）
........................................................... 8

04 高级提示词技巧（约束与压缩）
........................................................... 12

05 Function Call：让AI拥有双手
........................................................... 16

06 RAG与上下文管理
........................................................... 20

07 实战：开发你的第一个AI Agent
........................................................... 24

08 课堂互动与现场演示
........................................................... 28

09 课后总结与拓展资源
........................................................... 30

**💡 本讲义标注说明**

【互动提示】→ 演讲者与听众互动环节 【重点标注】→ 核心考点与易错点
【代码实践】→ 现场编程任务

**01 什么是提示工程**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

提示工程（Prompt Engineering）是与大语言模型（LLM）沟通的艺术与科学。

**▶ 1.1 从一个比喻开始**

想象你面对一位全知全能但"有点迷糊"的助手。

-   如果你说："帮我写篇文章" → 助手茫然，不知道写什么

-   如果你说："请以一名资深软件工程师的身份，用Markdown格式撰写一篇关于Python异步编程的技术博客，要求包含代码示例和性能对比表格"
    → 助手立刻精准输出

**01 什么是提示工程**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

提示工程（Prompt Engineering）是与大语言模型（LLM）沟通的艺术与科学。

**▶ 1.1 从一个比喻开始**

想象你面对一位全知全能但"有点迷糊"的助手。

-   如果你说："帮我写篇文章" → 助手茫然，不知道写什么

-   如果你说："请以一名资深软件工程师的身份，用Markdown格式撰写一篇关于Python异步编程的技术博客，要求包含代码示例和性能对比表格"
    → 助手立刻精准输出

> **【核心定义】** 提示工程 =
> 通过精心设计输入文本（Prompt），引导AI生成高质量、符合预期的输出。它不是"欺骗AI"，而是"高效沟通"。

**▶ 1.2 为什么提示工程如此重要？**

-   大语言模型的本质是"下一个词预测器"，它不具备真正的"理解"，而是通过概率计算生成文本

-   同样的模型，不同的提示词，输出质量可能天差地别

-   掌握提示工程 = 掌握了驾驭AI的"方向盘"

> ⭐
> **提示工程不是编程，但比编程更需要逻辑思维；不是写作，但比写作更需要结构化表达。**
>
> **🎤 【互动提示 · 5分钟】**
>
> 请现场同学打开任意AI对话工具（如Kimi、DeepSeek、ChatGPT），输入："写一篇关于春天的文章"和"请以朱自清的散文风格，写一篇800字关于江南春色的抒情散文，要求运用通感修辞手法"，对比两次输出的差异。

**02 提示工程核心概念体系**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 2.1 核心概念速览**

以下概念将在后续课程中逐一深入讲解，先建立整体认知框架：

  **概念**         **英文/缩写**       **一句话解释**
  ---------------- ------------------- ------------------------------------------------------------------
  System Prompt    系统提示词          给AI的"身份设定"和"行为准则"，决定AI以什么角色、什么规则回答问题
  User Prompt      用户提示词          用户直接输入的问题或指令，是AI处理的核心内容
  Token            词元                AI处理文本的最小单位（1个汉字≈1-2个token，1个英文单词≈1个token）
  Context          上下文              AI当前能"看到"的全部对话内容，包括历史消息和系统设定
  Context Length   上下文长度          模型能处理的最大token数（如4K、8K、128K），超限则遗忘
  RAG              检索增强生成        让AI在回答前先查阅外部文档，解决"幻觉"和知识时效问题
  Function Call    函数调用/工具调用   让AI不仅能说话，还能执行代码、查天气、操作文件等

**▶ 2.2 概念关系图**

**【概念关系】**

-   System Prompt + User Prompt → 组成完整输入 → 进入LLM处理

-   LLM输出 → 可能包含Function Call请求 → Agent执行工具 → 结果返回LLM

-   RAG在输入阶段注入外部知识，扩展Context，提升回答准确性

-   Context Length是硬性天花板，超限需压缩或摘要

> **【记忆口诀】**
> 系统定身份，用户提问题，Token算成本，上下文管记忆，RAG查资料，Function动手脚，长度是瓶颈。
>
> ⭐ **Context
> Length是提示工程的"物理天花板"——再强的技巧，也突破不了模型能处理的token上限。**
>
> **🎤 【互动提示 · 3分钟】**
>
> 提问：如果一篇论文有2万字，而你的AI模型Context
> Length只有4K（约3000汉字），你该如何让AI帮你总结这篇论文？（提示：分块、摘要、RAG）

**03 基础提示词技巧（角色与结构）**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 3.1 角色定义法：给AI一个"人设"**

这是提示工程中最基础、最有效的技巧。

-   原理：大模型在预训练时学习了大量"角色-风格-内容"的关联模式

-   效果：指定角色后，AI会自动调用该角色对应的知识库、语言风格和思维方式

> **【对比实验】** 【普通提问】"解释什么是递归" → 教科书式干巴巴的解释\
> 【角色提问】"你是一位擅长用生活化比喻教学的计算机教授，请向大一新生解释什么是递归，要求用"俄罗斯套娃"做比喻，并给出一个Python代码示例"
> → 生动、有深度、有代码

**▶ 3.2 回答框架法：给AI一个"模板"**

告诉AI"我要什么格式"，比告诉AI"我要什么内容"更重要。

-   段落叙述式："请用三段式结构回答：第一段定义，第二段原理，第三段应用案例"

-   表格对比式："请以表格形式对比Python的list、tuple、set三种数据结构，列包含：特性、可变性、适用场景"

-   列表清单式："请列出5个Python性能优化的最佳实践，每条包含：问题描述、优化方案、代码示例"

> \# 角色+框架 组合示例\
> System Prompt:\
> 你是一位经验丰富的Python技术面试官。\
> \
> User Prompt:\
> 请按照以下框架，设计一道关于"Python装饰器"的面试题：\
> 1. 题目背景（50字内）\
> 2. 核心代码（包含一个待完善的装饰器函数）\
> 3. 面试追问清单（3个递进式问题）\
> 4. 参考答案与评分标准
>
> ⭐
> **角色定义解决"谁来答"的问题，框架约束解决"怎么答"的问题，两者组合威力倍增。**

**▶ 3.3 对抗式框架：让AI自己"辩论"**

利用AI的多面性，让它同时扮演正方和反方，从而获得更全面的回答。

> \# 对抗式提示词示例\
> "请分别以'支持远程办公'和'反对远程办公'两个立场，\
> 各列出3个核心论点，并进行交叉反驳。\
> 最后以中立视角给出综合结论和建议。"
>
> **【应用场景】**
> 学术论文的文献综述、商业决策的SWOT分析、技术选型的优缺点对比、政策制定的利弊权衡
>
> **🎤 【互动提示 · 5分钟】**
>
> 现场练习：请同学们用"角色定义+回答框架"技巧，向AI提问一个你专业领域的问题（如"作为资深前端工程师，请对比Vue3和React18的Composition
> API设计哲学，用表格列出5个维度"），观察输出质量。

**04 高级提示词技巧（约束与压缩）**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 4.1 反向约束：告诉AI"不要做什么"**

正向约束（"要做什么"）+ 反向约束（"不要做什么"）= 精准控制输出边界。

-   段落叙述："请用学术风格撰写，避免口语化表达，不要使用第一人称"

-   表格输出："请生成Markdown表格，不要包含任何解释性文字，表头用英文"

-   列表输出："请列出要点，每条不超过20字，不要编号，用•符号开头"

> **【技巧要点】**
> 反向约束通常比正向约束更有效，因为AI的"默认行为"往往包含大量冗余信息（如寒暄、解释、总结），通过反向约束可以精准裁剪。

**▶ 4.2 AI主动询问：让AI帮你"完善问题"**

当你不确定如何提问时，可以让AI反问你。

-   一次性多问题："我想设计一个电商网站，但我不知道从何问起。请列出10个你需要了解的关键信息，以便给出最佳方案"

-   单问题+选项："我想学习机器学习，但不知道从何入手。请从以下维度问我一个问题：A.数学基础
    B.编程语言 C.学习目标 D.时间投入。请选最重要的一个维度提问。"

> \# AI主动询问的高级用法\
> "我要撰写一份大学生创新创业大赛的参赛材料，\
> 但我的项目还在构思阶段。\
> \
> 请你扮演一位大赛评委，向我提出5个关键问题，\
> 每个问题提供A/B/C三个选项，帮助我明确项目方向。\
> \
> 要求：\
> 1. 问题要具体，不能泛泛而谈\
> 2. 选项要有区分度，覆盖不同策略\
> 3. 每问完一个问题，等待我回答后再问下一个"
>
> ⭐
> **AI主动询问的本质是"需求澄清"——把模糊意图转化为结构化需求，这是从"新手提问"到"专家提问"的关键跃迁。**

**▶ 4.3 上下文管理：压缩与查询**

当对话轮数增多，上下文必然膨胀，需要主动管理。

-   摘要压缩：将前70%的历史对话压缩为摘要，保留最近30%的原文

-   关键信息提取：每5轮对话提取一次5W信息（Who/What/When/Where/Why），存入日志文件

-   本地查询：当用户说"/search"或表达查找意图时，检索日志文件并注入上下文

> \# 上下文压缩策略（伪代码）\
> def compress\_context(history, max\_tokens=3000):\
> total\_tokens = count\_tokens(history)\
> if total\_tokens &gt; max\_tokens:\
> \# 前70%压缩为摘要\
> old\_part = history\[:int(len(history)\*0.7)\]\
> summary = llm\_summarize(old\_part)\
> \# 后30%保留原文\
> new\_part = history\[int(len(history)\*0.7):\]\
> return \[summary\] + new\_part\
> return history
>
> **【实战提醒】**
> 上下文压缩不是"丢数据"，而是"换形式"——用结构化摘要替代原始对话，用关键信息日志替代全文检索。
>
> **🎤 【互动提示 · 8分钟】**
>
> 现场演示：请一位同学提供一段500字以上的复杂需求描述，我们用"AI主动询问"技巧，让AI逐步澄清需求，最终生成结构化需求文档。

**05 Function Call：让AI拥有双手**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 5.1 什么是Function Call？**

Function
Call（函数调用/工具调用）是让大语言模型从"只会说话"进化到"能动手做事"的核心机制。

-   本质：LLM是一个黑盒子，触及外部世界的唯一方法就是调用预先定义好的工具函数

-   流程：用户提问 → LLM分析 → 判断需要调用工具 → 生成调用参数 →
    Agent执行函数 → 结果返回LLM → LLM生成最终回答

> **【比喻】** Function
> Call就像给一位聪明的盲人配了一根"智能拐杖"——拐杖能探测路况（查天气）、能开门（操作文件）、能导航（访问网页），盲人（LLM）决定何时使用拐杖。

**▶ 5.2 五大基础工具开发**

以下是我们课程中开发的五个核心工具函数，构成AI Agent的"手脚"：

  **工具名称**   **功能描述**                                 **教学价值**
  -------------- -------------------------------------------- --------------------------------
  list\_files    列出目录下所有文件及属性（大小、修改时间）   让AI感知本地文件系统
  rename\_file   修改指定文件的名称                           让AI具备文件管理能力
  delete\_file   删除指定文件                                 让AI具备风险操作能力（需谨慎）
  create\_file   在指定目录新建文件并写入内容                 让AI具备内容生成与持久化能力
  read\_file     读取指定文件的内容                           让AI具备知识获取能力

**▶ 5.3 工具调用代码实战**

核心代码结构：定义工具 → 注册工具 → LLM决策 → 执行工具 → 结果回传

> \# tool\_chat\_client.py 核心逻辑\
> import os\
> import json\
> from datetime import datetime\
> \
> def list\_files(directory):\
> """列出目录下所有文件"""\
> files = \[\]\
> for item in os.listdir(directory):\
> path = os.path.join(directory, item)\
> stat = os.stat(path)\
> files.append({\
> "name": item,\
> "size": stat.st\_size,\
> "is\_dir": os.path.isdir(path),\
> "modified": datetime.fromtimestamp(stat.st\_mtime).strftime("%Y-%m-%d
> %H:%M")\
> })\
> return json.dumps(files, ensure\_ascii=False)\
> \
> def read\_file(filepath):\
> """读取文件内容"""\
> with open(filepath, 'r', encoding='utf-8') as f:\
> return f.read()\
> \
> def create\_file(directory, filename, content):\
> """创建文件并写入内容"""\
> filepath = os.path.join(directory, filename)\
> with open(filepath, 'w', encoding='utf-8') as f:\
> f.write(content)\
> return f"文件 {filename} 已创建，共 {len(content)} 字符"\
> \
> \# 工具定义（发送给LLM的JSON Schema）\
> tools = \[\
> {\
> "type": "function",\
> "function": {\
> "name": "list\_files",\
> "description": "列出指定目录下的所有文件",\
> "parameters": {\
> "type": "object",\
> "properties": {\
> "directory": {"type": "string", "description": "目录路径"}\
> },\
> "required": \["directory"\]\
> }\
> }\
> },\
> \# ... 其他工具定义\
> \]\
> \
> \# LLM调用时传入tools参数\
> response = client.chat.completions.create(\
> model="qwen3.5",\
> messages=messages,\
> tools=tools, \# 关键：告诉LLM有哪些工具可用\
> tool\_choice="auto" \# 让LLM自动决定是否调用工具\
> )
>
> ⭐ **Function Call的JSON
> Schema是"契约"——LLM根据description理解工具用途，根据parameters生成合法参数，Agent负责执行并返回结果。**

**▶ 5.4 扩展工具：网络访问与日期获取**

-   curl访问网页：通过subprocess调用curl命令，获取网页HTML内容

-   日期获取：LLM不知道当前日期，必须通过工具或System Prompt注入

> \# 网络访问工具\
> def curl\_webpage(url):\
> import subprocess\
> result = subprocess.run(\
> \['curl', '-s', '-L', url\],\
> capture\_output=True, text=True, encoding='utf-8'\
> )\
> return result.stdout\[:5000\] \# 限制返回长度\
> \
> \# 日期工具（解决LLM的时间盲区）\
> def get\_current\_date():\
> return datetime.now().strftime("%Y年%m月%d日")\
> \
> \# System Prompt中注入日期\
> system\_prompt =
> f"""你是一个智能助手。当前日期：{get\_current\_date()}。\
> 当用户询问天气、日程等时效性问题时，请使用工具获取最新信息。"""
>
> **【常见错误】**
> LLM会"幻觉"日期——它根据训练数据的截止时间"猜测"当前日期，往往出错。必须通过System
> Prompt或工具注入真实日期。
>
> **🎤 【互动提示 · 10分钟】**
>
> 现场演示：运行tool\_chat\_client.py，输入"请查看明天青城山的最高和最低气温"，观察AI如何自动调用curl工具访问wttr.in网站，并解析天气数据。

**06 RAG与上下文管理**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 6.1 RAG：检索增强生成**

RAG（Retrieval-Augmented
Generation）是解决LLM"知识幻觉"和"知识过时"的杀手锏。

-   问题：LLM的训练数据有截止日期，且无法访问你的私人文档

-   方案：在生成回答前，先从外部知识库检索相关文档片段，注入上下文，再让LLM基于"真实资料"回答

> **【RAG流程】** 1. 用户提问 → 2. 向量化查询 → 3.
> 向量数据库检索Top-K相关片段 → 4. 将片段注入Prompt → 5.
> LLM基于片段生成回答

**▶ 6.2 AnythingLLM：本地RAG实践**

AnythingLLM是一款开源的本地文档向量数据库软件，支持将PDF、Word、TXT等文档向量化存储。

-   安装：下载AnythingLLM桌面版，配置LMStudio作为模型后端

-   使用：新建工作区 → 上传文档 → 自动分块向量化 → 开启对话

-   API：开启本地服务（端口3001），通过REST API进行程序化访问

> \# AnythingLLM API调用示例\
> def anythingllm\_query(message, workspace\_slug, api\_key):\
> import subprocess\
> import json\
> \
> url =
> f"http://localhost:3001/api/v1/workspace/{workspace\_slug}/chat"\
> \
> payload = json.dumps({"message": message, "mode": "chat"})\
> \
> cmd = \[\
> 'curl', '-s', '-X', 'POST', url,\
> '-H', f'Authorization: Bearer {api\_key}',\
> '-H', 'Content-Type: application/json',\
> '-d', payload\
> \]\
> \
> result = subprocess.run(cmd, capture\_output=True, text=True)\
> response = json.loads(result.stdout)\
> return response.get("textResponse", "无响应")\
> \
> \# 在Agent中注册为工具\
> \# 当用户提到"文档仓库"、"文件仓库"时自动触发
>
> ⭐
> **RAG不是替代LLM，而是给LLM配了一个"外接硬盘"——LLM负责理解问题、整合信息、生成回答，向量数据库负责精准检索。**

**▶ 6.3 上下文压缩策略**

长对话必然导致上下文膨胀，需要主动压缩以维持对话质量。

-   触发条件：聊天轮数超过5轮，或上下文长度超过3K tokens

-   压缩策略：前70%内容由LLM总结为摘要，后30%保留原文

-   关键信息提取：每5轮提取5W信息（Who/What/When/Where/Why），存入本地日志

> \# 上下文压缩实现\
> def compress\_chat\_history(history, max\_length=3000):\
> """\
> history: 消息列表 \[{"role": "user", "content": "..."}, ...\]\
> """\
> current\_length = sum(len(msg\["content"\]) for msg in history)\
> \
> if current\_length &gt; max\_length:\
> \# 计算分割点\
> split\_idx = int(len(history) \* 0.7)\
> \
> \# 前70%交给LLM总结\
> old\_messages = history\[:split\_idx\]\
> summary\_prompt =
> f"请总结以下对话的关键信息：{json.dumps(old\_messages)}"\
> summary = call\_llm(summary\_prompt)\
> \
> \# 后30%保留原文\
> new\_messages = history\[split\_idx:\]\
> \
> return \[\
> {"role": "system", "content": f"【历史摘要】{summary}"},\
> \*new\_messages\
> \]\
> \
> return history
>
> **【设计原则】**
> 压缩不是删除，而是"语义保留"——用摘要替代原文，确保LLM仍能理解对话脉络。
>
> **🎤 【互动提示 · 3分钟】**
>
> 请同学们思考：如果上下文长度是128K（约10万字），是否还需要压缩？（答案：需要，因为长上下文会稀释注意力，导致"中间遗忘"现象）

**07 实战：开发你的第一个AI Agent**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 7.1 项目初始化与配置**

从零开始，用AI辅助开发一个完整的Agent项目。

-   环境要求：Python
    3.12+、LMStudio（本地模型）或在线API（OpenRouter等）

-   AI Coding平台：Trae（免费）、Cursor、VS Code + Copilot

-   项目结构：空白目录 → 初始化venv → 配置.gitignore → 创建.env模板

> \# 项目目录结构\
> ai-agent-course/\
> ├── .env \# 环境变量（API密钥等，不提交Git）\
> ├── .env.example \# 环境变量模板（提交Git）\
> ├── .gitignore \# Git排除文件\
> ├── README.md \# 项目说明文档\
> ├── requirements.txt \# Python依赖\
> ├── practice01/ \# 基础HTTP调用\
> │ └── chat\_client.py\
> ├── practice02/ \# 工具调用（5个文件操作+网络访问）\
> │ └── tool\_chat\_client.py\
> ├── practice03/ \# 上下文压缩+关键信息提取\
> ├── practice04/ \# AnythingLLM集成\
> ├── practice05/ \# 流式输出+历史记录\
> ├── practice06/ \# Skill加载系统\
> ├── practice07/ \# 链式工具调用\
> └── .agents/\
> └── skills/\
> └── notice/\
> └── SKILL.md
>
> **【开发范式】** Vibe Coding：用自然语言描述需求，让AI
> Coding平台生成代码 → 人工审查 → 测试 → 迭代优化。

**▶ 7.2 核心代码：从HTTP调用到流式对话**

> \# practice01/chat\_client.py - 基础HTTP调用\
> import os\
> import json\
> import time\
> from urllib.request import Request, urlopen\
> from dotenv import load\_dotenv\
> \
> load\_dotenv()\
> \
> BASE\_URL = os.getenv("BASE\_URL", "http://localhost:1234/v1")\
> API\_KEY = os.getenv("API\_KEY", "lm-studio")\
> MODEL = os.getenv("MODEL", "qwen3.5")\
> \
> def chat\_completion(message):\
> start\_time = time.time()\
> \
> req = Request(\
> f"{BASE\_URL}/chat/completions",\
> data=json.dumps({\
> "model": MODEL,\
> "messages": \[{"role": "user", "content": message}\],\
> "stream": False\
> }).encode("utf-8"),\
> headers={\
> "Content-Type": "application/json",\
> "Authorization": f"Bearer {API\_KEY}"\
> },\
> method="POST"\
> )\
> \
> with urlopen(req) as resp:\
> data = json.loads(resp.read().decode("utf-8"))\
> \
> elapsed = time.time() - start\_time\
> content = data\["choices"\]\[0\]\["message"\]\["content"\]\
> tokens = data.get("usage", {}).get("total\_tokens", 0)\
> speed = tokens / elapsed if elapsed &gt; 0 else 0\
> \
> print(f"⏱️ 耗时: {elapsed:.2f}s | 🔢 Token: {tokens} | ⚡ 速度:
> {speed:.1f} token/s")\
> return content\
> \
> if \_\_name\_\_ == "\_\_main\_\_":\
> response = chat\_completion("你好，请介绍一下Python的异步编程")\
> print(response)
>
> ⭐ **使用Python标准库urllib而非requests，减少依赖，教学项目更轻量。**

**▶ 7.3 流式输出与历史记录循环**

> \# practice05/stream\_chat.py - 流式输出+历史记录\
> import json\
> from urllib.request import Request, urlopen\
> \
> def stream\_chat\_completion(messages):\
> """支持流式输出和历史记录的对话客户端"""\
> req = Request(\
> f"{BASE\_URL}/chat/completions",\
> data=json.dumps({\
> "model": MODEL,\
> "messages": messages,\
> "stream": True \# 关键：开启流式输出\
> }).encode("utf-8"),\
> headers={\
> "Content-Type": "application/json",\
> "Authorization": f"Bearer {API\_KEY}"\
> },\
> method="POST"\
> )\
> \
> full\_content = ""\
> with urlopen(req) as resp:\
> for line in resp:\
> line = line.decode("utf-8").strip()\
> if line.startswith("data: "):\
> data = line\[6:\]\
> if data == "\[DONE\]":\
> break\
> try:\
> chunk = json.loads(data)\
> delta = chunk\["choices"\]\[0\]\["delta"\].get("content", "")\
> print(delta, end="", flush=True)\
> full\_content += delta\
> except:\
> pass\
> \
> return full\_content\
> \
> \# 主循环：持续对话直到Ctrl+C\
> def main():\
> history = \[{"role": "system", "content": "你是一个 helpful
> 的AI助手。"}\]\
> \
> print("🤖 AI助手已启动，输入内容开始对话，Ctrl+C退出")\
> try:\
> while True:\
> user\_input = input("\\n👤 你: ")\
> history.append({"role": "user", "content": user\_input})\
> \
> print("🤖 AI: ", end="")\
> response = stream\_chat\_completion(history)\
> history.append({"role": "assistant", "content": response})\
> \
> except KeyboardInterrupt:\
> print("\\n\\n👋 再见！")\
> \
> if \_\_name\_\_ == "\_\_main\_\_":\
> main()
>
> **【流式输出的意义】**
> 用户体验：AI"打字式"输出，降低等待焦虑；实时反馈：长文本生成时可提前阅读；Token统计：流式模式下需客户端自行统计token数。
>
> **🎤 【互动提示 · 8分钟】**
>
> 请同学们运行stream\_chat.py，体验流式输出的"打字效果"，并尝试连续对话5轮以上，观察历史记录如何累积。

**▶ 7.4 Skill系统：模块化能力加载**

Skill是"可复用的提示词模板"，让Agent具备专业化能力。

-   Skill文件格式：Markdown文件，包含YAML front matter（元数据）+
    正文（提示词规则）

-   加载逻辑：扫描.skills目录 → 读取SKILL.md → 提取name/description →
    注入System Prompt

> \# .agents/skills/notice/SKILL.md 示例\
> ---\
> name: notice\
> description: 撰写、修改、润色各类通知公文\
> version: 1.0\
> ---\
> \
> \# 通知撰写规范\
> \
> \#\# 格式要求\
> 1. 通知标题\*\*不能以"通知"二字开头\*\*\
> 2. 必须冠以"XX部"前缀，例如"采购部通知""宣传部通知"\
> 3. 如果用户未告知部门，使用"XX部"代替\
> \
> \#\# 内容结构\
> 1. 标题：XX部通知\
> 2. 发文依据（政策/会议决定）\
> 3. 具体事项（时间、地点、要求）\
> 4. 落款与日期\
> \
> \#\# 语气要求\
> - 正式、简洁、无歧义\
> - 避免口语化表达\
> - 时间表述精确到日
>
> \# Skill加载代码（practice06/skill\_loader.py）\
> import os\
> import yaml\
> \
> def list\_available\_skills(skills\_dir=".agents/skills"):\
> """扫描并列出所有可用技能"""\
> skills = \[\]\
> if not os.path.exists(skills\_dir):\
> return skills\
> \
> for skill\_name in os.listdir(skills\_dir):\
> skill\_path = os.path.join(skills\_dir, skill\_name, "SKILL.md")\
> if os.path.exists(skill\_path):\
> with open(skill\_path, 'r', encoding='utf-8') as f:\
> content = f.read()\
> \
> \# 提取YAML front matter\
> if content.startswith('---'):\
> parts = content.split('---', 2)\
> if len(parts) &gt;= 3:\
> metadata = yaml.safe\_load(parts\[1\])\
> skills.append({\
> "name": metadata.get("name", skill\_name),\
> "description": metadata.get("description", "")\
> })\
> \
> return skills\
> \
> def load\_skill\_content(skill\_name, skills\_dir=".agents/skills"):\
> """加载指定Skill的正文内容（不含YAML）"""\
> skill\_path = os.path.join(skills\_dir, skill\_name, "SKILL.md")\
> with open(skill\_path, 'r', encoding='utf-8') as f:\
> content = f.read()\
> \
> if content.startswith('---'):\
> parts = content.split('---', 2)\
> return parts\[2\].strip() if len(parts) &gt;= 3 else content\
> return content\
> \
> \# 在System Prompt中注入Skill列表\
> skills = list\_available\_skills()\
> system\_prompt = f"""你是一个智能助手。可用技能：{json.dumps(skills)}\
> 当用户请求匹配某个技能时，调用load\_skill\_content加载该技能规则并遵照执行。"""
>
> ⭐
> **Skill系统的本质是"提示工程工程化"——将反复使用的提示词模板封装为可维护、可复用、可扩展的模块。**

**▶ 7.5 链式工具调用：让AI自主规划**

链式调用（Chained Tool
Calls）是Agent的"高级形态"——AI根据中间结果自主决定下一步操作。

-   核心思想：前一个工具的输出作为后一个工具的输入参数

-   决策机制：LLM在每次工具调用后分析结果，判断任务是否完成或需要继续

-   防循环：设置max\_iterations（建议10次）防止无限循环

> \# practice07/chained\_agent.py - 链式调用核心\
> import json\
> \
> class ChainedCallContext:\
> """链式调用上下文管理器"""\
> def \_\_init\_\_(self, max\_iterations=10):\
> self.history = \[\] \# 调用历史\
> self.variables = {} \# 中间变量存储\
> self.max\_iterations = max\_iterations\
> self.iteration = 0\
> \
> def record\_step(self, tool\_name, arguments, result):\
> self.history.append({\
> "step": self.iteration,\
> "tool": tool\_name,\
> "args": arguments,\
> "result": result\
> })\
> self.iteration += 1\
> \
> def set\_variable(self, key, value):\
> self.variables\[key\] = value\
> \
> def get\_variable(self, key):\
> return self.variables.get(key)\
> \
> def build\_analysis\_prompt(user\_request, context):\
> """构建LLM决策提示词"""\
> history\_text = json.dumps(context.history, ensure\_ascii=False)\
> variables\_text = json.dumps(context.variables, ensure\_ascii=False)\
> \
> return f"""用户请求：{user\_request}\
> \
> 已执行步骤：{history\_text}\
> 当前变量：{variables\_text}\
> \
> 决策规则：\
> 1. 分析已执行步骤的结果\
> 2. 判断任务是否完成\
> 3. 如未完成，选择下一个工具并填写参数\
> 4. 可使用 {{variable\_name}} 引用上下文变量\
> \
> 请按以下JSON格式返回决策：\
> 完成任务：{{"done": true, "answer": "最终回答"}}\
> 继续调用：{{"done": false, "tool\_call": {{"name": "工具名",
> "arguments": {{"参数": "值"}}}}}}"""\
> \
> def execute\_chained\_tool\_call(user\_request, tools,
> max\_iterations=10):\
> context = ChainedCallContext(max\_iterations)\
> messages = \[{"role": "system", "content":
> "你是一个智能Agent，擅长多步骤任务规划。"}\]\
> \
> for i in range(max\_iterations):\
> \# 构建分析提示词\
> analysis\_prompt = build\_analysis\_prompt(user\_request, context)\
> messages.append({"role": "user", "content": analysis\_prompt})\
> \
> \# 调用LLM决策\
> response = call\_llm(messages)\
> \
> \# 解析JSON决策\
> try:\
> decision = json.loads(extract\_json(response))\
> except:\
> return f"解析失败：{response}"\
> \
> if decision.get("done"):\
> return decision\["answer"\]\
> \
> \# 执行工具\
> tool\_call = decision\["tool\_call"\]\
> result = execute\_tool(tool\_call\["name"\],
> tool\_call\["arguments"\])\
> context.record\_step(tool\_call\["name"\], tool\_call\["arguments"\],
> result)\
> \
> messages.append({"role": "assistant", "content": f"工具
> {tool\_call\['name'\]} 返回：{result}"})\
> \
> return "达到最大迭代次数，任务未完成"\
> \
> \# 测试案例1：文件搜索链式调用\
> \#
> 用户："请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"\
> \# 步骤1: list\_files("practice06") → 获取文件列表\
> \# 步骤2: read\_file(每个含def的文件) → 读取内容\
> \# 步骤3: 总结内容 → 返回最终答案
>
> **【链式调用的关键】** LLM的决策质量决定链式调用的成败——需要在System
> Prompt中提供清晰的决策规则、工具描述和示例。
>
> **🎤 【互动提示 · 10分钟】**
>
> 现场演示：运行chained\_agent.py，输入"读取1.txt和2.txt（内容都是正整数），把两数相加的和写入result.txt"，观察AI如何自动分三步完成：读取文件1
> → 读取文件2 → 计算并写入结果。

**08 课堂互动与现场演示**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 8.1 互动环节设计**

公开课的成功取决于听众的参与度，以下是精心设计的互动节点：

  **环节**   **时间点**   **互动形式**            **教学目标**
  ---------- ------------ ----------------------- ----------------------------
  对比实验   第15分钟     全体举手投票            直观感受提示词质量差异
  角色扮演   第30分钟     分组讨论+代表发言       理解角色定义对输出的影响
  现场编程   第60分钟     学生上台操作+教师点评   掌握基础代码编写能力
  Bug排查    第90分钟     小组竞赛                培养调试思维和问题解决能力
  创意挑战   第110分钟    个人创作+展示           激发创新应用思维

**▶ 8.2 现场演示脚本**

以下为教师现场演示的标准化流程，确保演示流畅、不出错：

-   演示1：提示词对比（5分钟）

> 准备两个浏览器标签页，同时输入"帮我写一段Python代码"和"你是一位Python高级工程师，请用PEP8规范编写一个带类型注解的斐波那契数列生成器函数，要求支持迭代器协议，并附带单元测试"，对比输出差异。

-   演示2：Function Call实时调用（8分钟）

> 运行tool\_chat\_client.py，输入"请查看我的项目目录下有哪些Python文件"，观察AI自动调用list\_files工具；再输入"读取chat\_client.py的内容"，观察AI自动调用read\_file工具。

-   演示3：流式输出体验（3分钟）

> 运行stream\_chat.py，输入"请用500字解释量子计算的基本原理"，让学生观察"打字式"输出效果，对比非流式模式的等待体验。

-   演示4：链式调用全流程（10分钟）

> 运行chained\_agent.py，输入复杂任务"访问https://www.nsu.edu.cn/HTML/news/2024/06/article\_3974.html，总结页面内容，保存到summary.txt"，展示AI自主规划的三步执行过程。
>
> **【演示技巧】** 1. 提前测试所有代码，确保网络畅通；2. 准备"Plan
> B"截图，防止现场网络故障；3.
> 边操作边讲解"我在想什么"，展示教师的思维过程；4.
> 邀请学生预测下一步输出，增强参与感。

**▶ 8.3 学生常见问题预判与解答**

-   Q: "为什么我的AI回答总是很短？" → A: 检查是否在System
    Prompt中限制了max\_tokens，或User Prompt中未明确要求输出长度

-   Q: "Function Call和RAG有什么区别？" → A: Function
    Call是"动手做事"（执行代码），RAG是"查资料"（检索文档），两者互补

-   Q: "本地模型和在线模型哪个更好？" → A:
    在线模型（如GPT-4、Claude）更聪明但收费；本地模型（如Qwen3.5）免费但需好显卡，适合学习和隐私场景

-   Q: "提示工程会被AI进化淘汰吗？" → A:
    不会。模型越强大，提示工程越重要——因为强大的模型能做更多事，更需要精准引导避免"用力过猛"

> **🎤 【互动提示 · 5分钟】**
>
> 请一位高级教师分享：您在教学中遇到过哪些"AI回答不靠谱"的情况？您是如何通过优化提示词解决的？

**09 课后总结与拓展资源**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ 9.1 核心知识图谱**

本课程的知识体系可以用以下层次结构概括：

-   第一层：认知层 —— 理解LLM的本质（概率预测器）、Token机制、Context
    Length限制

-   第二层：技巧层 —— 角色定义、框架约束、反向约束、主动询问、上下文压缩

-   第三层：工具层 —— Function Call开发（文件操作、网络访问、日期获取）

-   第四层：系统层 —— RAG集成（AnythingLLM）、Skill加载、链式调用

-   第五层：工程层 —— 项目初始化、Git管理、README撰写、SPEC开发范式

> **【学习路径建议】** 初学者：第1→2→3→4章 → 完成practice01-03代码\
> 进阶者：第5→6→7章 → 完成practice04-07代码 → 开发个人Skill\
> 竞赛者：第8→9章 → 用AI辅助撰写参赛材料 → 参加中国大学生计算机设计大赛

**▶ 9.2 关键要点速查表**

  **场景**           **最佳实践**
  ------------------ -----------------------------------------------------------
  想让AI写得更专业   System Prompt定义专家角色 + User Prompt指定输出框架
  想让AI回答更精准   提供具体示例（Few-shot）+ 反向约束排除不想要的输出
  长对话质量下降     触发上下文压缩：前70%摘要 + 后30%原文保留
  需要查私有文档     部署AnythingLLM本地RAG，通过API注入文档片段
  AI需要操作文件     开发Function Call工具，定义JSON Schema，让LLM自主决策
  复杂任务分多步     实现链式调用，用ChainedCallContext管理中间状态
  重复性任务自动化   封装为Skill（SKILL.md），通过YAML front matter注册
  项目开发规范化     采用SPEC范式：spec.md → requirement.md → api.md → test.md

**▶ 9.3 课后作业与拓展任务**

**【必做作业】**

-   配置本地开发环境：安装Python 3.12+、LMStudio、Trae

-   完成practice01-03的代码开发，确保能正常运行

-   撰写实验报告：记录每个练习的输入、输出、遇到的问题及解决方案

**【选做拓展】**

-   尝试用AI辅助开发一个个人项目（如智能笔记助手、代码审查工具）

-   注册GitHub账号，将课程代码推送到公开仓库，完善README.md

-   撰写一篇技术博客，分享你的提示工程学习心得

-   准备中国大学生计算机设计大赛材料，用本课程所学AI技巧辅助创作

**▶ 9.4 推荐资源**

-   Skill Hub：https://skillhub.cn/ —— 丰富的AI Skill模板库

-   MiniMax Skills：https://github.com/MiniMax-AI/skills/ ——
    企业级Skill示例

-   OpenRouter：https://openrouter.ai/ —— 免费在线LLM API聚合平台

-   AnythingLLM：https://anythingllm.com/ —— 本地RAG解决方案

-   Pandoc：https://pandoc.org/ —— Markdown转PDF/Word工具

> **【教师寄语】**
> 提示工程不是"咒语"，而是"沟通的艺术"。当你学会像对待一位聪明但需要引导的助手一样与AI对话时，你就掌握了这个时代最核心的生产力工具。记住：AI不会替代你，但会用AI的人会替代不会用AI的人。
>
> ⭐
> **本课程的最终目标：每位同学都能发布一个GitHub项目、撰写一份AI开发教程讲义、或输出一份高质量的竞赛参赛材料。**

**附录 完整代码参考（教师备课用）**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**▶ A.1 环境配置文件模板**

> \# .env.example —— 复制为.env后填写真实值\
> BASE\_URL=http://localhost:1234/v1\
> API\_KEY=lm-studio\
> MODEL=qwen3.5\
> \
> \# AnythingLLM配置（可选）\
> ANYTHINGLLM\_API\_KEY=your\_api\_key\_here\
> ANYTHINGLLM\_WORKSPACE\_SLUG=your\_workspace\_slug

**▶ A.2 完整工具调用客户端**

> \# practice02/tool\_chat\_client.py\
> import os\
> import json\
> import subprocess\
> from urllib.request import Request, urlopen\
> from dotenv import load\_dotenv\
> \
> load\_dotenv()\
> \
> BASE\_URL = os.getenv("BASE\_URL")\
> API\_KEY = os.getenv("API\_KEY")\
> MODEL = os.getenv("MODEL")\
> \
> \# ========== 工具函数定义 ==========\
> def list\_files(directory):\
> """列出目录下所有文件及属性"""\
> try:\
> files = \[\]\
> for item in os.listdir(directory):\
> path = os.path.join(directory, item)\
> stat = os.stat(path)\
> files.append({\
> "name": item,\
> "size": f"{stat.st\_size} bytes",\
> "is\_directory": os.path.isdir(path),\
> "modified":
> \_\_import\_\_('datetime').datetime.fromtimestamp(stat.st\_mtime).strftime("%Y-%m-%d
> %H:%M")\
> })\
> return json.dumps(files, ensure\_ascii=False, indent=2)\
> except Exception as e:\
> return f"错误: {str(e)}"\
> \
> def read\_file(filepath):\
> """读取文件内容"""\
> try:\
> with open(filepath, 'r', encoding='utf-8') as f:\
> return f.read()\
> except Exception as e:\
> return f"错误: {str(e)}"\
> \
> def create\_file(directory, filename, content):\
> """创建文件并写入内容"""\
> try:\
> os.makedirs(directory, exist\_ok=True)\
> filepath = os.path.join(directory, filename)\
> with open(filepath, 'w', encoding='utf-8') as f:\
> f.write(content)\
> return f"成功创建文件: {filepath}"\
> except Exception as e:\
> return f"错误: {str(e)}"\
> \
> def rename\_file(directory, old\_name, new\_name):\
> """重命名文件"""\
> try:\
> old\_path = os.path.join(directory, old\_name)\
> new\_path = os.path.join(directory, new\_name)\
> os.rename(old\_path, new\_path)\
> return f"成功重命名: {old\_name} -&gt; {new\_name}"\
> except Exception as e:\
> return f"错误: {str(e)}"\
> \
> def delete\_file(filepath):\
> """删除文件"""\
> try:\
> os.remove(filepath)\
> return f"成功删除: {filepath}"\
> except Exception as e:\
> return f"错误: {str(e)}"\
> \
> def curl\_webpage(url):\
> """通过curl访问网页"""\
> try:\
> result = subprocess.run(\
> \['curl', '-s', '-L', '--max-time', '10', url\],\
> capture\_output=True, text=True, encoding='utf-8'\
> )\
> return result.stdout\[:8000\] \# 限制返回长度\
> except Exception as e:\
> return f"错误: {str(e)}"\
> \
> def get\_current\_date():\
> """获取当前日期"""\
> from datetime import datetime\
> return datetime.now().strftime("%Y年%m月%d日 %H:%M")\
> \
> \# 工具映射表\
> TOOL\_MAP = {\
> "list\_files": list\_files,\
> "read\_file": read\_file,\
> "create\_file": create\_file,\
> "rename\_file": rename\_file,\
> "delete\_file": delete\_file,\
> "curl\_webpage": curl\_webpage,\
> "get\_current\_date": get\_current\_date\
> }\
> \
> \# ========== LLM工具定义（JSON Schema） ==========\
> TOOLS = \[\
> {\
> "type": "function",\
> "function": {\
> "name": "list\_files",\
> "description": "列出指定目录下的所有文件和子目录",\
> "parameters": {\
> "type": "object",\
> "properties": {\
> "directory": {"type": "string", "description": "要列出的目录路径"}\
> },\
> "required": \["directory"\]\
> }\
> }\
> },\
> {\
> "type": "function",\
> "function": {\
> "name": "read\_file",\
> "description": "读取指定文件的内容",\
> "parameters": {\
> "type": "object",\
> "properties": {\
> "filepath": {"type": "string", "description": "文件路径"}\
> },\
> "required": \["filepath"\]\
> }\
> }\
> },\
> {\
> "type": "function",\
> "function": {\
> "name": "create\_file",\
> "description": "在指定目录创建新文件并写入内容",\
> "parameters": {\
> "type": "object",\
> "properties": {\
> "directory": {"type": "string", "description": "目标目录"},\
> "filename": {"type": "string", "description": "文件名"},\
> "content": {"type": "string", "description": "文件内容"}\
> },\
> "required": \["directory", "filename", "content"\]\
> }\
> }\
> },\
> {\
> "type": "function",\
> "function": {\
> "name": "curl\_webpage",\
> "description": "通过curl命令访问网页并返回HTML内容",\
> "parameters": {\
> "type": "object",\
> "properties": {\
> "url": {"type": "string", "description": "要访问的URL"}\
> },\
> "required": \["url"\]\
> }\
> }\
> },\
> {\
> "type": "function",\
> "function": {\
> "name": "get\_current\_date",\
> "description": "获取当前日期和时间",\
> "parameters": {"type": "object", "properties": {}}\
> }\
> }\
> \]\
> \
> \# ========== 系统提示词 ==========\
> SYSTEM\_PROMPT =
> f"""你是一个智能Agent助手，当前日期：{get\_current\_date()}。\
> \
> 你可以使用以下工具帮助用户：\
> 1. list\_files - 列出目录文件\
> 2. read\_file - 读取文件内容\
> 3. create\_file - 创建文件\
> 4. curl\_webpage - 访问网页\
> 5. get\_current\_date - 获取当前日期\
> \
> 当用户提到"文档仓库"、"文件仓库"时，优先使用文件操作工具。\
> 当用户询问天气、新闻等时效性信息时，使用curl\_webpage工具获取最新数据。\
> \
> 重要：如果用户询问涉及今天、明天等时间相关的问题，你必须先调用get\_current\_date获取真实日期。"""\
> \
> \# ========== 核心调用函数 ==========\
> def chat\_with\_tools(messages, tools=None):\
> """带工具调用的对话函数"""\
> req = Request(\
> f"{BASE\_URL}/chat/completions",\
> data=json.dumps({\
> "model": MODEL,\
> "messages": messages,\
> "tools": tools or TOOLS,\
> "tool\_choice": "auto",\
> "stream": False\
> }).encode("utf-8"),\
> headers={\
> "Content-Type": "application/json",\
> "Authorization": f"Bearer {API\_KEY}"\
> },\
> method="POST"\
> )\
> \
> with urlopen(req) as resp:\
> return json.loads(resp.read().decode("utf-8"))\
> \
> def execute\_tool\_call(tool\_call):\
> """执行工具调用"""\
> name = tool\_call\["function"\]\["name"\]\
> arguments = json.loads(tool\_call\["function"\]\["arguments"\])\
> \
> if name in TOOL\_MAP:\
> result = TOOL\_MAP\[name\](\*\*arguments)\
> return {"tool\_call\_id": tool\_call\["id"\], "role": "tool", "name":
> name, "content": result}\
> return {"error": f"未知工具: {name}"}\
> \
> def main():\
> messages = \[{"role": "system", "content": SYSTEM\_PROMPT}\]\
> \
> print("🤖 智能Agent已启动，支持工具调用。Ctrl+C退出")\
> try:\
> while True:\
> user\_input = input("\\n👤 你: ")\
> messages.append({"role": "user", "content": user\_input})\
> \
> \# 第一次调用：LLM决定是否使用工具\
> response = chat\_with\_tools(messages)\
> message = response\["choices"\]\[0\]\["message"\]\
> \
> \# 检查是否有工具调用\
> if message.get("tool\_calls"):\
> print("🔧 正在调用工具...")\
> messages.append(message) \# 添加assistant的tool\_calls请求\
> \
> \# 执行所有工具调用\
> for tool\_call in message\["tool\_calls"\]:\
> result = execute\_tool\_call(tool\_call)\
> messages.append({\
> "role": "tool",\
> "tool\_call\_id": result\["tool\_call\_id"\],\
> "name": result\["name"\],\
> "content": result\["content"\]\
> })\
> print(f" ✓ {result\['name'\]}: {result\['content'\]\[:100\]}...")\
> \
> \# 第二次调用：LLM基于工具结果生成最终回答\
> final\_response = chat\_with\_tools(messages)\
> final\_message =
> final\_response\["choices"\]\[0\]\["message"\]\["content"\]\
> print(f"🤖 AI: {final\_message}")\
> messages.append({"role": "assistant", "content": final\_message})\
> else:\
> content = message\["content"\]\
> print(f"🤖 AI: {content}")\
> messages.append({"role": "assistant", "content": content})\
> \
> except KeyboardInterrupt:\
> print("\\n\\n👋 再见！")\
> \
> if \_\_name\_\_ == "\_\_main\_\_":\
> main()
>
> **【代码说明】**
> 以上为完整可运行的工具调用客户端代码，包含7个工具函数、JSON
> Schema定义、工具执行映射、以及完整的对话循环。教师可直接用于课堂演示。

**▶ A.3 课程项目GitHub推送指南**

> \# 1. 安装Git并配置\
> \# 下载：https://git-scm.com/downloads\
> \# 安装时勾选"Add to PATH"\
> \
> git config --global user.name "你的GitHub用户名"\
> git config --global user.email "你的邮箱@example.com"\
> \
> \# 2. 初始化仓库\
> cd ai-agent-course\
> git init\
> \
> \# 3. 创建.gitignore\
> echo ".env" &gt; .gitignore\
> echo "\_\_pycache\_\_/" &gt;&gt; .gitignore\
> echo "venv/" &gt;&gt; .gitignore\
> \
> \# 4. 提交代码\
> git add .\
> git commit -m "init: 初始化AI Agent教学项目"\
> \
> \# 5. 连接GitHub远程仓库\
> git remote add origin https://github.com/你的用户名/仓库名.git\
> git branch -M main\
> git push -u origin main\
> \
> \# 6. 创建个人主页仓库（用户名.github.io）\
> \# 在GitHub新建一个与你的用户名完全相同的public仓库\
> \# 添加README.md作为个人主页内容
>
> ⭐
> **GitHub是程序员的"名片"——一个维护良好的GitHub主页，比任何简历都更有说服力。**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**感谢聆听 · 期待在GitHub上看到你的项目**

人工智能提示工程 · Prompt Engineering
