import os, sys
from setuptools import setup

cwd = os.getcwd()
try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    setup(
        name = 'peachapisec-api',
        description = 'Peach Web Proxy API module',
        long_description = open('README.rst').read(),
        author = 'Peach Tech',
        author_email = 'support@peachfuzzer.com',
        url = 'https://peach.tech',
        version = '1.3.27',

        py_modules = ['peachapisec'],

        # also update requirements.txt!
        install_requires = ['requests>=2.11'],

        license = 'Apache License 2.0',
        keywords = 'peach fuzzing security test rest',

        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Topic :: Security',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3'
        ])

finally:
    os.chdir(cwd)

# end
