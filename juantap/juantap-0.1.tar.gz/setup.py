from setuptools import setup

setup(
    name='juantap',
    packages=['juantap'],
    version='0.1',
    description='CLI for managing multiple dedicated CS:GO servers, based on a single root installation',
    author='Mathias Sass Michno',
    author_email='m@michno.me',
    install_requires=[
        'click',
        'sh'
    ],
    entry_points='''
        [console_scripts]
        juantap=juantap:cli
    ''',
    url='https://github.com/mathiassmichno/juantap',
    keywords=['csgo', 'linuxgsm', 'server management', 'overlayfs'],
)
