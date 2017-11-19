from setuptools import setup, find_packages

setup(
    name = 'pyleetx',
    version = '0.0.8',
    description = 'Python interface to 1337x.to',
    url = 'https://github.com/srob650/pyleetx',
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

    keywords = 'python leetx 1337x torrents torrent',
    packages=['pyleetx'],
    install_requires=['requests', 'beautifulsoup4']

)
