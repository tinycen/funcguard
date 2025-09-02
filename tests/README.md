# FuncGuard 测试说明

这个目录包含了FuncGuard库的所有测试用例。

## 测试文件结构

- `test_core.py` - 测试核心功能（timeout_handler和retry_function）
- `test_tools.py` - 测试工具函数（send_request）
- `run_tests.py` - 测试运行脚本
- `requirements-test.txt` - 测试依赖

## 运行测试

### 方法1：使用测试运行脚本
```bash
python tests/run_tests.py
```

### 方法2：使用unittest模块
```bash
# 运行所有测试
python -m unittest discover tests -v

# 运行特定测试文件
python -m unittest tests.test_core -v
python -m unittest tests.test_tools -v

# 运行特定测试类
python -m unittest tests.test_core.TestTimeoutHandler -v

# 运行特定测试方法
python -m unittest tests.test_core.TestTimeoutHandler.test_normal_execution -v
```

### 方法3：使用pytest（如果已安装）
```bash
pip install pytest
pytest tests/ -v
```

## 安装测试依赖

```bash
pip install -r tests/requirements-test.txt
```

## 测试覆盖率

可以使用coverage工具查看测试覆盖率：

```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # 生成HTML报告
```

## 测试内容

### 核心功能测试 (test_core.py)
- `TestTimeoutHandler`：测试函数超时控制
  - 正常执行
  - 超时处理
  - 参数传递
  - 关键字参数传递

- `TestRetryFunction`：测试函数重试机制
  - 首次成功
  - 重试后成功
  - 重试耗尽
  - 超时重试
  - 重试延迟

### 工具函数测试 (test_tools.py)
- `TestSendRequest`：测试HTTP请求功能
  - GET/POST请求
  - JSON响应
  - 文本响应
  - Response对象返回
  - 自动重试
  - 超时设置
  - 错误处理

## 添加新测试

当添加新功能时，请在相应的测试文件中添加对应的测试用例，并确保：
1. 测试函数名以`test_`开头
2. 使用`unittest.TestCase`作为基类
3. 使用断言方法验证结果
4. 对于外部依赖，使用`unittest.mock`进行模拟