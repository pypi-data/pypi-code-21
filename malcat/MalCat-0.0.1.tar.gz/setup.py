import setuptools
import sys


dependencies = {'cssselect', 'lxml', 'requests', 'six'}
if sys.version_info < (3, 4):
    dependencies.add('enum34')


with open('README.rst') as f:
    readme = f.read()


setuptools.setup(
    name='MalCat',
    version='0.0.1',
    description='MAL list-to-text processing utility.',
    long_description=readme,

    author='Doomcat55',
    author_email='Doomcat55@gmail.com',
    url='https://github.com/Doomcat55/MalCat',

    packages=setuptools.find_packages(),
    include_package_data=True,

    install_requires=dependencies,

    license='MIT',

    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
    ]
)
