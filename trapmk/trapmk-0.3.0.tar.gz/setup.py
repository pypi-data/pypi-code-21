from setuptools import setup
import ast

from trapmk import __version__


with open('trapmk/trapmk.py') as f:
    trapmk_contents = f.read()
module = ast.parse(trapmk_contents)
readme_docstring = ast.get_docstring(module)

setup(
    name='trapmk',
    version=__version__,
    description='trapmk: TrapHack adventure builder',
    long_description=readme_docstring,
    author='SlimeMaid',
    author_email='slimemaid@gmail.com',
    keywords='cli',
    install_requires=['jinja2_markdown==0.0.3',],
    packages=['trapmk',],
    entry_points = {
        'console_scripts': [
            'trapmk=trapmk.trapmk:entrypoint',
        ],
    },
    package_dir={'trapmk': 'trapmk',},
)
