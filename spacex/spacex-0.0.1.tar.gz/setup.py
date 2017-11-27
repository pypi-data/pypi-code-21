import os

from distutils.core import setup

rootpath = os.path.abspath(os.path.dirname(__file__))


def extract_version(mod='spacex'):
    ver = None
    fname = os.path.join(rootpath, mod, '__init__.py')
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                _, ver = line.split('=')
                ver = ver.strip()[1:-1]  # Remove quotes.
                break
    return ver

version = extract_version()

setup(
    name='spacex',
    packages=['spacex'],
    version=version,
    description='A synchronous wrapper for the Space X API.',
    author='Tyler Gibbs',
    author_email='gibbstyler7@gmail.com',
    url='https://github.com/TheTrain2000/spacex.py',
    download_url='https://github.com/TheTrain2000/spacex.py/archive/{}.tar.gz'.format(version),
    keywords=['api', 'synchronous', 'wrapper', 'space x'],
    classifiers=[],
    install_requires=['requests==2.18.4']
)
