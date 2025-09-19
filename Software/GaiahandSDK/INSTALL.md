<!--
 * @File name: 
 * @Descripttion: 
 * @Author: tanzhiqiang
 * @Email: zhiqiangtan89@gmail.com
 * @Version: 
 * @Date: 2025-07-02 17:39:24
 * @History: 
-->
# 手部控制模块安装指南

## 安装方式

### 1. 从源码安装（推荐）

```bash
# 克隆仓库
git clone https://gitee.com/stellarrobot/handsdk.git
cd hand

# 安装依赖
pip install -r requirements.txt

# 安装模块
pip install -e .
```

### 2. 直接安装

```bash
# 安装到系统Python环境
pip install .

# 或者安装到用户环境
pip install --user .
```

### 3. 开发模式安装

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest
```

## 依赖要求

- Python >= 3.7
- pyserial >= 3.5
- numpy >= 1.21.0
- typing-extensions >= 4.0.0

## 使用示例

```python
from hand import create_hand, HandType, HandSide
from hand.gaiahand.hand_mappings import FingerType, JointType, GestureType
import math

# 创建Gaia手部实例
hand = create_hand(HandType.GAIA, HandSide.RIGHT, port='COM4')

# 连接设备
if hand.connect():
    print("连接成功")
    
    # 设置关节角度
    hand.set_joint_angle(FingerType.INDEX, JointType.MCP, math.pi/4)
    
    # 执行手势
    hand.perform_gesture(GestureType.OPEN_HAND)
    
    # 断开连接
    hand.disconnect()
```

## 故障排除

### 串口权限问题（Linux）

如果遇到串口权限问题，请运行：

```bash
# 添加用户到dialout组
sudo usermod -a -G dialout $USER

# 重新登录或重启系统
```

### 依赖安装失败

如果依赖安装失败，请尝试：

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。 