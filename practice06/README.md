# Practice 06: 技能管理 Agent

## 概述

本练习实现一个具备技能管理功能的 AI Agent，能够自动读取技能列表，并在需要时自动加载技能内容到 system prompt。

## 功能特性

- **技能列表管理**: 自动读取 `agents/skills` 目录下的所有技能
- **YAML Frontmatter 解析**: 解析 SKILL.md 文件中的元数据
- **自动技能检测**: 根据用户输入自动检测并加载匹配的技能
- **技能内容注入**: 将技能正文内容（YAML frontmatter 之后的部分）注入 system prompt
- **技能查询**: 支持用户查询可用技能
- **动态提示词**: 根据激活的技能动态更新系统提示词

## 文件结构

```
practice06/
├── agent_with_skills.py  # 主程序
├── skills_manager.py     # 技能管理模块
└── README.md            # 说明文档
```
agents/skills/           # 技能目录
├── code_analysis/       # 代码分析技能
│   └── SKILL.md
├── file_operations/     # 文件操作技能
│   └── SKILL.md
├── notice/             # 通知撰写技能
│   └── SKILL.md
└── web_search/         # 网络搜索技能
    └── SKILL.md
```

## 核心功能

### 1. 技能管理模块 (skills_manager.py)

#### `list_available_skills()`
读取所有可用技能的信息：
```python
skills = list_available_skills()
```

#### `parse_yaml_frontmatter()`
解析 Markdown 文件中的 YAML frontmatter：
```python
frontmatter = parse_yaml_frontmatter(content)
# 返回: {'name': '...', 'description': '...', ...}
```

#### `format_skills_as_json()`
将技能列表格式化为 JSON 字符串（用于 system prompt）：
```python
json_str = format_skills_as_json(skills)
# 返回: '{"skills": [{"name": "...", "description": "..."}, ...]}'
```

#### `load_skill_content()`
加载技能的完整内容（包括正文）：
```python
result = load_skill_content('file_operations')
# 返回: {'success': True, 'name': '...', 'content': '...', ...}
```

### 2. SKILL.md 格式

每个技能目录中的 SKILL.md 文件必须包含 YAML frontmatter：

```markdown
---
name: skill_name
description: 技能的简短描述
version: 1.0.0
author: Author Name
tags: [tag1, tag2]
---

# 技能名称

## 功能概述
...
```

### 3. 主程序 (agent_with_skills.py)

启动时自动加载技能列表，并通过 system prompt 发送 JSON 格式的技能列表：

```json
{
  "skills": [
    {
      "name": "file_operations",
      "description": "提供文件和目录操作能力..."
    },
    {
      "name": "web_search",
      "description": "提供网络搜索能力..."
    }
  ]
}
```

支持以下命令：
- `/skills` - 显示可用技能列表
- `/skill` - 显示当前激活的技能
- `/clear` - 清空对话历史
- `/history` - 查看对话历史
- `/exit` - 退出程序

支持以下工具调用：
- `list_available_skills` - 列出所有可用技能
- `load_skill_content` - 加载指定技能的完整内容

### 4. 自动技能加载示例

当用户输入触发词时，系统会自动加载对应的技能：

```
👤 你: 帮我写个通知，关于五一放假安排
[系统] 检测到可能需要使用技能: notice
[系统] 已加载技能: notice
🤖 AI: XX部通知

各位同事：

根据国家法定节假日安排，现将五一劳动节放假事宜通知如下：
...
```

**notice 技能的特殊规则**：
- 通知标题必须以"XX部通知"格式开头
- 不能以"通知"二字开头
- 如果用户未告知部门，使用"XX部"占位

## 使用方法

### 1. 配置环境

确保 `.env` 文件已配置：
```bash
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-3.5-turbo
```

### 2. 运行程序

⚠️ **重要**: 请先运行 Python 程序，然后在程序的提示符下输入内容！

#### 方法1：使用批处理文件（推荐 for Windows）
```bash
# 双击运行 start.bat 文件，或在 PowerShell 中执行：
cd practice06
.\start.bat
```

#### 方法2：命令行启动
```bash
cd practice06
python agent_with_skills.py
```

#### 正确输入方式

运行后会看到提示：
```
👤 你: 
```

**这时再输入你的问题**，例如：
```
👤 你: 帮我写个关于五一放假的通知
```

#### ❌ 错误做法（不要这样做）

直接在 PowerShell 命令行输入中文：
```
PS E:\trae\zhou4\practice06> 帮我写个关于五一放假的通知
```

这会导致错误：
```
无法将"帮我写个关于五一放假的通知"项识别为 cmdlet、函数、脚本文件...
```

#### ✅ 正确做法

1. 先运行程序：`python agent_with_skills.py`
2. 等待出现 `"👤 你:"` 提示
3. 然后输入你的问题

**简单记忆**: 看到 `"👤 你:"` 才能输入！

### 3. 查询技能

输入以下问题查询可用技能：
```
👤 你: 你有什么技能？
🤖 AI: 以下是我可用的技能：

1. **file_operations** (v1.0.0)
   - 描述: 提供文件和目录操作能力...

2. **web_search** (v1.0.0)
   - 描述: 提供网络搜索能力...

3. **code_analysis** (v1.0.0)
   - 描述: 提供代码分析和审查能力...
```

## 扩展技能

要添加新技能，只需：

1. 在 `agents/skills/` 下创建新目录
2. 创建 SKILL.md 文件，包含 YAML frontmatter
3. 重启 Agent，新技能会自动加载

## 学习要点

1. **YAML Frontmatter 解析**: 学习如何解析 Markdown 文件中的元数据
2. **目录遍历**: 学习如何遍历目录结构
3. **动态提示词**: 学习如何根据运行时信息动态构建系统提示词
4. **技能注册机制**: 理解插件化架构的基本原理

## 与之前练习的关系

- **Practice 05**: 继承了知识提取和搜索功能
- **Practice 04**: 继承了工具调用架构
- **Practice 03**: 继承了文件操作工具
- **Practice 02**: 继承了对话历史管理
- **Practice 01**: 继承了 HTTP 通信基础

## 下一步

在此基础上，可以进一步实现：
- 技能的热加载和卸载
- 技能依赖管理
- 技能权限控制
- 技能版本管理
