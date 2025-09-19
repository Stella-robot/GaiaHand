#!/usr/bin/env python3
"""
手部控制模块

支持Gaia灵巧手的统一控制接口。
"""

# 导入主要的类和函数
from .core import Hand, create_hand, GaiaHandAdapter

# 导入枚举类型
from .gaiahand.hand_mappings import (
    HandType,
    HandSide,
    FingerType,
    JointType,
    GestureType
)

# 导入工具函数
from .utils.serial_utils import (
    get_available_ports,
    get_system_type,
    quick_detect_ports,
    auto_detect_gaia_ports
)

# 版本信息
__version__ = "1.0.0"
__author__ = "Gaia Hand Team"
__email__ = "support@gaiahand.com"

# 导出主要的公共接口
__all__ = [
    # 主要类
    "Hand",
    "create_hand",
    "GaiaHandAdapter",
    
    # 枚举类型
    "HandType",
    "HandSide", 
    "FingerType",
    "JointType",
    "GestureType",
    
    # 工具函数
    "get_available_ports",
    "get_system_type",
    "quick_detect_ports",
    "auto_detect_gaia_ports",
] 