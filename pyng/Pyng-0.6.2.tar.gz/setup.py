from distutils.core import setup
import os
import re

# set the version number from the most recent CHANGES entry
vxxx = re.compile(r'^v(.*?),')
for line in open(os.path.join(os.path.dirname(__file__), "CHANGES.txt")):
    match = vxxx.search(line)
    if match:
        version = match.group(1)
    # but keep looping: last assignment wins

setup(
    name='Pyng',
    version=version,
    author='Nat Goodspeed',
    author_email='nat.cognitoy@gmail.com',
    packages=['pyng', 'pyng.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/Pyng/',
    license='LICENSE.txt',
    description='Yet another collection of Python utility functions',
    long_description=open('README.txt').read(),
)
