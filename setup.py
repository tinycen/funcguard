import os
from setuptools import setup, find_packages

# 读取README文件
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'A funcguard for Python.'

root_dir = os.path.dirname(__file__)

with open(os.path.join(root_dir, "requirements.txt"), encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

with open(os.path.join(root_dir, "funcguard", ".version"), encoding="utf-8") as fh:
    version = "v" + fh.read().strip()

setup(
    name='funcguard',
    version=version,
    packages=find_packages(),
    install_requires=requirements,
    author='tinycen',
    author_email='sky_ruocen@qq.com',
    description='FuncGuard是一个Python库，提供函数执行超时控制、重试机制、HTTP请求封装和格式化打印工具。',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tinycen/funcguard',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,
    zip_safe=False,
)
