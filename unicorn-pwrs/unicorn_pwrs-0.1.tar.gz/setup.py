from setuptools import setup, find_packages
from codecs import open #  for consistent encoding
from os import path

fullpath_package_root = path.abspath(path.dirname(__file__))
readme = path.join(fullpath_package_root, 'README.rst')

with open(readme, encoding='utf-8') as r:
	README_contents=r.read()


setup(
	name='unicorn_pwrs',
	version='0.1',
	description="You only live once.",
	long_description=README_contents,

	author='A.M. \'Thomas\'',
	author_email='thomasoflight@lightfaced.org',
	url='https://github.com/thomasoflight/unicorn_pwrs',
	license='APACHE 2.0',

	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Topic :: Software Development',
		'Operating System :: MacOS',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		],

	keywords='resume experimental command-line terminal',
	packages=find_packages(),
	install_requires=['simpleaudio'],
	extras_require={},
	package_dir={'unicorn_pwrs': 'unicorn_pwrs'},
	package_data={
		'unicorn_pwrs':[
			'data/cover.txt',
			'data/cv.txt',
			'data/reference.txt',
			'data/unicorn_bleep.wav',
			'data/unicorn_click.wav'
		]
	},

	entry_points={
		'console_scripts': [
			'unicorn_pwrs = unicorn_pwrs.unicorn_pwrs:main',
		],
	}

)
