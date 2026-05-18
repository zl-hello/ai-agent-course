import os
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("检查配置")
print("=" * 60)

# 检查当前目录
print(f"\n当前工作目录: {os.getcwd()}")
print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")

# 查找 .env 文件
env_paths = [
    ".env",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
]

print("\n查找 .env 文件:")
for path in env_paths:
    abs_path = os.path.abspath(path)
    exists = os.path.exists(path)
    print(f"  {abs_path}: {'存在' if exists else '不存在'}")

# 读取 .env 文件
print("\n读取 .env 文件内容:")
env_vars = {}
for path in env_paths:
    if os.path.exists(path):
        print(f"\n使用: {os.path.abspath(path)}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("文件内容:")
            print("-" * 40)
            print(content)
            print("-" * 40)
            
            # 解析
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
        break

print("\n解析的配置:")
for key, value in env_vars.items():
    print(f"  {key} = {value}")

print("\n关键配置:")
print(f"  LLM_BASE_URL: {env_vars.get('LLM_BASE_URL', '未设置')}")
print(f"  LLM_MODEL: {env_vars.get('LLM_MODEL', '未设置')}")
print(f"  LLM_API_KEY: {env_vars.get('LLM_API_KEY', '未设置')[:30]}..." if env_vars.get('LLM_API_KEY') else "  LLM_API_KEY: 未设置")

print("\n" + "=" * 60)
