#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地址检测工具模块

提供获取本机IP地址、公网IP地址以及IP地址验证等功能。
"""

import socket
import requests


def get_local_ip():
    """
    获取本机局域网IP地址
    
    :return: 本机IP地址字符串，如果获取失败返回None
    """
    try:
        # 创建一个UDP socket来获取本机IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到一个外部地址（不需要真正连接成功）
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception as e:
        print(f"获取本机IP地址失败: {e}")
        return None


def get_public_ip():
    """
    获取本机公网IP地址
    
    :return: 公网IP地址字符串，如果获取失败返回None
    """
    try:
        # 使用多个IP查询服务作为备选
        ip_services = [
            'https://api.ipify.org',
            'https://ipapi.co/ip/',
            'https://ifconfig.me/ip',
            'https://api.myip.com'
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # 验证是否为有效的IP地址格式
                    if is_valid_ip(ip):
                        return ip
            except:
                continue
                
        return None
    except Exception as e:
        print(f"获取公网IP地址失败: {e}")
        return None


def is_valid_ip(ip_string):
    """
    验证字符串是否为有效的IP地址
    
    :param ip_string: 要验证的IP地址字符串
    :return: 如果是有效的IP地址返回True，否则返回False
    """
    try:
        parts = ip_string.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
                
        return True
    except:
        return False


def get_ip_info():
    """
    获取本机IP地址信息（包括局域网IP和公网IP）
    
    :return: 包含IP信息的字典
    """
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    ip_info = {
        'local_ip': local_ip,
        'public_ip': public_ip,
        'hostname': socket.gethostname()
    }
    
    return ip_info