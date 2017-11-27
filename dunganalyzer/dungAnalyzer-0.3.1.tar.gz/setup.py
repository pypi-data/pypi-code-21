import os
import sys
from setuptools import setup, find_packages

f = open('README.rst')
readme = f.read()
f.close()

version = '0.3.1'

if sys.argv[-1] == 'publish':
    if os.system("pip3 freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip3 freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python3 setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

setup(

    name='dungAnalyzer',
    version=version,
    description='Stemming words and removal of stop words',
    long_description=readme,
    author='phenix',
    author_email='maruf@algomatrix.co',
    maintainer='algomatrix',
    maintainer_email='maruf@algomatrix.co',
    url='',
    packages=find_packages(),
    include_package_data=True,
    package_data={'dungAnalyzer': ['resources/*.txt']},
    install_requires = ['nltk==3.2.5'],
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Bengali',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing',
    ],
    zip_safe=False,
)
