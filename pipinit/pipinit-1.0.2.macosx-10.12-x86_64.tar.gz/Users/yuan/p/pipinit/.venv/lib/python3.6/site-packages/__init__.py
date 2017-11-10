from os import path, getcwd

import click


def inputWithDefault(prompt, default=''):
    inputGot = input(prompt)
    if inputGot == '':
        inputGot = default

    return inputGot


@click.command()
def cli():

    if path.isfile(getcwd() + '/setup.py'):
        print('setup.py exists, will not overwrite')
        return

    dirName = getcwd().split('/')[-1]
    name = inputWithDefault('Name of the project({}): '.format(dirName),
                            dirName)

    version = inputWithDefault('Current version(1.0.0): ', '1.0.0')

    description = inputWithDefault('Short description: ')

    url = inputWithDefault('URL: ')

    author = inputWithDefault('Author: ')

    author_email = inputWithDefault('Author email: ')

    license = inputWithDefault('License(MIT): ', 'MIT')

    python_requires = inputWithDefault('Python requires(>=3): ', '>=3')

    text = '''from setuptools import setup, find_packages
setup(
    name='{}',
    version='{}',
    description='{}',
    url='{}',
    author='{}',
    author_email='{}',
    license='{}',
    packages=find_packages(),
    python_requires='{}'
    )'''.format(name, version, description, url, author, author_email, license,
                python_requires)
    with open('setup.py', 'w') as f:
        f.write(text)
