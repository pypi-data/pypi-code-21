import io
from setuptools import setup, find_packages


def parse_requirements(file):
    required = []
    with open(file) as f:
        for req in f.read().splitlines():
            if not req.strip().startswith('#'):
                required.append(req)
    return required


def read(*args, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in args:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


requirements = parse_requirements('requirements.txt')
long_description = read('README.rst', 'CHANGES.rst')
LGPLv3 = 'License :: OSI Approved :: GNU Lesser General Public License v3 ' \
         'or later (LGPLv3+)'

setup(
    name="keyring-otp",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    test_suite='kotp.tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        LGPLv3,
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],

    # metadata for upload to PyPI
    author="Pierre Verkest",
    author_email="pverkest@anybox.fr",
    description="OTP command line tool",
    long_description=long_description,
    license="GPLv3",
    keywords="keyring otp totp",
    url="https://github.com/petrus-v/keyring-otp",
    entry_points={
        'console_scripts': [
            'kotp=kotp.cli:main',
        ],
    },
)
