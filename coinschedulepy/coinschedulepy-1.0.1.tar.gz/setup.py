from setuptools import setup, find_packages

setup(
    name='coinschedulepy',

    version='1.0.1',

    description='A python3 wrapper for the coinschedule api',
    long_description='Coinschedule is a Python3 wrapper for the coinschedule.com API',

    url='https://github.com/0x15f/coinschedule-python',

    author='Jake Casto',
    author_email='jakehcasto@aol.com',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='ico icos coinschedule api python3',

    packages=find_packages(),

    install_requires=['json', 'requests'],
)