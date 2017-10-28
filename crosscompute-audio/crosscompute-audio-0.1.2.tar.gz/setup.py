from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = """
[crosscompute.types]
audio = crosscompute_audio:AudioType
"""
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.rst'])
setup(
    name='crosscompute-audio',
    version='0.1.2',
    description='Audio data type plugin for CrossCompute',
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: MIT License',
    ],
    author='Salah Ahmed',
    author_email='salah93@crosscompute.com',
    url='https://github.com/salah93/crosscompute-audio',
    keywords='web crosscompute',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'crosscompute>=0.7.0',
    ],
    entry_points=ENTRY_POINTS)
