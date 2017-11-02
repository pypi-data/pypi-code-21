from setuptools import setup, find_packages

setup(
	name = 'icheckin',
	packages = find_packages(),
	install_requires = [
		'requests==2.18.1',
		'click==6.7',
		'halo==0.0.7'
	],
	version = '1.3.5',
	description = 'A console application for Sunway University\'s iCheckin',
	author = 'Marcus Mu',
	author_email = 'chunkhang@gmail.com',
	license = 'UNLICENSE',
	url = 'https://github.com/chunkhang/icheckin',
	keywords = [
		'icheckin', 
		'sunway'
	], 
	classifiers = [
		'Intended Audience :: End Users/Desktop',
		'Programming Language :: Python :: 3 :: Only',
		'Environment :: Console'
	],
	entry_points = {
		'console_scripts': [
			'icheckin=icheckin.icheckin:cli'
		]
	}
)