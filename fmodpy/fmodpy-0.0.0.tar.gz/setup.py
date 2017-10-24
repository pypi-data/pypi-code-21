from setuptools import setup

setup(
    author = 'Thomas C.H. Lux',
    author_email = 'tchlux@vt.edu',
    name='fmodpy',
    packages=['fmodpy'],
    version='0.0.0',
    description = 'A lightweight, efficient, highly automated, fortran wrapper for python.',
    url = 'https://github.com/tchlux/fmodpy',
    download_url = 'https://github.com/tchlux/fmodpy/archive/0.0.0.tar.gz',
    # license='MIT',
    keywords = ['python', 'python3', 'python27', 'fortran', 'wrapper'],
    install_requires=['numpy>=1.11', 'matplotlib>=1.5']
)
