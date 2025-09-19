'''
File name: 
Descripttion: 
Author: tanzhiqiang
Email: zhiqiangtan89@gmail.com
Version: 
Date: 2025-07-02 18:04:38
History: 
'''
#!/usr/bin/env python3
"""
手部控制抽象基类

定义了手部控制的标准接口，支持多种手部类型。
"""

import time
import math
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np

from .gaiahand.hand_mappings import (
    FINGER_ID_TO_TYPE,
    JOINT_ID_TO_TYPE,
    get_finger_type_from_id,
    get_joint_type_from_id,
    FingerType, 
    JointType, 
    GestureType,
    HandType,
    HandSide
)

logger = logging.getLogger(__name__)

class Hand(ABC):
    """
    抽象手部控制基类
    
    定义了手部控制的标准接口，包括：
    - 连接管理
    - 位置控制
    - 状态查询
    - 手势执行
    - 运动学计算
    """
    
    def __init__(self, hand_type: HandType, hand_side: Union[str, HandSide] = HandSide.RIGHT):
        """
        初始化手部控制实例
        
        Args:
            hand_type: 手部类型
            hand_side: 手部侧边 ("right", "left", "double" 或 HandSide枚举)
        """
        self.hand_type = hand_type
        
        # 统一hand_side的处理
        if isinstance(hand_side, str):
            hand_side = hand_side.lower()
            if hand_side in ["right", "r"]:
                self.hand_side = HandSide.RIGHT
            elif hand_side in ["left", "l"]:
                self.hand_side = HandSide.LEFT
            elif hand_side in ["double", "both", "d"]:
                self.hand_side = HandSide.DOUBLE
            else:
                raise ValueError(f"不支持的手部侧边: {hand_side}，支持的值: right, left, double")
        else:
            self.hand_side = hand_side
        
        self.connected = False
        self._hand_instance = None
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(message)s'
        )
    
    @property
    def hand_side_name(self) -> str:
        """获取手部侧边名称"""
        return self.hand_side.value
    
    @property
    def is_double_hand(self) -> bool:
        """是否为双手模式"""
        return self.hand_side == HandSide.DOUBLE
    
    @property
    def is_left_hand(self) -> bool:
        """是否为左手模式"""
        return self.hand_side == HandSide.LEFT
    
    @property
    def is_right_hand(self) -> bool:
        """是否为右手模式"""
        return self.hand_side == HandSide.RIGHT
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接到手部硬件
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开与手部硬件的连接"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查是否已连接
        
        Returns:
            bool: 是否已连接
        """
        pass
    
    @abstractmethod
    def get_joint_positions(self, joint_names: Optional[List[str]] = None) -> np.ndarray:
        """
        获取关节位置
        
        Args:
            joint_names: 关节名称列表，如果为None则返回所有关节
            
        Returns:
            np.ndarray: 关节位置数组
        """
        pass
    
    @abstractmethod
    def set_joint_positions(self, positions: Union[List[float], np.ndarray], 
                          joint_names: Optional[List[str]] = None,
                          finger_ids: Optional[List[int]] = None) -> bool:
        """
        设置关节位置
        
        Args:
            positions: 目标位置列表或数组
            joint_names: 关节名称列表
            finger_ids: 手指ID列表
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def control_single_finger(self, finger_id: int, finger_positions: List[float]) -> bool:
        """
        控制单个手指
        
        Args:
            finger_id: 手指ID
            finger_positions: 手指关节位置列表
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def control_finger_joint(self, finger_id: int, joint_id: int, position: float) -> bool:
        """
        控制单个关节
        
        Args:
            finger_id: 手指ID
            joint_id: 关节ID
            position: 目标位置
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def control_multiple_fingers(self, finger_positions_dict: Dict[int, List[float]]) -> bool:
        """
        控制多个手指
        
        Args:
            finger_positions_dict: 手指ID到位置列表的映射
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def hand_zero(self) -> bool:
        """
        手部回零
        
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def emergency_stop(self) -> bool:
        """
        紧急停止
        
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def get_motor_status(self, motor_id: Optional[int] = None) -> Dict:
        """
        获取电机状态
        
        Args:
            motor_id: 电机ID，如果为None则返回所有电机状态
            
        Returns:
            Dict: 电机状态信息
        """
        pass
    
    # 可选的高级功能接口
    def set_joint_angle(self, finger: FingerType, joint: JointType, angle: float, speed: float = 0.5) -> bool:
        """
        设置指定手指关节的角度（可选实现）
        
        Args:
            finger: 手指类型
            joint: 关节类型
            angle: 目标角度(弧度)
            speed: 运动速度(0-1)
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 set_joint_angle 方法")
        return False
    
    def get_joint_angle(self, finger: FingerType, joint: JointType) -> float:
        """
        获取指定手指关节的当前角度（可选实现）
        
        Args:
            finger: 手指类型
            joint: 关节类型
            
        Returns:
            float: 当前角度(弧度)
        """
        logger.warning(f"{self.hand_type.value} 未实现 get_joint_angle 方法")
        return 0.0
    
    def perform_gesture(self, gesture: GestureType, speed: float = 0.5, duration: float = 1.0) -> bool:
        """
        执行预定义手势（可选实现）
        
        Args:
            gesture: 手势类型
            speed: 运动速度(0-1)
            duration: 手势持续时间(秒)
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 perform_gesture 方法")
        return False
    
    def enable_motor(self, motor_id: int, enable: bool = True) -> bool:
        """
        设置电机使能状态（可选实现）
        
        Args:
            motor_id: 电机ID
            enable: 是否使能
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 enable_motor 方法")
        return False
    
    def enable_all_motors(self, enable: bool = True) -> bool:
        """
        设置所有电机使能状态（可选实现）
        
        Args:
            enable: 是否使能
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 enable_all_motors 方法")
        return False
    
    def enable_motors_broadcast(self, enable_states: Dict[int, bool]) -> bool:
        """
        广播设置多个电机的使能/失能状态（可选实现）
        
        Args:
            enable_states: 电机ID到使能状态的映射字典
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 enable_motors_broadcast 方法")
        return False
    
    def enable_all_motors_broadcast(self, enable: bool = True) -> bool:
        """
        广播设置所有电机的使能/失能状态（可选实现）
        
        Args:
            enable: True表示使能，False表示失能
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 enable_all_motors_broadcast 方法")
        return False
    
    def jog_joint(self, finger: FingerType, joint: JointType, direction: int) -> bool:
        """
        点动控制指定关节（可选实现）
        
        Args:
            finger: 手指类型
            joint: 关节类型
            direction: 运动方向(0=停止, 1=顺时针, 2=逆时针)
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 jog_joint 方法")
        return False
    
    def forward_kinematics(self, finger: FingerType) -> Tuple[float, float]:
        """
        计算指定手指指尖的正运动学位置（可选实现）
        
        Args:
            finger: 手指类型
            
        Returns:
            Tuple[float, float]: 指尖位置(x, y)
        """
        logger.warning(f"{self.hand_type.value} 未实现 forward_kinematics 方法")
        return 0.0, 0.0
    
    def inverse_kinematics(self, finger: FingerType, x: float, y: float) -> Dict[JointType, float]:
        """
        计算指定手指的逆运动学解（可选实现）
        
        Args:
            finger: 手指类型
            x: 目标x坐标
            y: 目标y坐标
            
        Returns:
            Dict[JointType, float]: 关节角度字典
        """
        logger.warning(f"{self.hand_type.value} 未实现 inverse_kinematics 方法")
        return {}
    
    def move_finger_to_position(self, finger: FingerType, x: float, y: float, speed: float = 0.5) -> bool:
        """
        移动指定手指到目标位置（可选实现）
        
        Args:
            finger: 手指类型
            x: 目标x坐标
            y: 目标y坐标
            speed: 运动速度(0-1)
            
        Returns:
            bool: 操作是否成功
        """
        logger.warning(f"{self.hand_type.value} 未实现 move_finger_to_position 方法")
        return False
    
    def close(self):
        """关闭连接并清理资源"""
        if hasattr(self, '_hand_instance') and self._hand_instance:
            if hasattr(self._hand_instance, 'close'):
                self._hand_instance.close()
        self.disconnect()
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.connect():
            raise RuntimeError(f"无法连接到 {self.hand_type.value}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


class GaiaHandAdapter(Hand):
    """GaiaHand适配器"""
    
    def __init__(self, hand_side: Union[str, HandSide] = HandSide.RIGHT, 
                 port: Optional[str] = None, baudrate: int = 230400,
                 left_port: Optional[str] = None, right_port: Optional[str] = None):
        super().__init__(HandType.GAIA, hand_side)
        self.baudrate = baudrate
        
        # 导入串口工具
        from .utils.serial_utils import get_default_ports, get_system_type
        
        # 获取系统默认串口配置
        default_ports = get_default_ports()
        system = get_system_type()
        
        # 串口配置 - 使用跨平台默认值
        self.left_port = left_port or default_ports['left']
        self.right_port = right_port or default_ports['right']
        
        # 根据手部侧边确定使用的串口
        if self.is_left_hand:
            self.port = port or self.left_port
        elif self.is_right_hand:
            self.port = port or self.right_port
        else:  # 双手模式
            self.port = port  # 双手模式需要外部指定主串口
        
        # 双手模式下的实例
        self._left_hand_instance = None
        self._right_hand_instance = None
        self._hand_instance = None  # 单手模式下的实例
        
        # 记录系统信息
        logger.info(f"GaiaHandAdapter 初始化 - 系统: {system.upper()}")
        logger.info(f"  手部侧边: {self.hand_side_name}")
        logger.info(f"  左手串口: {self.left_port}")
        logger.info(f"  右手串口: {self.right_port}")
        logger.info(f"  当前串口: {self.port}")

    def _get_hand_instances(self) -> List[Any]:
        """
        获取所有可用的手部实例
        
        Returns:
            手部实例列表
        """
        if self.is_double_hand:
            instances = []
            if self._left_hand_instance:
                instances.append(self._left_hand_instance)
            if self._right_hand_instance:
                instances.append(self._right_hand_instance)
            return instances
        else:
            return [self._hand_instance] if self._hand_instance else []

    def connect(self) -> bool:
        try:
            from .gaiahand.gaia_hand import GaiaHand
            
            if self.is_double_hand:
                # 双手模式：创建两个实例
                self._left_hand_instance = GaiaHand(port=self.left_port, baudrate=self.baudrate)
                self._right_hand_instance = GaiaHand(port=self.right_port, baudrate=self.baudrate)
                
                # 连接左手
                left_connected = self._left_hand_instance.connect()
                if not left_connected:
                    logger.warning(f"左手连接失败: {self.left_port}")
                
                # 连接右手
                right_connected = self._right_hand_instance.connect()
                if not right_connected:
                    logger.warning(f"右手连接失败: {self.right_port}")
                
                self.connected = left_connected or right_connected
                if self.connected:
                    logger.info(f"双手模式连接状态 - 左手: {'成功' if left_connected else '失败'}, 右手: {'成功' if right_connected else '失败'}")
                else:
                    logger.error("双手模式连接失败")
                
            else:
                # 单手模式：创建单个实例
                self._hand_instance = GaiaHand(port=self.port, baudrate=self.baudrate)
                self.connected = self._hand_instance.connect()
                if self.connected:
                    logger.info(f"成功连接到 {self.hand_type.value} ({self.hand_side_name}) - 串口: {self.port}")
                else:
                    logger.error(f"连接 {self.hand_type.value} ({self.hand_side_name}) 失败 - 串口: {self.port}")
            
            return self.connected
            
        except Exception as e:
            logger.error(f"连接 {self.hand_type.value} ({self.hand_side_name}) 失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        if self.is_double_hand:
            if self._left_hand_instance:
                self._left_hand_instance.disconnect()
            if self._right_hand_instance:
                self._right_hand_instance.disconnect()
        else:
            if self._hand_instance:
                self._hand_instance.disconnect()
        self.connected = False
    
    def is_connected(self) -> bool:
        if self.is_double_hand:
            left_connected = self._left_hand_instance is not None
            right_connected = self._right_hand_instance is not None
            return self.connected and (left_connected or right_connected)
        else:
            return self.connected and self._hand_instance is not None
        
    def init_hand(self) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        
        try:
            # GaiaHand的初始化主要是调用hand_correct_zero方法
            logger.info("开始GaiaHand初始化...")
            success = self.hand_correct_zero()
            
            if success:
                logger.info("GaiaHand初始化成功")
            else:
                logger.error("GaiaHand初始化失败")
            
            return success
            
        except Exception as e:
            logger.error(f"GaiaHand初始化异常: {e}")
            return False
    
    def emergency_stop(self) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时紧急停止所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.emergency_stop()
                    except Exception as e:
                        logger.warning(f"紧急停止失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：紧急停止单个实例
                self._hand_instance.emergency_stop()
                return True
        except Exception as e:
            logger.error(f"紧急停止失败: {e}")
            return False

    def enable_motor(self, motor_id: int, enable: bool = True) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时使能所有实例的指定电机
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.enable_motor(motor_id, enable)
                    except Exception as e:
                        logger.warning(f"设置电机使能状态失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：使能单个实例的指定电机
                return self._hand_instance.enable_motor(motor_id, enable)
        except Exception as e:
            logger.error(f"设置电机使能状态失败: {e}")
            return False
    
    def enable_all_motors(self, enable: bool = True) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时使能所有电机
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.enable_all_motors(enable)
                    except Exception as e:
                        logger.warning(f"设置所有电机使能状态失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：使能单个实例的所有电机
                return self._hand_instance.enable_all_motors(enable)
        except Exception as e:
            logger.error(f"设置所有电机使能状态失败: {e}")
            return False
    
    def enable_motors_broadcast(self, enable_states: Dict[int, bool]) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时广播设置所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.enable_motors_broadcast(enable_states)
                    except Exception as e:
                        logger.warning(f"广播设置多个电机使能状态失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：广播设置单个实例
                return self._hand_instance.enable_motors_broadcast(enable_states)
        except Exception as e:
            logger.error(f"广播设置多个电机使能状态失败: {e}")
            return False
    
    def enable_all_motors_broadcast(self, enable: bool = True) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时广播使能
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.enable_all_motors_broadcast(enable)
                    except Exception as e:
                        logger.warning(f"广播设置所有电机使能状态失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：广播设置单个实例
                return self._hand_instance.enable_all_motors_broadcast(enable)
        except Exception as e:
            logger.error(f"广播设置所有电机使能状态失败: {e}")
            return False

    def get_joint_positions(self, joint_names: Optional[List[str]] = None) -> np.ndarray:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        
        # GaiaHand使用不同的接口，需要转换
        positions = []
        
        if self.is_double_hand:
            # 双手模式：合并左右手的位置
            for instance in self._get_hand_instances():
                for finger in FingerType:
                    for joint in JointType:
                        angle = instance.get_joint_angle(finger, joint)
                        positions.append(math.degrees(angle))  # 转换为度数
        else:
            # 单手模式
            for finger in FingerType:
                for joint in JointType:
                    angle = self._hand_instance.get_joint_angle(finger, joint)
                    positions.append(math.degrees(angle))  # 转换为度数
        
        result = np.array(positions)
        if joint_names:
            # 这里需要根据joint_names重新排序
            # 简化实现，实际使用时需要根据具体的关节名称映射
            pass
        return result
    
    def move_joints_pos(self, positions: Union[List[float], Dict], speed: float = 0.5, 
                       use_broadcast: bool = False) -> bool:
        """
        移动所有关节到指定位置
        
        Args:
            positions: 关节位置数据，支持两种格式：
                      1. 列表格式：包含15个（单手）或30个（双手）位置数据
                         位置数据按以下顺序排列：
                         单手模式：拇指(3个关节) + 食指(3个关节) + 中指(3个关节) + 无名指(3个关节) + 小指(3个关节)
                         双手模式：右手(15个关节) + 左手(15个关节)
                      2. 字典格式：
                         {
                             1: {  # 右手位置命令
                                 1: [10, 20, 30, 0, 23, 30],  # 拇指
                                 2: [0, 25, 40, 0],   # 食指
                                 3: [0, 25, 40, 0],   # 中指
                                 4: [0, 25, 40, 0],   # 无名指
                                 5: [0, 15, 25, 0],   # 小指
                             },
                             2: {  # 左手位置命令
                                 1: [10, 20, 30, 0],  # 拇指
                                 2: [0, 25, 40, 0],   # 食指
                                 3: [0, 25, 40, 0],   # 中指
                                 4: [0, 25, 40, 0],   # 无名指
                                 5: [0, 15, 25, 0],   # 小指
                             }
                         }
                         其中：1=右手，2=左手；1=拇指，2=食指，3=中指，4=无名指，5=小指
            speed: 运动速度(0-1)
            use_broadcast: 是否使用广播模式，True使用set_joint_angles_broadcast，False使用set_joint_angle逐个设置
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        
        try:
            # 检查输入数据类型
            if isinstance(positions, dict):
                return self._move_joints_pos_dict(positions, speed, use_broadcast)
            elif isinstance(positions, list):
                return self._move_joints_pos_list(positions, speed, use_broadcast)
            else:
                logger.error(f"不支持的位置数据类型: {type(positions)}")
                return False
                    
        except Exception as e:
            logger.error(f"移动关节位置失败: {e}")
            return False
    
    def _move_joints_pos_dict(self, positions_dict: Dict, speed: float, use_broadcast: bool) -> bool:
        """
        使用字典格式移动关节位置
        
        Args:
            positions_dict: 字典格式的位置数据
            speed: 运动速度
            use_broadcast: 是否使用广播模式
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 验证字典格式
            if not positions_dict:
                logger.error("位置字典不能为空")
                return False
            
            # 检查手部标识
            valid_hand_ids = {1, 2}  # 1=右手，2=左手
            hand_ids = set(positions_dict.keys())
            
            # 处理指令6格式
            if 6 in positions_dict:
                return self._process_command_6(positions_dict[6], speed, use_broadcast)
            
            # 检查其他手部ID是否有效
            other_hand_ids = hand_ids - {6}
            if other_hand_ids and not other_hand_ids.issubset(valid_hand_ids):
                logger.error(f"无效的手部ID: {other_hand_ids - valid_hand_ids}，有效值: {valid_hand_ids}")
                return False
            
            # 检查手指标识
            valid_finger_ids = {1, 2, 3, 4, 5}  # 1=拇指，2=食指，3=中指，4=无名指，5=小指
            
            success = True
            
            # 处理右手 (ID=1)
            if 1 in positions_dict:
                right_hand_data = positions_dict[1]
                if not isinstance(right_hand_data, dict):
                    logger.error("右手位置数据必须是字典格式")
                    return False
                
                # 验证右手手指ID
                right_finger_ids = set(right_hand_data.keys())
                if not right_finger_ids.issubset(valid_finger_ids):
                    logger.error(f"无效的右手手指ID: {right_finger_ids - valid_finger_ids}")
                    return False
                
                # 控制右手关节
                right_success = self._control_hand_joints_dict(right_hand_data, "右手", speed, use_broadcast)
                success = success and right_success
            
            # 处理左手 (ID=2)
            if 2 in positions_dict:
                left_hand_data = positions_dict[2]
                if not isinstance(left_hand_data, dict):
                    logger.error("左手位置数据必须是字典格式")
                    return False
                
                # 验证左手手指ID
                left_finger_ids = set(left_hand_data.keys())
                if not left_finger_ids.issubset(valid_finger_ids):
                    logger.error(f"无效的左手手指ID: {left_finger_ids - valid_finger_ids}")
                    return False
                
                # 控制左手关节
                left_success = self._control_hand_joints_dict(left_hand_data, "左手", speed, use_broadcast)
                success = success and left_success
            
            return success
            
        except Exception as e:
            logger.error(f"字典格式移动关节位置失败: {e}")
            return False
    
    def _process_command_6(self, command_data: List, speed: float, use_broadcast: bool) -> bool:
        """
        处理指令6格式：6: [手部, 手指, 关节, 位置值]
        
        Args:
            command_data: 指令6的数据列表 [手部, 手指, 关节, 位置值]
            speed: 运动速度
            use_broadcast: 是否使用广播模式
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 验证指令6的数据格式
            if not isinstance(command_data, list):
                logger.error("指令6的数据必须是列表格式")
                return False
            
            if len(command_data) != 4:
                logger.error(f"指令6需要4个参数，实际提供: {len(command_data)}")
                return False
            
            # 解析参数并转换为正确的类型
            try:
                hand_id = int(command_data[0])
                finger_id = int(command_data[1])
                joint_id = int(command_data[2])
                position_value = float(command_data[3])
            except (ValueError, TypeError) as e:
                logger.error(f"指令6参数类型转换失败: {e}")
                return False
            
            # 验证手部ID (1=右手, 2=左手)
            if hand_id not in [1, 2]:
                logger.error(f"无效的手部ID: {hand_id}，有效值: 1(右手), 2(左手)")
                return False
            
            # 验证手指ID (1-5)
            if not 1 <= finger_id <= 5:
                logger.error(f"无效的手指ID: {finger_id}，有效值: 1-5")
                return False
            
            # 验证关节ID (1-3)
            if not 1 <= joint_id <= 3:
                logger.error(f"无效的关节ID: {joint_id}，有效值: 1-3")
                return False
            
            # 验证位置值
            if not isinstance(position_value, (int, float)):
                logger.error(f"位置值必须是数字，实际类型: {type(position_value)}")
                return False
            
            # 手指ID到FingerType的映射
            finger_id_to_type = {
                1: FingerType.THUMB,
                2: FingerType.INDEX,
                3: FingerType.MIDDLE,
                4: FingerType.RING,
                5: FingerType.LITTLE
            }
            
            # 关节ID到JointType的映射
            joint_id_to_type = {
                1: JointType.JOINT_1,
                2: JointType.JOINT_2,
                3: JointType.JOINT_3
            }
            
            # 获取对应的枚举类型
            finger_type = finger_id_to_type[finger_id]
            joint_type = joint_id_to_type[joint_id]
            
            # 确定使用哪个实例
            if self.is_double_hand:
                if hand_id == 1 and self._right_hand_instance:  # 右手
                    instance = self._right_hand_instance
                    hand_name = "右手"
                elif hand_id == 2 and self._left_hand_instance:  # 左手
                    instance = self._left_hand_instance
                    hand_name = "左手"
                else:
                    logger.warning(f"手部{hand_id}实例不可用")
                    return False
            else:
                if (hand_id == 1 and self.is_right_hand) or (hand_id == 2 and self.is_left_hand):
                    instance = self._hand_instance
                    hand_name = "右手" if hand_id == 1 else "左手"
                else:
                    logger.warning(f"手部{hand_id}模式未启用")
                    return False
            
            # 设置关节角度（位置值已经是弧度制）
            try:
                instance.set_joint_angle(finger_type, joint_type, position_value, speed)
                logger.info(f"指令6成功：{hand_name}手指{finger_id}关节{joint_id}设置为{position_value}弧度")
                return True
            except Exception as e:
                logger.error(f"指令6设置关节失败: {e}")
                return False
                
        except Exception as e:
            logger.error(f"处理指令6失败: {e}")
            return False
    
    def _control_hand_joints_dict(self, hand_data: Dict, hand_name: str, speed: float, use_broadcast: bool) -> bool:
        """
        控制单个手部的关节（使用字典格式）
        
        Args:
            hand_data: 手部字典数据
            hand_name: 手部名称（用于日志）
            speed: 运动速度
            use_broadcast: 是否使用广播模式
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 手指ID到FingerType的映射
            finger_id_to_type = {
                1: FingerType.THUMB,
                2: FingerType.INDEX,
                3: FingerType.MIDDLE,
                4: FingerType.RING,
                5: FingerType.LITTLE
            }
            
            # 关节索引到JointType的映射
            joint_index_to_type = {
                0: JointType.JOINT_1,
                1: JointType.JOINT_2,
                2: JointType.JOINT_3
            }
            
            success_count = 0
            total_count = 0
            
            # 确定使用哪个实例
            if self.is_double_hand:
                if hand_name == "右手" and self._right_hand_instance:
                    instance = self._right_hand_instance
                elif hand_name == "左手" and self._left_hand_instance:
                    instance = self._left_hand_instance
                else:
                    logger.warning(f"{hand_name}实例不可用")
                    return False
            else:
                if (hand_name == "右手" and self.is_right_hand) or (hand_name == "左手" and self.is_left_hand):
                    instance = self._hand_instance
                else:
                    logger.warning(f"{hand_name}模式未启用")
                    return False
            
            if use_broadcast:
                # 广播模式：收集所有关节角度
                angles_dict = {}
                
                for finger_id, finger_positions in hand_data.items():
                    if not isinstance(finger_positions, list):
                        logger.error(f"{hand_name}手指{finger_id}的位置数据必须是列表格式")
                        continue
                    
                    finger_type = finger_id_to_type.get(finger_id)
                    if finger_type is None:
                        logger.error(f"{hand_name}无效的手指ID: {finger_id}")
                        continue
                    
                    # 处理每个关节位置
                    for joint_index, position in enumerate(finger_positions):
                        if joint_index >= 3:  # 每个手指最多3个关节
                            logger.warning(f"{hand_name}手指{finger_id}的位置数据超出3个关节，忽略多余数据")
                            break
                        
                        if not isinstance(position, (int, float)):
                            logger.error(f"{hand_name}手指{finger_id}关节{joint_index+1}的位置值必须是数字")
                            continue
                        
                        joint_type = joint_index_to_type.get(joint_index)
                        if joint_type is None:
                            logger.error(f"{hand_name}无效的关节索引: {joint_index}")
                            continue
                        
                        # 将度数转换为弧度
                        angle_rad = math.radians(float(position))
                        angles_dict[(finger_type, joint_type)] = angle_rad
                        total_count += 1
                
                # 使用广播方式设置所有关节角度
                if angles_dict:
                    try:
                        instance.set_joint_angles_broadcast(angles_dict)
                        success_count = len(angles_dict)
                        logger.info(f"{hand_name}广播模式：成功设置 {success_count} 个关节位置")
                    except Exception as e:
                        logger.error(f"{hand_name}广播设置失败: {e}")
                        return False
                
            else:
                # 逐个设置关节角度
                for finger_id, finger_positions in hand_data.items():
                    if not isinstance(finger_positions, list):
                        logger.error(f"{hand_name}手指{finger_id}的位置数据必须是列表格式")
                        continue
                    
                    finger_type = finger_id_to_type.get(finger_id)
                    if finger_type is None:
                        logger.error(f"{hand_name}无效的手指ID: {finger_id}")
                        continue
                    
                    # 处理每个关节位置
                    for joint_index, position in enumerate(finger_positions):
                        if joint_index >= 3:  # 每个手指最多3个关节
                            logger.warning(f"{hand_name}手指{finger_id}的位置数据超出3个关节，忽略多余数据")
                            break
                        
                        if not isinstance(position, (int, float)):
                            logger.error(f"{hand_name}手指{finger_id}关节{joint_index+1}的位置值必须是数字")
                            continue
                        
                        joint_type = joint_index_to_type.get(joint_index)
                        if joint_type is None:
                            logger.error(f"{hand_name}无效的关节索引: {joint_index}")
                            continue
                        
                        try:
                            # 将度数转换为弧度
                            angle_rad = math.radians(float(position))
                            instance.set_joint_angle(finger_type, joint_type, angle_rad, speed)
                            time.sleep(0.002)  # 短暂延时
                            success_count += 1
                        except Exception as e:
                            logger.warning(f"{hand_name}设置关节 {finger_type.value}-{joint_type.value} 失败: {e}")
                        
                        total_count += 1
                
                logger.info(f"{hand_name}逐个设置模式：成功设置 {success_count}/{total_count} 个关节位置")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"控制{hand_name}关节失败: {e}")
            return False
    
    def _move_joints_pos_list(self, positions: List[float], speed: float, use_broadcast: bool) -> bool:
        """
        使用列表格式移动关节位置（原有实现）
        
        Args:
            positions: 关节位置列表
            speed: 运动速度
            use_broadcast: 是否使用广播模式
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 验证输入数据
            if not positions:
                logger.error("位置数据不能为空")
                return False
            
            # 检查位置数据长度
            if len(positions) not in [15, 30]:
                logger.error(f"位置数据长度错误: {len(positions)}，期望15（单手）或30（双手）")
                return False
            
            # 判断是否为双手模式
            is_double_hand_data = len(positions) == 30
            
            if self.is_double_hand:
                if not is_double_hand_data:
                    logger.error("双手模式需要30个位置数据")
                    return False
                
                # 双手模式：分别处理左右手
                # 修改顺序：前15个是右手，后15个是左手
                right_positions = positions[:15]
                left_positions = positions[15:]
                
                success = True
                
                # 处理右手
                if self._right_hand_instance:
                    right_success = self._move_single_hand_joints(
                        self._right_hand_instance, right_positions, speed, use_broadcast
                    )
                    success = success and right_success
                
                # 处理左手
                if self._left_hand_instance:
                    left_success = self._move_single_hand_joints(
                        self._left_hand_instance, left_positions, speed, use_broadcast
                    )
                    success = success and left_success
                
                return success
                
            else:
                # 单手模式
                if is_double_hand_data:
                    logger.warning("单手模式接收到30个位置数据，只使用前15个")
                    positions = positions[:15]
                
                # 使用默认实例
                return self._move_single_hand_joints(self._hand_instance, positions, speed, use_broadcast)
                    
        except Exception as e:
            logger.error(f"列表格式移动关节位置失败: {e}")
            return False
    
    def _move_single_hand_joints(self, instance: Any, positions: List[float], speed: float, use_broadcast: bool = False) -> bool:
        """
        移动单个手部的所有关节到指定位置
        
        Args:
            instance: 手部实例
            positions: 15个关节位置数据
            speed: 运动速度
            use_broadcast: 是否使用广播模式
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 验证位置数据长度
            if len(positions) != 15:
                logger.error(f"单个手部需要15个位置数据，实际提供: {len(positions)}")
                return False
            
            # 定义关节顺序：拇指(3) + 食指(3) + 中指(3) + 无名指(3) + 小指(3)
            finger_joint_order = [
                # 拇指的3个关节
                (FingerType.THUMB, JointType.JOINT_1),
                (FingerType.THUMB, JointType.JOINT_2),
                (FingerType.THUMB, JointType.JOINT_3),
                # 食指的3个关节
                (FingerType.INDEX, JointType.JOINT_1),
                (FingerType.INDEX, JointType.JOINT_2),
                (FingerType.INDEX, JointType.JOINT_3),
                # 中指的3个关节
                (FingerType.MIDDLE, JointType.JOINT_1),
                (FingerType.MIDDLE, JointType.JOINT_2),
                (FingerType.MIDDLE, JointType.JOINT_3),
                # 无名指的3个关节
                (FingerType.RING, JointType.JOINT_1),
                (FingerType.RING, JointType.JOINT_2),
                (FingerType.RING, JointType.JOINT_3),
                # 小指的3个关节
                (FingerType.LITTLE, JointType.JOINT_1),
                (FingerType.LITTLE, JointType.JOINT_2),
                (FingerType.LITTLE, JointType.JOINT_3)
            ]
            
            if use_broadcast:
                # 使用广播方式设置所有关节角度
                angles_dict = {}
                for i, (finger, joint) in enumerate(finger_joint_order):
                    if i < len(positions):
                        # 将度数转换为弧度
                        angle_rad = math.radians(positions[i])
                        angles_dict[(finger, joint)] = angle_rad
                
                instance.set_joint_angles_broadcast(angles_dict)
                logger.info(f"广播模式：成功设置 {len(angles_dict)} 个关节位置")
            else:
                # 逐个设置关节角度
                success_count = 0
                for i, (finger, joint) in enumerate(finger_joint_order):
                    if i < len(positions):
                        # 将度数转换为弧度
                        angle_rad = math.radians(positions[i])
                        try:
                            instance.set_joint_angle(finger, joint, angle_rad, speed)
                            time.sleep(0.002)
                            success_count += 1
                        except Exception as e:
                            logger.warning(f"设置关节 {finger.value}-{joint.value} 失败: {e}")
                
                logger.info(f"逐个设置模式：成功设置 {success_count}/{len(positions)} 个关节位置")
            
            return True
            
        except Exception as e:
            logger.error(f"移动单个手部关节失败: {e}")
            return False
    
    def set_joint_positions(self, positions: Union[List[float], np.ndarray], 
                          joint_names: Optional[List[str]] = None,
                          finger_ids: Optional[List[int]] = None) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            # GaiaHand使用不同的接口，需要转换
            # 这里需要根据positions和joint_names的映射来设置角度
            # 简化实现，实际使用时需要根据具体的关节映射关系
            logger.warning("GaiaHand的set_joint_positions方法需要根据具体关节映射关系实现")
            return True
        except Exception as e:
            logger.error(f"设置关节位置失败: {e}")
            return False
    
    def control_single_finger(self, finger_id: int, finger_positions: List[float]) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            # 将finger_id转换为FingerType
            finger = get_finger_type_from_id(finger_id)
            
            if self.is_double_hand:
                # 双手模式：同时控制所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        # 将finger_positions转换为关节角度
                        for joint_id, position in enumerate(finger_positions[:3]):  # 只取前3个关节
                            joint = get_joint_type_from_id(joint_id)
                            if joint:
                                angle = math.radians(position)  # 转换为弧度
                                instance.set_joint_angle(finger, joint, angle)
                    except Exception as e:
                        logger.warning(f"控制手指失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：使用单个实例
                # 将finger_positions转换为关节角度
                for joint_id, position in enumerate(finger_positions[:3]):  # 只取前3个关节
                    joint = get_joint_type_from_id(joint_id)
                    if joint:
                        angle = math.radians(position)  # 转换为弧度
                        self._hand_instance.set_joint_angle(finger, joint, angle)
                return True
        except Exception as e:
            logger.error(f"控制单个手指失败: {e}")
            return False
    
    def control_finger_joint(self, finger_id: int, joint_id: int, position: float) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            # 将finger_id转换为FingerType
            finger = get_finger_type_from_id(finger_id)
            
            # 将joint_id转换为JointType
            joint = get_joint_type_from_id(joint_id)
            
            angle = math.radians(position)  # 转换为弧度
            
            if self.is_double_hand:
                # 双手模式：同时控制所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.set_joint_angle(finger, joint, angle)
                    except Exception as e:
                        logger.warning(f"控制关节失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：使用单个实例
                self._hand_instance.set_joint_angle(finger, joint, angle)
                return True
        except Exception as e:
            logger.error(f"控制单个关节失败: {e}")
            return False
    
    def control_multiple_fingers(self, finger_positions_dict: Dict[int, List[float]]) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            for finger_id, positions in finger_positions_dict.items():
                self.control_single_finger(finger_id, positions)
            return True
        except Exception as e:
            logger.error(f"控制多个手指失败: {e}")
            return False
    
    def hand_zero(self) -> bool:
        """手部回零（简单版本，直接设置所有关节为0）"""
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时回零所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        for finger in FingerType:
                            for joint in JointType:
                                instance.set_joint_angle(finger, joint, 0.0)
                                time.sleep(0.002)  # 短暂延时
                    except Exception as e:
                        logger.warning(f"手部回零失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：回零单个实例
                for finger in FingerType:
                    for joint in JointType:
                        self._hand_instance.set_joint_angle(finger, joint, 0.0)
                        time.sleep(0.002)  # 短暂延时
                return True
        except Exception as e:
            logger.error(f"手部回零失败: {e}")
            return False
    
    def hand_correct_zero(self) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时回零所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        for finger in FingerType:
                            for joint in JointType:
                                instance.set_joint_angle(finger, joint, 0.0)
                    except Exception as e:
                        logger.warning(f"手部回零失败: {e}")
                        success = False
                return success
            else:
                # time.sleep(2)
                # 单手模式：回零单个实例
                # for finger in FingerType:
                #     for joint in JointType:
                #         self._hand_instance.set_joint_angle(finger, joint, 0.0)
                #         time.sleep(0.002)

                # Joint2 运动 ==============================================
                self._hand_instance.set_joint_angle(FingerType.THUMB, JointType.JOINT_2, 2.14159)
                time.sleep(0.5)
                self._hand_instance.jog_joint(FingerType.THUMB, JointType.JOINT_2, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.THUMB, JointType.JOINT_2, -0.72359)
                time.sleep(0.7)
                self._hand_instance.jog_joint(FingerType.THUMB, JointType.JOINT_2, 1)
                time.sleep(0.02)

                self._hand_instance.set_joint_angle(FingerType.INDEX, JointType.JOINT_2, 2.14159)
                time.sleep(0.5)
                self._hand_instance.jog_joint(FingerType.INDEX, JointType.JOINT_2, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.INDEX, JointType.JOINT_2, -0.72359)
                time.sleep(0.7)
                self._hand_instance.jog_joint(FingerType.INDEX, JointType.JOINT_2, 1)
                time.sleep(0.02)

                self._hand_instance.set_joint_angle(FingerType.MIDDLE, JointType.JOINT_2, 2.14159)
                time.sleep(0.5)
                self._hand_instance.jog_joint(FingerType.MIDDLE, JointType.JOINT_2, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.MIDDLE, JointType.JOINT_2, -0.72359)
                time.sleep(0.7)
                self._hand_instance.jog_joint(FingerType.MIDDLE, JointType.JOINT_2, 1)
                time.sleep(0.02)

                self._hand_instance.set_joint_angle(FingerType.RING, JointType.JOINT_2, 2.14159)
                time.sleep(0.5)
                self._hand_instance.jog_joint(FingerType.RING, JointType.JOINT_2, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.RING, JointType.JOINT_2, -0.72359)
                time.sleep(0.7)
                self._hand_instance.jog_joint(FingerType.RING, JointType.JOINT_2, 1)
                time.sleep(0.02)

                self._hand_instance.set_joint_angle(FingerType.LITTLE, JointType.JOINT_2, 2.14159)
                time.sleep(0.5)
                self._hand_instance.jog_joint(FingerType.LITTLE, JointType.JOINT_2, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.LITTLE, JointType.JOINT_2, -0.72359)
                time.sleep(0.7)
                self._hand_instance.jog_joint(FingerType.LITTLE, JointType.JOINT_2, 1)
                time.sleep(0.02)
                # Joint2 运动 ==============================================

                # Joint3 运动 ==============================================
                self._hand_instance.set_joint_angle(FingerType.THUMB, JointType.JOINT_3, -1.74533)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.THUMB, JointType.JOINT_3, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.INDEX, JointType.JOINT_3, -1.74533)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.INDEX, JointType.JOINT_3, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.MIDDLE, JointType.JOINT_3, -1.74533)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.MIDDLE, JointType.JOINT_3, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.RING, JointType.JOINT_3, -1.74533)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.RING, JointType.JOINT_3, 1)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.LITTLE, JointType.JOINT_3, -1.74533)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.LITTLE, JointType.JOINT_3, 1)
                time.sleep(0.02)
                # Joint3 运动 ==============================================

                # Joint1 运动 ==============================================
                # 全部手指向右
                self._hand_instance.set_joint_angle(FingerType.THUMB, JointType.JOINT_1, 2.07453)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.THUMB, JointType.JOINT_1, 2)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.THUMB, JointType.JOINT_1, -0.27453)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.THUMB, JointType.JOINT_1, 1)
                # for i in range(3):
                #     self._hand_instance.jog_joint(FingerType.THUMB, JointType.JOINT_1, 2)
                #     time.sleep(0.3)

                self._hand_instance.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, -0.97453)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.INDEX, JointType.JOINT_1, 2)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.MIDDLE, JointType.JOINT_1, -0.97453)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.MIDDLE, JointType.JOINT_1, 2)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.RING, JointType.JOINT_1, -0.97453)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.RING, JointType.JOINT_1, 2)
                time.sleep(0.02)
                self._hand_instance.set_joint_angle(FingerType.LITTLE, JointType.JOINT_1, -1.27453)
                time.sleep(1)
                self._hand_instance.jog_joint(FingerType.LITTLE, JointType.JOINT_1, 1)
                time.sleep(0.02)


                # 全部手指向左
                self._hand_instance.set_joint_angle(FingerType.RING, JointType.JOINT_1, 0.67453)
                time.sleep(1)
                for i in range(2):
                    self._hand_instance.jog_joint(FingerType.RING, JointType.JOINT_1, 2)
                    time.sleep(0.2)

                self._hand_instance.set_joint_angle(FingerType.MIDDLE, JointType.JOINT_1, 0.67453)
                time.sleep(1)
                for i in range(2):
                    self._hand_instance.jog_joint(FingerType.MIDDLE, JointType.JOINT_1, 2)
                    time.sleep(0.2)

                self._hand_instance.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, 0.67453)
                time.sleep(1)
                for i in range(2):
                    self._hand_instance.jog_joint(FingerType.INDEX, JointType.JOINT_1, 2)
                    time.sleep(0.2)
                # Joint1 运动 ==============================================

                return True
        except Exception as e:
            logger.error(f"手部回零失败: {e}")
            return False
    
    def get_motor_status(self, motor_id: Optional[int] = None, sync: bool = False, timeout: float = 1.0) -> Dict:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：返回所有电机状态
                all_status = {}
                for i, instance in enumerate(self._get_hand_instances()):
                    hand_name = "left" if i == 0 and self._left_hand_instance else "right"
                    if motor_id is None:
                        all_status[hand_name] = instance.get_all_motor_status(sync, timeout)
                    else:
                        all_status[hand_name] = instance.get_motor_status(motor_id, sync, timeout)
                return all_status
            else:
                # 单手模式：返回单个实例状态
                if motor_id is None:
                    print(f"core.py : 获取所有电机状态 (sync={sync})")
                    return self._hand_instance.get_all_motor_status(sync, timeout)
                else:
                    print(f"core.py : 获取单个电机状态 (sync={sync})")
                    status = self._hand_instance.get_motor_status(motor_id, sync, timeout)
                    # 确保返回的数值是正确的类型
                    if isinstance(status, dict):
                        # 确保角度是数值类型
                        if 'angle' in status and not isinstance(status['angle'], (int, float)):
                            try:
                                status['angle'] = float(status['angle'])
                            except (ValueError, TypeError):
                                status['angle'] = 0.0
                        
                        # 确保其他数值字段也是正确的类型
                        for key in ['temp', 'bus_voltage', 'fsm_state', 'error_code']:
                            if key in status and not isinstance(status[key], (int, float)):
                                try:
                                    status[key] = float(status[key]) if key in ['temp', 'bus_voltage'] else int(status[key])
                                except (ValueError, TypeError):
                                    status[key] = 0.0 if key in ['temp', 'bus_voltage'] else 0
                    
                    return status
        except Exception as e:
            logger.error(f"获取电机状态失败: {e}")
            return {}
    
    # 重写可选方法，因为GaiaHand支持这些功能
    def set_joint_angle(self, finger: FingerType, joint: JointType, angle: float, 
                       speed: float = 0.5) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时设置所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.set_joint_angle(finger, joint, angle, speed)
                    except Exception as e:
                        logger.warning(f"设置关节角度失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：设置单个实例
                self._hand_instance.set_joint_angle(finger, joint, angle, speed)
                return True
        except Exception as e:
            logger.error(f"设置关节角度失败: {e}")
            return False
    
    def get_joint_angle(self, finger: FingerType, joint: JointType) -> float:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        
        if self.is_double_hand:
            # 双手模式：返回第一个可用实例的角度
            for instance in self._get_hand_instances():
                try:
                    return instance.get_joint_angle(finger, joint)
                except:
                    continue
            logger.error("未找到可用的手部实例")
            return 0.0
        else:
            # 单手模式：返回单个实例角度
            return self._hand_instance.get_joint_angle(finger, joint)
    
    def perform_gesture(self, gesture: GestureType, speed: float = 0.5, duration: float = 1.0) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时执行手势
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.perform_gesture(gesture, speed, duration)
                    except Exception as e:
                        logger.warning(f"执行手势失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：执行单个手势
                self._hand_instance.perform_gesture(gesture, speed, duration)
                return True
        except Exception as e:
            logger.error(f"执行手势失败: {e}")
            return False
    
    def jog_joint(self, finger: FingerType, joint: JointType, direction: int) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时点动所有实例
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.jog_joint(finger, joint, direction)
                    except Exception as e:
                        logger.warning(f"点动控制失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：点动单个实例
                self._hand_instance.jog_joint(finger, joint, direction)
                return True
        except Exception as e:
            logger.error(f"点动控制失败: {e}")
            return False
    
    def forward_kinematics(self, finger: FingerType) -> Tuple[float, float]:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        
        if self.is_double_hand:
            # 双手模式：返回第一个可用实例的正运动学结果
            for instance in self._get_hand_instances():
                try:
                    return instance.forward_kinematics(finger)
                except:
                    continue
            logger.error("未找到可用的手部实例")
            return 0.0, 0.0
        else:
            # 单手模式：返回单个实例的正运动学结果
            return self._hand_instance.forward_kinematics(finger)
    
    def inverse_kinematics(self, finger: FingerType, x: float, y: float) -> Dict[JointType, float]:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        
        if self.is_double_hand:
            # 双手模式：返回第一个可用实例的逆运动学结果
            for instance in self._get_hand_instances():
                try:
                    return instance.inverse_kinematics(finger, x, y)
                except:
                    continue
            logger.error("未找到可用的手部实例")
            return {}
        else:
            # 单手模式：返回单个实例的逆运动学结果
            return self._hand_instance.inverse_kinematics(finger, x, y)
    
    def move_finger_to_position(self, finger: FingerType, x: float, y: float, 
                              speed: float = 0.5) -> bool:
        if not self.is_connected():
            raise RuntimeError("未连接到手部硬件")
        try:
            if self.is_double_hand:
                # 双手模式：同时移动到指定位置
                success = True
                for instance in self._get_hand_instances():
                    try:
                        instance.move_finger_to_position(finger, x, y, speed)
                    except Exception as e:
                        logger.warning(f"移动手指到目标位置失败: {e}")
                        success = False
                return success
            else:
                # 单手模式：移动到指定位置
                self._hand_instance.move_finger_to_position(finger, x, y, speed)
                return True
        except Exception as e:
            logger.error(f"移动手指到目标位置失败: {e}")
            return False


def create_hand(hand_type: Union[str, HandType], hand_side: Union[str, HandSide] = HandSide.RIGHT, **kwargs) -> Hand:
    """
    工厂函数：创建手部控制实例
    
    Args:
        hand_type: 手部类型 ("gaia" 或 HandType枚举)
        hand_side: 手部侧边 ("right", "left", "double" 或 HandSide枚举)
        **kwargs: 其他参数，如port, baudrate等
        
    Returns:
        Hand: 手部控制实例
    """
    # 转换hand_type为HandType枚举
    if isinstance(hand_type, str):
        hand_type = hand_type.lower()
        if hand_type in ["gaia", "gaiahand"]:
            hand_type = HandType.GAIA
        else:
            raise ValueError(f"不支持的手部类型: {hand_type}，目前只支持 GaiaHand")
    
    if hand_type == HandType.GAIA:
        # 提取串口参数
        port = kwargs.get('port', None)  # 不再设置默认值，让GaiaHandAdapter自己处理
        baudrate = kwargs.get('baudrate', 230400)
        left_port = kwargs.get('left_port', None)
        right_port = kwargs.get('right_port', None)
        
        # 记录创建信息
        from .utils.serial_utils import get_system_type
        system = get_system_type()
        logger.info(f"创建 GaiaHand 实例 - 系统: {system.upper()}")
        logger.info(f"  手部侧边: {hand_side}")
        logger.info(f"  指定串口: {port}")
        logger.info(f"  左手串口: {left_port}")
        logger.info(f"  右手串口: {right_port}")
        logger.info(f"  波特率: {baudrate}")
        
        return GaiaHandAdapter(hand_side, port=port, baudrate=baudrate, 
                             left_port=left_port, right_port=right_port)
    else:
        raise ValueError(f"不支持的手部类型: {hand_type}，目前只支持 GaiaHand")


# 示例使用代码
if __name__ == "__main__":
    import math
    
    # 使用统一的接口
    print("=== 统一接口测试 ===")
    
    # 测试GaiaHand的不同侧边
    print(f"\n--- 测试 GaiaHand 不同侧边 ---")
    
    # 测试右手
    try:
        # 使用上下文管理器测试右手
        with create_hand("gaia", "right", port='COM4') as hand:
            print(f"手部类型: {hand.hand_type.value}")
            print(f"手部侧边: {hand.hand_side_name}")
            print(f"是否为右手: {hand.is_right_hand}")
            
            if hand.is_connected():
                print("GaiaHand右手连接成功")
                
                # 使能所有电机
                hand.enable_all_motors(True)
                
                # 测试广播使能方法
                print("测试广播使能方法...")
                
                # 测试enable_all_motors_broadcast
                success = hand.enable_all_motors_broadcast(True)
                print(f"广播使能所有电机: {'成功' if success else '失败'}")
                
                # 测试enable_motors_broadcast
                enable_states = {1: True, 2: False, 3: True, 4: False, 5: True}
                success = hand.enable_motors_broadcast(enable_states)
                print(f"广播设置特定电机使能状态: {'成功' if success else '失败'}")
                
                # 执行手势
                hand.perform_gesture(GestureType.OPEN_HAND)
                time.sleep(2)
                
                # 设置关节角度
                hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, math.pi/4)
                
    except Exception as e:
        print(f"GaiaHand右手测试失败: {e}")
    
    # 测试左手
    try:
        with create_hand("gaia", "left", port='COM5') as hand:
            print(f"手部类型: {hand.hand_type.value}")
            print(f"手部侧边: {hand.hand_side_name}")
            print(f"是否为左手: {hand.is_left_hand}")
            
            if hand.is_connected():
                print("GaiaHand左手连接成功")
                
                # 使能所有电机
                hand.enable_all_motors(True)
                
                # 控制左手食指的第一个关节
                hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, math.pi/6, hand_side=HandSide.LEFT)
                
                # 获取左手食指第一个关节的角度
                angle = hand.get_joint_angle(FingerType.INDEX, JointType.JOINT_1, hand_side=HandSide.LEFT)
                print(f"左手食指第一个关节角度: {math.degrees(angle):.2f}度")
                
    except Exception as e:
        print(f"GaiaHand左手测试失败: {e}")
    
    # 测试双手模式
    try:
        with create_hand("gaia", "double", left_port='COM5', right_port='COM4') as hand:
            print(f"手部类型: {hand.hand_type.value}")
            print(f"手部侧边: {hand.hand_side_name}")
            print(f"是否为双手: {hand.is_double_hand}")
            
            if hand.is_connected():
                print("GaiaHand双手连接成功")
                
                # 使能所有电机
                hand.enable_all_motors(True)
                
                # 同时控制左右手
                print("同时控制左右手...")
                
                # 右手食指第一个关节
                hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, math.pi/4, hand_side=HandSide.RIGHT)
                
                # 左手拇指第一个关节
                hand.set_joint_angle(FingerType.THUMB, JointType.JOINT_1, math.pi/6, hand_side=HandSide.LEFT)
                
                # 同时执行手势（双手同时张开）
                hand.perform_gesture(GestureType.OPEN_HAND)
                time.sleep(2)
                
                # 同时回零
                hand.hand_zero()
                
                # 获取电机状态
                status = hand.get_motor_status()
                print(f"电机状态: {status}")
                
    except Exception as e:
        print(f"GaiaHand双手测试失败: {e}")
    
    # 测试高级功能
    print(f"\n--- 测试高级功能 ---")
    try:
        with create_hand("gaia", "right", port='COM4') as hand:
            if hand.is_connected():
                print("测试高级功能...")
                
                # 点动控制
                hand.jog_joint(FingerType.INDEX, JointType.JOINT_1, 1)  # 顺时针
                time.sleep(1)
                hand.jog_joint(FingerType.INDEX, JointType.JOINT_1, 0)  # 停止
                
                # 正运动学
                x, y = hand.forward_kinematics(FingerType.INDEX)
                print(f"食指指尖位置: ({x:.2f}, {y:.2f})")
                
                # 逆运动学
                target_x, target_y = 50.0, 30.0
                angles = hand.inverse_kinematics(FingerType.INDEX, target_x, target_y)
                print(f"到达位置({target_x}, {target_y})的关节角度: {angles}")
                
                # 移动到指定位置
                hand.move_finger_to_position(FingerType.INDEX, target_x, target_y)
                
    except Exception as e:
        print(f"高级功能测试失败: {e}")
    
    print("=== 测试完成 ===")
