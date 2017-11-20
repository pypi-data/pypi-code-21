
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from dtperiod import __version__

metadata = {
    'name': 'dtperiod',
    'py_modules': ['dtperiod'],
    'version': __version__,
    'description': 'provide datetime Period object',
    'python_requires': '>=2.4,!=3.0.*,!=3.1.*,!=3.2.*',
    'author': 'Shuhei Hirata',
    'author_email': 'sh7916@gmail.com',
    'license': 'MIT',
    'url': 'https://github.com/hrtshu/dtperiod',
    'keywords': ['datetime', 'date', 'period'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
}

setup(**metadata)
