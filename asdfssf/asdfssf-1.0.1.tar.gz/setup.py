import codecs
import os
import sys

try:
	from setuptools import setup
except:
	from distuils.core import setup

NAME = "asdfssf"
"""
名字，一般放你包的名字即可
"""
 
PACKAGES = ["asdfssf",]
"""
包含的包，可以多个，这是一个列表
"""
 
DESCRIPTION = "this is a test package for packing python liberaries tutorial."
"""
关于这个包的描述
"""
 
LONG_DESCRIPTION = "test"
"""
参见read方法说明
"""
 
KEYWORDS = "test python package"
"""
关于当前包的一些关键字，方便PyPI进行分类。
"""
 
AUTHOR = "MitchellChu"
"""
谁是这个包的作者，写谁的名字吧
我是MitchellChu，自然这里写的是MitchellChu
"""
 
AUTHOR_EMAIL = "youremail@email.com"
"""
作者的邮件地址
"""
 
URL = "http://blog.useasp.net/"
"""
你这个包的项目地址，如果有，给一个吧，没有你直接填写在PyPI你这个包的地址也是可以的
"""
 
VERSION = "1.0.1"
"""
当前包的版本，这个按你自己需要的版本控制方式来
"""
 
LICENSE = "MIT"
"""
授权方式，我喜欢的是MIT的方式，你可以换成其他方式
"""
 
setup(
	name = NAME,
	version = VERSION,
	description = DESCRIPTION,
	long_description = LONG_DESCRIPTION,
	classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
	keywords = KEYWORDS,
	author = AUTHOR,
	author_email = AUTHOR_EMAIL,
	url = URL,
	license = LICENSE,
	packages = PACKAGES,
	include_package_data=True,
	zip_safe=True,
)
 