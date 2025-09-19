# Gaia Hand 插补功能使用指南

本目录包含了 Gaia Hand 的插补运动功能演示案例，展示了如何实现复杂的轨迹规划和运动控制。

## 文件说明

### 核心文件
- `gh_interpolation.py` - 插补功能核心模块（位于 `src/hand/hand/gaiahand/`）
- `gh_kinematic.py` - 运动学正逆解模块（位于 `src/hand/hand/gaiahand/`）

### 演示案例
- `gaiahand_interpolation_demo.py` - 完整硬件演示（需要实际硬件）
- `gaiahand_interpolation_simulation.py` - 模拟演示（无需硬件）
- `interpolation_example.py` - 基础插补示例（位于 `src/hand/hand/gaiahand/`）

## 功能特性

### 1. 直线插补
- 计算从起始点到目标点的直线路径
- 支持速度规划和时间控制
- 自动关节角度计算

### 2. 圆弧插补
- 支持任意圆心和半径的圆弧轨迹
- 可指定起始和结束角度
- 适用于圆形运动任务

### 3. 样条插补
- 通过多个路径点生成平滑轨迹
- 支持复杂的多段路径规划
- 自动处理路径点之间的过渡

### 4. 速度规划插补
- 包含加速、匀速、减速三个阶段
- 支持梯形和三角形速度曲线
- 精确的速度和时间控制

### 5. 轨迹验证和平滑
- 自动验证关节角度范围限制
- 检查关节角速度限制
- 轨迹平滑处理功能

## 快速开始

### 1. 模拟演示（推荐先运行）
```bash
cd src/hand/example
python gaiahand_interpolation_simulation.py
```

这个演示不需要实际硬件，会生成3D可视化图表展示插补效果。

### 2. 硬件演示（需要实际硬件）
```bash
cd src/hand/example
python gaiahand_interpolation_demo.py
```

**注意：** 运行硬件演示前请确保：
- Gaia Hand 已正确连接
- 串口设备驱动已安装
- 手部处于安全状态

### 3. 基础示例
```bash
cd src/hand/hand/gaiahand
python gh_interpolation.py
```

## 使用示例

### 直线插补
```python
from src.hand.hand.gaiahand.gh_interpolation import gh_linear_interpolation

# 定义起始和目标位置
start_pos = [20, -10, 40]
end_pos = [30, 10, 50]

# 生成轨迹
joint_traj, time_traj, pos_traj = gh_linear_interpolation(
    start_pos, end_pos, num_points=30, max_velocity=10.0
)
```

### 圆弧插补
```python
from src.hand.hand.gaiahand.gh_interpolation import gh_circular_interpolation

# 定义圆弧参数
center = [25, 0, 45]
radius = 15
start_angle = -np.pi/4
end_angle = np.pi/4

# 生成轨迹
joint_traj, time_traj, pos_traj = gh_circular_interpolation(
    center, radius, start_angle, end_angle, num_points=40, max_velocity=10.0
)
```

### 样条插补
```python
from src.hand.hand.gaiahand.gh_interpolation import gh_spline_interpolation

# 定义路径点
waypoints = [
    [20, -10, 40],
    [30, 0, 45],
    [40, 10, 50],
    [35, 15, 45],
    [25, 5, 40]
]

# 生成轨迹
joint_traj, time_traj, pos_traj = gh_spline_interpolation(
    waypoints, num_points_per_segment=20, max_velocity=10.0
)
```

### 轨迹验证
```python
from src.hand.hand.gaiahand.gh_interpolation import validate_trajectory

# 验证轨迹
is_valid, issues = validate_trajectory(joint_traj, max_joint_velocity=2.0, time_trajectory=time_traj)
if is_valid:
    print("轨迹验证通过")
else:
    print("轨迹验证失败:")
    for issue in issues:
        print(f"  - {issue}")
```

## 参数说明

### 通用参数
- `num_points`: 插补点数量，影响轨迹精度
- `max_velocity`: 最大速度 (mm/s)，影响运动时间
- `acceleration`: 加速度 (mm/s²)，仅用于速度规划插补

### 关节限制
- `theta1`: 无特殊限制
- `theta2`: 范围 [-30°, 180°]
- `theta3`: 必须 ≥ 0°

### 速度限制
- 建议关节角速度不超过 2.0 rad/s
- 末端执行器速度建议不超过 20 mm/s

## 注意事项

### 1. 硬件安全
- 运行硬件演示前确保手部周围无障碍物
- 建议在低速模式下测试
- 随时准备紧急停止

### 2. 轨迹规划
- 确保目标位置在手部工作空间内
- 避免奇异点附近的轨迹
- 考虑关节角度和速度限制

### 3. 错误处理
- 插补函数会处理逆解失败的情况
- 验证轨迹的合理性
- 检查日志输出中的警告信息

## 故障排除

### 常见问题

1. **导入错误**
   ```
   ImportError: attempted relative import with no known parent package
   ```
   **解决方案：** 确保在正确的目录下运行，或使用绝对导入

2. **逆解失败**
   ```
   ValueError: cos(β) 超出 [-1, 1]，目标点不可达
   ```
   **解决方案：** 检查目标位置是否在手部工作空间内

3. **轨迹验证失败**
   ```
   第 X 个点: theta2 (XX.XX°) 超出范围 [-30°, 180°]
   ```
   **解决方案：** 调整起始或目标位置，避免超出关节限制

4. **硬件连接失败**
   ```
   手部连接失败
   ```
   **解决方案：** 检查串口设备连接和驱动安装

## 扩展功能

### 自定义插补算法
可以在 `gh_interpolation.py` 中添加新的插补函数：

```python
def custom_interpolation(start_pos, end_pos, **kwargs):
    """自定义插补函数"""
    # 实现自定义插补逻辑
    pass
```

### 轨迹优化
- 添加碰撞检测
- 实现能量最优轨迹
- 支持多指协调运动

### 实时控制
- 集成传感器反馈
- 实现自适应轨迹调整
- 支持在线轨迹修改

## 技术支持

如有问题，请检查：
1. 日志输出信息
2. 硬件连接状态
3. 参数设置合理性
4. 工作空间限制

更多技术文档请参考项目根目录的 `docs/` 文件夹。 