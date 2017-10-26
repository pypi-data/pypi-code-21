from setuptools import setup

setup(
    name='xamarin-legos',
    version='1.0.3',
    description='command line tool to fetch details from github projects/nuget packages',
    author='Prashant Cholachagudda',
    author_email='pvc@outlook.com',
    py_modules=['nuget','legos_command'],
    install_requires=['Click','PyGithub','arrow', 'tabulate', 'requests', 'configparser'],
    url='https://github.com/prashantvc/legos-cli',
    entry_points='''
        [console_scripts]
        legos=legos_command:cli
    ''',
    )