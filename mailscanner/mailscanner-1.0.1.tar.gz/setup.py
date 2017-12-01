from setuptools import setup

setup(
    name='mailscanner',
    packages=['mailscanner'],
    version='1.0.1',
    description='Reads and parses email messages using IMAP',
    author='Ville Kumpulainen',
    author_email='ville.kumpulainen@gmail.com',
    url='http://github.com/coumbole/mailscanner',
    keywords = ['email', 'imap', 'parser'],
    license = 'GPL-3.0',
    python_requires='>=3',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ]
)
