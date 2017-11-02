from setuptools import setup, find_packages

from tinyj2 import __description__

with open('requirements.txt') as f:
    install_requires = f.readlines()

setup(
    name='tinyj2',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    packages=find_packages(),
    url='',
    license='',
    author='Wojciech Wróblewski',
    author_email='wojciech.wroblewski@gmx.com',
    description=__description__,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'tinyj2 = tinyj2.__main__:main',
        ]
    },
)
