"""
Practice 07: 链式工具调用完整测试
模拟实际工具执行流程
"""

import os
import sys

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from chained_tools import ChainedCallContext, parse_llm_response, execute_chained_tool_call


def test_case_1_file_search_full():
    """
    测试用例1：文件搜索链式调用（完整执行）
    
    模拟用户请求："请查找practice06目录下所有包含'def关键词的文件，并总结这些文件的主要内容"
    """
    print("\n" + "=" * 70)
    print("测试用例1：文件搜索链式调用（完整执行）")
    print("=" * 70)
    
    call_count = [0]  # 使用列表来在闭包中修改
    executed_tools = []  # 记录已执行的工具
    
    def mock_tool_executor(tool_name, params):
        """模拟工具执行器"""
        call_count[0] += 1
        executed_tools.append(tool_name)
        print(f"\n  [执行 {call_count[0]}] {tool_name}({params})")
        
        if tool_name == "search_files":
            directory = params.get("directory", ".")
            keyword = params.get("keyword", "")
            print(f"    -> 搜索目录 '{directory}' 中包含 '{keyword}' 的文件")
            
            # 模拟搜索结果
            matches = [
                {"filename": "agent_with_skills.py", "path": f"{directory}/agent_with_skills.py"},
                {"filename": "skills_manager.py", "path": f"{directory}/skills_manager.py"}
            ]
            print(f"    -> 找到 {len(matches)} 个匹配文件")
            return {
                "success": True,
                "matches": matches,
                "keyword": keyword,
                "directory": directory
            }
            
        elif tool_name == "read_file":
            filename = params.get("filename", "")
            print(f"    -> 读取文件: {filename}")
            
            # 模拟文件内容
            content = f"def list_available_skills():\n    '''列出所有可用技能'''\n    pass\n\ndef load_skill_content(skill_name):\n    '''加载技能内容'''\n    pass"
            print(f"    -> 文件大小: {len(content)} 字符")
            return {
                "success": True,
                "content": content,
                "filename": filename
            }
            
        elif tool_name == "generate_summary":
            content = params.get("content", "")
            print(f"    -> 生成摘要，输入长度: {len(str(content))} 字符")
            
            summary = "文件包含技能管理相关的函数定义，如 list_available_skills 和 load_skill_content"
            print(f"    -> 摘要: {summary[:50]}...")
            return {
                "success": True,
                "summary": summary
            }
        
        return {"success": True, "result": "mock"}
    
    def mock_llm_caller(messages):
        """模拟 LLM 决策器 - 逐步执行工具链"""
        # 根据已执行的工具决定下一步
        if "search_files" not in executed_tools:
            print("  [LLM决策] 需要搜索文件")
            return '{"done": false, "tool_call": {"name": "search_files", "arguments": {"directory": "practice06", "keyword": "def"}}}'
        
        elif "read_file" not in executed_tools:
            print("  [LLM决策] 需要读取第一个匹配文件")
            return '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "practice06", "filename": "agent_with_skills.py"}}}'
        
        elif "generate_summary" not in executed_tools:
            print("  [LLM决策] 需要生成摘要")
            return '{"done": false, "tool_call": {"name": "generate_summary", "arguments": {"content": "def list_available_skills():\\n    pass\\n\\ndef load_skill_content(skill_name):\\n    pass"}}}'
        
        else:
            print("  [LLM决策] 任务完成")
            return '{"done": true, "answer": "找到2个包含\\"def\\"的文件：agent_with_skills.py 和 skills_manager.py。主要内容是技能管理相关的函数定义，包括 list_available_skills 和 load_skill_content。"}'
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手，擅长文件搜索和内容分析。",
        max_iterations=5
    )
    
    print("\n" + "-" * 70)
    print("测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  工具调用次数: {call_count[0]}")
    print(f"  执行的工具: {executed_tools}")
    print(f"  最终结果: {result['final_result']}")
    print("=" * 70)
    
    return result['success'] and result['iterations'] == 3


def test_case_2_multi_file_operation_full():
    """
    测试用例2：多文件操作（完整执行）
    
    模拟用户请求："读取1.txt和2.txt两个文件，把两个数相加的和写入result.txt文件"
    """
    print("\n" + "=" * 70)
    print("测试用例2：多文件操作（完整执行）")
    print("=" * 70)
    
    call_count = [0]
    executed_tools = []
    numbers = {}  # 存储读取的数字
    
    def mock_tool_executor(tool_name, params):
        """模拟工具执行器"""
        call_count[0] += 1
        executed_tools.append(tool_name)
        print(f"\n  [执行 {call_count[0]}] {tool_name}({params})")
        
        if tool_name == "read_file":
            filename = params.get("filename", "")
            print(f"    -> 读取文件: {filename}")
            
            # 模拟文件内容
            if "1.txt" in filename:
                content = "100"
                numbers['a'] = 100
            elif "2.txt" in filename:
                content = "200"
                numbers['b'] = 200
            else:
                content = "0"
            
            print(f"    -> 文件内容: {content}")
            return {
                "success": True,
                "content": content,
                "filename": filename
            }
            
        elif tool_name == "write_file":
            filename = params.get("filename", "")
            content = params.get("content", "")
            print(f"    -> 写入文件: {filename}")
            print(f"    -> 写入内容: {content}")
            
            return {
                "success": True,
                "filename": filename,
                "path": f"practice07/{filename}"
            }
        
        return {"success": True, "result": "mock"}
    
    def mock_llm_caller(messages):
        """模拟 LLM 决策器"""
        # 根据已执行的工具决定下一步
        read_count = executed_tools.count("read_file")
        
        if read_count == 0:
            print("  [LLM决策] 需要读取1.txt")
            return '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "practice07", "filename": "1.txt"}}}'
        
        elif read_count == 1:
            print("  [LLM决策] 需要读取2.txt")
            return '{"done": false, "tool_call": {"name": "read_file", "arguments": {"directory": "practice07", "filename": "2.txt"}}}'
        
        elif "write_file" not in executed_tools:
            print("  [LLM决策] 需要写入结果文件")
            return '{"done": false, "tool_call": {"name": "write_file", "arguments": {"directory": "practice07", "filename": "result.txt", "content": "300"}}}'
        
        else:
            print("  [LLM决策] 任务完成")
            return '{"done": true, "answer": "成功读取1.txt(100)和2.txt(200)，计算和为300，已写入result.txt文件。"}'
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="读取1.txt和2.txt两个文件，把两个数相加的和写入result.txt文件",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手，擅长文件操作和数学计算。",
        max_iterations=5
    )
    
    print("\n" + "-" * 70)
    print("测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  工具调用次数: {call_count[0]}")
    print(f"  执行的工具: {executed_tools}")
    print(f"  最终结果: {result['final_result']}")
    print("=" * 70)
    
    return result['success'] and result['iterations'] == 3


def test_case_3_webpage_processing_full():
    """
    测试用例3：网页处理链式调用（完整执行）
    
    模拟用户请求："访问网页并总结页面内容，保存到practice07/summary.txt"
    """
    print("\n" + "=" * 70)
    print("测试用例3：网页处理链式调用（完整执行）")
    print("=" * 70)
    
    call_count = [0]
    executed_tools = []
    
    def mock_tool_executor(tool_name, params):
        """模拟工具执行器"""
        call_count[0] += 1
        executed_tools.append(tool_name)
        print(f"\n  [执行 {call_count[0]}] {tool_name}({params})")
        
        if tool_name == "fetch_webpage":
            url = params.get("url", "")
            print(f"    -> 获取网页: {url}")
            
            # 模拟网页内容
            content = """宁夏大学新闻中心

标题：学校举办2024年毕业典礼
发布时间：2024-06-20

6月20日，宁夏大学2024年毕业典礼在文萃校区举行。校长在典礼上致辞，
鼓励毕业生们勇于追梦、敢于创新。共有3000余名毕业生参加了本次典礼。

典礼上，优秀毕业生代表发表了感言，回顾了大学四年的学习生活。
校长为毕业生代表颁发了学位证书。"""
            
            print(f"    -> 网页内容长度: {len(content)} 字符")
            return {
                "success": True,
                "content": content,
                "url": url
            }
            
        elif tool_name == "generate_summary":
            content = params.get("content", "")
            print(f"    -> 生成摘要，输入长度: {len(str(content))} 字符")
            
            summary = "宁夏大学于6月20日举办2024年毕业典礼，校长致辞鼓励毕业生勇于追梦。共有3000余名毕业生参加。"
            print(f"    -> 摘要: {summary}")
            return {
                "success": True,
                "summary": summary
            }
            
        elif tool_name == "write_file":
            filename = params.get("filename", "")
            content = params.get("content", "")
            print(f"    -> 写入文件: {filename}")
            print(f"    -> 内容预览: {str(content)[:50]}...")
            
            return {
                "success": True,
                "filename": filename,
                "path": f"practice07/{filename}"
            }
        
        return {"success": True, "result": "mock"}
    
    def mock_llm_caller(messages):
        """模拟 LLM 决策器"""
        # 根据已执行的工具决定下一步
        if "fetch_webpage" not in executed_tools:
            print("  [LLM决策] 需要获取网页内容")
            return '{"done": false, "tool_call": {"name": "fetch_webpage", "arguments": {"url": "https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html"}}}'
        
        elif "generate_summary" not in executed_tools:
            print("  [LLM决策] 需要生成摘要")
            return '{"done": false, "tool_call": {"name": "generate_summary", "arguments": {"content": "宁夏大学新闻..."}}}'
        
        elif "write_file" not in executed_tools:
            print("  [LLM决策] 需要保存到文件")
            return '{"done": false, "tool_call": {"name": "write_file", "arguments": {"directory": "practice07", "filename": "summary.txt", "content": "宁夏大学于6月20日举办2024年毕业典礼..."}}}'
        
        else:
            print("  [LLM决策] 任务完成")
            return '{"done": true, "answer": "成功获取网页内容并生成摘要，已保存到 practice07/summary.txt 文件。"}'
    
    # 执行链式调用
    result = execute_chained_tool_call(
        user_request="访问网页并总结页面内容，保存到practice07/summary.txt",
        tool_executor=mock_tool_executor,
        llm_caller=mock_llm_caller,
        system_prompt="你是一个智能助手，擅长网页抓取和内容分析。",
        max_iterations=5
    )
    
    print("\n" + "-" * 70)
    print("测试结果:")
    print(f"  成功: {result['success']}")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  工具调用次数: {call_count[0]}")
    print(f"  执行的工具: {executed_tools}")
    print(f"  最终结果: {result['final_result']}")
    print("=" * 70)
    
    return result['success'] and result['iterations'] == 3


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Practice 07: 链式工具调用完整测试")
    print("=" * 70)
    
    # 运行三个测试用例
    results = []
    
    results.append(("测试1-文件搜索", test_case_1_file_search_full()))
    results.append(("测试2-多文件操作", test_case_2_multi_file_operation_full()))
    results.append(("测试3-网页处理", test_case_3_webpage_processing_full()))
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试汇总")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "通过" if passed else "失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 70)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败！")
    print("=" * 70)
