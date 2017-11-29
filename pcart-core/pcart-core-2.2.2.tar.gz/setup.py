from distutils.core import setup
from setuptools import find_packages

INSTALL_REQUIREMENTS = [
    'Django>=1.10.5',
    'Markdown==2.6.8',
    'unicode-slugify>=0.1.3',
    'django-cms>=3.4.2',
    'django-ace>=1.0.3',
    'psutil>=5.2.2',
]

setup(
    name='pcart-core',
    version='2.2.2',
    author='Oleh Korkh',
    author_email='oleh.korkh@the7bits.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    license='BSD License',
    description='A powerful e-commerce solution for Django CMS',
    long_description=open('README.txt').read(),
    platforms=['OS Independent'],
    url='http://the7bits.com/',
    install_requires=INSTALL_REQUIREMENTS,
)
