from setuptools import setup, find_packages

# 读取README文件
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'A funcguard for Python.'

setup(
    name='funcguard',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='tinycen',
    author_email='sky_ruocen@qq.com',
    description='FuncGuard是一个Python库，提供函数执行超时控制、重试机制、HTTP请求封装和格式化打印工具。',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tinycen/funcguard',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,
    zip_safe=False,
)
