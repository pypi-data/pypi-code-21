import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('Pysitron/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='pysitron',
    author='Jackie Vincent Larsen',
    author_email='jackie.v.larsen@gmail.com',
    version=version,
    url='https://github.com/jVinc/Pysitron',
    download_url='https://github.com/jVinc/Pysitron/tree/v0.0.3.8',
    packages=['pysitron'],
    description='A framework for building desktop applications in Python using web technologies',
    keywords = ['app-development', 'desktop', 'web'],
    install_requires=[
        'werkzeug',
        'jinja2',
        'cefpython3'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)