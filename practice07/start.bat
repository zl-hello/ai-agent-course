@echo off
chcp 65001 >nul
echo ============================================
echo  启动 Practice 07: 链式工具调用 Agent
echo ============================================
echo.
echo 功能特点:
echo   - 链式工具调用（Chained Tool Calls）
echo   - 前一个工具的输出作为后一个工具的输入
echo   - LLM 根据中间结果自主决定下一步工具调用
echo.
echo 测试示例:
echo   1. 分析目录并读取文件
echo      输入: 分析目录 ./practice07 并读取文件
echo   2. 搜索历史并总结
echo      输入: 搜索历史关于通知的内容并总结
echo   3. 使用技能
echo      输入: 使用 notice 技能帮我写个通知
echo.
echo 正在启动程序，请稍候...
echo.
python agent_with_skills.py
pause
