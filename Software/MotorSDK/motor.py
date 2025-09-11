#!/usr/bin/env python3
"""
电机控制基类
提供对电机的基本控制接口
"""

import time
import math
import serial
import threading
import struct
import datetime
import queue
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class CommandType(Enum):
    """命令类型枚举"""
    ENABLE_MOTOR = "enable_motor"
    ENABLE_ALL_MOTORS = "enable_all_motors"
    ENABLE_MOTORS_BROADCAST = "enable_motors_broadcast"
    ENABLE_ALL_MOTORS_BROADCAST = "enable_all_motors_broadcast"
    SET_MOTOR_ANGLE = "set_motor_angle"
    GET_MOTOR_ANGLE = "get_motor_angle"
    JOG_MOTOR = "jog_motor"
    EMERGENCY_STOP = "emergency_stop"
    GET_MOTOR_STATUS = "get_motor_status"
    GET_ALL_MOTOR_STATUS = "get_all_motor_status"
    GET_ALL_MOTOR_ANGLE = "get_all_motor_angle"
    SET_MOTOR_ANGLES_BROADCAST = "set_motor_angles_broadcast"
    SET_MOTOR_SPEEDS_BROADCAST = "set_motor_speeds_broadcast"
    SET_MOTOR_CURRENTS_BROADCAST = "set_motor_currents_broadcast"

class ResponseType(Enum):
    """响应类型枚举"""
    STATUS_RESPONSE = "status_response"
    ANGLE_BROADCAST = "angle_broadcast"
    SPEED_BROADCAST = "speed_broadcast"
    CURRENT_BROADCAST = "current_broadcast"
    ENABLE_BROADCAST = "enable_broadcast"
    ERROR_RESPONSE = "error_response"

@dataclass
class Command:
    """命令数据结构"""
    id: str
    type: CommandType
    data: Dict[str, Any]
    timestamp: float
    callback: Optional[callable] = None
    timeout: float = 5.0  # 默认5秒超时

@dataclass
class Response:
    """响应数据结构"""
    type: ResponseType
    data: Dict[str, Any]
    timestamp: float
    raw_data: bytes

class Motor:
    """电机控制基类"""
    
    # Protocol constants
    FRAME_HEAD = b'\x55\xAA\x00\x14'
    ANGLE_BROADCAST_HEAD1 = b'\x55\xAB'
    ANGLE_BROADCAST_HEAD2 = b'\x55\xAC'
    SPEED_BROADCAST_HEAD1 = b'\x55\xAD'
    SPEED_BROADCAST_HEAD2 = b'\x55\xAE'
    CURRENT_BROADCAST_HEAD1 = b'\x55\xAF'
    CURRENT_BROADCAST_HEAD2 = b'\x55\xB0'
    ENABLE_BROADCAST_HEAD = b'\x55\xB1'
    
    TARGET_DEVICE_ID = 0x01
    DEVICE_BOARDCASE_ID = 0xFF
    JOG_ID = 0xF0
    STATUS_PULL_ID = 0xA0
    
    # 新增电机使能/失能相关的协议常量
    ENABLE_MOTOR_ID = 0xB0  # 单个电机使能/失能命令ID
    ENABLE_ALL_MOTORS_ID = 0xB1  # 所有电机使能/失能命令ID
    ENABLE_BROADCAST_HEAD1 = b'\x55\xB1'  # 1-8号电机广播使能/失能帧头
    ENABLE_BROADCAST_HEAD2 = b'\x55\xB2'  # 9-16号电机广播使能/失能帧头
    
    def __init__(self, port: str = 'COM4', baudrate: int = 256000):
        """
        初始化电机控制实例
        
        Args:
            port: 串口名称
            baudrate: 波特率
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.connected = False
        self.lock = threading.Lock()
        
        # 队列和线程
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.send_thread = None
        self.receive_thread = None
        self.running = False
        
        # 命令计数器
        self.command_counter = 0
        
        # 响应回调字典
        self.response_callbacks = {}
        
        # 数据接收缓冲区
        self.receive_buffer = bytearray()
        self.buffer_lock = threading.Lock()
        
        # CRC16_CCITT_FALSE 查找表
        self.crc16_table = []
        for i in range(256):
            crc = (i << 8) & 0xFFFF
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
            self.crc16_table.append(crc)
    
    def connect(self) -> bool:
        """
        连接到电机控制系统
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.05,  # 50ms超时
                write_timeout=0.05  # 50ms写超时
            )
            self.connected = True
            
            # 清空接收缓冲区
            self.clear_receive_buffer()
            
            # 启动通信线程
            self._start_communication_threads()
            
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开与电机控制系统的连接"""
        self._stop_communication_threads()
        
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
    
    def _start_communication_threads(self):
        """启动通信线程"""
        if not self.running:
            self.running = True
            
            # 启动发送线程
            self.send_thread = threading.Thread(target=self._send_worker, daemon=True)
            self.send_thread.start()
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._receive_worker, daemon=True)
            self.receive_thread.start()
            
            print("通信线程已启动")
    
    def _stop_communication_threads(self):
        """停止通信线程"""
        self.running = False
        
        # 等待线程结束
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.join(timeout=1.0)
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
        
        print("通信线程已停止")
    
    def _send_worker(self):
        """发送工作线程"""
        while self.running:
            try:
                # 从队列获取命令
                command = self.command_queue.get(timeout=0.1)
                
                if command is None:  # 停止信号
                    break
                
                # 执行命令
                self._execute_command(command)
                
                # 标记任务完成
                self.command_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"发送线程错误: {e}")
                time.sleep(0.01)
    
    def _receive_worker(self):
        """接收工作线程"""
        while self.running:
            try:
                if not self.connected or not self.serial:
                    time.sleep(0.1)
                    continue
                
                # 检查是否有数据可读
                if self.serial.in_waiting > 0:
                    # 读取数据
                    data = self.serial.read(self.serial.in_waiting)
                    if data:
                        current_time = datetime.datetime.now()
                        print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 接收数据: {' '.join(f'{b:02X}' for b in data)}")
                        
                        # 将数据添加到缓冲区
                        with self.buffer_lock:
                            self.receive_buffer.extend(data)
                        
                        # 处理缓冲区中的完整数据包
                        self._process_receive_buffer()
                
                time.sleep(0.001)  # 1ms延时
                
            except Exception as e:
                print(f"接收线程错误: {e}")
                time.sleep(0.01)
    
    def _process_receive_buffer(self):
        """处理接收缓冲区中的完整数据包"""
        with self.buffer_lock:
            # 查找完整的帧
            complete_frames = []
            remaining_buffer = bytearray()
            
            # 查找所有帧头位置
            frame_positions = []
            pos = 0
            while pos < len(self.receive_buffer) - 3:
                if self.receive_buffer[pos:pos+4] == self.FRAME_HEAD:
                    frame_positions.append(pos)
                pos += 1
            
            if not frame_positions:
                # 没有找到帧头，保留所有数据
                remaining_buffer = self.receive_buffer.copy()
            else:
                # 处理找到的帧
                for i, frame_start in enumerate(frame_positions):
                    # 计算帧结束位置
                    if i + 1 < len(frame_positions):
                        frame_end = frame_positions[i + 1]
                    else:
                        # 最后一个帧，检查是否有足够的数据
                        if frame_start + 20 <= len(self.receive_buffer):
                            frame_end = frame_start + 20  # 标准帧长度
                        else:
                            # 数据不完整，保留从帧头开始的所有数据
                            frame_end = frame_start
                    
                    if frame_end > frame_start:
                        # 提取完整帧
                        frame_data = bytes(self.receive_buffer[frame_start:frame_end])
                        if len(frame_data) == 20:  # 标准帧长度
                            complete_frames.append(frame_data)
                        else:
                            # 帧不完整，保留从帧头开始的数据
                            remaining_buffer.extend(self.receive_buffer[frame_start:])
                            break
                    else:
                        # 帧不完整，保留从帧头开始的数据
                        remaining_buffer.extend(self.receive_buffer[frame_start:])
                        break
                
                # 如果第一个帧头之前有数据，也保留
                if frame_positions[0] > 0:
                    remaining_buffer = self.receive_buffer[:frame_positions[0]] + remaining_buffer
            
            # 更新缓冲区
            self.receive_buffer = remaining_buffer
            
            # 处理完整的帧
            for frame_data in complete_frames:
                print(f"处理完整帧: {' '.join(f'{b:02X}' for b in frame_data)}")
                responses = self._parse_single_frame(frame_data)
                for response in responses:
                    # 将响应放入队列
                    self.response_queue.put(response)
                    
                    # 检查是否有对应的回调
                    if response.type in self.response_callbacks:
                        for callback in self.response_callbacks[response.type]:
                            try:
                                callback(response)
                            except Exception as e:
                                print(f"响应回调错误: {e}")
            
            # 如果缓冲区中有不完整的数据，打印调试信息
            if len(self.receive_buffer) > 0:
                print(f"缓冲区剩余不完整数据: {' '.join(f'{b:02X}' for b in self.receive_buffer)} (长度: {len(self.receive_buffer)})")
    
    def _send_raw(self, frame: bytes):
        """
        发送原始数据帧
        
        Args:
            frame: 要发送的数据帧
            
        Raises:
            RuntimeError: 发送失败
        """
        if not self.connected or not self.serial:
            raise RuntimeError("未连接到电机控制系统")
            
        with self.lock:
            try:
                # 清空发送缓冲区
                self.serial.reset_output_buffer()

                current_time = datetime.datetime.now()
                print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 发送数据: {' '.join(f'{b:02X}' for b in frame)}")
                # 发送数据
                self.serial.write(frame)
                self.serial.flush()
                time.sleep(0.003)
            except Exception as e:
                raise RuntimeError(f"发送数据失败: {e}")
    
    def _calculate_crc16_ccitt_false(self, data: bytes) -> int:
        """
        计算CRC16_CCITT_FALSE校验值
        
        Args:
            data: 要计算CRC的数据
            
        Returns:
            int: CRC16校验值
        """
        crc = 0xFFFF  # 初始值
        for byte in data:
            crc = ((crc << 8) & 0xFF00) ^ self.crc16_table[((crc >> 8) ^ byte) & 0xFF]
        return crc & 0xFFFF

    def _build_frame(self, can_id: int, can_data: bytes) -> bytes:
        """
        构造通信帧
        
        Args:
            can_id: CAN ID
            can_data: CAN数据
            
        Returns:
            bytes: 完整的通信帧
        """
        # 构造帧头(4字节) + CAN ID(4字节) + CAN数据(8字节)
        frame = self.FRAME_HEAD + struct.pack('<I', can_id) + can_data.ljust(8, b'\x00')
        
        # 计算CRC16_CCITT_FALSE (从CAN ID开始计算)
        crc = self._calculate_crc16_ccitt_false(frame[4:])
        # 将CRC16打包为4字节，高2字节为0
        crc_bytes = struct.pack('<H', crc) + b'\x00\x00'
        frame += crc_bytes
        
        return frame

    def _execute_command(self, command: Command):
        """执行命令"""
        try:
            current_time = datetime.datetime.now()
            print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 执行命令: {command.type.value}")
            
            if command.type == CommandType.ENABLE_MOTOR:
                self._execute_enable_motor(command)
            elif command.type == CommandType.ENABLE_ALL_MOTORS:
                self._execute_enable_all_motors(command)
            elif command.type == CommandType.ENABLE_MOTORS_BROADCAST:
                self._execute_enable_motors_broadcast(command)
            elif command.type == CommandType.ENABLE_ALL_MOTORS_BROADCAST:
                self._execute_enable_all_motors_broadcast(command)
            elif command.type == CommandType.SET_MOTOR_ANGLE:
                self._execute_set_motor_angle(command)
            elif command.type == CommandType.GET_MOTOR_ANGLE:
                self._execute_get_motor_angle(command)
            elif command.type == CommandType.GET_MOTOR_STATUS:
                self._execute_get_motor_status(command)
            elif command.type == CommandType.GET_ALL_MOTOR_STATUS:
                self._execute_get_all_motor_status(command)
            elif command.type == CommandType.GET_ALL_MOTOR_ANGLE:
                self._execute_get_all_motor_angle(command)
            elif command.type == CommandType.JOG_MOTOR:
                self._execute_jog_motor(command)
            elif command.type == CommandType.EMERGENCY_STOP:
                self._execute_emergency_stop(command)
            elif command.type == CommandType.SET_MOTOR_ANGLES_BROADCAST:
                self._execute_set_motor_angles_broadcast(command)
            elif command.type == CommandType.SET_MOTOR_SPEEDS_BROADCAST:
                self._execute_set_motor_speeds_broadcast(command)
            elif command.type == CommandType.SET_MOTOR_CURRENTS_BROADCAST:
                self._execute_set_motor_currents_broadcast(command)
            else:
                print(f"未知命令类型: {command.type}")
                
        except Exception as e:
            print(f"执行命令失败: {e}")
            # 创建错误响应
            error_response = Response(
                type=ResponseType.ERROR_RESPONSE,
                data={"error": str(e), "command_id": command.id},
                timestamp=time.time(),
                raw_data=b''
            )
            self.response_queue.put(error_response)
    
    def _parse_response_data(self, data: bytes) -> list:
        """解析响应数据"""
        responses = []
        
        try:
            # 检查数据长度
            if len(data) < 4:
                return responses
            
            print(f"开始解析响应数据，总长度: {len(data)} 字节")
            
            # 查找所有帧头位置
            frame_positions = []
            pos = 0
            while pos < len(data) - 3:
                if data[pos:pos+4] == self.FRAME_HEAD:
                    frame_positions.append(pos)
                pos += 1
            
            print(f"找到 {len(frame_positions)} 个帧头位置: {frame_positions}")
            
            # 逐个解析每个数据包
            for i, frame_start in enumerate(frame_positions):
                print(f"解析第 {i+1} 个数据包，起始位置: {frame_start}")
                
                # 计算数据包结束位置
                if i + 1 < len(frame_positions):
                    frame_end = frame_positions[i + 1]
                else:
                    frame_end = len(data)
                
                # 提取当前数据包
                frame_data = data[frame_start:frame_end]
                print(f"数据包 {i+1} 长度: {len(frame_data)} 字节")
                print(f"数据包 {i+1} 内容: {' '.join(f'{b:02X}' for b in frame_data)}")
                
                # 解析当前数据包
                frame_responses = self._parse_single_frame(frame_data)
                responses.extend(frame_responses)
            
            print(f"总共解析出 {len(responses)} 个响应")
            return responses
                    
        except Exception as e:
            print(f"解析响应数据失败: {e}")
            import traceback
            traceback.print_exc()
        
        return responses
    
    def _parse_single_frame(self, frame_data: bytes) -> list:
        """解析单个数据帧"""
        responses = []
        
        try:
            # 检查帧头
            if frame_data[0:4] == self.FRAME_HEAD:
                # 这是一个有效的响应帧
                if len(frame_data) >= 20:
                    # 解析状态响应
                    motor_id = frame_data[5] if len(frame_data) > 5 else 0
                    
                    # 检查是否是状态响应
                    if frame_data[4] == 0x00:  # 响应ID
                        # 解析数据包1
                        if len(frame_data) >= 16:
                            data1 = frame_data[8:16]
                            fsm_state = data1[0]
                            error_code = data1[1]
                            soft_version = data1[2]
                            temp = data1[3] - 50  # 减去偏移量50
                            
                            # 解析角度数据
                            raw_angle = (data1[5] << 8 | data1[4])
                            if raw_angle & 0x8000:
                                raw_angle = raw_angle - 0x10000
                            angle = raw_angle * 0.0078125  # Q7格式转角度
                            
                            # 解析母线电压
                            raw_bus_voltage = (data1[7] << 8 | data1[6])
                            if raw_bus_voltage & 0x8000:
                                raw_bus_voltage = raw_bus_voltage - 0x10000
                            bus_voltage = raw_bus_voltage * 0.0078125  # Q7格式转电压
                            
                            # 判断电机是否在线
                            # fsm_state != 9 表示电机在线，fsm_state == 9 表示电机离线
                            is_online = fsm_state != 9
                            
                            print(f"解析电机{motor_id}状态响应: fsm_state={fsm_state}, online={is_online}")
                            
                            # 创建状态响应
                            status_response = Response(
                                type=ResponseType.STATUS_RESPONSE,
                                data={
                                    'motor_id': motor_id,
                                    'online': is_online,
                                    'fsm_state': fsm_state,
                                    'error_code': error_code,
                                    'soft_version': f"v{soft_version//100}.{(soft_version%100)//10}.{soft_version%10}",
                                    'temp': temp,
                                    'angle': angle,
                                    'bus_voltage': bus_voltage
                                },
                                timestamp=time.time(),
                                raw_data=frame_data
                            )
                            responses.append(status_response)
            
            # 检查广播帧头
            elif frame_data[0:2] in [self.ANGLE_BROADCAST_HEAD1, self.ANGLE_BROADCAST_HEAD2]:
                # 角度广播响应
                if len(frame_data) >= 20:
                    angles = {}
                    for i in range(8):
                        if i*2+1 < len(frame_data)-2:  # 减去CRC长度
                            angle_value = struct.unpack('<h', frame_data[2+i*2:4+i*2])[0]
                            motor_id = i + 1 + (0 if frame_data[0:2] == self.ANGLE_BROADCAST_HEAD1 else 8)
                            angles[motor_id] = angle_value * 0.0078125  # Q7格式转角度
                    
                    broadcast_response = Response(
                        type=ResponseType.ANGLE_BROADCAST,
                        data={'angles': angles},
                        timestamp=time.time(),
                        raw_data=frame_data
                    )
                    responses.append(broadcast_response)
            
            elif frame_data[0:2] in [self.SPEED_BROADCAST_HEAD1, self.SPEED_BROADCAST_HEAD2]:
                # 速度广播响应
                if len(frame_data) >= 20:
                    speeds = {}
                    for i in range(8):
                        if i*2+1 < len(frame_data)-2:
                            speed_value = struct.unpack('<h', frame_data[2+i*2:4+i*2])[0]
                            motor_id = i + 1 + (0 if frame_data[0:2] == self.SPEED_BROADCAST_HEAD1 else 8)
                            speeds[motor_id] = speed_value / 163.84  # Q15格式转百分比
                    
                    broadcast_response = Response(
                        type=ResponseType.SPEED_BROADCAST,
                        data={'speeds': speeds},
                        timestamp=time.time(),
                        raw_data=frame_data
                    )
                    responses.append(broadcast_response)
            
            elif frame_data[0:2] in [self.CURRENT_BROADCAST_HEAD1, self.CURRENT_BROADCAST_HEAD2]:
                # 电流广播响应
                if len(frame_data) >= 20:
                    currents = {}
                    for i in range(8):
                        if i*2+1 < len(frame_data)-2:
                            current_value = struct.unpack('<h', frame_data[2+i*2:4+i*2])[0]
                            motor_id = i + 1 + (0 if frame_data[0:2] == self.CURRENT_BROADCAST_HEAD1 else 8)
                            currents[motor_id] = current_value
                    
                    broadcast_response = Response(
                        type=ResponseType.CURRENT_BROADCAST,
                        data={'currents': currents},
                        timestamp=time.time(),
                        raw_data=frame_data
                    )
                    responses.append(broadcast_response)
            
            elif frame_data[0:2] in [self.ENABLE_BROADCAST_HEAD1, self.ENABLE_BROADCAST_HEAD2]:
                # 使能广播响应
                if len(frame_data) >= 20:
                    enable_states = {}
                    for i in range(16):
                        if i < len(frame_data)-2:
                            enable_states[i+1] = frame_data[2+i] == 1
                    
                    broadcast_response = Response(
                        type=ResponseType.ENABLE_BROADCAST,
                        data={'enable_states': enable_states},
                        timestamp=time.time(),
                        raw_data=frame_data
                    )
                    responses.append(broadcast_response)
                    
        except Exception as e:
            print(f"解析单个数据帧失败: {e}")
        
        return responses

    def _execute_enable_motor(self, command: Command):
        """执行单个电机使能命令"""
        motor_id = command.data['motor_id']
        enable = command.data['enable']
        
        if not 1 <= motor_id <= 15:
            raise ValueError(f"无效的电机ID: {motor_id}")
        
        # 构造20字节的命令数据
        data = bytearray(20)
        # 设置帧头
        data[0:4] = self.FRAME_HEAD
        # 设置电机ID
        data[4] = motor_id
        # 设置使能状态
        data[14] = 1 if enable else 2
        
        # 计算CRC
        crc = self._calculate_crc16_ccitt_false(data[4:16])
        data[16:18] = struct.pack('<H', crc)
        
        current_time = datetime.datetime.now()
        print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 使能电机{motor_id}命令: {' '.join(f'{b:02X}' for b in data)}")
        
        # 发送命令
        self._send_raw(data)
    
    def _execute_enable_all_motors(self, command: Command):
        """执行所有电机使能命令"""
        enable = command.data['enable']
        
        # 构造所有电机使能/失能命令
        can_data = bytes([0xFF, 1 if enable else 0]) + b'\x00' * 6
        frame = self._build_frame(self.ENABLE_ALL_MOTORS_ID, can_data)

        current_time = datetime.datetime.now()
        print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 广播使能命令: {' '.join(f'{b:02X}' for b in frame)}")
        
        # 发送命令
        self._send_raw(frame)
    
    def _execute_enable_motors_broadcast(self, command: Command):
        """执行电机广播使能命令"""
        enable_states = command.data['enable_states']
        
        # 构造16字节的数据，每个字节表示一个电机的状态
        data = bytearray(16)
        for motor_id, enable in enable_states.items():
            if not 1 <= motor_id <= 16:
                raise ValueError(f"无效的电机ID: {motor_id}")
            # 1=使能，2=失能
            data[motor_id - 1] = 1 if enable else 2
            
        # 计算CRC
        crc = self._calculate_crc16_ccitt_false(data)
        crc_bytes = struct.pack('<H', crc)
        
        # 构造完整帧：帧头 + 数据 + CRC
        frame = self.ENABLE_BROADCAST_HEAD + data + crc_bytes

        current_time = datetime.datetime.now()
        print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 广播使能命令: {' '.join(f'{b:02X}' for b in frame)}")
        
        # 发送命令
        self._send_raw(frame)
    
    def _execute_enable_all_motors_broadcast(self, command: Command):
        """执行所有电机广播使能命令"""
        enable = command.data['enable']
        
        # 构造16字节的数据，所有电机设置为相同状态
        data = bytearray(16)
        enable_value = 1 if enable else 2  # 1=使能，2=失能
        for i in range(16):
            data[i] = enable_value
            
        # 计算CRC
        crc = self._calculate_crc16_ccitt_false(data)
        crc_bytes = struct.pack('<H', crc)
        
        # 构造完整帧：帧头 + 数据 + CRC
        frame = self.ENABLE_BROADCAST_HEAD + data + crc_bytes

        current_time = datetime.datetime.now()
        print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 广播所有电机使能命令: {' '.join(f'{b:02X}' for b in frame)}")
        
        # 发送命令
        self._send_raw(frame)
    
    def _execute_set_motor_angle(self, command: Command):
        """执行设置电机角度命令"""
        motor_id = command.data['motor_id']
        angle = command.data['angle']
        speed = command.data.get('speed', 0.5)
        
        # 将角度转换为度数
        angle_deg = math.degrees(angle)
        
        # 将速度转换为百分比
        speed_percent = max(0, min(100, speed * 100))
        
        # 构造命令数据
        ref_q7 = int(angle_deg * 128)  # Q7 表示的角度
        spd_ref = int(speed_percent * 300.00)  # 百分比转Q15 
        cur_ref = int(5000)
        
        can_data = struct.pack('<hhh', ref_q7, spd_ref, cur_ref) + b'\x00' * 2
        frame = self._build_frame(motor_id, can_data)

        # current_time = datetime.datetime.now()
        # print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 发送角度设置命令: {' '.join(f'{b:02X}' for b in frame)}")
        
        # 发送命令
        self._send_raw(frame)
    
    def _execute_get_motor_status(self, command: Command):
        """执行获取电机状态命令"""
        motor_id = command.data['motor_id']
        
        # 构造状态查询命令 - 数据包1
        can_data1 = bytes([motor_id, 0x01]) + b'\x00' * 6
        frame1 = self._build_frame(self.STATUS_PULL_ID, can_data1)
        
        # 构造状态查询命令 - 数据包2
        can_data2 = bytes([motor_id, 0x02]) + b'\x00' * 6
        frame2 = self._build_frame(self.STATUS_PULL_ID, can_data2)
        
        print(f"\n检查电机{motor_id}状态:")
        print(f"发送数据包1命令: {' '.join(f'{b:02X}' for b in frame1)}")
        print(f"发送数据包2命令: {' '.join(f'{b:02X}' for b in frame2)}")
        
        # 发送命令
        self._send_raw(frame1)
        # time.sleep(0.002)  # 短暂延时
        # self._send_raw(frame2) # TUDO
    
    def _execute_get_motor_angle(self, command: Command):
        """执行获取电机角度命令"""
        motor_id = command.data['motor_id']
        
        # 构造状态查询命令 - 数据包1（包含角度信息）
        can_data1 = bytes([motor_id, 0x01]) + b'\x00' * 6
        frame1 = self._build_frame(self.STATUS_PULL_ID, can_data1)
        
        print(f"获取电机{motor_id}角度:")
        print(f"发送状态查询命令: {' '.join(f'{b:02X}' for b in frame1)}")
        
        # 发送命令
        self._send_raw(frame1)
    
    def _execute_get_all_motor_status(self, command: Command):
        """执行获取所有电机状态命令"""
        print("获取所有电机状态:")
        
        # 逐个查询每个电机的状态
        for motor_id in range(1, 16):
            try:
                # 构造状态查询命令 - 数据包1
                can_data1 = bytes([motor_id, 0x01]) + b'\x00' * 6
                frame1 = self._build_frame(self.STATUS_PULL_ID, can_data1)
                
                # 发送命令
                self._send_raw(frame1)
                # time.sleep(0.01)  # 添加延时避免通信冲突
                
            except Exception as e:
                print(f"查询电机{motor_id}状态失败: {e}")
    
    def _execute_get_all_motor_angle(self, command: Command):
        """执行获取所有电机角度命令"""
        print("获取所有电机角度:")
        
        # 逐个查询每个电机的角度（通过状态查询获取）
        for motor_id in range(1, 16):
            try:
                # 构造状态查询命令 - 数据包1（包含角度信息）
                can_data1 = bytes([motor_id, 0x01]) + b'\x00' * 6
                frame1 = self._build_frame(self.STATUS_PULL_ID, can_data1)
                
                # 发送命令
                self._send_raw(frame1)
                # time.sleep(0.01)  # 添加延时避免通信冲突
                
            except Exception as e:
                print(f"查询电机{motor_id}角度失败: {e}")
    
    def _execute_jog_motor(self, command: Command):
        """执行点动控制命令"""
        motor_id = command.data['motor_id']
        direction = command.data['direction']
        
        if direction not in [0, 1, 2]:
            raise ValueError(f"无效的方向值: {direction}")
        
        # 构造点动命令
        can_data = bytes([motor_id, 0, direction]) + b'\x00' * 5
        frame = self._build_frame(self.JOG_ID, can_data)
        
        # 发送命令
        self._send_raw(frame)
    
    def _execute_emergency_stop(self, command: Command):
        """执行紧急停止命令"""
        # 停止所有电机
        for motor_id in range(1, 16):
            try:
                can_data = bytes([motor_id, 0, 0]) + b'\x00' * 5
                frame = self._build_frame(self.JOG_ID, can_data)
                self._send_raw(frame)
            except Exception as e:
                print(f"停止电机 {motor_id} 失败: {e}")
    
    def _execute_set_motor_angles_broadcast(self, command: Command):
        """执行广播设置电机角度命令"""
        angles = command.data['angles']
        
        # 将角度转换为Q7格式
        angle_values = {motor_id: int(angle * 128) for motor_id, angle in angles.items()}
        self._broadcast_motor_values(
            angle_values,
            self.ANGLE_BROADCAST_HEAD1,
            self.ANGLE_BROADCAST_HEAD2,
            (-32768, 32767),  # Q7格式的范围
            "角度"
        )
    
    def _execute_set_motor_speeds_broadcast(self, command: Command):
        """执行广播设置电机速度命令"""
        speeds = command.data['speeds']
        
        # 将速度百分比转换为Q15格式
        speed_values = {motor_id: int(speed * 163.84) for motor_id, speed in speeds.items()}
        self._broadcast_motor_values(
            speed_values,
            self.SPEED_BROADCAST_HEAD1,
            self.SPEED_BROADCAST_HEAD2,
            (0, 16384),  # Q15格式的范围
            "速度"
        )
    
    def _execute_set_motor_currents_broadcast(self, command: Command):
        """执行广播设置电机电流命令"""
        currents = command.data['currents']
        
        self._broadcast_motor_values(
            currents,
            self.CURRENT_BROADCAST_HEAD1,
            self.CURRENT_BROADCAST_HEAD2,
            (0, 3000),  # 电流范围
            "电流"
        )

    def _broadcast_motor_values(self, values: Dict[int, float], head1: bytes, head2: bytes, 
                              value_range: Tuple[float, float], value_name: str):
        """
        通用的电机值广播函数
        
        Args:
            values: 电机ID到值的映射字典
            head1: 第一组广播的帧头
            head2: 第二组广播的帧头
            value_range: 值的有效范围 (min, max)
            value_name: 值的名称（用于日志）
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")

        # 分组
        group1 = {}  # 1-8号电机
        group2 = {}  # 9-16号电机
        min_val, max_val = value_range
        
        for motor_id, value in values.items():
            if not 1 <= motor_id <= 16:
                raise ValueError(f"无效的电机ID: {motor_id}")
            if not min_val <= value <= max_val:
                raise ValueError(f"无效的{value_name}值: {value}，必须在{min_val}-{max_val}之间")
            if 1 <= motor_id <= 8:
                group1[motor_id] = value
            else:
                group2[motor_id] = value

        def send_group(group: Dict[int, float], head: bytes, group_num: int):
            """发送一组电机值"""
            data = bytearray(16)
            for i in range(8):
                motor_id = i + 1 + (group_num - 1) * 8
                if motor_id in group:
                    data[i*2:i*2+2] = struct.pack('<h', group[motor_id])
                else:
                    data[i*2:i*2+2] = b'\x00\x00'
            crc = self._calculate_crc16_ccitt_false(data)
            crc_bytes = struct.pack('<H', crc)
            frame = head + data + crc_bytes
            current_time = datetime.datetime.now()
            print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 广播{value_name}命令{group_num}: {' '.join(f'{b:02X}' for b in frame)}")
            self._send_raw(frame)
            # time.sleep(0.002)

        # 发送两组广播
        send_group(group1, head1, 1)
        send_group(group2, head2, 2)

    # 公共接口方法
    def enable_motor(self, motor_id: int, enable: bool = True, callback: Optional[callable] = None) -> str:
        """
        设置指定电机的使能/失能状态
        
        Args:
            motor_id: 电机ID (1-15)
            enable: True表示使能，False表示失能
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"enable_motor_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.ENABLE_MOTOR,
            data={'motor_id': motor_id, 'enable': enable},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def enable_all_motors(self, enable: bool = True, callback: Optional[callable] = None) -> str:
        """
        设置所有电机的使能/失能状态
        
        Args:
            enable: True表示使能，False表示失能
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"enable_all_motors_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.ENABLE_ALL_MOTORS,
            data={'enable': enable},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def enable_motors_broadcast(self, enable_states: Dict[int, bool], callback: Optional[callable] = None) -> str:
        """
        广播设置多个电机的使能/失能状态
        
        Args:
            enable_states: 电机ID到使能状态的映射字典
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"enable_motors_broadcast_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.ENABLE_MOTORS_BROADCAST,
            data={'enable_states': enable_states},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def enable_all_motors_broadcast(self, enable: bool = True, callback: Optional[callable] = None) -> str:
        """
        广播设置所有电机的使能/失能状态
        
        Args:
            enable: True表示使能，False表示失能
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"enable_all_motors_broadcast_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.ENABLE_ALL_MOTORS_BROADCAST,
            data={'enable': enable},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def set_motor_angle(self, motor_id: int, angle: float, speed: float = 0.5, callback: Optional[callable] = None) -> str:
        """
        设置指定电机的角度
        
        Args:
            motor_id: 电机ID
            angle: 目标角度(弧度)
            speed: 运动速度(0-1)
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"set_motor_angle_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.SET_MOTOR_ANGLE,
            data={'motor_id': motor_id, 'angle': angle, 'speed': speed},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def get_motor_status(self, motor_id: int, sync: bool = False, timeout: float = 1.0) -> Dict:
        """获取指定电机的状态
        
        Args:
            motor_id: 电机ID
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            Dict: 电机状态信息
        """
        if not self.connected:
            return {'online': False, 'angle': 0.0, 'fsm_state': 0, 'error_code': 0, 'temp': 0.0, 'bus_voltage': 0.0}
        
        if sync:
            # 同步方式：直接发送命令并等待响应
            return self._get_motor_status_sync(motor_id, timeout)
        else:
            # 异步方式：发送命令到队列，尝试从响应队列获取最新数据
            command_id = f"get_motor_status_{self.command_counter}"
            self.command_counter += 1
            
            command = Command(
                id=command_id,
                type=CommandType.GET_MOTOR_STATUS,
                data={'motor_id': motor_id},
                timestamp=time.time()
            )
            
            self.command_queue.put(command)
            
            # 尝试从响应队列获取该电机的最近状态
            return self._get_latest_motor_status(motor_id, timeout)
    
    def _get_latest_motor_status(self, motor_id: int, timeout: float = 0.2) -> Dict:
        """从响应队列获取指定电机的最新状态
        
        Args:
            motor_id: 电机ID
            timeout: 等待超时时间（秒），默认0.2秒
            
        Returns:
            Dict: 电机状态信息
        """
        try:
            # 等待一小段时间，让响应数据到达
            start_time = time.time()
            wait_time = timeout  # 使用传入的timeout参数
            
            print(f"开始从响应队列获取电机{motor_id}状态，等待时间: {wait_time*1000:.0f}ms")
            
            while time.time() - start_time < wait_time:
                # 检查响应队列中是否有该电机的状态数据
                temp_responses = []
                latest_status = None
                
                # 从响应队列中取出所有响应，寻找目标电机的状态
                while not self.response_queue.empty():
                    try:
                        response = self.response_queue.get_nowait()
                        temp_responses.append(response)
                        
                        # 检查是否是目标电机的状态响应
                        if (hasattr(response, 'type') and hasattr(response, 'data') and
                            response.type.value == 'status_response' and 
                            response.data.get('motor_id') == motor_id):
                            latest_status = response.data
                            print(f"从响应队列获取电机{motor_id}真实状态: {latest_status}")
                    except queue.Empty:
                        break
                
                # 将其他响应放回队列
                for response in temp_responses:
                    if response != latest_status:  # 不重复放回已找到的状态
                        self.response_queue.put(response)
                
                # 如果找到了状态数据，返回真实数据
                if latest_status:
                    return latest_status
                
                # 短暂等待后再次检查
                time.sleep(0.01)  # 10ms
            
            # 如果没有找到，返回默认值
            print(f"等待{wait_time*1000:.0f}ms后未收到电机{motor_id}响应，返回默认状态")
            return {
                'online': False,
                'angle': 0.0,
                'fsm_state': 0,
                'error_code': 0,
                'temp': 25.0,
                'bus_voltage': 24.0
            }
            
        except Exception as e:
            print(f"获取电机{motor_id}最新状态失败: {e}")
            return {
                'online': False,
                'angle': 0.0,
                'fsm_state': 0,
                'error_code': 0,
                'temp': 25.0,
                'bus_voltage': 24.0
            }
    
    def get_all_motor_status(self, sync: bool = False, timeout: float = 0.5) -> Dict[int, bool]:
        """获取所有电机的状态
        
        Args:
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            Dict[int, bool]: 电机ID到状态的映射，True表示在线，False表示离线
        """
        if not self.connected:
            return {i: False for i in range(1, 16)}
        
        if sync:
            # 同步方式：逐个获取每个电机的状态
            status = {}
            for motor_id in range(1, 16):
                try:
                    motor_status = self._get_motor_status_sync(motor_id, timeout=timeout/15)
                    status[motor_id] = motor_status.get('online', False)
                except Exception as e:
                    print(f"获取电机{motor_id}状态失败: {e}")
                    status[motor_id] = False
            return status
        else:
            # 异步方式：发送命令到队列，尝试从响应队列获取最新数据
            command_id = f"get_all_motor_status_{self.command_counter}"
            self.command_counter += 1
            
            command = Command(
                id=command_id,
                type=CommandType.GET_ALL_MOTOR_STATUS,
                data={},
                timestamp=time.time()
            )
            
            self.command_queue.put(command)
            
            # 尝试从响应队列获取所有电机的最新状态
            return self._get_latest_all_motor_status(timeout)
    
    def get_all_motor_angle(self, sync: bool = False, timeout: float = 0.5) -> Dict[int, float]:
        """获取所有电机的角度
        
        Args:
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            Dict[int, float]: 电机ID到角度的映射，角度单位为弧度
        """
        if not self.connected:
            return {i: 0.0 for i in range(1, 16)}
        
        if sync:
            # 同步方式：逐个获取每个电机的角度
            angles = {}
            for motor_id in range(1, 16):
                try:
                    motor_status = self._get_motor_status_sync(motor_id, timeout=timeout/15)
                    angles[motor_id] = motor_status.get('angle', 0.0)
                except Exception as e:
                    print(f"获取电机{motor_id}角度失败: {e}")
                    angles[motor_id] = 0.0
            return angles
        else:
            # 异步方式：发送命令到队列，尝试从响应队列获取最新数据
            command_id = f"get_all_motor_angle_{self.command_counter}"
            self.command_counter += 1
            
            command = Command(
                id=command_id,
                type=CommandType.GET_ALL_MOTOR_ANGLE,  # 使用获取所有电机角度的命令
                data={},
                timestamp=time.time()
            )
            
            self.command_queue.put(command)
            
            # 尝试从响应队列获取所有电机的最新角度
            return self._get_latest_all_motor_angle(timeout)
    
    def _get_latest_all_motor_status(self, timeout: float = 0.5) -> Dict[int, bool]:
        """从响应队列获取所有电机的最新状态
        
        Args:
            timeout: 等待超时时间（秒），默认0.5秒
            
        Returns:
            Dict[int, bool]: 电机ID到状态的映射，True表示在线，False表示离线
        """
        try:
            # 等待一小段时间，让响应数据到达
            start_time = time.time()
            wait_time = timeout  # 使用传入的timeout参数
            motor_statuses = {}
            
            print(f"开始从响应队列获取电机状态，等待时间: {wait_time*1000:.0f}ms")
            
            while time.time() - start_time < wait_time:
                # 检查响应队列中是否有电机状态数据
                temp_responses = []
                batch_updated = False
                
                # 从响应队列中取出所有响应，收集电机状态
                while not self.response_queue.empty():
                    try:
                        response = self.response_queue.get_nowait()
                        temp_responses.append(response)
                        
                        # 检查是否是状态响应
                        if hasattr(response, 'type') and hasattr(response, 'data'):
                            if response.type.value == 'status_response':
                                motor_id = response.data.get('motor_id')
                                if motor_id and 1 <= motor_id <= 15:
                                    is_online = response.data.get('online', False)
                                    motor_statuses[motor_id] = is_online
                                    batch_updated = True
                                    # print(f"从响应队列获取电机{motor_id}状态: online={is_online}")
                    except queue.Empty:
                        break

                # 将其他响应放回队列
                for response in temp_responses:
                    self.response_queue.put(response)
                
                # 如果这一批次有更新，继续等待更多数据
                if batch_updated:
                    print(f"批次更新完成，当前已获取{len(motor_statuses)}个电机状态")
                    # 短暂等待，让更多响应到达
                    time.sleep(0.01)  # 10ms
                else:
                    # 没有新数据，稍微等待一下再检查
                    time.sleep(0.02)  # 20ms
            
            # 构建完整的状态字典
            all_status = {}
            for motor_id in range(1, 16):
                all_status[motor_id] = motor_statuses.get(motor_id, False)
            
            if motor_statuses:
                print(f"响应队列状态获取完成，共获取{len(motor_statuses)}个电机状态: {motor_statuses}")
            else:
                print(f"等待{wait_time*1000:.0f}ms后未收到电机响应，返回默认状态")
            
            return all_status
            
        except Exception as e:
            print(f"获取所有电机最新状态失败: {e}")
            return {i: False for i in range(1, 16)}
    
    def _get_latest_all_motor_angle(self, timeout: float = 0.5) -> Dict[int, float]:
        """从响应队列获取所有电机的最新角度
        
        Args:
            timeout: 等待超时时间（秒），默认0.5秒
            
        Returns:
            Dict[int, float]: 电机ID到角度的映射，角度单位为弧度
        """
        try:
            # 等待一小段时间，让响应数据到达
            start_time = time.time()
            wait_time = timeout  # 使用传入的timeout参数
            motor_angles = {}
            
            print(f"开始从响应队列获取电机角度，等待时间: {wait_time*1000:.0f}ms")
            
            while time.time() - start_time < wait_time:
                # 检查响应队列中是否有电机状态数据
                temp_responses = []
                batch_updated = False
                
                # 从响应队列中取出所有响应，收集电机角度
                while not self.response_queue.empty():
                    try:
                        response = self.response_queue.get_nowait()
                        temp_responses.append(response)
                        
                        # 检查是否是状态响应
                        if hasattr(response, 'type') and hasattr(response, 'data'):
                            if response.type.value == 'status_response':
                                motor_id = response.data.get('motor_id')
                                if motor_id and 1 <= motor_id <= 15:
                                    angle = response.data.get('angle', 0.0)
                                    motor_angles[motor_id] = angle
                                    batch_updated = True
                                    # print(f"从响应队列获取电机{motor_id}角度: {angle:.4f}")
                    except queue.Empty:
                        break

                # 将其他响应放回队列
                for response in temp_responses:
                    self.response_queue.put(response)
                
                # 如果这一批次有更新，继续等待更多数据
                if batch_updated:
                    print(f"批次更新完成，当前已获取{len(motor_angles)}个电机角度")
                    # 短暂等待，让更多响应到达
                    time.sleep(0.01)  # 10ms
                else:
                    # 没有新数据，稍微等待一下再检查
                    time.sleep(0.02)  # 20ms
            
            # 构建完整的角度字典
            all_angles = {}
            for motor_id in range(1, 16):
                all_angles[motor_id] = motor_angles.get(motor_id, 0.0)
            
            if motor_angles:
                print(f"响应队列角度获取完成，共获取{len(motor_angles)}个电机角度")
            else:
                print(f"等待{wait_time*1000:.0f}ms后未收到电机角度响应，返回默认角度")
            
            return all_angles
            
        except Exception as e:
            print(f"获取所有电机最新角度失败: {e}")
            return {i: 0.0 for i in range(1, 16)}
    
    def get_motor_angle(self, motor_id: int, sync: bool = False, timeout: float = 0.2) -> float:
        """获取指定电机的当前角度
        
        Args:
            motor_id: 电机ID
            sync: 是否使用同步方式（True=同步等待响应，False=异步返回默认值）
            timeout: 同步等待超时时间（秒）
            
        Returns:
            float: 当前角度(弧度)
        """
        if not self.connected:
            return 0.0
        
        if sync:
            # 同步方式：获取电机状态并提取角度
            status = self._get_motor_status_sync(motor_id, timeout)
            return status.get('angle', 0.0)
        else:
            # 异步方式：发送命令到队列，尝试从响应队列获取最新数据
            command_id = f"get_motor_angle_{self.command_counter}"
            self.command_counter += 1
            
            command = Command(
                id=command_id,
                type=CommandType.GET_MOTOR_ANGLE,
                data={'motor_id': motor_id},
                timestamp=time.time()
            )
            
            self.command_queue.put(command)
            
            # 尝试从响应队列获取该电机的最近角度
            status = self._get_latest_motor_status(motor_id, timeout)
            return status.get('angle', 0.0)

    def jog_motor(self, motor_id: int, direction: int, callback: Optional[callable] = None) -> str:
        """
        点动控制指定电机
        
        Args:
            motor_id: 电机ID
            direction: 运动方向(0=停止, 1=顺时针, 2=逆时针)
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"jog_motor_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.JOG_MOTOR,
            data={'motor_id': motor_id, 'direction': direction},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def emergency_stop(self, callback: Optional[callable] = None) -> str:
        """
        紧急停止所有电机
        
        Args:
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"emergency_stop_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.EMERGENCY_STOP,
            data={},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def _get_motor_status_sync(self, motor_id: int, timeout: float = 1.0) -> Dict:
        """同步获取电机状态"""
        try:
            # 清空响应队列中的旧数据
            self.clear_response_queue()
            
            # 发送命令
            command_id = f"get_motor_status_sync_{self.command_counter}"
            self.command_counter += 1
            
            command = Command(
                id=command_id,
                type=CommandType.GET_MOTOR_STATUS,
                data={'motor_id': motor_id},
                timestamp=time.time()
            )
            
            self.command_queue.put(command)
            
            # 等待响应
            start_time = time.time()
            while time.time() - start_time < timeout:
                response = self.get_response(timeout=0.1)
                if response and response.type == ResponseType.STATUS_RESPONSE:
                    if response.data.get('motor_id') == motor_id:
                        return response.data
                time.sleep(0.01)
            
            # 超时返回默认值
            print(f"获取电机{motor_id}状态超时")
            return {
                'online': False,
                'angle': 0.0,
                'fsm_state': 0,
                'error_code': 0,
                'temp': 25.0,
                'bus_voltage': 24.0
            }
            
        except Exception as e:
            print(f"同步获取电机{motor_id}状态失败: {e}")
            return {
                'online': False,
                'angle': 0.0,
                'fsm_state': 0,
                'error_code': 0,
                'temp': 25.0,
                'bus_voltage': 24.0
            }

    def add_response_callback(self, response_type: ResponseType, callback: callable):
        """
        添加响应回调函数
        
        Args:
            response_type: 响应类型
            callback: 回调函数
        """
        if response_type not in self.response_callbacks:
            self.response_callbacks[response_type] = []
        self.response_callbacks[response_type].append(callback)

    def remove_response_callback(self, response_type: ResponseType, callback: callable):
        """
        移除响应回调函数
        
        Args:
            response_type: 响应类型
            callback: 回调函数
        """
        if response_type in self.response_callbacks:
            try:
                self.response_callbacks[response_type].remove(callback)
            except ValueError:
                pass

    def get_response(self, timeout: float = 1.0) -> Optional[Response]:
        """
        获取响应数据
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            Response: 响应数据，如果超时返回None
        """
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def clear_response_queue(self):
        """清空响应队列"""
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break

    def get_queue_status(self) -> Dict[str, int]:
        """
        获取队列状态
        
        Returns:
            Dict[str, int]: 包含命令队列和响应队列长度的字典
        """
        return {
            'command_queue_size': self.command_queue.qsize(),
            'response_queue_size': self.response_queue.qsize(),
            'receive_buffer_size': len(self.receive_buffer)
        }

    def set_motor_angles_broadcast(self, angles: Dict[int, float], callback: Optional[callable] = None) -> str:
        """
        广播设置多个电机的角度
        
        Args:
            angles: 电机ID到角度的映射字典，角度单位为度
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"set_motor_angles_broadcast_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.SET_MOTOR_ANGLES_BROADCAST,
            data={'angles': angles},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def set_motor_speeds_broadcast(self, speeds: Dict[int, float], callback: Optional[callable] = None) -> str:
        """
        广播设置多个电机的速度
        
        Args:
            speeds: 电机ID到速度的映射字典，速度为百分比(0-100)
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"set_motor_speeds_broadcast_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.SET_MOTOR_SPEEDS_BROADCAST,
            data={'speeds': speeds},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def set_motor_currents_broadcast(self, currents: Dict[int, int], callback: Optional[callable] = None) -> str:
        """
        广播设置多个电机的电流
        
        Args:
            currents: 电机ID到电流的映射字典，电流单位为mA
            callback: 响应回调函数
            
        Returns:
            str: 命令ID
        """
        if not self.connected:
            raise RuntimeError("未连接到电机控制系统")
            
        command_id = f"set_motor_currents_broadcast_{self.command_counter}"
        self.command_counter += 1
        
        command = Command(
            id=command_id,
            type=CommandType.SET_MOTOR_CURRENTS_BROADCAST,
            data={'currents': currents},
            timestamp=time.time(),
            callback=callback
        )
        
        self.command_queue.put(command)
        return command_id

    def clear_receive_buffer(self):
        """清空接收缓冲区"""
        with self.buffer_lock:
            self.receive_buffer.clear()
            print("接收缓冲区已清空")

    def get_buffer_status(self) -> Dict[str, int]:
        """
        获取缓冲区状态
        
        Returns:
            Dict[str, int]: 包含接收缓冲区长度的字典
        """
        with self.buffer_lock:
            return {
                'receive_buffer_size': len(self.receive_buffer),
                'command_queue_size': self.command_queue.qsize(),
                'response_queue_size': self.response_queue.qsize()
            }
