import ast
import os
import re
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('pygments_solarized/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(
        _version_re.search(f.read().decode('utf-8')).group(1)
    ))

setup(
    name='pygments-solarized',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    keywords='pygments style solarized',
    description='Pygments version of the solarized theme based on john2x/solarized-pygment.',
    long_description='Pygments version of the solarized theme based on john2x/solarized-pygment.',
    url='https://github.com/meganlkm/pygments-solarized',
    author='meganlkm',
    author_email='devstuff.io@gmail.com',
    install_requires=['Pygments>=2.0.0'],
    entry_points={
        'pygments.styles': [
            'solarized=pygments_solarized:SolarizedStyle',
            'solarized_dark=pygments_solarized:SolarizedDarkStyle',
            'solarized_dark256=pygments_solarized:SolarizedDark256Style'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
