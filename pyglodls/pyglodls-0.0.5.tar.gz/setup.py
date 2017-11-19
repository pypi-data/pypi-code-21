from setuptools import setup, find_packages

setup(
    name = 'pyglodls',
    version = '0.0.5',
    description = 'Python interface to http://glodls.to',
    url = 'https://github.com/srob650/pyglodls',
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

    keywords = 'python glodls glotorrents torrents torrent',
    packages=['pyglodls'],
    install_requires=['requests', 'bs4']

)
