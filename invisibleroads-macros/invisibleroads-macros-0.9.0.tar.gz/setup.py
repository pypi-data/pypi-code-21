from os.path import abspath, dirname, join
from setuptools import find_packages, setup


FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.rst', 'CHANGES.rst'])
setup(
    name='invisibleroads-macros',
    version='0.9.0',
    description='Shortcut functions',
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url='https://github.com/invisibleroads/invisibleroads-macros',
    keywords='invisibleroads',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[
        'attrs',
        'configparser',
        'simplejson',
        'six',
    ],
    tests_require=[
        'pytest',
    ])
