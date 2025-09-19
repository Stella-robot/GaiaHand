#!/usr/bin/env python3
"""
测试 move_joints_pos 功能

测试不同手部类型的 move_joints_pos 方法，包括单手和双手模式。
"""

import time
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand import create_hand, HandSide
from hand.utils.serial_utils import auto_detect_gaia_ports

def detect_serial_ports():
    """
    检测可用的串口
    
    Returns:
        dict: 串口配置信息
    """
    try:
        print("正在检测可用串口...")
        ports_config = auto_detect_gaia_ports()
        
        if not ports_config or not ports_config['available']:
            print("未检测到可用串口，请检查硬件连接")
            return None
        
        return ports_config
        
    except Exception as e:
        print(f"串口检测失败: {e}")
        return None

def test_gaia_hand_move_joints_pos(ports_config):
    """测试 GaiaHand 的 move_joints_pos 功能"""
    print("=== 测试 GaiaHand move_joints_pos 功能 ===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过单手测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand 实例
        hand = create_hand("gaia", "right", port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand 连接成功 (串口: {ports_config['right']})")
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(2)
            
            # 测试单手模式 - 15个关节位置（非广播模式，默认）
            print("\n--- 测试单手模式（非广播） ---")
            
            # 创建测试位置数据：所有关节都设置为30度
            positions = [30.0] * 15  # 15个关节，每个30度
            
            print(f"设置位置数据: {positions}")
            success = hand.move_joints_pos(positions, speed=0.5, use_broadcast=False)
            print(f"非广播模式结果: {'成功' if success else '失败'}")
            
            # 等待2秒
            time.sleep(1)
            
            # 测试单手模式 - 广播模式
            print("\n--- 测试单手模式（广播模式） ---")
            
            # 创建测试位置数据：所有关节都设置为45度
            positions = [45.0] * 15  # 15个关节，每个45度
            
            print(f"设置位置数据: {positions}")
            success = hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
            print(f"广播模式结果: {'成功' if success else '失败'}")
            
            # 等待2秒
            time.sleep(1)
            
            # 测试单手模式 - 自定义位置数据
            print("\n--- 测试单手模式（自定义位置） ---")
            
            # 创建自定义位置数据：每个手指不同的角度
            custom_positions = [
                # 拇指的3个关节
                45.0, 30.0, 15.0,
                # 食指的3个关节
                60.0, 45.0, 30.0,
                # 中指的3个关节
                75.0, 60.0, 45.0,
                # 无名指的3个关节
                90.0, 75.0, 60.0,
                # 小指的3个关节
                105.0, 90.0, 75.0
            ]
            
            print(f"设置自定义位置数据: {custom_positions}")
            success = hand.move_joints_pos(custom_positions, speed=0.5, use_broadcast=False)
            print(f"自定义位置结果: {'成功' if success else '失败'}")
            
            # 等待2秒
            time.sleep(2)
            
            # 测试单手模式 - 手势执行
            print("\n--- 测试单手模式（手势执行） ---")
            
            # 握拳手势（所有关节弯曲）
            fist_positions = [90.0] * 15
            print("执行握拳手势...")
            success = hand.move_joints_pos(fist_positions, speed=0.5, use_broadcast=False)
            print(f"握拳结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 张开手势（所有关节伸直）
            open_positions = [0.0] * 15
            print("执行张开手势...")
            success = hand.move_joints_pos(open_positions, speed=0.5, use_broadcast=True)
            print(f"张开结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            # 下使能所有关节
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            
            hand.close()

def test_gaia_hand_double_move_joints_pos(ports_config):
    """测试 GaiaHand 双手模式的 move_joints_pos 功能"""
    print("\n=== 测试 GaiaHand 双手模式 move_joints_pos 功能 ===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("未找到可用的左右手串口，跳过双手测试")
        return
    
    hand = None
    try:
        # 创建双手 GaiaHand 实例
        hand = create_hand("gaia", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand 双手模式连接成功 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试双手模式 - 30个关节位置
            print("\n--- 测试双手模式（非广播） ---")
            
            # 创建双手测试位置数据
            # 修改顺序：前15个是右手，后15个是左手
            right_positions = [15.0] * 15  # 右手所有关节15度
            left_positions = [45.0] * 15   # 左手所有关节45度
            double_positions = right_positions + left_positions
            
            print(f"设置双手位置数据: 右手{right_positions[:3]}..., 左手{left_positions[:3]}...")
            
            # 使用非广播模式
            success = hand.move_joints_pos(double_positions, speed=0.5, use_broadcast=False)
            print(f"双手非广播模式结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 使用广播模式
            print("\n--- 测试双手模式（广播模式） ---")
            success = hand.move_joints_pos(double_positions, speed=0.5, use_broadcast=True)
            print(f"双手广播模式结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试双手模式 - 自定义位置数据
            print("\n--- 测试双手模式（自定义位置） ---")
            
            # 右手：拇指弯曲，其他手指伸直
            right_custom = [
                # 拇指的3个关节
                90.0, 90.0, 90.0,
                # 其他手指的3个关节
                0.0, 0.0, 0.0,  # 食指
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            # 左手：食指弯曲，其他手指伸直
            left_custom = [
                # 拇指的3个关节
                0.0, 0.0, 0.0,
                # 食指的3个关节
                90.0, 90.0, 90.0,
                # 其他手指的3个关节
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            custom_double_positions = right_custom + left_custom
            print(f"设置自定义双手位置数据: 右手拇指弯曲，左手食指弯曲")
            success = hand.move_joints_pos(custom_double_positions, speed=0.5, use_broadcast=False)
            print(f"自定义双手位置结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试双手模式 - 手势执行
            print("\n--- 测试双手模式（手势执行） ---")
            
            # 双手握拳
            double_fist = [90.0] * 30
            print("执行双手握拳手势...")
            success = hand.move_joints_pos(double_fist, speed=0.5, use_broadcast=False)
            print(f"双手握拳结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 双手张开
            double_open = [0.0] * 30
            print("执行双手张开手势...")
            success = hand.move_joints_pos(double_open, speed=0.5, use_broadcast=True)
            print(f"双手张开结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand 双手模式连接失败 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 双手模式测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            # 下使能所有关节
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            
            hand.close()

def test_gaia_hand_smooth_transition(ports_config):
    """测试 GaiaHand 平滑过渡功能"""
    print("\n=== 测试 GaiaHand 平滑过渡功能 ===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过平滑过渡测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand 实例
        hand = create_hand("gaia", "right", port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand 连接成功，开始平滑过渡测试 (串口: {ports_config['right']})")
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 创建起始和结束位置
            start_positions = [0.0] * 15
            end_positions = [90.0] * 15
            
            print("执行平滑过渡：从伸直状态到弯曲状态")
            
            # 分5步过渡（非广播模式，更稳定）
            for i in range(6):
                t = i / 5.0
                positions = []
                for j in range(15):
                    pos = start_positions[j] + (end_positions[j] - start_positions[j]) * t
                    positions.append(pos)
                
                print(f"步骤 {i+1}/6: 过渡进度 {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=False)
                time.sleep(0.5)
            
            print("平滑过渡完成")
            
            time.sleep(2)
            
            # 反向过渡：从弯曲状态到伸直状态
            print("执行反向过渡：从弯曲状态到伸直状态")
            
            for i in range(6):
                t = i / 5.0
                positions = []
                for j in range(15):
                    pos = end_positions[j] + (start_positions[j] - end_positions[j]) * t
                    positions.append(pos)
                
                print(f"步骤 {i+1}/6: 过渡进度 {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=False)
                time.sleep(0.5)
            
            print("反向过渡完成")
            
        else:
            print(f"GaiaHand 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 平滑过渡测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            # 下使能所有关节
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            
            hand.close()

def test_reset_pose_zero(ports_config):
    """测试手部回零功能"""
    print("\n=== 测试手部回零功能 ===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过回零测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand 实例
        hand = create_hand("gaia", "right", port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand 连接成功，开始回零测试 (串口: {ports_config['right']})")
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(2)
            
            # 执行回零操作
            print("执行回零操作...")
            hand.hand_zero()
            print("回零操作完成")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 回零测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            # 下使能所有关节
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            
            hand.close()


def main():
    """主测试函数"""
    print("开始测试 move_joints_pos 功能")
    print("=" * 50)
    
    # 检测串口
    ports_config = detect_serial_ports()
    
    if not ports_config:
        print("串口检测失败，无法进行测试")
        return
    
    print(f"\n使用串口配置:")
    print(f"  左手: {ports_config['left']}")
    print(f"  右手: {ports_config['right']}")
    print(f"  可用串口: {ports_config['available']}")

    # 测试回零位
    test_reset_pose_zero(ports_config)
    
    # 测试 GaiaHand 单手模式
    # test_gaia_hand_move_joints_pos(ports_config)
    
    # 测试 GaiaHand 双手模式
    # test_gaia_hand_double_move_joints_pos(ports_config)
    
    # 测试 GaiaHand 平滑过渡
    # test_gaia_hand_smooth_transition(ports_config)
    
    print("\n" + "=" * 50)
    print("所有测试完成")

if __name__ == "__main__":
    main() 