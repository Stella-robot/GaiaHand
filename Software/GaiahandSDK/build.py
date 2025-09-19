#!/usr/bin/env python3
"""
手部控制模块构建脚本

用于构建、安装和测试手部控制模块。
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """运行命令并处理错误"""
    print(f"\n{'='*50}")
    if description:
        print(f"执行: {description}")
    print(f"命令: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("需要Python 3.7或更高版本")
        return False
    print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n安装依赖包...")
    return run_command("pip install -r requirements.txt", "安装依赖包")

def build_package():
    """构建包"""
    print("\n构建包...")
    
    # 清理之前的构建
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("*.egg-info"):
        for egg_info in Path(".").glob("*.egg-info"):
            shutil.rmtree(egg_info)
    
    return run_command("python setup.py sdist bdist_wheel", "构建源码包和轮子包")

def install_package():
    """安装包"""
    print("\n安装包...")
    return run_command("pip install -e .", "以开发模式安装包")

def test_installation():
    """测试安装"""
    print("\n测试安装...")
    return run_command("python test_installation.py", "运行安装测试")

def main():
    """主函数"""
    print("手部控制模块构建工具")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 构建包
    if not build_package():
        print("❌ 包构建失败")
        sys.exit(1)
    
    # 安装包
    if not install_package():
        print("❌ 包安装失败")
        sys.exit(1)
    
    # 测试安装
    if not test_installation():
        print("❌ 安装测试失败")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 构建和安装完成！")
    print("="*50)
    print("\n现在可以使用以下方式导入模块:")
    print("from hand import create_hand, HandType, HandSide")
    print("hand = create_hand(HandType.GAIA, HandSide.RIGHT)")

if __name__ == "__main__":
    main() 