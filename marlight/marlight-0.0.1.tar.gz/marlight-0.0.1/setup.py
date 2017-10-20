
import os

from setuptools import setup, find_packages

def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as r_file:
        return  r_file.read()

setup(
        name='marlight',
        version='0.0.1',
        description='Marglight RGBW control through ethernet bridge',
        long_description=readme(),
        author='Nicolas Gilles',
        author_email='nicolas.gilles@gmail.com',
        license='BSD 2-Clause',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
        ],

        packages=find_packages('src'),
        package_dir={'':'src'}
)
