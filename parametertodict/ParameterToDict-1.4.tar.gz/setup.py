try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Converts parameter to dictionary.',
    'author': 'Suyogya Khanal',
    'download_url': 'https://pypi.python.org/pypi/parametertodict',
    'author_email': 'suyogkhanal4@gmail.com',
    'version': '1.4',
    'install_requires': ['nose'],
    'packages': ['ParameterToDict'],
    'scripts': ['bin/ParameterToDict'],
    'name': 'ParameterToDict'
}

setup(**config)
