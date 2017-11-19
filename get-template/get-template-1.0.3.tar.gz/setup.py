from setuptools import setup, find_packages
from pip.req import parse_requirements
from get_template import __version__

with open('README.md') as reader:
    readme = reader.read()

requirements = [str(ir.req) for ir in parse_requirements("requirements.txt", session=False)]

setup(
    name='get-template',
    version=__version__,
    description='Templating',
    long_description=readme,
    url='https://gitlab.com/Dithyrambe/templator',
    author='dithyrambe',
    author_email='dithyrambe@outlook.fr',
    license='WTFPL',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Template',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'template = get_template.cli.__main__:template'
        ]
    },
)
