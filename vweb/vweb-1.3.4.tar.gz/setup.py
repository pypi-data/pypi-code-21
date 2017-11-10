from setuptools import setup
import string

with open('README.md') as f:
    readme = f.read()
with open('requirements.txt') as f:
    requirements = map(string.strip, open('requirements.txt').readlines())

setup(
    name='vweb',
    packages=['vweb'],
    version='1.3.4',
    description='Simple Python Website Frame work',
    long_description=readme,
    url='https://github.com/dlink/vweb',
    author='David Link',
    author_email='dvlink@gmail.com',
    license='GNU General Public License (GPL)',
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    keywords = ['cgi', 'web framework']
    #zip_safe=False,
    #install_requires=requirements
)
