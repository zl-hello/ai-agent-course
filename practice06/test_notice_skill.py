"""
Practice 06: Notice 技能测试脚本

测试场景：
1. 用户不说部门，要求写五一放假通知，应该以"XX部通知"开头
2. 用户表明是"销售部"，要求写通知，应该以"销售部通知"开头
"""

import os
import sys
import io

# 设置 UTF-8 编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from skills_manager import list_available_skills, load_skill_content, format_skills_as_json


def test_skill_loading():
    """测试技能加载"""
    print("=" * 60)
    print("测试 1: 加载所有技能")
    print("=" * 60)
    
    skills = list_available_skills()
    print(f"\n✅ 找到 {len(skills)} 个技能")
    
    # 查找 notice 技能
    notice_skill = None
    for skill in skills:
        if skill['name'] == 'notice':
            notice_skill = skill
            break
    
    if notice_skill:
        print(f"✅ 找到 notice 技能: {notice_skill['name']}")
        print(f"   描述: {notice_skill['description']}")
        return True
    else:
        print("❌ 未找到 notice 技能")
        return False


def test_skill_content_loading():
    """测试加载技能内容"""
    print("\n" + "=" * 60)
    print("测试 2: 加载 notice 技能内容")
    print("=" * 60)
    
    result = load_skill_content('notice')
    
    if result.get('success'):
        print(f"✅ 成功加载技能内容")
        print(f"   技能名称: {result['name']}")
        print(f"   目录: {result['directory']}")
        print(f"   内容长度: {len(result['content'])} 字符")
        
        # 检查内容中是否包含关键规则
        content = result['content']
        if 'XX部通知' in content:
            print("✅ 内容包含 'XX部通知' 规则")
        else:
            print("⚠️  内容可能缺少 'XX部通知' 规则")
        
        if '不能以"通知"二字开头' in content:
            print("✅ 内容包含标题格式规则")
        else:
            print("⚠️  内容可能缺少标题格式规则")
        
        return True
    else:
        print(f"❌ 加载失败: {result.get('error')}")
        return False


def test_skill_detection():
    """测试技能检测逻辑"""
    print("\n" + "=" * 60)
    print("测试 3: 技能触发词检测")
    print("=" * 60)
    
    # 定义触发词映射（从 agent_with_skills.py 复制）
    skill_triggers = {
        'notice': ['写通知', '撰写通知', '修改通知', '润色通知', '通知怎么写', '帮我写个通知', '通知'],
    }
    
    test_cases = [
        ("帮我写个通知", True),
        ("撰写一个关于五一放假的通知", True),
        ("修改这个通知", True),
        ("润色一下通知", True),
        ("通知怎么写", True),
        ("你好", False),
        ("今天天气怎么样", False),
    ]
    
    for user_input, should_trigger in test_cases:
        user_input_lower = user_input.lower()
        detected = False
        
        for skill_name, triggers in skill_triggers.items():
            for trigger in triggers:
                if trigger in user_input_lower:
                    detected = True
                    break
        
        status = "✅" if detected == should_trigger else "❌"
        expected = "应该触发" if should_trigger else "不应该触发"
        actual = "触发" if detected else "未触发"
        
        print(f"{status} 输入: '{user_input}' -> {actual} (期望: {expected})")


def simulate_scenario_1():
    """模拟场景1：用户不说部门"""
    print("\n" + "=" * 60)
    print("测试场景 1: 用户不说部门")
    print("=" * 60)
    print("\n用户输入: '帮我写个关于五一放假的通知'")
    print("期望: 以 'XX部通知' 开头")
    print("\n系统处理流程:")
    print("1. 检测触发词 '写通知' -> 匹配 notice 技能")
    print("2. 加载 notice 技能内容")
    print("3. 将技能内容注入 system prompt")
    print("4. LLM 根据技能规则生成通知")
    print("\n预期输出格式:")
    print("XX部通知")
    print("")
    print("各位同事：")
    print("")
    print("根据国家法定节假日安排，现将五一劳动节放假事宜通知如下：")
    print("...")


def simulate_scenario_2():
    """模拟场景2：用户表明部门"""
    print("\n" + "=" * 60)
    print("测试场景 2: 用户表明是销售部")
    print("=" * 60)
    print("\n用户输入: '我是销售部的，帮我写个关于五一放假的通知'")
    print("期望: 以 '销售部通知' 开头")
    print("\n系统处理流程:")
    print("1. 检测触发词 '写通知' -> 匹配 notice 技能")
    print("2. 加载 notice 技能内容")
    print("3. 将技能内容注入 system prompt")
    print("4. LLM 识别用户部门为'销售部'，根据技能规则生成通知")
    print("\n预期输出格式:")
    print("销售部通知")
    print("")
    print("各位同事：")
    print("")
    print("根据国家法定节假日安排，现将五一劳动节放假事宜通知如下：")
    print("...")


def test_json_format():
    """测试 JSON 格式输出"""
    print("\n" + "=" * 60)
    print("测试 4: JSON 格式技能列表")
    print("=" * 60)
    
    skills = list_available_skills()
    json_str = format_skills_as_json(skills)
    
    print("\nJSON 格式输出:")
    print(json_str)
    
    # 验证 JSON 格式
    import json
    try:
        data = json.loads(json_str)
        if 'skills' in data and isinstance(data['skills'], list):
            print("\n✅ JSON 格式正确")
            for skill in data['skills']:
                if 'name' in skill and 'description' in skill:
                    print(f"   - {skill['name']}: {skill['description'][:40]}...")
        else:
            print("\n❌ JSON 格式不正确")
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON 解析错误: {e}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Practice 06: Notice 技能测试")
    print("=" * 60)
    
    # 运行所有测试
    test_skill_loading()
    test_skill_content_loading()
    test_skill_detection()
    test_json_format()
    simulate_scenario_1()
    simulate_scenario_2()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n要运行实际的 Agent 测试，请执行:")
    print("  cd practice06")
    print("  python agent_with_skills.py")
    print("\n然后输入:")
    print("  帮我写个关于五一放假的通知")
    print("  我是销售部的，帮我写个关于五一放假的通知")


if __name__ == "__main__":
    main()
