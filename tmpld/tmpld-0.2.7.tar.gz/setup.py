import re
from setuptools import setup, find_packages


with open('tmpld/__init__.py', 'rt') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md') as fd:
    long_description = fd.read()


setup(
    name='tmpld',
    version=version,
    description='Render templates in docker entrypoint scripts.',
    long_description=long_description,
    keywords=[
        'kubernetes',
        'clustering',
        'entrypoint',
        'entrypoints',
        'docker',
        'template',
        'templates'
    ],
    author='Joe Black',
    author_email='me@joeblack.nyc',
    url='https://github.com/joeblackwaslike/tmpld',
    download_url=(
        'https://github.com/joeblackwaslike/tmpld/tarball/v%s' % version),
    license='Apache 2.0',
    zip_safe=False,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    install_requires=[
        'cement',
        'delegator.py>=0.0.13',
        'Jinja2',
        'pyrkube>=0.2.3',
        'PyYAML'
    ],
    extras_require=dict(
        caps=['pycaps'],
        xpath=['lxml.etree'],
        jpath=['jsonpath-rw'],
        all=['pycaps', 'lxml.etree', 'jsonpath-rw']
    ),
    entry_points=dict(
        console_scripts=['tmpld = tmpld.cli.main:main']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing',
        'Topic :: Utilities'
    ]
)
