'''
Module setup file.
'''

from setuptools import setup
setup(
    name='urbandictionary_top',
    version='0.1',
    py_modules=['urbandictionary_top'],
    install_requires=[
        'beautifulsoup4',
        'html5lib',
        'requests',
    ],
    description=('A dead simple module that fetches the top definition and '
                 'example of a term from urbandictionary. '
                 '(https://urbandictionary.com)'),
    author='sage',
    author_email='laymonage@gmail.com',
    url='https://github.com/laymonage/urbandictionary_top-python',
    download_url=('https://github.com/laymonage/urbandictionary_top-python/'
                  'archive/0.1.tar.gz'),
    keywords=['urban', 'dictionary', 'urbandictionary', 'top', 'definition',
              'example'],
    classifiers=[],
)
