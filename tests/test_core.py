#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能模块单元测试

本测试文件包含对错误诊断和资源下载模块的单元测试，
确保各核心功能的正确性。
"""

import unittest
import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.error_detector import ErrorDetector
from core.resource_downloader import ResourceDownloader


class TestErrorDetector(unittest.TestCase):
    """错误诊断器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = ErrorDetector()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.error_rules)
        self.assertGreater(len(self.detector.error_rules), 0)
    
    def test_diagnose_memory_error(self):
        """测试内存错误诊断"""
        error_info = "Access violation at 0x00000000"
        results = self.detector.diagnose(error_info)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['title'], '内存访问错误')
    
    def test_diagnose_directx_error(self):
        """测试DirectX错误诊断"""
        error_info = "DXGI_ERROR_DEVICE_REMOVED"
        results = self.detector.diagnose(error_info)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # 检查是否匹配到DirectX相关错误
        titles = [r['title'] for r in results]
        self.assertTrue(any('DirectX' in t or '显卡' in t for t in titles))
    
    def test_diagnose_dll_error(self):
        """测试DLL缺失错误诊断"""
        error_info = "vcruntime140.dll is missing"
        results = self.detector.diagnose(error_info)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['title'], 'DLL文件缺失')
    
    def test_diagnose_unknown_error(self):
        """测试未知错误诊断"""
        error_info = "some unknown error message xyz123"
        results = self.diagnose(error_info)
        
        self.assertIsInstance(results, list)
        # 未知错误应该返回通用建议
        self.assertEqual(results[0]['title'], '未知错误')
    
    def test_confidence_range(self):
        """测试置信度范围"""
        error_info = "access violation memory error"
        results = self.detector.diagnose(error_info)
        
        for result in results:
            self.assertGreaterEqual(result['confidence'], 0)
            self.assertLessEqual(result['confidence'], 100)
    
    def test_custom_rule(self):
        """测试添加自定义规则"""
        patterns = [r"custom.*error", r"TEST_ERROR_CODE"]
        result = self.detector.add_custom_rule(
            patterns=patterns,
            title="自定义错误",
            cause="自定义测试错误",
            solution="这是测试解决方案"
        )
        
        self.assertTrue(result)
        
        # 验证规则已添加
        test_error = "TEST_ERROR_CODE 12345"
        results = self.detector.diagnose(test_error)
        
        titles = [r['title'] for r in results]
        self.assertIn('自定义错误', titles)
    
    def test_invalid_regex(self):
        """测试无效正则表达式"""
        patterns = [r"[invalid"]  # 无效的正则表达式
        
        result = self.detector.add_custom_rule(
            patterns=patterns,
            title="测试",
            cause="测试",
            solution="测试"
        )
        
        self.assertFalse(result)
    
    def test_get_statistics(self):
        """测试统计信息获取"""
        stats = self.detector.get_error_statistics()
        
        self.assertIn('total_rules', stats)
        self.assertIn('categories', stats)
        self.assertIn('version', stats)
        self.assertGreater(stats['total_rules'], 0)


class TestResourceDownloader(unittest.TestCase):
    """资源下载器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.downloader = ResourceDownloader()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.downloader)
        self.assertIsNotNone(self.downloader.resource_db)
        self.assertGreater(len(self.downloader.resource_db), 0)
    
    def test_search_by_keyword(self):
        """测试关键词搜索"""
        results = self.downloader.search("补丁")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('name', result)
            self.assertIn('type', result)
            self.assertIn('size', result)
            self.assertIn('source', result)
    
    def test_search_by_type(self):
        """测试按类型搜索"""
        results = self.downloader.search("游戏", resource_type="MOD")
        
        self.assertIsInstance(results, list)
        for result in results:
            self.assertEqual(result['type'], 'MOD')
    
    def test_search_no_results(self):
        """测试无结果搜索"""
        results = self.downloader.search("不存在的内容xyz123")
        
        self.assertIsInstance(results, list)
        # 应该有备选结果
        self.assertGreater(len(results), 0)
    
    def test_search_empty_keyword(self):
        """测试空关键词搜索"""
        results = self.downloader.search("")
        
        self.assertIsInstance(results, list)
    
    def test_get_resource_info(self):
        """测试获取资源详情"""
        info = self.downloader.get_resource_info("PATCH_001")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], '游戏优化补丁 v2.5')
        self.assertEqual(info['type'], '补丁')
    
    def test_get_resource_info_not_found(self):
        """测试获取不存在的资源"""
        info = self.downloader.get_resource_info("NOT_EXIST")
        
        self.assertIsNone(info)
    
    def test_download_success(self):
        """测试成功下载"""
        result = self.downloader.download("PATCH_001", "/tmp/test")
        
        self.assertTrue(result)
        
        # 检查下载历史
        history = self.downloader.get_download_history()
        self.assertGreater(len(history), 0)
    
    def test_download_failure(self):
        """测试失败下载"""
        result = self.downloader.download("NOT_EXIST", "/tmp/test")
        
        self.assertFalse(result)
    
    def test_clear_history(self):
        """测试清空历史记录"""
        # 先下载一些资源
        self.downloader.download("PATCH_001", "/tmp/test1")
        self.downloader.download("PATCH_002", "/tmp/test2")
        
        # 清空历史
        self.downloader.clear_download_history()
        
        history = self.downloader.get_download_history()
        self.assertEqual(len(history), 0)
    
    def test_get_statistics(self):
        """测试统计信息"""
        stats = self.downloader.get_statistics()
        
        self.assertIn('total_resources', stats)
        self.assertIn('total_downloads', stats)
        self.assertIn('resource_types', stats)
        self.assertIn('average_rating', stats)
        self.assertGreater(stats['total_resources'], 0)
    
    def test_get_recommendations(self):
        """测试推荐资源"""
        recommendations = self.downloader.get_recommendations(count=3)
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertIn('name', rec)
            self.assertIn('rating', rec)
            self.assertIn('download_count', rec)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestErrorDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceDownloader))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
