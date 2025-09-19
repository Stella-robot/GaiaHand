## 状态查询

### 发送的数据

55 AA 00 14 A0 00 00 00 08 01 00 00 00 00 00 00 43 E6 00 00
55 AA 00 14 A0 00 00 00 08 02 00 00 00 00 00 00 C1 3E 00 00

其中

- 55 AA 00 14是帧头

- A0 00 00 00是can_id，
- 08 01 00 00 00 00 00 00
  - 其中08是设备ID
  - 01，代表读取数据包1，读取运行状态与版本信息CONFIG_RUN_STATUS_R；如果是02，则是读取数据包2，CONFIG_INFO_02_R。

### 返回的数据

55 AA 00 14 00 08 01 00 00 00 70 00 00 00 FA 05 01 A0 00 00
55 AA 00 14 00 08 02 00 00 00 00 00 00 00 00 00 FD F8 00 00

- 1~4位：55 AA 00 14是帧头

- 5~8位：00 08 01 00或00 08 02 00

  - 其中08是设备ID

  - 01则是返回的是数据包1，对于9~16位：00 00 70 00 00 00 FA 05，具体解析如下

    - data[0]：运行状态fsm

      - mcReady     = 0,    ///< 准备状态,该状态电机空闲，等待控制命令

        mcInit      = 1,    ///< 初始化,该状态进行启动前的变量初始化

        mcCharge    = 2,    ///< 预充电,电机启动前给自举电容充电，一般用于高压驱动，低压驱动一般不需要

        mcTailWind  = 3,    ///< 顺逆风检测,该状态下电机进行顺逆风检测 

        mcPosiCheck = 4,    ///< 初始位置检测

        mcAlign     = 5,    ///< 预定位

        mcStart     = 6,    ///< 启动，用于配置启动代码

        mcRun       = 7,    ///< 运行，

        mcStop      = 8,    ///< 停止

        mcFault     = 9,    ///< 故障状态

        mcBrake     = 10,   ///< 刹车

    - data[1]：故障码err_code

      - FaultNoSource = 0,  ///< 无故障

        FaultHardOVCurrent = 1,  ///< 硬件过流

        FaultSoftOVCurrent = 2,  ///< 软件过流

        FaultHardOverVoltage = 3,  ///< 硬件过压

        FaultSoftOverVoltage = 4,  ///< 软件过压

        FaultHardUnderVoltage = 5,  ///< 硬件欠压

        FaultSoftUnderVoltage = 6,  ///< 软件欠压

        FaultPhaseLost = 7,  ///< 缺相

        FaultStall = 8,  ///< 堵转

        FaultSoftOTErr = 9,  ///< 软件过温

        FaultHardOTErr = 9,  ///< 硬件过温

        FaultUartLost = 10, ///< 通信丢失

        FaultPOST = 11, ///< FCT自检故障

    - data[2]：软件版本soft_ver，如103，解释为v1.0.3

    - data[3]：RSVD0，保留

    - data[4]，data[5]：手指角度，Q7，Intel小端示例：angle_fb= (data[5] << 8 | data[4]) * 0.0078125(1/128);。单位度

    - data[6]，data[7]：RSVD1，保留

  - 02则是返回的是数据包2，对于9~16位：00 00 00 00 00 00 00 00，具体解析如下

    - data[0]，data[1]：D_cur。D轴电流，Q15，0~32767表示电流0~5.625A，Intel小端示例：Dcur= (data[1] << 8 | data[0]);
    - data[2]，data[3]：Q_cur。Q轴电流，Q15，0~32767表示电流0~5.625A
    - data[4]，data[5]：Vbus。母线电压，Q7，单位V
    - data[6]，data[7]：angle_fb。末端角度，Q7，Intel小端示例：angle_fb= (data[5] << 8 | data[4]) * 0.0078125(1/128); 

- 17~18位：比如01 A0，是16位校验位

- 19~20位：保留，暂时为0



55 AA 00 14 01 00 00 00 00 00 00 00 00 00 01 00 F6 0C 00 00