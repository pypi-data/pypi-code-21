from setuptools import setup, find_packages

setup(
    name='harbor-cli',
    version='0.1.0',
    description='Harbor-CLI is a tool to share Android builds of React Native projects',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'Click',
        'pyrebase',
        'pyfiglet',
        'colorama',
        'requests',
        'inquirer',
        'terminaltables'
    ],
    entry_points={
        'console_scripts': ['harbor=lib.cli:cli']
    },
    url='',
    author='Srishan Bhattarai',
    author_email='srishanbhattarai@gmail.com',
    license='MIT',
    include_package_data=True
)
