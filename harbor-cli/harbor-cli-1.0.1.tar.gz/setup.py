from setuptools import setup, find_packages

setup(
    name='harbor-cli',
    version='1.0.1',
    description='Harbor-CLI is a tool to share Android builds of React Native projects',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'Click==6.7',
        'pyrebase==3.0.27',
        'pyfiglet==0.7.5',
        'colorama==0.3.9',
        'requests==2.11.1',
        'inquirer==2.2.0',
        'terminaltables==3.1.0'
    ],
    entry_points={
        'console_scripts': ['harbor=lib.cli:cli']
    },
    extras_require={
        'develop': ['pytest', 'pylint'],
    },
    url='',
    author='Srishan Bhattarai',
    author_email='srishanbhattarai@gmail.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
