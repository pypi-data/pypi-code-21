from setuptools import setup, find_packages

setup(
    name = 'pyzooqle',
    version = '0.0.5',
    description = 'Python interface to https://zooqle.com',
    url = 'https://github.com/srob650/pyzooqle',
    author = 'srob650',
    author_email = 'pytvmaze@gmail.com',
    license='MIT',

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'
    ],

    keywords = 'python zooqle torrents torrent',
    packages=['pyzooqle'],
    install_requires=['requests', 'bs4']

)
