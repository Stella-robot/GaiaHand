'''
File name: 
Descripttion: 
Author: tanzhiqiang
Email: zhiqiangtan89@gmail.com
Version: 
Date: 2025-07-08 12:03:31
History: 
'''
"""
Gaia手部映射表模块

此模块导入通用的手部映射表，并包含Gaia手部特有的电机映射。
"""

# 导入通用的手部映射
from ..utils.hand_mappings import (
    HandType,
    HandSide,
    FingerType,
    JointType,
    GestureType,
    FINGER_ID_TO_TYPE,
    JOINT_ID_TO_TYPE,
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

# 导入Gaia特有的电机映射
from .motor_mappings import (
    GAIA_MOTOR_MAP,
    GAIA_MOTOR_ID_TO_FINGER_JOINT,
    GAIA_JOINT_SIGN_MAP,
    get_motor_id,
    get_finger_joint_from_motor_id,
    get_all_motor_ids,
    get_finger_motor_ids,
    get_joint_motor_ids,
    get_joint_sign_mapping,
    convert_joint_angle_to_motor_angle,
    convert_motor_angle_to_joint_angle
)


# Gaia手部特有的映射表已移至 motor_mappings.py 模块

# 所有工具函数已移至 utils.hand_mappings 模块 