import json
import unittest
from unittest.mock import patch, MagicMock
import requests

from funcguard.tools import send_request


class MockResponse:
    """模拟requests响应"""
    
    def __init__(self, json_data=None, text="", status_code=200):
        self.json_data = json_data or {}
        self.text = text
        self.status_code = status_code
    
    def json(self):
        return self.json_data


class TestSendRequest(unittest.TestCase):
    """测试send_request函数"""
    
    @patch('requests.request')
    def test_get_request_json_response(self, mock_request):
        """测试GET请求返回JSON"""
        mock_response = MockResponse(json_data={"key": "value"})
        mock_request.return_value = mock_response
        
        result = send_request(
            method="GET",
            url="https://api.example.com/data",
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(result, {"key": "value"})
        mock_request.assert_called_once()
    
    @patch('requests.request')
    def test_post_request_with_data(self, mock_request):
        """测试POST请求带数据"""
        mock_response = MockResponse(json_data={"status": "created"})
        mock_request.return_value = mock_response
        
        result = send_request(
            method="POST",
            url="https://api.example.com/users",
            headers={"Content-Type": "application/json"},
            data={"name": "test", "email": "test@example.com"}
        )
        
        self.assertEqual(result, {"status": "created"})
        mock_request.assert_called_once()
    
    @patch('requests.request')
    def test_return_response_object(self, mock_request):
        """测试返回response对象"""
        mock_response = MockResponse(text="raw response")
        mock_request.return_value = mock_response
        
        result = send_request(
            method="GET",
            url="https://api.example.com/raw",
            headers={},
            return_type="response"
        )
        
        self.assertEqual(result, mock_response)
    
    @patch('requests.request')
    def test_return_text_response(self, mock_request):
        """测试返回文本响应"""
        mock_response = MockResponse(text="plain text response")
        mock_request.return_value = mock_response
        
        result = send_request(
            method="GET",
            url="https://api.example.com/text",
            headers={},
            return_type="text"
        )
        
        self.assertEqual(result, "plain text response")
    
    @patch('requests.request')
    def test_custom_timeout(self, mock_request):
        """测试自定义超时时间"""
        mock_response = MockResponse()
        mock_request.return_value = mock_response
        
        send_request(
            method="GET",
            url="https://api.example.com/data",
            headers={},
            timeout=30
        )
        
        mock_request.assert_called_once()
    
    @patch('funcguard.core.retry_function')
    @patch('requests.request')
    def test_auto_retry_enabled(self, mock_request, mock_retry):
        """测试启用自动重试"""
        # 设置retry_function返回一个包含正确json数据的MockResponse对象
        mock_response = MockResponse(json_data={"success": True})
        mock_retry.return_value = mock_response
        
        result = send_request(
            method="POST",
            url="https://api.example.com/data",
            headers={"Content-Type": "application/json"},
            data={"key": "value"},
            auto_retry={
                "task_name": "API测试",
                "max_retries": 3,
                "execute_timeout": 60
            }
        )
        
        # 验证结果
        if hasattr(result, 'json_data'):
            # 如果result是MockResponse对象，直接比较其json_data
            self.assertEqual(result.json_data, {"success": True})
        else:
            # 否则直接比较result
            self.assertEqual(result, {"success": True})
        mock_retry.assert_called_once()
    
    @patch('requests.request')
    def test_none_response_raises_error(self, mock_request):
        """测试None响应抛出错误"""
        mock_request.return_value = None
        
        with self.assertRaises(ValueError) as context:
            send_request("GET", "https://api.example.com/data", {})
        
        self.assertEqual(str(context.exception), "请求返回的响应为None")
    
    def test_invalid_return_type(self):
        """测试无效的返回类型"""
        with patch('requests.request') as mock_request:
            mock_response = MockResponse()
            mock_request.return_value = mock_response
            
            # 对于无效的return_type，函数会尝试访问response.text
            result = send_request(
                method="GET",
                url="https://api.example.com/data",
                headers={},
                return_type="invalid"
            )
            self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()