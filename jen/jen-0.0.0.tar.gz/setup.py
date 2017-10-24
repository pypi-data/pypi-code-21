from setuptools import setup

long_description = """
Static site generator and prototyping tool based on Jinja2.
It\'s able to serve contents and build a static site from a simple file structure.

https://github.com/hugollm/jen
"""

setup(
    name = 'jen',
    version = '0.0.0',

    packages = ['jen'],
    include_package_data = True,

    install_requires = ['gunicorn >= 19, < 20', 'Jinja2 >= 2, < 3'],
    entry_points = {'console_scripts': ['jen=jen.main:run']},

    author = 'Hugo Leonardo Leão Mota',
    author_email = 'hugo.txt@gmail.com',
    license = 'MIT',
    url = 'https://github.com/hugollm/jen',

    keywords = 'jen static site generator prototype build',
    description = 'Static site generator and prototyping tool based on Jinja2.',

    long_description = long_description,
)
