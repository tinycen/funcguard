import time
import unittest
from unittest.mock import patch

from funcguard.core import timeout_handler, retry_function


class TestTimeoutHandler(unittest.TestCase):
    """测试timeout_handler函数"""
    
    def test_normal_execution(self):
        """测试正常执行的函数"""
        def quick_function():
            time.sleep(0.1)
            return "success"
        
        result = timeout_handler(quick_function, execution_timeout=2)
        self.assertEqual(result, "success")
    
    def test_timeout_execution(self):
        """测试超时的函数"""
        def slow_function():
            time.sleep(2)
            return "should not reach here"
        
        from funcguard.core import FuncguardTimeoutError
        with self.assertRaises(FuncguardTimeoutError) as context:
            timeout_handler(slow_function, execution_timeout=1)
        
        self.assertIn("执行时间超过 1 秒", str(context.exception))
    
    def test_function_with_args(self):
        """测试带参数的函数"""
        def add_numbers(a, b):
            return a + b
        
        result = timeout_handler(add_numbers, args=(3, 4), execution_timeout=2)
        self.assertEqual(result, 7)
    
    def test_function_with_kwargs(self):
        """测试带关键字参数的函数"""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        result = timeout_handler(greet, kwargs={"name": "World", "greeting": "Hi"}, execution_timeout=2)
        self.assertEqual(result, "Hi, World!")


class TestRetryFunction(unittest.TestCase):
    """测试retry_function函数"""
    
    def test_successful_first_try(self):
        """测试第一次就成功的函数"""
        def always_success():
            return "success"
        
        result = retry_function(always_success, max_retries=2, task_name="test")
        self.assertEqual(result, "success")
    
    def test_retry_until_success(self):
        """测试重试后成功的函数"""
        attempts = []
        
        def sometimes_fail():
            attempts.append(len(attempts))
            if len(attempts) < 2:
                raise ValueError("Not yet")
            return "finally success"
        
        result = retry_function(sometimes_fail, max_retries=2, task_name="test")
        self.assertEqual(result, "finally success")
        self.assertEqual(len(attempts), 2)
    
    def test_exhaust_all_retries(self):
        """测试耗尽所有重试次数"""
        def always_fail():
            raise RuntimeError("Always fails")
        
        with self.assertRaises(RuntimeError) as context:
            retry_function(always_fail, max_retries=2, task_name="test")
        
        self.assertEqual(str(context.exception), "Always fails")
    
    def test_timeout_in_retry(self):
        """测试重试中的超时处理"""
        def timeout_function():
            time.sleep(2)
            return "should timeout"
        
        # retry_function会在重试耗尽后抛出最后的异常
        from funcguard.core import FuncguardTimeoutError
        with self.assertRaises(FuncguardTimeoutError):
            retry_function(timeout_function, max_retries=1, execute_timeout=1, task_name="test")
    
    @patch('time.sleep')
    def test_retry_with_custom_delay(self, mock_sleep):
        """测试重试延迟"""
        def always_fail():
            raise ValueError("test")
        
        with self.assertRaises(ValueError):
            retry_function(always_fail, max_retries=2, task_name="test")
        
        # 验证sleep被调用了正确的次数
        self.assertEqual(mock_sleep.call_count, 1)


if __name__ == '__main__':
    unittest.main()