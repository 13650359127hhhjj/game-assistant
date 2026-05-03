#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块

提供统一的日志记录功能，支持：
- 多级别日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 日志文件输出
- 控制台彩色输出
- 日志格式自定义
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


# 全局日志器字典
_loggers = {}


def setup_logger(
    name: str = "GameAssistant",
    log_dir: str = "logs",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置并返回一个配置好的日志器
    
    Args:
        name: 日志器名称
        log_dir: 日志文件目录
        log_level: 日志级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的旧日志文件数量
        
    Returns:
        配置好的Logger对象
    """
    # 如果日志器已存在，直接返回
    if name in _loggers:
        return _loggers[name]
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带日志轮转）
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 保存到全局字典
    _loggers[name] = logger
    
    logger.info(f"日志系统初始化完成，日志文件: {log_file}")
    
    return logger


def get_logger(name: str = "GameAssistant") -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        Logger对象
    """
    # 如果日志器已存在，直接返回
    if name in _loggers:
        return _loggers[name]
    
    # 否则创建新的日志器
    return setup_logger(name)


class LoggerAdapter:
    """日志适配器，用于为特定模块提供定制化的日志记录"""
    
    def __init__(self, module_name: str):
        """
        初始化日志适配器
        
        Args:
            module_name: 模块名称
        """
        self.logger = get_logger()
        self.module_name = module_name
    
    def debug(self, message: str):
        """记录DEBUG级别日志"""
        self.logger.debug(f"[{self.module_name}] {message}")
    
    def info(self, message: str):
        """记录INFO级别日志"""
        self.logger.info(f"[{self.module_name}] {message}")
    
    def warning(self, message: str):
        """记录WARNING级别日志"""
        self.logger.warning(f"[{self.module_name}] {message}")
    
    def error(self, message: str):
        """记录ERROR级别日志"""
        self.logger.error(f"[{self.module_name}] {message}")
    
    def critical(self, message: str):
        """记录CRITICAL级别日志"""
        self.logger.critical(f"[{self.module_name}] {message}")


def log_function_call(func):
    """
    装饰器：记录函数调用
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        logger.debug(f"调用函数: {func_name}, 参数: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func_name} 执行完成")
            return result
        except Exception as e:
            logger.error(f"函数 {func_name} 执行出错: {str(e)}")
            raise
    
    return wrapper


def log_performance(func):
    """
    装饰器：记录函数执行时间
    
    Usage:
        @log_performance
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        start_time = datetime.now()
        logger.info(f"开始执行函数: {func_name}")
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            logger.info(f"函数 {func_name} 执行完成，耗时: {elapsed:.3f}秒")
            return result
        except Exception as e:
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            logger.error(f"函数 {func_name} 执行出错，耗时: {elapsed:.3f}秒, 错误: {str(e)}")
            raise
    
    return wrapper


# 初始化默认日志器
_default_logger = setup_logger()


if __name__ == "__main__":
    # 测试日志功能
    logger = setup_logger("TestLogger")
    
    logger.debug("这是一个调试信息")
    logger.info("这是一个信息")
    logger.warning("这是一个警告")
    logger.error("这是一个错误")
    logger.critical("这是一个严重错误")
    
    # 测试日志适配器
    adapter = LoggerAdapter("TestModule")
    adapter.info("模块日志测试")
    
    # 测试装饰器
    @log_performance
    def test_function():
        import time
        time.sleep(0.5)
        return "执行完成"
    
    result = test_function()
    print(f"结果: {result}")
