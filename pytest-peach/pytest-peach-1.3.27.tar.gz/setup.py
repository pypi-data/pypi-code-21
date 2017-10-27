import os
from setuptools import setup

cwd = os.getcwd()
try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    version = '1.3.27'

    setup(
        name = 'pytest-peach',
        description = 'pytest plugin for fuzzing with Peach API Security',
        long_description = open('README.rst').read(),
        author = 'Peach Tech',
        author_email = 'contact@peachfuzzer.com',
        url = 'https://peach.tech',
        version = '1.3.27',

        py_modules = ['pytest_peach'],
        entry_points = {'pytest11': ['peach = pytest_peach']},

        # Also update requirements.txt!
        install_requires = ['pytest>=2.8.7', 'peachapisec-api>=%s' % version],

        license = 'Apache License, Version 2.0',
        keywords = 'py.test pytest fuzzing peach',

        classifiers = [
            'Development Status :: 4 - Beta',
            'Framework :: Pytest',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Topic :: Security',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5'
        ])

finally:
    os.chdir(cwd)

# end
