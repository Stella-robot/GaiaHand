"""
通用关节映射表模块

此模块包含所有手部类型共用的枚举和映射表，统一管理以避免代码重复。
"""

from enum import Enum
from typing import Dict, Tuple, Any

class HandType(Enum):
    """手部类型枚举"""
    GAIA = "GaiaHand"


class HandSide(Enum):
    """手部侧边枚举"""
    RIGHT = "right"    # 右手
    LEFT = "left"      # 左手
    DOUBLE = "double"  # 双手


class FingerType(Enum):
    """手指类型枚举"""
    THUMB = "拇指"
    INDEX = "食指"
    MIDDLE = "中指"
    RING = "无名指"
    LITTLE = "小指"


class JointType(Enum):
    """关节类型枚举"""
    JOINT_1 = "掌指关节"      # 掌指关节 (Metacarpophalangeal joint)
    JOINT_2 = "近端指间关节"   # 近端指间关节 (Proximal interphalangeal joint)
    JOINT_3 = "远端指间关节"   # 远端指间关节 (Distal interphalangeal joint)


class GestureType(Enum):
    """手势类型枚举"""
    OPEN_HAND = "张开手"
    CLOSED_FIST = "握拳"
    POINT = "指点"
    THUMBS_UP = "点赞"


# ==================== URDF关节名称映射表 ====================

# URDF关节名称到手指和关节的映射（右手）
URDF_JOINT_TO_FINGER_JOINT_RIGHT = {
    'right_thumb_joint_1': (FingerType.THUMB, JointType.JOINT_1),
    'right_thumb_joint_2': (FingerType.THUMB, JointType.JOINT_2),
    'right_thumb_joint_3': (FingerType.THUMB, JointType.JOINT_3),
    'right_index_joint_1': (FingerType.INDEX, JointType.JOINT_1),
    'right_index_joint_2': (FingerType.INDEX, JointType.JOINT_2),
    'right_index_joint_3': (FingerType.INDEX, JointType.JOINT_3),
    'right_middle_joint_1': (FingerType.MIDDLE, JointType.JOINT_1),
    'right_middle_joint_2': (FingerType.MIDDLE, JointType.JOINT_2),
    'right_middle_joint_3': (FingerType.MIDDLE, JointType.JOINT_3),
    'right_ring_joint_1': (FingerType.RING, JointType.JOINT_1),
    'right_ring_joint_2': (FingerType.RING, JointType.JOINT_2),
    'right_ring_joint_3': (FingerType.RING, JointType.JOINT_3),
    'right_little_joint_1': (FingerType.LITTLE, JointType.JOINT_1),
    'right_little_joint_2': (FingerType.LITTLE, JointType.JOINT_2),
    'right_little_joint_3': (FingerType.LITTLE, JointType.JOINT_3)
}

# URDF关节名称到手指和关节的映射（左手）
URDF_JOINT_TO_FINGER_JOINT_LEFT = {
    'left_thumb_joint_1': (FingerType.THUMB, JointType.JOINT_1),
    'left_thumb_joint_2': (FingerType.THUMB, JointType.JOINT_2),
    'left_thumb_joint_3': (FingerType.THUMB, JointType.JOINT_3),
    'left_index_joint_1': (FingerType.INDEX, JointType.JOINT_1),
    'left_index_joint_2': (FingerType.INDEX, JointType.JOINT_2),
    'left_index_joint_3': (FingerType.INDEX, JointType.JOINT_3),
    'left_middle_joint_1': (FingerType.MIDDLE, JointType.JOINT_1),
    'left_middle_joint_2': (FingerType.MIDDLE, JointType.JOINT_2),
    'left_middle_joint_3': (FingerType.MIDDLE, JointType.JOINT_3),
    'left_ring_joint_1': (FingerType.RING, JointType.JOINT_1),
    'left_ring_joint_2': (FingerType.RING, JointType.JOINT_2),
    'left_ring_joint_3': (FingerType.RING, JointType.JOINT_3),
    'left_little_joint_1': (FingerType.LITTLE, JointType.JOINT_1),
    'left_little_joint_2': (FingerType.LITTLE, JointType.JOINT_2),
    'left_little_joint_3': (FingerType.LITTLE, JointType.JOINT_3)
}

# 兼容性映射（默认使用右手）
URDF_JOINT_TO_FINGER_JOINT = URDF_JOINT_TO_FINGER_JOINT_RIGHT

# 手指和关节到URDF关节名称的映射（右手）
FINGER_JOINT_TO_URDF_JOINT_RIGHT = {
    (FingerType.THUMB, JointType.JOINT_1): 'right_thumb_joint_1',
    (FingerType.THUMB, JointType.JOINT_2): 'right_thumb_joint_2',
    (FingerType.THUMB, JointType.JOINT_3): 'right_thumb_joint_3',
    (FingerType.INDEX, JointType.JOINT_1): 'right_index_joint_1',
    (FingerType.INDEX, JointType.JOINT_2): 'right_index_joint_2',
    (FingerType.INDEX, JointType.JOINT_3): 'right_index_joint_3',
    (FingerType.MIDDLE, JointType.JOINT_1): 'right_middle_joint_1',
    (FingerType.MIDDLE, JointType.JOINT_2): 'right_middle_joint_2',
    (FingerType.MIDDLE, JointType.JOINT_3): 'right_middle_joint_3',
    (FingerType.RING, JointType.JOINT_1): 'right_ring_joint_1',
    (FingerType.RING, JointType.JOINT_2): 'right_ring_joint_2',
    (FingerType.RING, JointType.JOINT_3): 'right_ring_joint_3',
    (FingerType.LITTLE, JointType.JOINT_1): 'right_little_joint_1',
    (FingerType.LITTLE, JointType.JOINT_2): 'right_little_joint_2',
    (FingerType.LITTLE, JointType.JOINT_3): 'right_little_joint_3'
}

# 手指和关节到URDF关节名称的映射（左手）
FINGER_JOINT_TO_URDF_JOINT_LEFT = {
    (FingerType.THUMB, JointType.JOINT_1): 'left_thumb_joint_1',
    (FingerType.THUMB, JointType.JOINT_2): 'left_thumb_joint_2',
    (FingerType.THUMB, JointType.JOINT_3): 'left_thumb_joint_3',
    (FingerType.INDEX, JointType.JOINT_1): 'left_index_joint_1',
    (FingerType.INDEX, JointType.JOINT_2): 'left_index_joint_2',
    (FingerType.INDEX, JointType.JOINT_3): 'left_index_joint_3',
    (FingerType.MIDDLE, JointType.JOINT_1): 'left_middle_joint_1',
    (FingerType.MIDDLE, JointType.JOINT_2): 'left_middle_joint_2',
    (FingerType.MIDDLE, JointType.JOINT_3): 'left_middle_joint_3',
    (FingerType.RING, JointType.JOINT_1): 'left_ring_joint_1',
    (FingerType.RING, JointType.JOINT_2): 'left_ring_joint_2',
    (FingerType.RING, JointType.JOINT_3): 'left_ring_joint_3',
    (FingerType.LITTLE, JointType.JOINT_1): 'left_little_joint_1',
    (FingerType.LITTLE, JointType.JOINT_2): 'left_little_joint_2',
    (FingerType.LITTLE, JointType.JOINT_3): 'left_little_joint_3'
}

# 兼容性映射（默认使用右手）
FINGER_JOINT_TO_URDF_JOINT = FINGER_JOINT_TO_URDF_JOINT_RIGHT

# ==================== 手势快照映射表 ====================

# 手指名称到URDF关节名称的映射（右手，用于手势快照）
FINGER_NAME_TO_URDF_JOINT_RIGHT = {
    '拇指': {
        '掌指关节': 'right_thumb_joint_1',
        '近端指间关节': 'right_thumb_joint_2',
        '远端指间关节': 'right_thumb_joint_3'
    },
    '食指': {
        '掌指关节': 'right_index_joint_1',
        '近端指间关节': 'right_index_joint_2',
        '远端指间关节': 'right_index_joint_3'
    },
    '中指': {
        '掌指关节': 'right_middle_joint_1',
        '近端指间关节': 'right_middle_joint_2',
        '远端指间关节': 'right_middle_joint_3'
    },
    '无名指': {
        '掌指关节': 'right_ring_joint_1',
        '近端指间关节': 'right_ring_joint_2',
        '远端指间关节': 'right_ring_joint_3'
    },
    '小指': {
        '掌指关节': 'right_little_joint_1',
        '近端指间关节': 'right_little_joint_2',
        '远端指间关节': 'right_little_joint_3'
    }
}

# 手指名称到URDF关节名称的映射（左手，用于手势快照）
FINGER_NAME_TO_URDF_JOINT_LEFT = {
    '拇指': {
        '掌指关节': 'left_thumb_joint_1',
        '近端指间关节': 'left_thumb_joint_2',
        '远端指间关节': 'left_thumb_joint_3'
    },
    '食指': {
        '掌指关节': 'left_index_joint_1',
        '近端指间关节': 'left_index_joint_2',
        '远端指间关节': 'left_index_joint_3'
    },
    '中指': {
        '掌指关节': 'left_middle_joint_1',
        '近端指间关节': 'left_middle_joint_2',
        '远端指间关节': 'left_middle_joint_3'
    },
    '无名指': {
        '掌指关节': 'left_ring_joint_1',
        '近端指间关节': 'left_ring_joint_2',
        '远端指间关节': 'left_ring_joint_3'
    },
    '小指': {
        '掌指关节': 'left_little_joint_1',
        '近端指间关节': 'left_little_joint_2',
        '远端指间关节': 'left_little_joint_3'
    }
}

# 兼容性映射（默认使用右手）
FINGER_NAME_TO_URDF_JOINT = FINGER_NAME_TO_URDF_JOINT_RIGHT

# ==================== ID到类型映射表 ====================

# 手指ID到手指类型的映射
FINGER_ID_TO_TYPE = {
    0: FingerType.THUMB,
    1: FingerType.INDEX,
    2: FingerType.MIDDLE,
    3: FingerType.RING,
    4: FingerType.LITTLE
}

# 手指类型到手指ID的映射
FINGER_TYPE_TO_ID = {
    FingerType.THUMB: 0,
    FingerType.INDEX: 1,
    FingerType.MIDDLE: 2,
    FingerType.RING: 3,
    FingerType.LITTLE: 4
}

# 关节ID到关节类型的映射
JOINT_ID_TO_TYPE = {
    0: JointType.JOINT_1,   # 掌指关节
    1: JointType.JOINT_2,   # 近端指间关节
    2: JointType.JOINT_3    # 远端指间关节
}

# 关节类型到关节ID的映射
JOINT_TYPE_TO_ID = {
    JointType.JOINT_1: 0,   # 掌指关节
    JointType.JOINT_2: 1,   # 近端指间关节
    JointType.JOINT_3: 2    # 远端指间关节
}

# ==================== 工具函数 ====================

def get_urdf_joint_mapping(hand_side: str = "right") -> Dict[str, Tuple[FingerType, JointType]]:
    """
    获取URDF关节映射表
    
    Args:
        hand_side: 手部侧边，"right" 或 "left"
        
    Returns:
        Dict: URDF关节名称到手指和关节的映射
    """
    if hand_side.lower() == "left":
        return URDF_JOINT_TO_FINGER_JOINT_LEFT
    else:
        return URDF_JOINT_TO_FINGER_JOINT_RIGHT


def get_finger_name_mapping(hand_side: str = "right") -> Dict[str, Dict[str, str]]:
    """
    获取手指名称映射表
    
    Args:
        hand_side: 手部侧边，"right" 或 "left"
        
    Returns:
        Dict: 手指名称到URDF关节名称的映射
    """
    if hand_side.lower() == "left":
        return FINGER_NAME_TO_URDF_JOINT_LEFT
    else:
        return FINGER_NAME_TO_URDF_JOINT_RIGHT


def get_finger_joint_from_urdf_joint(urdf_joint_name: str) -> Tuple[FingerType, JointType]:
    """
    从URDF关节名称获取手指和关节类型
    
    Args:
        urdf_joint_name: URDF关节名称
        
    Returns:
        Tuple: (FingerType, JointType)
        
    Raises:
        ValueError: 如果关节名称无效
    """
    # 尝试右手映射
    if urdf_joint_name in URDF_JOINT_TO_FINGER_JOINT_RIGHT:
        return URDF_JOINT_TO_FINGER_JOINT_RIGHT[urdf_joint_name]
    
    # 尝试左手映射
    if urdf_joint_name in URDF_JOINT_TO_FINGER_JOINT_LEFT:
        return URDF_JOINT_TO_FINGER_JOINT_LEFT[urdf_joint_name]
    
    raise ValueError(f"无效的URDF关节名称: {urdf_joint_name}")


def get_urdf_joint_name(finger: FingerType, joint: JointType, hand_side: str = "right") -> str:
    """
    获取URDF关节名称
    
    Args:
        finger: 手指类型
        joint: 关节类型
        hand_side: 手部侧边，"right" 或 "left"
        
    Returns:
        str: URDF关节名称
    """
    if hand_side.lower() == "left":
        mapping = FINGER_JOINT_TO_URDF_JOINT_LEFT
    else:
        mapping = FINGER_JOINT_TO_URDF_JOINT_RIGHT
    
    return mapping.get((finger, joint), f"unknown_{finger.value}_{joint.value}")


def get_finger_type_from_id(finger_id: int) -> FingerType:
    """
    从手指ID获取手指类型
    
    Args:
        finger_id: 手指ID (0-4)
        
    Returns:
        FingerType: 手指类型
        
    Raises:
        ValueError: 如果手指ID无效
    """
    if finger_id not in FINGER_ID_TO_TYPE:
        raise ValueError(f"无效的手指ID: {finger_id}，有效范围: 0-4")
    
    return FINGER_ID_TO_TYPE[finger_id]


def get_joint_type_from_id(joint_id: int) -> JointType:
    """
    从关节ID获取关节类型
    
    Args:
        joint_id: 关节ID (0-2)
        
    Returns:
        JointType: 关节类型
        
    Raises:
        ValueError: 如果关节ID无效
    """
    if joint_id not in JOINT_ID_TO_TYPE:
        raise ValueError(f"无效的关节ID: {joint_id}，有效范围: 0-2")
    
    return JOINT_ID_TO_TYPE[joint_id]


def get_finger_index(finger: FingerType) -> int:
    """
    获取手指索引
    
    Args:
        finger: 手指类型
        
    Returns:
        int: 手指索引 (0-4)
        
    Raises:
        ValueError: 如果手指类型无效
    """
    if finger not in FINGER_TYPE_TO_ID:
        raise ValueError(f"无效的手指类型: {finger}")
    
    return FINGER_TYPE_TO_ID[finger]


def get_finger_type(finger_id: int) -> FingerType:
    """
    获取手指类型
    
    Args:
        finger_id: 手指ID (0-4)
        
    Returns:
        FingerType: 手指类型
        
    Raises:
        ValueError: 如果手指ID无效
    """
    if finger_id not in FINGER_ID_TO_TYPE:
        raise ValueError(f"无效的手指ID: {finger_id}，有效范围: 0-4")
    
    return FINGER_ID_TO_TYPE[finger_id]


def get_joint_index(joint: JointType) -> int:
    """
    获取关节索引
    
    Args:
        joint: 关节类型
        
    Returns:
        int: 关节索引 (0-2)
        
    Raises:
        ValueError: 如果关节类型无效
    """
    if joint not in JOINT_TYPE_TO_ID:
        raise ValueError(f"无效的关节类型: {joint}")
    
    return JOINT_TYPE_TO_ID[joint]
