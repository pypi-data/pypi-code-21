"""Following
Ninad Sathaye, ``Learning Python Application Development,'' by PacktPub, 2016,
https://www.packtpub.com/application-development/learning-python-application-development
"""
from distutils.core import setup

with open('README.md') as file_:
    readme = file_.read()

setup(
    name='dimensionalquantity',
    version='0.5.0',
    packages=['dimensionalquantity','dimensionalquantity/tests'],
    url='https://github.com/stefantkeller/dimensionalquantity',
    license='LICENSE',
    description='Conveniently attach units to numbers.',
    long_description=readme,
    author='Stefan T. Keller',
    author_email='stefantkeller@gmail.com'
)
