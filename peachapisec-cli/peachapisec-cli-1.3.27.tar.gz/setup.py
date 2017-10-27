import os
from setuptools import setup

cwd = os.getcwd()
try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    setup(
        name = 'peachapisec-cli',
        description = 'Peach API Security command line tool',
        long_description = open('README.rst').read(),
        author = 'Peach Tech',
        author_email = 'contact@peachfuzzer.com',
        url = 'https://peach.tech',
        version = '1.3.27',

        py_modules = ['peachcli'],

        # update requirements.txt as well!
        install_requires = ['click>=6.7', 'peachapisec-api==1.3.27'],
        scripts=['bin/peachcli', 'bin/peachcli.bat'],

        license = 'Apache License, Version 2.0',
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
