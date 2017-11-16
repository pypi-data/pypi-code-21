# coding=utf-8
from setuptools import setup

setup(
    name='bismuth',
    description='bismuth message service',
    version='0.1',
    author='Kent Ross',
    author_email='k@mad.cash',
    url='',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Operating System :: POSIX',
        'Framework :: AsyncIO',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications',
        'Topic :: Security :: Cryptography',
    ],

    packages=[
        'bismuth_messages',
        'bismuth_messages.proto',
        'bismuth_messages.proto.client_server',
        'bismuth_server',
    ],
    package_dir={'': "src"},
    package_data={
        'bismuth_messages.proto': ['*.proto'],
        'bismuth_messages.proto.client_server': ['*.proto'],
        'bismuth_server': ['postgres/*.sql'],
    },
    data_files=[
        ('nginx', [
           'nginx/example.config',
        ]),
        ('src/bismuth_jsclient', [
            'src/bismuth_jsclient/app.html',
            'src/bismuth_jsclient/static/client.js',
            'src/bismuth_jsclient/static/style.css',
        ]),
        ('test/postgres', [
            'test/postgres/test_errs.sql',
            'test/postgres/test_schema.sql',
        ]),
    ],
    install_requires=[
        'aiofiles==0.3.2',
        'aioredis==1.0.0b2',
        'asyncpg==0.13.0',
        'hiredis==0.2.0',
        'httptools==0.0.9',
        'libnacl==1.6.1',
        'protobuf==3.4.0',
        'sanic==0.6.0',
        'six==1.11.0',
        'ujson==1.35',
        'uvloop==0.8.1',
        'websockets==4.0.1',
    ],
    extras_require={
        'test': [
            'pytest-asyncio',
            'pytest-cov',
        ]
    },
    entry_points={
        'console_scripts': [
            'bismuth-runserver = bismuth_server.server:main',
        ],
    },
)
