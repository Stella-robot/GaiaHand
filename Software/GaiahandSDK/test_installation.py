#!/usr/bin/env python3
"""
手部控制模块安装测试脚本

用于验证模块是否正确安装和导入。
"""

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试主模块导入
        import hand
        print("✓ 主模块导入成功")
        
        # 测试子模块导入
        from hand import create_hand
        print("✓ create_hand函数导入成功")
        
        from hand.gaiahand import gaia_hand
        print("✓ gaia_hand模块导入成功")
        
        from hand.gaiahand import hand_mappings
        print("✓ hand_mappings模块导入成功")
        
        from hand.gaiahand import motor
        print("✓ motor模块导入成功")
        
        from hand.utils import serial_utils
        print("✓ serial_utils模块导入成功")
        
        # 测试枚举类型导入
        from hand.gaiahand.hand_mappings import HandType, HandSide, FingerType, JointType, GestureType
        print("✓ 枚举类型导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

def test_hand_creation():
    """测试手部实例创建"""
    print("\n测试手部实例创建...")
    
    try:
        from hand import create_hand
        from hand.gaiahand.hand_mappings import HandType, HandSide
        
        # 测试Gaia手部创建
        hand = create_hand(HandType.GAIA, HandSide.RIGHT)
        print("✓ Gaia手部实例创建成功")
        
        # 移除PantheonHand测试
        print("✓ 只支持GaiaHand")
        
        return True
        
    except Exception as e:
        print(f"✗ 手部实例创建失败: {e}")
        return False

def test_serial_utils():
    """测试串口工具"""
    print("\n测试串口工具...")
    
    try:
        from hand.utils.serial_utils import get_system_type, get_available_ports
        
        system_type = get_system_type()
        print(f"✓ 系统类型检测成功: {system_type}")
        
        ports = get_available_ports()
        print(f"✓ 串口检测成功，找到 {len(ports)} 个串口")
        
        return True
        
    except Exception as e:
        print(f"✗ 串口工具测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("手部控制模块安装测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_hand_creation,
        test_serial_utils,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！模块安装成功。")
        print("\n使用示例:")
        print("from hand import create_hand, HandType, HandSide")
        print("hand = create_hand(HandType.GAIA, HandSide.RIGHT)")
    else:
        print("❌ 部分测试失败，请检查安装。")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 