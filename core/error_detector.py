#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误诊断模块

本模块实现游戏错误的智能诊断功能，通过分析用户输入的错误信息，
匹配内置的错误规则库，返回可能的错误原因和解决方案。
"""

import re
import time
from typing import List, Dict, Optional
from utils.logger import get_logger


class ErrorDetector:
    """游戏错误诊断器类"""
    
    def __init__(self):
        """初始化错误诊断器"""
        self.logger = get_logger(__name__)
        self._init_error_rules()
        self.logger.info("错误诊断器初始化完成")
    
    def _init_error_rules(self):
        """初始化错误规则库"""
        # 错误规则库，包含错误模式、可能原因和解决方案
        self.error_rules = [
            {
                "patterns": [
                    r"0[xX]0*1\d{7,}",  # 内存地址格式
                    r"access\s+violation",
                    r"内存访问冲突",
                    r"Memory\s+access\s+violation"
                ],
                "title": "内存访问错误",
                "cause": "程序尝试访问无效的内存地址，可能是由于内存损坏、指针错误或驱动程序问题导致",
                "solution": "1. 更新显卡驱动至最新版本\n2. 检查游戏完整性，验证文件是否损坏\n3. 关闭后台运行的不兼容程序\n4. 以管理员权限运行游戏\n5. 检查内存是否存在问题"
            },
            {
                "patterns": [
                    r"dxgi_error",
                    r"directx\s+error",
                    r"DirectX\s+.*错误",
                    r"DX\d+.*错误"
                ],
                "title": "DirectX错误",
                "cause": "DirectX组件缺失或损坏，可能是显卡驱动问题或DirectX运行时环境异常",
                "solution": "1. 重新安装DirectX最终用户运行时\n2. 更新显卡驱动程序\n3. 使用dxdiag检查DirectX状态\n4. 更新Windows系统补丁"
            },
            {
                "patterns": [
                    r"vcruntime.*dll",
                    r"msvcp.*dll",
                    r"缺少.*dll",
                    r"missing\s+dll"
                ],
                "title": "DLL文件缺失",
                "cause": "Visual C++运行库或其他必要的动态链接库文件缺失或损坏",
                "solution": "1. 安装Visual C++ 2015-2022运行库\n2. 使用系统文件检查器修复：sfc /scannow\n3. 重新安装游戏\n4. 检查杀毒软件是否误删系统文件"
            },
            {
                "patterns": [
                    r"shader\s+error",
                    r"着色器.*错误",
                    r"shader\s+model"
                ],
                "title": "着色器错误",
                "cause": "显卡着色器编译失败，可能由于驱动版本不兼容或图形API问题",
                "solution": "1. 更新显卡驱动至最新版本\n2. 降低游戏图形设置\n3. 验证游戏文件完整性\n4. 检查显卡是否支持所需着色器版本"
            },
            {
                "patterns": [
                    r"out\s+of\s+memory",
                    r"内存不足",
                    r"insufficient\s+memory"
                ],
                "title": "内存不足错误",
                "cause": "系统可用内存不足，可能是后台程序占用过多内存或游戏内存泄漏",
                "solution": "1. 关闭不必要的后台程序\n2. 增加虚拟内存大小\n3. 检查是否存在内存泄漏\n4. 升级物理内存"
            },
            {
                "patterns": [
                    r"network\s+error",
                    r"网络.*错误",
                    r"连接.*失败",
                    r"connection\s+failed"
                ],
                "title": "网络连接错误",
                "cause": "网络连接异常，可能是服务器问题、网络设置或防火墙阻止",
                "solution": "1. 检查网络连接状态\n2. 确认游戏服务器是否在线\n3. 检查防火墙和杀毒软件设置\n4. 尝试更换网络环境\n5. 使用网络加速器"
            },
            {
                "patterns": [
                    r"disk\s+error",
                    r"磁盘.*错误",
                    r"storage\s+.*error"
                ],
                "title": "磁盘读写错误",
                "cause": "硬盘读写失败，可能是硬盘损坏、磁盘空间不足或存储设备问题",
                "solution": "1. 检查硬盘剩余空间\n2. 扫描硬盘坏道\n3. 更换游戏安装目录\n4. 检查硬盘健康状态"
            },
            {
                "patterns": [
                    r"graphics\s+.*error",
                    r"显卡.*错误",
                    r"GPU\s+.*error"
                ],
                "title": "显卡错误",
                "cause": "显卡相关错误，可能由于驱动问题、过热或硬件故障",
                "solution": "1. 更新显卡驱动\n2. 降低显卡温度，清理散热器\n3. 检查显卡是否超频\n4. 如有问题，考虑更换显卡"
            },
            {
                "patterns": [
                    r"audio\s+.*error",
                    r"音频.*错误",
                    r"sound\s+.*error"
                ],
                "title": "音频错误",
                "cause": "音频设备或驱动出现问题，可能是声卡驱动或音频服务异常",
                "solution": "1. 更新声卡驱动\n2. 检查默认音频设备设置\n3. 重启Windows音频服务\n4. 检查音频设备连接"
            },
            {
                "patterns": [
                    r"crash",
                    r"崩溃",
                    r"crashed",
                    r"程序终止"
                ],
                "title": "程序崩溃",
                "cause": "程序异常终止，可能由于兼容性问题、硬件故障或软件冲突",
                "solution": "1. 查看崩溃日志文件\n2. 以兼容模式运行\n3. 更新相关驱动程序\n4. 检查系统兼容性\n5. 联系游戏官方支持"
            },
            {
                "patterns": [
                    r"timeout",
                    r"超时",
                    r"timed?\s*out"
                ],
                "title": "操作超时",
                "cause": "操作在规定时间内未完成，可能是网络延迟或系统响应慢",
                "solution": "1. 检查网络连接质量\n2. 增加操作超时等待时间\n3. 关闭占用带宽的应用\n4. 更换更快的网络环境"
            },
            {
                "patterns": [
                    r"permission\s+denied",
                    r"权限不足",
                    r"拒绝访问",
                    r"access\s+denied"
                ],
                "title": "权限错误",
                "cause": "程序没有足够的权限执行操作，可能是UAC限制或文件权限问题",
                "solution": "1. 以管理员身份运行程序\n2. 修改文件或文件夹权限\n3. 关闭UAC进行测试\n4. 检查安全软件设置"
            },
            {
                "patterns": [
                    r"display\s+.*error",
                    r"显示.*错误",
                    r"screen\s+.*error"
                ],
                "title": "显示错误",
                "cause": "显示相关问题，可能是分辨率、刷新率或显示适配器问题",
                "solution": "1. 调整游戏分辨率设置\n2. 更新显示适配器驱动\n3. 检查显示器连接\n4. 还原显示设置默认值"
            },
            {
                "patterns": [
                    r"anti-cheat",
                    r"反作弊",
                    r"easy\s*anticheat",
                    r"battleeye"
                ],
                "title": "反作弊系统错误",
                "cause": "游戏反作弊系统检测到异常或与系统组件冲突",
                "solution": "1. 重新安装游戏反作弊组件\n2. 关闭杀毒软件后重新尝试\n3. 确保系统时间和时区正确\n4. 以管理员权限运行游戏启动器"
            },
            {
                "patterns": [
                    r"font\s+.*error",
                    r"字体.*错误",
                    r"missing\s+font"
                ],
                "title": "字体错误",
                "cause": "游戏必需的字体文件缺失或损坏",
                "solution": "1. 安装游戏所需字体包\n2. 修复系统字体库\n3. 重新安装游戏\n4. 从其他电脑复制字体文件"
            }
        ]
        
        self.logger.info(f"已加载 {len(self.error_rules)} 条错误规则")
    
    def diagnose(self, error_info: str) -> List[Dict]:
        """
        诊断错误信息
        
        Args:
            error_info: 用户输入的错误信息
            
        Returns:
            诊断结果列表，每个元素包含title、cause、solution、confidence
        """
        self.logger.info(f"开始诊断错误信息: {error_info[:50]}...")
        
        # 模拟诊断过程（实际应用中可能需要更复杂的分析）
        time.sleep(0.5)
        
        results = []
        error_info_lower = error_info.lower()
        
        for rule in self.error_rules:
            for pattern in rule['patterns']:
                try:
                    if re.search(pattern, error_info_lower, re.IGNORECASE):
                        result = {
                            'title': rule['title'],
                            'cause': rule['cause'],
                            'solution': rule['solution'],
                            'confidence': self._calculate_confidence(pattern, error_info_lower)
                        }
                        results.append(result)
                        self.logger.info(f"匹配到错误规则: {rule['title']}")
                        break
                except re.error as e:
                    self.logger.warning(f"正则表达式错误: {pattern}, {str(e)}")
        
        # 如果没有匹配到任何规则，返回通用建议
        if not results:
            results.append({
                'title': '未知错误',
                'cause': '未能识别具体错误类型，建议提供更详细的错误信息',
                'solution': '1. 请提供完整的错误信息和错误代码\n2. 尝试重启游戏或电脑\n3. 检查游戏官方论坛是否有类似问题\n4. 联系游戏技术支持获取帮助',
                'confidence': 30
            })
            self.logger.warning("未匹配到任何错误规则")
        
        # 按置信度排序
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        self.logger.info(f"诊断完成，找到 {len(results)} 个可能的原因")
        return results[:5]  # 最多返回5个结果
    
    def _calculate_confidence(self, pattern: str, error_info: str) -> int:
        """
        计算匹配置信度
        
        Args:
            pattern: 匹配模式
            error_info: 错误信息
            
        Returns:
            置信度（0-100）
        """
        # 基础置信度
        base_confidence = 70
        
        # 根据错误信息长度调整
        if len(error_info) > 100:
            base_confidence += 10
        
        # 根据模式复杂度调整
        if len(pattern) > 20:
            base_confidence += 5
        
        # 添加随机因素模拟真实场景
        import random
        base_confidence += random.randint(-10, 10)
        
        # 限制置信度范围
        return max(50, min(95, base_confidence))
    
    def add_custom_rule(self, patterns: List[str], title: str, cause: str, solution: str) -> bool:
        """
        添加自定义错误规则
        
        Args:
            patterns: 匹配模式列表
            title: 错误标题
            cause: 可能原因
            solution: 解决方案
            
        Returns:
            是否添加成功
        """
        try:
            # 验证正则表达式
            for pattern in patterns:
                re.compile(pattern, re.IGNORECASE)
            
            # 添加新规则
            new_rule = {
                'patterns': patterns,
                'title': title,
                'cause': cause,
                'solution': solution
            }
            self.error_rules.append(new_rule)
            
            self.logger.info(f"添加自定义规则成功: {title}")
            return True
            
        except re.error as e:
            self.logger.error(f"添加自定义规则失败，正则表达式错误: {str(e)}")
            return False
    
    def get_error_statistics(self) -> Dict:
        """
        获取错误规则统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_rules': len(self.error_rules),
            'categories': len(set(rule['title'] for rule in self.error_rules)),
            'version': '1.0.0'
        }
