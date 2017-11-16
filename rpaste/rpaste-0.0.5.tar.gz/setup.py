try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from rpaste.version import __version__

setup(
    name='rpaste',
    packages=['rpaste'],
    version=__version__,
    description='Code Snippets Uploader',
    author='Anup Pokhrel',
    author_email='virtualanup@gmail.com',
    url='https://github.com/rpaste/rpaste',
    keywords=['rpaste', 'paste', 'bin'],
    classifiers=[],
    entry_points={
        "console_scripts": [
            "rpaste=rpaste:main",
        ]
    },
    install_requires=[
    ],
)
