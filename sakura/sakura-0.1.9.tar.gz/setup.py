from setuptools import setup

setup(
    name='sakura',
    packages=['sakura'],
    version='0.1.9',
    description='sakura',
    author='None',
    author_email='None',
    maintainer='sakura',
    maintainer_email='sakura@nonono.rocks',
    url='https://github.com/nevermoreluo/sakura',
    download_url='https://github.com/nevermoreluo/sakura/archive/master.zip',
    install_requires=[
        'wheel>=0.30.0',
        'pycrypto>=2.6.1',
        'python-dateutil>=2.6.1',
        'pytz==2017.2',
        'psutil>=5.3.1',
        'protobuf>=3.4.0',
        'tornado>=4.5.2'
      ],
)
