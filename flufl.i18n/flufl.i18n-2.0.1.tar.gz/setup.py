from setup_helpers import description, get_version, require_python
from setuptools import setup, find_packages


require_python(0x30400f0)
__version__ = get_version('flufl/i18n/__init__.py')


setup(
    name='flufl.i18n',
    version=__version__,
    namespace_packages=['flufl'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    maintainer='Barry Warsaw',
    maintainer_email='barry@python.org',
    description=description('README.rst'),
    license='ASLv2',
    url='https://flufli18n.readthedocs.io',
    download_url='https://pypi.python.org/pypi/flufl.i18n',
    install_requires=[
        'atpublic',
        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        ]
    )
