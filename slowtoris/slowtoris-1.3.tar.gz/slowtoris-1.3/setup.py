from setuptools import setup

setup(
        name = 'slowtoris',
        packages = ['slowtoris'],
        version = '1.3',
        description = 'A Python implementation of the Slow Loris attack with support for the Tor network and SOCKS5 proxies.',
        author = 'Gabriel Duque',
        author_email = 'g.duque@protonmail.ch',
        url = 'https://github.com/naganori-san/slowtoris',
        download_url = 'https://github.com/naganori-san/slowtoris/archive/0.3.tar.gz',
        keywords = ['hacking-tools', 'security', 'dos-tools'],
        license = 'MIT',
        scripts = ['slowtoris/slowtoris'],
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Education',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3 :: Only',
            ],
        install_requires = [
            'click',
            'PySocks',
            'stem'
            ]
        )
