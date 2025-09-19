'''
File name: 
Descripttion: 
Author: tanzhiqiang
Email: zhiqiangtan89@gmail.com
Version: 
Date: 2025-07-04 14:44:11
History: 
'''
#!/usr/bin/env python3
"""
Gaia 灵巧手控制模块

提供对Gaia灵巧手的控制接口，包括电机控制、手势执行等功能。
"""

import time
import math
from typing import Dict, Tuple, Optional, List
from .motor import Motor
from .hand_mappings import (
    GAIA_MOTOR_MAP, 
    get_motor_id, 
    get_finger_joint_from_motor_id,
    FINGER_ID_TO_TYPE,
    JOINT_ID_TO_TYPE,
    FingerType, 
    JointType, 
    GestureType,
    convert_joint_angle_to_motor_angle,
    convert_motor_angle_to_joint_angle
)

class GaiaHand(Motor):
    """Gaia灵巧手控制类"""
    
    def __init__(self, port: str = 'COM4', baudrate: int = 230400):
        """
        初始化Gaia灵巧手控制器
        
        Args:
            port: 串口名称
            baudrate: 波特率
        """
        super().__init__(port, baudrate)
        
        # 使用统一的映射表
        self.motor_map = GAIA_MOTOR_MAP
        
        # 手指长度参数(mm)
        self.finger_lengths = {
            FingerType.THUMB: {
                JointType.JOINT_1: 30,
                JointType.JOINT_2: 25,
                JointType.JOINT_3: 20
            },
            FingerType.INDEX: {
                JointType.JOINT_1: 35,
                JointType.JOINT_2: 30,
                JointType.JOINT_3: 25
            },
            FingerType.MIDDLE: {
                JointType.JOINT_1: 40,
                JointType.JOINT_2: 35,
                JointType.JOINT_3: 30
            },
            FingerType.RING: {
                JointType.JOINT_1: 35,
                JointType.JOINT_2: 30,
                JointType.JOINT_3: 25
            },
            FingerType.LITTLE: {
                JointType.JOINT_1: 30,
                JointType.JOINT_2: 25,
                JointType.JOINT_3: 20
            }
        }
    
    def get_motor_id(self, finger: FingerType, joint: JointType) -> int:
        """
        获取指定手指关节对应的电机ID
        
        Args:
            finger: 手指类型
            joint: 关节类型
            
        Returns:
            int: 电机ID
        """
        return get_motor_id(finger, joint)
    
    def set_joint_angle(self, finger: FingerType, joint: JointType, angle: float, speed: float = 0.85):
        """
        设置指定手指关节的角度
        
        Args:
            finger: 手指类型
            joint: 关节类型
            angle: 目标角度(弧度)
            speed: 运动速度(0-1)
            
        Note:
            目前电机系统不返回响应数据，此方法只发送命令
        """
        motor_id = self.get_motor_id(finger, joint)
        if motor_id is None:
            raise ValueError(f"无效的手指关节组合: {finger.value}{joint.value}")
        
        # 使用灵活的正负映射关系
        motor_angle = convert_joint_angle_to_motor_angle(finger, joint, angle)

        # 调用父类的电机角度设置方法
        self.set_motor_angle(motor_id, motor_angle, speed)
    
    def get_joint_angle(self, finger: FingerType, joint: JointType) -> float:
        """
        获取指定手指关节的当前角度
        
        Args:
            finger: 手指类型
            joint: 关节类型
            
        Returns:
            float: 当前角度(弧度)
            
        Note:
            目前无法从电机获取实际角度，返回默认值0
            保留此接口以便将来实现实际的角度获取功能
        """
        motor_id = self.get_motor_id(finger, joint)
        if motor_id is None:
            raise ValueError(f"无效的手指关节组合: {finger.value}{joint.value}")
        
        # 获取电机角度
        motor_angle = self.get_motor_angle(motor_id)
        
        # 使用灵活的正负映射关系
        joint_angle = convert_motor_angle_to_joint_angle(finger, joint, motor_angle)
        
        return joint_angle
    
    def get_motor_angle(self, motor_id: int, sync: bool = False, timeout: float = 1.0) -> float:
        """
        获取指定电机的当前角度（向后兼容方法）
        
        Args:
            motor_id: 电机ID
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            float: 当前角度(弧度)
        """
        # 调用父类的电机角度获取方法
        return super().get_motor_angle(motor_id, sync, timeout)
    
    def get_motor_status(self, motor_id: int, sync: bool = False, timeout: float = 1.0) -> Dict:
        """
        获取指定电机的状态（向后兼容方法）
        
        Args:
            motor_id: 电机ID
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            Dict: 电机状态信息
        """
        # 调用父类的电机状态获取方法
        return super().get_motor_status(motor_id, sync, timeout)
    
    def get_all_motor_status(self, sync: bool = False, timeout: float = 2.0) -> Dict[int, bool]:
        """获取所有电机的状态（向后兼容方法）
        
        Args:
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            Dict[int, bool]: 电机ID到状态的映射，True表示在线，False表示离线
        """
        # 调用父类的所有电机状态获取方法
        return super().get_all_motor_status(sync, timeout)
    
    def set_finger_angles(self, finger: FingerType, angles: Dict[JointType, float], speed: float = 0.5):
        """
        设置指定手指所有关节的角度
        
        Args:
            finger: 手指类型
            angles: 关节角度字典
            speed: 运动速度(0-1)
        """
        for joint, angle in angles.items():
            self.set_joint_angle(finger, joint, angle, speed)
    
    def get_current_angles(self, finger: FingerType) -> Dict[JointType, float]:
        """
        获取指定手指所有关节的当前角度
        
        Args:
            finger: 手指类型
            
        Returns:
            Dict[JointType, float]: 关节角度字典
        """
        angles = {}
        for joint in JointType:
            angles[joint] = self.get_joint_angle(finger, joint)
        return angles
    
    def jog_joint(self, finger: FingerType, joint: JointType, direction: int):
        """
        点动控制指定关节
        
        Args:
            finger: 手指类型
            joint: 关节类型
            direction: 运动方向(0=停止, 1=顺时针, 2=逆时针)
            
        Note:
            目前电机系统不返回响应数据，此方法只发送命令
        """
        motor_id = self.get_motor_id(finger, joint)
        if motor_id is None:
            raise ValueError(f"无效的手指关节组合: {finger.value}{joint.value}")
        
        # 调用父类的电机点动方法
        self.jog_motor(motor_id, direction)
    
    def set_joint_angles_broadcast(self, angles: Dict[Tuple[FingerType, JointType], float]):
        """
        广播设置多个关节的角度
        
        Args:
            angles: 手指关节到角度的映射字典，角度单位为弧度
        """
        # 转换为电机ID到角度的映射
        motor_angles = {}
        for (finger, joint), angle in angles.items():
            motor_id = self.get_motor_id(finger, joint)
            if motor_id is not None:
                # 使用灵活的正负映射关系
                motor_angle = convert_joint_angle_to_motor_angle(finger, joint, angle)
                
                # 转换为度数
                motor_angles[motor_id] = math.degrees(motor_angle)
        
        # 调用父类的广播方法
        self.set_motor_angles_broadcast(motor_angles)
    
    def set_joint_speeds_broadcast(self, speeds: Dict[Tuple[FingerType, JointType], float]):
        """
        广播设置多个关节的速度
        
        Args:
            speeds: 手指关节到速度的映射字典，速度为百分比(0-100)
        """
        # 转换为电机ID到速度的映射
        motor_speeds = {}
        for (finger, joint), speed in speeds.items():
            motor_id = self.get_motor_id(finger, joint)
            if motor_id is not None:
                motor_speeds[motor_id] = speed
        
        # 调用父类的广播方法
        self.set_motor_speeds_broadcast(motor_speeds)
    
    def set_joint_currents_broadcast(self, currents: Dict[Tuple[FingerType, JointType], int]):
        """
        广播设置多个关节的电流
        
        Args:
            currents: 手指关节到电流的映射字典，电流单位为mA
        """
        # 转换为电机ID到电流的映射
        motor_currents = {}
        for (finger, joint), current in currents.items():
            motor_id = self.get_motor_id(finger, joint)
            if motor_id is not None:
                motor_currents[motor_id] = current
        
        # 调用父类的广播方法
        self.set_motor_currents_broadcast(motor_currents)
    
    def perform_gesture(self, gesture: GestureType, speed: float = 0.5, duration: float = 1.0):
        """
        执行预定义手势
        
        Args:
            gesture: 手势类型
            speed: 运动速度(0-1)
            duration: 手势持续时间(秒)
        """
        # if gesture not in self.gestures:
        #     raise ValueError(f"不支持的手势: {gesture.value}")
        
        # # 获取手势对应的角度配置
        # angles = self.gestures[gesture]
        
        # # 设置所有关节角度
        # for (finger, joint), angle in angles.items():
        #     self.set_joint_angle(finger, joint, angle, speed)
        
        # # 等待指定时间
        time.sleep(duration)
    
    def interpolate_to_position(self, target_angles: Dict[Tuple[FingerType, JointType], float], 
                              steps: int = 50, delay: float = 0.01):
        """
        平滑插值到目标位置
        
        Args:
            target_angles: 目标角度字典
            steps: 插值步数
            delay: 每步延迟时间(秒)
        """
        # 获取当前位置
        current_angles = {}
        for (finger, joint) in target_angles.keys():
            current_angles[(finger, joint)] = self.get_joint_angle(finger, joint)
        
        # 执行插值
        for step in range(steps):
            t = step / (steps - 1)
            for (finger, joint), target_angle in target_angles.items():
                current_angle = current_angles[(finger, joint)]
                angle = current_angle + (target_angle - current_angle) * t
                self.set_joint_angle(finger, joint, angle)
            time.sleep(delay)
    
    def forward_kinematics(self, finger: FingerType) -> Tuple[float, float]:
        """
        计算指定手指指尖的正运动学位置
        
        Args:
            finger: 手指类型
            
        Returns:
            Tuple[float, float]: 指尖位置(x, y)
        """
        # 获取当前角度
        angles = self.get_current_angles(finger)
        
        # 获取手指长度
        lengths = self.finger_lengths[finger]
        
        # 计算各关节位置
        x = 0
        y = 0
        angle_sum = 0
        
        for joint in [JointType.JOINT_1, JointType.JOINT_2, JointType.JOINT_3]:
            angle_sum += angles[joint]
            x += lengths[joint] * math.cos(angle_sum)
            y += lengths[joint] * math.sin(angle_sum)
        
        return x, y
    
    def inverse_kinematics(self, finger: FingerType, x: float, y: float) -> Dict[JointType, float]:
        """
        计算指定手指的逆运动学解
        
        Args:
            finger: 手指类型
            x: 目标x坐标
            y: 目标y坐标
            
        Returns:
            Dict[JointType, float]: 关节角度字典
        """
        # 获取手指长度
        lengths = self.finger_lengths[finger]
        
        # 计算目标距离
        target_dist = math.sqrt(x*x + y*y)
        
        # 检查是否可达
        max_dist = sum(lengths.values())
        if target_dist > max_dist:
            raise ValueError("目标位置超出可达范围")
        
        # 使用几何方法求解
        angles = {}
        
        # MCP关节角度
        angles[JointType.JOINT_1] = math.atan2(y, x)
        
        # PIP和DIP关节角度
        # 使用余弦定理求解
        a = lengths[JointType.JOINT_2]
        b = lengths[JointType.JOINT_3]
        c = target_dist - lengths[JointType.JOINT_1]
        
        cos_angle = (a*a + b*b - c*c) / (2*a*b)
        cos_angle = max(min(cos_angle, 1), -1)  # 限制在[-1, 1]范围内
        
        angles[JointType.JOINT_2] = math.acos(cos_angle)
        angles[JointType.JOINT_3] = angles[JointType.JOINT_2]
        
        return angles
    
    def move_finger_to_position(self, finger: FingerType, x: float, y: float, speed: float = 0.5):
        """
        移动指定手指到目标位置
        
        Args:
            finger: 手指类型
            x: 目标x坐标
            y: 目标y坐标
            speed: 运动速度(0-1)
        """
        # 计算逆运动学解
        angles = self.inverse_kinematics(finger, x, y)
        
        # 设置关节角度
        self.set_finger_angles(finger, angles, speed)
