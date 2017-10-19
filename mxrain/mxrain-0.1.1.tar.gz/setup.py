from setuptools import setup, find_packages
"""
打包时用的setup必须引入
"""


VERSION = '0.1.1'

setup(
    name='mxrain',
    version=VERSION,
    description='一个小的测试项目',
    long_description='我的个人兴趣',
    classifiers=[],
    keywords='python cli mx rain',
    author='rain.xia',
    author_email='xjjrain2015@126.com',
    url='',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
    entry_pointers={
        'console_scripts': [
            'mxrain=mxrainsrc.mxrain'
        ]
    }
)
