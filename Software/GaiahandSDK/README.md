<!--
 * @File name: 
 * @Descripttion: 
 * @Author: tanzhiqiang
 * @Email: zhiqiangtan89@gmail.com
 * @Version: 
 * @Date: 2025-08-11 10:12:10
 * @History: 
-->
# Hand Control Module (手部控制模块)

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

一个统一的手部控制模块，支持Gaia灵巧手的控制接口。提供高级抽象接口和底层控制功能，适用于机器人研究、教育和工业应用。

## 📋 目录

- [功能特性](#功能特性)
- [支持的手部类型](#支持的手部类型)
- [快速开始](#快速开始)
- [安装](#安装)
- [基本使用](#基本使用)
- [API文档](#api文档)
- [示例代码](#示例代码)
- [架构设计](#架构设计)
- [故障排除](#故障排除)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性

### 🔧 核心功能
- **统一接口**: 提供标准化的手部控制接口，支持多种手部类型
- **多手部支持**: 支持单手、双手和混合模式
- **实时控制**: 支持实时关节角度控制和位置控制
- **手势执行**: 内置多种预设手势，支持自定义手势
- **运动学计算**: 提供正逆运动学计算功能
- **状态监控**: 实时监控电机状态和手部状态

### 🚀 高级功能
- **异步通信**: 支持异步电机状态查询，提高响应速度
- **广播控制**: 支持单点控制和广播控制模式
- **平滑运动**: 支持关节平滑过渡和轨迹规划
- **紧急停止**: 提供紧急停止功能，确保安全
- **自动检测**: 自动检测串口设备
- **错误处理**: 完善的错误处理和恢复机制

### 🛠️ 开发友好
- **类型提示**: 完整的Python类型提示支持
- **详细文档**: 提供详细的API文档和使用示例
- **日志系统**: 完善的日志记录和调试功能
- **单元测试**: 包含完整的单元测试套件
- **跨平台**: 支持Windows、Linux和macOS

## 🤖 支持的手部类型

### Gaia手部 (GaiaHand)
- 基于串口通信的灵巧手系统
- 支持15个关节（单手）或30个关节（双手）
- 提供精确的位置控制和状态监控
- 支持手势录制和回放功能

## 🚀 快速开始

### 环境要求
- Python 3.7+
- 串口驱动 (GaiaHand)

### 安装依赖
```bash
# 安装基础依赖
pip install pyserial>=3.5 numpy>=1.21.0 typing-extensions>=4.0.0

# 或者使用requirements.txt
pip install -r requirements.txt
```

### 安装模块
```bash
# 开发模式安装
pip install -e .

# 或者直接安装
pip install .
```

## 📖 基本使用

### 1. 创建手部实例

```python
from hand import create_hand, HandType, HandSide

# 创建Gaia灵巧手实例
gaia_hand = create_hand(
    hand_type=HandType.GAIA,
    hand_side=HandSide.RIGHT,
    port="COM3",
    baudrate=230400
)
```

### 2. 连接和基本控制

```python
# 连接手部
if gaia_hand.connect():
    print("手部连接成功")
    
    # 使能所有电机
    gaia_hand.enable_all_motors(True)
    
    # 设置关节角度
    from hand import FingerType, JointType
    gaia_hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, 45.0)
    
    # 执行手势
    from hand import GestureType
    gaia_hand.perform_gesture(GestureType.FIST)
    
    # 断开连接
    gaia_hand.disconnect()
```

### 3. 高级控制功能

```python
# 使用move_joints_pos进行批量控制
positions = {
    6: [1, 1, 1, 0.5]  # 手部1，食指关节1，角度0.5弧度
}
gaia_hand.move_joints_pos(positions, speed=0.8)

# 运动学计算
x, y = gaia_hand.forward_kinematics(FingerType.INDEX)
print(f"食指末端位置: ({x:.3f}, {y:.3f})")

# 逆运动学
target_x, target_y = 0.1, 0.05  # 目标位置(米)
joint_angles = gaia_hand.inverse_kinematics(FingerType.INDEX, target_x, target_y)
```

## 📚 API文档

### 核心类

#### Hand (抽象基类)
手部控制的抽象基类，定义了标准接口。

**主要方法:**
- `connect()`: 连接手部硬件
- `disconnect()`: 断开连接
- `is_connected()`: 检查连接状态
- `set_joint_angle()`: 设置关节角度
- `get_joint_angle()`: 获取关节角度
- `perform_gesture()`: 执行手势
- `emergency_stop()`: 紧急停止

#### GaiaHandAdapter
Gaia灵巧手的适配器类。

**特殊功能:**
- 串口通信管理
- 15自由度控制
- 高精度位置控制
- 实时状态监控

### 枚举类型

#### HandType
```python
class HandType(Enum):
    GAIA = "gaia"      # Gaia手部
```

#### HandSide
```python
class HandSide(Enum):
    RIGHT = "right"   # 右手
    LEFT = "left"     # 左手
    DOUBLE = "double" # 双手
```

#### FingerType
```python
class FingerType(Enum):
    THUMB = "拇指"    # 拇指
    INDEX = "食指"    # 食指
    MIDDLE = "中指"   # 中指
    RING = "无名指"   # 无名指
    LITTLE = "小指"   # 小指
```

#### JointType
```python
class JointType(Enum):
    JOINT_1 = "关节1"  # 第一关节
    JOINT_2 = "关节2"  # 第二关节
    JOINT_3 = "关节3"  # 第三关节
```

#### GestureType
```python
class GestureType(Enum):
    FIST = "握拳"           # 握拳
    OPEN = "张开"          # 张开
    POINT = "指向"         # 指向
    VICTORY = "胜利"       # 胜利手势
    OK = "OK"             # OK手势
    THUMB_UP = "点赞"      # 点赞
```

### 工具函数

#### 串口工具
```python
from hand import get_available_ports, auto_detect_gaia_ports

# 获取可用串口
ports = get_available_ports()

# 自动检测Gaia手部串口
gaia_ports = auto_detect_gaia_ports()
```

## 💡 示例代码

### 基础示例

查看 `example/` 目录中的完整示例：

- `gaia_hand_usage_example.py`: Gaia手部使用示例
- `motor_usage_example.py`: 底层电机控制示例
- `move_joints_pos.py`: 关节位置控制示例

### 快速示例

```python
# 简单的手部控制示例
from hand import create_hand, HandType, HandSide, FingerType, JointType, GestureType

def simple_hand_control():
    # 创建手部实例
    hand = create_hand(HandType.GAIA, HandSide.RIGHT, port="COM3")
    
    try:
        # 连接手部
        if hand.connect():
            print("手部连接成功")
            
            # 使能电机
            hand.enable_all_motors(True)
            
            # 执行一系列动作
            hand.perform_gesture(GestureType.OPEN)
            time.sleep(1)
            
            hand.perform_gesture(GestureType.FIST)
            time.sleep(1)
            
            hand.perform_gesture(GestureType.POINT)
            time.sleep(1)
            
            print("动作执行完成")
        else:
            print("手部连接失败")
            
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        hand.disconnect()

if __name__ == "__main__":
    simple_hand_control()
```

## 🏗️ 架构设计

### 模块结构
```
hand/
├── hand/
│   ├── __init__.py          # 模块入口
│   ├── core.py              # 核心抽象类和适配器
│   ├── gaiahand/            # Gaia手部实现
│   │   ├── gaia_hand.py     # Gaia手部适配器
│   │   ├── motor.py         # 电机控制
│   │   └── hand_mappings.py # 映射关系
│   └── utils/               # 工具函数
│       └── serial_utils.py  # 串口工具
├── example/                 # 示例代码
├── docs/                    # 文档
├── tests/                   # 测试代码
└── setup.py                 # 安装配置
```

### 设计模式

1. **工厂模式**: 使用`create_hand()`工厂函数创建手部实例
2. **适配器模式**: 通过适配器类统一不同手部类型的接口
3. **策略模式**: 支持串口通信策略
4. **观察者模式**: 状态变化通知机制

### 通信协议

#### 串口协议 (GaiaHand)
- 波特率: 230400
- 数据位: 8
- 停止位: 1
- 校验位: 无

## 🔧 故障排除

### 常见问题

#### 1. 连接失败
**症状**: 无法连接到手部硬件
**解决方案**:

- 检查串口号是否正确
- 确认硬件连接正常
- 检查驱动是否安装
- 验证波特率设置

#### 2. 通信超时
**症状**: 命令执行超时
**解决方案**:
- 检查通信线路质量
- 降低波特率
- 增加超时时间
- 检查硬件状态

#### 3. 电机不响应
**症状**: 电机不执行命令
**解决方案**:
- 检查电机使能状态
- 验证关节角度范围
- 检查电源供应
- 查看错误日志

#### 4. 位置控制异常
**症状**: 位置控制不准确
**解决方案**:
- 执行手部回零操作
- 检查编码器状态
- 验证运动学参数
- 校准关节角度

### 调试方法

1. **启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **使用串口调试工具**:
```python
from hand import get_available_ports
ports = get_available_ports()
print(f"可用串口: {ports}")
```

3. **检查硬件状态**:
```python
status = hand.get_motor_status()
print(f"电机状态: {status}")
```

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

### 开发环境设置
```bash
# 克隆仓库
git clone https://gitee.com/stellarrobot/handsdk.git
cd handsdk

# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest tests/
```

### 代码规范
- 遵循PEP 8代码风格
- 添加类型提示
- 编写单元测试
- 更新文档

### 提交规范
- 使用清晰的提交信息
- 包含测试用例
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目主页**: https://gitee.com/stellarrobot/handsdk
- **问题反馈**: https://gitee.com/stellarrobot/handsdk/issues
- **邮箱**: zhiqiangtan89@gmail.com
- **文档**: https://hand-control.readthedocs.io/

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**注意**: 使用本模块时请确保在安全环境下进行测试，并遵循相关的安全操作规程。
