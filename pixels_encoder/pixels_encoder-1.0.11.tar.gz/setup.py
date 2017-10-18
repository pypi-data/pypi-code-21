from setuptools import find_packages, setup
from app import __version__

setup(
    name='pixels_encoder',
    version=__version__,
    description='extract image pixels info into json',
    url='https://github.com/app-craft/pixels-encoder',
    author='sroik',
    author_email='vasili.kazhanouski@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests*']),

    entry_points='''
        [console_scripts]
        pixels_encoder=app:cli
    ''',

    install_requires=[
        'pillow',
        'numpy',
    ],
    zip_safe=False
)
