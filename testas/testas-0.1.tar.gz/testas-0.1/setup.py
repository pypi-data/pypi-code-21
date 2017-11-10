from setuptools import setup, find_packages
from distutils.core import setup
setup(
    name='testas',
    packages=['testas'],
    version='0.1',
    description='A simple lib that prints out hello world',
    author='Abhijit Sen',
    author_email='abhijit.sen@hotmail.com',
    url='https://github.com/abhisen/',
    download_url='https://github.com/abhisen/',
    keywords=['dev3l', 'archetype', 'pypi', 'package'],  # arbitrary keywords
    install_requires=[
        'pytest==2.9.2'
             ],
    classifiers=[],
    entry_points={
        'console_scripts': [
            'hello_world = package_archetype.hello_world:print_hello_world'
        ]},
)
