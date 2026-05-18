"""
调试环境变量读取
"""
import os
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("调试环境变量读取")
print("=" * 60)

# 显示当前工作目录
print(f"\n当前工作目录: {os.getcwd()}")
print(f"脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")

# 尝试多个路径查找 .env 文件
env_path = ".env"
possible_paths = [
    env_path,  # 当前目录
    os.path.join(os.path.dirname(os.path.abspath(__file__)), env_path),  # 脚本所在目录
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), env_path),  # 上级目录
]

print("\n查找 .env 文件:")
found_path = None
for path in possible_paths:
    abs_path = os.path.abspath(path)
    exists = os.path.exists(path)
    print(f"  - {abs_path}")
    print(f"    存在: {exists}")
    if exists and not found_path:
        found_path = path

if found_path:
    print(f"\n使用的 .env 文件: {os.path.abspath(found_path)}")
    
    print("\n.env 文件内容:")
    print("-" * 60)
    with open(found_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    print("-" * 60)
    
    # 解析环境变量
    print("\n解析的环境变量:")
    env_vars = {}
    with open(found_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                env_vars[key] = value
                print(f"  {key} = {value}")
    
    print("\n关键配置:")
    print(f"  LLM_BASE_URL: {env_vars.get('LLM_BASE_URL', '未设置')}")
    print(f"  LLM_MODEL: {env_vars.get('LLM_MODEL', '未设置')}")
    print(f"  LLM_API_KEY: {env_vars.get('LLM_API_KEY', '未设置')[:20]}..." if env_vars.get('LLM_API_KEY') else "  LLM_API_KEY: 未设置")
else:
    print("\n[错误] 找不到 .env 文件！")

print("\n" + "=" * 60)
