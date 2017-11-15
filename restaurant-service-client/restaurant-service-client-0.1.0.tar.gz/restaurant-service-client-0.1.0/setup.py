from setuptools import setup
from setuptools import find_packages

setup(
    name='restaurant-service-client',
    version='0.1.0',
    author='Guido Barbaglia',
    author_email='guido.barbaglia@gmail.com',
    packages=find_packages(),
    license='LICENSE',
    long_description=open('README.md').read(),
    description='Restaurant Service Client',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest>=3.0',
        'pact-test'
    ],
    url='https://github.com/Kalimaha/restaurant-service-client'
)
