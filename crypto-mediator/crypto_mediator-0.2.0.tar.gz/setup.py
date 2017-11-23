from setuptools import setup


setup(
    name = "crypto_mediator",
    version = "0.2.0",
    author = "Connor Wallace",
    author_email = "wallaconno@gmail.com",
    description = ('Client that allows communication between many crypto exchanges'),
    license = "MIT",
    keywords = "cryptocurrency client",
    url = "http://www.github.com/cowalla/mediator",
    packages=[
        ''
        'crypto_mediator',
        'crypto_mediator.clients',
        'crypto_mediator.fixtures',
        'crypto_mediator.clients.tests',
    ],
    install_requires=[
        'astroid==1.5.3',
        'backports.functools-lru-cache==1.4',
        'backports.ssl-match-hostname==3.5.0.1',
        'bintrees==2.0.7',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'configparser==3.5.0',
        'enum34==1.1.6',
        'funcsigs==1.0.2',
        'gdax==1.0.6',
        'idna==2.6',
        'isort==4.2.15',
        'lazy-object-proxy==1.3.1',
        'liqui==1.0.1',
        'mccabe==0.6.1',
        'mock==2.0.0',
        'pbr==3.1.1',
        'py==1.5.1',
        'pylint==1.7.4',
        'pytest==3.2.5',
        'requests==2.7.0',
        'singledispatch==3.4.0.3',
        'six==1.10.0',
        'urllib3==1.22',
        'websocket-client==0.40.0',
        'wheel==0.24.0',
        'wrapt==1.10.11',
    ],
    dependency_links=[
        'git+https://github.com/ericsomdahl/python-bittrex',
        'https://github.com/s4w3d0ff/python-poloniex',
    ]
)