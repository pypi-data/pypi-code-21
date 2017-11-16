from setuptools import setup, find_packages
from distutils.util import convert_path

# Finding the version number
# See https://packaging.python.org/single_source_version/ for the technique
version_ns = {}
ver_path = convert_path('tiros/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), version_ns)

setup(
    name='tiros',
    version=version_ns['__version__'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False, # if not set, static files are not included in the package
    install_requires=['requests>=2.11.1',
                      'boto3>=1.4.4',
                      'datetime>=4.1.1',
                      'Flask>=0.2',
                      'semantic_version>=2.6.0'
                      ],
    entry_points={
        'console_scripts': [
            'tiros = tiros.cli:main',
        ],
    },
)
