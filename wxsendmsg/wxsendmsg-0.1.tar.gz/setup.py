#from distutils.core import setup
from setuptools import setup, find_packages

setup(
	name='wxsendmsg',
	version='0.1',
	description='Python module/library wxsendmsg.',
	long_description = open('README').read(),
	author='ding',
	author_email='dingyinggui@aliyun.com',
	license='MIT',
	url='http://www.shiranba.cn',
	platforms = ['any'],
	keywords=['Python','wxsendmsg'],
	#requires=['requests'],
	install_requires=['requests'],
	packages=['wxsendmsg'],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers',
		'Environment :: Console',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.0',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Topic :: Internet',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)

