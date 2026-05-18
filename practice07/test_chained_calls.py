"""
Practice 07: 链式工具调用测试脚本
包含三个测试用例
"""

import os
import sys

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from chained_tools import ChainedCallContext, parse_llm_response, execute_chained_tool_call


def test_case_1_file_search():
    """
    测试用例1：文件搜索链式调用
    
    模拟用户请求："请查找practice06目录下所有包含'def关键词的文件，并总结这些文件的主要内容"
    
    预期流程：
    1. search_files(directory="practice06", keyword="def") - 搜索包含"def"的文件
    2. read_file(filename=匹配的文件) - 读取文件内容
    3. generate_summary(content=文件内容) - 生成摘要
    4. 任务完成，返回摘要
    """
    print("\n" + "=" * 70)
    print("测试用例1：文件搜索链式调用")
    print("=" * 70)
    print("\n用户请求：请查找practice06目录下所有包含'def'关键词的文件，")
    print("          并总结这些文件的主要内容")
    print("\n预期流程：")
    print("  步骤1: search_files(directory='practice06', keyword='def')")
    print("         → 返回匹配的文件列表")
    print("  步骤2: read_file(filename=第一个匹配文件)")
    print("         → 返回文件内容")
    print("  步骤3: generate_summary(content=文件内容)")
    print("         → 返回摘要")
    print("  步骤4: 任务完成")
    
    # 模拟工具执行
    def mock_tool_executor(tool_name, params):
        print(f"\n  [执行工具] {tool_name}({params})")
        
        if tool_name == "search_files":
            return {
                "success": True,
                "matches": [
                    {"filename": "agent_with_skills.py", "path": "practice06/agent_with_skills.py"},
                    {"filename": "skills_manager.py", "path": "practice06/skills_manager.py"}
                ],
                "keyword": "def",
                "directory": "practice06"
            }
        elif tool_name == "read_file":
            return {
                "success": True,
                "content": "def list_available_skills():\n    '''列出所有可用技能'''\n    pass\n\ndef load_skill_content(skill_name):\n    '''加载技能内容'''\n    pass",
                "filename": params.get("filename", "unknown")
            }
        elif tool_name == "generate_summary":
            return {
                "success": True,
                "summary": "文件包含技能管理相关的函数定义，如 list_available_skills 和 load_skill_content"
            }
        
        return {"success": True, "result": "mock"}
    
    # 模拟 LLM 决策
    def mock_llm_caller(messages):
        last_msg = messages[-1]["content"]
        
        if "search_files" not in last_msg:
            return '{"done": false, "tool_call": {"name": "search_files", "arguments": {"directory": "practice06", "keyword": "def"}}}'
        elif "read_file" not in last_msg:
            return '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "practice06", "filename": "agent_with_skills.py"}}}'
        elif "generate_summary" not in last_msg:
            return '{"done": false, "tool_call": {"name": "generate_summary", "arguments": {"content": "文件内容..."}}}'
        else:
            return '{"done": true, "answer": "找到2个包含\\"def\\"的文件：agent_with_skills.py 和 skills_manager.py。主要内容是技能管理相关的函数定义。"}'
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手。",
        max_iterations=5
    )
    
    print("\n" + "-" * 70)
    print("测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  最终结果: {result['final_result']}")
    print("=" * 70)


def test_case_2_multi_file_operation():
    """
    测试用例2：多文件操作
    
    模拟用户请求："读取/Users/atfa/Desktop/实验报告/practice07/1.txt和
    /Users/atfa/Desktop/实验报告/practice07/2.txt 两个文件，
    文件内容的都是正整数，把两个数相加的和写入result.txt 文件。"
    
    预期流程：
    1. read_file(filename="1.txt") - 读取第一个文件
    2. read_file(filename="2.txt") - 读取第二个文件
    3. write_file(filename="result.txt", content="和") - 写入结果
    4. 任务完成
    """
    print("\n" + "=" * 70)
    print("测试用例2：多文件操作")
    print("=" * 70)
    print("\n用户请求：读取1.txt和2.txt两个文件，")
    print("          文件内容都是正整数，")
    print("          把两个数相加的和写入result.txt文件")
    print("\n预期流程：")
    print("  步骤1: read_file(filename='1.txt')")
    print("         → 返回: content='100'")
    print("  步骤2: read_file(filename='2.txt')")
    print("         → 返回: content='200'")
    print("  步骤3: write_file(filename='result.txt', content='300')")
    print("         → 返回: 写入成功")
    print("  步骤4: 任务完成")
    
    # 模拟工具执行
    def mock_tool_executor(tool_name, params):
        print(f"\n  [执行工具] {tool_name}({params})")
        
        if tool_name == "read_file":
            filename = params.get("filename", "")
            if "1.txt" in filename:
                return {"success": True, "content": "100", "filename": filename}
            elif "2.txt" in filename:
                return {"success": True, "content": "200", "filename": filename}
        elif tool_name == "write_file":
            return {
                "success": True, 
                "filename": params.get("filename"),
                "path": f"practice07/{params.get('filename')}"
            }
        
        return {"success": True, "result": "mock"}
    
    # 模拟 LLM 决策
    def mock_llm_caller(messages):
        last_msg = messages[-1]["content"]
        
        if "read_file" not in last_msg or "1.txt" not in str(messages):
            return '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "practice07", "filename": "1.txt"}}}'
        elif "2.txt" not in str(messages):
            return '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "practice07", "filename": "2.txt"}}}'
        elif "write_file" not in str(messages):
            return '{"done": false, "tool_call": {"name": "write_file", "arguments": {"directory": "practice07", "filename": "result.txt", "content": "300"}}}'
        else:
            return '{"done": true, "answer": "成功读取1.txt(100)和2.txt(200)，计算和为300，已写入result.txt文件。"}'
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="读取1.txt和2.txt两个文件，把两个数相加的和写入result.txt文件",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手。",
        max_iterations=5
    )
    
    print("\n" + "-" * 70)
    print("测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  最终结果: {result['final_result']}")
    print("=" * 70)


def test_case_3_webpage_processing():
    """
    测试用例3：网页处理链式调用
    
    模拟用户请求："访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html
    并总结页面内容，保存到 practice07/summary.txt"
    
    预期流程：
    1. fetch_webpage(url="...") - 获取网页内容
    2. generate_summary(content=网页内容) - 生成摘要
    3. write_file(filename="summary.txt", content=摘要) - 保存到文件
    4. 任务完成
    """
    print("\n" + "=" * 70)
    print("测试用例3：网页处理链式调用")
    print("=" * 70)
    print("\n用户请求：访问网页并总结页面内容，")
    print("          保存到 practice07/summary.txt")
    print("\n预期流程：")
    print("  步骤1: fetch_webpage(url='https://...')")
    print("         → 返回: 网页HTML内容")
    print("  步骤2: generate_summary(content=网页内容)")
    print("         → 返回: 摘要")
    print("  步骤3: write_file(filename='summary.txt', content=摘要)")
    print("         → 返回: 写入成功")
    print("  步骤4: 任务完成")
    
    # 模拟工具执行
    def mock_tool_executor(tool_name, params):
        print(f"\n  [执行工具] {tool_name}({params})")
        
        if tool_name == "fetch_webpage":
            return {
                "success": True,
                "content": "宁夏大学新闻页面\n\n标题：学校举办2024年毕业典礼\n\n内容：6月20日，宁夏大学2024年毕业典礼在文萃校区举行。校长在典礼上致辞，鼓励毕业生们勇于追梦...",
                "url": params.get("url", "")
            }
        elif tool_name == "generate_summary":
            return {
                "success": True,
                "summary": "宁夏大学于6月20日举办2024年毕业典礼，校长致辞鼓励毕业生勇于追梦。"
            }
        elif tool_name == "write_file":
            return {
                "success": True,
                "filename": params.get("filename"),
                "path": f"practice07/{params.get('filename')}"
            }
        
        return {"success": True, "result": "mock"}
    
    # 模拟 LLM 决策
    def mock_llm_caller(messages):
        last_msg = messages[-1]["content"]
        
        if "fetch_webpage" not in str(messages):
            return '{"done": false, "tool_call": {"name": "fetch_webpage", "arguments": {"url": "https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html"}}}'
        elif "generate_summary" not in str(messages):
            return '{"done": false, "tool_call": {"name": "generate_summary", "arguments": {"content": "网页内容..."}}}'
        elif "write_file" not in str(messages):
            return '{"done": false, "tool_call": {"name": "write_file", "arguments": {"directory": "practice07", "filename": "summary.txt", "content": "摘要内容..."}}}'
        else:
            return '{"done": true, "answer": "成功获取网页内容并生成摘要，已保存到 practice07/summary.txt 文件。"}'
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="访问网页并总结页面内容，保存到 practice07/summary.txt",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手。",
        max_iterations=5
    )
    
    print("\n" + "-" * 70)
    print("测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  最终结果: {result['final_result']}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Practice 07: 链式工具调用测试")
    print("=" * 70)
    
    # 运行三个测试用例
    test_case_1_file_search()
    test_case_2_multi_file_operation()
    test_case_3_webpage_processing()
    
    print("\n" + "=" * 70)
    print("所有测试完成！")
    print("=" * 70)
