from distutils.core import setup

setup(
    name='aopclient',
    version='1.0.5',
    author='Jim Barcelona, Arun Suresh',
    author_email='barce@me.com, arunvsuresh@gmail.com',
    packages=['aopclient', 'aopclient.tests'],
    install_requires=[
      'future',
    ],
    scripts=[],
    url='http://pypi.python.org/pypi/aopclient/',
    license='LICENSE',
    description='A client for interacting with the AOL Platform.',
    long_description=open('README.txt').read(),
)
 
