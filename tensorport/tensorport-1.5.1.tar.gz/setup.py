from setuptools import setup, find_packages
from version import VERSION

setup(
    name='tensorport',
    version=VERSION,
    py_modules=[
        'tensorport_cli', 'tensorport', 'version', 'utils', 'tf_runner'
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires='>2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        'click', 'py', 'coreapi-cli', 'gitpython', 'raven', 'terminaltables',
        'click_log==0.1.8', 'virtualenv', 'six'
    ],
    entry_points='''
        [console_scripts]
        tport=tensorport_cli:cli
    ''',

    author="TensorPort",
    author_email="info@tensorport.com",
    description="TensorPort CLI and Python library.",
    license="Apache Software License",
    keywords="",
    url="http://tensorport.com",
)
