from distutils.core import setup

setup(
    name='simpcass',
    packages=['simpcass'],
    version='0.1.3',
    description='A simple client for Apache Cassandra',
    author='Andy Kuszyk',
    author_email='pairofsocks@hotmail.co.uk',
    url='https://github.com/andykuszyk/simpcass',
    download_url='https://github.com/andykuszyk/simpcass/archive/0.1.tar.gz',
    keywords=['cassandra'],
    classifiers=[],
    install_requires=[
        'cassandra-driver',
    ],
)
