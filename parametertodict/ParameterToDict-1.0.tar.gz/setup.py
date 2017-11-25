try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Converts parameter to dictionary.',
    'author': 'Suyogya Khanal',
    'download_url': 'https://pypi.python.org/parametertodict',
    'author_email': 'suyogkhanal4@gmail.com',
    'version': '1.0',
    'install_requires': ['nose'],
    'packages': ['ParameterToDict'],
    'scripts': [],
    'name': 'ParameterToDict'
}

setup(**config)
