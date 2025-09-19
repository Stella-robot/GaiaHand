#!/usr/bin/env python3
"""
串口工具模块

提供跨平台的串口检测和配置功能，用于手部控制器的连接配置。
支持Windows和Linux系统。
"""

import serial
import serial.tools.list_ports
import logging
import os
import platform
import glob
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def get_system_type() -> str:
    """
    获取当前操作系统类型
    
    Returns:
        str: 操作系统类型 ('windows', 'linux', 'darwin', 'unknown')
    """
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'darwin'
    else:
        return 'unknown'

def get_common_ports() -> Dict[str, List[str]]:
    """
    获取不同系统下的常见串口名称
    
    Returns:
        Dict[str, List[str]]: 系统到常见串口列表的映射
    """
    return {
        'windows': ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8'],
        'linux': ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
                  '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3',
                  '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3'],
        'darwin': ['/dev/tty.usbserial-*', '/dev/tty.usbmodem*', '/dev/tty.usb*'],
        'unknown': []
    }

def get_linux_serial_ports() -> List[str]:
    """
    在Linux系统下获取所有可用的串口
    
    Returns:
        List[str]: 可用串口列表
    """
    ports = []
    
    # 优先检测USB串口设备（更可能用于手部控制器）
    usb_patterns = [
        '/dev/ttyUSB*',
        '/dev/ttyACM*',
        '/dev/tty.usbserial*',
        '/dev/tty.usbmodem*'
    ]
    
    # 然后检测系统串口（通常需要特殊权限）
    system_patterns = [
        '/dev/ttyS*'
    ]
    
    # 检测USB串口
    logger.info("检测USB串口设备...")
    for pattern in usb_patterns:
        try:
            found_ports = glob.glob(pattern)
            for port in found_ports:
                if os.path.exists(port) and check_linux_port_permissions(port):
                    ports.append(port)
                    logger.info(f"找到USB串口: {port}")
        except Exception as e:
            logger.debug(f"搜索模式 {pattern} 失败: {e}")
    
    # 如果USB串口不足，再检测系统串口
    if len(ports) < 2:
        logger.info("USB串口不足，检测系统串口...")
        for pattern in system_patterns:
            try:
                found_ports = glob.glob(pattern)
                for port in found_ports:
                    if os.path.exists(port):
                        # 对于系统串口，即使权限不足也添加到列表中，但标记为需要权限
                        if check_linux_port_permissions(port):
                            ports.append(port)
                            logger.info(f"找到系统串口: {port}")
                        else:
                            logger.warning(f"系统串口 {port} 权限不足，需要sudo权限")
                            # 可以选择是否添加权限不足的串口
                            # ports.append(port)
            except Exception as e:
                logger.debug(f"搜索模式 {pattern} 失败: {e}")
    
    # 去重并排序
    ports = sorted(list(set(ports)))
    
    # 记录检测结果
    if ports:
        logger.info(f"Linux串口检测完成，找到 {len(ports)} 个可用串口: {ports}")
    else:
        logger.warning("Linux串口检测完成，未找到可用串口")
        logger.info("建议:")
        logger.info("1. 检查USB设备是否正确连接")
        logger.info("2. 运行 'lsusb' 查看USB设备")
        logger.info("3. 运行 'ls -la /dev/ttyUSB* /dev/ttyACM*' 查看串口设备")
        logger.info("4. 检查用户权限: 'groups $USER'")
    
    return ports

def check_linux_port_permissions(port: str) -> bool:
    """
    检查Linux下串口的访问权限
    
    Args:
        port: 串口路径
        
    Returns:
        bool: 是否有访问权限
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(port):
            logger.debug(f"串口 {port} 不存在")
            return False
        
        # 检查是否为字符设备
        if not os.path.isdir(port):
            stat_info = os.stat(port)
            if not stat_info.st_mode & 0o170000 == 0o20000:  # 不是字符设备
                logger.debug(f"串口 {port} 不是字符设备")
                return False
        
        # 检查读取权限
        if not os.access(port, os.R_OK):
            logger.warning(f"串口 {port} 没有读取权限")
            logger.info(f"  解决方法: sudo chmod 644 {port}")
            return False
        
        # 检查写入权限
        if not os.access(port, os.W_OK):
            logger.warning(f"串口 {port} 没有写入权限")
            logger.info(f"  解决方法: sudo chmod 666 {port}")
            return False
            
        return True
        
    except Exception as e:
        logger.debug(f"检查串口 {port} 权限失败: {e}")
        return False

def get_available_ports() -> List[Dict]:
    """
    获取系统中所有可用的串口（跨平台）
    
    Returns:
        list: 可用串口列表，每个元素包含串口信息字典
    """
    ports = []
    system = get_system_type()
    
    try:
        if system == 'linux':
            # Linux系统：使用pyserial + 自定义检测
            linux_ports = get_linux_serial_ports()
            
            # 使用pyserial获取详细信息
            available_ports = serial.tools.list_ports.comports()
            port_info_map = {port.device: port for port in available_ports}
            
            for port_path in linux_ports:
                if check_linux_port_permissions(port_path):
                    port_info = {
                        'port': port_path,
                        'description': '',
                        'manufacturer': '',
                        'product': '',
                        'vid': None,
                        'pid': None
                    }
                    
                    # 尝试从pyserial获取详细信息
                    if port_path in port_info_map:
                        pyserial_port = port_info_map[port_path]
                        port_info.update({
                            'description': pyserial_port.description or '',
                            'manufacturer': pyserial_port.manufacturer or '',
                            'product': pyserial_port.product or '',
                            'vid': pyserial_port.vid,
                            'pid': pyserial_port.pid
                        })
                    
                    ports.append(port_info)
                    
        else:
            # Windows和其他系统：使用pyserial的标准方法
            available_ports = serial.tools.list_ports.comports()
            for port in available_ports:
                ports.append({
                    'port': port.device,
                    'description': port.description,
                    'manufacturer': port.manufacturer,
                    'product': port.product,
                    'vid': port.vid,
                    'pid': port.pid
                })
                
    except Exception as e:
        logger.error(f"获取串口列表失败: {e}")
    
    return ports

def quick_detect_ports() -> List[str]:
    """
    快速检测可用串口（跨平台）
    
    Returns:
        list: 可用串口列表
    """
    try:
        ports = []
        system = get_system_type()
        
        if system == 'linux':
            # Linux系统：使用自定义检测
            available_ports = get_linux_serial_ports()
        else:
            # Windows和其他系统：使用pyserial
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
        
        logger.info("检测到的串口:")
        for port in available_ports:
            logger.info(f"  {port}")
            ports.append(port)
        
        if not ports:
            logger.warning("未检测到任何串口")
        else:
            logger.info(f"可用串口: {ports}")
        
        return ports
        
    except Exception as e:
        logger.error(f"串口检测失败: {e}")
        return []

def test_port_connection(port: str, baudrate: int = 230400, timeout: int = 2) -> bool:
    """
    测试串口连接（跨平台）
    
    Args:
        port: 串口号
        baudrate: 波特率
        timeout: 超时时间
        
    Returns:
        bool: 连接是否成功
    """
    try:
        # Linux系统下检查权限
        system = get_system_type()
        if system == 'linux' and not check_linux_port_permissions(port):
            logger.warning(f"串口 {port} 权限不足，可能需要sudo权限或添加用户到dialout组")
            return False
        
        ser = serial.Serial(port, baudrate, timeout=timeout)
        ser.close()
        return True
    except Exception as e:
        logger.warning(f"串口 {port} 连接测试失败: {e}")
        return False

def get_default_ports() -> Dict[str, str]:
    """
    获取系统默认的串口配置
    
    Returns:
        Dict[str, str]: 默认串口配置
    """
    system = get_system_type()
    common_ports = get_common_ports()
    
    if system == 'windows':
        return {
            'left': 'COM5',
            'right': 'COM4'
        }
    elif system == 'linux':
        # Linux下使用常见的USB串口
        linux_ports = common_ports.get('linux', [])
        if len(linux_ports) >= 2:
            return {
                'left': linux_ports[1],  # 第二个串口作为左手
                'right': linux_ports[0]  # 第一个串口作为右手
            }
        elif len(linux_ports) == 1:
            return {
                'left': linux_ports[0],
                'right': linux_ports[0]
            }
        else:
            return {
                'left': '/dev/ttyUSB0',
                'right': '/dev/ttyUSB1'
            }
    else:
        # 其他系统使用通用配置
        return {
            'left': 'COM5',
            'right': 'COM4'
        }

def suggest_gaia_ports(ports: List[str]) -> Optional[Dict[str, str]]:
    """
    为 Gaia 手部控制器建议串口配置（跨平台）
    
    Args:
        ports: 可用串口列表
        
    Returns:
        dict: 建议的串口配置
    """
    if not ports:
        return None
    
    config = {
        'left': None,
        'right': None,
        'available': ports
    }
    
    system = get_system_type()
    default_ports = get_default_ports()
    
    # 如果只有一个串口，用于右手
    if len(ports) == 1:
        config['right'] = ports[0]
        config['left'] = ports[0]  # 单手模式
    # 如果有两个或更多串口
    elif len(ports) >= 2:
        # 尝试匹配默认配置
        if default_ports['right'] in ports:
            config['right'] = default_ports['right']
        else:
            config['right'] = ports[0]
            
        if default_ports['left'] in ports:
            config['left'] = default_ports['left']
        else:
            config['left'] = ports[1]
    
    return config

def auto_detect_gaia_ports() -> Optional[Dict[str, str]]:
    """
    自动检测 Gaia 手部控制器的串口（跨平台）
    
    Returns:
        dict: 检测到的串口配置
    """
    system = get_system_type()
    logger.info(f"=== 自动检测 Gaia 手部控制器串口 ({system.upper()}) ===")
    
    # 获取可用串口
    ports = quick_detect_ports()
    
    if not ports:
        logger.error("未检测到任何可用串口")
        
        # 提供系统特定的建议
        if system == 'linux':
            logger.info("Linux系统诊断建议:")
            logger.info("1. 检查USB设备连接:")
            logger.info("   lsusb")
            logger.info("   dmesg | tail")
            logger.info("")
            logger.info("2. 检查串口设备:")
            logger.info("   ls -la /dev/ttyUSB* /dev/ttyACM*")
            logger.info("   ls -la /dev/ttyS* | head -5")
            logger.info("")
            logger.info("3. 检查用户权限:")
            logger.info("   groups $USER")
            logger.info("   sudo usermod -a -G dialout $USER")
            logger.info("")
            logger.info("4. 临时解决权限问题:")
            logger.info("   sudo chmod 666 /dev/ttyUSB* /dev/ttyACM*")
            logger.info("")
            logger.info("5. 运行调试脚本:")
            logger.info("   chmod +x linux_debug.sh && ./linux_debug.sh")
        elif system == 'windows':
            logger.info("Windows系统建议:")
            logger.info("1. 确保设备已连接")
            logger.info("2. 检查设备管理器中的串口设备")
            logger.info("3. 安装必要的USB驱动")
        
        return None
    
    logger.info(f"可用串口数量: {len(ports)}")
    logger.info(f"可用串口列表: {ports}")
    
    # 测试串口连接
    working_ports = []
    for port in ports:
        logger.info(f"测试串口 {port}...")
        if test_port_connection(port):
            working_ports.append(port)
            logger.info(f"串口 {port} 连接测试成功")
        else:
            logger.warning(f"串口 {port} 连接测试失败")
    
    if not working_ports:
        logger.error("所有串口连接测试都失败")
        if system == 'linux':
            logger.info("Linux系统额外建议:")
            logger.info("1. 检查设备是否被其他程序占用:")
            logger.info("   lsof | grep tty")
            logger.info("2. 检查串口配置:")
            logger.info("   stty -F /dev/ttyUSB0")
            logger.info("3. 尝试不同的波特率")
        return None
    
    # 生成建议配置
    config = suggest_gaia_ports(working_ports)
    
    if config:
        logger.info(f"检测结果:")
        logger.info(f"  左手串口: {config['left']}")
        logger.info(f"  右手串口: {config['right']}")
        logger.info(f"  工作串口: {working_ports}")
        
        # 提供使用示例
        logger.info("使用示例:")
        logger.info("```python")
        logger.info("from src.core.hand import create_hand")
        logger.info("")
        logger.info("# 单手模式")
        logger.info(f"hand = create_hand('gaia', 'right', port='{config['right']}')")
        logger.info("")
        logger.info("# 双手模式")
        logger.info(f"hand = create_hand('gaia', 'double', left_port='{config['left']}', right_port='{config['right']}')")
        logger.info("```")
    
    return config

def find_gaia_hand_ports() -> Dict[str, str]:
    """
    查找可能的 Gaia 手部控制器串口（跨平台）
    
    Returns:
        dict: 包含可能的左右手串口
    """
    ports = get_available_ports()
    gaia_ports = {
        'left': None,
        'right': None,
        'available': []
    }
    
    system = get_system_type()
    default_ports = get_default_ports()
    
    logger.info(f"检测到的串口 ({system.upper()}):")
    for port_info in ports:
        port = port_info['port']
        description = port_info['description']
        manufacturer = port_info['manufacturer']
        product = port_info['product']
        
        logger.info(f"  {port}: {description}")
        if manufacturer:
            logger.info(f"    制造商: {manufacturer}")
        if product:
            logger.info(f"    产品: {product}")
        
        gaia_ports['available'].append(port)
        
        # 尝试识别左右手串口（基于常见的命名规则）
        if 'left' in description.lower() or 'l' in port.lower():
            gaia_ports['left'] = port
        elif 'right' in description.lower() or 'r' in port.lower():
            gaia_ports['right'] = port
    
    # 如果没有通过描述识别到，使用默认的常见串口
    if not gaia_ports['left'] and default_ports['left'] in gaia_ports['available']:
        gaia_ports['left'] = default_ports['left']
    if not gaia_ports['right'] and default_ports['right'] in gaia_ports['available']:
        gaia_ports['right'] = default_ports['right']
    
    # 如果还是没有，使用前两个可用串口
    if len(gaia_ports['available']) >= 2:
        if not gaia_ports['left']:
            gaia_ports['left'] = gaia_ports['available'][0]
        if not gaia_ports['right']:
            gaia_ports['right'] = gaia_ports['available'][1]
    
    return gaia_ports

def get_linux_permission_help() -> str:
    """
    获取Linux下串口权限设置的帮助信息
    
    Returns:
        str: 帮助信息
    """
    return """
Linux系统串口权限设置帮助:

1. 临时解决方案（需要每次重启后重新设置）:
   sudo chmod 666 /dev/ttyUSB*
   sudo chmod 666 /dev/ttyACM*

2. 永久解决方案（推荐）:
   a) 将当前用户添加到dialout组:
      sudo usermod -a -G dialout $USER
   
   b) 重新登录或重启系统
   
   c) 验证权限:
      groups $USER
      ls -la /dev/ttyUSB*

3. 创建udev规则（最推荐）:
   a) 创建规则文件:
      sudo nano /etc/udev/rules.d/99-serial.rules
   
   b) 添加以下内容:
      SUBSYSTEM=="tty", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="yyyy", MODE="0666"
      (将xxxx和yyyy替换为实际的vendor和product ID)
   
   c) 重新加载规则:
      sudo udevadm control --reload-rules
      sudo udevadm trigger

4. 检查设备信息:
   lsusb
   udevadm info -a -n /dev/ttyUSB0
"""

def print_system_info():
    """
    打印系统信息，用于调试
    """
    system = get_system_type()
    logger.info(f"操作系统: {system.upper()}")
    logger.info(f"Python版本: {platform.python_version()}")
    logger.info(f"pyserial版本: {serial.VERSION}")
    
    if system == 'linux':
        logger.info("Linux系统信息:")
        try:
            import subprocess
            result = subprocess.run(['lsb_release', '-a'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(result.stdout)
        except:
            pass
        
        logger.info("串口设备:")
        try:
            import subprocess
            result = subprocess.run(['ls', '-la', '/dev/ttyUSB*', '/dev/ttyACM*'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(result.stdout)
        except:
            pass 