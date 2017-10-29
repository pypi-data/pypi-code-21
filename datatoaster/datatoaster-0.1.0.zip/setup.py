from setuptools import setup, find_packages

with open('README.md', encoding = "utf-8") as f:
    readme = f.read()

setup(
    name='datatoaster',
    version='0.1.0',
    description='A Python library that can convert raw data to chart data',
    long_description=readme,
    author='Harry Yu',
    author_email='harryyunull@gmail.com',
    url='https://github.com/abc612008/datatoaster',
    license="MIT",
    packages=find_packages(exclude=('tests', 'docs', 'demo'))
)
