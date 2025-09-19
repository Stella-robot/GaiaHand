"""
手部工具模块

此模块包含手部控制相关的通用工具和映射表。
"""

from .hand_mappings import (
    HandType,
    HandSide,
    FingerType,
    JointType,
    GestureType,
    URDF_JOINT_TO_FINGER_JOINT_RIGHT,
    URDF_JOINT_TO_FINGER_JOINT_LEFT,
    URDF_JOINT_TO_FINGER_JOINT,
    FINGER_JOINT_TO_URDF_JOINT_RIGHT,
    FINGER_JOINT_TO_URDF_JOINT_LEFT,
    FINGER_JOINT_TO_URDF_JOINT,
    FINGER_NAME_TO_URDF_JOINT_RIGHT,
    FINGER_NAME_TO_URDF_JOINT_LEFT,
    FINGER_NAME_TO_URDF_JOINT,
    get_urdf_joint_mapping,
    get_finger_name_mapping,
    get_finger_joint_from_urdf_joint,
    get_urdf_joint_name,
    get_finger_type_from_id,
    get_joint_type_from_id
)

__all__ = [
    'HandType',
    'HandSide',
    'FingerType',
    'JointType',
    'GestureType',
    'URDF_JOINT_TO_FINGER_JOINT_RIGHT',
    'URDF_JOINT_TO_FINGER_JOINT_LEFT',
    'URDF_JOINT_TO_FINGER_JOINT',
    'FINGER_JOINT_TO_URDF_JOINT_RIGHT',
    'FINGER_JOINT_TO_URDF_JOINT_LEFT',
    'FINGER_JOINT_TO_URDF_JOINT',
    'FINGER_NAME_TO_URDF_JOINT_RIGHT',
    'FINGER_NAME_TO_URDF_JOINT_LEFT',
    'FINGER_NAME_TO_URDF_JOINT',
    'get_urdf_joint_mapping',
    'get_finger_name_mapping',
    'get_finger_joint_from_urdf_joint',
    'get_urdf_joint_name',
    'get_finger_type_from_id',
    'get_joint_type_from_id'
] 