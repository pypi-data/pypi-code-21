from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
	name='Pabiana',
	version='0.1.2',
	packages=find_packages(),
	install_requires=['pip>=9.0.1', 'pyzmq>=16.0.2'],
	setup_requires=['pytest-runner>=2.12.1'],
	tests_require=['pytest>=3.2.2'],
	zip_safe=False,
	
	url='https://github.com/kankiri/pabiana',
	author='Alexander Schöberl',
	author_email='alexander.schoeberl@gmail.com',
	description='A minimalistic framework to build distributed cognitive applications based on ØMQ',
	long_description=open(path.join(here, 'README.md')).read(),
	keywords=['framework', 'cognitive', 'distributed', 'ØMQ'],
	license='MIT'
)
