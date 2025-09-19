#!/usr/bin/env python3
"""
GaiaHandAdapter 使用示例

展示如何使用 core.py 中的 GaiaHandAdapter 进行高级手部控制。
包括手部连接、关节控制、手势执行、运动学计算等功能。
"""

import time
import sys
import os
import math

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand import create_hand, HandSide
from hand.gaiahand.hand_mappings import FingerType, JointType, GestureType
from hand.utils.serial_utils import auto_detect_gaia_ports

def detect_serial_ports():
    """检测可用的串口"""
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

def test_hand_creation():
    """测试手部创建功能"""
    print("=== 测试手部创建功能 ===")
    
    # 检测串口
    ports_config = detect_serial_ports()
    if not ports_config:
        print("串口检测失败，无法创建手部实例")
        return None, None
    
    print(f"使用串口配置:")
    print(f"  左手: {ports_config['left']}")
    print(f"  右手: {ports_config['right']}")
    
    # 创建右手实例
    print("\n创建右手实例...")
    right_hand = create_hand("gaia", "right", port=ports_config['right'])
    print(f"  手部类型: {right_hand.hand_type.value}")
    print(f"  手部侧边: {right_hand.hand_side_name}")
    print(f"  是否为右手: {right_hand.is_right_hand}")
    
    # 创建左手实例
    print("\n创建左手实例...")
    left_hand = create_hand("gaia", "left", port=ports_config['left'])
    print(f"  手部类型: {left_hand.hand_type.value}")
    print(f"  手部侧边: {left_hand.hand_side_name}")
    print(f"  是否为左手: {left_hand.is_left_hand}")
    
    # 创建双手实例
    print("\n创建双手实例...")
    double_hand = create_hand("gaia", "double", 
                             left_port=ports_config['left'], 
                             right_port=ports_config['right'])
    print(f"  手部类型: {double_hand.hand_type.value}")
    print(f"  手部侧边: {double_hand.hand_side_name}")
    print(f"  是否为双手: {double_hand.is_double_hand}")
    
    return right_hand, double_hand

def test_hand_connection(hand, hand_name):
    """测试手部连接功能"""
    print(f"\n=== 测试{hand_name}连接功能 ===")
    
    try:
        # 连接手部
        print(f"正在连接{hand_name}...")
        if hand.connect():
            print(f"{hand_name}连接成功")
            
            # 检查连接状态
            print(f"  连接状态: {'已连接' if hand.is_connected() else '未连接'}")
            
            return True
        else:
            print(f"{hand_name}连接失败")
            return False
            
    except Exception as e:
        print(f"{hand_name}连接过程中发生错误: {e}")
        return False

def test_motor_enable(hand, hand_name):
    """测试电机使能功能"""
    print(f"\n=== 测试{hand_name}电机使能功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过电机使能测试")
        return False
    
    try:
        # 测试单个电机使能
        print("测试单个电机使能...")
        for motor_id in range(1, 6):  # 测试1-5号电机
            print(f"使能电机 {motor_id}...")
            success = hand.enable_motor(motor_id, True)
            print(f"  结果: {'成功' if success else '失败'}")
            time.sleep(0.1)
        
        # 测试所有电机使能
        print("\n测试所有电机使能...")
        success = hand.enable_all_motors(True)
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(1)
        
        # 测试广播使能
        print("\n测试广播使能...")
        enable_states = {1: True, 2: True, 3: True, 4: True, 5: True}
        success = hand.enable_motors_broadcast(enable_states)
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(1)
        
        # 测试广播使能所有电机
        print("\n测试广播使能所有电机...")
        success = hand.enable_all_motors_broadcast(True)
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(2)
        
        print(f"{hand_name}电机使能测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}电机使能测试失败: {e}")
        return False

def test_joint_angle_control(hand, hand_name):
    """测试关节角度控制功能"""
    print(f"\n=== 测试{hand_name}关节角度控制功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过关节角度控制测试")
        return False
    
    try:
        # 测试设置单个关节角度
        print("测试设置单个关节角度...")
        
        # 测试不同手指和关节
        test_configs = [
            (FingerType.THUMB, JointType.JOINT_1, 30.0),
            (FingerType.INDEX, JointType.JOINT_2, 45.0),
            (FingerType.MIDDLE, JointType.JOINT_3, 60.0),
            (FingerType.RING, JointType.JOINT_1, 15.0),
            (FingerType.LITTLE, JointType.JOINT_2, 75.0)
        ]
        
        for finger, joint, angle_deg in test_configs:
            angle_rad = math.radians(angle_deg)
            print(f"设置{finger.value}的{joint.value}为{angle_deg}度...")
            success = hand.set_joint_angle(finger, joint, angle_rad, speed=0.5)
            print(f"  结果: {'成功' if success else '失败'}")
            time.sleep(0.5)
        
        # 等待运动完成
        time.sleep(2)
        
        # 测试获取关节角度
        print("\n测试获取关节角度...")
        for finger, joint, _ in test_configs:
            angle_rad = hand.get_joint_angle(finger, joint)
            angle_deg = math.degrees(angle_rad)
            print(f"{finger.value}的{joint.value}当前角度: {angle_deg:.2f}度")
        
        print(f"{hand_name}关节角度控制测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}关节角度控制测试失败: {e}")
        return False

def test_finger_control(hand, hand_name):
    """测试手指控制功能"""
    print(f"\n=== 测试{hand_name}手指控制功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过手指控制测试")
        return False
    
    try:
        # 测试控制单个手指
        print("测试控制单个手指...")
        
        # 控制拇指
        thumb_positions = [30.0, 45.0, 60.0]  # 三个关节的角度
        print("控制拇指...")
        success = hand.control_single_finger(0, thumb_positions)  # 拇指ID为0
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(1)
        
        # 控制食指
        index_positions = [15.0, 30.0, 45.0]
        print("控制食指...")
        success = hand.control_single_finger(1, index_positions)  # 食指ID为1
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(1)
        
        # 测试控制单个关节
        print("\n测试控制单个关节...")
        success = hand.control_finger_joint(2, 1, 90.0)  # 中指第二个关节90度
        print(f"  控制中指第二个关节: {'成功' if success else '失败'}")
        time.sleep(1)
        
        # 测试控制多个手指
        print("\n测试控制多个手指...")
        finger_positions = {
            0: [0.0, 0.0, 0.0],    # 拇指伸直
            1: [45.0, 45.0, 45.0], # 食指弯曲
            2: [90.0, 90.0, 90.0]  # 中指弯曲
        }
        success = hand.control_multiple_fingers(finger_positions)
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(2)
        
        print(f"{hand_name}手指控制测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}手指控制测试失败: {e}")
        return False

def test_gesture_execution(hand, hand_name):
    """测试手势执行功能"""
    print(f"\n=== 测试{hand_name}手势执行功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过手势执行测试")
        return False
    
    try:
        # 测试执行预定义手势
        print("测试执行预定义手势...")
        
        gestures = [
            GestureType.OPEN_HAND,
            GestureType.CLOSE_HAND,
            GestureType.POINT,
            GestureType.THUMB_UP,
            GestureType.VICTORY
        ]
        
        for gesture in gestures:
            print(f"执行手势: {gesture.value}...")
            success = hand.perform_gesture(gesture, speed=0.5, duration=2.0)
            print(f"  结果: {'成功' if success else '失败'}")
            time.sleep(3)  # 等待手势完成
        
        print(f"{hand_name}手势执行测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}手势执行测试失败: {e}")
        return False

def test_kinematics(hand, hand_name):
    """测试运动学功能"""
    print(f"\n=== 测试{hand_name}运动学功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过运动学测试")
        return False
    
    try:
        # 测试正运动学
        print("测试正运动学...")
        for finger in FingerType:
            x, y = hand.forward_kinematics(finger)
            print(f"{finger.value}指尖位置: ({x:.2f}, {y:.2f})")
        
        # 测试逆运动学
        print("\n测试逆运动学...")
        target_x, target_y = 50.0, 30.0
        for finger in [FingerType.INDEX, FingerType.MIDDLE]:
            angles = hand.inverse_kinematics(finger, target_x, target_y)
            print(f"{finger.value}到达位置({target_x}, {target_y})的关节角度: {angles}")
        
        # 测试移动到指定位置
        print("\n测试移动到指定位置...")
        for finger in [FingerType.INDEX]:
            success = hand.move_finger_to_position(finger, target_x, target_y, speed=0.5)
            print(f"{finger.value}移动到位置({target_x}, {target_y}): {'成功' if success else '失败'}")
            time.sleep(2)
        
        print(f"{hand_name}运动学测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}运动学测试失败: {e}")
        return False

def test_jog_control(hand, hand_name):
    """测试点动控制功能"""
    print(f"\n=== 测试{hand_name}点动控制功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过点动控制测试")
        return False
    
    try:
        # 测试点动控制
        print("测试点动控制...")
        
        # 测试食指第一个关节
        finger = FingerType.INDEX
        joint = JointType.JOINT_1
        
        # 顺时针点动
        print(f"{finger.value}的{joint.value}顺时针点动...")
        success = hand.jog_joint(finger, joint, 1)  # 1=顺时针
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(2)
        
        # 停止
        print(f"{finger.value}的{joint.value}停止...")
        success = hand.jog_joint(finger, joint, 0)  # 0=停止
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(1)
        
        # 逆时针点动
        print(f"{finger.value}的{joint.value}逆时针点动...")
        success = hand.jog_joint(finger, joint, 2)  # 2=逆时针
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(2)
        
        # 停止
        print(f"{finger.value}的{joint.value}停止...")
        success = hand.jog_joint(finger, joint, 0)  # 0=停止
        print(f"  结果: {'成功' if success else '失败'}")
        time.sleep(1)
        
        print(f"{hand_name}点动控制测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}点动控制测试失败: {e}")
        return False

def test_motor_status_monitoring(hand, hand_name):
    """测试电机状态监控功能"""
    print(f"\n=== 测试{hand_name}电机状态监控功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过电机状态监控测试")
        return False
    
    try:
        # 测试获取单个电机状态
        print("测试获取单个电机状态...")
        for motor_id in range(1, 6):
            status = hand.get_motor_status(motor_id)
            print(f"电机 {motor_id} 状态: {status}")
            time.sleep(0.1)
        
        # 测试获取所有电机状态
        print("\n测试获取所有电机状态...")
        all_status = hand.get_motor_status()  # 不指定motor_id
        print(f"所有电机状态: {all_status}")
        
        # 测试获取关节位置
        print("\n测试获取关节位置...")
        positions = hand.get_joint_positions()
        print(f"关节位置: {positions}")
        
        print(f"{hand_name}电机状态监控测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}电机状态监控测试失败: {e}")
        return False

def test_emergency_stop(hand, hand_name):
    """测试紧急停止功能"""
    print(f"\n=== 测试{hand_name}紧急停止功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过紧急停止测试")
        return False
    
    try:
        # 先设置一些关节角度
        print("设置关节角度...")
        for finger in FingerType:
            for joint in JointType:
                hand.set_joint_angle(finger, joint, math.radians(30.0), speed=0.3)
                time.sleep(0.1)
        
        time.sleep(2)
        
        # 执行紧急停止
        print("执行紧急停止...")
        success = hand.emergency_stop()
        print(f"  结果: {'成功' if success else '失败'}")
        
        # 等待紧急停止生效
        time.sleep(1)
        
        print(f"{hand_name}紧急停止测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}紧急停止测试失败: {e}")
        return False

def test_hand_zero(hand, hand_name):
    """测试手部回零功能"""
    print(f"\n=== 测试{hand_name}回零功能 ===")
    
    if not hand.is_connected():
        print(f"{hand_name}未连接，跳过回零测试")
        return False
    
    try:
        # 执行手部回零
        print("执行手部回零...")
        success = hand.hand_zero()
        print(f"  结果: {'成功' if success else '失败'}")
        
        # 等待回零完成
        time.sleep(3)
        
        # 检查回零后的状态
        print("检查回零后的状态...")
        positions = hand.get_joint_positions()
        print(f"  关节位置: {positions}")
        
        print(f"{hand_name}回零测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}回零测试失败: {e}")
        return False

def test_context_manager(hand, hand_name):
    """测试上下文管理器功能"""
    print(f"\n=== 测试{hand_name}上下文管理器功能 ===")
    
    try:
        # 使用上下文管理器
        print("使用上下文管理器...")
        with create_hand("gaia", "right", port=hand.port) as ctx_hand:
            print(f"  在上下文管理器中: {'已连接' if ctx_hand.is_connected() else '未连接'}")
            
            # 执行一些操作
            ctx_hand.enable_all_motors_broadcast(True)
            time.sleep(1)
            
            # 设置一个关节角度
            ctx_hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, math.radians(45.0))
            time.sleep(1)
        
        print("  上下文管理器退出，连接已自动关闭")
        print(f"{hand_name}上下文管理器测试完成")
        return True
        
    except Exception as e:
        print(f"{hand_name}上下文管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始 GaiaHandAdapter 使用示例测试")
    print("=" * 60)
    
    # 测试手部创建
    right_hand, double_hand = test_hand_creation()
    
    if right_hand:
        try:
            # 测试右手功能
            if test_hand_connection(right_hand, "右手"):
                test_motor_enable(right_hand, "右手")
                test_joint_angle_control(right_hand, "右手")
                test_finger_control(right_hand, "右手")
                test_gesture_execution(right_hand, "右手")
                test_kinematics(right_hand, "右手")
                test_jog_control(right_hand, "右手")
                test_motor_status_monitoring(right_hand, "右手")
                test_emergency_stop(right_hand, "右手")
                test_hand_zero(right_hand, "右手")
                test_context_manager(right_hand, "右手")
        finally:
            # 关闭右手连接
            print("\n=== 关闭右手连接 ===")
            right_hand.close()
            print("右手连接已关闭")
    
    if double_hand:
        try:
            # 测试双手功能
            if test_hand_connection(double_hand, "双手"):
                test_motor_enable(double_hand, "双手")
                test_joint_angle_control(double_hand, "双手")
                test_finger_control(double_hand, "双手")
                test_gesture_execution(double_hand, "双手")
                test_kinematics(double_hand, "双手")
                test_jog_control(double_hand, "双手")
                test_motor_status_monitoring(double_hand, "双手")
                test_emergency_stop(double_hand, "双手")
                test_hand_zero(double_hand, "双手")
        finally:
            # 关闭双手连接
            print("\n=== 关闭双手连接 ===")
            double_hand.close()
            print("双手连接已关闭")
    
    print("\n" + "=" * 60)
    print("GaiaHandAdapter 使用示例测试完成")

if __name__ == "__main__":
    main() 