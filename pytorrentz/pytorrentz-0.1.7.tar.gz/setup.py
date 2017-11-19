from setuptools import setup, find_packages

setup(
    name = 'pytorrentz',
    version = '0.1.7',
    description = ('Python interface to https://www.torrentz.eu -- '
                   'based on https://github.com/dannvix/torrentz-magdl'),
    url = 'https://github.com/srob650/pytorrentz',
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

    keywords = 'python torrentz torrents torrent',
    packages=['pytorrentz'],
    install_requires=['requests', 'bs4', 'cfscrape']

)
