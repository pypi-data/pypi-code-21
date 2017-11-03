from distutils.core import setup

setup(
    name='lockboxcli',
    version='0.0.1',
    author='Jim Barcelona',
    author_email='barce@me.com',
    packages=['lockboxcli', 'lockboxcli.tests'],
    install_requires=[
      'future',
    ],
    scripts=[],
    url='http://pypi.python.org/pypi/lockboxcli/',
    license='LICENSE',
    description='A client for interacting with Lockbox, an aws lambda for handling server secrets.',
    long_description=open('README.txt').read(),
)
 
