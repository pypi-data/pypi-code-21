from setuptools import setup


def readme():
	with open('README.rst') as f:
		return f.read()


setup(name='jk_sql',
	version='0.2017.10.20',
	description='This python module provides a uniform API to create, modify, read and write data to SQL tables in a database independent way.',
	author='Jürgen Knauth',
	author_email='pubsrc@binary-overflow.de',
	license='Apache 2.0',
	url='https://github.com/jkpubsrc/python-module-jk-fileaccess',
	download_url='https://github.com/jkpubsrc/python-module-jk-fileaccess/tarball/0.2017.10.7',
	keywords=[
		'file', 'filesystem', 'ssh', 'sftp', 'cifs', 'smb', 'iterating'
	],
	packages=[
		'jk_sql'
	],
	install_requires=[
	],
	include_package_data=True,
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python :: 3.5',
		'License :: OSI Approved :: Apache Software License'
	],
	long_description=readme(),
	zip_safe=False)

