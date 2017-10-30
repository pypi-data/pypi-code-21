from distutils.core import setup

setup(
    name='Pyng',
    version='0.6.0',
    author='Nat Goodspeed',
    author_email='nat.cognitoy@gmail.com',
    packages=['pyng', 'pyng.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/Pyng/',
    license='LICENSE.txt',
    description='Yet another collection of Python utility functions',
    long_description=open('README.txt').read(),
)
