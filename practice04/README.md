# Practice 04: AnythingLLM 查询 Agent

基于 Practice 03 的文件操作 Agent，添加 AnythingLLM 文档仓库查询功能。

## 功能特性

### 1. 文件操作工具（继承自 Practice 03）
- **list_files**: 列出目录下的文件和文件夹
- **rename_file**: 重命名文件
- **delete_file**: 删除文件
- **create_file**: 创建新文件
- **read_file**: 读取文件内容

### 2. AnythingLLM 查询工具（新增）
- **query_anythingllm**: 查询 AnythingLLM 文档仓库中的信息
  - 使用 subprocess 调用 curl 命令访问 API
  - 支持中文编码
  - 自动处理 API 认证

## 环境配置

在 `.env` 文件中添加以下配置：

```bash
# LLM API 配置（与 Practice 03 相同）
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
LLM_API_KEY=your-api-key

# AnythingLLM 配置（新增）
ANYTHINGLLM_BASE_URL=http://localhost:3001
ANYTHINGLLM_API_KEY=your-anythingllm-api-key
ANYTHINGLLM_WORKSPACE_SLUG=your-workspace-slug
```

## 使用方法

### 1. 启动程序

```bash
cd practice04
python agent_with_tools.py
```

### 2. 使用文件操作工具

与 Practice 03 相同：
- "列出当前目录的文件"
- "创建一个名为 test.txt 的文件，内容是 Hello World"
- "读取 test.txt 文件"

### 3. 使用 AnythingLLM 查询工具

当提到以下关键词时，Agent 会自动触发 AnythingLLM 查询：
- "文档仓库"
- "文件仓库"
- "仓库"
- "知识库"

示例查询：
- "查询文档仓库中关于 Python 的资料"
- "在知识库中搜索机器学习相关内容"
- "仓库里有关于 API 设计的文档吗？"

## 技术实现

### anythingllm_tools.py

核心功能模块，包含：

1. **query_anythingllm(message, api_key, workspace_slug)**
   - 使用 subprocess 调用 curl 命令
   - 发送 POST 请求到 `/api/v1/workspace/{workspace_slug}/chat`
   - 使用 `--data-binary` 确保中文编码正确
   - 处理 API 响应并返回结构化数据

2. **check_anythingllm_health(base_url)**
   - 检查 AnythingLLM 服务是否正常运行
   - 访问 `/api/docs/` 端点

3. **ANYTHINGLLM_TOOLS_DEFINITION**
   - LLM 工具定义，用于 Function Calling

4. **execute_anythingllm_tool(tool_name, parameters)**
   - 工具执行入口函数

### agent_with_tools.py

修改内容：

1. **导入 AnythingLLM 工具模块**
   ```python
   from anythingllm_tools import (
       ANYTHINGLLM_TOOLS_DEFINITION, 
       execute_anythingllm_tool,
       query_anythingllm,
       check_anythingllm_health
   )
   ```

2. **合并工具定义**
   ```python
   def _get_all_tools(self) -> List[Dict]:
       all_tools = FILE_TOOLS.copy()
       all_tools.extend(ANYTHINGLLM_TOOLS_DEFINITION)
       return all_tools
   ```

3. **更新系统提示词**
   - 添加 AnythingLLM 工具说明
   - 明确触发条件："文档仓库"、"文件仓库"、"仓库"、"知识库"

4. **工具调用分发**
   ```python
   if tool_name == "query_anythingllm":
       result = execute_anythingllm_tool(tool_name, parameters)
   else:
       result = execute_file_tool(tool_name, parameters)
   ```

## 测试方法

### 测试 AnythingLLM 连接

```python
from anythingllm_tools import check_anythingllm_health

result = check_anythingllm_health()
print(result)
```

### 测试查询功能

```python
from anythingllm_tools import query_anythingllm

result = query_anythingllm("什么是机器学习？")
print(result)
```

## 故障排除

### 1. curl 命令未找到
- **错误**: `找不到 curl 命令`
- **解决**: 安装 curl 并添加到系统 PATH

### 2. 连接超时
- **错误**: `请求超时（60秒）`
- **解决**: 检查 AnythingLLM 服务是否已启动

### 3. 401 未授权
- **错误**: `API 返回 401`
- **解决**: 检查 `.env` 中的 `ANYTHINGLLM_API_KEY` 是否正确

### 4. 中文乱码
- **现象**: 返回的中文显示为乱码
- **解决**: 确保使用 `--data-binary` 和 `-H "Content-Type: application/json"`

## 实验报告

### 实验目标
实现通过 curl 命令查询 AnythingLLM 文档仓库的功能。

### 实验步骤
1. 创建 `anythingllm_tools.py` 模块
2. 实现 `query_anythingllm` 函数使用 subprocess 调用 curl
3. 处理中文编码问题
4. 修改 `agent_with_tools.py` 集成新工具
5. 更新系统提示词明确触发条件
6. 测试功能

### 关键技术点
1. **subprocess 模块**: 使用 `subprocess.run()` 执行 curl 命令
2. **中文编码**: 使用 `json.dumps(ensure_ascii=False)` 和 `--data-binary`
3. **环境变量**: 从 `.env` 读取配置并设置到 `os.environ`
4. **工具合并**: 将文件工具和 AnythingLLM 工具合并到同一个 Agent

### 遇到的问题及解决
1. **问题**: curl 命令参数复杂
   - **解决**: 使用列表形式构建命令，避免字符串转义问题

2. **问题**: API 响应解析失败
   - **解决**: 添加 try-except 捕获 JSONDecodeError

3. **问题**: 中文编码错误
   - **解决**: 使用 `--data-binary` 代替 `-d`，确保 UTF-8 编码

### 实验结果
成功实现 AnythingLLM 查询功能，Agent 能够：
- 识别用户查询文档仓库的意图
- 调用 curl 命令访问 AnythingLLM API
- 正确处理中文内容
- 返回结构化的查询结果

## 参考资料

- [AnythingLLM API 文档](http://localhost:3001/api/docs/)
- [subprocess 模块文档](https://docs.python.org/3/library/subprocess.html)
- [curl 命令手册](https://curl.se/docs/manpage.html)
