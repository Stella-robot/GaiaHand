# GaiaHand Motor类接口说明文档

## 概述

`Motor`类是GaiaHand电机控制的核心类，基于串口通信协议提供对电机的基本控制接口。该类支持异步命令执行、配置管理、状态监控等功能。

## 类初始化

### 构造函数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `hand_side` | str | "right" | 手部侧边，"right" 或 "left" |
| `port` | str | None | 串口配置参数 |

**示例：**
```python
# 创建右手电机控制实例
motor = Motor(hand_side="right", port="COM4")

# 创建左手电机控制实例
motor = Motor(hand_side="left")
```

## 连接管理接口

### 连接控制

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `connect()` | 连接到电机控制系统 | 无 | bool | 返回连接是否成功 |
| `disconnect()` | 断开与电机控制系统的连接 | 无 | None | 停止所有通信线程 |
| `is_connected()` | 检查是否已连接 | 无 | bool | 检查连接状态和心跳 |

**示例：**
```python
# 连接设备
if motor.connect():
    print("连接成功")
else:
    print("连接失败")

# 检查连接状态
if motor.is_connected():
    print("设备已连接")
```

## 手指角度控制接口

### 角度设置与获取

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `set_finger_angles(finger_id, angles, enable, callback)` | 设置手指角度 | `finger_id`: int (0-4)<br>`angles`: List[float] (3个关节角度)<br>`enable`: int (默认1)<br>`callback`: callable (可选) | str (命令ID) | 异步设置指定手指的3个关节角度 |
| `get_finger_angles(finger_id, callback)` | 获取手指角度 | `finger_id`: int (0-4)<br>`callback`: callable (可选) | str (命令ID) | 异步获取指定手指的当前角度 |
| `get_finger_angles_with_bias(finger_id)` | 获取考虑零点偏置的手指角度 | `finger_id`: int (0-4) | List[float] | 同步获取考虑零点偏置的角度值 |

**参数说明：**
- `finger_id`: 手指ID，0-4分别对应拇指、食指、中指、无名指、小指
- `angles`: 角度列表，包含3个关节的角度值 [joint_1, joint_2, joint_3]
- `enable`: 使能状态，1=使能，2=急停，3=紧绳，4=卷绳恢复
- `callback`: 回调函数，格式为 `callback(success, result)`

**示例：**
```python
# 设置食指角度
def angle_callback(success, result):
    if success:
        print(f"角度设置成功: {result}")
    else:
        print(f"角度设置失败: {result}")

motor.set_finger_angles(
    finger_id=1, 
    angles=[30.0, 45.0, 60.0], 
    enable=1, 
    callback=angle_callback
)

# 获取考虑零点偏置的角度
angles = motor.get_finger_angles_with_bias(finger_id=1)
print(f"食指角度: {angles}")
```

## 关节位置管理接口

### 零点偏置管理

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `initialize_zero_bias_positions()` | 初始化关节零点偏置位置 | 无 | bool | 从硬件读取所有关节的零点偏置配置 |
| `get_zero_bias_positions()` | 获取当前零点偏置位置 | 无 | np.ndarray | 返回15个关节的零点偏置数组 |
| `set_zero_bias_positions(zero_bias_positions)` | 设置零点偏置位置 | `zero_bias_positions`: np.ndarray | None | 设置15个关节的零点偏置 |
| `get_joint_positions_with_bias()` | 获取考虑零点偏置的关节位置 | 无 | np.ndarray | 返回15个关节的实际位置（考虑零点偏置） |

**示例：**
```python
# 初始化零点偏置
if motor.initialize_zero_bias_positions():
    print("零点偏置初始化成功")

# 获取所有关节的实际位置
positions = motor.get_joint_positions_with_bias()
print(f"关节位置: {positions}")

# 获取零点偏置
zero_bias = motor.get_zero_bias_positions()
print(f"零点偏置: {zero_bias}")
```

## 点动控制接口

### 点动操作

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `jog_control(dev_id, enable, m0_dir, m1_dir, m2_dir, callback)` | 点动控制 | `dev_id`: int<br>`enable`: bool<br>`m0_dir`: int (默认0)<br>`m1_dir`: int (默认0)<br>`m2_dir`: int (默认0)<br>`callback`: callable (可选) | str (命令ID) | 控制指定设备的点动操作 |

**参数说明：**
- `dev_id`: 设备ID
- `enable`: 是否启用点动
- `m0_dir`, `m1_dir`, `m2_dir`: 三个电机的方向控制

**示例：**
```python
# 启用点动控制
motor.jog_control(
    dev_id=1, 
    enable=True, 
    m0_dir=1, 
    m1_dir=0, 
    m2_dir=-1
)
```

## 配置管理接口

### 配置读写

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `config_read(board_id, cmd, timeout, callback)` | 读取配置 | `board_id`: int<br>`cmd`: int<br>`timeout`: float (默认3.0)<br>`callback`: callable (可选) | str (命令ID) | 异步读取指定配置项 |
| `config_write(board_id, cmd, value, callback)` | 写入配置 | `board_id`: int<br>`cmd`: int<br>`value`: float<br>`callback`: callable (可选) | str (命令ID) | 异步写入指定配置项 |

**参数说明：**
- `board_id`: 板卡ID
- `cmd`: 配置命令类型（参考CONFIG_CMD枚举）
- `value`: 配置值
- `timeout`: 读取超时时间（秒）

**示例：**
```python
# 读取配置
def config_callback(success, result):
    if success:
        print(f"配置值: {result}")
    else:
        print(f"读取失败: {result}")

motor.config_read(
    board_id=0x01, 
    cmd=CONFIG_CMD.CONF_FIN_ZERO_MCP.value, 
    timeout=2.0, 
    callback=config_callback
)

# 写入配置
motor.config_write(
    board_id=0x01, 
    cmd=CONFIG_CMD.CONF_FIN_ZERO_MCP.value, 
    value=1.57, 
    callback=lambda success, result: print(f"写入{'成功' if success else '失败'}")
)
```

## 安全控制接口

### 急停与状态监控

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `emergency_stop(callback)` | 急停操作 | `callback`: callable (可选) | str (命令ID) | 对所有手指执行急停 |
| `get_finger_status(finger_id, callback)` | 获取手指状态 | `finger_id`: int (可选)<br>`callback`: callable (可选) | str (命令ID) | 获取手指状态和错误码 |

**示例：**
```python
# 急停
motor.emergency_stop(callback=lambda success, result: print("急停完成"))

# 获取所有手指状态
motor.get_finger_status(callback=lambda success, result: print(f"状态: {result}"))

# 获取指定手指状态
motor.get_finger_status(finger_id=1, callback=lambda success, result: print(f"食指状态: {result}"))
```

## 绳索控制接口

### 绳索操作

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `rope_tight(finger_id, callback)` | 紧绳操作 | `finger_id`: int (可选)<br>`callback`: callable (可选) | str (命令ID) | 对指定手指或所有手指执行紧绳 |
| `rope_recv(finger_id, callback)` | 卷绳恢复操作 | `finger_id`: int (可选)<br>`callback`: callable (可选) | str (命令ID) | 对指定手指或所有手指执行卷绳恢复 |

**示例：**
```python
# 对所有手指紧绳
motor.rope_tight(callback=lambda success, result: print("紧绳完成"))

# 对指定手指卷绳恢复
motor.rope_recv(finger_id=1, callback=lambda success, result: print("食指卷绳恢复完成"))
```

## 响应管理接口

### 响应处理

| 方法名 | 功能描述 | 参数 | 返回值 | 说明 |
|--------|----------|------|--------|------|
| `get_response(timeout)` | 获取响应 | `timeout`: float (默认1.0) | Response 或 None | 从响应队列获取响应对象 |
| `clear_response_queue()` | 清空响应队列 | 无 | None | 清空所有待处理的响应 |
| `get_queue_status()` | 获取队列状态 | 无 | Dict[str, int] | 返回命令队列和响应队列的大小 |

**示例：**
```python
# 获取响应
response = motor.get_response(timeout=2.0)
if response:
    print(f"响应类型: {response.type}")
    print(f"响应数据: {response.data}")

# 检查队列状态
status = motor.get_queue_status()
print(f"命令队列: {status['command_queue_size']}")
print(f"响应队列: {status['response_queue_size']}")

# 清空响应队列
motor.clear_response_queue()
```

## 配置命令枚举

### CONFIG_CMD 枚举值

| 枚举值 | 数值 | 说明 |
|--------|------|------|
| `CONF_FIN_ZERO_MCP` | 32 | 手指MCP关节零点 |
| `CONF_FIN_ZERO_PIP` | 33 | 手指PIP关节零点 |
| `CONF_FIN_ZERO_DIP` | 34 | 手指DIP关节零点 |
| `CONF_ROPE_K0` | 9 | 绳索参数K0 |
| `CONF_ROPE_K1` | 10 | 绳索参数K1 |
| `CONF_ROPE_K2` | 11 | 绳索参数K2 |
| `CONF_ROPE_0_KP` | 13 | 绳索0比例系数 |
| `CONF_ROPE_0_KI` | 14 | 绳索0积分系数 |
| `CONF_ROPE_0_KD` | 15 | 绳索0微分系数 |
| `CONF_CURRENT_LIMIT_M0` | 38 | M0电机电流限制 |
| `CONF_CURRENT_LIMIT_M12` | 39 | M1/M2电机电流限制 |
| `CONF_SPEED_LIMIT_M0` | 40 | M0电机速度限制 |
| `CONF_SPEED_LIMIT_M12` | 41 | M1/M2电机速度限制 |

## 手指状态枚举

### FingerState 枚举值

| 枚举值 | 数值 | 说明 |
|--------|------|------|
| `FSM_INITIAL` | 0x00 | 初始状态 |
| `FSM_ZERO_SET` | 0x01 | 零点设置状态 |
| `FSM_ROPE_INIT` | 0x02 | 绳索初始化状态 |
| `FSM_READY` | 0x03 | 就绪状态 |
| `FSM_RUN` | 0x04 | 运行状态 |
| `FSM_MODE_JOG` | 0x05 | 点动模式状态 |
| `FSM_FAULT` | 0x06 | 故障状态 |
| `FSM_ROPE_RECV` | 0x07 | 绳索恢复状态 |

## 使用示例

### 完整使用流程

```python
from src.hand.hand.gaiahand.motor import Motor, CONFIG_CMD

# 1. 创建电机控制实例
motor = Motor(hand_side="right", port="COM4")

# 2. 连接设备
if not motor.connect():
    print("连接失败")
    exit(1)

# 3. 初始化零点偏置
if motor.initialize_zero_bias_positions():
    print("零点偏置初始化成功")

# 4. 设置手指角度
def angle_callback(success, result):
    if success:
        print(f"角度设置成功: {result}")
    else:
        print(f"角度设置失败: {result}")

motor.set_finger_angles(
    finger_id=1,  # 食指
    angles=[30.0, 45.0, 60.0],  # MCP, PIP, DIP角度
    enable=1,  # 使能
    callback=angle_callback
)

# 5. 获取手指状态
def status_callback(success, result):
    if success:
        print(f"手指状态: {result}")
    else:
        print(f"状态获取失败: {result}")

motor.get_finger_status(callback=status_callback)

# 6. 获取实际角度（考虑零点偏置）
angles = motor.get_finger_angles_with_bias(finger_id=1)
print(f"食指实际角度: {angles}")

# 7. 急停
motor.emergency_stop(callback=lambda success, result: print("急停完成"))

# 8. 断开连接
motor.disconnect()
```

## 注意事项

1. **异步操作**: 大部分控制方法都是异步的，需要通过回调函数或响应队列获取结果
2. **连接状态**: 使用前必须确保设备已连接
3. **零点偏置**: 建议在连接后立即初始化零点偏置
4. **错误处理**: 所有操作都应该包含适当的错误处理
5. **线程安全**: 该类使用线程锁确保线程安全
6. **串口ID映射**: 左右手的串口ID不同，系统会自动处理
7. **超时设置**: 配置读取操作有超时机制，可根据网络状况调整 