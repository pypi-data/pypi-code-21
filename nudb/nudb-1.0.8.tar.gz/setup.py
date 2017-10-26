from setuptools import setup
import codecs

setup(
    name='nudb',
    version = '1.0.8',
    description = 'For nudb',
    long_description = codecs.open('docs/README.txt', 'r', 'utf-8').read(),
    author = 'Szu-Hsuan, Wu',
    author_email = 'shuan0713@gmail.com',
    url = 'https://github.com/wshs0713/nudb',
    packages = ['nudb'],
    keywords = ['nudb'],
    license = 'docs/LICENSE.txt',
    install_requires=[
        'requests >= 2.13.0'
    ]
)
