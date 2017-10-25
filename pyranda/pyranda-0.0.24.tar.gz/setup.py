from setuptools import setup

with open('README') as f:
    long_description = ''.join(f.readlines())

setup(
    name='pyranda',
    version='0.0.24',
    description='Generate random data of common czech names',
    long_description=long_description,
    author='Radomír Ludva',
    author_email='rludva@radmi.cz',
    license='Public Domain',
    url='https://github.com/rludva/pyranda',
    packages=['pyranda', 'pyranda/demo'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: Czech',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pyranda  = pyranda.app:main',
        ],
    },
    setup_requires=['pytest-runner',],
    tests_require=['pytest',],
)
