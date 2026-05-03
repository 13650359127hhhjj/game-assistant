#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能游戏错误诊断与资源下载辅助系统
项目入口文件

作者：小米激励计划申请者
版本：1.0.0
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from utils.logger import setup_logger
import tkinter as tk


def main():
    """主函数，启动应用程序"""
    # 设置日志系统
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("智能游戏错误诊断与资源下载辅助系统启动")
    logger.info("=" * 50)
    
    try:
        # 创建主窗口
        root = tk.Tk()
        app = MainWindow(root)
        logger.info("应用程序初始化成功")
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}")
        raise
    finally:
        logger.info("应用程序已退出")


if __name__ == "__main__":
    main()
