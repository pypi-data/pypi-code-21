#!/usr/bin/env python3
"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject

Extra supported commands are:
* gen_tl, to generate the classes required for Telethon to run
* clean_tl, to clean these generated classes
* pypi, to generate sdist, bdist_wheel, and push to PyPi
"""

# To use a consistent encoding
from codecs import open
from sys import argv
import os

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

try:
    from telethon import TelegramClient
except Exception as e:
    print('Failed to import TelegramClient due to', e)
    TelegramClient = None


class TempWorkDir:
    """Switches the working directory to be the one on which this file lives,
       while within the 'with' block.
    """
    def __init__(self):
        self.original = None

    def __enter__(self):
        self.original = os.path.abspath(os.path.curdir)
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        return self

    def __exit__(self, *args):
        os.chdir(self.original)


def gen_tl():
    from telethon_generator.tl_generator import TLGenerator
    generator = TLGenerator('telethon/tl')
    if generator.tlobjects_exist():
        print('Detected previous TLObjects. Cleaning...')
        generator.clean_tlobjects()

    print('Generating TLObjects...')
    generator.generate_tlobjects(
        'telethon_generator/scheme.tl', import_depth=2
    )
    print('Done.')


def main():
    if len(argv) >= 2 and argv[1] == 'gen_tl':
        gen_tl()

    elif len(argv) >= 2 and argv[1] == 'clean_tl':
        from telethon_generator.tl_generator import TLGenerator
        print('Cleaning...')
        TLGenerator('telethon/tl').clean_tlobjects()
        print('Done.')

    elif len(argv) >= 2 and argv[1] == 'pypi':
        # Need python3.5 or higher, but Telethon is supposed to support 3.x
        # Place it here since noone should be running ./setup.py pypi anyway
        from subprocess import run
        from shutil import rmtree

        for x in ('build', 'dist', 'Telethon.egg-info'):
            rmtree(x, ignore_errors=True)
        run('python3 setup.py sdist', shell=True)
        run('python3 setup.py bdist_wheel', shell=True)
        run('twine upload dist/*', shell=True)
        for x in ('build', 'dist', 'Telethon.egg-info'):
            rmtree(x, ignore_errors=True)

    else:
        if not TelegramClient:
            gen_tl()
            from telethon import TelegramClient as TgClient
            version = TgClient.__version__
        else:
            version = TelegramClient.__version__

        # Get the long description from the README file
        with open('README.rst', encoding='utf-8') as f:
            long_description = f.read()

        setup(
            name='Telethon',

            # Versions should comply with PEP440.
            version=version,
            description="Full-featured Telegram client library for Python 3",
            long_description=long_description,

            url='https://github.com/LonamiWebs/Telethon',
            download_url='https://github.com/LonamiWebs/Telethon/releases',

            author='Lonami Exo',
            author_email='totufals@hotmail.com',

            license='MIT',

            # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=[
                #   3 - Alpha
                #   4 - Beta
                #   5 - Production/Stable
                'Development Status :: 3 - Alpha',

                'Intended Audience :: Developers',
                'Topic :: Communications :: Chat',

                'License :: OSI Approved :: MIT License',

                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.6'
            ],
            keywords='telegram api chat client library messaging mtproto',
            packages=find_packages(exclude=[
                'telethon_generator', 'telethon_tests', 'run_tests.py',
                'try_telethon.py'
            ]),
            install_requires=['pyaes', 'rsa']
        )


if __name__ == '__main__':
    with TempWorkDir():  # Could just use a try/finally but this is + reusable
        main()
