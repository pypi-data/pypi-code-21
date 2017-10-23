from distutils.core import setup


def readfile(name):
    with open(name) as f:
        return f.read()


README = readfile('README.rst')


install_requires = [
    'selenium >= 3.0.2'
]


setup(
    name='webparser',
    version='1.0',
    packages=['webparser'],
    url='https://github.com/soomrack/webparser',
    license='MIT',
    author='Mikhail Ananyevskiy (aka soomrack)',
    author_email='soomrack@gmail.com',
    description='Tiny framework for parsing web.',
    long_description=README,
    keywords='webparser web parser selenium',
    classifiers=[
       'Intended Audience :: Developers',
       'Programming Language :: Python :: 3.4',
       'Natural Language :: English',
    ]
)
