#!/usr/bin/env python3
"""
Motor 类使用示例

展示如何使用 motor.py 中的 Motor 类进行底层电机控制。
包括电机连接、使能、角度设置、状态查询、点动控制等功能。
"""

import time
import sys
import os
import math

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand.gaiahand.motor import Motor

def test_motor_connection():
    """测试电机连接功能"""
    print("=== 测试电机连接功能 ===")
    
    # 创建电机实例
    motor = Motor(port='COM4', baudrate=256000)
    
    try:
        # 连接电机
        print("正在连接电机...")
        if motor.connect():
            print("电机连接成功")
            
            # 等待连接稳定
            time.sleep(1)
            
            # 检查连接状态
            print(f"连接状态: {'已连接' if motor.is_connected() else '未连接'}")
            
            return motor
        else:
            print("电机连接失败")
            return None
            
    except Exception as e:
        print(f"连接过程中发生错误: {e}")
        return None

def test_motor_enable(motor):
    """测试电机使能功能"""
    print("\n=== 测试电机使能功能 ===")
    
    if not motor:
        print("电机未连接，跳过使能测试")
        return False
    
    try:
        # 测试单个电机使能
        print("测试单个电机使能...")
        for motor_id in range(1, 6):  # 测试1-5号电机
            print(f"使能电机 {motor_id}...")
            command_id = motor.enable_motor(motor_id, True)
            print(f"  命令ID: {command_id}")
            time.sleep(0.1)
        
        # 等待使能完成
        time.sleep(2)
        
        # 测试所有电机使能
        print("\n测试所有电机使能...")
        command_id = motor.enable_all_motors(True)
        print(f"  命令ID: {command_id}")
        time.sleep(2)
        
        # 测试广播使能
        print("\n测试广播使能...")
        enable_states = {1: True, 2: True, 3: True, 4: True, 5: True}
        command_id = motor.enable_motors_broadcast(enable_states)
        print(f"  命令ID: {command_id}")
        time.sleep(1)
        
        # 测试广播使能所有电机
        print("\n测试广播使能所有电机...")
        command_id = motor.enable_all_motors_broadcast(True)
        print(f"  命令ID: {command_id}")
        time.sleep(2)
        
        print("电机使能测试完成")
        return True
        
    except Exception as e:
        print(f"电机使能测试失败: {e}")
        return False

def test_motor_angle_control(motor):
    """测试电机角度控制功能"""
    print("\n=== 测试电机角度控制功能 ===")
    
    if not motor:
        print("电机未连接，跳过角度控制测试")
        return False
    
    try:
        # 测试单个电机角度设置
        print("测试单个电机角度设置...")
        for motor_id in range(1, 6):  # 测试1-5号电机
            angle = 30.0 + motor_id * 10  # 不同电机设置不同角度
            print(f"设置电机 {motor_id} 角度为 {angle} 度...")
            command_id = motor.set_motor_angle(motor_id, angle, speed=0.5)
            print(f"  命令ID: {command_id}")
            time.sleep(0.5)
        
        # 等待运动完成
        time.sleep(3)
        
        # 测试广播角度设置
        print("\n测试广播角度设置...")
        angles = {1: 0.0, 2: 15.0, 3: 30.0, 4: 45.0, 5: 60.0}
        command_id = motor.set_motor_angles_broadcast(angles)
        print(f"  命令ID: {command_id}")
        time.sleep(3)
        
        print("电机角度控制测试完成")
        return True
        
    except Exception as e:
        print(f"电机角度控制测试失败: {e}")
        return False

def test_motor_status_query(motor):
    """测试电机状态查询功能"""
    print("\n=== 测试电机状态查询功能 ===")
    
    if not motor:
        print("电机未连接，跳过状态查询测试")
        return False
    
    try:
        # 测试单个电机状态查询
        print("测试单个电机状态查询...")
        for motor_id in range(1, 6):  # 查询1-5号电机
            print(f"\n查询电机 {motor_id} 状态...")
            
            # 同步查询
            status = motor.get_motor_status(motor_id, sync=True, timeout=1.0)
            print(f"  同步查询结果: {status}")
            
            # 异步查询
            status = motor.get_motor_status(motor_id, sync=False, timeout=1.0)
            print(f"  异步查询结果: {status}")
            
            # 查询角度
            angle = motor.get_motor_angle(motor_id, sync=True, timeout=1.0)
            print(f"  当前角度: {angle:.2f} 度")
            
            time.sleep(0.2)
        
        # 测试所有电机状态查询
        print("\n测试所有电机状态查询...")
        
        # 查询所有电机状态
        all_status = motor.get_all_motor_status(sync=True, timeout=1.0)
        print(f"  所有电机状态: {all_status}")
        
        # 查询所有电机角度
        all_angles = motor.get_all_motor_angle(sync=True, timeout=1.0)
        print(f"  所有电机角度: {all_angles}")
        
        print("电机状态查询测试完成")
        return True
        
    except Exception as e:
        print(f"电机状态查询测试失败: {e}")
        return False

def test_motor_jog_control(motor):
    """测试电机点动控制功能"""
    print("\n=== 测试电机点动控制功能 ===")
    
    if not motor:
        print("电机未连接，跳过点动控制测试")
        return False
    
    try:
        # 测试电机点动控制
        print("测试电机点动控制...")
        motor_id = 1  # 测试1号电机
        
        # 顺时针点动
        print(f"电机 {motor_id} 顺时针点动...")
        command_id = motor.jog_motor(motor_id, 1)  # 1=顺时针
        print(f"  命令ID: {command_id}")
        time.sleep(2)
        
        # 停止
        print(f"电机 {motor_id} 停止...")
        command_id = motor.jog_motor(motor_id, 0)  # 0=停止
        print(f"  命令ID: {command_id}")
        time.sleep(1)
        
        # 逆时针点动
        print(f"电机 {motor_id} 逆时针点动...")
        command_id = motor.jog_motor(motor_id, 2)  # 2=逆时针
        print(f"  命令ID: {command_id}")
        time.sleep(2)
        
        # 停止
        print(f"电机 {motor_id} 停止...")
        command_id = motor.jog_motor(motor_id, 0)  # 0=停止
        print(f"  命令ID: {command_id}")
        time.sleep(1)
        
        print("电机点动控制测试完成")
        return True
        
    except Exception as e:
        print(f"电机点动控制测试失败: {e}")
        return False

def test_emergency_stop(motor):
    """测试紧急停止功能"""
    print("\n=== 测试紧急停止功能 ===")
    
    if not motor:
        print("电机未连接，跳过紧急停止测试")
        return False
    
    try:
        # 先设置一些电机角度
        print("设置电机角度...")
        for motor_id in range(1, 6):
            motor.set_motor_angle(motor_id, 45.0, speed=0.3)
            time.sleep(0.1)
        
        time.sleep(2)
        
        # 执行紧急停止
        print("执行紧急停止...")
        command_id = motor.emergency_stop()
        print(f"  命令ID: {command_id}")
        
        # 等待紧急停止生效
        time.sleep(1)
        
        # 查询电机状态确认停止
        print("查询电机状态确认停止...")
        for motor_id in range(1, 6):
            status = motor.get_motor_status(motor_id, sync=True, timeout=0.5)
            print(f"  电机 {motor_id} 状态: {status}")
        
        print("紧急停止测试完成")
        return True
        
    except Exception as e:
        print(f"紧急停止测试失败: {e}")
        return False

def test_broadcast_control(motor):
    """测试广播控制功能"""
    print("\n=== 测试广播控制功能 ===")
    
    if not motor:
        print("电机未连接，跳过广播控制测试")
        return False
    
    try:
        # 测试广播角度设置
        print("测试广播角度设置...")
        angles = {
            1: 10.0,   # 拇指关节1
            2: 20.0,   # 拇指关节2
            3: 30.0,   # 拇指关节3
            4: 15.0,   # 食指关节1
            5: 25.0    # 食指关节2
        }
        command_id = motor.set_motor_angles_broadcast(angles)
        print(f"  广播角度设置命令ID: {command_id}")
        time.sleep(3)
        
        # 测试广播速度设置
        print("\n测试广播速度设置...")
        speeds = {1: 0.3, 2: 0.4, 3: 0.5, 4: 0.6, 5: 0.7}
        command_id = motor.set_motor_speeds_broadcast(speeds)
        print(f"  广播速度设置命令ID: {command_id}")
        time.sleep(1)
        
        # 测试广播电流设置
        print("\n测试广播电流设置...")
        currents = {1: 100, 2: 150, 3: 200, 4: 250, 5: 300}
        command_id = motor.set_motor_currents_broadcast(currents)
        print(f"  广播电流设置命令ID: {command_id}")
        time.sleep(1)
        
        print("广播控制测试完成")
        return True
        
    except Exception as e:
        print(f"广播控制测试失败: {e}")
        return False

def test_communication_monitoring(motor):
    """测试通信监控功能"""
    print("\n=== 测试通信监控功能 ===")
    
    if not motor:
        print("电机未连接，跳过通信监控测试")
        return False
    
    try:
        # 查看队列状态
        print("查看队列状态...")
        queue_status = motor.get_queue_status()
        print(f"  队列状态: {queue_status}")
        
        # 查看缓冲区状态
        print("\n查看缓冲区状态...")
        buffer_status = motor.get_buffer_status()
        print(f"  缓冲区状态: {buffer_status}")
        
        # 清空接收缓冲区
        print("\n清空接收缓冲区...")
        motor.clear_receive_buffer()
        print("  接收缓冲区已清空")
        
        # 清空响应队列
        print("\n清空响应队列...")
        motor.clear_response_queue()
        print("  响应队列已清空")
        
        # 再次查看状态
        print("\n再次查看状态...")
        queue_status = motor.get_queue_status()
        buffer_status = motor.get_buffer_status()
        print(f"  队列状态: {queue_status}")
        print(f"  缓冲区状态: {buffer_status}")
        
        print("通信监控测试完成")
        return True
        
    except Exception as e:
        print(f"通信监控测试失败: {e}")
        return False

def test_callback_functions(motor):
    """测试回调函数功能"""
    print("\n=== 测试回调函数功能 ===")
    
    if not motor:
        print("电机未连接，跳过回调函数测试")
        return False
    
    try:
        # 定义回调函数
        def status_callback(response):
            print(f"  状态回调: {response.data}")
        
        def angle_callback(response):
            print(f"  角度回调: {response.data}")
        
        # 添加回调函数
        print("添加回调函数...")
        motor.add_response_callback(motor.ResponseType.STATUS_RESPONSE, status_callback)
        motor.add_response_callback(motor.ResponseType.ANGLE_BROADCAST, angle_callback)
        
        # 触发一些操作来产生响应
        print("触发操作产生响应...")
        for motor_id in range(1, 4):
            motor.get_motor_status(motor_id, sync=False)
            time.sleep(0.1)
        
        # 等待响应
        time.sleep(2)
        
        # 移除回调函数
        print("移除回调函数...")
        motor.remove_response_callback(motor.ResponseType.STATUS_RESPONSE, status_callback)
        motor.remove_response_callback(motor.ResponseType.ANGLE_BROADCAST, angle_callback)
        
        print("回调函数测试完成")
        return True
        
    except Exception as e:
        print(f"回调函数测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始 Motor 类使用示例测试")
    print("=" * 60)
    
    # 测试电机连接
    motor = test_motor_connection()
    
    if motor:
        try:
            # 测试电机使能
            test_motor_enable(motor)
            
            # 测试电机角度控制
            test_motor_angle_control(motor)
            
            # 测试电机状态查询
            test_motor_status_query(motor)
            
            # 测试电机点动控制
            test_motor_jog_control(motor)
            
            # 测试广播控制
            test_broadcast_control(motor)
            
            # 测试通信监控
            test_communication_monitoring(motor)
            
            # 测试回调函数
            test_callback_functions(motor)
            
            # 测试紧急停止
            test_emergency_stop(motor)
            
        finally:
            # 断开连接
            print("\n=== 断开电机连接 ===")
            motor.disconnect()
            print("电机连接已断开")
    
    print("\n" + "=" * 60)
    print("Motor 类使用示例测试完成")

if __name__ == "__main__":
    main() 