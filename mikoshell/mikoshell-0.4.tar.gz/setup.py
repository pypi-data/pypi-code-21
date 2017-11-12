from distutils.core import setup

setup(
    name = 'mikoshell',
    packages = ['mikoshell'],
    install_requires = ['paramiko'],
    version = '0.4',
    description = 'Simple shell interface for Paramiko',
    author = 'Matt Ryan',
    author_email = 'inetuid@gmail.com',
    url = 'https://github.com/inetuid/mikoshell',
    download_url = 'https://github.com/inetuid/mikoshell/tarball/0.4',
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
