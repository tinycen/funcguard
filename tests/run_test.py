#!/usr/bin/env python3
"""
测试运行脚本
运行所有测试用例
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入测试模块
from tests.test_core import TestTimeoutHandler, TestRetryFunction
from tests.test_tools import TestSendRequest


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTimeoutHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestRetryFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestSendRequest))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)