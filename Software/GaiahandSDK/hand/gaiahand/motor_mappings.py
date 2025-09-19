"""
Gaia手部电机映射表模块

此模块包含Gaia手部特有的电机ID映射表。
"""

from typing import Dict, Tuple

from ..utils.hand_mappings import FingerType, JointType

# ==================== 电机ID映射表 ====================

# Gaia手部电机ID映射表 - 使用元组键 (FingerType, JointType)
GAIA_MOTOR_MAP = {
    (FingerType.THUMB, JointType.JOINT_1): 1,
    (FingerType.THUMB, JointType.JOINT_2): 2,
    (FingerType.THUMB, JointType.JOINT_3): 3,
    (FingerType.INDEX, JointType.JOINT_1): 4,
    (FingerType.INDEX, JointType.JOINT_2): 5,
    (FingerType.INDEX, JointType.JOINT_3): 6,
    (FingerType.MIDDLE, JointType.JOINT_1): 7,
    (FingerType.MIDDLE, JointType.JOINT_2): 8,
    (FingerType.MIDDLE, JointType.JOINT_3): 9,
    (FingerType.RING, JointType.JOINT_1): 10,
    (FingerType.RING, JointType.JOINT_2): 11,
    (FingerType.RING, JointType.JOINT_3): 12,
    (FingerType.LITTLE, JointType.JOINT_1): 13,
    (FingerType.LITTLE, JointType.JOINT_2): 14,
    (FingerType.LITTLE, JointType.JOINT_3): 15
}

# 电机ID到手指和关节的反向映射
GAIA_MOTOR_ID_TO_FINGER_JOINT = {
    1: (FingerType.THUMB, JointType.JOINT_1),
    2: (FingerType.THUMB, JointType.JOINT_2),
    3: (FingerType.THUMB, JointType.JOINT_3),
    4: (FingerType.INDEX, JointType.JOINT_1),
    5: (FingerType.INDEX, JointType.JOINT_2),
    6: (FingerType.INDEX, JointType.JOINT_3),
    7: (FingerType.MIDDLE, JointType.JOINT_1),
    8: (FingerType.MIDDLE, JointType.JOINT_2),
    9: (FingerType.MIDDLE, JointType.JOINT_3),
    10: (FingerType.RING, JointType.JOINT_1),
    11: (FingerType.RING, JointType.JOINT_2),
    12: (FingerType.RING, JointType.JOINT_3),
    13: (FingerType.LITTLE, JointType.JOINT_1),
    14: (FingerType.LITTLE, JointType.JOINT_2),
    15: (FingerType.LITTLE, JointType.JOINT_3)
}

# ==================== 关节正负映射表 ====================
# 定义每个手指每个关节的正负映射关系
# True表示正相关（关节角度 = 电机角度），False表示负相关（关节角度 = -电机角度）
GAIA_JOINT_SIGN_MAP = {
    (FingerType.THUMB, JointType.JOINT_1): False,   # 拇指关节1：正相关
    (FingerType.THUMB, JointType.JOINT_2): False,  # 拇指关节2：负相关
    (FingerType.THUMB, JointType.JOINT_3): True,   # 拇指关节3：正相关
    
    (FingerType.INDEX, JointType.JOINT_1): True,   # 食指关节1：正相关
    (FingerType.INDEX, JointType.JOINT_2): False,  # 食指关节2：负相关
    (FingerType.INDEX, JointType.JOINT_3): True,   # 食指关节3：正相关
    
    (FingerType.MIDDLE, JointType.JOINT_1): True,  # 中指关节1：正相关
    (FingerType.MIDDLE, JointType.JOINT_2): False, # 中指关节2：负相关
    (FingerType.MIDDLE, JointType.JOINT_3): True,  # 中指关节3：正相关
    
    (FingerType.RING, JointType.JOINT_1): True,    # 无名指关节1：正相关
    (FingerType.RING, JointType.JOINT_2): False,   # 无名指关节2：负相关
    (FingerType.RING, JointType.JOINT_3): True,    # 无名指关节3：正相关
    
    (FingerType.LITTLE, JointType.JOINT_1): True,  # 小指关节1：正相关
    (FingerType.LITTLE, JointType.JOINT_2): False, # 小指关节2：负相关
    (FingerType.LITTLE, JointType.JOINT_3): True,  # 小指关节3：正相关
}

# ==================== 工具函数 ====================

def get_motor_id(finger: FingerType, joint: JointType) -> int:
    """
    获取电机ID
    
    Args:
        finger: 手指类型
        joint: 关节类型
        
    Returns:
        int: 电机ID
        
    Raises:
        ValueError: 如果手指和关节组合无效
    """
    motor_id = GAIA_MOTOR_MAP.get((finger, joint))
    if motor_id is None:
        raise ValueError(f"无效的手指和关节组合: {finger.value}, {joint.value}")
    return motor_id


def get_finger_joint_from_motor_id(motor_id: int) -> Tuple[FingerType, JointType]:
    """
    从电机ID获取手指和关节类型
    
    Args:
        motor_id: 电机ID
        
    Returns:
        Tuple: (FingerType, JointType)
        
    Raises:
        ValueError: 如果电机ID无效
    """
    finger_joint = GAIA_MOTOR_ID_TO_FINGER_JOINT.get(motor_id)
    if finger_joint is None:
        raise ValueError(f"无效的电机ID: {motor_id}")
    return finger_joint


def get_all_motor_ids() -> list:
    """
    获取所有电机ID列表
    
    Returns:
        list: 电机ID列表
    """
    return list(GAIA_MOTOR_ID_TO_FINGER_JOINT.keys())


def get_finger_motor_ids(finger: FingerType) -> list:
    """
    获取指定手指的所有电机ID
    
    Args:
        finger: 手指类型
        
    Returns:
        list: 电机ID列表
    """
    motor_ids = []
    for (f, j), motor_id in GAIA_MOTOR_MAP.items():
        if f == finger:
            motor_ids.append(motor_id)
    return sorted(motor_ids)


def get_joint_motor_ids(joint: JointType) -> list:
    """
    获取指定关节类型的所有电机ID
    
    Args:
        joint: 关节类型
        
    Returns:
        list: 电机ID列表
    """
    motor_ids = []
    for (f, j), motor_id in GAIA_MOTOR_MAP.items():
        if j == joint:
            motor_ids.append(motor_id)
    return sorted(motor_ids)


def get_joint_sign_mapping(finger: FingerType, joint: JointType) -> bool:
    """
    获取指定手指关节的正负映射关系
    
    Args:
        finger: 手指类型
        joint: 关节类型
        
    Returns:
        bool: True表示正相关，False表示负相关
        
    Raises:
        ValueError: 如果手指和关节组合无效
    """
    sign_mapping = GAIA_JOINT_SIGN_MAP.get((finger, joint))
    if sign_mapping is None:
        raise ValueError(f"无效的手指和关节组合: {finger.value}, {joint.value}")
    return sign_mapping


def convert_joint_angle_to_motor_angle(finger: FingerType, joint: JointType, joint_angle: float) -> float:
    """
    将关节角度转换为电机角度
    
    Args:
        finger: 手指类型
        joint: 关节类型
        joint_angle: 关节角度（弧度）
        
    Returns:
        float: 电机角度（弧度）
    """
    is_positive = get_joint_sign_mapping(finger, joint)
    if is_positive:
        return joint_angle
    else:
        return -joint_angle


def convert_motor_angle_to_joint_angle(finger: FingerType, joint: JointType, motor_angle: float) -> float:
    """
    将电机角度转换为关节角度
    
    Args:
        finger: 手指类型
        joint: 关节类型
        motor_angle: 电机角度（弧度）
        
    Returns:
        float: 关节角度（弧度）
    """
    is_positive = get_joint_sign_mapping(finger, joint)
    if is_positive:
        return motor_angle
    else:
        return -motor_angle 